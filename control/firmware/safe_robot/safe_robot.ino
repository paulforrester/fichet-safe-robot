// Fichet-Bauche "Complice" combination robot — Arduino Mega 2560 + RAMPS 1.4.
//
//   control/firmware/README.md  build, flash, commands, log format
//   control/bringup.md          bench bring-up, stage by stage
//   control/wiring.md           pin map and harness
//   config.h                    every value not yet measured, in one place
//
// Libraries: TMCStepper 0.7.3 (Arduino Library Manager, by teemuatlut);
// SoftwareSerial, SPI and EEPROM (used in hw_mega.cpp) come with the Arduino AVR core.
#include <SPI.h>
#include <SoftwareSerial.h>
#include <TMCStepper.h>

#include "config.h"
#include "hw_mega.h"
#include "pins.h"
#include "src/core/robot.h"
#include "src/core/settings_from_config.h"

#define FW_VERSION "0.2 (2026-10-06)"

core::Settings g_settings = core::makeSettings();
HwMega g_hw(g_settings);
core::Robot g_robot(g_hw, g_settings);

void setup() {
  Serial.begin(CFG_USB_BAUD);
  g_hw.begin();
  Serial.println(F("# Fichet safe robot " FW_VERSION " - type help"));
  g_robot.boot();
}

void loop() {
  char line[64];
  if (g_hw.readLine(line, sizeof(line))) g_robot.handleLine(line);
  if (g_hw.takeAbort()) g_robot.abort();
  if (g_hw.takeButtonPress()) {
    // Button: pause a run in progress; otherwise resume a stored run, or start one.
    if (g_robot.busy()) g_robot.requestPause();
    else if (g_robot.progress().state == core::RUN_ACTIVE) g_robot.handleLine("resume");
    else if (g_robot.progress().state == core::RUN_NONE) g_robot.handleLine("start");
  }
  g_robot.tick();
  g_hw.updateLed(g_robot.state());
}
