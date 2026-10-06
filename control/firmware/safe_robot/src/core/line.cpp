#include "line.h"

namespace core {

Line& Line::p(const char* f) {
#ifdef __AVR__
  for (char ch; (ch = (char)pgm_read_byte(f)) != 0; ++f) c(ch);
#else
  while (*f) c(*f++);
#endif
  return *this;
}

Line& Line::s(const char* r) {
  while (r && *r) c(*r++);
  return *this;
}

Line& Line::c(char ch) {
  if (n_ < kCap) {
    buf_[n_++] = ch;
    buf_[n_] = 0;
  }
  return *this;
}

Line& Line::u(uint32_t v) {
  char tmp[11];
  uint8_t k = 0;
  do { tmp[k++] = (char)('0' + v % 10); v /= 10; } while (v);
  while (k) c(tmp[--k]);
  return *this;
}

Line& Line::i(int32_t v) {
  if (v < 0) { c('-'); return u((uint32_t)(-(v + 1)) + 1); }
  return u((uint32_t)v);
}

Line& Line::x(uint32_t v) {
  char tmp[8];
  uint8_t k = 0;
  do { uint8_t d = v & 0xF; tmp[k++] = (char)(d < 10 ? '0' + d : 'A' + d - 10); v >>= 4; } while (v);
  while (k) c(tmp[--k]);
  return *this;
}

Line& Line::deci(int32_t t) {
  if (t < 0) { c('-'); t = -t; }
  u((uint32_t)(t / 10));
  c('.');
  return c((char)('0' + t % 10));
}

}  // namespace core
