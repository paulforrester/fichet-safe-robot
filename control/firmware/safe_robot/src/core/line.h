// Fixed-buffer builder for one log line. Plain C++ (uses avr-libc's
// pgmspace on AVR so string literals stay in flash, not in the Mega's 8 KB RAM).
#pragma once
#include <stdint.h>

#ifdef __AVR__
#include <avr/pgmspace.h>
#define CP(s) PSTR(s)
#else
#define CP(s) (s)
#endif

namespace core {

class Line {
 public:
  Line() { clear(); }
  void clear() { n_ = 0; buf_[0] = 0; }
  Line& p(const char* flashStr);  // literal wrapped in CP()
  Line& s(const char* ramStr);
  Line& c(char ch);
  Line& i(int32_t v);
  Line& u(uint32_t v);
  Line& x(uint32_t v);        // hex, no prefix
  Line& deci(int32_t tenths); // 123 -> "12.3"
  Line& sep() { return c(','); }
  const char* str() const { return buf_; }

 private:
  static const uint8_t kCap = 120;
  char buf_[kCap + 1];
  uint8_t n_;
};

}  // namespace core
