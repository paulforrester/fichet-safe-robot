// Search order over the 3 dials. Plain C++.
//
// Serpentine ("boustrophedon") order: consecutive indices differ in exactly
// one dial, by exactly one position. So every attempt moves one dial by one
// detent, and no dial ever wraps from the last position back to the first
// (which a wheel with a hard stop couldn't do anyway).
#pragma once
#include <stdint.h>

namespace core {

struct Combo {
  uint8_t d[3];  // 0-based positions counted from the home stop
};

inline bool operator==(const Combo& a, const Combo& b) {
  return a.d[0] == b.d[0] && a.d[1] == b.d[1] && a.d[2] == b.d[2];
}

uint16_t comboCount(uint8_t n);                 // n^3
Combo comboAt(uint16_t index, uint8_t n);       // index in [0, n^3)
uint16_t comboIndex(const Combo& c, uint8_t n); // inverse of comboAt

}  // namespace core
