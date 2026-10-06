// Builds core::Settings from config.h. Plain C++ (config.h is only
// #defines), so the host tests run against the same defaults as the Mega.
#pragma once
#include "../../config.h"
#include "settings.h"

namespace core {

inline Settings makeSettings() {
  Settings s;
  s.fullStepsPerRev = CFG_FULL_STEPS_PER_REV;
  s.microsteps = CFG_MICROSTEPS;
  s.dialGear = CFG_DIAL_GEAR;
  s.keyGear = CFG_KEY_GEAR;
  s.positions = CFG_POSITIONS;
  s.axesMask = CFG_AXES_MASK;
  const uint8_t inv[AX_COUNT] = {CFG_INVERT_A, CFG_INVERT_B, CFG_INVERT_C, CFG_INVERT_KEY};
  const uint8_t sg[AX_COUNT] = {CFG_SGTHRS_A, CFG_SGTHRS_B, CFG_SGTHRS_C, CFG_SGTHRS_KEY};
  for (uint8_t a = 0; a < AX_COUNT; ++a) {
    AxisCfg& x = s.ax[a];
    const bool key = a == AX_KEY;
    x.invert = inv[a];
    x.runMa = key ? CFG_KEY_RUN_MA : CFG_DIAL_RUN_MA;
    x.holdPct = key ? CFG_KEY_HOLD_PCT : CFG_DIAL_HOLD_PCT;
    x.sgthrs = sg[a];
    x.rps = key ? CFG_KEY_RPS : CFG_DIAL_RPS;
    x.startRps = CFG_START_RPS;
    x.accelRps2 = CFG_ACCEL_RPS2;
  }
  s.seatDialDeg = CFG_SEAT_DIAL_DEG;
  s.seatRps = CFG_SEAT_RPS;
  s.seatMa = CFG_SEAT_MA;
  s.dialHome[0] = CFG_HOME_MODE_A;
  s.dialHome[1] = CFG_HOME_MODE_B;
  s.dialHome[2] = CFG_HOME_MODE_C;
  s.homeMaxDialDeg = CFG_HOME_MAX_DIAL_DEG;
  s.homeBackoffFull = CFG_HOME_BACKOFF_FULL;
  s.homeRepeatTolFull = CFG_HOME_REPEAT_TOL_FULL;
  s.homeOffsetFull[0] = CFG_HOME_OFFSET_A;
  s.homeOffsetFull[1] = CFG_HOME_OFFSET_B;
  s.homeOffsetFull[2] = CFG_HOME_OFFSET_C;
  s.dialApproachFull = CFG_DIAL_APPROACH_FULL;
  s.keyHome = CFG_KEY_HOME_MODE;
  s.keyHomeSearchDeg = CFG_KEY_HOME_SEARCH_DEG;
  s.keyHomeExtraDeg = CFG_KEY_HOME_EXTRA_DEG;
  s.keyLearnMaxDeg = CFG_KEY_LEARN_MAX_DEG;
  s.keyLearnRepeats = CFG_KEY_LEARN_REPEATS;
  s.keyLearnSpreadDeci = CFG_KEY_LEARN_SPREAD_DECI;
  s.keyTargetMarginDeci = CFG_KEY_TARGET_MARGIN_DECI;
  s.keySuccessMinDeci = CFG_KEY_SUCCESS_MIN_DECI;
  s.keyCleanTolDeci = CFG_KEY_CLEAN_TOL_DECI;
  s.keyEarlyTolDeci = CFG_KEY_EARLY_TOL_DECI;
  s.recheckEvery = CFG_RECHECK_EVERY;
  s.recheckHomeTolFull = CFG_RECHECK_HOME_TOL_FULL;
  s.recheckNTolDeci = CFG_RECHECK_N_TOL_DECI;
  s.maxConsecutiveEarly = CFG_MAX_CONSECUTIVE_EARLY;
  s.resumeFromCheckpoint = CFG_RESUME_FROM_CHECKPOINT;
  s.stallIgnoreFull = CFG_STALL_IGNORE_FULL;
  s.sgMinRps = CFG_SG_MIN_RPS;
  s.fclkHz = CFG_FCLK_HZ;
  s.labelAtHome[0] = CFG_LABEL_AT_HOME_A;
  s.labelAtHome[1] = CFG_LABEL_AT_HOME_B;
  s.labelAtHome[2] = CFG_LABEL_AT_HOME_C;
  s.labelStep[0] = CFG_LABEL_STEP_A;
  s.labelStep[1] = CFG_LABEL_STEP_B;
  s.labelStep[2] = CFG_LABEL_STEP_C;
  return s;
}

}  // namespace core
