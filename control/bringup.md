# Bench bring-up plan

> **Revision 2026-10-17.2** · key driver on the RAMPS E0 socket; UART pigtail · log: `docs/revisions.md`

Seven short stages, in order. Each ends with **"Send back"**: the numbers or
log lines I need to fill in `control/firmware/safe_robot/config.h`.

Wiring is in `control/wiring.md`; firmware commands in
`control/firmware/README.md`.

**Safety, every stage**
- Plug and unplug things (motors including the key motor cable, and drivers)
  only with **12 V off**.
- Keep a hand near the 12 V plug: pulling it stops everything. Typing `!`
  aborts a move.
- Power order: USB first, then 12 V. Off: 12 V first.
- Start at low current, and never put fingers in the gears.

**Software on the Mac** (set up once; details in `docs/manual.md` §3–4):
- **Arduino IDE 2** (arduino.cc) builds the firmware and uploads it over USB:
  board package **Arduino AVR Boards**, library **TMCStepper 0.7.3**, board
  **Arduino Mega or Mega 2560**, port `/dev/cu.usbmodemXXXX` (manual §3.2,
  §3.3, §4.1).
- **The logger** talks to the robot: you type commands in it, and it saves
  everything to `runs/<date>_raw.log` (for any stage you can just send me
  that file). Once: `python3 -m venv ~/safe-robot-venv` and
  `~/safe-robot-venv/bin/python -m pip install pyserial` (manual §3.5). Each
  time, from the repo folder:
  `~/safe-robot-venv/bin/python control/firmware/tools/logger.py --port /dev/cu.usbmodemXXXX`
  (`ls /dev/cu.usbmodem*` finds the port; manual §5.3).
- Or the IDE's Serial Monitor at 115200, "Newline" (it doesn't save). Only one
  program can have the port open: close the logger before uploading.

---

## Stage 0 — Preparation (no power)

1. **Flash** (manual §3.1–3.3 and §4.1): get the code (`git clone` or
   GitHub's Download ZIP), install the Arduino IDE, the AVR board package and
   TMCStepper 0.7.3. Open `control/firmware/safe_robot/safe_robot.ino`,
   board "Arduino Mega or Mega 2560", **Verify**, then **Upload** with only
   USB connected (RAMPS may be on or off the Mega).
2. Start the logger and type `status`. You should see
   `# Fichet safe robot 0.5 (2026-10-16, rev 2026-10-13.1) - type help` and `# state=IDLE run=0 next=0 ...`.
3. **RAMPS jumpers** (under the sockets): X none; Y **MS1** only; Z **MS2**
   only; **E0 MS1 + MS2** (the key, address 3); E1 none; **no MS3 jumper
   anywhere**. (Correction, 2026-10-09: E0 was missing from this step.)
4. **EN-end pins** on all **four** drivers (the three dials and the key;
   leave the spare untouched): before fitting the heatsinks, cut the
   **bottom** ends of the two EN-end pins flush underneath; leave the tops.
   No soldering (revision 2026-10-08.2; `control/wiring.md` §3.3).
5. **VREF pots**: set later, by measurement, in stage 1 (step 3a). (BTT's
   manual doesn't say which way is minimum, and the pot only has a voltage
   with 12 V on.)
6. Fit heatsinks. **Driver orientation**: do the multimeter check in manual
   §2.4 step 2: match the driver's EN and GND pins to the small EN and GND
   labels in the RAMPS silkscreen. The driver's VS/GND/motor side goes in the
   socket row nearer that axis's motor header.

**Send back**: the two lines from step 2; the orientation check results for
X (manual §2.4 step 2); any surprises in steps 3–6.

---

## Stage 1 — One driver talking over UART (no motor)

Setup: Mega + RAMPS, **one** driver in the **X** socket, no motor. UART
pigtail (manual §2.5, already checked with the multimeter): lead **TX2** on
AUX-4 pin 18, **RX2** on AUX-4 pin 17, **A** on the top of the X driver's
**RX** pin (4th from EN). Leads B, C and KEY hang free for now (their female
ends are insulated; keep them off the board). An F–F jumper from the top of
the X driver's **DIAG** pin → X_MIN **S** pin. 12 V into RAMPS's **5A** input.

1. USB on, logger running. Then 12 V on.
2. Type `set axes 1`, then `ping`.
3. Look at the `DRV,A,...` line. Good: `DRV,A,1,21,0,0,0,0,…` = present,
   version 21, MS1 = 0, MS2 = 0, DIAG pin low, DIAG register low. The last two
   fields are status (GSTAT reads 1 right after power-up: that's the
   driver's "I was reset" flag, normal).
3a. **Set its VREF pot to minimum by measurement** (12 V on; the driver stays
   off, EN held high by the RAMPS pull-up, and no motor is connected).
   Multimeter on DC V, black probe on the "5A" − terminal, red probe on the
   pot's metal centre. Turn the pot slowly, a little at a time, the way that
   makes the reading **fall**, until it stops falling (near 0 V). Which way
   that is isn't in BTT's manual, hence measuring. If the centre reads 0 V
   whichever way you turn, stop and tell me.
   **Careful: the pot sits right beside the VM (12 V, "VS" on the board) and
   GND pins.** Put heat shrink over the screwdriver's shaft so only the tip
   is bare, or use a plastic trimmer tool. (Paul, 2026-10-09: a bare
   screwdriver bridged VM–GND, a spark, and the pot then read 0 V: the 12 V
   rail had dropped out (RAMPS F1 or the PSU's protection). After 2 minutes
   with everything off it was back: 12.3 V at the "5A" terminal and at VM,
   all four drivers answering `ping`, no damage.)
4. If it says `DRV,A,0,0,...`: 12 V off. Check lead A is on **RX** (not TX
   or CLK), the TX2 and RX2 leads aren't swapped on AUX-4 (TX2 is the lead
   with R1), and there's no jumper on X's MS3 position. Then try again.
5. 12 V off. Add the Y, Z and **E0 (key)** drivers — with their jumpers and
   DIAG jumpers: Y → X_MAX S, Z → Z_MIN S, **E0 → Z_MAX S** — and pigtail
   leads B, C and KEY on the RX pins of the Y, Z and E0 drivers. 12 V on.
   `set axes 15`, `ping`. Then set the **Y, Z and E0 pots** to minimum the
   same way as step 3a.
6. **Check each DIAG lead lands on its own input** (the pull test). The 7th
   field of a `DRV` line is the level the Mega reads on that axis's DIAG
   input; its pull-up makes it 1 when nothing drives it. Pull the **A** lead
   off the top of the X driver's DIAG pin (leave the header end), `ping`:
   only `DRV,A` may show 1 there. Put it back; repeat for B (Y driver),
   C (Z driver) and K (E0 driver). Another axis going to 1 = crossed leads in
   the endstop connector; none = the lead isn't on a DIAG input. (Paul,
   2026-10-10: the A and K leads were crossed in the connector, which showed
   up only in stage 3 as a stall that never stopped the key; this step catches
   it before any motor turns.)

**Send back**: the `DRV,A` line from step 3; the lowest VREF reading and
which way you turned (step 3a; and for the other three); the four `DRV` lines from
step 5; for step 6, which axis went to 1 for each pulled lead. Expect `DRV,B,1,21,1,0,...`, `DRV,C,1,21,0,1,...`
and **`DRV,K,1,21,1,1,...`** (the key in E0, address 3: MS1 = MS2 = 1). If a
DIAG field reads 1 at rest, say which.

---

## Stage 2 — One motor turning at low current

Setup: as stage 1 end; a motor on the **X** motor header (12 V off while
plugging). The motor sits loose on the bench. Put a tape flag on its shaft and
draw a mark on the bench in line with it.

1. 12 V on. `set axes 1`, `set maA 400` (0.4 A).
2. `jog A 200`. The shaft should make **exactly one turn** and stop on the
   mark. Note which way it turned, seen from the shaft end.
3. `jog A -200`: one turn back.
4. `jog A 800` (4 turns): smooth? Back on the mark?
5. If it buzzes or jitters instead of turning, 12 V off and swap the two
   middle wires of the motor plug (`docs/bom.md` note). Then repeat.
   (Paul, 2026-10-09/10: needed on **all four** motors, every plug wired the
   same; after the swap they all run smooth and quiet.
   `control/harness/ramps_and_uart.md` A5.)

**Result (Paul, 2026-10-10):** `jog A 200` = exactly one turn, so the motor
is **1.8° per step (200 full steps/rev)**, as `config.h` assumes. `jog A 200`
turns the shaft **clockwise seen from the shaft end** (motor A, plug black
toward 2B, `invA` 0). What that means for the dial is settled in stage 4b.

**Send back**: (a) did 200 steps give exactly one turn — or how far off
(e.g. "half a turn" means the motor is 0.9°/step); (b) direction of `jog A
200`, seen from the shaft end (clockwise/anticlockwise); (c) smooth or noisy;
(d) the `# moved ...` lines.

---

## Stage 3 — StallGuard on the bench (by hand): check the 50 % rule

Same setup. The firmware calibrates its own stall thresholds: it measures
the free-running StallGuard reading, then calls it a stall when the reading
falls to **50 %** of that (`CFG_SG_CAL_PCT`). This stage checks that 50 %
sits clearly between running free and stalling. It follows the datasheet's
own procedure (§11.2): watch SG_RESULT running free, then while braking the
shaft by hand.

1. `set maA 600` (the dial current; 1000 until 2026-10-14), `set sgA 0` (no stopping).
2. `sg A 800`. The logger prints `SG,A,<step>,<value>` lines while the motor
   runs free. Note the typical and the lowest value.
3. `sg A 800` again. This time pinch the tape flag (or the shaft through a
   rag) with growing force until the motor stalls (it buzzes and stops
   turning). Let go at once. Note the lowest value just before the stall.
4. Check the rule: `set sgA <free-running median ÷ 4>` (that is how the
   firmware sets it, `sgthrsFromBaseline()`: SGTHRS = median × 50 % ÷ 2,
   and DIAG fires when SG_RESULT ≤ 2 × SGTHRS). **Correction (2026-10-10):**
   this said "lowest ÷ 4"; the firmware uses the median. `jog A 800` without touching, 3 times:
   each must end `stalled=0`. Then `jog A 800` and pinch, 3 times: each must
   stop by itself, `stalled=1`, soon after you load it.

**Send back**: the raw log (it has all the SG lines), and whether step 4
behaved. If 50 % is too tight or too loose, I'll change `CFG_SG_CAL_PCT`.

**Result, key motor (Paul, 2026-10-10).** Run on the key (`K`, E0) instead of
dial A: the dial motors were already in their housing, the key turner's
spindle was easy to reach, cap off the key. `set maK 600` (the key's start
current), 1 rev/s, 1/16 microsteps, StealthChop, 1 m motor cable.
- Running free (step 3's run outside the grip, 1,147 samples): SG_RESULT
  median **276**, lowest **248**, highest 350.
- Gripped: falls steadily while the shaft still turns (230 → 46), crossing
  the 50 % line (138) about 14 full steps before the shaft stopped; stalled,
  it swings 0–340 with readings of **0–20** about every 4 full steps.
- `set sgK 69` (276 × 50 % ÷ 2): 4 of 4 free runs `stalled=0` (800 full
  steps each); 3 of 3 gripped runs stopped by themselves, `stalled=1`, after
  156, 200 and 120 full steps.
- **The 50 % rule holds for the key** at 0.6 A through the 1 m cable, with a
  wide margin (lowest free 248 against a trip point of 138). The dials get the
  same check from their own calibration on the door (stage 4).
- On the way: the first try never stopped because the A and K DIAG leads were
  crossed in the endstop connector (found with the pull test, now stage 1
  step 6).

---

## Stage 4 — Dial unit on the door: seat, calibrate, home

**4a. By hand first (no electronics).** Already answered (Paul,
2026-10-06): every dial turns clockwise without limit, stops when turned
anticlockwise, and has 20 evenly spaced clicks (18°). There are no marks on
the door. The robot now finds the clicks itself. The dials turn with the real
key inserted at its start position, and still click with the key turned to
its ~100° stop (Paul, 2026-10-06). Nothing left to do by hand here.

**4b. On the door** (12 V off while placing): dial unit on, all three motors
plugged in (A = top-left = X, B = top-right = Y, C = bottom = Z). The key
turner is not needed yet. 12 V on. `set axes 7`.
1. **Direction**: `jog A 10`. Watch dial A's big gear, or a tape flag on it.
   Did the *dial* turn clockwise or anticlockwise, seen from in front of the
   safe? Same for `jog B 10` and `jog C 10`.
   (The dials stop anticlockwise, so the firmware homes anticlockwise and
   treats clockwise as positive. I'll set the invert flags from your answer,
   or use `set invA 1` etc.)
   **Result (Paul, 2026-10-10):** with invert 0, `jog A/B/C 10` turned every
   dial **anticlockwise**, all three alike, so `CFG_INVERT_A/B/C` = 1
   (firmware after this change; until it is uploaded, `set invA 1`,
   `set invB 1`, `set invC 1` after every reset).
   Don't look for a stall by jogging a dial into its stop: before
   `calibrate`, the dial thresholds are 0 (`CFG_SGTHRS_A/B/C`, StallGuard
   off), and a short jog is mostly ramp, below the speed where StallGuard
   reads (`CFG_SG_MIN_RPS` 0.4 rev/s) plus the first 2 full steps ignored.
   `calibrate` sets the thresholds and homes with bounded moves at speed.
   (Paul, 2026-10-10: short jogs into the stop didn't stop on a stall.)
2. **Seat**: `seat`. Each dial turns 1/8 turn slowly **clockwise** (the way it
   never meets its stop). Listen and watch: does each plug **drop into its
   star** (a click, the plug moves in)?
3. **Calibrate**: `calibrate`. For each dial, it makes one free clockwise
   turn and prints `CAL,…,A,<baseline>,<threshold>,<ripple>,<noise>,<clicks
   found 1/0>`. Then it homes (two `HOME` lines; pass 2 should read about
   **40**) and prints `OFFSET,…,A,<position 1 in full steps>,1`. From
   firmware v0.5 it ends by switching the dial drivers off for half a second
   and on again (`EV,…,SETTLED,7`), so each dial falls into its click.
   - `stalled on its free calibration turn`: `set sgA 0` (and B, C), then
     retry.
   - `clicks not clear`: send me the log; it falls back to a fixed offset.

   **Result (Paul, 2026-10-14):** at 1000 mA the homing failed its repeat
   check (`HOMEREP`). At 600 mA (`set maA 600`, `maB`, `maC`) seat,
   calibration and homing passed on all three dials: `CAL` A 216/54/29/6/1,
   B 242/61/16/9/0, C 257/64/11/5/1 (baseline/threshold/ripple/noise/clicks);
   pass 2 41, 41, 40; position 1 at 14.3 (A) and 18.3 (C) full steps from
   the clicks. **Dial B's clicks don't show** (ripple 16 against noise 9,
   the same at a second calibrate), so B uses the config offset, 10 full
   steps. So `CFG_DIAL_RUN_MA` = **600** (firmware v0.5; before it, `set maA
   600` etc. after every reset).
4. **Home repeatability**: `home A` 5 times, then B and C. Pass 2 should stay
   near 40 each time.

   **Result (Paul, 2026-10-14, at 600 mA):** A: pass 2 41–42, position 1
   14.3–15.9. C: 40–41, 17.4–18.7. **B: 40–41 whenever it was the first home
   after a seat or after the motors had been off; homed again straight after
   a home, 47, 47, 48, 49** (two `HOMEREP`). Over three homes in a row B's
   stop seemed to move 32 full steps anticlockwise, which a fixed stop can't,
   and when an error switched the motors off, B's next first pass ran 29 full
   steps from where it had stopped. Something in B's drive gives under the
   homing push and relaxes when the motor lets go. B's gear moves ≤ 5° (Paul,
   2026-10-16).
   **Decision (Paul, 2026-10-16):** not worth chasing: homing is once per
   session. End it by switching the dial drivers off so the dials settle into
   their clicks (firmware v0.5: after every homing, at session start, each
   re-check, `calibrate` and `home`). Each later home then starts from a
   relaxed drive, like the good first homes above.
   **Re-check with v0.5:** `calibrate`, then `home B` 3 times. Pass 2 should
   now stay near 40 every time.
5. **The settle.** Watch the three big gears at the end of `calibrate`, when
   `EV,…,SETTLED,7` prints. Does any of them turn as its motor lets go, and
   how far? A and C should hardly move (their position 1 comes from their
   clicks). If B turns more than ~5° (a quarter of a click), say which way:
   its config offset (`CFG_HOME_OFFSET_B`) then moves to its click. Otherwise
   the first re-check of a run would stop with `RECHECK` and print the
   offset to use (firmware README, v0.5).
   (The earlier version of this step, `goto 5 5 5` then `release`, was
   refused on 2026-10-14: B's `HOMEREP` had switched every motor off, which
   un-homes every dial, and only C was homed again. v0.5 says which dials
   aren't homed.)
6. **Key out vs. key in.** `release`, take the real key out, then
   `calibrate`. Put the key back in at its start, then `calibrate` again.
   This compares the dials' load and click pattern with and without the
   key. A clear difference would suggest the key changes what the dials
   drive (`control/sequence.md`, "Does a combination dialled with the key
   already in count?"). The same numbers are only weak reassurance.
7. **Position 20, and does anything add up over full turns?** (Paul's
   question, 2026-10-16: is there an error per step?)
   a. `calibrate`, then `home A`, `home B`, `home C`. Note each `HOME` pass 1:
      that's the reference.
   b. Five times: `goto 20 20 20`, then `goto 1 1 1`. Each dial turns 19
      clicks out and back, 5 times.
   c. `home A`, `home B`, `home C` again. Each pass 1 should match (a) within
      ~2 full steps. 4 or more means steps were lost along the way.
   Dial C's first click is ~18.5 full steps from its stop, so its position 20
   (19 clicks on) is only ~1.5 full steps (~1.4° of dial) short of one full
   turn from the stop, where the stop catches again when the dial turns back.
   Does every `goto 1 1 1` end with `# dials at 1 1 1`, or with `JAM`?

**Send back**: the `HOME` lines from 4 (v0.5); for 5, which gears moved and
how far; for 6, both runs' `CAL` and `OFFSET` lines, labelled "key out" and
"key in"; for 7, the `HOME` lines from a and c and any `goto` that didn't end
with `# dials at …`.

---

## Stage 5 — Key turner: direction, current, stop angle

**5a. By hand**: all answered (Paul, 2026-10-06). The key goes in one way
only. From there it won't turn anticlockwise at all: that rest stop is the
firmware's key home. It turns ~100° clockwise to its stop and stays wherever
it is left (no spring back). It comes out only back at the start. So before
any stage below, turn it back to the start by hand.

**5b. Mounted**: key in, at its start; key turner on (12 V off while placing
and plugging). The key driver is in the RAMPS **E0** socket (revision
2026-10-08.1), VREF pot at minimum; its motor's own cable is plugged into the
E0 motor header. 12 V on. `set axes 8` (key only), then `ping`: expect
`DRV,K,1,21,1,1,...`.
1. **Direction**: `set maK 400`, `key 10`. The key should turn **clockwise**
   10° and come back. If it went anticlockwise: `set invK 1`, and say so.
2. **Minimum current**, with StallGuard off (`set sgK 0`): `key 80` at
   `set maK 500`, then 400, 300, 250, 200. For each, did the key actually get
   to about 80° (watch the cap), or did the motor skip or buzz?
3. Set `maK` to **2 × the lowest current that worked**, 1000 at most.
4. **Calibrate the key**: `calibrate`. It turns the key 60° clockwise, sets
   the key's threshold from its free-running reading (`CAL,…,K,…`), then turns
   back until it stalls on the rest stop. That return proves the threshold
   works. If it says `did not find its rest stop`: send me the log.
5. **Stop angle**: `learn`, 3 times. Each prints 3 `LEARN` lines and an
   `NSTOP` line (N and the spread).
6. Watch the key-turner housing during the learns: does it shift or rock
   on its magnets?
7. **Key StallGuard through the cable**: during the `learn` turns, did the
   key's stall detection find the stop cleanly (an `NSTOP` line each time,
   with a small spread)? If it reads dull or erratic, shorten the key motor
   cable and repeat (revision 2026-10-08.1: the cable length is the one thing
   about the E0 move still unproven).

**Send back**: direction; the current table from 5b.2; final `maK`; the raw
log (CAL, LEARN, NSTOP lines); any housing movement; whether the key's
StallGuard found the stop cleanly through the 1 m cable.

---

## Stage 6 — A short dry run

Everything on the door, both units, cable plugged. I'll have sent a
`config.h` with your numbers by now; upload it. 12 V on.

1. `cfg`, then `ping`: all four `DRV` lines present.
2. `reset yes`, then `start`. The session start takes ~40 s: key home, key
   calibration, seat, one calibration turn per dial, home ×3, learn.
3. Let it run **~50 attempts** (about a minute). Each attempt turns one dial
   by one click, turns the key to its stop and back.
4. Press the **button** (or type `pause`). It finishes the attempt, re-checks
   (re-homes and re-learns), and stops.
5. Watch for: anything sliding on the door; a dial moving while the key is
   turned (it never should); odd noises.
6. **Power-dip check** (does the firmware notice a driver reset? See
   `control/firmware/README.md`, "Driver resets"):
   1. `home`. It homes the key, then each dial. Wait until nothing moves.
   2. Switch the 12 V supply off, count to 5, and switch it back on. Leave
      the USB connected.
   3. Straight away, `goto 2 2 2`. Expect `GSTAT,…,A,1,before`, then
      `ERR,…,DRVFAULT,…`. **No dial should move.** If the boot line
      `# Fichet safe robot …` appeared when the 12 V came back, the Mega
      restarted instead: say so.
   4. `ping`. In each of the four `DRV` lines, the second-to-last field
      (GSTAT) should read `1`. The paused run is untouched.

**Send back**: the raw log; the time for 50 attempts; anything that moved or
sounded wrong; from step 6, the `GSTAT`, `ERR` and `DRV` lines, and whether
anything moved after `goto`. Then we'll set the classification bands from the
measured spread and start the real run with `resume`.

---

## What these stages settle (`config.h` / `CLAUDE.md` open items)

| Open item | Stage |
|---|---|
| Driver UART addresses and wiring (UART lead on each driver's RX pin) | 1 |
| Motor step angle | 2: **1.8° confirmed** (Paul, 2026-10-10) |
| StallGuard thresholds — now self-calibrated; the 50 % rule and speeds | 3, 4, 5 |
| Hard stop and clicks per turn | answered 2026-10-06: stop anticlockwise, unlimited clockwise, 20 clicks |
| Dials still turn with the key inserted at rest | answered 2026-10-06: yes, at rest and at the key's ~100° stop |
| Does a combination dialled with the key in count? | weak hint from 4b.6; the real test is the first full run |
| Motor direction ↔ dial direction | 4b |
| Plug seating (seat routine angle and speed) | 4b |
| Position 1 relative to the stop: found from the clicks (A, C, 2026-10-14); B from the config offset, then settled into its click (v0.5) | 4b.5 |
| Key motor direction | 5 (rest stop answered 2026-10-06: none anticlockwise of the start → `keyhome` 0) |
| Key current (2 × minimum) | 5 |
| Key stop angle N and its spread (classification bands) | 5, 6 |
| Magnets holding under real loads | 5, 6 |
| The firmware notices a driver reset (GSTAT check, v0.3) | 6 |
| Dial current | 600 mA (2026-10-14: at 1 A homing failed its repeat check). The dial torque itself is still not measured |
| Dial position 20 clear of the stop on the way back (C's first click is ~18.5 full steps out); no steps lost over full turns | 4b.7 |
