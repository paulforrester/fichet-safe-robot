// Hardware abstraction used by the core. Plain C++, no Arduino headers.
// The Mega implementation is safe_robot/hw_mega.cpp; the host tests use a
// simulated lock (control/firmware/test/sim_hal.h).
#pragma once
#include <stdint.h>

namespace core {

enum Axis : uint8_t { AX_A = 0, AX_B = 1, AX_C = 2, AX_KEY = 3, AX_COUNT = 4 };

// Receives SG_RESULT samples taken at cruise speed during a move (StallGuard
// is unreliable at low speed, datasheet §11.5). stepIndex = microsteps since
// the move started.
class SgSink {
 public:
  virtual ~SgSink() {}
  virtual void sample(uint32_t stepIndex, uint16_t sg) = 0;
};

// One bounded move. Steps are microsteps in the axis's *logical* direction:
// dials: + = away from the home stop; key: + = clockwise seen from the front.
// The hardware layer maps logical to motor direction (Settings::invert).
struct MoveRequest {
  Axis axis = AX_A;
  int32_t steps = 0;          // signed; |steps| is the hard bound of the move
  float startSps = 1;         // microsteps/s at the first step
  float maxSps = 1;           // cruise speed, microsteps/s
  float accelSps2 = 1;        // microsteps/s^2
  bool stopOnStall = true;    // stop at the first DIAG pulse
  bool sampleSG = false;      // read SG_RESULT over UART while moving (cruise min is reported)
  bool traceSG = false;       // also print every sample as "SG,axis,fullstep,value" (bench)
  SgSink* sgSink = nullptr;   // also hand cruise samples to this (calibration)
  uint16_t ignoreStallSteps = 0;  // ignore DIAG for this many microsteps at the start
  uint32_t timeoutMs = 1000;  // wall-clock bound
};

struct MoveResult {
  int32_t stepsDone = 0;   // signed, logical; equals steps unless stopped early
  bool stalled = false;
  bool aborted = false;    // operator abort ('!' on serial)
  bool timedOut = false;
  bool diagHighAtStart = false;  // DIAG already high: wire off or driver error
  bool dirFailed = false;  // key: direction register didn't read back (UART)
  bool driverFault = false;  // set by the core, not the Hal: GSTAT showed a fault before or after the move
  uint16_t sgMin = 0xFFFF; // lowest SG_RESULT seen at cruise speed (0xFFFF = none)
};

// GSTAT bits (TMC2209 datasheet, GSTAT, p. 24), as Hal::gstat() returns them.
// configure() clears them; the driver sets them again.
enum GstatBits : uint8_t {
  GSTAT_RESET = 0x01,     // registers back at power-on values: VS (12 V) or VIO dropped out (DS §17)
  GSTAT_DRV_ERR = 0x02,   // power stage shut down: overtemperature or short (latched)
  GSTAT_UV_CP = 0x04,     // charge pump undervoltage now: power stage off (not latched)
  GSTAT_NO_REPLY = 0x80,  // not a GSTAT bit: the driver didn't answer the read
};

// Per-driver settings pushed over UART before a phase of motion.
struct DriverSetup {
  uint16_t runMa;
  uint8_t holdPct;   // hold current as % of run
  uint8_t sgthrs;    // StallGuard threshold (0 = never signals)
  uint32_t tcoolthrs;// DIAG enabled when TSTEP <= this (i.e. above a speed)
};

struct DriverStatus {
  bool present = false;  // answered with IOIN VERSION 0x21
  uint8_t version = 0;
  bool ms1 = false, ms2 = false;
  bool diagPin = false;  // Mega pin level
  bool diagIoin = false; // driver's own IOIN.DIAG
  uint8_t gstat = 0;
  uint8_t ifcnt = 0;
};

class Hal {
 public:
  virtual ~Hal() {}
  virtual DriverStatus ping(Axis ax) = 0;
  virtual bool configure(Axis ax, const DriverSetup& s) = 0;  // true = read-back OK; clears GSTAT
  // GSTAT of one driver (GstatBits; 0 = fine), or GSTAT_NO_REPLY. A driver
  // whose supply dropped out comes back with its power-on registers (no
  // current setting, no StallGuard, other microsteps) and nothing else shows
  // it, so the core reads this around every move (control/firmware/README.md,
  // "Driver resets").
  virtual uint8_t gstat(Axis ax) = 0;
  virtual void enable(Axis ax, bool on) = 0;
  virtual MoveResult move(const MoveRequest& r) = 0;  // blocking, bounded
  virtual uint32_t millis() = 0;
  virtual void emit(const char* line) = 0;            // one log line, no newline
  // Persistent bytes (EEPROM on the Mega).
  virtual uint8_t storeRead(uint16_t addr) = 0;
  virtual void storeWrite(uint16_t addr, uint8_t v) = 0;
  virtual uint16_t storeSize() = 0;
};

}  // namespace core
