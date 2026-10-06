# Firmware — Fichet safe robot (Mega 2560 + RAMPS 1.4 + 4 × TMC2209)

Implements the sequence in `control/sequence.md` on the pin map in
`control/wiring.md`. Bring it up on the bench with `control/bringup.md`.

## What it does

1. **Session start** (on `start`, `resume`, or the button): pings all four
   drivers over UART (version 0x21, right address) and configures them. Then
   it homes the key against its rest stop, seats the dials (slow, bounded
   1/8 turn clockwise — the dials turn clockwise without limit, so this never
   meets a stop), and homes each dial anticlockwise on its stop, in two
   passes that must agree. Last, it learns the key's stop angle **N** (3 tries, median, spread
   checked).
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
   prints the combination (positions 1–20 from each dial's home stop, plus door
   numbers if `config.h` has the mapping). The success is saved in EEPROM.
5. **Resumable**: progress is in EEPROM. After a power cut or a re-seat,
   `resume` (or the button) redoes the session start and continues from the
   last re-checked index (≤ 200 attempts redone). A pause runs a re-check
   first, so a resume after a pause loses nothing.

StealthChop tunes itself during the first moves after power-up (datasheet
§6, AT#1/AT#2, p. 38: up to ~400 full steps at 60–300 RPM). The key homing,
the seat, the two homing passes and the 3 learn tries give it that before
the attempts start; bench StallGuard values should be taken after a few
moves too.

Every move has a step bound and a timeout. Stalls are caught on the DIAG
interrupt. `!` on the serial line aborts the current move and switches all
drivers off. Dials never move while the key is out of rest. StallGuard
thresholds default to 0 ("not tuned"), and a run refuses to start until the
bench sets them.

## Files

| Path | What |
|---|---|
| `safe_robot/safe_robot.ino` | setup/loop: serial lines, button, LED |
| `safe_robot/config.h` | **every unmeasured value, in one block** (directions, currents, speeds, StallGuard thresholds, home offsets, key home mode, classification bands, re-check interval) |
| `safe_robot/pins.h` | pin map (= `control/wiring.md` §1) |
| `safe_robot/hw_mega.{h,cpp}` | thin hardware layer: TMCStepper setup, step pulses, DIAG interrupt latches, non-blocking SG_RESULT reads, EEPROM, USB serial |
| `safe_robot/src/core/` | **plain C++, no Arduino**: sequencer (`robot`), serpentine order (`combo`), step ramp, classification, EEPROM journal, TMC UART frames, log-line builder |
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
| `seat`, `home [A\|B\|C]`, `learn` | bench: run one part of the session start |
| `goto a b c` | bench: dials to positions (1–20) after `home` |
| `try` | bench: one key attempt at the current dial setting |
| `key <deg>` | bench: turn the key clockwise up to `deg` (stops on stall), then back |
| `jog <A\|B\|C\|K> <fullsteps>` | bench: bounded move (±800 full steps), stops on stall |
| `sg <A\|B\|C\|K> <fullsteps>` | bench: like jog, printing `SG,axis,fullstep,value` samples |
| `set <name> <value>` | bench, RAM only: `sgA..sgK`, `maA..maK`, `rps100A..K` (speed × 100), `invA..K`, `offA..C`, `keyhome`, `margin`, `success`, `clean`, `early` (0.1°), `recheck`, `seatma`, `seatrps100`, `sgmin100` |

The button: pauses a running session; when idle, resumes a stored run or
starts a new one.

## Log lines (what `tools/logger.py` reads)

```
ATT,ms,index,a,b,c,keySteps,keyDeg,stalled,sgMin,class,nDeg     one per attempt
SUCCESS,ms,index,a,b,c,keyDeg,doorA,doorB,doorC
HOME,ms,dial,pass,distFull,stalled,sgMin     LEARN,ms,try,keySteps,keyDeg,stalled,sgMin
NSTOP,ms,keySteps,keyDeg,spreadDeg           RECHECK,ms,index,dial,discrepancyFull,nDeg,ok
EV,ms,name,detail    ERR,ms,code,text    DRV,...    CFG,...    SG,...    # human text
```

`a,b,c` are positions 1–20 counted from each dial's home stop. `keyDeg` is
measured from the key's rest stop. `class` is CLEAN / FALSESET / SUCCESS /
EARLY. The raw angle is always logged, so classes can be redone afterwards:

```
python3 control/firmware/tools/logger.py --port /dev/tty.usbmodemXXXX    # live; type commands here
python3 control/firmware/tools/logger.py --analyse runs/<stamp>_attempts.csv
```

## Verified here (cloud session, no hardware)

- **Host tests**: `make -C control/firmware/test` — 35 tests, ~36,000 checks,
  0 failures. Built with `-Wall -Wextra -Werror` and also run under
  AddressSanitizer + UBSan. They cover:
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
    seat never pressing a stop;
  - the simulator also polices the firmware: no dial moves with the key out,
    every move bounded and with a timeout, never a move on a disabled driver,
    never pressing into a stop with stall detection off, current never above
    1.2 A.
- **Logger**: `python3 -m pytest control/firmware/tools` (3 tests). A
  simulated full run (`make -C control/firmware/test simlog`, 1,787 attempts)
  replays through `logger.py`, and its offline classes match the firmware's on
  every attempt.
- **AVR build**: compiles for the ATmega2560 with avr-gcc 7.3 + Arduino AVR
  core 1.8.6 + TMCStepper 0.7.3 (Ubuntu packages; the Arduino download
  servers are blocked here): 42.4 KB flash (16.2 %), 1.2 KB static RAM
  (15.0 %), no warnings from this code.

**Not verified**: anything on hardware. The simulator's lock is my model of
the description in `control/sequence.md`, not of the real lock. Directions,
the hard stops, the key's rest stop, StallGuard thresholds and speeds, and the
home offset are all unknown until `control/bringup.md` is done.
