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
// 1.8 deg/step (200/rev): confirmed in bench stage 2 (one commanded rev = one
// turn, Paul 2026-10-10).
#define CFG_FULL_STEPS_PER_REV   200
#define CFG_MICROSTEPS           16     // MRES over UART; interpolated to 256 by the driver
#define CFG_DIAL_GEAR            2      // 14T pinion -> 28T dial gear (cad/dial_unit_housing.scad)
#define CFG_KEY_GEAR             5      // key turner v2 (revision 2026-10-18.1): 12T pinion / 60T gear.
                                        // Direct drive (1) couldn't start the key back from its stop
                                        // (>= 0.98 N·m, Paul 2026-10-18)
#define CFG_POSITIONS            20     // positions per dial wheel: 20 clicks per turn (Paul, 2026-10-06)

// Drivers fitted: A=1, B=2, C=4, key=8. 15 = all (needed for `start`). Bench
// stages with fewer drivers use `set axes <mask>` instead of editing this.
#define CFG_AXES_MASK            15

// ---- Directions: dials measured (stage 4b.1, Paul 2026-10-10); key: stage 5 --
// 1 = flip the motor direction. Dials: set so that a positive jog turns the
// dial CLOCKWISE seen from the front. That is away from the home stop: every
// dial turns clockwise without limit and stops only anticlockwise (Paul,
// 2026-10-06). Key: set so that a positive jog turns the key CLOCKWISE (the
// way it opens). The dial motors turn opposite to the dials (external
// gears), so the three dials probably share one value.
// Bench 4b.1 (Paul, 2026-10-10): with 0, a positive jog turned the motor
// clockwise and every dial ANTICLOCKWISE (towards its stop), all three alike.
#define CFG_INVERT_A             1
#define CFG_INVERT_B             1
#define CFG_INVERT_C             1
#define CFG_INVERT_KEY           1      // direct drive turned the key clockwise with 0 (stage 5,
                                        // 2026-10-18); one gear pair reverses it. Stage 5 step 1 re-checks

// ---- Currents (control/wiring.md §7) ---------------------------------------
// Dials: 600 mA from the door test (bring-up 4b, Paul 2026-10-14): at 1000 mA
// homing failed its repeat check (HOMEREP); at 600 mA seat, calibration turn
// and homing passed on all three dials, free-running StallGuard ~4x above the
// stall level. The dial torque itself is still not measured.
#define CFG_DIAL_RUN_MA          600
#define CFG_DIAL_HOLD_PCT        50
#define CFG_KEY_RUN_MA           1000   // direct drive needed >= 500 mA (Paul, door, 2026-10-18). Geared 5:1 the
                                        // motor needs ~1/4 of the torque; stage 5 measures the minimum again
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
#define CFG_ACCEL_RPS2           5.0f   // dials
#define CFG_KEY_ACCEL_RPS2       20.0f  // key: direct drive, light; reaches cruise within ~5 full steps,
                                        // so its short moves have cruise-speed StallGuard readings
#define CFG_SEAT_RPS             0.1f   // slow, so the plug can drop into the star (stage 4)
#define CFG_SG_MIN_RPS           0.4f   // DIAG only enabled above this speed (TCOOLTHRS)
#define CFG_STALL_IGNORE_FULL    2      // ignore DIAG for the first full steps of a move

// ---- StallGuard thresholds ---------------------------------------------------
// With CFG_SG_AUTOCAL = 1 (default) these are only a fallback: every session
// measures each motor's free-running load and sets its own threshold, and the
// last calibration is kept in EEPROM. Without autocal: 0 = not tuned, so
// `start`, `resume` and homing refuse to run. Higher = more sensitive (stall
// when SG_RESULT <= 2*SGTHRS, datasheet §5.3).
#define CFG_SGTHRS_A             0
#define CFG_SGTHRS_B             0
#define CFG_SGTHRS_C             0
#define CFG_SGTHRS_KEY           0

// ---- Self-calibration (Paul's suggestion, 2026-10-06; datasheet §11.4) -------
// Every session: each dial makes one free clockwise turn (the dials turn
// clockwise without limit), the key turns CFG_KEY_CAL_DEG from rest. Their
// StallGuard readings set the thresholds, and the dials' 18-degree click
// ripple sets where position 1 is. `calibrate` does the same as a separate
// step and prints the results. Bench stages 3-4 check the numbers.
#define CFG_SG_AUTOCAL           1
#define CFG_SG_CAL_PCT           50     // ASSUMPTION: stall = SG down to 50 % of the free-running low; stage 3 checks
// Key (v0.7.2, door 2026-10-18, direct drive at 1000 mA): free turn reads
// 200-244; from ~50 deg the key meets graduated resistance up to its ~100
// deg stop, and there it dipped to ~142 every 4 full steps. 50 % (trip at
// ~130) stopped every learn at 55 deg; 25 % (trip ~65) missed the hard stops.
// Geared 5:1 (v0.8) the motor sees the stiff zone at ~1/5 of that torque, so
// 50 % may hold: ASSUMPTION, stage 5 step 3 traces it (`sg K`) and sets this.
#define CFG_KEY_SG_CAL_PCT       50
#define CFG_SG_CAL_MIN_BASE      40     // a lower free-running SG can't be told from a stall
// 0 since 2026-10-18: on the door the click-found offsets put position 0 on
// the stop and each target on the near side of its click (bring-up 4b); the
// offsets below were measured by hand instead. The CAL line still reports
// the ripple. 1 = find position 0 from the clicks every session.
#define CFG_DETENT_AUTOCAL       0
#define CFG_DETENT_MIN_AMP       3      // ripple (SG units) needed to trust the click phase; else the offsets below
#define CFG_KEY_CAL_DEG          45     // free travel only: resistance starts at ~55 deg, stop at ~100 (Paul, 2026-10-18; was 60)

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
// Fallback (CFG_DETENT_AUTOCAL finds it each session), or the offset itself
// with `set detentcal 0`: from the stall point to the middle of position 0
// (the first click), full steps clockwise. Paul (2026-10-06): the clicks are
// evenly spaced, 18 deg apart; where the first one sits relative to the stop
// isn't known. 10 = half a position. Correction (2026-10-18): on the door the
// click-found offsets put position 0 on the stop and every position on the
// near side of its click (it fell back one click when released), so these are
// to be MEASURED by hand (bring-up 4b step 8) and CFG_DETENT_AUTOCAL set to 0.
// MEASURED (Paul, 2026-10-18, bring-up 4b step 8, 7mm plugs, v0.6/0.7): the
// offsets at which each dial, sent to position 5 and released, stays in its
// click and counts 5 clicks back to its stop. Two clicks (A, C) and a click
// and a half (B) from the stall point: the play between motor and dial
// (~10-12 full steps) plus the wind-up at the stall, plus the stop-to-first-
// click distance.
#define CFG_HOME_OFFSET_A        40
#define CFG_HOME_OFFSET_B        30
#define CFG_HOME_OFFSET_C        40
// Every dial move that ends turning anticlockwise overshoots by this much and
// comes back clockwise, so each position is reached turning the same way.
// ASSUMPTION (2026-10-18): the drive has play between motor and dial (the
// door results that day point to it, unmeasured), so the same step count
// would land the dial in a different place depending on the direction. 20 =
// one click, more than any play seen. Bring-up 4b step 8 checks it (`set
// approach 0` to compare). 0 = off.
#define CFG_DIAL_APPROACH_FULL   20
// ...but never closer than this to the stall point (full steps). Correction
// (Paul, 2026-10-18): `goto 1 0 0` then `goto 0 0 0` stopped with JAM. The
// overshoot back past position 0 was only kept off the stall point itself,
// and the stall point is the motor pressed into the stop (the drive wound
// up), so reaching it again reads as a stall. 10 = half a click, an
// ASSUMPTION (the wind-up isn't measured): if a dial at a small offset still
// jams going back to 0, raise it (`set approachclear N`).
#define CFG_DIAL_APPROACH_CLEAR_FULL 10
// 1 = `goto` goes on clockwise past the stop (19 -> 0) when that's shorter
// than going back (Paul's request, v0.6). 0 since v0.6.2: passing the stop
// clockwise means pushing through the anti-reverse cam, a distinct click
// that needs more force (Paul, 2026-10-18), and `sg A 400` stalled there
// at 600 mA (bring-up 4b, 2026-10-18). Inside one turn nothing crosses it.
#define CFG_DIAL_WRAP            0
// Inside one turn: the calibration sweep and `load` turn the dials from
// position 0 clockwise, stopping this far short of where the stop's cam would
// be met again (one dial turn from the stall point), full steps. The dial
// trails the motor by ~10-12 full steps (sg A 400, 2026-10-18): 30 leaves
// 1.5 clicks. ASSUMPTION.
#define CFG_CAM_CLEAR_FULL       30

// ---- Settle after homing (Paul's decision, 2026-10-16) ------------------------
// After the dials are homed (session start, every re-check, `calibrate`,
// `home`), their drivers are switched off for CFG_DIAL_SETTLE_MS so each dial
// can fall into its nearest click (and dial B's drive, which gives a little
// under the homing push, can relax: bring-up 4b, 2026-10-14), then switched
// on again. Switching on pulls each motor to the nearest of its
// holding points, one every 4 full steps (DS §3.6.1: the motor pulls back into
// the same step if it moved less than +-2 full steps). So a dial that fell
// less than 2 full steps is pulled back where it was; one that fell further
// ends within 2 full steps (1.8 deg of dial) of its click, and its step count
// is then off by 4 (or 8) full steps, which the next re-check sees as a home
// discrepancy (CFG_RECHECK_HOME_TOL_FULL 8: fine up to a fall of 6 full steps).
// 0 = no settle.
#define CFG_DIAL_SETTLE_MS       500    // ASSUMPTION: long enough for a click to pull its dial in; stage 4b checks
// Settle after every dial move as well (goto, each attempt), not just after
// homing (Paul, 2026-10-18: "accuracy over speed"). Each settle lets the dials
// drop into their clicks, so a target needs only to be within half a click of
// a click centre. Costs CFG_DIAL_SETTLE_MS + CFG_DIAL_SETTLE_ON_MS per attempt
// (~1.5 h over 8,000). 0 = after homing only.
#define CFG_DIAL_SETTLE_EACH     1
#define CFG_DIAL_SETTLE_ON_MS    200    // still, after switching back on, before the next move (precaution:
                                        // StealthChop tunes at standstill, DS §6.1 AT#1 <=130 ms)

// ---- Key -----------------------------------------------------------------------
// The key can't turn anticlockwise at all from its insertion position (Paul,
// 2026-10-06): that rest stop is the key's home, re-found every attempt (0).
// 1 = return by step count instead (for a key without a rest stop).
#define CFG_KEY_HOME_MODE        0
#define CFG_KEY_HOME_SEARCH_DEG  180    // session start: anticlockwise bound to find the rest stop. The key
                                        // stays wherever it was left (Paul, 2026-10-06), e.g. ~100 deg after a
                                        // power cut mid-attempt, so this must cover the whole travel
#define CFG_KEY_HOME_EXTRA_DEG   15     // retract: anticlockwise bound past the angle reached
#define CFG_KEY_REST_TOL_DECI    50     // v0.8: a retract (or `key`'s return) that stalls more than 5 deg
                                        // short of the rest is a stuck key, not the rest stop (2026-10-18:
                                        // direct drive stalled in the stiff zone on the way back)
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
// There are no marks on the door (Paul, 2026-10-06): positions are reported as
// clicks counted clockwise from each dial's stop, 0 = first click (Paul,
// 2026-10-18: 0..19; it was 1..20 until firmware v0.6).
#define CFG_LABEL_AT_HOME_A      0
#define CFG_LABEL_AT_HOME_B      0
#define CFG_LABEL_AT_HOME_C      0
#define CFG_LABEL_STEP_A         1      // +1 or -1 per position away from home
#define CFG_LABEL_STEP_B         1
#define CFG_LABEL_STEP_C         1

// ---- Electrical (control/wiring.md) ----------------------------------------------
#define CFG_R_SENSE              0.11f  // BTT TMC2209 V1.3 sense resistors (schematic R3/R5)
#define CFG_UART_BAUD            115200 // TMC2209: 9000 baud .. fCLK/16 (datasheet §4.1)
#define CFG_FCLK_HZ              12000000UL  // internal clock, nominal (datasheet)
#define CFG_USB_BAUD             115200
