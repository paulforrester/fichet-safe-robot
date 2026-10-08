# Bench bring-up plan

> **Revision 2026-10-08.2** · key driver on the RAMPS E0 socket; UART pigtail · log: `docs/revisions.md`

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

**Logging**: run `python3 control/firmware/tools/logger.py --port <port>`
(after `python3 -m pip install pyserial`), and type commands in that window.
It saves everything to `runs/<date>_raw.log`. For any stage you can just send
me that file. (Or use the Arduino Serial Monitor at 115200, Newline — but not
both at once.)

---

## Stage 0 — Preparation (no power)

1. **Flash**: install TMCStepper 0.7.3 (Library Manager). Open
   `control/firmware/safe_robot/safe_robot.ino`, board "Arduino Mega or Mega
   2560". Upload with only USB connected (RAMPS may be on or off the Mega).
2. Start the logger and type `status`. You should see
   `# Fichet safe robot 0.4 (2026-10-08, rev 2026-10-08.1) - type help` and `# state=IDLE run=0 next=0 ...`.
3. **RAMPS jumpers** (under the sockets): X none; Y **MS1** only; Z **MS2**
   only; **no MS3 jumper anywhere**.
4. **EN-end pins** on all **four** drivers (the three dials and the key;
   leave the spare untouched): before fitting the heatsinks, cut the
   **bottom** ends of the two EN-end pins flush underneath; leave the tops.
   No soldering (revision 2026-10-08.2; `control/wiring.md` §3.3).
5. Fit heatsinks. **Driver orientation**: do the multimeter check in manual
   §2.4 step 2 first (the sockets have no pin-1 mark on top). The driver's
   VS/GND/motor side goes in the socket row nearer that axis's motor header.

**Send back**: the two lines from step 2; the orientation check results for
X (manual §2.4 step 2); any surprises in steps 3–5.

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
4. If it says `DRV,A,0,0,...`: 12 V off. Check lead A is on **RX** (not TX
   or CLK), the TX2 and RX2 leads aren't swapped on AUX-4 (TX2 is the lead
   with R1), and there's no jumper on X's MS3 position. Then try again.
5. 12 V off. Add the Y, Z and **E0 (key)** drivers — with their jumpers and
   DIAG jumpers: Y → X_MAX S, Z → Z_MIN S, **E0 → Z_MAX S** — and pigtail
   leads B, C and KEY on the RX pins of the Y, Z and E0 drivers. 12 V on.
   `set axes 15`, `ping`.

**Send back**: the `DRV,A` line from step 3, and the four `DRV` lines from
step 5. Expect `DRV,B,1,21,1,0,...`, `DRV,C,1,21,0,1,...`
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

1. `set maA 1000` (the dial current), `set sgA 0` (no stopping).
2. `sg A 800`. The logger prints `SG,A,<step>,<value>` lines while the motor
   runs free. Note the typical and the lowest value.
3. `sg A 800` again. This time pinch the tape flag (or the shaft through a
   rag) with growing force until the motor stalls (it buzzes and stops
   turning). Let go at once. Note the lowest value just before the stall.
4. Check the rule: `set sgA <free-running lowest ÷ 4>` (that is how the
   firmware sets it: half of 50 %). `jog A 800` without touching, 3 times:
   each must end `stalled=0`. Then `jog A 800` and pinch, 3 times: each must
   stop by itself, `stalled=1`, soon after you load it.

**Send back**: the raw log (it has all the SG lines), and whether step 4
behaved. If 50 % is too tight or too loose, I'll change `CFG_SG_CAL_PCT`.

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
2. **Seat**: `seat`. Each dial turns 1/8 turn slowly **clockwise** (the way it
   never meets its stop). Listen and watch: does each plug **drop into its
   star** (a click, the plug moves in)?
3. **Calibrate**: `calibrate`. For each dial, it makes one free clockwise
   turn and prints `CAL,…,A,<baseline>,<threshold>,<ripple>,<noise>,<clicks
   found 1/0>`. Then it homes (two `HOME` lines; pass 2 should read about
   **40**) and prints `OFFSET,…,A,<position 1 in full steps>,1`.
   - `stalled on its free calibration turn`: `set sgA 0` (and B, C), then
     retry.
   - `clicks not clear`: send me the log; it falls back to a fixed offset.
4. **Home repeatability**: `home A` 5 times, then B and C. Pass 2 should stay
   near 40 each time.
5. **Parked on a click?** `goto 5 5 5`, then `release` (motors off). Watch and
   listen: does any dial **snap** to a click when released? Sitting still
   means it was parked on its click.
6. **Key out vs. key in.** `release`, take the real key out, then
   `calibrate`. Put the key back in at its start, then `calibrate` again.
   This compares the dials' load and click pattern with and without the
   key. A clear difference would suggest the key changes what the dials
   drive (`control/sequence.md`, "Does a combination dialled with the key
   already in count?"). The same numbers are only weak reassurance.

**Send back**: directions; seated yes/no per dial; the raw log
(CAL / HOME / OFFSET lines); for 4b.5, which dials snapped, if any; for
4b.6, both runs' CAL and OFFSET lines, labelled "key out" and "key in".

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
| Motor step angle (1.8° assumed) | 2 |
| StallGuard thresholds — now self-calibrated; the 50 % rule and speeds | 3, 4, 5 |
| Hard stop and clicks per turn | answered 2026-10-06: stop anticlockwise, unlimited clockwise, 20 clicks |
| Dials still turn with the key inserted at rest | answered 2026-10-06: yes, at rest and at the key's ~100° stop |
| Does a combination dialled with the key in count? | weak hint from 4b.6; the real test is the first full run |
| Motor direction ↔ dial direction | 4b |
| Plug seating (seat routine angle and speed) | 4b |
| Position 1 relative to the stop — now found from the clicks; parked-on-click check | 4b |
| Key motor direction | 5 (rest stop answered 2026-10-06: none anticlockwise of the start → `keyhome` 0) |
| Key current (2 × minimum) | 5 |
| Key stop angle N and its spread (classification bands) | 5, 6 |
| Magnets holding under real loads | 5, 6 |
| The firmware notices a driver reset (GSTAT check, v0.3) | 6 |
| Dial torque (dial current, still 1 A) | not measured directly: if homing works at 1 A with margin, keep it; we can try 0.8 A in stage 4 |
