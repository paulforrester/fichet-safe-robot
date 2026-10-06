// Last calibration, kept in EEPROM (after the progress journal), so a new
// session can home the key against its rest stop before it re-calibrates.
// Plain C++.
#pragma once
#include <stdint.h>
#include "hal.h"

namespace core {

struct CalRecord {
  uint8_t sgthrs[AX_COUNT] = {0, 0, 0, 0};    // 0 = not calibrated
  uint16_t baseline[AX_COUNT] = {0, 0, 0, 0};
  int16_t offsetUs[3] = {-1, -1, -1};         // position 1 from the stall zero; -1 = none
};

class CalStore {
 public:
  static const uint16_t kBase = 512;  // journal uses 0..415
  static const uint16_t kSize = 2 + 1 + AX_COUNT + 2 * AX_COUNT + 2 * 3 + 2;
  explicit CalStore(Hal& hal) : hal_(hal) {}
  bool load(CalRecord& out);
  void save(const CalRecord& r);

 private:
  Hal& hal_;
};

}  // namespace core
