#include <cstdio>
#include "minitest.h"
int main() { std::setvbuf(stdout, nullptr, _IONBF, 0); return mt::runAll(); }
