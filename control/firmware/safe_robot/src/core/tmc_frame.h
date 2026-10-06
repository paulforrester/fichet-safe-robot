// TMC2209 single-wire UART frames (datasheet rev 1.09 §4.1-4.2). Plain C++.
//
// Used by the hardware layer for *non-blocking* register reads while a motor
// is stepping (SG_RESULT sampling). Everything else goes through TMCStepper.
// Read request: 0x05, node address, register, CRC.
// Reply:        0x05, 0xFF (master), register, 4 data bytes (MSB first), CRC.
// On the shared single-wire bus the Mega also hears its own request (echo);
// the parser skips it because the echo's second byte is a node address
// (0..3), never 0xFF.
#pragma once
#include <stdint.h>

namespace core {

uint8_t tmcCrc8(const uint8_t* data, uint8_t len);  // CRC8-ATM, LSB first
void tmcReadRequest(uint8_t node, uint8_t reg, uint8_t out[4]);

class TmcReplyParser {
 public:
  void start(uint8_t reg) { reg_ = reg; n_ = 0; }
  // Feed one received byte. Returns true when a complete reply for reg has
  // arrived; then ok() tells whether its CRC matched and value() holds data.
  bool feed(uint8_t b);
  bool ok() const { return ok_; }
  uint32_t value() const { return value_; }

 private:
  uint8_t reg_ = 0, n_ = 0;
  uint8_t buf_[8];
  bool ok_ = false;
  uint32_t value_ = 0;
};

}  // namespace core
