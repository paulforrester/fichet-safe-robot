# Host-side tests for the firmware core (no Arduino, no hardware).
#   make -C control/firmware/test        build and run
CXX      ?= g++
CXXFLAGS ?= -std=c++11 -O2 -Wall -Wextra -Werror -g
CORE     := ../safe_robot/src/core
SRCS     := $(wildcard $(CORE)/*.cpp) test_units.cpp test_robot.cpp main.cpp
HDRS     := $(wildcard $(CORE)/*.h) ../safe_robot/config.h minitest.h sim_hal.h

all: run

tests: $(SRCS) $(HDRS)
	$(CXX) $(CXXFLAGS) -o $@ $(SRCS)

run: tests
	./tests

# A simulated full run's log, for checking tools/logger.py end to end.
simlog: $(wildcard $(CORE)/*.cpp) sim_run.cpp $(HDRS)
	$(CXX) $(CXXFLAGS) -o sim_run $(wildcard $(CORE)/*.cpp) sim_run.cpp
	./sim_run > /tmp/simrun_raw.log

clean:
	rm -f tests tests_asan sim_run

.PHONY: all run clean simlog
