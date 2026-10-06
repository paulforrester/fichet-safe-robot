// Prints a whole simulated run's serial log in the logger's raw format
// ("<host time>\t<line>"), for checking tools/logger.py end to end:
//   make simlog && python3 ../tools/logger.py --replay /tmp/simrun_raw.log
#include <cstdio>

#include "../safe_robot/src/core/robot.h"
#include "../safe_robot/src/core/settings_from_config.h"
#include "sim_hal.h"

int main() {
  SimHal h;
  h.secret[0] = 4; h.secret[1] = 9; h.secret[2] = 13;
  h.falseSets.insert(SimHal::comboKey(1, 2, 3));
  h.falseSets.insert(SimHal::comboKey(3, 10, 0));
  core::Settings s = core::makeSettings();
  for (int a = 0; a < core::AX_COUNT; ++a) s.ax[a].sgthrs = 80;
  core::Robot r(h, s);
  r.boot();
  r.handleLine("start");
  for (int i = 0; i < 100000 && r.busy(); ++i) r.tick();
  for (auto& l : h.lines) std::printf("2026-10-06T12:00:00.000\t%s\n", l.c_str());
  return r.state() == core::ST_SUCCESS ? 0 : 1;
}
