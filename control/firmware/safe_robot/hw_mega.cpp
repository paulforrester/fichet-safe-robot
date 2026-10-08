#include "hw_mega.h"

#include <EEPROM.h>

#include "config.h"
#include "pins.h"
#include "src/core/ramp.h"

using namespace core;

namespace {

struct AxisPins { uint8_t step, dir, en, diag; };
// All four drivers sit in RAMPS sockets (X, Y, Z, E0), each with its own
// STEP, DIR and EN line (revision 2026-10-08.1; before it, the key's DIR and
// EN were tied low on a remote board).
const AxisPins kPins[AX_COUNT] = {
  {PIN_A_STEP, PIN_A_DIR, PIN_A_EN, PIN_A_DIAG},
  {PIN_B_STEP, PIN_B_DIR, PIN_B_EN, PIN_B_DIAG},
  {PIN_C_STEP, PIN_C_DIR, PIN_C_EN, PIN_C_DIAG},
  {PIN_K_STEP, PIN_K_DIR, PIN_K_EN, PIN_K_DIAG},
};

// DIAG is a pulse (datasheet §11.2): latch it in an interrupt so a short
// pulse between two loop iterations is never missed.
volatile bool g_diag[AX_COUNT];
void diagA() { g_diag[AX_A] = true; }
void diagB() { g_diag[AX_B] = true; }
void diagC() { g_diag[AX_C] = true; }
void diagK() { g_diag[AX_KEY] = true; }

const uint8_t kRegSgResult = 0x41;

// CHOPCONF.MRES encoding: 256 microsteps -> 0, 128 -> 1, ... 1 -> 8.
uint8_t mresFor(uint16_t microsteps) {
  uint8_t m = 8;
  for (uint16_t v = 1; v < microsteps && m; v <<= 1) --m;
  return m;
}
const uint8_t kToffOn = 3;  // CHOPCONF reset default; TOFF=0 disables the driver

}  // namespace

HwMega::HwMega(Settings& s)
    : s_(s),
      drv_{{&TMC_SERIAL, CFG_R_SENSE, 0}, {&TMC_SERIAL, CFG_R_SENSE, 1},
           {&TMC_SERIAL, CFG_R_SENSE, 2}, {&TMC_SERIAL, CFG_R_SENSE, 3}} {}

void HwMega::begin() {
  for (uint8_t a = 0; a < AX_COUNT; ++a) {
    const AxisPins& p = kPins[a];
    pinMode(p.step, OUTPUT);
    digitalWrite(p.step, LOW);
    pinMode(p.dir, OUTPUT);
    digitalWrite(p.dir, LOW);
    pinMode(p.en, OUTPUT);
    digitalWrite(p.en, HIGH);  // disabled (RAMPS also pulls EN high, 10 k)
    // Pull-up: an unplugged DIAG lead reads high = "stalled", and the
    // firmware refuses to move (wiring.md §1).
    pinMode(p.diag, INPUT_PULLUP);
    g_diag[a] = false;
  }
  attachInterrupt(digitalPinToInterrupt(PIN_A_DIAG), diagA, RISING);
  attachInterrupt(digitalPinToInterrupt(PIN_B_DIAG), diagB, RISING);
  attachInterrupt(digitalPinToInterrupt(PIN_C_DIAG), diagC, RISING);
  attachInterrupt(digitalPinToInterrupt(PIN_K_DIAG), diagK, RISING);
  pinMode(PIN_BUTTON, INPUT_PULLUP);
  pinMode(PIN_LED, OUTPUT);
  TMC_SERIAL.begin(CFG_UART_BAUD);
}

// ---------------------------------------------------------------- serial + button
bool HwMega::pollSerial() {
  bool abort = false;
  while (Serial.available()) {
    const char c = (char)Serial.read();
    if (c == '!') { abort = true; continue; }
    if (lineReady_) continue;  // previous line not taken yet: drop
    if (c == '\n' || c == '\r') {
      if (lineLen_) { line_[lineLen_] = 0; lineReady_ = true; }
    } else if (lineLen_ < sizeof(line_) - 1) {
      line_[lineLen_++] = c;
    }
  }
  return abort;
}

bool HwMega::takeAbort() {
  const bool a = abortSeen_;
  abortSeen_ = false;
  return a;
}

bool HwMega::readLine(char* out, uint8_t cap) {
  if (pollSerial()) abortSeen_ = true;
  pollButton();
  if (!lineReady_) return false;
  strncpy(out, line_, cap - 1);
  out[cap - 1] = 0;
  lineReady_ = false;
  lineLen_ = 0;
  return true;
}

void HwMega::pollButton() {
  const bool now = digitalRead(PIN_BUTTON);
  const uint32_t t = ::millis();
  if (now != btnLast_) { btnLast_ = now; btnChangedMs_ = t; }
  if (now != btnStable_ && t - btnChangedMs_ > 30) {
    btnStable_ = now;
    if (!now) btnPressed_ = true;  // pressed = pulled to GND
  }
}

bool HwMega::takeButtonPress() {
  pollButton();
  const bool p = btnPressed_;
  btnPressed_ = false;
  return p;
}

void HwMega::updateLed(RobotState st) {
  const uint32_t t = ::millis();
  bool on;
  switch (st) {
    case ST_RUN: case ST_SESSION: on = (t / 100) % 2; break;   // fast blink
    case ST_SUCCESS: on = true; break;                          // steady
    case ST_ERROR: on = (t / 150) % 8 < 3 && (t / 150) % 2 == 0; break;  // double blink
    default: on = (t / 1000) % 2; break;                        // slow blink
  }
  digitalWrite(PIN_LED, on);
}

// ---------------------------------------------------------------- drivers
DriverStatus HwMega::ping(Axis ax) {
  DriverStatus st;
  TMC2209Stepper& d = drv_[ax];
  const uint32_t ioin = d.IOIN();
  st.present = !d.CRCerror && ioin != 0;
  st.version = (uint8_t)(ioin >> 24);
  st.ms1 = (ioin >> 2) & 1;
  st.ms2 = (ioin >> 3) & 1;
  st.diagIoin = (ioin >> 4) & 1;
  st.diagPin = digitalRead(kPins[ax].diag);
  if (st.present) {
    st.gstat = d.GSTAT();
    st.ifcnt = d.IFCNT();
  }
  return st;
}

bool HwMega::configure(Axis ax, const DriverSetup& c) {
  TMC2209Stepper& d = drv_[ax];
  d.begin();                 // GCONF: pdn_disable=1 (UART owns PDN_UART), mstep_reg_select=1
  d.senddelay(2);            // multi-node bus: SENDDELAY >= 2 (datasheet p. 19)
  d.GSTAT(0x07);             // clear reset / drv_err / uv_cp flags
  d.I_scale_analog(false);   // internal reference: the VREF pot no longer matters
  d.internal_Rsense(false);  // external 0.11 ohm sense resistors
  d.en_spreadCycle(false);   // StealthChop: StallGuard4 only works there (datasheet §11)
  d.multistep_filt(true);
  d.toff(kToffOn);           // power stage on/off is the EN pin, for every axis
  d.intpol(true);
  d.microsteps(s_.microsteps);
  d.rms_current(c.runMa, c.holdPct / 100.0f);
  d.pwm_autoscale(true);
  d.pwm_autograd(true);
  d.TPWMTHRS(0);             // StealthChop at all speeds
  d.TCOOLTHRS(c.tcoolthrs);  // DIAG only above the StallGuard speed
  d.SGTHRS(c.sgthrs);
  d.TPOWERDOWN(20);
  // Read back what can be read (IHOLD_IRUN, TCOOLTHRS, SGTHRS are write-only).
  const uint32_t g = d.GCONF();
  if (d.CRCerror) return false;
  const bool gOk = ((g >> 6) & 1) && ((g >> 7) & 1) && !(g & 1) && !((g >> 2) & 1);  // pdn_disable, mstep_reg_select, !i_scale_analog, !en_spreadcycle
  const uint32_t ch = d.CHOPCONF();
  if (d.CRCerror) return false;
  return gOk && ((ch >> 24) & 0x0F) == mresFor(s_.microsteps);  // MRES is CHOPCONF bits 24..27
}

// GSTAT is read-and-write-1-to-clear (datasheet p. 24): reading leaves it
// set, so a reset stays visible until configure() clears it. TMCStepper's
// read() flags a reply that never came as a CRC error (all zeros fail its
// crc == 0 test) and tries twice; three of those.
uint8_t HwMega::gstat(Axis ax) {
  TMC2209Stepper& d = drv_[ax];
  for (uint8_t attempt = 0; attempt < 3; ++attempt) {
    const uint8_t g = d.GSTAT();
    if (!d.CRCerror) return g & (GSTAT_RESET | GSTAT_DRV_ERR | GSTAT_UV_CP);
  }
  return GSTAT_NO_REPLY;
}

void HwMega::enable(Axis ax, bool on) {
  digitalWrite(kPins[ax].en, on ? LOW : HIGH);  // EN is active low
}

// ---------------------------------------------------------------- SG sampling
void HwMega::sgStart(uint8_t) {
  sgState_ = SG_IDLE;
  sgMin_ = 0xFFFF;
  sgLast_ = micros();
}

// One SG_RESULT read in flight at a time. A sample is attributed to the step
// index at which it was requested; only cruise-speed samples count towards
// the minimum and go to the calibration sink (StallGuard is unreliable at
// low speed, datasheet §11.5).
void HwMega::sgPoll(uint8_t ax, uint32_t stepIndex, bool cruise, bool trace, SgSink* sink) {
  const uint32_t now = micros();
  if (sgState_ == SG_IDLE) {
    if (now - sgLast_ < 2000) return;
    sgReqStep_ = stepIndex;
    sgReqCruise_ = cruise;
    while (TMC_SERIAL.available()) TMC_SERIAL.read();
    uint8_t req[4];
    tmcReadRequest(ax, kRegSgResult, req);
    TMC_SERIAL.write(req, 4);  // buffered, interrupt-driven: doesn't block the step loop
    sgParser_.start(kRegSgResult);
    sgT0_ = now;
    sgState_ = SG_WAIT;
    return;
  }
  while (TMC_SERIAL.available()) {
    if (sgParser_.feed((uint8_t)TMC_SERIAL.read())) {
      if (sgParser_.ok()) {
        const uint16_t v = sgParser_.value() & 0x3FF;
        if (sgReqCruise_) {
          if (v < sgMin_) sgMin_ = v;
          if (sink) sink->sample(sgReqStep_, v);
        }
        if (trace && Serial.availableForWrite() > 24) {
          Serial.print(F("SG,"));
          Serial.print("ABCK"[ax]);
          Serial.print(',');
          Serial.print(sgReqStep_ / s_.microsteps);
          Serial.print(',');
          Serial.println(v);
        }
      }
      sgState_ = SG_IDLE;
      sgLast_ = now;
      return;
    }
  }
  if (now - sgT0_ > 5000) { sgState_ = SG_IDLE; sgLast_ = now; }  // no reply: try again later
}

void HwMega::sgFinish() {
  // Let an outstanding reply finish so it can't collide with the next
  // TMCStepper transaction on the shared wire.
  const uint32_t t0 = micros();
  while (sgState_ == SG_WAIT && micros() - t0 < 6000) {
    while (TMC_SERIAL.available())
      if (sgParser_.feed((uint8_t)TMC_SERIAL.read())) sgState_ = SG_IDLE;
  }
  sgState_ = SG_IDLE;
}

// ---------------------------------------------------------------- motion
MoveResult HwMega::move(const MoveRequest& r) {
  MoveResult res;
  if (r.steps == 0) return res;
  const AxisPins& p = kPins[r.axis];
  const bool logicalFwd = r.steps > 0;
  const bool motorFwd = logicalFwd != (bool)s_.ax[r.axis].invert;
  digitalWrite(p.dir, motorFwd ? HIGH : LOW);
  delayMicroseconds(5);  // DIR-to-STEP setup is 20 ns min (datasheet p. 63)
  if (digitalRead(p.diag) == HIGH) { res.diagHighAtStart = true; return res; }

  const uint32_t n = (uint32_t)(r.steps > 0 ? r.steps : -r.steps);
  const int8_t sign = r.steps > 0 ? 1 : -1;
  Ramp ramp;
  ramp.begin(n, r.startSps, r.maxSps, r.accelSps2);
  if (r.sampleSG) sgStart(r.axis);
  noInterrupts();
  g_diag[r.axis] = false;
  interrupts();

  const uint32_t t0 = ::millis();
  uint32_t next = micros();
  uint32_t i = 0;
  for (; i < n; ++i) {
    const uint32_t dt = ramp.nextIntervalUs();
    while ((int32_t)(micros() - next) < 0) {
      if (r.sampleSG) {
        const bool cruise = i >= ramp.accelSteps() && i + ramp.accelSteps() < n;
        sgPoll(r.axis, i, cruise, r.traceSG, r.sgSink);
      }
    }
    if ((int32_t)(micros() - next) > (int32_t)dt) next = micros();  // fell behind: don't sprint
    digitalWrite(p.step, HIGH);
    delayMicroseconds(2);  // STEP high >= 100 ns (datasheet p. 63)
    digitalWrite(p.step, LOW);
    next += dt;

    if (i < r.ignoreStallSteps) {
      g_diag[r.axis] = false;
    } else if (r.stopOnStall && g_diag[r.axis]) {
      res.stalled = true;
      ++i;
      break;
    }
    if ((i & 31) == 0) {
      if (pollSerial()) { res.aborted = true; ++i; break; }
      pollButton();
      if (::millis() - t0 > r.timeoutMs) { res.timedOut = true; ++i; break; }
    }
  }
  if (r.sampleSG) sgFinish();
  res.stepsDone = sign * (int32_t)(i < n ? i : n);
  res.sgMin = sgMin_;
  if (!r.sampleSG) res.sgMin = 0xFFFF;
  return res;
}

// ---------------------------------------------------------------- EEPROM
uint8_t HwMega::storeRead(uint16_t addr) { return EEPROM.read(addr); }
void HwMega::storeWrite(uint16_t addr, uint8_t v) { EEPROM.update(addr, v); }  // skips unchanged bytes
uint16_t HwMega::storeSize() { return EEPROM.length(); }
