#include "journal.h"

namespace core {

namespace {
const uint16_t kMagic = 0x5AFE;
const uint8_t kVersion = 1;
// Slot layout (little endian): magic u16, version u8, seq u32, state u8,
// next u16, verified u16, success u16, clean u16, attempts u32, cfgHash u32,
// crc u16 = 2+1+4+1+2+2+2+2+4+4+2 = 26 bytes.
void put16(uint8_t* b, uint16_t v) { b[0] = v; b[1] = v >> 8; }
void put32(uint8_t* b, uint32_t v) { put16(b, v); put16(b + 2, v >> 16); }
uint16_t get16(const uint8_t* b) { return b[0] | ((uint16_t)b[1] << 8); }
uint32_t get32(const uint8_t* b) { return get16(b) | ((uint32_t)get16(b + 2) << 16); }
}  // namespace

uint16_t crc16(const uint8_t* data, uint16_t len) {
  uint16_t crc = 0xFFFF;
  for (uint16_t i = 0; i < len; ++i) {
    crc ^= (uint16_t)data[i] << 8;
    for (uint8_t b = 0; b < 8; ++b) crc = (crc & 0x8000) ? (crc << 1) ^ 0x1021 : crc << 1;
  }
  return crc;
}

bool Journal::readSlot(uint8_t slot, Progress& p, uint32_t& seq) {
  uint8_t b[kSlotSize];
  const uint16_t a = base_ + (uint16_t)slot * kSlotSize;
  for (uint16_t i = 0; i < kSlotSize; ++i) b[i] = hal_.storeRead(a + i);
  if (get16(b) != kMagic || b[2] != kVersion) return false;
  if (crc16(b, kSlotSize - 2) != get16(b + kSlotSize - 2)) return false;
  seq = get32(b + 3);
  p.state = b[7];
  p.nextIndex = get16(b + 8);
  p.verifiedIndex = get16(b + 10);
  p.successIndex = get16(b + 12);
  p.cleanIndex = get16(b + 14);
  p.attempts = get32(b + 16);
  p.cfgHash = get32(b + 20);
  return true;
}

bool Journal::load(Progress& out) {
  bool found = false;
  for (uint8_t s = 0; s < slots_; ++s) {
    Progress p;
    uint32_t seq;
    if (readSlot(s, p, seq) && (!found || seq > lastSeq_)) {
      found = true;
      lastSeq_ = seq;
      lastSlot_ = s;
      out = p;
    }
  }
  if (!found) {
    lastSlot_ = 0xFF;
    lastSeq_ = 0;
  }
  return found;
}

void Journal::save(const Progress& p) {
  uint8_t b[kSlotSize];
  const uint32_t seq = lastSeq_ + 1;
  put16(b, kMagic);
  b[2] = kVersion;
  put32(b + 3, seq);
  b[7] = p.state;
  put16(b + 8, p.nextIndex);
  put16(b + 10, p.verifiedIndex);
  put16(b + 12, p.successIndex);
  put16(b + 14, p.cleanIndex);
  put32(b + 16, p.attempts);
  put32(b + 20, p.cfgHash);
  put16(b + 24, crc16(b, kSlotSize - 2));
  const uint8_t slot = (lastSlot_ == 0xFF) ? 0 : (uint8_t)((lastSlot_ + 1) % slots_);
  const uint16_t a = base_ + (uint16_t)slot * kSlotSize;
  for (uint16_t i = 0; i < kSlotSize; ++i) hal_.storeWrite(a + i, b[i]);
  lastSlot_ = slot;
  lastSeq_ = seq;
}

void Journal::clear() {
  for (uint16_t i = 0; i < (uint16_t)slots_ * kSlotSize; ++i) hal_.storeWrite(base_ + i, 0xFF);
  lastSlot_ = 0xFF;
  lastSeq_ = 0;
}

}  // namespace core
