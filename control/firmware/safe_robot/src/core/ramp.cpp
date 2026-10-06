#include "ramp.h"
#include <math.h>

namespace core {

void Ramp::begin(uint32_t total, float startSps, float maxSps, float accelSps2) {
  total_ = total;
  i_ = 0;
  v0_ = startSps > 1.0f ? startSps : 1.0f;
  vmax_ = maxSps > v0_ ? maxSps : v0_;
  a_ = accelSps2 > 1.0f ? accelSps2 : 1.0f;
  const float n = (vmax_ * vmax_ - v0_ * v0_) / (2.0f * a_);
  nAcc_ = (uint32_t)n;
  if (2 * nAcc_ > total_) nAcc_ = total_ / 2;  // triangular profile
}

float Ramp::speedAt(uint32_t i) const {
  uint32_t j;  // distance (in steps) from the nearer end of the move
  if (i < nAcc_) {
    j = i;
  } else if (i + nAcc_ >= total_) {
    j = total_ - 1 - i;
  } else {
    return vmax_;
  }
  float v = sqrtf(v0_ * v0_ + 2.0f * a_ * (float)j);
  return v < vmax_ ? v : vmax_;
}

uint32_t Ramp::nextIntervalUs() {
  const float v = speedAt(i_);
  if (i_ < total_) ++i_;
  return (uint32_t)(1000000.0f / v + 0.5f);
}

}  // namespace core
