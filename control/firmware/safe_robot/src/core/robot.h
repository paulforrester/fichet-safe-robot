// The sequencer: session start (seat -> home -> learn N), the attempt loop,
// periodic re-checks, resume after power loss, and the serial commands.
// Plain C++; all hardware access goes through Hal.
//
// Serial log protocol (one line each; the logger keys on the first field):
//   # text                                   human-readable info
//   EV,ms,name,detail                        events
//   DRV,axis,present,version,ms1,ms2,diagPin,diagIoin,gstat,ifcnt
//   HOME,ms,dial,pass,distFull,stalled,sgMin
//   LEARN,ms,try,keySteps,keyDeg,stalled,sgMin
//   NSTOP,ms,keySteps,keyDeg,spreadDeg
//   ATT,ms,index,a,b,c,keySteps,keyDeg,stalled,sgMin,class,nDeg
//   RECHECK,ms,index,dial,discrepancyFull,nDeg,ok
//   SUCCESS,ms,index,a,b,c,keyDeg,doorA,doorB,doorC
//   CAL,ms,axis,baseline,sgthrs,amp,resid,clicksTrusted   (self-calibration)
//   OFFSET,ms,dial,offsetFull,fromClicks                  (position 1 after homing)
//   GSTAT,ms,axis,gstat,when      a driver reset or fault (GstatBits, hex); when =
//                                 before / after (a move), attempt, config
//   ERR,ms,code,text
// Dial positions a,b,c are 1..20 counted from each dial's home stop.
#pragma once
#include <stdint.h>
#include "calib.h"
#include "calstore.h"
#include "classify.h"
#include "combo.h"
#include "hal.h"
#include "journal.h"
#include "line.h"
#include "settings.h"

namespace core {

enum RobotState : uint8_t {
  ST_IDLE = 0,    // nothing running (dials may or may not be homed)
  ST_SESSION,     // session start in progress (ping, seat, home, learn)
  ST_RUN,         // attempt loop
  ST_PAUSED,      // run paused by the operator; `resume` continues
  ST_SUCCESS,     // stopped on a success; key held where it got to
  ST_DONE,        // all combinations tried
  ST_ERROR        // stopped on an error; see the last ERR line
};

class Robot {
 public:
  Robot(Hal& hal, Settings& s);
  void boot();                       // load the journal, report
  void handleLine(const char* line); // one serial command
  void tick();                       // do one unit of work if busy
  void requestPause() { pauseReq_ = true; }
  void abort();                      // '!' between moves, or the `abort` command
  RobotState state() const { return state_; }
  const Progress& progress() const { return prog_; }
  int32_t learnedN() const { return n_; }
  bool busy() const { return state_ == ST_SESSION || state_ == ST_RUN; }

 private:
  enum Step : uint8_t {
    SS_PING, SS_KEYHOME, SS_KEYCAL, SS_SEAT, SS_CAL, SS_HOME_A, SS_HOME_B, SS_HOME_C, SS_LEARN, SS_DONE
  };
  // session / run
  void startSession(bool thenRun);
  void sessionStep();
  void runStep();
  bool attempt(int32_t index, Outcome* out);
  bool recheck();
  void finishRun(RobotState st);
  void pauseNow();
  // building blocks (return false after reporting an error)
  bool pingAll();
  bool configureAll(bool seatCurrent);
  bool seatDials();
  bool homeDial(uint8_t d, int32_t expectDist, int32_t* discrepancy);
  bool keyHome(int32_t boundUs);
  bool learnN();
  bool learnForRun();
  bool calKey();
  bool calDial(uint8_t d);
  bool calibrateDials();
  void saveCal();
  void resetOffsets();
  int32_t turnUs() const { return usPerMotorRev(s_) * s_.dialGear; }
  bool gotoCombo(const Combo& c);
  bool moveDialTo(uint8_t d, int32_t targetUs);
  bool keyTry(int32_t* reached, bool* stalled, uint16_t* sgMin);
  bool keyRetract(int32_t reached, Outcome o);
  MoveResult doMove(Axis ax, int32_t steps, float rps, bool stopOnStall, bool sampleSG, bool traceSG = false,
                    SgSink* sink = nullptr);
  bool checkMove(const MoveResult& r, Axis ax, bool expectStall, bool allowStall);
  bool driverOk(Axis ax, const char* when);  // GSTAT clear? Else logs a GSTAT line
  bool driversOk();                          // all fitted drivers; stops on a fault
  void driverFault();                        // the stop: rewind (in a run), ERR DRVFAULT
  // helpers
  int32_t dialTarget(uint8_t d, uint8_t pos) const;
  uint8_t dialPosition(uint8_t d) const;
  void error(const char* code, const char* text);  // code/text are CP() literals
  void event(const char* name, int32_t detail);    // name is a CP() literal
  void emit(Line& l) { hal_.emit(l.str()); }
  void saveProgress() { journal_.save(prog_); }
  void releaseAll();
  void printStatus();
  void printCfg();
  void cmdSet(const char* name, int32_t v);
  void logAttempt(int32_t index, const Combo& c, int32_t reached, bool stalled, uint16_t sgMin, Outcome o);
  bool tuned();
  bool fitted(uint8_t a) const { return (s_.axesMask >> a) & 1; }
  bool needAll();

  Hal& hal_;
  Settings& s_;
  Journal journal_;
  CalStore calStore_;
  CalRecord cal_;
  Progress prog_;
  RobotState state_ = ST_IDLE;
  Step step_ = SS_PING;
  bool thenRun_ = false;
  bool pauseReq_ = false;
  bool homed_[3] = {false, false, false};
  int32_t dialPos_[3] = {0, 0, 0};  // logical microsteps from each stall zero
  bool keyHomed_ = false;
  bool configured_[AX_COUNT] = {false, false, false, false};  // set up, and not released since
  int32_t keyPos_ = 0;
  bool nValid_ = false;
  int32_t n_ = 0;
  uint16_t sinceRecheck_ = 0;
  int32_t absCount_[3] = {0, 0, 0};   // every dial microstep since boot (click phases)
  int32_t offsetUs_[3] = {0, 0, 0};   // position 1 from the stall zero
  int32_t notchAbs_[3] = {0, 0, 0};   // click centre, absolute microsteps mod one click
  bool notchOk_[3] = {false, false, false};
  bool offsetFromClicks_[3] = {false, false, false};
  bool forceCal_ = false;             // `calibrate`: apply even if autocal is off
  uint8_t consecutiveEarly_ = 0;
};

}  // namespace core
