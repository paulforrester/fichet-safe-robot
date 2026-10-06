#include "calib.h"

#include <math.h>

namespace core {

namespace {
int32_t floorMod(int32_t a, int32_t m) { int32_t r = a % m; return r < 0 ? r + m : r; }
const uint8_t kMinPerBin = 3;
const float kTwoPi = 6.2831853f;
}  // namespace

void DetentProfile::begin(int32_t startAbs, uint8_t microsteps, uint16_t windowFull) {
  startAbs_ = startAbs;
  us_ = microsteps ? microsteps : 1;
  window_ = windowFull;
  firstFull_ = -1;
  total_ = 0;
  for (uint8_t b = 0; b < kBins; ++b) { sum_[b] = 0; n_[b] = 0; }
}

void DetentProfile::sample(uint32_t stepIndex, uint16_t sg) {
  const int32_t full = (int32_t)(stepIndex / us_);
  if (firstFull_ < 0) firstFull_ = full;
  if (full - firstFull_ >= window_) return;  // exactly one turn: other ripples average out
  const int32_t abs = startAbs_ + (int32_t)stepIndex;
  const uint8_t bin = (uint8_t)(floorMod(abs, (int32_t)kBins * us_) / us_);
  sum_[bin] += sg;
  if (n_[bin] < 0xFFFF) ++n_[bin];
  ++total_;
}

bool DetentProfile::complete() const {
  for (uint8_t b = 0; b < kBins; ++b)
    if (n_[b] < kMinPerBin) return false;
  return true;
}

uint16_t DetentProfile::baseline() const {
  int32_t lo = 0x7FFFFFFF;
  for (uint8_t b = 0; b < kBins; ++b) {
    if (!n_[b]) continue;
    const int32_t m = sum_[b] / n_[b];
    if (m < lo) lo = m;
  }
  return lo == 0x7FFFFFFF ? 0 : (uint16_t)lo;
}

void DetentProfile::fit(uint16_t* amp, uint16_t* resid, int32_t* notchAbsMod) const {
  float m[kBins], mean = 0;
  for (uint8_t b = 0; b < kBins; ++b) { m[b] = n_[b] ? (float)sum_[b] / n_[b] : 0; mean += m[b]; }
  mean /= kBins;
  float c = 0, s = 0;
  for (uint8_t b = 0; b < kBins; ++b) {
    const float a = kTwoPi * (b + 0.5f) / kBins;  // bin centre, in full steps
    c += (m[b] - mean) * cosf(a);
    s += (m[b] - mean) * sinf(a);
  }
  const float A = 2.0f * sqrtf(c * c + s * s) / kBins;
  const float th = atan2f(s, c);  // SG peak at this phase
  float r2 = 0;
  for (uint8_t b = 0; b < kBins; ++b) {
    const float e = m[b] - mean - A * cosf(kTwoPi * (b + 0.5f) / kBins - th);
    r2 += e * e;
  }
  *amp = (uint16_t)(A + 0.5f);
  *resid = (uint16_t)(sqrtf(r2 / kBins) + 0.5f);
  // Peak position in microsteps, then a quarter click on to the notch centre.
  const int32_t clickUs = (int32_t)kBins * us_;
  const int32_t peakUs = (int32_t)(th / kTwoPi * clickUs + (th < 0 ? clickUs : 0) + 0.5f);
  *notchAbsMod = floorMod(peakUs + clickUs / 4, clickUs);
}

uint16_t MedianSink::median() {
  if (!n_) return 0;
  for (uint8_t i = 1; i < n_; ++i)
    for (uint8_t j = i; j > 0 && v_[j] < v_[j - 1]; --j) { uint16_t t = v_[j]; v_[j] = v_[j - 1]; v_[j - 1] = t; }
  return v_[n_ / 2];
}

uint8_t sgthrsFromBaseline(uint16_t baseline, uint8_t pct) {
  const uint32_t v = ((uint32_t)baseline * pct + 100) / 200;  // round(baseline * pct/100 / 2)
  if (v < 1) return 1;
  if (v > 255) return 255;
  return (uint8_t)v;
}

int32_t detentOffset(int32_t notchAbsMod, int32_t zeroAbs, int32_t clickUs, int32_t minOffset,
                     int32_t prevOffset) {
  int32_t off = floorMod(notchAbsMod - zeroAbs, clickUs);
  if (prevOffset >= 0) {
    int32_t best = off;
    for (int32_t c = off; c <= off + 2 * clickUs; c += clickUs) {
      const int32_t dc = c > prevOffset ? c - prevOffset : prevOffset - c;
      const int32_t db = best > prevOffset ? best - prevOffset : prevOffset - best;
      if (dc < db) best = c;
    }
    return best;
  }
  while (off < minOffset) off += clickUs;
  return off;
}

}  // namespace core
