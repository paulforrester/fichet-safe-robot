// Minimal test framework (no dependencies): TEST(name) { CHECK(...); }
#pragma once
#include <cstdio>
#include <functional>
#include <string>
#include <vector>

namespace mt {
struct Case { const char* name; std::function<void()> fn; };
inline std::vector<Case>& cases() { static std::vector<Case> v; return v; }
inline int& failures() { static int f = 0; return f; }
inline int& checks() { static int c = 0; return c; }
struct Reg { Reg(const char* n, std::function<void()> f) { cases().push_back({n, f}); } };
inline int runAll() {
  for (auto& c : cases()) {
    const int before = failures();
    c.fn();
    std::printf("%s %s\n", failures() == before ? "PASS" : "FAIL", c.name);
  }
  std::printf("%zu tests, %d checks, %d failures\n", cases().size(), checks(), failures());
  return failures() ? 1 : 0;
}
}  // namespace mt

#define TEST(name) static void name(); static mt::Reg reg_##name(#name, name); static void name()
#define CHECK(cond) do { ++mt::checks(); if (!(cond)) { ++mt::failures(); \
  std::printf("  %s:%d: CHECK(%s) failed\n", __FILE__, __LINE__, #cond); } } while (0)
#define CHECK_EQ(a, b) do { ++mt::checks(); auto va = (a); auto vb = (b); if (!(va == vb)) { ++mt::failures(); \
  std::printf("  %s:%d: CHECK_EQ(%s, %s) failed: %lld vs %lld\n", __FILE__, __LINE__, #a, #b, \
  (long long)va, (long long)vb); } } while (0)
