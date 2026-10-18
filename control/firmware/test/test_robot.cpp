// End-to-end tests: the real sequencer (core::Robot) against SimHal.
#include <cmath>
#include <cstdlib>
#include <cstring>
#include <map>
#include <memory>
#include <string>

#include "../safe_robot/src/core/robot.h"
#include "../safe_robot/src/core/settings_from_config.h"
#include "minitest.h"
#include "sim_hal.h"

using namespace core;

namespace {

Settings tunedSettings() {
  Settings s = makeSettings();  // config.h defaults
  for (int a = 0; a < AX_COUNT; ++a) s.ax[a].sgthrs = 80;  // "tuned" on the bench
  return s;
}

// Run ticks until the robot leaves the busy states (or a tick budget runs out).
void runUntilIdle(Robot& r, int maxTicks = 20000) {
  for (int i = 0; i < maxTicks && r.busy(); ++i) r.tick();
}

int secretIndex(const SimHal& h) {
  Combo c = {{h.secret[0], h.secret[1], h.secret[2]}};
  return comboIndex(c, 20);
}

// Indices of all ATT lines, in order.
std::vector<int> attIndices(const SimHal& h) {
  std::vector<int> v;
  for (auto& l : h.lines)
    if (l.rfind("ATT,", 0) == 0) {
      const char* p = l.c_str() + 4;
      p = std::strchr(p, ',') + 1;  // skip ms
      v.push_back(std::atoi(p));
    }
  return v;
}

std::string field(const std::string& line, int n) {
  size_t a = 0;
  for (int i = 0; i < n; ++i) a = line.find(',', a) + 1;
  return line.substr(a, line.find(',', a) - a);
}

void noViolations(const SimHal& h) {
  for (auto& v : h.violations) std::printf("  violation: %s\n", v.c_str());
  CHECK(h.violations.empty());
}

}  // namespace

TEST(run_finds_the_combination) {
  SimHal h;
  h.secret[0] = 2; h.secret[1] = 5; h.secret[2] = 17;  // index 2*400 + (5)*20 + ... (serpentine)
  Settings s = tunedSettings();
  Robot r(h, s);
  r.boot();
  r.handleLine("start");
  runUntilIdle(r);
  CHECK_EQ(r.state(), ST_SUCCESS);
  CHECK_EQ(r.progress().state, RUN_SUCCESS);
  CHECK_EQ(r.progress().successIndex, secretIndex(h));
  const std::string ok = h.last("SUCCESS,");
  CHECK(field(ok, 3) == "2" && field(ok, 4) == "5" && field(ok, 5) == "17");  // positions 0..19 (v0.6)
  // Every index before the success was tried, in order, exactly once
  // (re-checks every 200 attempts don't repeat attempts).
  std::vector<int> idx = attIndices(h);
  CHECK_EQ((int)idx.size(), secretIndex(h) + 1);
  for (size_t i = 0; i < idx.size(); ++i) CHECK_EQ(idx[i], (int)i);
  CHECK_EQ(h.count("ERR,"), 0);
  CHECK(h.count("RECHECK,") >= 4 * (secretIndex(h) / 200));
  CHECK(h.has("NSTOP,"));
  noViolations(h);
  // The key is held where it stopped (not retracted, driver still on).
  CHECK(h.enabled[AX_KEY]);
  CHECK(h.keyPhys() > h.keyN + 80);
}

TEST(each_attempt_moves_one_dial_one_position) {
  SimHal h;
  h.secret[0] = 0; h.secret[1] = 3; h.secret[2] = 9;
  Settings s = tunedSettings();
  s.recheckEvery = 0;
  s.dialApproachFull = 0;  // one move per position change (the approach is tested below)
  Robot r(h, s);
  r.boot();
  r.handleLine("start");
  // Skip the session start, then look at dial moves between attempts.
  while (r.state() == ST_SESSION) r.tick();
  const size_t from = h.moves.size();
  runUntilIdle(r);
  int dialMoves = 0;
  for (size_t i = from; i < h.moves.size(); ++i)
    if (h.moves[i].axis != AX_KEY) {
      ++dialMoves;
      CHECK_EQ(std::abs(h.moves[i].steps), 320);
    }
  // +1: a fresh run learns N at combinations 0 and 1, so attempt 0 first
  // moves dial C back one position.
  CHECK_EQ(dialMoves, secretIndex(h) + 1);
  noViolations(h);
}

TEST(false_sets_are_logged_and_skipped) {
  SimHal h;
  h.secret[0] = 1; h.secret[1] = 0; h.secret[2] = 4;
  h.falseSets.insert(SimHal::comboKey(0, 3, 3));
  h.falseSets.insert(SimHal::comboKey(0, 19, 7));
  Settings s = tunedSettings();
  Robot r(h, s);
  r.boot();
  r.handleLine("start");
  runUntilIdle(r);
  CHECK_EQ(r.state(), ST_SUCCESS);
  int fs = 0;
  for (auto& l : h.lines)
    if (l.rfind("ATT,", 0) == 0 && field(l, 10) == "FALSESET") ++fs;
  CHECK_EQ(fs, 2);
  noViolations(h);
}

TEST(power_loss_resume_rewinds_to_checkpoint_and_finishes) {
  SimHal h;
  h.secret[0] = 3; h.secret[1] = 1; h.secret[2] = 1;
  Settings s = tunedSettings();
  {
    Robot r(h, s);
    r.boot();
    r.handleLine("start");
    // Run until index ~650, then "pull the plug" mid-run.
    for (int i = 0; i < 100000 && r.progress().nextIndex < 650; ++i) r.tick();
    CHECK(r.progress().nextIndex >= 650);
    CHECK_EQ(r.progress().verifiedIndex, 600);
  }
  // Power back: new Robot object on the same EEPROM; drivers are off; the
  // mechanics are where they were. Paul also took the units off and back on.
  for (auto& e : h.enabled) e = false;
  h.reseat();
  Robot r2(h, s);
  h.lines.clear();
  r2.boot();
  CHECK(h.has("# run in progress"));
  r2.handleLine("resume");
  CHECK(h.has("# rewinding"));
  runUntilIdle(r2);
  CHECK_EQ(r2.state(), ST_SUCCESS);
  CHECK_EQ(r2.progress().successIndex, secretIndex(h));
  std::vector<int> idx = attIndices(h);
  CHECK(!idx.empty());
  if (!idx.empty()) { CHECK_EQ(idx.front(), 600); CHECK_EQ(idx.back(), secretIndex(h)); }
  noViolations(h);
}

TEST(unit_slip_is_caught_by_recheck_and_rewound) {
  SimHal h;
  h.secret[0] = 2; h.secret[1] = 2; h.secret[2] = 2;
  Settings s = tunedSettings();
  Robot r(h, s);
  r.boot();
  r.handleLine("start");
  for (int i = 0; i < 100000 && r.progress().nextIndex < 450; ++i) r.tick();
  // The dial unit gets knocked: dial B's wheel slips 2 positions.
  h.slip(1, 2);
  runUntilIdle(r);
  CHECK_EQ(r.state(), ST_ERROR);
  CHECK(h.last("ERR,").find("RECHECK") != std::string::npos);
  CHECK_EQ(r.progress().nextIndex, 400);  // rewound to the last good re-check
  CHECK_EQ(r.progress().state, RUN_ACTIVE);
  // Paul re-seats and resumes: the run completes and finds it.
  h.reseat();
  r.handleLine("resume");
  runUntilIdle(r);
  CHECK_EQ(r.state(), ST_SUCCESS);
  CHECK_EQ(r.progress().successIndex, secretIndex(h));
  noViolations(h);
}

TEST(pause_verifies_then_resume_needs_no_rewind) {
  SimHal h;
  h.secret[0] = 1; h.secret[1] = 1; h.secret[2] = 1;
  Settings s = tunedSettings();
  Robot r(h, s);
  r.boot();
  r.handleLine("start");
  for (int i = 0; i < 100000 && r.progress().nextIndex < 123; ++i) r.tick();
  r.requestPause();
  runUntilIdle(r);
  CHECK_EQ(r.state(), ST_PAUSED);
  CHECK_EQ(r.progress().verifiedIndex, r.progress().nextIndex);
  for (int a = 0; a < 4; ++a) CHECK(!h.enabled[a]);
  const uint16_t at = r.progress().nextIndex;
  h.lines.clear();
  r.handleLine("resume");
  CHECK(!h.has("# rewinding"));
  runUntilIdle(r);
  CHECK_EQ(r.state(), ST_SUCCESS);
  CHECK(!attIndices(h).empty() && attIndices(h).front() == (int)at);
  noViolations(h);
}

TEST(refuses_to_start_untuned) {
  SimHal h;
  Settings s = makeSettings();  // SGTHRS all 0 by default
  Robot r(h, s);
  r.boot();
  r.handleLine("start");
  CHECK_EQ(r.state(), ST_ERROR);
  CHECK(h.last("ERR,").find("TUNE") != std::string::npos);
  CHECK(h.moves.empty());
}

TEST(missing_driver_stops_before_any_motion) {
  SimHal h;
  h.present[AX_KEY] = false;  // E0 driver missing, or its UART lead off its RX pin
  Settings s = tunedSettings();
  Robot r(h, s);
  r.boot();
  r.handleLine("start");
  runUntilIdle(r);
  CHECK_EQ(r.state(), ST_ERROR);
  CHECK(h.last("ERR,").find("DRIVER") != std::string::npos);
  CHECK(h.moves.empty());
  CHECK_EQ(h.count("DRV,"), 4);
}

TEST(no_hard_stop_on_a_dial_is_reported) {
  SimHal h;
  h.dialHasStop[2] = false;
  Settings s = tunedSettings();
  Robot r(h, s);
  r.boot();
  r.handleLine("start");
  runUntilIdle(r);
  CHECK_EQ(r.state(), ST_ERROR);
  CHECK(h.last("ERR,").find(",HOME,") != std::string::npos);
  noViolations(h);
}

TEST(key_without_rest_stop) {
  SimHal h;
  h.keyRestStop = false;
  h.secret[0] = 0; h.secret[1] = 2; h.secret[2] = 5;
  Settings s = tunedSettings();
  {
    Robot r(h, s);
    r.boot();
    r.handleLine("start");
    runUntilIdle(r);
    CHECK_EQ(r.state(), ST_ERROR);
    CHECK(h.last("ERR,").find("KEYHOME") != std::string::npos);
  }
  // With keyhome 1 (count steps back), the run works.
  h.cmd[AX_KEY] = 0;
  h.keyOff = 0;
  s.keyHome = KEYHOME_COUNT;
  Robot r(h, s);
  r.boot();
  r.handleLine("resume");
  runUntilIdle(r);
  CHECK_EQ(r.state(), ST_SUCCESS);
  CHECK_EQ(r.progress().successIndex, secretIndex(h));
  noViolations(h);
}

TEST(diag_stuck_high_is_an_error) {
  SimHal h;
  h.diagStuck[AX_B] = true;
  Settings s = tunedSettings();
  Robot r(h, s);
  r.boot();
  r.handleLine("start");
  runUntilIdle(r);
  CHECK_EQ(r.state(), ST_ERROR);
  CHECK(h.last("ERR,").find("DIAG") != std::string::npos);
}

TEST(abort_releases_everything) {
  SimHal h;
  h.abortAtMove = 6;
  Settings s = tunedSettings();
  Robot r(h, s);
  r.boot();
  r.handleLine("start");
  runUntilIdle(r);
  CHECK_EQ(r.state(), ST_ERROR);
  CHECK(h.last("ERR,").find("ABORT") != std::string::npos);
  for (int a = 0; a < 4; ++a) CHECK(!h.enabled[a]);
}

TEST(early_stops_are_retried_then_pause) {
  SimHal h;
  h.secret[0] = 5; h.secret[1] = 5; h.secret[2] = 5;
  Settings s = tunedSettings();
  Robot r(h, s);
  r.boot();
  r.handleLine("start");
  for (int i = 0; i < 100000 && r.progress().nextIndex < 50; ++i) r.tick();
  h.keyObstruction = h.keyN - 200;  // something blocks the key ~22 deg early
  runUntilIdle(r);
  CHECK_EQ(r.state(), ST_ERROR);
  CHECK(h.last("ERR,").find("EARLY") != std::string::npos);
  CHECK_EQ(r.progress().nextIndex, 50);  // the EARLY attempts don't count
  int early = 0;
  for (auto& l : h.lines) if (l.rfind("ATT,", 0) == 0 && field(l, 10) == "EARLY") ++early;
  CHECK_EQ(early, 3);
  noViolations(h);
}

TEST(combination_at_index_zero_is_reported_during_learning) {
  SimHal h;
  h.secret[0] = 0; h.secret[1] = 0; h.secret[2] = 0;
  Settings s = tunedSettings();
  Robot r(h, s);
  r.boot();
  r.handleLine("start");
  runUntilIdle(r);
  CHECK_EQ(r.state(), ST_SUCCESS);
  CHECK(h.has("ERR,") && h.last("ERR,").find("NOSTOP") != std::string::npos);
  CHECK(h.enabled[AX_KEY]);  // key held
}

TEST(resume_refuses_when_position_settings_changed) {
  SimHal h;
  Settings s = tunedSettings();
  {
    Robot r(h, s);
    r.boot();
    r.handleLine("start");
    for (int i = 0; i < 100000 && r.progress().nextIndex < 20; ++i) r.tick();
    r.requestPause();
    runUntilIdle(r);
  }
  s.detentAutocal = 0;  // positions would now come from CFG_HOME_OFFSET: a different numbering
  Robot r(h, s);
  r.boot();
  r.handleLine("resume");
  CHECK(h.last("ERR,").find("CFGHASH") != std::string::npos);
  r.handleLine("resume force");
  CHECK(r.busy());
}

TEST(bench_commands) {
  SimHal h;
  Settings s = tunedSettings();
  Robot r(h, s);
  r.boot();
  r.handleLine("ping");
  CHECK_EQ(h.count("DRV,"), 4);
  r.handleLine("home");
  CHECK_EQ(h.count("HOME,"), 6);
  r.handleLine("learn");
  CHECK(h.has("NSTOP,"));
  r.handleLine("goto 4 5 6");
  CHECK(h.has("# dials at 4 5 6"));
  for (int d = 0; d < 3; ++d) CHECK_EQ(h.detentOf(d), 4 + d);  // 0 = the first click (v0.6)
  r.handleLine("try");
  CHECK(h.last("ATT,").find(",-1,4,5,6,") != std::string::npos);
  r.handleLine("goto 20 0 0");
  CHECK(h.last("# position out of range").find("0..19") != std::string::npos);
  r.handleLine("jog K 10");
  r.handleLine("jog K -10");
  r.handleLine("sg A 40");
  {
    const std::string m = h.last("# moved");
    const size_t at = m.find("sgMin=");
    CHECK(at != std::string::npos);
    const int sg = at == std::string::npos ? -1 : std::atoi(m.c_str() + at + 6);
    CHECK(sg > 250 && sg < 340);  // the dial's free-running load, ripple included
  }
  r.handleLine("set sgA 95");
  CHECK_EQ(s.ax[AX_A].sgthrs, 95);
  r.handleLine("set nonsense 1");
  CHECK(h.last("# unknown setting").size() > 0);
  r.handleLine("cfg");
  CHECK(h.count("CFG,") >= 8);
  r.handleLine("bogus");
  CHECK(h.last("# unknown command").size() > 0);
  noViolations(h);
}

TEST(dull_stallguard_fails_safe) {
  // SGTHRS too low: DIAG would only come more than 2 full steps into a stop,
  // but by then the rotor slips a pole and bounces back, so DIAG never comes.
  // The firmware must stop at its travel bound and report, not loop.
  SimHal h;
  h.lagMin = 40; h.lagSpan = 5;
  Settings s = tunedSettings();
  Robot r(h, s);
  r.boot();
  r.handleLine("start");
  runUntilIdle(r);
  CHECK_EQ(r.state(), ST_ERROR);
  CHECK(h.last("ERR,").find("KEYHOME") != std::string::npos);
  CHECK(h.moves.size() <= 2);
  for (int a = 0; a < 4; ++a) CHECK(!h.enabled[a]);
  noViolations(h);
}

TEST(recheck_learns_n_at_a_clean_fail_not_a_false_set) {
  // The attempt just before a re-check (index 199) is a false set: N must
  // not be re-learned there, or the re-check would cry wolf.
  SimHal h;
  h.secret[0] = 0; h.secret[1] = 12; h.secret[2] = 0;
  const Combo fs = comboAt(199, 20);
  h.falseSets.insert(SimHal::comboKey(fs.d[0], fs.d[1], fs.d[2]));
  Settings s = tunedSettings();
  Robot r(h, s);
  r.boot();
  r.handleLine("start");
  runUntilIdle(r);
  CHECK_EQ(r.state(), ST_SUCCESS);
  CHECK_EQ(h.count("ERR,"), 0);
  noViolations(h);
}

TEST(false_set_at_the_first_combination_does_not_inflate_n) {
  SimHal h;
  h.falseSets.insert(SimHal::comboKey(0, 0, 0));
  h.secret[0] = 0; h.secret[1] = 4; h.secret[2] = 4;
  Settings s = tunedSettings();
  Robot r(h, s);
  r.boot();
  r.handleLine("start");
  runUntilIdle(r);
  CHECK_EQ(r.state(), ST_SUCCESS);
  CHECK_EQ(h.count("ERR,"), 0);
  CHECK(h.has("EV,") && h.last("EV,").size() > 0);
  // Attempt 0 (the false set) is logged as such, not as a clean fail.
  CHECK(h.lines.size() > 0);
  bool att0 = false;
  for (auto& l : h.lines)
    if (l.rfind("ATT,", 0) == 0 && field(l, 2) == "0") { att0 = true; CHECK(field(l, 10) == "FALSESET"); }
  CHECK(att0);
  noViolations(h);
}

TEST(bench_with_one_driver_fitted) {
  SimHal h;
  h.present[AX_B] = h.present[AX_C] = h.present[AX_KEY] = false;
  Settings s = tunedSettings();
  Robot r(h, s);
  r.boot();
  r.handleLine("jog A 10");
  CHECK(h.last("ERR,").find("DRIVER") != std::string::npos);  // all four expected by default
  r.handleLine("set axes 1");
  r.handleLine("jog A 200");
  CHECK(h.last("# moved").find("moved 200 full steps") != std::string::npos);
  r.handleLine("jog B 10");
  CHECK(h.last("# that driver").size() > 0);
  r.handleLine("seat");
  CHECK(h.has("EV,") && h.last("EV,").find("SEATED") != std::string::npos);
  r.handleLine("home A");
  CHECK_EQ(h.count("HOME,"), 2);
  r.handleLine("start");
  CHECK(h.last("# a run needs").size() > 0);
  CHECK_EQ(r.progress().state, RUN_NONE);
  noViolations(h);
}

TEST(abort_between_moves_and_key_out_guard) {
  SimHal h;
  Settings s = tunedSettings();
  Robot r(h, s);
  r.boot();
  r.handleLine("start");
  r.tick();  // ping + configure
  CHECK(r.busy());
  r.handleLine("abort");
  CHECK_EQ(r.state(), ST_ERROR);
  CHECK(h.last("ERR,").find("ABORT") != std::string::npos);
  for (int a = 0; a < 4; ++a) CHECK(!h.enabled[a]);
  // Bench: with the key homed and then left out, dials must not move.
  r.handleLine("learn");
  r.handleLine("jog K 20");
  const size_t before = h.moves.size();
  r.handleLine("home A");
  CHECK(h.last("ERR,").find("KEYOUT") != std::string::npos);
  CHECK_EQ(h.moves.size(), before);
  noViolations(h);
}

TEST(dials_turn_clockwise_freely_and_seat_never_presses_the_stop) {
  // Paul, 2026-10-06: every dial turns clockwise without limit and stops
  // only turning anticlockwise. Start each wheel just clockwise of its stop
  // (the worst case for an anticlockwise seat), and check homing still finds
  // the stop from there and from nearly a full turn away.
  SimHal h;
  h.dial[0].wheel0 = 40;    // just past the stop
  h.dial[1].wheel0 = 6350;  // almost a full turn from it
  h.dial[2].wheel0 = 3200;
  h.secret[0] = 1; h.secret[1] = 0; h.secret[2] = 2;
  Settings s = tunedSettings();
  Robot r(h, s);
  r.boot();
  r.handleLine("start");
  runUntilIdle(r);
  CHECK_EQ(r.state(), ST_SUCCESS);
  CHECK_EQ(r.progress().successIndex, secretIndex(h));
  // The seat turns are the slow moves: all clockwise (logical +).
  int seats = 0;
  for (auto& m : h.moves)
    if (m.axis != AX_KEY && !m.stopOnStall) { ++seats; CHECK(m.steps > 0); }
  CHECK_EQ(seats, 3);
  noViolations(h);
}

// ---------------------------------------------------------------- calibration
namespace {
int calField(const SimHal& h, char axis, int n) {
  for (auto it = h.lines.rbegin(); it != h.lines.rend(); ++it)
    if (it->rfind("CAL,", 0) == 0 && (*it)[it->find(',', 4) + 1] == axis) return std::atoi(field(*it, n).c_str());
  return -1;
}
double offsetFull(const SimHal& h, char axis) {
  for (auto it = h.lines.rbegin(); it != h.lines.rend(); ++it)
    if (it->rfind("OFFSET,", 0) == 0 && (*it)[it->find(',', 7) + 1] == axis) return std::atof(field(*it, 3).c_str());
  return -1;
}
}  // namespace

TEST(session_calibrates_thresholds_and_click_positions) {
  SimHal h;
  h.secret[0] = 0; h.secret[1] = 1; h.secret[2] = 2;
  Settings s = tunedSettings();
  Robot r(h, s);
  r.boot();
  r.handleLine("start");
  while (r.state() == ST_SESSION) r.tick();
  CHECK_EQ(r.state(), ST_RUN);
  // Dial baseline = lowest bin mean of 300 - 25*sin + noise: about 275.
  for (char a : {'A', 'B', 'C'}) {
    const int base = calField(h, a, 3), thr = calField(h, a, 4), trusted = calField(h, a, 7);
    CHECK(base > 265 && base < 285);
    CHECK(std::abs(thr - (base * 50 + 100) / 200) <= 1);
    CHECK_EQ(trusted, 1);
    // Position 1 lands on click 0: offset = click centre + the stall lag
    // (20..30 usteps = 1.25..1.9 full steps), within a full step or so.
    const int d = a - 'A';
    const double want = (h.detentPhase[d] + 25) / 16.0;
    CHECK(std::fabs(offsetFull(h, a) - want) < 1.6);
    // And the wheel really sits on a click: the session ends at combination
    // 1 (N learned at 0 and 1), so dial C is on its second click.
    CHECK_EQ(h.detentOf(d), d == 2 ? 1 : 0);
  }
  CHECK(std::abs(calField(h, 'K', 3) - 240) <= 2);
  CHECK_EQ(s.ax[AX_KEY].sgthrs, 60);
  noViolations(h);
}

TEST(clicks_anywhere_relative_to_the_stop_are_found) {
  // Where the first click sits relative to the stop isn't known (Paul): try
  // three very different places. Without click calibration, the config
  // offset (10 full steps) would miss them.
  SimHal h;
  h.detentPhase[0] = 40; h.detentPhase[1] = 200; h.detentPhase[2] = 300;
  h.secret[0] = 2; h.secret[1] = 3; h.secret[2] = 4;
  Settings s = tunedSettings();
  Robot r(h, s);
  r.boot();
  r.handleLine("start");
  runUntilIdle(r);
  CHECK_EQ(r.state(), ST_SUCCESS);
  CHECK_EQ(r.progress().successIndex, secretIndex(h));
  noViolations(h);

  SimHal h2;
  h2.detentPhase[0] = 40; h2.detentPhase[1] = 200; h2.detentPhase[2] = 300;
  Settings s2 = tunedSettings();
  s2.detentAutocal = 0;
  s2.settleMs = 0;  // and no settle (the next test has it)
  Robot r2(h2, s2);
  r2.boot();
  r2.handleLine("start");
  while (r2.state() == ST_SESSION) r2.tick();
  CHECK_EQ(h2.detentOf(0), -1);  // between clicks: such a run could never open the lock
}

namespace {
int firstLine(const SimHal& h, const char* prefix, size_t from = 0) {
  for (size_t i = from; i < h.lines.size(); ++i) if (h.lines[i].rfind(prefix, 0) == 0) return (int)i;
  return -1;
}
int lastLineBefore(const SimHal& h, const char* prefix, int before) {
  int k = -1;
  for (int i = 0; i < before && i < (int)h.lines.size(); ++i) if (h.lines[i].rfind(prefix, 0) == 0) k = i;
  return k;
}
}  // namespace

TEST(settle_after_homing_puts_each_dial_on_its_click) {
  // Paul (2026-10-16): end the session-start homing by switching the dial
  // drivers off, so each dial falls into its click. Same clicks as above,
  // with the config offset (as dial B on the door, whose clicks StallGuard
  // can't see): every dial now ends on a click.
  SimHal h;
  h.detentPhase[0] = 40; h.detentPhase[1] = 200; h.detentPhase[2] = 300;
  Settings s = tunedSettings();
  s.detentAutocal = 0;
  Robot r(h, s);
  r.boot();
  r.handleLine("start");
  while (r.state() == ST_SESSION) r.tick();
  CHECK_EQ(r.state(), ST_RUN);
  for (int d = 0; d < 3; ++d) CHECK(h.detentOf(d) == 0);  // position 1 = the first click
  CHECK_EQ(h.falls, 3);
  // Order: after the last HOME/OFFSET line, before learning N.
  const int st = firstLine(h, "EV,");
  int settled = -1;
  for (int i = st; i >= 0 && i < (int)h.lines.size(); ++i)
    if (h.lines[i].find(",SETTLED,7") != std::string::npos) { settled = i; break; }
  CHECK(settled > 0);
  CHECK(lastLineBefore(h, "OFFSET,", settled) > lastLineBefore(h, "HOME,", settled));
  CHECK(firstLine(h, "OFFSET,", (size_t)settled) < 0);
  CHECK(firstLine(h, "LEARN,") > settled);
  for (int d = 0; d < 3; ++d) CHECK(h.enabled[d]);  // back on, holding
  noViolations(h);
}

TEST(settle_that_shifts_the_count_passes_the_recheck) {
  // Dial B's position 1 sits ~5 full steps off its click: it falls in and its
  // motor ends one 4-full-step cycle further on, so the re-check sees a
  // 4-full-step home discrepancy, within CFG_RECHECK_HOME_TOL_FULL (8).
  SimHal h;
  h.detentPhase[1] = 215;
  h.secret[0] = 1; h.secret[1] = 2; h.secret[2] = 3;  // past the first re-check
  Settings s = tunedSettings();
  s.detentAutocal = 0;
  Robot r(h, s);
  r.boot();
  r.handleLine("start");
  runUntilIdle(r);
  CHECK_EQ(r.state(), ST_SUCCESS);
  CHECK_EQ(r.progress().successIndex, secretIndex(h));
  CHECK_EQ(h.count("ERR,"), 0);
  int bLines = 0;
  for (auto& l : h.lines)
    if (l.rfind("RECHECK,", 0) == 0 && field(l, 3) == "B") {
      ++bLines;
      CHECK(std::abs(std::atoi(field(l, 4).c_str()) - 4) <= 2);
      CHECK(field(l, 6) == "1");
    }
  CHECK(bLines >= 1);
  noViolations(h);
}

TEST(settle_fall_of_8_full_steps_stops_at_the_recheck_and_says_the_offset) {
  // Known limit (config.h, CFG_DIAL_SETTLE_MS): dial B's click sits ~8 full
  // steps clockwise of its config offset. The settle puts it on the click but
  // leaves its step count 8 full steps off, the whole re-check margin: the
  // first re-check stops the run (rewound: nothing was tested wrongly) and
  // prints the offset that fixes it.
  SimHal h;
  h.detentPhase[1] = 256;
  h.secret[0] = 1; h.secret[1] = 2; h.secret[2] = 3;
  Settings s = tunedSettings();
  s.detentAutocal = 0;
  {
    Robot r(h, s);
    r.boot();
    r.handleLine("start");
    runUntilIdle(r);
    CHECK_EQ(r.state(), ST_ERROR);
    CHECK(h.last("ERR,").find(",RECHECK,") != std::string::npos);
    CHECK_EQ(r.progress().nextIndex, 0);  // rewound to the start
    CHECK(h.has("# dial B is on its config offset: if nothing moved, `set offB 18`"));
  }
  s.homeOffsetFull[1] = 18;  // as the hint says
  SimHal h2;
  h2.detentPhase[1] = 256;
  h2.secret[0] = 1; h2.secret[1] = 2; h2.secret[2] = 3;
  Robot r2(h2, s);
  r2.boot();
  r2.handleLine("start");
  runUntilIdle(r2);
  CHECK_EQ(r2.state(), ST_SUCCESS);
  CHECK_EQ(r2.progress().successIndex, secretIndex(h2));
  CHECK_EQ(h2.falls, 0);  // on its click already: nothing to fall
  noViolations(h2);
}

TEST(settle_off_and_bench_home_settles_only_that_dial) {
  SimHal h;
  Settings s = tunedSettings();
  Robot r(h, s);
  r.boot();
  r.handleLine("home B");
  CHECK(h.last("EV,").find(",SETTLED,2") != std::string::npos);
  r.handleLine("set settlems 0");
  const int before = h.count("EV,");
  r.handleLine("home");
  CHECK_EQ(h.count("EV,"), before);  // no SETTLED event with the settle off
  noViolations(h);
}

TEST(no_visible_clicks_falls_back_to_the_config_offset) {
  SimHal h;
  h.sgDetentAmp = 0;
  h.secret[0] = 0; h.secret[1] = 0; h.secret[2] = 7;
  Settings s = tunedSettings();
  Robot r(h, s);
  r.boot();
  r.handleLine("start");
  runUntilIdle(r);
  CHECK_EQ(calField(h, 'A', 7), 0);
  CHECK(h.has("# clicks not clear"));
  CHECK(std::fabs(offsetFull(h, 'A') - 10.0) < 0.01);  // CFG_HOME_OFFSET
  CHECK_EQ(r.state(), ST_SUCCESS);  // the sim's clicks sit near the config offset
  noViolations(h);
}

TEST(stallguard_reading_too_low_to_calibrate) {
  SimHal h;
  h.sgDialBase = 30;
  h.sgDetentAmp = 5;
  Settings s = tunedSettings();
  // No dial thresholds yet: the first calibration's free turn (v0.7: with
  // thresholds it homes first, and homing would report the low reading).
  for (int a = 0; a < 3; ++a) s.ax[a].sgthrs = 0;
  Robot r(h, s);
  r.boot();
  r.handleLine("start");
  runUntilIdle(r);
  CHECK_EQ(r.state(), ST_ERROR);
  CHECK(h.last("ERR,").find("SGCAL") != std::string::npos);
  noViolations(h);
}

TEST(power_cut_with_the_key_turned_resumes) {
  // The key stays wherever it is left (Paul): a power cut mid-attempt leaves
  // it near its stop, ~100 deg out. The session start must find the rest
  // stop from there before any dial moves.
  SimHal h;
  h.secret[0] = 1; h.secret[1] = 5; h.secret[2] = 5;
  Settings s = tunedSettings();
  {
    Robot r(h, s);
    r.boot();
    r.handleLine("start");
    for (int i = 0; i < 100000 && r.progress().nextIndex < 120; ++i) r.tick();
  }
  for (auto& e : h.enabled) e = false;
  h.cmd[AX_KEY] = h.keyN;  // key left at its stop
  CHECK(h.keyPhys() > 800);
  Robot r2(h, s);
  r2.boot();
  r2.handleLine("resume");
  runUntilIdle(r2);
  CHECK_EQ(r2.state(), ST_SUCCESS);
  CHECK_EQ(r2.progress().successIndex, secretIndex(h));
  noViolations(h);
}

TEST(calibrate_command_stores_what_a_run_needs) {
  // Fresh robot, config thresholds all 0: a run can't even home the key.
  SimHal h;
  Settings s = makeSettings();
  {
    Robot r(h, s);
    r.boot();
    r.handleLine("start");
    CHECK(h.last("ERR,").find("TUNE") != std::string::npos);
    r.handleLine("calibrate");  // key at its start position, by hand
    CHECK(h.has("# calibration saved"));
    CHECK(h.count("CAL,") == 4);
    CHECK(s.ax[AX_KEY].sgthrs > 0);
  }
  // Power cycle: the stored calibration lets the run start.
  Settings s2 = makeSettings();
  Robot r2(h, s2);
  h.lines.clear();
  r2.boot();
  CHECK(h.has("# last calibration loaded"));
  r2.handleLine("start");
  CHECK(r2.busy());
  runUntilIdle(r2);
  CHECK_EQ(r2.state(), ST_SUCCESS);
  noViolations(h);
}

// ---------------------------------------------------------------- goto (v0.6, Paul 2026-10-18)
TEST(goto_stays_inside_one_turn_by_default) {
  // v0.6.2: passing the stop clockwise pushes through the anti-reverse cam
  // (Paul, 2026-10-18), so by default 19 -> 0 goes back, never across it.
  SimHal h;
  Settings s = tunedSettings();
  Robot r(h, s);
  r.boot();
  r.handleLine("home");
  r.handleLine("goto 19 19 19");
  const size_t m0 = h.moves.size();
  r.handleLine("goto 0 0 0");
  CHECK(h.has("# dials at 0 0 0"));
  for (size_t i = m0; i < h.moves.size(); ++i) CHECK(h.moves[i].steps < 0 || h.moves[i].steps <= 20 * 16);
  CHECK(h.moves[m0].steps < -18 * 320);  // 19 back (and the approach overshoot)
  for (int d = 0; d < 3; ++d) CHECK_EQ(h.detentOf(d), 0);
  CHECK_EQ(h.count("ERR,"), 0);
  noViolations(h);
}

TEST(goto_takes_the_shorter_way_round_with_wrap_on) {
  SimHal h;
  Settings s = tunedSettings();
  s.dialWrap = 1;
  Robot r(h, s);
  r.boot();
  r.handleLine("home");
  r.handleLine("goto 19 19 19");
  CHECK(h.has("# dials at 19 19 19"));
  for (int d = 0; d < 3; ++d) CHECK_EQ(h.detentOf(d), 19);
  // 19 -> 0: one click clockwise (past the stop), not 19 back.
  size_t m0 = h.moves.size();
  r.handleLine("goto 0 0 0");
  CHECK(h.has("# dials at 0 0 0"));
  CHECK_EQ(h.moves.size(), m0 + 3);
  for (size_t i = m0; i < h.moves.size(); ++i) CHECK_EQ(h.moves[i].steps, 320);
  for (int d = 0; d < 3; ++d) CHECK_EQ(h.detentOf(d), 0);
  // ...and the firmware knows it's at 0 (its count wrapped back into the first turn).
  r.handleLine("learn");
  r.handleLine("try");
  CHECK(h.last("ATT,").find(",-1,0,0,0,") != std::string::npos);
  // The count is back in the first turn: 0 -> 1 is one click, and a re-home finds the stop where the count says.
  m0 = h.moves.size();
  r.handleLine("goto 1 1 1");
  for (size_t i = m0; i < h.moves.size(); ++i) CHECK_EQ(h.moves[i].steps, 320);
  for (int d = 0; d < 3; ++d) CHECK_EQ(h.detentOf(d), 1);
  {
    std::string offA;
    for (auto& l : h.lines) if (l.rfind("OFFSET,", 0) == 0 && field(l, 2) == "A") offA = l;
    CHECK(!offA.empty());
    const double off = std::atof(field(offA, 3).c_str());  // position 0, full steps from the stall
    h.lines.clear();
    r.handleLine("home A");
    std::string first;
    for (auto& l : h.lines) if (l.rfind("HOME,", 0) == 0 && field(l, 3) == "1") { first = l; break; }
    const double dist = std::atof(field(first, 4).c_str());
    CHECK(std::fabs(dist - (off + 20)) <= 3);  // position 1 = one click past position 0
    r.handleLine("home");
  }
  // 10 -> 0 is a tie (10 either way): back, anticlockwise.
  r.handleLine("goto 10 10 10");
  m0 = h.moves.size();
  r.handleLine("goto 0 0 0");
  CHECK(h.moves[m0].steps < 0);
  for (int d = 0; d < 3; ++d) CHECK_EQ(h.detentOf(d), 0);
  // 2 -> 15: forward (13 clicks). Going back round would cross the stop anticlockwise: never.
  r.handleLine("goto 2 2 2");
  m0 = h.moves.size();
  r.handleLine("goto 15 15 15");
  CHECK(h.moves[m0].steps > 0);
  for (int d = 0; d < 3; ++d) CHECK_EQ(h.detentOf(d), 15);
  CHECK_EQ(h.count("ERR,"), 0);
  noViolations(h);
}

// Paul (2026-10-18): `goto 1 0 0`, `goto 0 0 0` stopped with JAM: the
// overshoot past position 0 went back onto the stall point, i.e. into the
// stop. Track every dial move from the stall point: never closer than the
// clearance, for any offset (clicks at the default, or a small fixed one).
TEST(going_back_to_position_0_never_presses_the_stop) {
  for (int offFull : {-1, 3, 9, 12, 25}) {
    SimHal h;
    Settings s = tunedSettings();
    if (offFull >= 0) { s.detentAutocal = 0; for (int d = 0; d < 3; ++d) s.homeOffsetFull[d] = (int16_t)offFull; }
    Robot r(h, s);
    r.boot();
    r.handleLine("home");
    // Each dial's position from its stall point, from the OFFSET line and the moves since.
    int32_t pos[3];
    for (int d = 0; d < 3; ++d) {
      std::string off;
      for (auto& l : h.lines) if (l.rfind("OFFSET,", 0) == 0 && field(l, 2) == std::string(1, "ABC"[d])) off = l;
      pos[d] = (int32_t)std::lround(std::atof(field(off, 3).c_str()) * 16);
    }
    const size_t m0 = h.moves.size();
    for (const char* cmd : {"goto 1 0 0", "goto 0 0 0", "goto 0 1 1", "goto 0 0 0", "goto 3 3 3", "goto 0 0 0"}) r.handleLine(cmd);
    int32_t lowest[3] = {pos[0], pos[1], pos[2]};
    for (size_t i = m0; i < h.moves.size(); ++i) {
      const int d = h.moves[i].axis;
      if (d > 2) continue;
      pos[d] += h.moves[i].steps;
      if (pos[d] < lowest[d]) lowest[d] = pos[d];
    }
    for (int d = 0; d < 3; ++d) CHECK(lowest[d] >= std::min((int32_t)s.dialApproachClearFull * 16, (int32_t)std::lround(offFull >= 0 ? offFull * 16 : 1e9)));
    CHECK_EQ(h.count("ERR,"), 0);
    CHECK(h.has("# dials at 0 0 0"));
    noViolations(h);
  }
}

TEST(every_position_is_reached_turning_clockwise) {
  // The approach (CFG_DIAL_APPROACH_FULL): a move that would end turning
  // anticlockwise overshoots and comes back clockwise, never into the stop.
  SimHal h;
  Settings s = tunedSettings();
  Robot r(h, s);
  r.boot();
  r.handleLine("home");
  r.handleLine("goto 8 8 8");
  size_t m0 = h.moves.size();
  r.handleLine("goto 3 3 3");
  CHECK_EQ(h.moves.size(), m0 + 6);  // per dial: back past it, then forward onto it
  for (size_t i = m0; i < h.moves.size(); i += 2) {
    CHECK_EQ(h.moves[i].steps, -5 * 320 - 20 * 16);
    CHECK_EQ(h.moves[i + 1].steps, 20 * 16);
  }
  for (int d = 0; d < 3; ++d) CHECK_EQ(h.detentOf(d), 3);
  // To position 0 the overshoot is cut short so the dial never presses into its stop.
  r.handleLine("goto 0 0 0");
  for (int d = 0; d < 3; ++d) CHECK_EQ(h.detentOf(d), 0);
  CHECK_EQ(h.count("ERR,"), 0);
  noViolations(h);
}

// ---------------------------------------------------------------- `load` (v0.6)
// Paul (2026-10-18): placing the unit off centre loads one dial, and its
// calibration can stall. `load` turns every dial together and prints each
// one's load every 0.5 s, so the unit can be nudged until all run light.
namespace {
// The fields of a LOAD/LOADSUM line for dial ch: {mean, pct} (LOAD) or {mean, low, pct} (LOADSUM).
std::vector<int> loadFields(const std::string& line, char ch, int n) {
  std::vector<int> v;
  const std::string key = std::string(",") + ch + ",";
  size_t p = line.find(key);
  if (p == std::string::npos) return v;
  p += key.size();
  for (int i = 0; i < n; ++i) {
    v.push_back(std::atoi(line.c_str() + p));
    p = line.find(',', p);
    if (p == std::string::npos) break;
    ++p;
  }
  return v;
}
}  // namespace

// v0.7: `load` homes, then sweeps inside one turn (Paul, 2026-10-18: passing
// the stop clockwise pushes through its anti-reverse cam).
std::vector<size_t> lockstepMoves(const SimHal& h, size_t from) {
  std::vector<size_t> v;
  for (size_t i = from; i < h.moves.size(); ++i) if (h.moves[i].withMask) v.push_back(i);
  return v;
}

TEST(load_homes_then_sweeps_inside_one_turn_and_reports_live) {
  SimHal h;
  Settings s = makeSettings();
  Robot r(h, s);
  r.boot();
  r.handleLine("calibrate");
  CHECK(h.has("# calibration saved"));
  const size_t before = h.moves.size();
  h.lines.clear();
  r.handleLine("load 3");
  CHECK_EQ(h.count("HOME,"), 6);  // homed first
  std::vector<size_t> ls = lockstepMoves(h, before);
  CHECK_EQ((int)ls.size(), 6);    // 3 sweeps, out and back
  double far = 0;
  for (auto& l : h.lines) if (l.rfind("OFFSET,", 0) == 0) far = std::max(far, std::atof(field(l, 3).c_str()));
  for (size_t k = 0; k < ls.size(); ++k) {
    const MoveRequest& m = h.moves[ls[k]];
    CHECK_EQ((int)m.axis, (int)AX_A);
    CHECK_EQ((int)m.withMask, 0x06);
    CHECK(k % 2 == 0 ? m.steps > 0 : m.steps < 0);
    CHECK(m.stopOnStall && m.sampleSG && m.timeoutMs > 0);
    // out from position 0 to 30 full steps short of one turn from the stall point: never the cam
    CHECK(far * 16 + std::abs(m.steps) <= 6400 - 30 * 16 + 16);
    CHECK(std::abs(m.steps) > 300 * 16);
  }
  const int n = h.count("LOAD,");
  CHECK(n >= 15);
  for (auto& l : h.lines) {
    if (l.rfind("LOAD,", 0) != 0) continue;
    for (char ch : {'A', 'B', 'C'}) {
      std::vector<int> f = loadFields(l, ch, 2);
      CHECK_EQ((int)f.size(), 2);
      if (f.size() == 2) {
        CHECK(f[0] > 270 && f[0] < 330);
        CHECK(f[1] > 95 && f[1] < 125);
      }
    }
  }
  CHECK(h.has("LOADSUM,"));
  CHECK(h.has("# load done"));
  CHECK_EQ(h.count("ERR,"), 0);
  r.handleLine("goto 2 2 2");
  CHECK(h.last("# goto").find("not homed: A B C") != std::string::npos);
  noViolations(h);
}

TEST(load_shows_which_dial_is_loaded) {
  SimHal h;
  Settings s = makeSettings();
  Robot r(h, s);
  r.boot();
  r.handleLine("calibrate");
  h.sgExtraLoadLockstep[1] = 60;  // unit nudged off centre: dial B's plug pressed sideways
  h.lines.clear();
  r.handleLine("load 2");
  const std::string sum = h.last("LOADSUM,");
  std::vector<int> a = loadFields(sum, 'A', 3), b = loadFields(sum, 'B', 3), c = loadFields(sum, 'C', 3);
  CHECK(a.size() == 3 && b.size() == 3 && c.size() == 3);
  if (a.size() == 3 && b.size() == 3 && c.size() == 3) {
    CHECK(b[0] < a[0] - 45 && b[0] < c[0] - 45);
    CHECK(b[2] < a[2] - 15);
  }
  CHECK(!h.has("# load stopped"));
  noViolations(h);
}

TEST(load_stops_on_a_stall_and_names_the_dial) {
  SimHal h;
  Settings s = makeSettings();
  Robot r(h, s);
  r.boot();
  r.handleLine("calibrate");
  h.sgExtraLoadLockstep[2] = 250;  // dial C jammed: SG far under its threshold
  h.lines.clear();
  r.handleLine("load 5");
  CHECK(h.has("# load stopped: dial C stalled"));
  CHECK_EQ(h.count("ERR,"), 0);   // information while placing the unit, not a fault
  CHECK_EQ(r.state(), ST_IDLE);
  noViolations(h);
}

TEST(load_refuses_bad_sweeps) {
  SimHal h;
  Settings s = tunedSettings();
  Robot r(h, s);
  r.boot();
  const size_t m0 = h.moves.size();
  r.handleLine("load 0");
  r.handleLine("load 21");
  CHECK_EQ(h.moves.size(), m0);
  CHECK_EQ(h.count("# load [sweeps"), 2);
  r.handleLine("key 30");
  r.handleLine("load 1");
  CHECK(h.has("# load done"));
  noViolations(h);
}

TEST(load_needs_a_calibration_first) {
  // It homes first, which needs stall thresholds (calibrate once).
  SimHal h;
  Settings s = makeSettings();
  for (int a = 0; a < 3; ++a) s.ax[a].sgthrs = 0;
  s.axesMask = 0x07;
  Robot r(h, s);
  r.boot();
  const size_t m0 = h.moves.size();
  r.handleLine("load 1");
  CHECK(h.has("# load homes the dials first"));
  CHECK_EQ(h.moves.size(), m0);
  noViolations(h);
}

// v0.7: once thresholds exist, calibration homes first and sweeps inside one
// turn; only the very first one (no thresholds) makes the old free turn.
TEST(calibration_stays_inside_one_turn_once_thresholds_exist) {
  SimHal h;
  Settings s = makeSettings();
  Robot r(h, s);
  r.boot();
  size_t m0 = h.moves.size();
  r.handleLine("calibrate");
  CHECK(h.has("# calibration saved"));
  int freeTurns = 0;
  for (size_t i = m0; i < h.moves.size(); ++i)
    if (h.moves[i].axis < 3 && h.moves[i].sgSink && h.moves[i].steps == 6400 + 1600) ++freeTurns;
  CHECK_EQ(freeTurns, 3);  // first calibration: the old free turn and a quarter
  m0 = h.moves.size();
  h.lines.clear();
  r.handleLine("calibrate");
  CHECK(h.has("# calibration saved"));
  CHECK_EQ(h.count("HOME,"), 12);  // homed before the sweep and after it
  double far = 0;
  for (auto& l : h.lines) if (l.rfind("OFFSET,", 0) == 0) far = std::max(far, std::atof(field(l, 3).c_str()));
  int sweeps = 0;
  for (size_t i = m0; i < h.moves.size(); ++i) {
    const MoveRequest& m = h.moves[i];
    if (m.axis >= 3 || !m.sgSink) continue;
    ++sweeps;
    CHECK(m.steps > 0 && far * 16 + m.steps <= 6400 - 30 * 16 + 16);
  }
  CHECK_EQ(sweeps, 3);
  CHECK_EQ(h.count("CAL,"), 4);
  CHECK(!h.has("# clicks not clear"));
  CHECK_EQ(h.count("ERR,"), 0);
  noViolations(h);
}

// v0.7, Paul (2026-10-18), accuracy over speed: every goto / attempt move
// ends with a settle of the dials that moved, so a target that is a few full
// steps off its click still ends in it.
TEST(dials_settle_after_every_move) {
  SimHal h;
  Settings s = makeSettings();
  Robot r(h, s);
  r.boot();
  r.handleLine("calibrate");
  const int d0 = h.disables[0], d1 = h.disables[1], d2 = h.disables[2];
  r.handleLine("goto 3 0 0");
  CHECK_EQ(h.disables[0], d0 + 1);   // A moved: settled
  CHECK_EQ(h.disables[1], d1);       // B, C didn't move: left alone
  CHECK_EQ(h.disables[2], d2);
  CHECK_EQ(h.detentOf(0), 3);
  // The dial 6 full steps behind where the count says (e.g. play): without
  // the settle a goto leaves it off its click, with it the dial drops in.
  // (The settle after homing already does this once: v0.5.)
  h.dial[0].off += 6 * 16;
  r.handleLine("set settleeach 0");
  r.handleLine("goto 5 0 0");
  const int without = h.detentOf(0);
  r.handleLine("set settleeach 1");
  r.handleLine("goto 6 0 0");
  CHECK_EQ(without, -1);           // 6 full steps off: not on the click
  CHECK_EQ(h.detentOf(0), 6);      // settled into it
  CHECK_EQ(h.count("ERR,"), 0);
  noViolations(h);
}

TEST(load_abort_stops_and_releases) {
  SimHal h;
  Settings s = makeSettings();
  Robot r(h, s);
  r.boot();
  r.handleLine("calibrate");
  h.abortAtMove = h.moveCount;  // the load move
  r.handleLine("load 5");
  CHECK(h.last("ERR,").find("ABORT") != std::string::npos);
  for (int a = 0; a < 4; ++a) CHECK(!h.enabled[a]);
  noViolations(h);
}

// ---------------------------------------------------------------- driver resets (GSTAT)
// A driver whose supply dips (12 V terminal, a loose socket, a 5 V glitch) comes back
// with its power-on registers: no StallGuard. The firmware must notice before
// it trusts another move.
namespace {
// Which dial the attempt at index idx moves (exactly one does).
int movingDial(int idx) {
  const Combo a = comboAt((uint16_t)(idx - 1), 20), b = comboAt((uint16_t)idx, 20);
  for (int d = 2; d >= 0; --d) if (a.d[d] != b.d[d]) return d;
  return -1;
}
int keyMoves(const SimHal& h) {
  int n = 0;
  for (auto& m : h.moves) if (m.axis == AX_KEY) ++n;
  return n;
}
}  // namespace

TEST(key_driver_reset_during_the_key_try_is_not_a_false_success) {
  SimHal h;
  h.secret[0] = 1; h.secret[1] = 4; h.secret[2] = 9;
  Settings s = tunedSettings();
  Robot r(h, s);
  r.boot();
  r.handleLine("start");
  for (int i = 0; i < 100000 && r.progress().nextIndex < 300; ++i) r.tick();
  CHECK_EQ(r.progress().verifiedIndex, 200);
  // What the check costs: one attempt reads GSTAT 12 times (all 4 drivers,
  // then before and after the dial move, the settle that follows it (v0.7),
  // the key try and the retract).
  const int reads = h.gstatReads;
  r.tick();
  CHECK_EQ(h.gstatReads - reads, 12);
  // The key driver's 12 V drops out for a moment halfway through the next key try.
  h.resetOnMove = AX_KEY;
  runUntilIdle(r);
  CHECK_EQ(r.state(), ST_ERROR);
  CHECK(!h.has("SUCCESS,"));
  for (auto& l : h.lines) if (l.rfind("ATT,", 0) == 0) CHECK(field(l, 10) != "SUCCESS");
  CHECK(h.last("GSTAT,").find(",K,1,after") != std::string::npos);
  CHECK(h.last("ERR,").find(",DRVFAULT,") != std::string::npos);
  CHECK_EQ(r.progress().state, RUN_ACTIVE);
  CHECK_EQ(r.progress().nextIndex, 200);  // rewound to the last re-check
  for (int a = 0; a < 4; ++a) CHECK(!h.enabled[a]);
  noViolations(h);
  // Paul fixes the contact and resumes: the run finds the real combination.
  h.lines.clear();
  r.handleLine("resume");
  runUntilIdle(r);
  CHECK_EQ(r.state(), ST_SUCCESS);
  CHECK_EQ(r.progress().successIndex, secretIndex(h));
  CHECK(!attIndices(h).empty() && attIndices(h).front() == 200);
  noViolations(h);
}

TEST(control_unseen_key_reset_gives_a_false_success) {
  // The failure the check exists for, reproduced: the same reset, but GSTAT
  // not looked at (firmware v0.2). The key turns open-loop to N + 15 deg
  // with no stall, and the run stops on a SUCCESS that isn't one.
  SimHal h;
  h.secret[0] = 1; h.secret[1] = 4; h.secret[2] = 9;
  Settings s = tunedSettings();
  Robot r(h, s);
  r.boot();
  r.handleLine("start");
  for (int i = 0; i < 100000 && r.progress().nextIndex < 300; ++i) r.tick();
  h.resetHidden = true;
  h.resetOnMove = AX_KEY;
  runUntilIdle(r);
  CHECK_EQ(r.state(), ST_SUCCESS);
  CHECK(r.progress().successIndex != secretIndex(h));
  CHECK(r.progress().successIndex < 310);
  CHECK(h.keyPhys() <= h.keyN);  // the key never got past its stop: the lock didn't open
}

TEST(key_driver_reset_during_a_dial_move_stops_before_the_key_turns) {
  SimHal h;
  h.secret[0] = 1; h.secret[1] = 4; h.secret[2] = 9;
  Settings s = tunedSettings();
  Robot r(h, s);
  r.boot();
  r.handleLine("start");
  for (int i = 0; i < 100000 && r.progress().nextIndex < 300; ++i) r.tick();
  h.resetOnMove = movingDial(r.progress().nextIndex);
  h.resetAxis = AX_KEY;
  const int keyBefore = keyMoves(h);
  runUntilIdle(r);
  CHECK_EQ(r.state(), ST_ERROR);
  CHECK_EQ(keyMoves(h), keyBefore);  // the key never moved on the reset driver
  CHECK(h.last("GSTAT,").find(",K,1,before") != std::string::npos);
  CHECK(h.last("ERR,").find(",DRVFAULT,") != std::string::npos);
  CHECK_EQ(r.progress().nextIndex, 200);
  noViolations(h);
}

TEST(idle_dial_driver_reset_is_caught_before_the_next_attempt_moves) {
  // Dial A moves only every 400 attempts: a reset while it sits still is
  // caught by the all-driver check at the start of the next attempt.
  SimHal h;
  h.secret[0] = 1; h.secret[1] = 4; h.secret[2] = 9;
  Settings s = tunedSettings();
  Robot r(h, s);
  r.boot();
  r.handleLine("start");
  for (int i = 0; i < 100000 && r.progress().nextIndex < 450; ++i) r.tick();
  h.driverReset(AX_A);
  const size_t movesBefore = h.moves.size();
  runUntilIdle(r);
  CHECK_EQ(r.state(), ST_ERROR);
  CHECK_EQ(h.moves.size(), movesBefore);  // nothing moved after the reset
  CHECK(h.last("GSTAT,").find(",A,1,attempt") != std::string::npos);
  CHECK(h.last("ERR,").find(",DRVFAULT,") != std::string::npos);
  CHECK_EQ(r.progress().nextIndex, 400);
  noViolations(h);
  r.handleLine("resume");
  runUntilIdle(r);
  CHECK_EQ(r.state(), ST_SUCCESS);
  CHECK_EQ(r.progress().successIndex, secretIndex(h));
  noViolations(h);
}

TEST(driver_that_stops_answering_mid_run_stops_it) {
  // The key branch's fuse blows: its driver goes silent.
  SimHal h;
  h.secret[0] = 0; h.secret[1] = 9; h.secret[2] = 9;
  Settings s = tunedSettings();
  Robot r(h, s);
  r.boot();
  r.handleLine("start");
  for (int i = 0; i < 100000 && r.progress().nextIndex < 50; ++i) r.tick();
  h.present[AX_KEY] = false;
  runUntilIdle(r);
  CHECK_EQ(r.state(), ST_ERROR);
  CHECK(h.last("GSTAT,").find(",K,80,attempt") != std::string::npos);
  CHECK(h.last("ERR,").find(",DRVFAULT,") != std::string::npos);
  CHECK_EQ(r.progress().nextIndex, 0);
  noViolations(h);
}

TEST(reset_before_a_settings_rewrite_is_reported_not_wiped) {
  // configure() clears GSTAT. Dial A, set up at the session's first step,
  // resets during dial B's seat turn; the seat's closing settings rewrite
  // must report it rather than clear it (A's click phase from its count
  // could be up to 2 full steps out after a reset).
  SimHal h;
  h.secret[0] = 0; h.secret[1] = 1; h.secret[2] = 2;
  Settings s = tunedSettings();
  Robot r(h, s);
  r.boot();
  h.resetOnMove = AX_B;
  h.resetAxis = AX_A;
  r.handleLine("start");
  runUntilIdle(r);
  CHECK_EQ(r.state(), ST_ERROR);
  CHECK(h.last("GSTAT,").find(",A,1,config") != std::string::npos);
  CHECK(h.last("ERR,").find(",DRVFAULT,") != std::string::npos);
  CHECK(!h.has("ATT,"));
  noViolations(h);
  r.handleLine("resume");
  runUntilIdle(r);
  CHECK_EQ(r.state(), ST_SUCCESS);
  CHECK_EQ(r.progress().successIndex, secretIndex(h));
  noViolations(h);
}

TEST(bench_command_after_a_12v_cycle_reports_it_once) {
  // The drivers were set up and not released, so a reset is news: report it,
  // forget the positions, and set up afresh on the next command.
  SimHal h;
  Settings s = tunedSettings();
  Robot r(h, s);
  r.boot();
  r.handleLine("home");
  CHECK_EQ(h.count("HOME,"), 6);
  for (int a = 0; a < 4; ++a) h.driverReset(a);  // 12 V off and on, no `release`
  const size_t moves = h.moves.size();
  r.handleLine("jog A 20");
  CHECK(h.last("GSTAT,").find(",A,1,config") != std::string::npos);
  CHECK(h.last("ERR,").find(",DRVFAULT,") != std::string::npos);
  CHECK_EQ(h.moves.size(), moves);
  r.handleLine("goto 2 2 2");
  CHECK(h.last("# goto: not homed: A B C").size() > 0);  // positions forgotten: home first
  r.handleLine("jog A 20");
  CHECK(h.last("# moved").find("moved 20 full steps") != std::string::npos);
  noViolations(h);
}

TEST(a_12v_cycle_while_paused_is_not_an_error) {
  // Pausing releases the drivers: nothing relies on their setup, so the
  // resume's session start just sets them up again.
  SimHal h;
  h.secret[0] = 0; h.secret[1] = 3; h.secret[2] = 3;
  Settings s = tunedSettings();
  Robot r(h, s);
  r.boot();
  r.handleLine("start");
  for (int i = 0; i < 100000 && r.progress().nextIndex < 30; ++i) r.tick();
  r.requestPause();
  runUntilIdle(r);
  CHECK_EQ(r.state(), ST_PAUSED);
  for (int a = 0; a < 4; ++a) h.driverReset(a);
  r.handleLine("resume");
  runUntilIdle(r);
  CHECK_EQ(r.state(), ST_SUCCESS);
  CHECK_EQ(h.count("ERR,"), 0);
  CHECK_EQ(h.count("GSTAT,"), 0);
  noViolations(h);
}
