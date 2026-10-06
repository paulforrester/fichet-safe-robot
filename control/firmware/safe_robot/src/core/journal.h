// Run progress kept in EEPROM so a run survives power loss. Plain C++.
//
// A ring of fixed-size slots; each save goes to the next slot with a higher
// sequence number and a CRC. Loading picks the valid slot with the highest
// sequence, so a save torn by a power cut just falls back to the one before.
// 16 slots spread the writes: 8,000 attempts = 500 writes per slot.
#pragma once
#include <stdint.h>
#include "hal.h"

namespace core {

enum RunState : uint8_t {
  RUN_NONE = 0,     // no run started (or cleared)
  RUN_ACTIVE = 1,   // in progress (paused, or interrupted by power loss)
  RUN_SUCCESS = 2,  // stopped on a success at successIndex
  RUN_EXHAUSTED = 3 // all combinations tried, no success
};

struct Progress {
  uint8_t state = RUN_NONE;
  uint16_t nextIndex = 0;      // next combination index to try
  uint16_t verifiedIndex = 0;  // everything before this passed a re-check
  uint16_t successIndex = 0;
  uint16_t cleanIndex = 0xFFFF; // most recent clean fail (N is re-learned there); 0xFFFF = none
  uint32_t attempts = 0;       // attempts made, all sessions (incl. repeats)
  uint32_t cfgHash = 0;        // settings that define positions
};

class Journal {
 public:
  static const uint16_t kSlotSize = 26;
  Journal(Hal& hal, uint16_t base, uint8_t slots) : hal_(hal), base_(base), slots_(slots) {}
  bool load(Progress& out);    // false = nothing valid stored
  void save(const Progress& p);
  void clear();

 private:
  bool readSlot(uint8_t slot, Progress& p, uint32_t& seq);
  Hal& hal_;
  uint16_t base_;
  uint8_t slots_;
  uint8_t lastSlot_ = 0xFF;
  uint32_t lastSeq_ = 0;
};

uint16_t crc16(const uint8_t* data, uint16_t len);  // CRC-16/CCITT-FALSE

}  // namespace core
