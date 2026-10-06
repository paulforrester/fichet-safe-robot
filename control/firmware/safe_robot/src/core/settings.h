// Runtime settings. Filled from config.h by the sketch (makeSettings() in
// safe_robot.ino); the host tests fill it directly. Bench commands (`set`)
// can override fields in RAM; copy good values back into config.h.
#pragma once
#include <stdint.h>
#include "hal.h"

namespace core {

enum HomeMode : uint8_t { HOME_STALL = 0, HOME_NONE = 1 };
enum KeyHomeMode : uint8_t { KEYHOME_STALL_CCW = 0, KEYHOME_COUNT = 1 };

struct AxisCfg {
  uint8_t invert;     // 1 = flip motor direction for logical + (dials: away from stop; key: clockwise)
  uint16_t runMa;     // RMS run current
  uint8_t holdPct;    // hold current, % of run
  uint8_t sgthrs;     // StallGuard threshold; 0 = not tuned (runs refuse to start)
  float rps;          // cruise speed, motor rev/s
  float startRps;     // speed of the first step
  float accelRps2;    // motor rev/s^2
};

struct Settings {
  // Mechanics
  uint16_t fullStepsPerRev;  // motor full steps per revolution
  uint8_t microsteps;        // driver MRES
  uint8_t dialGear;          // motor turns per dial turn
  uint8_t keyGear;           // motor turns per key turn
  uint8_t positions;         // positions per dial wheel
  AxisCfg ax[AX_COUNT];
  uint8_t axesMask;          // drivers fitted: bit 0 = A, 1 = B, 2 = C, 3 = key (bench: fewer)
  // Seat (dials): slow, bounded turn so each spring-loaded plug drops into its star
  uint16_t seatDialDeg;
  float seatRps;
  uint16_t seatMa;
  // Dial homing
  uint8_t dialHome[3];         // HomeMode per dial
  uint16_t homeMaxDialDeg;     // bound of the homing move
  uint16_t homeBackoffFull;    // back-off between the two homing passes
  uint16_t homeRepeatTolFull;  // pass 2 must stall within backoff +/- this
  int16_t homeOffsetFull[3];   // stall point -> position 1, full steps away from the stop
  uint16_t dialApproachFull;   // >0: approach every target from the home side (anti-backlash)
  // Key
  uint8_t keyHome;             // KeyHomeMode
  uint16_t keyHomeSearchDeg;   // session start: CCW bound to find the rest stop
  uint16_t keyHomeExtraDeg;    // retract: CCW bound beyond the angle reached
  uint16_t keyLearnMaxDeg;     // bound when learning N
  uint8_t keyLearnRepeats;
  uint16_t keyLearnSpreadDeci; // max spread of the learn tries (0.1 deg)
  uint16_t keyTargetMarginDeci;// each try drives to N + this
  uint16_t keySuccessMinDeci;  // >= N + this is a success
  uint16_t keyCleanTolDeci;    // <= N + this is a clean fail
  uint16_t keyEarlyTolDeci;    // < N - this is an anomaly
  // Run
  uint16_t recheckEvery;        // attempts between re-checks (re-home + re-learn)
  uint16_t recheckHomeTolFull;  // allowed home discrepancy at a re-check
  uint16_t recheckNTolDeci;     // allowed change of N at a re-check
  uint8_t maxConsecutiveEarly;  // that many EARLY results in a row -> pause
  uint8_t resumeFromCheckpoint; // after power loss, restart from the last re-checked index
  uint16_t stallIgnoreFull;     // ignore DIAG over the first full steps of a move
  float sgMinRps;               // DIAG only enabled above this motor speed (sets TCOOLTHRS)
  uint32_t fclkHz;              // driver clock (internal, nominal 12 MHz)
  // Self-calibration (control/firmware/README.md, "Calibration")
  uint8_t sgAutocal;            // 1 = set SGTHRS every session from a free turn / free key travel
  uint8_t sgCalPct;             // stall = SG_RESULT down to this % of the free-running baseline
  uint16_t sgCalMinBase;        // a baseline below this can't be told from a stall: error
  uint8_t detentAutocal;        // 1 = find the clicks every session; position 1 = first click
  uint8_t detentMinAmp;         // click ripple (SG units) needed to trust it
  uint16_t keyCalDeg;           // key free-travel calibration move from rest (well short of N)
  // Door numbering, only for the success report
  uint8_t labelAtHome[3];       // door number at position 1
  int8_t labelStep[3];          // +1 or -1 per position away from the stop
};

// Derived quantities.
inline int32_t usPerMotorRev(const Settings& s) { return (int32_t)s.fullStepsPerRev * s.microsteps; }
inline int32_t usPerPosition(const Settings& s) { return usPerMotorRev(s) * s.dialGear / s.positions; }
inline int32_t usPerKeyRev(const Settings& s) { return usPerMotorRev(s) * s.keyGear; }
inline int32_t keyDeciToUs(const Settings& s, int32_t deci) { return deci * usPerKeyRev(s) / 3600; }
inline int32_t keyUsToDeci(const Settings& s, int32_t us) { return us * 3600 / usPerKeyRev(s); }
inline int32_t dialDegToUs(const Settings& s, int32_t deg) { return deg * usPerMotorRev(s) * s.dialGear / 360; }
// TCOOLTHRS for "DIAG on above v": TSTEP counts fCLK cycles per 1/256 microstep
// (datasheet TSTEP, p. 28), so at v rev/s TSTEP = fclk / (v * fullsteps * 256).
inline uint32_t tcoolthrsFor(const Settings& s, float rps) {
  return (uint32_t)((float)s.fclkHz / (rps * (float)s.fullStepsPerRev * 256.0f));
}
uint32_t positionHash(const Settings& s);  // settings that define dial positions

}  // namespace core
