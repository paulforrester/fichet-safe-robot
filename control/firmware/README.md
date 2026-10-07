# Firmware — Fichet safe robot (Mega 2560 + RAMPS 1.4 + 4 × TMC2209)

Implements the sequence in `control/sequence.md` on the pin map in
`control/wiring.md`. Bring it up on the bench with `control/bringup.md`.

## What it does

1. **Session start** (on `start`, `resume`, or the button; ~40 s), in order:
   - ping all four drivers over UART (version 0x21, right address) and
     configure them;
   - home the key against its rest stop (searching up to 180°: the key stays
     wherever it was left);
   - **calibrate the key** (see Calibration below);
   - seat the dials: slow, bounded 1/8 turn clockwise. The dials turn
     clockwise without limit, so this never meets a stop;
   - **calibrate each dial** with one free clockwise turn;
   - home each dial anticlockwise on its stop, in two passes that must agree,
     and park it on its first click;
   - learn the key's stop angle **N** (3 tries, median, spread checked).
2. **Attempt loop** over the 8,000 combinations in serpentine order: each
   attempt moves **one dial by one position**, never wraps a dial, turns the
   key to N + 15°, and logs the **actual angle reached**. It classifies the
   attempt (clean / false set / success / early), retracts the key to its
   rest stop, and saves progress to EEPROM.
3. **Every 200 attempts, a re-check**: re-home every dial (the home must be
   where the step count says it is) and re-learn N at the last clean fail.
   If anything moved, it stops, **rewinds to the last good re-check**, and
   asks for a re-seat.
4. **Success** (key gets ≥ N + 10°): stops, holds the key where it got to, and
   prints the combination as positions 1–20: clicks counted clockwise from
   each dial's stop (there are no marks on the door). The success is saved in
   EEPROM. The key stays turned after `release` (it doesn't spring back), so
   take the key turner off and pull the key to open the door, as the manual
   says.
5. **Resumable**: progress is in EEPROM. After a power cut or a re-seat,
   `resume` (or the button) redoes the session start and continues from the
   last re-checked index (≤ 200 attempts redone). A pause runs a re-check
   first, so a resume after a pause loses nothing.

## Calibration (Paul's suggestion, 2026-10-06)

The robot measures its own StallGuard thresholds and finds the clicks,
instead of relying on hand-tuned numbers. The datasheet recommends this kind
of in-application threshold rather than a fixed one (§11.4, p. 59).

- **Each dial**: one free turn clockwise (1¼ turns with the ramps). The
  dials turn clockwise without limit, so nothing is pressed. Every
  cruise-speed SG_RESULT reading is binned by its place within a click (20
  full steps = 18°).
  - **Threshold**: the lowest bin mean is the dial's heaviest free-running
    load. SGTHRS is set so a stall reads at **50 %** of it
    (`CFG_SG_CAL_PCT`; stall = SG_RESULT ≤ 2·SGTHRS, datasheet §5.3).
  - **Clicks**: their ripple has an 18° period, and its fundamental gives
    where the clicks are. Model: turning clockwise, the click spring helps
    just before a notch (SG highest) and resists just after (SG lowest), so
    the notch is a quarter click after the SG peak. After homing, position 1
    is the first click at least 3 full steps clockwise of the stop. Later
    sessions keep the same numbering, using the offset stored in EEPROM.
  - If the ripple is too weak to trust (amplitude < 3, or < 2× the
    residual), it falls back to `CFG_HOME_OFFSET_x` and says so.
- **Key**: from rest, 60° clockwise (its stop is at ~100°); median SG →
  threshold. It then goes back to rest by stalling on the rest stop **with
  the new threshold**, which proves the threshold works.
- The last calibration is kept in EEPROM. The next session needs it for its
  very first move (homing the key) before it re-calibrates.
- `calibrate` does all of this as a separate step and prints `CAL` /
  `OFFSET` lines. Run it once, with the key turned back to its start by hand.
  `set autocal 0` / `set detentcal 0` switch either part off (then `sgX` /
  `offX` are used as set).
- **ASSUMPTIONS to check on the bench** (`control/bringup.md` stages 3–4):
  - that 50 % sits safely between free running and a stall;
  - that the click ripple is visible in SG_RESULT at all.

StealthChop tunes itself during the first moves after power-up (datasheet
§6, AT#1/AT#2, p. 38: up to ~400 full steps at 60–300 RPM). The calibration
turn — 500 full steps at 1 rev/s motor — gives it that before anything
depends on StallGuard.

Every move has a step bound and a timeout. Stalls are caught on the DIAG
interrupt. `!` on the serial line aborts the current move and switches all
drivers off. Dials never move while the key is out of rest. A run refuses to
start until the key has a threshold (from `calibrate`, or `CFG_SGTHRS_KEY`).
No move starts on a driver that has reset (next section).

## Driver resets (GSTAT check, v0.3, 2026-10-07)

**The problem.** A TMC2209's logic runs from VS (12 V) through its own
regulator, not from VIO (datasheet §2.2, p. 10; `control/wiring.md` §3.5). If
VS or VIO dips, the chip resets to its power-on registers (§17, p. 74). Here
that could be a loose contact in the hub's interim fuse holder
(`control/wiring.md`, log 2026-10-07), a PTC trip, or a cable glitch. After a
reset (datasheet pp. 9, 22–23, 28–29, 32):
- `SGTHRS` and `TCOOLTHRS` are 0: no StallGuard, no DIAG pulse;
- the current comes from the VREF pot (`I_scale_analog` = 1), with `IRUN` = 31;
- the microsteps come from MS1/MS2: 1/8, 1/32, 1/64 and 1/16 for A, B, C and the key;
- `CHOPCONF` = 0x10000053, so the power stage is on (TOFF = 3);
- the motor pulls to the driver's power-on electrical position, up to
  ±2 full steps away (§3.6.1, p. 15).

Only `GSTAT.reset` (bit 0) shows that it happened. v0.2 set the drivers up
only during the session start (and at each bench command), and read GSTAT
only in `ping`.

**The worst case in v0.2** (traced from the datasheet defaults and the
TMCStepper 0.7.3 source; not tried on hardware): the key driver resets
between two key moves.
- Before each key move, `setKeyShaft()` calls `shaft()`, and TMCStepper
  writes the whole GCONF from its own copy. That sets `I_scale_analog` back
  to 0, so the current no longer comes from the pot: `IRUN` = 31 is ~1.8 A RMS
  with the 0.11 Ω sense resistors. It also selects the MRES register, still at
  its reset value of 1/256 step.
- So the key turns under 10° instead of N + 15°, open loop, and never stalls.
- `reached` is then the commanded angle, and `classify()` returns SUCCESS.
  The run stops on a false success, holding the key.

The simulator reproduces the false success
(`control_unseen_key_reset_gives_a_false_success`). A dial driver that
resets moves its dial by the wrong amount until the next re-check fails on
homing. That costs time, but `resume` rewinds, so it doesn't give a wrong
result.

**What v0.3 does** (all in `src/core/robot.cpp`, through `Hal::gstat()`):
- **Before and after every move**, it reads the moving driver's GSTAT
  (`doMove`). Nothing moves on a driver that has reset. A reset during a move
  is seen before the move's result is used: a key try is classified only
  after its "after" check.
- **At the start of every attempt** (and of a bench `try`), it reads all
  fitted drivers. That covers the dials that don't move in that attempt.
- **Before re-writing a driver's settings** while the robot still relies on
  them, it reads that driver first, because `configure()` clears GSTAT. In
  the session start, `calKey`, the seat and the dial calibration each set the
  drivers up again.
  - The first setup after power-up or a release (pause, error, `release`)
    clears the power-on flag, which is expected (`control/bringup.md`
    stage 1). So a 12 V cycle while paused is not an error.
  - On the bench, a command after switching 12 V off and on without
    `release` stops once with `DRVFAULT`, which is true: the positions are
    gone.
- **On a flag** (1 reset, 2 drv_err, 4 uv_cp) or **no answer** (80), it
  logs `GSTAT,ms,axis,gstat,when` and stops with `ERR,…,DRVFAULT`. In a
  run, it first rewinds to the last re-check, as a failed re-check does.

**Why stop, instead of re-running `configure()` and re-homing.**
- It's how every other hardware fault is handled (DRIVER, CONFIG, DIR, DIAG,
  JAM, TIMEOUT): drivers off, an ERR line, Paul fixes the cause, `resume`.
  Only EARLY retries, and it stops after three.
- A reset means a supply dropped out: a contact or cable fault, which will
  probably come back, perhaps worse. Carrying on would hide it.
- After a reset the positions are lost, not just the settings. Steps sent
  while the driver was down did nothing, and the motor may have jumped 2 full
  steps. Recovering needs the key and every dial re-homed and N re-learned.
  That is exactly the session start `resume` runs. Doing it automatically
  would duplicate that path inside the attempt loop, for a rare fault.
- The rewind costs at most 200 attempts (~3 min). It happens at the stop, so
  it doesn't depend on `CFG_RESUME_FROM_CHECKPOINT`. The attempt in progress,
  or the one before it (an idle dial is only checked at the next attempt),
  may have run with a driver that had reset.

**Cost**:
- 10 GSTAT reads per attempt: 4, then 2 for each of the 3 moves. A
  TMCStepper read waits 2 ms twice, so that is about 45 ms per attempt, ~5 %,
  or ~6 min over all 8,000.
- +0.9 KB of flash.

**Limits**:
- A reset *during* a move shows only at the move's end. Until then the move
  runs open loop, at the VREF-pot current and other microsteps. The longest
  such moves are the dials' homing passes: up to 1.15 dial turns towards the
  stop. So every driver's pot now goes to minimum (`docs/manual.md` 2.3;
  before, only the key's did). Then a driver that resets has next to no
  torque until the check.
- `uv_cp` isn't latched (datasheet p. 24). A short dip that switches the power
  stage off without resetting the chip shows only if a read happens during
  it. The step it may cost is what the re-checks are for.
- The datasheet routes the power-on reset to DIAG too (Fig. 15.1). That isn't
  relied on.

**Bench check**: `control/bringup.md` stage 6, step 6 (12 V off and on, then
a move must stop with `DRVFAULT`).

## Files

| Path | What |
|---|---|
| `safe_robot/safe_robot.ino` | setup/loop: serial lines, button, LED |
| `safe_robot/config.h` | **every unmeasured value, in one block** (directions, currents, speeds, StallGuard thresholds, home offsets, key home mode, classification bands, re-check interval) |
| `safe_robot/pins.h` | pin map (= `control/wiring.md` §1) |
| `safe_robot/hw_mega.{h,cpp}` | thin hardware layer: TMCStepper setup, step pulses, DIAG interrupt latches, non-blocking SG_RESULT reads, EEPROM, USB serial |
| `safe_robot/src/core/` | **plain C++, no Arduino**: sequencer (`robot`), calibration (`calib`, `calstore`), serpentine order (`combo`), step ramp, classification, EEPROM journal, TMC UART frames, log-line builder |
| `test/` | host tests (`make -C control/firmware/test`): unit tests + whole runs against a simulated lock (`sim_hal.h`) |
| `tools/logger.py` | serial → raw log + attempts CSV; `--analyse` re-classifies offline |
| `Makefile.mega` | command-line AVR build (how the cloud session checks it compiles) |

## Build and flash (Paul, Arduino IDE)

1. Arduino IDE → Tools → Manage Libraries → install **TMCStepper** by
   teemuatlut (**0.7.3**). SPI, SoftwareSerial and EEPROM come with the IDE.
2. Open `control/firmware/safe_robot/safe_robot.ino`.
3. Tools → Board: **Arduino Mega or Mega 2560**; Processor: **ATmega2560**;
   Port: the Mega's USB port. Upload.
4. Close the IDE's Serial Monitor before using `tools/logger.py` (only one
   program can have the port). Or use the Serial Monitor at **115200**, line
   ending **Newline**.

## Library choice: TMCStepper 0.7.3

- It drives the TMC2209 over a shared hardware UART with per-driver addresses
  (`TMC2209Stepper(Stream*, R_SENSE, address)`). That's exactly our bus.
- Its read handles the single-wire echo: it skips bytes until the reply header
  `0x05 0xFF <register>` (replies go to master address 0xFF, datasheet p. 19).
  It also checks the CRC and retries (`TMC2208Stepper::_sendDatagram()` /
  `read()`).
- It exposes everything we need: `rms_current()` (datasheet current formula
  with the 0.11 Ω sense resistors), `SGTHRS`, `SG_RESULT`, `TCOOLTHRS`,
  `shaft`, `toff`, `GSTAT`, `IOIN`, `senddelay`.
- Marlin 2.0.x — which runs TMC2209 over UART on RAMPS/Mega boards —
  depends on exactly this version (`ini/features.ini`: `HAS_TRINAMIC_CONFIG =
  TMCStepper@~0.7.3`, branch head 743d310). Marlin 2.1.x now builds against its own fork,
  MarlinFirmware/TMCStepper 0.8.9 (`ini/features.ini`). The fork's changes
  since 0.7.3 are about other chips/platforms, plus a longer TMC2208 read
  timeout. Our 115200-baud reads finish well inside 0.7.3's.
- 0.7.3 is what the Arduino Library Manager installs.
- Alternative considered: janelia-arduino/TMC2209 (TMC2209-only, maintained).
  It would also work; TMCStepper won on its RAMPS/Marlin track record.
- Not used for motion: the firmware makes its own step pulses (a plain
  trapezoid in `core/ramp`). That keeps every move bounded, lets it stop on
  the first DIAG pulse, and lets it read SG_RESULT between steps without
  blocking. AccelStepper would hide those.

## Serial commands (115200 baud, newline)

| Command | What |
|---|---|
| `help`, `status`, `cfg` | list commands; state + progress; current settings |
| `ping` | query all 4 drivers: `DRV,axis,present,version,ms1,ms2,diagPin,diagIoin,gstat,ifcnt` |
| `start` | new run from combination 0 (refuses if a run is stored or StallGuard isn't tuned) |
| `resume [force]` | continue a stored run (`force` if position settings changed) |
| `pause` (or the button) | finish the current attempt, re-check, switch drivers off |
| `!` | abort the current move at once, drivers off |
| `release` | all drivers off (also lets go of the key after a success) |
| `reset yes` | erase stored progress |
| `calibrate` | key (from its start position) + seat + one free turn per dial + homing; prints `CAL`/`OFFSET`, saves to EEPROM |
| `seat`, `home [A\|B\|C]`, `learn` | bench: run one part of the session start |
| `goto a b c` | bench: dials to positions (1–20) after `home` |
| `try` | bench: one key attempt at the current dial setting |
| `key <deg>` | bench: turn the key clockwise up to `deg` (stops on stall), then back |
| `jog <A\|B\|C\|K> <fullsteps>` | bench: bounded move (±800 full steps), stops on stall |
| `sg <A\|B\|C\|K> <fullsteps>` | bench: like jog, printing `SG,axis,fullstep,value` samples |
| `set <name> <value>` | bench, RAM only: `sgA..sgK`, `maA..maK`, `rps100A..K` (speed × 100), `invA..K`, `offA..C`, `keyhome`, `margin`, `success`, `clean`, `early` (0.1°), `recheck`, `seatma`, `seatrps100`, `sgmin100`, `autocal`, `detentcal`, `calpct` |

The button: pauses a running session; when idle, resumes a stored run or
starts a new one.

## Log lines (what `tools/logger.py` reads)

```
ATT,ms,index,a,b,c,keySteps,keyDeg,stalled,sgMin,class,nDeg     one per attempt
SUCCESS,ms,index,a,b,c,keyDeg,doorA,doorB,doorC
HOME,ms,dial,pass,distFull,stalled,sgMin     LEARN,ms,try,keySteps,keyDeg,stalled,sgMin
NSTOP,ms,keySteps,keyDeg,spreadDeg           RECHECK,ms,index,dial,discrepancyFull,nDeg,ok
CAL,ms,axis,baseline,sgthrs,amp,resid,clicksTrusted    OFFSET,ms,dial,offsetFull,fromClicks
GSTAT,ms,axis,gstat,when     a driver reset or fault, just before ERR DRVFAULT (see "Driver resets")
EV,ms,name,detail    ERR,ms,code,text    DRV,...    CFG,...    SG,...    # human text
```

`GSTAT`: `gstat` is hex: 1 = the driver reset, 2 = drv_err (overtemperature
or short), 4 = uv_cp (12 V too low), 80 = no answer; flags add up. `when` is
`before` or `after` (a move of that driver), `attempt` (the check of all
drivers before each attempt), or `config` (before its settings are written
again).

`a,b,c` are positions 1–20 counted from each dial's home stop. `keyDeg` is
measured from the key's rest stop. `class` is CLEAN / FALSESET / SUCCESS / EARLY. The raw angle is always logged, so classes can be redone afterwards:

```
python3 control/firmware/tools/logger.py --port /dev/tty.usbmodemXXXX    # live; type commands here
python3 control/firmware/tools/logger.py --analyse runs/<stamp>_attempts.csv
```

## Verified here (cloud session, no hardware)

- **Host tests**: `make -C control/firmware/test` — 53 tests, ~36,500 checks,
  0 failures. Built with `-Wall -Wextra -Werror` (g++ 13 and clang 18) and
  also run under AddressSanitizer + UBSan. They cover:
  - the serpentine order: a bijection, and each step moves one dial by one
    position;
  - the ramp, classification, the EEPROM journal (rotation, torn write), TMC
    CRC (cross-checked against TMCStepper's own) and the reply parser (echo,
    noise, bad CRC);
  - whole runs against the simulated lock: finds the combination; false sets
    logged and skipped; power loss + re-seat → resume; a dial slip caught by
    the re-check and rewound; pause/resume; untuned / missing driver / no hard
    stop / no key rest stop / DIAG stuck high / abort / repeated early stops;
    the combination at index 0; settings changed between sessions; a too-dull
    StallGuard fails safe; N is never learned on a false set; dials that turn
    clockwise without limit and stop anticlockwise (as Paul found), with the
    seat never pressing a stop; a power cut leaving the key at its ~100° stop;
  - driver resets (v0.3): a key reset during a key try stops the run with
    `DRVFAULT`, rewound, and no false success, and `resume` then finds the
    real combination. A control, with the reset hidden as in v0.2, shows the
    false success. Also covered: a key reset during a dial move stops it
    before the key turns; an idle dial's reset is caught before the next
    attempt moves anything; a reset before a settings rewrite is reported, not
    wiped; a driver that stops answering mid-run stops it; a bench command
    after an unreleased 12 V cycle reports it once; a 12 V cycle while paused
    is not an error; one attempt costs 10 GSTAT reads;
  - calibration: thresholds from the measured load; the click centre
    recovered from a noisy ripple at any phase and any start position;
    clicks placed anywhere relative to the stop (with a control showing the
    fixed config offset would miss them); no visible ripple → config
    fallback; readings too low → error; `calibrate` → stored → used after a
    power cycle; numbering kept stable across sessions;
  - the simulator also polices the firmware: no dial moves with the key out,
    every move bounded and with a timeout, never a move on a disabled driver,
    never a move on a driver that has reset, never pressing into a stop with
    stall detection off, current never above 1.2 A.
- **Logger**: `python3 -m pytest control/firmware/tools` (3 tests). A
  simulated full run (`make -C control/firmware/test simlog`, 1,787 attempts)
  replays through `logger.py`, and its offline classes match the firmware's on
  every attempt.
- **AVR build**: compiles for the ATmega2560 with avr-gcc 7.3 + Arduino AVR
  core 1.8.6 + TMCStepper 0.7.3 (Ubuntu packages; the Arduino download
  servers are blocked here): 52.4 KB flash (20.0 %), 1.4 KB static RAM
  (16.6 %), no warnings from this code.

**Not verified**: anything on hardware. The simulator's lock is my model of
the description in `control/sequence.md` and Paul's checks, not the real lock;
in particular its StallGuard click ripple is an assumption. Motor
directions, how SG_RESULT really looks on these dials, the 50 % threshold
rule and speeds are unknown until `control/bringup.md` is done.
