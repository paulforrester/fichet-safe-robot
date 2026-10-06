// Attempt classification from the key angle reached. Plain C++.
//
// All angles are key microsteps from the key's home (rest) position.
// N = this session's learned stop angle. The firmware logs the raw angle of
// every attempt anyway, so these classes can be redone offline
// (control/firmware/tools/logger.py).
#pragma once
#include <stdint.h>

namespace core {

enum Outcome : uint8_t {
  OUT_CLEAN = 0,    // stopped at N (within cleanTol)
  OUT_FALSESET = 1, // stopped past N + cleanTol but before N + successMin
  OUT_SUCCESS = 2,  // got to N + successMin or further
  OUT_EARLY = 3,    // stopped well short of N: something moved or jammed
};

struct ClassifyParams {
  int32_t n;           // learned stop
  int32_t cleanTol;    // |angle - N| band for a clean fail (upper side)
  int32_t earlyTol;    // angle < N - earlyTol is an anomaly
  int32_t successMin;  // angle >= N + successMin is a success
};

Outcome classify(int32_t reached, const ClassifyParams& p);
const char* outcomeName(Outcome o);  // "CLEAN", "FALSESET", "SUCCESS", "EARLY"

}  // namespace core
