#include "calstore.h"

#include "journal.h"  // crc16

namespace core {

namespace {
const uint16_t kMagic = 0xCA1B;
const uint8_t kVersion = 1;
}  // namespace

// Layout: magic u16, version u8, sgthrs[4] u8, baseline[4] u16,
// offsetUs[3] i16, crc u16 (little endian).
bool CalStore::load(CalRecord& out) {
  uint8_t b[kSize];
  for (uint16_t i = 0; i < kSize; ++i) b[i] = hal_.storeRead(kBase + i);
  if ((uint16_t)(b[0] | (b[1] << 8)) != kMagic || b[2] != kVersion) return false;
  if (crc16(b, kSize - 2) != (uint16_t)(b[kSize - 2] | (b[kSize - 1] << 8))) return false;
  uint8_t k = 3;
  for (uint8_t a = 0; a < AX_COUNT; ++a) out.sgthrs[a] = b[k++];
  for (uint8_t a = 0; a < AX_COUNT; ++a, k += 2) out.baseline[a] = (uint16_t)(b[k] | (b[k + 1] << 8));
  for (uint8_t d = 0; d < 3; ++d, k += 2) out.offsetUs[d] = (int16_t)(b[k] | (b[k + 1] << 8));
  return true;
}

void CalStore::save(const CalRecord& r) {
  uint8_t b[kSize];
  b[0] = kMagic & 0xFF;
  b[1] = kMagic >> 8;
  b[2] = kVersion;
  uint8_t k = 3;
  for (uint8_t a = 0; a < AX_COUNT; ++a) b[k++] = r.sgthrs[a];
  for (uint8_t a = 0; a < AX_COUNT; ++a) { b[k++] = r.baseline[a] & 0xFF; b[k++] = r.baseline[a] >> 8; }
  for (uint8_t d = 0; d < 3; ++d) { b[k++] = (uint16_t)r.offsetUs[d] & 0xFF; b[k++] = (uint16_t)r.offsetUs[d] >> 8; }
  const uint16_t c = crc16(b, kSize - 2);
  b[k++] = c & 0xFF;
  b[k] = c >> 8;
  for (uint16_t i = 0; i < kSize; ++i) hal_.storeWrite(kBase + i, b[i]);
}

}  // namespace core
