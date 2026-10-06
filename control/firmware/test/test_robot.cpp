// End-to-end tests: the real sequencer (core::Robot) against SimHal.
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
  CHECK(field(ok, 3) == "3" && field(ok, 4) == "6" && field(ok, 5) == "18");  // 1-based positions
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
  h.present[AX_KEY] = false;  // 12 V off at the key turner, or the cable unplugged
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
  s.homeOffsetFull[1] = 12;
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
  r.handleLine("try");
  CHECK(h.last("ATT,").find(",-1,4,5,6,") != std::string::npos);
  r.handleLine("jog K 10");
  r.handleLine("jog K -10");
  r.handleLine("sg A 40");
  CHECK(h.last("# moved").find("sgMin=300") != std::string::npos);
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
