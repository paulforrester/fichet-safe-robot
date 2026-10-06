#include "tmc_frame.h"

namespace core {

// Same algorithm as the datasheet's C example (§4.2): polynomial x^8+x^2+x+1,
// initial value 0, bytes fed LSB first.
uint8_t tmcCrc8(const uint8_t* data, uint8_t len) {
  uint8_t crc = 0;
  for (uint8_t i = 0; i < len; ++i) {
    uint8_t b = data[i];
    for (uint8_t j = 0; j < 8; ++j) {
      if ((crc >> 7) ^ (b & 0x01)) crc = (uint8_t)((crc << 1) ^ 0x07);
      else crc = (uint8_t)(crc << 1);
      b >>= 1;
    }
  }
  return crc;
}

void tmcReadRequest(uint8_t node, uint8_t reg, uint8_t out[4]) {
  out[0] = 0x05;
  out[1] = node;
  out[2] = reg & 0x7F;
  out[3] = tmcCrc8(out, 3);
}

bool TmcReplyParser::feed(uint8_t b) {
  // Header: sync 0x05 (low nibble 0101; upper nibble reserved), 0xFF, reg.
  if (n_ == 0) {
    if ((b & 0x0F) == 0x05) buf_[n_++] = b;
    return false;
  }
  if (n_ == 1) {
    if (b == 0xFF) { buf_[n_++] = b; }
    else { n_ = ((b & 0x0F) == 0x05) ? 1 : 0; if (n_) buf_[0] = b; }
    return false;
  }
  if (n_ == 2) {
    if (b == reg_) { buf_[n_++] = b; }
    else { n_ = ((b & 0x0F) == 0x05) ? 1 : 0; if (n_) buf_[0] = b; }
    return false;
  }
  buf_[n_++] = b;
  if (n_ < 8) return false;
  ok_ = tmcCrc8(buf_, 7) == buf_[7];
  value_ = ((uint32_t)buf_[3] << 24) | ((uint32_t)buf_[4] << 16) | ((uint32_t)buf_[5] << 8) | buf_[6];
  n_ = 0;
  return true;
}

}  // namespace core
