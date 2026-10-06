// Simulated robot + lock for host tests. Models, per the design in
// control/sequence.md and control/wiring.md:
//  - 3 dial wheels that turn clockwise without limit and stop turning
//    anticlockwise at one point per turn (as Paul found on the real dials,
//    2026-10-06), 20 detents, and a spring-loaded plug that only engages
//    after some turning (the seat routine). Logical + = clockwise;
//  - the key: a rest stop at 0 (optional), a stop at N for a wrong
//    combination, further for false sets, and the bolt end for the right one;
//  - StallGuard: SG_RESULT per microstep. Dials: a baseline with a ripple at
//    the click period (lower climbing out of a click, higher falling in);
//    key: flat on its free travel; at a stop: low, after a lag of a couple of
//    full steps. DIAG fires when SG_RESULT <= 2 * SGTHRS (as configured), only
//    above a speed (TCOOLTHRS). Cruise-speed samples go to the move's SgSink. The rotor follows the field
//    elastically up to 2 full steps of lag; pushed further into a stop it
//    slips a pole (falls back 4 full steps = one electrical cycle), as a
//    real stepper does at the stop when nothing stops it (e.g. the slow seat).
// It also polices the firmware: dial moves with the key out, unbounded
// moves, moves without a timeout, pressing into a stop with stall detection
// off.
#pragma once
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <set>
#include <string>
#include <vector>

#include "../safe_robot/src/core/hal.h"
#include "../safe_robot/src/core/ramp.h"

struct SimHal : public core::Hal {
  // ---- world parameters (logical microsteps; 16 usteps/full step)
  int32_t usPerPos = 320;          // 200 full steps * 16 * 2 (gear) / 20
  int32_t turn = 6400;             // usteps per dial turn
  int32_t detentPhase[3] = {140, 150, 130};  // physical position of detent 0
  int32_t detentTol = 80;          // within this of a detent = "on" it
  uint8_t secret[3] = {7, 12, 3};  // the combination, detent indices from the stop
  std::set<int> falseSets;         // comboKey(a,b,c) that give a false set
  bool keyRestStop = true;
  int32_t keyN = 889;              // ~100 deg at 3200 usteps/rev
  int32_t keyFalseExtra = 53;      // ~6 deg
  int32_t keyOpen = 1778;          // ~200 deg: bolt end
  int32_t keyObstruction = -1;     // if >=0: key stops here (anomaly injection)
  bool dialHasStop[3] = {true, true, true};
  float sgMinSps = 0.3f * 3200;    // DIAG enabled only above this speed
  uint32_t seed = 12345;
  int32_t lagMin = 20, lagSpan = 11;  // StallGuard detection lag, usteps (1.25-1.9 full steps)
  int32_t sgDialBase = 300, sgDetentAmp = 25, sgNoise = 4, sgKeyBase = 240, sgAtStop = 20, sgUnloaded = 340;
  // ---- driver/bus faults
  bool present[4] = {true, true, true, true};
  bool diagStuck[4] = {false, false, false, false};
  bool configFails = false;
  int abortAtMove = -1;            // abort the Nth move (0-based)
  // ---- state
  // wheel0: angle (from the stop, clockwise) while the plug is out; off: field
  // minus rotor; floor: the stop the rotor is above, in field-rotor units.
  struct Dial { bool engaged = false; int32_t engageLeft = 300; int32_t wheel0 = 3000; int32_t off = 0; int32_t floor = 0; } dial[3];
  int32_t cmd[4] = {0, 0, 0, 0};   // field (commanded) position per axis
  int32_t keyOff = 0;              // key rotor offset from its field (pole slips)
  static const int32_t kSlip = 32; // 2 full steps: beyond this the rotor slips a pole
  bool enabled[4] = {false, false, false, false};
  uint8_t sgthrs[4] = {0, 0, 0, 0};  // as last configured
  uint32_t now = 0;
  int moveCount = 0;
  std::vector<std::string> lines;
  std::vector<core::MoveRequest> moves;
  std::vector<std::string> violations;
  uint8_t eeprom[4096];
  bool echo = false;

  SimHal() { std::memset(eeprom, 0xFF, sizeof(eeprom)); }

  static int comboKey(int a, int b, int c) { return a * 400 + b * 20 + c; }
  uint32_t rnd() { seed = seed * 1103515245u + 12345u; return (seed >> 16) & 0x7FFF; }

  // Wheel angle (usteps clockwise from the stop, 0..turn-1) of dial d.
  int32_t wheel(int d) const {
    const Dial& dl = dial[d];
    if (!dl.engaged) return dl.wheel0;
    const int32_t raw = cmd[d] - dl.off;
    if (dialHasStop[d]) return (raw < dl.floor ? dl.floor : raw) - dl.floor;
    return ((raw % turn) + turn) % turn;
  }
  int detentOf(int d) const {
    const int32_t p = wheel(d) - detentPhase[d];
    const int32_t k = (int32_t)std::lround((double)p / usPerPos);
    if (k < 0 || k > 20 || std::abs(p - k * usPerPos) > detentTol) return -1;
    return (int)(k % 20);
  }
  int32_t keyLimit() const {
    if (keyObstruction >= 0) return keyObstruction;
    int k[3];
    for (int d = 0; d < 3; ++d) { k[d] = detentOf(d); if (k[d] < 0) return keyN; }
    if (k[0] == secret[0] && k[1] == secret[1] && k[2] == secret[2]) return keyOpen;
    if (falseSets.count(comboKey(k[0], k[1], k[2]))) return keyN + keyFalseExtra;
    return keyN;
  }
  int32_t keyPhys() const {
    int32_t p = cmd[3] - keyOff;
    const int32_t hi = keyLimit();
    if (p > hi) p = hi;
    if (keyRestStop && p < 0) p = 0;
    return p;
  }

  // Unit taken off and put back: plugs pop out, key back at rest.
  void reseat() {
    for (int d = 0; d < 3; ++d) {
      dial[d].wheel0 = wheel(d);
      dial[d].floor = 0;
      dial[d].engaged = false;
      dial[d].engageLeft = 1 + (int32_t)(rnd() % 790);  // within the 45-deg seat turn
    }
    cmd[3] = 0;
    keyOff = 0;
  }
  // A dial wheel slips relative to its motor by k positions (unit moved).
  void slip(int d, int k) { dial[d].off += k * usPerPos; }

  // ---- Hal
  core::DriverStatus ping(core::Axis ax) override {
    core::DriverStatus st;
    st.present = present[ax];
    st.version = present[ax] ? 0x21 : 0;
    st.ms1 = present[ax] && (ax == core::AX_B || ax == core::AX_KEY);
    st.ms2 = present[ax] && (ax == core::AX_C || ax == core::AX_KEY);
    st.diagPin = st.diagIoin = diagStuck[ax];
    return st;
  }
  bool configure(core::Axis ax, const core::DriverSetup& s) override {
    if (s.runMa > 1200) violations.push_back("current above ceiling");
    sgthrs[ax] = s.sgthrs;
    return !configFails;
  }
  void enable(core::Axis ax, bool on) override { enabled[ax] = on; }
  uint32_t millis() override { return now; }
  void emit(const char* line) override {
    lines.push_back(line);
    if (echo) std::printf("    | %s\n", line);
  }
  uint8_t storeRead(uint16_t a) override { return eeprom[a]; }
  void storeWrite(uint16_t a, uint8_t v) override { eeprom[a] = v; }
  uint16_t storeSize() override { return sizeof(eeprom); }

  core::MoveResult move(const core::MoveRequest& r) override {
    moves.push_back(r);
    core::MoveResult res;
    const int ax = r.axis;
    if (r.timeoutMs == 0) violations.push_back("move without timeout");
    if (std::abs(r.steps) > (ax == 3 ? 3000 : 8000)) violations.push_back("move over its bound");
    if (!enabled[ax]) violations.push_back("move on a disabled driver");
    if (ax < 3 && std::abs(keyPhys()) > 20) violations.push_back("dial moved with the key out");
    if (diagStuck[ax]) { res.diagHighAtStart = true; return res; }
    if (abortAtMove >= 0 && moveCount == abortAtMove) { ++moveCount; res.aborted = true; return res; }
    ++moveCount;
    const int dir = r.steps >= 0 ? 1 : -1;
    const int32_t n = std::abs(r.steps);
    core::Ramp ramp;
    ramp.begin((uint32_t)n, r.startSps, r.maxSps, r.accelSps2);
    const int32_t acc = (int32_t)ramp.accelSteps();
    const int32_t lag = lagMin + (int32_t)(rnd() % lagSpan);
    int32_t blocked = 0;
    uint16_t sgMin = 0xFFFF;
    res.stepsDone = r.steps;
    for (int32_t i = 0; i < n; ++i) {
      bool isBlocked;
      bool unloaded = false;
      if (ax < 3) {
        Dial& dl = dial[ax];
        if (!dl.engaged) {
          cmd[ax] += dir;
          if (--dl.engageLeft <= 0) { dl.engaged = true; dl.off = cmd[ax] - dl.wheel0; dl.floor = 0; }
          isBlocked = false;
          unloaded = true;
        } else {
          cmd[ax] += dir;
          if (dialHasStop[ax]) {
            // Clockwise past the stop point: the next stop is one turn on.
            while (cmd[ax] - dl.off >= dl.floor + turn) dl.floor += turn;
            if (cmd[ax] - dl.off < dl.floor - kSlip) dl.off -= 64;  // pole slip at the stop
          }
          const int32_t raw = cmd[ax] - dl.off;
          isBlocked = dialHasStop[ax] && raw < dl.floor && dir < 0;
        }
      } else {
        cmd[ax] += dir;
        const int32_t hi = keyLimit();
        if (cmd[ax] - keyOff > hi + kSlip) keyOff += 64;
        else if (keyRestStop && cmd[ax] - keyOff < -kSlip) keyOff -= 64;
        const int32_t raw = cmd[ax] - keyOff;
        isBlocked = (raw > hi && dir > 0) || (keyRestStop && raw < 0 && dir < 0);
      }
      if (isBlocked) ++blocked; else blocked = 0;
      if (isBlocked && !r.stopOnStall) violations.push_back("pressed into a stop with stall detection off");
      // SG_RESULT now: low once the load has built up against a stop.
      int32_t sg;
      if (blocked >= lag) sg = sgAtStop;
      else if (unloaded) sg = sgUnloaded;
      else if (ax < 3) {
        const double ph = 2 * M_PI * (wheel(ax) - detentPhase[ax]) / usPerPos;
        sg = sgDialBase - (int32_t)std::lround(dir * sgDetentAmp * std::sin(ph));
      } else {
        sg = sgKeyBase;
      }
      sg += (int32_t)(rnd() % (2 * sgNoise + 1)) - sgNoise;
      if (sg < 0) sg = 0;
      const bool cruise = i >= acc && i + acc < n;
      if (r.sampleSG && cruise && (i + 1) % 16 == 0) {
        if (sg < sgMin) sgMin = (uint16_t)sg;
        if (r.sgSink) r.sgSink->sample((uint32_t)i, (uint16_t)sg);
      }
      const bool diagOn = r.stopOnStall && i >= r.ignoreStallSteps && ramp.speedAt((uint32_t)i) >= sgMinSps;
      if (diagOn && sg <= 2 * (int32_t)sgthrs[ax]) {
        res.stalled = true;
        res.stepsDone = dir * (i + 1);
        break;
      }
    }
    res.sgMin = r.sampleSG ? sgMin : 0xFFFF;
    now += (uint32_t)(1000.0f * std::abs(res.stepsDone) / r.maxSps) + 5;
    return res;
  }

  // ---- helpers for tests
  int count(const char* prefix) const {
    int c = 0;
    for (auto& l : lines) if (l.rfind(prefix, 0) == 0) ++c;
    return c;
  }
  bool has(const char* prefix) const { return count(prefix) > 0; }
  std::string last(const char* prefix) const {
    for (auto it = lines.rbegin(); it != lines.rend(); ++it) if (it->rfind(prefix, 0) == 0) return *it;
    return "";
  }
};
