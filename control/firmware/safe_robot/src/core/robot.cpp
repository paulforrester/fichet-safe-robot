#include "robot.h"

#include <stdlib.h>
#include <string.h>

#ifdef __AVR__
#define TOKEQ(tok, lit) (strcmp_P((tok), PSTR(lit)) == 0)
#else
#define TOKEQ(tok, lit) (strcmp((tok), (lit)) == 0)
#endif

namespace core {

namespace {
const char kAxisChar[AX_COUNT] = {'A', 'B', 'C', 'K'};
// Expected (MS1, MS2) strapping per axis: UART addresses 0..3 (wiring.md §2).
const bool kMs1[AX_COUNT] = {false, true, false, true};
const bool kMs2[AX_COUNT] = {false, false, true, true};

int32_t iabs(int32_t v) { return v < 0 ? -v : v; }

bool parseAxis(const char* t, Axis* ax) {
  if (!t || !t[0] || t[1]) return false;
  const char ch = (char)(t[0] & ~0x20);  // upper case
  for (uint8_t i = 0; i < AX_COUNT; ++i)
    if (kAxisChar[i] == ch) { *ax = (Axis)i; return true; }
  return false;
}

void sort3(int32_t* v, uint8_t n) {  // insertion sort, n is small
  for (uint8_t i = 1; i < n; ++i)
    for (uint8_t j = i; j > 0 && v[j] < v[j - 1]; --j) { int32_t t = v[j]; v[j] = v[j - 1]; v[j - 1] = t; }
}
}  // namespace

uint32_t positionHash(const Settings& s) {
  uint32_t h = 2166136261u;  // FNV-1a
  auto mix = [&h](uint32_t v) { for (uint8_t i = 0; i < 4; ++i) { h ^= (v >> (8 * i)) & 0xFF; h *= 16777619u; } };
  mix(s.fullStepsPerRev); mix(s.microsteps); mix(s.dialGear); mix(s.positions);
  mix(s.detentAutocal);
  for (uint8_t d = 0; d < 3; ++d) {
    mix(s.ax[d].invert);
    mix(s.dialHome[d]);
    if (!s.detentAutocal) mix((uint32_t)(int32_t)s.homeOffsetFull[d]);  // else measured each session
  }
  return h;
}

Robot::Robot(Hal& hal, Settings& s) : hal_(hal), s_(s), journal_(hal, 0, 16), calStore_(hal) { resetOffsets(); }

void Robot::resetOffsets() {
  for (uint8_t d = 0; d < 3; ++d) {
    offsetUs_[d] = (int32_t)s_.homeOffsetFull[d] * s_.microsteps;
    notchOk_[d] = false;
  }
}

// ---------------------------------------------------------------- boot
void Robot::boot() {
  if (!journal_.load(prog_)) prog_ = Progress();
  Line l;
  l.p(CP("EV,")).u(hal_.millis()).p(CP(",BOOT,")).u(prog_.state);
  emit(l);
  if (calStore_.load(cal_) && s_.sgAutocal) {
    for (uint8_t a = 0; a < AX_COUNT; ++a)
      if (cal_.sgthrs[a]) s_.ax[a].sgthrs = cal_.sgthrs[a];
    l.clear();
    l.p(CP("# last calibration loaded: sgthrs A/B/C/K = ")).u(cal_.sgthrs[0]).c('/').u(cal_.sgthrs[1]).c('/')
        .u(cal_.sgthrs[2]).c('/').u(cal_.sgthrs[3]);
    emit(l);
  }
  printStatus();
  if (prog_.state == RUN_ACTIVE) {
    l.clear(); l.p(CP("# run in progress: next index ")).u(prog_.nextIndex)
        .p(CP(", last re-check at ")).u(prog_.verifiedIndex).p(CP(". Send `resume` (or press the button)."));
    emit(l);
  } else if (prog_.state == RUN_SUCCESS) {
    const Combo c = comboAt(prog_.successIndex, s_.positions);
    l.clear(); l.p(CP("# SUCCESS recorded at index ")).u(prog_.successIndex).p(CP(": dials "))
        .u(c.d[0] + 1).c('-').u(c.d[1] + 1).c('-').u(c.d[2] + 1).p(CP(" (from home). `reset yes` to clear."));
    emit(l);
  }
}

// ---------------------------------------------------------------- commands
void Robot::handleLine(const char* line) {
  char buf[64];
  strncpy(buf, line, sizeof(buf) - 1);
  buf[sizeof(buf) - 1] = 0;
  char* tok[5] = {0, 0, 0, 0, 0};
  uint8_t nt = 0;
  for (char* p = buf; *p && nt < 5;) {
    while (*p == ' ' || *p == '\t' || *p == '\r') ++p;
    if (!*p) break;
    tok[nt++] = p;
    while (*p && *p != ' ' && *p != '\t' && *p != '\r') ++p;
    if (*p) *p++ = 0;
  }
  if (nt == 0) return;
  const char* cmd = tok[0];
  Line l;

  if (TOKEQ(cmd, "status")) { printStatus(); return; }
  if (TOKEQ(cmd, "abort")) { abort(); return; }
  if (TOKEQ(cmd, "pause")) {
    if (busy()) { pauseReq_ = true; l.p(CP("# pause requested: stopping after this attempt")); emit(l); }
    return;
  }
  if (busy()) { l.p(CP("# busy: only status / pause / abort ('!') now")); emit(l); return; }

  if (TOKEQ(cmd, "help")) {
    const char* const lines[] = {
      CP("# commands: status | cfg | ping | start | resume [force] | pause | release | reset yes"),
      CP("#   calibrate | seat | home [A|B|C] | learn | goto a b c | try | key <deg> | jog <A|B|C|K> <n>"),
      CP("#   sg <A|B|C|K> <fullsteps> | set <name> <value> | abort (or '!': stops at once)"),
    };
    for (uint8_t i = 0; i < 3; ++i) { l.clear(); l.p(lines[i]); emit(l); }
    return;
  }
  if (TOKEQ(cmd, "cfg")) { printCfg(); return; }
  if (TOKEQ(cmd, "ping")) { pingAll(); if (state_ == ST_ERROR) state_ = ST_IDLE; return; }
  if (TOKEQ(cmd, "release")) { releaseAll(); state_ = ST_IDLE; l.p(CP("# all drivers off")); emit(l); return; }
  if (TOKEQ(cmd, "reset")) {
    if (tok[1] && TOKEQ(tok[1], "yes")) {
      journal_.clear(); prog_ = Progress(); state_ = ST_IDLE;
      l.p(CP("# progress cleared")); emit(l);
    } else { l.p(CP("# type `reset yes` to clear the stored progress")); emit(l); }
    return;
  }
  if (TOKEQ(cmd, "start")) {
    if (prog_.state == RUN_ACTIVE || prog_.state == RUN_SUCCESS) {
      l.p(CP("# a run is stored: `resume`, or `reset yes` to start over")); emit(l); return;
    }
    if (!needAll() || !tuned()) return;
    prog_ = Progress();
    prog_.state = RUN_ACTIVE;
    prog_.cfgHash = positionHash(s_);
    saveProgress();
    startSession(true);
    return;
  }
  if (TOKEQ(cmd, "resume")) {
    const bool force = tok[1] && TOKEQ(tok[1], "force");
    if (prog_.state != RUN_ACTIVE) { l.p(CP("# nothing to resume")); emit(l); return; }
    if (prog_.cfgHash != positionHash(s_) && !force) {
      error(CP("CFGHASH"), CP("dial position settings changed since the run started: `resume force` or `reset yes`"));
      return;
    }
    for (uint8_t d = 0; d < 3; ++d)
      if (s_.dialHome[d] == HOME_NONE && prog_.nextIndex > 0 && !force) {
        error(CP("NOHOME"), CP("a dial has no home stop, so positions can't be recovered: `resume force` or `reset yes`"));
        return;
      }
    if (!needAll() || !tuned()) return;
    if (s_.resumeFromCheckpoint && prog_.nextIndex != prog_.verifiedIndex) {
      l.p(CP("# rewinding from ")).u(prog_.nextIndex).p(CP(" to the last re-checked index ")).u(prog_.verifiedIndex);
      emit(l);
      prog_.nextIndex = prog_.verifiedIndex;
    }
    prog_.cfgHash = positionHash(s_);
    saveProgress();
    startSession(true);
    return;
  }

  // Bench commands. Each starts by checking and configuring the drivers.
  if (TOKEQ(cmd, "set")) {
    if (tok[1] && tok[2]) cmdSet(tok[1], atol(tok[2]));
    else { l.p(CP("# set <name> <value>; names in `cfg`")); emit(l); }
    return;
  }
  if (state_ == ST_SUCCESS) { l.p(CP("# success state: `release` first")); emit(l); return; }
  state_ = ST_IDLE;
  if (TOKEQ(cmd, "seat")) {
    if (!pingAll() || !configureAll(false)) return;
    if (fitted(AX_KEY) && !keyHome(keyDeciToUs(s_, (int32_t)s_.keyHomeSearchDeg * 10))) return;
    seatDials();
    return;
  }
  if (TOKEQ(cmd, "calibrate")) {
    // Separate calibration step. The key must be at its start position (turn
    // it back by hand): there may be no key threshold yet to find it with.
    if (!pingAll() || !configureAll(false)) return;
    forceCal_ = true;
    bool ok = true;
    if (fitted(AX_KEY)) { keyPos_ = 0; keyHomed_ = true; ok = calKey(); }
    if (ok) ok = seatDials() && calibrateDials();
    for (uint8_t d = 0; d < 3 && ok; ++d)
      if (fitted(d)) ok = homeDial(d, -1, 0);
    forceCal_ = false;
    if (ok) { saveCal(); l.p(CP("# calibration saved")); emit(l); }
    return;
  }
  if (TOKEQ(cmd, "home")) {
    if (!pingAll() || !configureAll(false)) return;
    // The key stays wherever it was left: get it to rest before any dial moves.
    if (fitted(AX_KEY) && !keyHomed_ && !keyHome(keyDeciToUs(s_, (int32_t)s_.keyHomeSearchDeg * 10))) return;
    Axis ax;
    if (tok[1] && parseAxis(tok[1], &ax) && ax != AX_KEY) { if (fitted(ax)) homeDial(ax, -1, 0); }
    else for (uint8_t d = 0; d < 3 && state_ != ST_ERROR; ++d) if (fitted(d)) homeDial(d, -1, 0);
    return;
  }
  if (TOKEQ(cmd, "learn")) {
    if (!fitted(AX_KEY)) { l.p(CP("# key driver not fitted (set axes)")); emit(l); return; }
    if (pingAll() && configureAll(false) && keyHome(keyDeciToUs(s_, (int32_t)s_.keyHomeSearchDeg * 10))) learnN();
    return;
  }
  if (TOKEQ(cmd, "goto")) {
    if (!(homed_[0] && homed_[1] && homed_[2]) || !tok[3]) { l.p(CP("# goto a b c (1..20), after `home`")); emit(l); return; }
    Combo c;
    for (uint8_t d = 0; d < 3; ++d) {
      const long v = atol(tok[d + 1]);
      if (v < 1 || v > s_.positions) { l.p(CP("# position out of range")); emit(l); return; }
      c.d[d] = (uint8_t)(v - 1);
    }
    if (keyHomed_ && keyPos_ != 0) { l.p(CP("# key not at rest")); emit(l); return; }
    if (gotoCombo(c)) { l.p(CP("# dials at ")).u(c.d[0] + 1).c(' ').u(c.d[1] + 1).c(' ').u(c.d[2] + 1); emit(l); }
    return;
  }
  if (TOKEQ(cmd, "try")) {
    if (!(homed_[0] && homed_[1] && homed_[2] && keyHomed_ && nValid_)) { l.p(CP("# try needs home + learn first")); emit(l); return; }
    Combo c = {{dialPosition(0), dialPosition(1), dialPosition(2)}};
    int32_t reached; bool stalled; uint16_t sg;
    if (!driversOk() || !keyTry(&reached, &stalled, &sg)) return;
    ClassifyParams cp = {n_, keyDeciToUs(s_, s_.keyCleanTolDeci), keyDeciToUs(s_, s_.keyEarlyTolDeci), keyDeciToUs(s_, s_.keySuccessMinDeci)};
    const Outcome o = classify(reached, cp);
    logAttempt(-1, c, reached, stalled, sg, o);
    if (o != OUT_SUCCESS) keyRetract(reached, o);
    else { state_ = ST_SUCCESS; l.p(CP("# key went past N: holding it. `release` to let go.")); emit(l); }
    return;
  }
  if (TOKEQ(cmd, "key")) {
    const int32_t deg = tok[1] ? atol(tok[1]) : 0;
    if (deg < 1 || deg > (int32_t)s_.keyLearnMaxDeg) { l.p(CP("# key <deg>: 1..learn bound, turns clockwise then back")); emit(l); return; }
    if (!fitted(AX_KEY)) { l.p(CP("# key driver not fitted (set axes)")); emit(l); return; }
    if (!pingAll() || !configureAll(false)) return;
    MoveResult r = doMove(AX_KEY, keyDeciToUs(s_, deg * 10), s_.ax[AX_KEY].rps, true, true);
    if (!checkMove(r, AX_KEY, false, true)) return;
    l.p(CP("# key went ")).deci(keyUsToDeci(s_, r.stepsDone)).p(CP(" deg, stalled=")).u(r.stalled).p(CP(", sgMin=")).u(r.sgMin);
    emit(l);
    MoveResult b = doMove(AX_KEY, -r.stepsDone, s_.ax[AX_KEY].rps, true, false);
    checkMove(b, AX_KEY, false, true);
    return;
  }
  if (TOKEQ(cmd, "jog") || TOKEQ(cmd, "sg")) {
    Axis ax;
    const int32_t full = tok[2] ? atol(tok[2]) : 0;
    if (!tok[1] || !parseAxis(tok[1], &ax) || full == 0 || iabs(full) > 800) {
      l.p(CP("# jog|sg <A|B|C|K> <fullsteps, +-800 max>")); emit(l); return;
    }
    if (!fitted(ax)) { l.p(CP("# that driver is not fitted (set axes)")); emit(l); return; }
    if (!pingAll() || !configureAll(false)) return;
    const bool sg = TOKEQ(cmd, "sg");
    MoveResult r = doMove(ax, full * s_.microsteps, s_.ax[ax].rps, true, sg, sg);
    if (!checkMove(r, ax, false, true)) return;
    if (ax == AX_KEY) keyPos_ += r.stepsDone; else dialPos_[ax] += r.stepsDone;
    l.p(CP("# moved ")).i(r.stepsDone / s_.microsteps).p(CP(" full steps, stalled=")).u(r.stalled)
        .p(CP(", sgMin=")).i(r.sgMin == 0xFFFF ? -1 : (int32_t)r.sgMin);
    emit(l);
    return;
  }
  l.p(CP("# unknown command; `help`"));
  emit(l);
}

void Robot::abort() {
  if (state_ == ST_SESSION || state_ == ST_RUN) {
    error(CP("ABORT"), CP("aborted by operator; `resume` to continue"));
  } else {
    releaseAll();
    if (state_ != ST_SUCCESS) state_ = ST_IDLE;
    Line l;
    l.p(CP("# all drivers off"));
    emit(l);
  }
}

void Robot::cmdSet(const char* name, int32_t v) {
  Line l;
  Axis ax = AX_A;
  const uint8_t len = (uint8_t)strlen(name);
  char base[12];
  // Per-axis names end in the axis letter: sgA, maK, rpsB, invC, offA ...
  bool perAxis = len >= 3 && len < sizeof(base) && parseAxis(name + len - 1, &ax);
  if (perAxis) { memcpy(base, name, len - 1); base[len - 1] = 0; }
  bool ok = true;
  if (perAxis && TOKEQ(base, "sg")) s_.ax[ax].sgthrs = (uint8_t)v;
  else if (perAxis && TOKEQ(base, "ma")) s_.ax[ax].runMa = (uint16_t)(v > 1200 ? 1200 : v);
  else if (perAxis && TOKEQ(base, "rps100")) s_.ax[ax].rps = v / 100.0f;
  else if (perAxis && TOKEQ(base, "inv")) s_.ax[ax].invert = v ? 1 : 0;
  else if (perAxis && TOKEQ(base, "off") && ax != AX_KEY) s_.homeOffsetFull[ax] = (int16_t)v;
  else if (TOKEQ(name, "keyhome")) s_.keyHome = v ? KEYHOME_COUNT : KEYHOME_STALL_CCW;
  else if (TOKEQ(name, "axes")) s_.axesMask = (uint8_t)(v & 0x0F);
  else if (TOKEQ(name, "autocal")) s_.sgAutocal = v ? 1 : 0;
  else if (TOKEQ(name, "detentcal")) s_.detentAutocal = v ? 1 : 0;
  else if (TOKEQ(name, "calpct")) s_.sgCalPct = (uint8_t)v;
  else if (TOKEQ(name, "margin")) s_.keyTargetMarginDeci = (uint16_t)v;
  else if (TOKEQ(name, "success")) s_.keySuccessMinDeci = (uint16_t)v;
  else if (TOKEQ(name, "clean")) s_.keyCleanTolDeci = (uint16_t)v;
  else if (TOKEQ(name, "early")) s_.keyEarlyTolDeci = (uint16_t)v;
  else if (TOKEQ(name, "recheck")) s_.recheckEvery = (uint16_t)v;
  else if (TOKEQ(name, "seatma")) s_.seatMa = (uint16_t)v;
  else if (TOKEQ(name, "seatrps100")) s_.seatRps = v / 100.0f;
  else if (TOKEQ(name, "sgmin100")) s_.sgMinRps = v / 100.0f;
  else ok = false;
  if (ok) { l.p(CP("# set ")).s(name).c('=').i(v).p(CP(" (RAM only; copy to config.h)")); }
  else { l.p(CP("# unknown setting ")).s(name); }
  emit(l);
}

// ---------------------------------------------------------------- session
void Robot::startSession(bool thenRun) {
  thenRun_ = thenRun;
  pauseReq_ = false;
  step_ = SS_PING;
  state_ = ST_SESSION;
  sinceRecheck_ = 0;
  consecutiveEarly_ = 0;
  resetOffsets();
  event(CP("SESSION"), prog_.nextIndex);
}

void Robot::tick() {
  if (state_ == ST_SESSION) sessionStep();
  else if (state_ == ST_RUN) runStep();
}

void Robot::sessionStep() {
  if (pauseReq_) { pauseReq_ = false; releaseAll(); state_ = ST_PAUSED; event(CP("PAUSE"), prog_.nextIndex); return; }
  bool ok = true;
  switch (step_) {
    case SS_PING: ok = pingAll() && configureAll(false); step_ = SS_KEYHOME; break;
    case SS_KEYHOME: ok = keyHome(keyDeciToUs(s_, (int32_t)s_.keyHomeSearchDeg * 10)); step_ = SS_KEYCAL; break;
    case SS_KEYCAL: ok = !s_.sgAutocal || calKey(); step_ = SS_SEAT; break;
    case SS_SEAT: ok = seatDials(); step_ = SS_CAL; break;
    case SS_CAL: ok = !(s_.sgAutocal || s_.detentAutocal) || calibrateDials(); step_ = SS_HOME_A; break;
    case SS_HOME_A: ok = homeDial(0, -1, 0); step_ = SS_HOME_B; break;
    case SS_HOME_B: ok = homeDial(1, -1, 0); step_ = SS_HOME_C; break;
    case SS_HOME_C: ok = homeDial(2, -1, 0); step_ = SS_LEARN; break;
    case SS_LEARN: saveCal(); ok = thenRun_ ? learnForRun() : learnN(); step_ = SS_DONE; break;
    case SS_DONE:
      if (thenRun_) { state_ = ST_RUN; event(CP("RUN"), prog_.nextIndex); }
      else state_ = ST_IDLE;
      return;
  }
  (void)ok;  // on failure the building block has already set ST_ERROR
}

void Robot::runStep() {
  if (pauseReq_) { pauseNow(); return; }
  if (prog_.nextIndex >= comboCount(s_.positions)) { finishRun(ST_DONE); return; }
  if (s_.recheckEvery && sinceRecheck_ >= s_.recheckEvery) {
    if (recheck()) sinceRecheck_ = 0;
    return;
  }
  const uint16_t idx = prog_.nextIndex;
  Outcome o;
  if (!attempt(idx, &o)) return;
  prog_.attempts++;
  if (o == OUT_SUCCESS) {
    prog_.state = RUN_SUCCESS;
    prog_.successIndex = idx;
    prog_.nextIndex = idx + 1;
    saveProgress();
    state_ = ST_SUCCESS;
    const Combo c = comboAt(idx, s_.positions);
    Line l;
    l.p(CP("SUCCESS,")).u(hal_.millis()).sep().u(idx);
    for (uint8_t d = 0; d < 3; ++d) l.sep().u(c.d[d] + 1);
    l.sep().deci(keyUsToDeci(s_, keyPos_));
    for (uint8_t d = 0; d < 3; ++d) {
      const int16_t door = (int16_t)(s_.labelAtHome[d] - 1) + (int16_t)s_.labelStep[d] * c.d[d];
      l.sep().u((uint32_t)((door % s_.positions + s_.positions) % s_.positions) + 1);
    }
    emit(l);
    l.clear(); l.p(CP("# key held where it stopped. Check the door, then `release`."));
    emit(l);
    return;
  }
  if (o == OUT_EARLY) {
    // Not a real test of this combination: retry it, unless it keeps happening.
    if (++consecutiveEarly_ >= s_.maxConsecutiveEarly) {
      saveProgress();
      error(CP("EARLY"), CP("key keeps stopping short of N: has a unit moved? Re-seat, then `resume`"));
    }
    return;
  }
  consecutiveEarly_ = 0;
  if (o == OUT_CLEAN) prog_.cleanIndex = idx;
  prog_.nextIndex = idx + 1;
  sinceRecheck_++;
  saveProgress();
}

bool Robot::attempt(int32_t index, Outcome* out) {
  const Combo c = comboAt((uint16_t)index, s_.positions);
  // The dials that don't move in this attempt are checked here; the moving
  // dial and the key are also checked around each of their moves (doMove).
  if (!driversOk()) return false;
  if (!gotoCombo(c)) return false;
  int32_t reached; bool stalled; uint16_t sg;
  if (!keyTry(&reached, &stalled, &sg)) return false;
  ClassifyParams cp = {n_, keyDeciToUs(s_, s_.keyCleanTolDeci), keyDeciToUs(s_, s_.keyEarlyTolDeci), keyDeciToUs(s_, s_.keySuccessMinDeci)};
  *out = classify(reached, cp);
  logAttempt(index, c, reached, stalled, sg, *out);
  if (*out == OUT_SUCCESS) return true;  // leave the key where it is
  return keyRetract(reached, *out);
}

bool Robot::recheck() {
  event(CP("RECHECK"), prog_.nextIndex);
  bool pass = true;
  for (uint8_t d = 0; d < 3; ++d) {
    if (s_.dialHome[d] == HOME_NONE) continue;
    int32_t disc = 0;
    const int32_t expect = dialPos_[d];
    if (!homeDial(d, expect, &disc)) return false;
    // Position 20 can sit just past the stop point (clockwise is endless),
    // so compare modulo one dial turn.
    const int32_t t = turnUs();
    disc = ((disc % t) + t + t / 2) % t - t / 2;
    const bool ok = iabs(disc) <= (int32_t)s_.recheckHomeTolFull * s_.microsteps;
    Line l;
    l.p(CP("RECHECK,")).u(hal_.millis()).sep().u(prog_.nextIndex).sep().c(kAxisChar[d]).sep()
        .i(disc / s_.microsteps).p(CP(",,")).u(ok);
    emit(l);
    pass = pass && ok;
  }
  const int32_t oldN = n_;
  if (pass) {
    if (!learnForRun()) return false;
    const bool ok = iabs(n_ - oldN) <= keyDeciToUs(s_, s_.recheckNTolDeci);
    Line l;
    l.p(CP("RECHECK,")).u(hal_.millis()).sep().u(prog_.nextIndex).p(CP(",K,,")).deci(keyUsToDeci(s_, n_)).sep().u(ok);
    emit(l);
    pass = ok;
  }
  if (!pass) {
    prog_.nextIndex = prog_.verifiedIndex;
    saveProgress();
    error(CP("RECHECK"), CP("a unit has moved (home or N changed): re-seat, then `resume` (rewound to last check)"));
    return false;
  }
  prog_.verifiedIndex = prog_.nextIndex;
  saveProgress();
  return true;
}

void Robot::pauseNow() {
  pauseReq_ = false;
  // Verify before stopping, so a later resume needn't rewind.
  if (s_.recheckEvery && sinceRecheck_ > 0 && !recheck()) return;
  releaseAll();
  state_ = ST_PAUSED;
  event(CP("PAUSE"), prog_.nextIndex);
}

void Robot::finishRun(RobotState st) {
  prog_.state = RUN_EXHAUSTED;
  saveProgress();
  releaseAll();
  state_ = st;
  event(CP("DONE"), prog_.nextIndex);
  Line l;
  l.p(CP("# all combinations tried without a clear success: look at the FALSESET lines in the log"));
  emit(l);
}

// ---------------------------------------------------------------- building blocks
bool Robot::pingAll() {
  bool ok = true;
  for (uint8_t a = 0; a < AX_COUNT; ++a) {
    const DriverStatus st = hal_.ping((Axis)a);
    Line l;
    l.p(CP("DRV,")).c(kAxisChar[a]).sep().u(st.present).sep().x(st.version).sep().u(st.ms1).sep().u(st.ms2)
        .sep().u(st.diagPin).sep().u(st.diagIoin).sep().x(st.gstat).sep().u(st.ifcnt);
    emit(l);
    if (!fitted(a)) continue;
    if (!st.present || st.version != 0x21) ok = false;
    else if (st.ms1 != kMs1[a] || st.ms2 != kMs2[a]) ok = false;
  }
  if (!ok) error(CP("DRIVER"), CP("a driver is missing or has the wrong address: 12 V on? UART leads? jumpers?"));
  return ok;
}

bool Robot::configureAll(bool seatCurrent) {
  const uint32_t tc = tcoolthrsFor(s_, s_.sgMinRps);
  for (uint8_t a = 0; a < AX_COUNT; ++a) {
    if (!fitted(a)) continue;
    // configure() clears GSTAT. A driver already set up (and not released
    // since) may have reset after its last check, and its motor may have
    // jumped (DS §3.6.1): report that rather than wipe it. The first setup
    // after power-up or a release clears the power-on flag, which is expected.
    if (configured_[a] && !driverOk((Axis)a, CP("config"))) { driverFault(); return false; }
    DriverSetup ds;
    ds.runMa = (seatCurrent && a != AX_KEY) ? s_.seatMa : s_.ax[a].runMa;
    if (ds.runMa > 1200) ds.runMa = 1200;  // wiring.md §7 ceiling
    ds.holdPct = s_.ax[a].holdPct;
    ds.sgthrs = s_.ax[a].sgthrs;
    ds.tcoolthrs = tc;
    if (!hal_.configure((Axis)a, ds)) {
      error(CP("CONFIG"), CP("driver settings did not read back (UART)"));
      return false;
    }
    configured_[a] = true;
    hal_.enable((Axis)a, true);
  }
  return true;
}

bool Robot::tuned() {
  for (uint8_t a = 0; a < AX_COUNT; ++a) {
    // With autocal, only the key needs a threshold up front: the session's
    // first move finds its rest stop. The dials calibrate before homing.
    const bool needs = fitted(a) && ((a == AX_KEY) || (!s_.sgAutocal && s_.dialHome[a] == HOME_STALL));
    if (needs && s_.ax[a].sgthrs == 0) {
      if (s_.sgAutocal)
        error(CP("TUNE"), CP("no key calibration yet: turn the key back to its start by hand, then `calibrate`"));
      else
        error(CP("TUNE"), CP("StallGuard threshold not set (bring-up stage 3): set sgA/sgB/sgC/sgK"));
      return false;
    }
  }
  for (uint8_t d = 0; d < 3; ++d)
    if (s_.homeOffsetFull[d] < 0) { error(CP("TUNE"), CP("home offset must be >= 0")); return false; }
  return true;
}

bool Robot::needAll() {
  if (s_.axesMask == 0x0F) return true;
  Line l;
  l.p(CP("# a run needs all four drivers: `set axes 15` (or CFG_AXES_MASK)"));
  emit(l);
  return false;
}

bool Robot::seatDials() {
  if (keyHomed_ && keyPos_ != 0) { error(CP("KEYOUT"), CP("refusing to turn dials with the key out of rest")); return false; }
  if (!configureAll(true)) return false;
  const int32_t steps = dialDegToUs(s_, s_.seatDialDeg);
  for (uint8_t d = 0; d < 3; ++d) {
    homed_[d] = false;
    if (!fitted(d)) continue;
    // Slow and bounded, clockwise (logical +): the dials turn clockwise
    // without limit and only stop anticlockwise (Paul, 2026-10-06), so the
    // seat turn can never press a seated plug into the stop.
    MoveResult r = doMove((Axis)d, steps, s_.seatRps, false, false);
    if (!checkMove(r, (Axis)d, false, true)) return false;
  }
  event(CP("SEATED"), 0);
  return configureAll(false);
}

bool Robot::homeDial(uint8_t d, int32_t expectDist, int32_t* discrepancy) {
  const Axis ax = (Axis)d;
  const float rps = s_.ax[d].rps;
  if (s_.dialHome[d] == HOME_NONE) {
    dialPos_[d] = 0;
    homed_[d] = true;
    event(CP("HOME_NONE"), d);
    return true;
  }
  if (keyHomed_ && keyPos_ != 0) { error(CP("KEYOUT"), CP("refusing to turn dials with the key out of rest")); return false; }
  homed_[d] = false;
  const int32_t bound = dialDegToUs(s_, s_.homeMaxDialDeg);
  MoveResult r1 = doMove(ax, -bound, rps, true, true);
  if (!checkMove(r1, ax, true, true)) return false;
  Line l;
  l.p(CP("HOME,")).u(hal_.millis()).sep().c(kAxisChar[d]).p(CP(",1,")).i(-r1.stepsDone / s_.microsteps).sep()
      .u(r1.stalled).sep().i(r1.sgMin == 0xFFFF ? -1 : (int32_t)r1.sgMin);
  emit(l);
  if (!r1.stalled) {
    error(CP("HOME"), CP("dial turned its full bound without stalling: plug seated? hard stop? SGTHRS?"));
    return false;
  }
  if (discrepancy && expectDist >= 0) *discrepancy = -r1.stepsDone - expectDist;
  const int32_t backoff = (int32_t)s_.homeBackoffFull * s_.microsteps;
  const int32_t tol = (int32_t)s_.homeRepeatTolFull * s_.microsteps;
  MoveResult rb = doMove(ax, backoff, rps, true, false);
  if (!checkMove(rb, ax, false, false)) return false;
  MoveResult r2 = doMove(ax, -(backoff + 2 * tol), rps, true, true);
  if (!checkMove(r2, ax, true, true)) return false;
  l.clear();
  l.p(CP("HOME,")).u(hal_.millis()).sep().c(kAxisChar[d]).p(CP(",2,")).i(-r2.stepsDone / s_.microsteps).sep()
      .u(r2.stalled).sep().i(r2.sgMin == 0xFFFF ? -1 : (int32_t)r2.sgMin);
  emit(l);
  if (!r2.stalled || iabs(-r2.stepsDone - backoff) > tol) {
    error(CP("HOMEREP"), CP("second homing pass disagrees with the first: tune SGTHRS / speed"));
    return false;
  }
  dialPos_[d] = 0;  // the stall point is zero
  homed_[d] = true;
  // Position 1 = the first click at least 3 full steps clockwise of the stall
  // point (so a dial at position 1 doesn't lean on its stop).
  const bool clicks = s_.detentAutocal && notchOk_[d];
  offsetFromClicks_[d] = clicks;
  offsetUs_[d] = clicks ? detentOffset(notchAbs_[d], absCount_[d], usPerPosition(s_), 3 * s_.microsteps,
                                      cal_.offsetUs[d])
                        : (int32_t)s_.homeOffsetFull[d] * s_.microsteps;
  l.clear();
  l.p(CP("OFFSET,")).u(hal_.millis()).sep().c(kAxisChar[d]).sep().deci(offsetUs_[d] * 10 / s_.microsteps)
      .sep().u(clicks);
  emit(l);
  return moveDialTo(d, dialTarget(d, 0));
}

bool Robot::keyHome(int32_t boundUs) {
  if (s_.keyHome == KEYHOME_COUNT) {  // no rest stop: trust that the key is at rest now
    keyPos_ = 0;
    keyHomed_ = true;
    return true;
  }
  MoveResult r = doMove(AX_KEY, -boundUs, s_.ax[AX_KEY].rps, true, false);
  if (!checkMove(r, AX_KEY, true, true)) return false;
  if (!r.stalled) {
    error(CP("KEYHOME"), CP("key found no rest stop turning anticlockwise: sgK too low? (no stop at all: `set keyhome 1`)"));
    return false;
  }
  keyPos_ = 0;
  keyHomed_ = true;
  return true;
}

bool Robot::learnN() {
  if (!keyHomed_) { error(CP("LEARN"), CP("key not homed")); return false; }
  int32_t v[9];
  uint8_t reps = s_.keyLearnRepeats;
  if (reps < 1) reps = 1;
  if (reps > 9) reps = 9;
  const int32_t bound = keyDeciToUs(s_, (int32_t)s_.keyLearnMaxDeg * 10);
  for (uint8_t t = 0; t < reps; ++t) {
    MoveResult r = doMove(AX_KEY, bound, s_.ax[AX_KEY].rps, true, true);
    if (!checkMove(r, AX_KEY, true, true)) return false;
    Line l;
    l.p(CP("LEARN,")).u(hal_.millis()).sep().u(t + 1).sep().i(r.stepsDone).sep().deci(keyUsToDeci(s_, r.stepsDone))
        .sep().u(r.stalled).sep().i(r.sgMin == 0xFFFF ? -1 : (int32_t)r.sgMin);
    emit(l);
    keyPos_ = r.stepsDone;
    if (!r.stalled) {
      // The key did not stop: this dial setting may be the combination.
      state_ = ST_SUCCESS;
      l.clear();
      l.p(CP("ERR,")).u(hal_.millis()).p(CP(",NOSTOP,key turned the full learn bound without stopping: this dial setting may open the safe. Key held; `release` to let go."));
      emit(l);
      return false;
    }
    v[t] = r.stepsDone;
    if (!keyRetract(r.stepsDone, OUT_CLEAN)) return false;
  }
  sort3(v, reps);
  n_ = v[reps / 2];
  nValid_ = true;
  const int32_t spread = v[reps - 1] - v[0];
  Line l;
  l.p(CP("NSTOP,")).u(hal_.millis()).sep().i(n_).sep().deci(keyUsToDeci(s_, n_)).sep().deci(keyUsToDeci(s_, spread));
  emit(l);
  if (spread > keyDeciToUs(s_, s_.keyLearnSpreadDeci)) {
    nValid_ = false;
    error(CP("LEARN"), CP("key stop angle not repeatable across the learn tries"));
    return false;
  }
  return true;
}

// ---------------------------------------------------------------- calibration
// Key: from rest, turn keyCalDeg clockwise (free travel: the stop is at
// ~100 deg), take the median StallGuard reading, set the threshold from it,
// then go back to rest by stalling on the rest stop with the new threshold,
// which proves it works.
bool Robot::calKey() {
  if (!keyHomed_ || keyPos_ != 0) { error(CP("KEYCAL"), CP("key not at rest")); return false; }
  MedianSink m;
  m.begin();
  MoveResult r = doMove(AX_KEY, keyDeciToUs(s_, (int32_t)s_.keyCalDeg * 10), s_.ax[AX_KEY].rps, true, true, false, &m);
  keyPos_ += r.stepsDone;
  if (!checkMove(r, AX_KEY, false, true)) return false;
  if (r.stalled) {
    error(CP("KEYCAL"), CP("key stopped during its free calibration travel: was it at its start? threshold too sensitive?"));
    return false;
  }
  const uint8_t n = m.count();
  const uint16_t base = m.median();
  const bool apply = s_.sgAutocal || forceCal_;
  if (n < 8 || base < s_.sgCalMinBase) {
    error(CP("KEYCAL"), CP("too few or too low StallGuard readings on the key's free travel (speed? current?)"));
    return false;
  }
  if (apply) {
    s_.ax[AX_KEY].sgthrs = sgthrsFromBaseline(base, s_.sgCalPct);
    cal_.sgthrs[AX_KEY] = s_.ax[AX_KEY].sgthrs;
    cal_.baseline[AX_KEY] = base;
    if (!configureAll(false)) return false;
  }
  Line l;
  l.p(CP("CAL,")).u(hal_.millis()).p(CP(",K,")).u(base).sep().u(s_.ax[AX_KEY].sgthrs).p(CP(",,,")).u(n);
  emit(l);
  return keyRetract(keyPos_, OUT_CLEAN);  // must stall on the rest stop
}

// Dial: one free clockwise turn (+ the ramps). The dials turn clockwise
// without limit (Paul, 2026-10-06), so nothing can be pressed.
bool Robot::calDial(uint8_t d) {
  if (keyHomed_ && keyPos_ != 0) { error(CP("KEYOUT"), CP("refusing to turn dials with the key out of rest")); return false; }
  DetentProfile prof;
  const uint16_t fullPerTurn = (uint16_t)(s_.fullStepsPerRev * s_.dialGear);
  prof.begin(absCount_[d], s_.microsteps, fullPerTurn);
  MoveResult r = doMove((Axis)d, turnUs() + turnUs() / 4, s_.ax[d].rps, true, true, false, &prof);
  if (!checkMove(r, (Axis)d, false, true)) return false;
  if (r.stalled) {
    error(CP("SGCAL"), CP("dial stalled on its free calibration turn: plug jammed? old threshold too sensitive (`set sgA 0`)?"));
    return false;
  }
  if (!prof.complete()) {
    error(CP("SGCAL"), CP("too few StallGuard readings over the calibration turn (speed? acceleration?)"));
    return false;
  }
  const uint16_t base = prof.baseline();
  uint16_t amp, resid;
  int32_t notch;
  prof.fit(&amp, &resid, &notch);
  notchAbs_[d] = notch;
  notchOk_[d] = amp >= s_.detentMinAmp && amp >= 2 * resid;
  if (s_.sgAutocal || forceCal_) {
    if (base < s_.sgCalMinBase) {
      error(CP("SGCAL"), CP("free-running StallGuard reading too low to tell from a stall (speed? current?)"));
      return false;
    }
    s_.ax[d].sgthrs = sgthrsFromBaseline(base, s_.sgCalPct);
    cal_.sgthrs[d] = s_.ax[d].sgthrs;
    cal_.baseline[d] = base;
  }
  Line l;
  l.p(CP("CAL,")).u(hal_.millis()).sep().c(kAxisChar[d]).sep().u(base).sep().u(s_.ax[d].sgthrs).sep().u(amp)
      .sep().u(resid).sep().u(notchOk_[d]);
  emit(l);
  if (s_.detentAutocal && !notchOk_[d]) {
    l.clear();
    l.p(CP("# clicks not clear in dial ")).c(kAxisChar[d]).p(CP("'s StallGuard ripple: using CFG_HOME_OFFSET for it"));
    emit(l);
  }
  return true;
}

bool Robot::calibrateDials() {
  for (uint8_t d = 0; d < 3; ++d)
    if (fitted(d) && !calDial(d)) return false;
  return configureAll(false);  // push the new thresholds before homing on them
}

void Robot::saveCal() {
  for (uint8_t d = 0; d < 3; ++d)
    if (homed_[d]) cal_.offsetUs[d] = offsetFromClicks_[d] ? (int16_t)offsetUs_[d] : (int16_t)-1;
  calStore_.save(cal_);
}

// Learn N where the result is known: at the most recent clean fail. Before
// there is one (fresh run), learn at the next two combinations and keep the
// lower N, so a false set at the first combination can't inflate N.
bool Robot::learnForRun() {
  const bool haveClean = prog_.cleanIndex != 0xFFFF;
  const uint16_t first = haveClean ? prog_.cleanIndex : prog_.nextIndex;
  if (!gotoCombo(comboAt(first, s_.positions)) || !learnN()) return false;
  if (haveClean || first + 1 >= comboCount(s_.positions)) return true;
  const int32_t n1 = n_;
  if (!gotoCombo(comboAt(first + 1, s_.positions)) || !learnN()) return false;
  if (n1 < n_) n_ = n1;
  event(CP("NSET"), keyUsToDeci(s_, n_));
  return true;
}

bool Robot::gotoCombo(const Combo& c) {
  if (keyHomed_ && keyPos_ != 0) { error(CP("KEYOUT"), CP("refusing to turn dials with the key out of rest")); return false; }
  for (uint8_t d = 0; d < 3; ++d)
    if (!moveDialTo(d, dialTarget(d, c.d[d]))) return false;
  return true;
}

bool Robot::moveDialTo(uint8_t d, int32_t target) {
  const Axis ax = (Axis)d;
  int32_t delta = target - dialPos_[d];
  if (delta == 0) return true;
  int32_t over = 0;
  if (s_.dialApproachFull && delta < 0) {
    over = (int32_t)s_.dialApproachFull * s_.microsteps;
    if (over > target) over = target;  // never into the stop
  }
  MoveResult r = doMove(ax, delta - over, s_.ax[d].rps, true, false);
  dialPos_[d] += r.stepsDone;
  if (!checkMove(r, ax, false, false)) return false;
  if (over) {
    r = doMove(ax, over, s_.ax[d].rps, true, false);
    dialPos_[d] += r.stepsDone;
    if (!checkMove(r, ax, false, false)) return false;
  }
  return true;
}

bool Robot::keyTry(int32_t* reached, bool* stalled, uint16_t* sgMin) {
  const int32_t target = n_ + keyDeciToUs(s_, s_.keyTargetMarginDeci);
  MoveResult r = doMove(AX_KEY, target, s_.ax[AX_KEY].rps, true, true);
  keyPos_ += r.stepsDone;
  if (!checkMove(r, AX_KEY, false, true)) return false;
  *reached = r.stepsDone;
  *stalled = r.stalled;
  *sgMin = r.sgMin;
  return true;
}

bool Robot::keyRetract(int32_t reached, Outcome o) {
  if (s_.keyHome == KEYHOME_STALL_CCW) {
    const int32_t extra = keyDeciToUs(s_, (int32_t)s_.keyHomeExtraDeg * 10);
    MoveResult r = doMove(AX_KEY, -(reached + extra), s_.ax[AX_KEY].rps, true, false);
    if (!checkMove(r, AX_KEY, true, true)) return false;
    if (!r.stalled) {
      error(CP("KEYHOME"), CP("key did not find its rest stop on the way back"));
      return false;
    }
  } else {
    // No rest stop: return the field to where it started. StallGuard stops
    // the motor before it slips a pole (datasheet §11.3), so the rotor
    // follows the field back; the periodic re-learn of N catches any drift.
    (void)o;
    MoveResult r = doMove(AX_KEY, -reached, s_.ax[AX_KEY].rps, true, false);
    if (!checkMove(r, AX_KEY, false, false)) return false;
  }
  keyPos_ = 0;
  return true;
}

MoveResult Robot::doMove(Axis ax, int32_t steps, float rps, bool stopOnStall, bool sampleSG, bool traceSG,
                         SgSink* sink) {
  const AxisCfg& a = s_.ax[ax];
  const float upr = (float)usPerMotorRev(s_);
  MoveRequest r;
  r.axis = ax;
  r.steps = steps;
  r.maxSps = rps * upr;
  r.startSps = (a.startRps < rps ? a.startRps : rps) * upr;
  r.accelSps2 = a.accelRps2 * upr;
  r.stopOnStall = stopOnStall;
  r.sampleSG = sampleSG || traceSG || sink;
  r.traceSG = traceSG;
  r.sgSink = sink;
  r.ignoreStallSteps = (uint16_t)(s_.stallIgnoreFull * s_.microsteps);
  const float n = (float)iabs(steps);
  const float t = n / r.maxSps + r.maxSps / r.accelSps2;  // upper bound of the profile time
  r.timeoutMs = (uint32_t)(2000.0f * t) + 2000;
  // A driver that reset has no current setting and no StallGuard: never
  // move on one. Checked again after the move, so a reset during it never
  // reaches a classification (an open-loop key move reads as a success).
  if (!driverOk(ax, CP("before"))) {
    MoveResult none;
    none.driverFault = true;
    return none;
  }
  MoveResult res = hal_.move(r);
  if (ax < 3) absCount_[ax] += res.stepsDone;
  if (!driverOk(ax, CP("after"))) res.driverFault = true;
  return res;
}

bool Robot::checkMove(const MoveResult& r, Axis ax, bool expectStall, bool allowStall) {
  (void)expectStall;  // callers check the "expected a stall but none" case themselves
  if (r.driverFault) { driverFault(); return false; }  // first: a reset explains any other symptom
  if (r.aborted) { error(CP("ABORT"), CP("move aborted by operator")); return false; }
  if (r.diagHighAtStart) { error(CP("DIAG"), CP("DIAG already high before the move: lead off, or driver error")); return false; }
  if (r.timedOut) { error(CP("TIMEOUT"), CP("move took too long")); return false; }
  if (r.stalled && !allowStall) {
    Line l;
    l.p(CP("# unexpected stall on axis ")).c(kAxisChar[ax]);
    emit(l);
    error(CP("JAM"), CP("unexpected stall: something is blocking, or SGTHRS too sensitive"));
    return false;
  }
  return true;
}

bool Robot::driverOk(Axis ax, const char* when) {
  const uint8_t g = hal_.gstat(ax);
  if (g == 0) return true;
  Line l;
  l.p(CP("GSTAT,")).u(hal_.millis()).sep().c(kAxisChar[ax]).sep().x(g).sep().p(when);
  emit(l);
  return false;
}

bool Robot::driversOk() {
  bool ok = true;
  for (uint8_t a = 0; a < AX_COUNT; ++a)
    if (fitted(a) && !driverOk((Axis)a, CP("attempt"))) ok = false;  // log every one at fault
  if (!ok) driverFault();
  return ok;
}

// Stop, as for any other hardware fault: a dip in a driver's supply is a
// fault to fix, and positions since it can't be trusted. `resume` sets up
// every driver again, re-homes, re-learns N. In a run, rewind now to the last
// re-check (as a failed re-check does), whatever resumeFromCheckpoint says:
// the attempt in progress, or the one before, may have run with a driver
// that had reset (control/firmware/README.md, "Driver resets").
void Robot::driverFault() {
  if (state_ == ST_RUN && prog_.state == RUN_ACTIVE && prog_.nextIndex != prog_.verifiedIndex) {
    prog_.nextIndex = prog_.verifiedIndex;
    saveProgress();
    Line l;
    l.p(CP("# rewound to the last re-checked index ")).u(prog_.verifiedIndex);
    emit(l);
  }
  error(CP("DRVFAULT"), CP("driver reset or fault (see the GSTAT line): power dip? Fix it and `resume`"));
}

// ---------------------------------------------------------------- helpers
int32_t Robot::dialTarget(uint8_t d, uint8_t pos) const {
  return offsetUs_[d] + (int32_t)pos * usPerPosition(s_);
}

uint8_t Robot::dialPosition(uint8_t d) const {
  const int32_t rel = dialPos_[d] - offsetUs_[d];
  const int32_t pp = usPerPosition(s_);
  int32_t p = (rel + (rel >= 0 ? pp / 2 : -pp / 2)) / pp;
  if (p < 0) p = 0;
  if (p >= s_.positions) p = s_.positions - 1;
  return (uint8_t)p;
}

void Robot::logAttempt(int32_t index, const Combo& c, int32_t reached, bool stalled, uint16_t sgMin, Outcome o) {
  Line l;
  l.p(CP("ATT,")).u(hal_.millis()).sep().i(index);
  for (uint8_t d = 0; d < 3; ++d) l.sep().u(c.d[d] + 1);
  l.sep().i(reached).sep().deci(keyUsToDeci(s_, reached)).sep().u(stalled).sep()
      .i(sgMin == 0xFFFF ? -1 : (int32_t)sgMin).sep().s(outcomeName(o)).sep().deci(keyUsToDeci(s_, n_));
  emit(l);
}

void Robot::error(const char* code, const char* text) {
  Line l;
  l.p(CP("ERR,")).u(hal_.millis()).sep().p(code).sep().p(text);
  emit(l);
  releaseAll();
  state_ = ST_ERROR;
}

void Robot::event(const char* name, int32_t detail) {
  Line l;
  l.p(CP("EV,")).u(hal_.millis()).sep().p(name).sep().i(detail);
  emit(l);
}

void Robot::releaseAll() {
  for (uint8_t a = 0; a < AX_COUNT; ++a) {
    hal_.enable((Axis)a, false);
    configured_[a] = false;  // nothing relies on its setup now
  }
  homed_[0] = homed_[1] = homed_[2] = false;
  keyHomed_ = false;
}

void Robot::printStatus() {
  static const char* const names[] = {"IDLE", "SESSION", "RUN", "PAUSED", "SUCCESS", "DONE", "ERROR"};
  Line l;
  l.p(CP("# state=")).s(names[state_]).p(CP(" run=")).u(prog_.state).p(CP(" next=")).u(prog_.nextIndex)
      .p(CP(" verified=")).u(prog_.verifiedIndex).p(CP(" attempts=")).u(prog_.attempts).p(CP(" N="));
  if (nValid_) l.deci(keyUsToDeci(s_, n_)); else l.c('-');
  l.p(CP(" homed="));
  for (uint8_t d = 0; d < 3; ++d) l.c(homed_[d] ? kAxisChar[d] : '-');
  l.c(keyHomed_ ? 'K' : '-');
  emit(l);
}

void Robot::printCfg() {
  Line l;
  for (uint8_t a = 0; a < AX_COUNT; ++a) {
    const AxisCfg& x = s_.ax[a];
    l.clear();
    l.p(CP("CFG,axis")).c(kAxisChar[a]).p(CP(",inv=")).u(x.invert).p(CP(",ma=")).u(x.runMa).p(CP(",hold%="))
        .u(x.holdPct).p(CP(",sg=")).u(x.sgthrs).p(CP(",rps100=")).u((uint32_t)(x.rps * 100 + 0.5f));
    emit(l);
  }
  l.clear();
  l.p(CP("CFG,mech,axes=")).u(s_.axesMask).p(CP(",fullsteps=")).u(s_.fullStepsPerRev).p(CP(",ustep=")).u(s_.microsteps).p(CP(",dialGear="))
      .u(s_.dialGear).p(CP(",keyGear=")).u(s_.keyGear).p(CP(",positions=")).u(s_.positions);
  emit(l);
  l.clear();
  l.p(CP("CFG,home,mode=")).u(s_.dialHome[0]).u(s_.dialHome[1]).u(s_.dialHome[2]).p(CP(",off="))
      .i(s_.homeOffsetFull[0]).c('/').i(s_.homeOffsetFull[1]).c('/').i(s_.homeOffsetFull[2])
      .p(CP(",backoff=")).u(s_.homeBackoffFull).p(CP(",tol=")).u(s_.homeRepeatTolFull)
      .p(CP(",seatDeg=")).u(s_.seatDialDeg).p(CP(",seatma=")).u(s_.seatMa);
  emit(l);
  l.clear();
  l.p(CP("CFG,key,home=")).u(s_.keyHome).p(CP(",learnMax=")).u(s_.keyLearnMaxDeg).p(CP(",margin=")).deci(s_.keyTargetMarginDeci)
      .p(CP(",success=")).deci(s_.keySuccessMinDeci).p(CP(",clean=")).deci(s_.keyCleanTolDeci)
      .p(CP(",early=")).deci(s_.keyEarlyTolDeci);
  emit(l);
  l.clear();
  l.p(CP("CFG,cal,autocal=")).u(s_.sgAutocal).p(CP(",calpct=")).u(s_.sgCalPct).p(CP(",minbase=")).u(s_.sgCalMinBase)
      .p(CP(",detentcal=")).u(s_.detentAutocal).p(CP(",minamp=")).u(s_.detentMinAmp).p(CP(",keyCalDeg="))
      .u(s_.keyCalDeg).p(CP(",offsetsFull=")).deci(offsetUs_[0] * 10 / s_.microsteps).c('/')
      .deci(offsetUs_[1] * 10 / s_.microsteps).c('/').deci(offsetUs_[2] * 10 / s_.microsteps);
  emit(l);
  l.clear();
  l.p(CP("CFG,run,recheck=")).u(s_.recheckEvery).p(CP(",sgmin100=")).u((uint32_t)(s_.sgMinRps * 100 + 0.5f))
      .p(CP(",tcoolthrs=")).u(tcoolthrsFor(s_, s_.sgMinRps)).p(CP(",hash=")).x(positionHash(s_));
  emit(l);
}

}  // namespace core
