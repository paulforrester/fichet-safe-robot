// Trapezoidal (constant acceleration) step timing. Plain C++.
#pragma once
#include <stdint.h>

namespace core {

class Ramp {
 public:
  // total: number of steps; speeds in steps/s; accel in steps/s^2.
  void begin(uint32_t total, float startSps, float maxSps, float accelSps2);
  // Interval in microseconds before step i (0-based); call in order.
  uint32_t nextIntervalUs();
  uint32_t index() const { return i_; }
  uint32_t accelSteps() const { return nAcc_; }
  float speedAt(uint32_t i) const;

 private:
  uint32_t total_ = 0, nAcc_ = 0, i_ = 0;
  float v0_ = 1, vmax_ = 1, a_ = 1;
};

}  // namespace core
