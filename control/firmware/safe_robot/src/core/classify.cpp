#include "classify.h"

namespace core {

Outcome classify(int32_t reached, const ClassifyParams& p) {
  if (reached >= p.n + p.successMin) return OUT_SUCCESS;
  if (reached < p.n - p.earlyTol) return OUT_EARLY;
  if (reached <= p.n + p.cleanTol) return OUT_CLEAN;
  return OUT_FALSESET;
}

const char* outcomeName(Outcome o) {
  switch (o) {
    case OUT_CLEAN: return "CLEAN";
    case OUT_FALSESET: return "FALSESET";
    case OUT_SUCCESS: return "SUCCESS";
    case OUT_EARLY: return "EARLY";
  }
  return "?";
}

}  // namespace core
