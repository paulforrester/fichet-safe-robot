// Self-calibration from StallGuard readings. Plain C++.
//
// Paul (2026-10-06): the force to turn each dial should be calibrated by the
// robot itself. The datasheet supports this: rather than one fixed
// threshold, "react to a change of SG_RESULT by determining a fitting value
// for SGTHRS in the application, e.g., moving away from the home position"
// (TMC2209 datasheet §11.4, p. 59).
//
// Dials: one free clockwise turn (the dials turn clockwise without limit).
// Every cruise-speed SG_RESULT sample is binned by its position within one
// click (20 full steps = 18 deg of dial).
//  - Baseline = the lowest bin mean: the free-running load at its heaviest
//    (climbing out of a click).
//  - The clicks show up as a ripple with a 20-full-step period. Its
//    fundamental gives where the clicks are. With a symmetric notch,
//    turning clockwise, the spring helps just before the notch (SG highest)
//    and resists just after (SG lowest). So the notch centre sits a quarter
//    period after the SG peak. This is a model to be checked on the bench
//    (control/bringup.md stage 4).
// Key: the median SG over its free travel from rest.
#pragma once
#include <stdint.h>
#include "hal.h"

namespace core {

class DetentProfile : public SgSink {
 public:
  static const uint8_t kBins = 20;  // full steps per click
  // startAbs: the dial's absolute microstep count at the start of the move.
  // windowFull: use this many full steps of cruise (one dial turn = 400).
  void begin(int32_t startAbs, uint8_t microsteps, uint16_t windowFull);
  void sample(uint32_t stepIndex, uint16_t sg) override;
  bool complete() const;              // every bin has enough samples
  uint16_t baseline() const;          // lowest bin mean
  // Fitted click fundamental: amplitude, residual RMS (both SG units), and
  // the notch centre as an absolute microstep position modulo one click.
  void fit(uint16_t* amp, uint16_t* resid, int32_t* notchAbsMod) const;
  uint16_t samples() const { return total_; }

 private:
  int32_t startAbs_ = 0;
  uint8_t us_ = 16;
  uint16_t window_ = 400;
  int32_t firstFull_ = -1;
  int32_t sum_[kBins];
  uint16_t n_[kBins];
  uint16_t total_ = 0;
};

class MedianSink : public SgSink {
 public:
  void begin() { n_ = 0; }
  void sample(uint32_t, uint16_t sg) override { if (n_ < kCap) v_[n_++] = sg; }
  uint8_t count() const { return n_; }
  uint16_t median();  // sorts in place; 0 if empty

 private:
  static const uint8_t kCap = 64;
  uint16_t v_[kCap];
  uint8_t n_ = 0;
};

// SGTHRS that signals a stall when SG_RESULT falls to pct % of the baseline
// (a stall is SG_RESULT <= 2 * SGTHRS, datasheet §5.3). Clamped to 1..255.
uint8_t sgthrsFromBaseline(uint16_t baseline, uint8_t pct);

// Offset of position 1 from the dial's homing zero, in microsteps: a click
// centre. With a previous offset (prevOffset >= 0, from the last session),
// the click nearest to it, so the numbering can't shift by one between
// sessions when a click sits right at the stop. Without one, the first click
// at least minOffset clockwise of the stall point.
int32_t detentOffset(int32_t notchAbsMod, int32_t zeroAbs, int32_t clickUs, int32_t minOffset,
                     int32_t prevOffset);

}  // namespace core
