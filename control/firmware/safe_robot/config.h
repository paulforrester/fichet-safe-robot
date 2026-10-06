// ============================================================================
// config.h — EVERY value that isn't measured yet lives here, in one block.
// Each one says where it came from and which bench stage
// (control/bringup.md) measures it. Bench values can be tried live with the
// serial `set` command (RAM only) and then copied here.
//
// Units: "full steps" are motor full steps (200/rev assumed, see below);
// rps = motor revolutions per second; deci = tenths of a degree.
// Dial "away" = turning away from the dial's home stop. Key "+" = clockwise
// seen from in front of the safe (the way the key unlocks).
// ============================================================================
#pragma once

// ---- Motor and drivetrain --------------------------------------------------
// ASSUMPTION: 1.8 deg/step (200/rev). Not yet confirmed on the 17HE19-2004S's
// data sheet. Bench stage 2 checks it (one commanded rev returns to a mark).
#define CFG_FULL_STEPS_PER_REV   200
#define CFG_MICROSTEPS           16     // MRES over UART; interpolated to 256 by the driver
#define CFG_DIAL_GEAR            2      // 14T pinion -> 28T dial gear (cad/dial_unit_housing.scad)
#define CFG_KEY_GEAR             1      // key turner is direct drive
#define CFG_POSITIONS            20     // positions per dial wheel: 20 clicks per turn (Paul, 2026-10-06)

// Drivers fitted: A=1, B=2, C=4, key=8. 15 = all (needed for `start`). Bench
// stages with fewer drivers use `set axes <mask>` instead of editing this.
#define CFG_AXES_MASK            15

// ---- Directions: motor sense UNKNOWN until bench stages 4b and 5b -----------
// 1 = flip the motor direction. Dials: set so that a positive jog turns the
// dial CLOCKWISE seen from the front. That is away from the home stop: every
// dial turns clockwise without limit and stops only anticlockwise (Paul,
// 2026-10-06). Key: set so that a positive jog turns the key CLOCKWISE (the
// way it opens). The dial motors turn opposite to the dials (external
// gears), so the three dials probably share one value.
#define CFG_INVERT_A             0
#define CFG_INVERT_B             0
#define CFG_INVERT_C             0
#define CFG_INVERT_KEY           0

// ---- Currents (control/wiring.md §7) ---------------------------------------
#define CFG_DIAL_RUN_MA          1000   // ~1 A RMS until the dial torque is measured
#define CFG_DIAL_HOLD_PCT        50
#define CFG_KEY_RUN_MA           600    // start; stage 5 sets it to 2x the measured minimum
#define CFG_KEY_HOLD_PCT         50
#define CFG_SEAT_MA              600    // lower current while seating the plugs

// ---- Speeds ------------------------------------------------------------------
// StallGuard4 needs speed: below ~0.3 rev/s this motor gives too little back
// EMF (datasheet §11.5 rule of thumb, with 0.55-0.59 N.m / 2 A / ~1.4 ohm —
// the resistance is from a vendor listing, not confirmed). 1 rev/s is ~3x
// that. Tune in bench stage 3.
#define CFG_DIAL_RPS             1.0f
#define CFG_KEY_RPS              1.0f
#define CFG_START_RPS            0.15f
#define CFG_ACCEL_RPS2           5.0f
#define CFG_SEAT_RPS             0.1f   // slow, so the plug can drop into the star (stage 4)
#define CFG_SG_MIN_RPS           0.4f   // DIAG only enabled above this speed (TCOOLTHRS)
#define CFG_STALL_IGNORE_FULL    2      // ignore DIAG for the first full steps of a move

// ---- StallGuard thresholds: UNKNOWN, bench stage 3 ---------------------------
// 0 = not tuned: `start`, `resume` and homing refuse to run. Higher = more
// sensitive (stall when SG_RESULT <= 2*SGTHRS, datasheet §5.3).
#define CFG_SGTHRS_A             0
#define CFG_SGTHRS_B             0
#define CFG_SGTHRS_C             0
#define CFG_SGTHRS_KEY           0

// ---- Seat and home (dials) -----------------------------------------------------
#define CFG_SEAT_DIAL_DEG        45     // at most 1/8 dial turn (control/sequence.md); turned clockwise
// Each dial has a hard stop turning anticlockwise (Paul, 2026-10-06): home on it.
// (1 = no stop: positions count from wherever the seat leaves the dial, and a
// run can't resume after a re-seat. Kept for completeness.)
#define CFG_HOME_MODE_A          0
#define CFG_HOME_MODE_B          0
#define CFG_HOME_MODE_C          0
#define CFG_HOME_MAX_DIAL_DEG    414    // 1.15 dial turns: bound of the homing move
#define CFG_HOME_BACKOFF_FULL    40     // 2 positions between the two homing passes
#define CFG_HOME_REPEAT_TOL_FULL 8      // the passes must agree within 0.4 position
// UNKNOWN: from the stall point to the middle of position 1, full steps away
// from the stop. Stage 4 measures it (detent scan). 10 = half a position.
#define CFG_HOME_OFFSET_A        10
#define CFG_HOME_OFFSET_B        10
#define CFG_HOME_OFFSET_C        10
#define CFG_DIAL_APPROACH_FULL   0      // >0: always finish dial moves going away from the stop

// ---- Key -----------------------------------------------------------------------
// The key can't turn anticlockwise at all from its insertion position (Paul,
// 2026-10-06): that rest stop is the key's home, re-found every attempt (0).
// 1 = return by step count instead (for a key without a rest stop).
#define CFG_KEY_HOME_MODE        0
#define CFG_KEY_HOME_SEARCH_DEG  30     // session start: anticlockwise bound to find the rest stop
#define CFG_KEY_HOME_EXTRA_DEG   15     // retract: anticlockwise bound past the angle reached
#define CFG_KEY_LEARN_MAX_DEG    160    // Paul measured ~100 deg to the stop
#define CFG_KEY_LEARN_REPEATS    3
#define CFG_KEY_LEARN_SPREAD_DECI 50    // learn tries must agree within 5.0 deg
// Classification (all relative to this session's learned stop N). Set the
// clean band to ~3x the learn spread measured in stage 5.
#define CFG_KEY_TARGET_MARGIN_DECI 150  // each try drives to N + 15 deg ("N + ~10%", sequence.md)
#define CFG_KEY_SUCCESS_MIN_DECI 100    // N + 10 deg or more = success: stop and report
#define CFG_KEY_CLEAN_TOL_DECI   40     // up to N + 4 deg = clean fail
#define CFG_KEY_EARLY_TOL_DECI   80     // below N - 8 deg = anomaly (retry, then pause)

// ---- Run -------------------------------------------------------------------------
#define CFG_RECHECK_EVERY        200    // re-home + re-learn every this many attempts
#define CFG_RECHECK_HOME_TOL_FULL 8     // home may differ by up to 0.4 position
#define CFG_RECHECK_N_TOL_DECI   50     // N may move by up to 5 deg
#define CFG_MAX_CONSECUTIVE_EARLY 3
#define CFG_RESUME_FROM_CHECKPOINT 1    // after power loss, redo attempts since the last re-check

// ---- Door numbering (only used to print the success in door numbers) ----------
// UNKNOWN: Paul can fill these in if the door has marks. Position 1 = home.
#define CFG_LABEL_AT_HOME_A      1
#define CFG_LABEL_AT_HOME_B      1
#define CFG_LABEL_AT_HOME_C      1
#define CFG_LABEL_STEP_A         1      // +1 or -1 per position away from home
#define CFG_LABEL_STEP_B         1
#define CFG_LABEL_STEP_C         1

// ---- Electrical (control/wiring.md) ----------------------------------------------
#define CFG_R_SENSE              0.11f  // BTT TMC2209 V1.3 sense resistors (schematic R3/R5)
#define CFG_UART_BAUD            115200 // TMC2209: 9000 baud .. fCLK/16 (datasheet §4.1)
#define CFG_FCLK_HZ              12000000UL  // internal clock, nominal (datasheet)
#define CFG_USB_BAUD             115200
