// Unit tests for the plain-C++ core pieces.
#include <cmath>
#include <cstring>
#include <set>

#include "../safe_robot/src/core/calib.h"
#include "../safe_robot/src/core/calstore.h"
#include "../safe_robot/src/core/classify.h"
#include "../safe_robot/src/core/combo.h"
#include "../safe_robot/src/core/journal.h"
#include "../safe_robot/src/core/line.h"
#include "../safe_robot/src/core/ramp.h"
#include "../safe_robot/src/core/settings_from_config.h"
#include "../safe_robot/src/core/tmc_frame.h"
#include "minitest.h"
#include "sim_hal.h"

using namespace core;

// ---------------------------------------------------------------- combo
TEST(combo_is_a_bijection_over_8000) {
  std::set<int> seen;
  for (uint16_t k = 0; k < 8000; ++k) {
    const Combo c = comboAt(k, 20);
    CHECK(c.d[0] < 20 && c.d[1] < 20 && c.d[2] < 20);
    seen.insert(c.d[0] * 400 + c.d[1] * 20 + c.d[2]);
    CHECK_EQ(comboIndex(c, 20), k);
  }
  CHECK_EQ((int)seen.size(), 8000);
  CHECK_EQ(comboCount(20), 8000);
}

TEST(combo_consecutive_differ_by_one_dial_one_position) {
  for (uint16_t k = 1; k < 8000; ++k) {
    const Combo a = comboAt(k - 1, 20), b = comboAt(k, 20);
    int changed = 0, step = 0;
    for (int d = 0; d < 3; ++d)
      if (a.d[d] != b.d[d]) { ++changed; step = std::abs(a.d[d] - b.d[d]); }
    CHECK_EQ(changed, 1);
    CHECK_EQ(step, 1);
  }
  const Combo first = comboAt(0, 20);
  CHECK(first.d[0] == 0 && first.d[1] == 0 && first.d[2] == 0);
}

TEST(combo_small_n) {
  for (uint8_t n = 2; n <= 5; ++n)
    for (uint16_t k = 0; k < comboCount(n); ++k) CHECK_EQ(comboIndex(comboAt(k, n), n), k);
}

// ---------------------------------------------------------------- ramp
TEST(ramp_trapezoid_timing) {
  Ramp r;
  r.begin(6400, 480, 3200, 16000);
  double t = 0, vmax = 0;
  std::vector<double> v;
  for (int i = 0; i < 6400; ++i) { const uint32_t us = r.nextIntervalUs(); t += us; v.push_back(1e6 / us); }
  for (double x : v) vmax = std::max(vmax, x);
  CHECK(vmax <= 3201 && vmax > 3150);
  // Analytic: accel distance (3200^2-480^2)/(2*16000) = 312.8 steps each end.
  CHECK_EQ(r.accelSteps(), 312u);
  const double ta = (3200.0 - 480.0) / 16000.0;          // accel time
  const double tc = (6400 - 2 * 312.8) / 3200.0;         // cruise
  CHECK(std::fabs(t / 1e6 - (2 * ta + tc)) < 0.01);
  for (int i = 1; i < 312; ++i) CHECK(v[i] >= v[i - 1] - 0.5);           // speeding up
  for (int i = 0; i < 300; ++i) CHECK(std::fabs(v[i] - v[6399 - i]) < 1.0);  // symmetric
}

TEST(ramp_triangular_and_tiny) {
  Ramp r;
  r.begin(100, 480, 3200, 16000);
  CHECK_EQ(r.accelSteps(), 50u);
  uint32_t first = r.nextIntervalUs();
  CHECK(first >= 2080 && first <= 2084);  // 1e6/480
  r.begin(1, 480, 3200, 16000);
  CHECK(r.nextIntervalUs() > 0);
  r.begin(0, 480, 3200, 16000);
  CHECK(r.nextIntervalUs() > 0);  // no division by zero, no hang
}

// ---------------------------------------------------------------- classify
TEST(classify_bands) {
  ClassifyParams p = {1000, 35, 71, 89};
  CHECK_EQ(classify(1000, p), OUT_CLEAN);
  CHECK_EQ(classify(1035, p), OUT_CLEAN);
  CHECK_EQ(classify(1036, p), OUT_FALSESET);
  CHECK_EQ(classify(1088, p), OUT_FALSESET);
  CHECK_EQ(classify(1089, p), OUT_SUCCESS);
  CHECK_EQ(classify(929, p), OUT_CLEAN);
  CHECK_EQ(classify(928, p), OUT_EARLY);
  CHECK(std::strcmp(outcomeName(OUT_FALSESET), "FALSESET") == 0);
}

// ---------------------------------------------------------------- journal
TEST(journal_roundtrip_and_rotation) {
  SimHal h;
  Journal j(h, 0, 16);
  Progress p;
  CHECK(!j.load(p));
  for (uint16_t k = 1; k <= 40; ++k) {
    Progress q;
    q.state = RUN_ACTIVE; q.nextIndex = k; q.verifiedIndex = k / 2; q.cleanIndex = k - 1; q.attempts = 1000 + k; q.cfgHash = 0xDEADBEEF;
    j.save(q);
  }
  Journal j2(h, 0, 16);
  CHECK(j2.load(p));
  CHECK_EQ(p.nextIndex, 40);
  CHECK_EQ(p.verifiedIndex, 20);
  CHECK_EQ(p.cleanIndex, 39);
  CHECK_EQ(p.attempts, 1040u);
  CHECK_EQ(p.cfgHash, 0xDEADBEEFu);
  // 40 saves over 16 slots: every slot written, none more than 3 times.
  for (int s = 0; s < 16; ++s) CHECK(h.eeprom[s * Journal::kSlotSize] == 0xFE);  // magic low byte
  CHECK(h.eeprom[16 * Journal::kSlotSize] == 0xFF);  // nothing past the ring
}

TEST(journal_torn_write_falls_back) {
  SimHal h;
  Journal j(h, 0, 16);
  Progress p;
  j.load(p);
  for (uint16_t k = 1; k <= 5; ++k) { Progress q; q.state = RUN_ACTIVE; q.nextIndex = k; j.save(q); }
  // Save #5 went to slot 4; tear it (power cut mid-write).
  h.eeprom[4 * Journal::kSlotSize + 9] ^= 0x55;
  Journal j2(h, 0, 16);
  CHECK(j2.load(p));
  CHECK_EQ(p.nextIndex, 4);
  // The next save must not land on top of slot 3.
  Progress q; q.state = RUN_ACTIVE; q.nextIndex = 77; j2.save(q);
  Journal j3(h, 0, 16);
  CHECK(j3.load(p));
  CHECK_EQ(p.nextIndex, 77);
  j3.clear();
  Journal j4(h, 0, 16);
  CHECK(!j4.load(p));
}

TEST(crc16_known_value) {
  const uint8_t s[] = {'1', '2', '3', '4', '5', '6', '7', '8', '9'};
  CHECK_EQ(crc16(s, 9), 0x29B1);  // CRC-16/CCITT-FALSE check value
}

// ---------------------------------------------------------------- TMC frames
// Reference: TMCStepper 0.7.3 TMC2208Stepper::calcCRC (MIT), copied verbatim
// in structure, to cross-check our independent implementation.
static uint8_t tmcstepperCalcCRC(uint8_t datagram[], uint8_t len) {
  uint8_t crc = 0;
  for (uint8_t i = 0; i < len; i++) {
    uint8_t currentByte = datagram[i];
    for (uint8_t j = 0; j < 8; j++) {
      if ((crc >> 7) ^ (currentByte & 0x01)) crc = (crc << 1) ^ 0x07;
      else crc = (crc << 1);
      crc &= 0xff;
      currentByte = currentByte >> 1;
    }
  }
  return crc;
}

TEST(tmc_crc_matches_tmcstepper) {
  SimHal rng;
  for (int t = 0; t < 2000; ++t) {
    uint8_t d[7];
    for (auto& b : d) b = (uint8_t)rng.rnd();
    CHECK_EQ(tmcCrc8(d, 7), tmcstepperCalcCRC(d, 7));
  }
  uint8_t req[4];
  tmcReadRequest(3, 0x41, req);
  CHECK(req[0] == 0x05 && req[1] == 3 && req[2] == 0x41);
  CHECK_EQ(req[3], tmcstepperCalcCRC(req, 3));
}

TEST(tmc_reply_parser_skips_echo_and_noise) {
  uint8_t req[4];
  tmcReadRequest(2, 0x41, req);
  uint8_t reply[8] = {0x05, 0xFF, 0x41, 0x00, 0x00, 0x01, 0x2C, 0};
  reply[7] = tmcCrc8(reply, 7);
  TmcReplyParser p;
  p.start(0x41);
  bool done = false;
  const uint8_t noise[] = {0x00, 0x05, 0x05, 0xFF, 0x12};  // includes a false start
  for (uint8_t b : noise) done |= p.feed(b);
  for (uint8_t b : req) done |= p.feed(b);  // our own echo
  CHECK(!done);
  for (int i = 0; i < 8; ++i) done = p.feed(reply[i]);
  CHECK(done);
  CHECK(p.ok());
  CHECK_EQ(p.value(), 300u);
  // Corrupted reply -> ok() false
  reply[5] ^= 1;
  p.start(0x41);
  for (int i = 0; i < 8; ++i) done = p.feed(reply[i]);
  CHECK(done);
  CHECK(!p.ok());
}

// ---------------------------------------------------------------- line + settings
TEST(line_formatting) {
  Line l;
  l.p("A,").i(-42).sep().u(4294967295u).sep().deci(-5).sep().deci(1234).sep().x(0x21).sep().i(-2147483647 - 1);
  CHECK(std::strcmp(l.str(), "A,-42,4294967295,-0.5,123.4,21,-2147483648") == 0);
  Line big;
  for (int i = 0; i < 300; ++i) big.c('x');
  CHECK_EQ((int)std::strlen(big.str()), 120);  // truncated, not overflowed
}

TEST(settings_derived_units) {
  Settings s = makeSettings();
  CHECK_EQ(usPerMotorRev(s), 3200);
  CHECK_EQ(usPerPosition(s), 320);          // 20 full steps per position (sequence.md)
  CHECK_EQ(dialDegToUs(s, 45), 800);        // seat: 1/8 dial turn = 90 deg of motor
  CHECK_EQ(keyDeciToUs(s, 1000), 888);      // 100 deg of key
  CHECK_EQ(keyUsToDeci(s, 889), 1000);
  // TCOOLTHRS for 0.4 rev/s: 12e6 / (0.4 * 200 * 256) = 585.9
  CHECK_EQ(tcoolthrsFor(s, 0.4f), 585u);
  // Defaults must be safe: StallGuard untuned until the bench says otherwise.
  CHECK_EQ(s.ax[AX_A].sgthrs, 0);
  CHECK(s.ax[AX_A].runMa <= 1200 && s.ax[AX_KEY].runMa <= 1200);
}

// ---------------------------------------------------------------- calibration
TEST(detent_profile_recovers_the_click_centre) {
  // SG = 300 - 25*sin(2*pi*(x - x0)/320) turning clockwise: notch at x0.
  for (int x0 : {0, 37, 160, 301}) {
    for (int start : {0, 1000, -777}) {
      DetentProfile p;
      p.begin(start, 16, 400);
      SimHal rng;
      for (uint32_t i = 0; i < 8000; i += 16) {
        const double ph = 2 * M_PI * ((start + (int)i) - x0) / 320.0;
        const int sg = 300 - (int)std::lround(25 * std::sin(ph)) + (int)(rng.rnd() % 9) - 4;
        p.sample(i, (uint16_t)sg);
      }
      CHECK(p.complete());
      uint16_t amp, resid;
      int32_t notch;
      p.fit(&amp, &resid, &notch);
      CHECK(amp >= 23 && amp <= 27);
      CHECK(resid <= 3);
      int err = std::abs(notch - ((x0 % 320) + 320) % 320);
      if (err > 160) err = 320 - err;
      CHECK(err <= 12);  // under one full step (bins are a full step wide)
      CHECK(p.baseline() >= 270 && p.baseline() <= 282);
    }
  }
}

TEST(detent_profile_flat_and_incomplete) {
  DetentProfile p;
  p.begin(0, 16, 400);
  for (uint32_t i = 0; i < 6400; i += 16) p.sample(i, 250);
  uint16_t amp, resid;
  int32_t notch;
  p.fit(&amp, &resid, &notch);
  CHECK_EQ(amp, 0);
  DetentProfile q;
  q.begin(0, 16, 400);
  for (uint32_t i = 0; i < 640; i += 16) q.sample(i, 250);  // two clicks' worth
  CHECK(!q.complete());
}

TEST(median_and_threshold_and_offset_helpers) {
  MedianSink m;
  m.begin();
  for (uint16_t v : {9, 1, 7, 3, 5}) m.sample(0, v);
  CHECK_EQ(m.median(), 5);
  CHECK_EQ(sgthrsFromBaseline(275, 50), 69);   // 2*69 = 138 = half of 275, rounded
  CHECK_EQ(sgthrsFromBaseline(1, 50), 1);
  CHECK_EQ(sgthrsFromBaseline(1023, 100), 255);
  // First click 3+ full steps clockwise of the zero...
  CHECK_EQ(detentOffset(165, 0, 320, 48, -1), 165);
  CHECK_EQ(detentOffset(5, 0, 320, 48, -1), 325);
  CHECK_EQ(detentOffset(1005, 1000, 320, 48, -1), 325);
  // ...unless the last session settled on a numbering: stay with it.
  CHECK_EQ(detentOffset(50, 0, 320, 48, 330), 370);
  CHECK_EQ(detentOffset(50, 0, 320, 48, 45), 50);
}

TEST(calstore_roundtrip_and_corruption) {
  SimHal h;
  CalStore cs(h);
  CalRecord r;
  CHECK(!cs.load(r));
  CalRecord w;
  w.sgthrs[0] = 69; w.sgthrs[3] = 60; w.baseline[1] = 277; w.offsetUs[2] = 325;
  cs.save(w);
  CHECK(cs.load(r));
  CHECK_EQ(r.sgthrs[0], 69);
  CHECK_EQ(r.sgthrs[3], 60);
  CHECK_EQ(r.baseline[1], 277);
  CHECK_EQ(r.offsetUs[2], 325);
  CHECK_EQ(r.offsetUs[0], -1);
  h.eeprom[CalStore::kBase + 5] ^= 1;
  CHECK(!cs.load(r));
  CHECK(CalStore::kBase >= 16 * Journal::kSlotSize);  // doesn't overlap the journal
}
