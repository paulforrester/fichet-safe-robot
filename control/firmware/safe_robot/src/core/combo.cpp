#include "combo.h"

namespace core {

uint16_t comboCount(uint8_t n) { return (uint16_t)n * n * n; }

Combo comboAt(uint16_t index, uint8_t n) {
  const uint16_t nn = (uint16_t)n * n;
  const uint8_t d0 = index / nn;
  const uint16_t rest = index % nn;
  const uint8_t raw1 = rest / n;
  const uint8_t raw2 = rest % n;
  // Middle dial reverses on every step of the slow dial; fast dial reverses
  // on every step of the (slow, middle) pair. index / n counts those rows.
  const uint8_t d1 = (d0 % 2 == 0) ? raw1 : (uint8_t)(n - 1 - raw1);
  const uint8_t d2 = ((index / n) % 2 == 0) ? raw2 : (uint8_t)(n - 1 - raw2);
  Combo c = {{d0, d1, d2}};
  return c;
}

uint16_t comboIndex(const Combo& c, uint8_t n) {
  const uint8_t d0 = c.d[0];
  const uint8_t raw1 = (d0 % 2 == 0) ? c.d[1] : (uint8_t)(n - 1 - c.d[1]);
  const uint16_t row = (uint16_t)d0 * n + raw1;
  const uint8_t raw2 = (row % 2 == 0) ? c.d[2] : (uint8_t)(n - 1 - c.d[2]);
  return row * n + raw2;
}

}  // namespace core
