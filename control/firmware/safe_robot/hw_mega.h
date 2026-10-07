// Hardware layer for the Mega 2560 + RAMPS 1.4 + 4 x TMC2209 (UART).
// Kept thin: step pulses, DIAG interrupt latches, TMCStepper calls, EEPROM,
// USB serial. All sequencing lives in src/core (plain C++, host-tested).
#pragma once
#include <Arduino.h>
#include <TMCStepper.h>

#include "src/core/hal.h"
#include "src/core/robot.h"
#include "src/core/settings.h"
#include "src/core/tmc_frame.h"

class HwMega : public core::Hal {
 public:
  explicit HwMega(core::Settings& s);
  void begin();
  // USB serial: collects a command line; returns true when one is complete.
  bool readLine(char* out, uint8_t cap);
  bool takeButtonPress();   // debounced press seen (in loop or during a move)
  bool takeAbort();         // '!' arrived while no move was running
  void updateLed(core::RobotState st);

  // core::Hal
  core::DriverStatus ping(core::Axis ax) override;
  bool configure(core::Axis ax, const core::DriverSetup& s) override;
  uint8_t gstat(core::Axis ax) override;
  void enable(core::Axis ax, bool on) override;
  core::MoveResult move(const core::MoveRequest& r) override;
  uint32_t millis() override { return ::millis(); }
  void emit(const char* line) override { Serial.println(line); }
  uint8_t storeRead(uint16_t addr) override;
  void storeWrite(uint16_t addr, uint8_t v) override;
  uint16_t storeSize() override;

 private:
  bool pollSerial();        // true if '!' (abort) arrived
  void pollButton();
  bool setKeyShaft(bool shaft);
  void sgStart(uint8_t ax);
  void sgPoll(uint8_t ax, uint32_t stepIndex, bool cruise, bool trace, core::SgSink* sink);
  void sgFinish();

  core::Settings& s_;
  TMC2209Stepper drv_[core::AX_COUNT];
  bool keyEnabled_ = false;
  // serial line buffer
  char line_[64];
  uint8_t lineLen_ = 0;
  bool lineReady_ = false;
  // button
  bool btnStable_ = true;   // pulled up: true = released
  bool btnLast_ = true;
  uint32_t btnChangedMs_ = 0;
  bool btnPressed_ = false;
  bool abortSeen_ = false;
  // SG sampler (non-blocking reads of SG_RESULT while stepping)
  enum { SG_IDLE, SG_WAIT } sgState_ = SG_IDLE;
  core::TmcReplyParser sgParser_;
  uint32_t sgT0_ = 0, sgLast_ = 0;
  uint16_t sgMin_ = 0xFFFF;
  uint32_t sgReqStep_ = 0;  // step index when the pending read was sent
  bool sgReqCruise_ = false;
};
