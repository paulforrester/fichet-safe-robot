# Control architecture and operating sequence

> **Revision 2026-10-08.2** · key driver on the RAMPS E0 socket; UART pigtail (no change to the sequence) · log: `docs/revisions.md`

Working notes on how the robot actually operates the safe, so this
doesn't only live in chat. Captures the mechanism understanding and
the operating sequence as of 2026-09-29 — expect this to get refined
once tomorrow's measurements and the first hardware tests come in.

## The mechanism

This is a classic wheel-pack combination lock, not a front-dial
combination safe:

- 3 "dial" sockets (the tube-socket spline our test key fits) each
  drive one combination wheel directly.
- A 4th socket takes the real opening key. Turning it drives a cam
  against a fence that rides on the edges of the 3 wheels.
- Wrong combination: the fence rides on the wheel edges, and the key
  stops after some angle, call it N°.
- Right combination: all 3 wheels' gates align under the fence, it
  drops in, and the key turns past N° (roughly N + 10%, though this
  margin may need empirical tuning — see False sets below) into the
  bolt-withdraw motion.
- Each dial wheel has 20 positions → 20³ = 8,000 combinations to
  search. Very tractable to brute-force.

## Hardware: one answer for "force feedback" on all 4 motors

Force/torque feedback is needed in two places, both solved by the
same component:

1. **Homing each dial wheel** — move backward until resistance is
   felt at position 1 of 20 (assumes each wheel has a natural hard
   stop just past position 1 — **needs verification against the real
   lock**, see open items below).
2. **Not overdriving key 4** — back off as soon as resistance is felt,
   whether that's the normal N° stop or (hopefully) further in on a
   winning combination.

**Recommendation: stepper motors + StallGuard-capable drivers
(TMC2209 or TMC2130)**, one per motor (4 total). These sense
back-EMF and report when a motor is being blocked — no separate
torque sensor, load cell, or current-sense board needed. Well
supported on both Arduino (step/dir + UART for the stall threshold)
and Raspberry Pi, ~€3-5/driver.

For key 4's rotation angle: counting steps from a freshly-established
home (re-homed at the start of every attempt, per the sequence below)
should be accurate without an encoder, as long as the printed coupler
doesn't slip under torque. A cheap magnetic encoder (AS5600) is an
easy add-on later if slip turns out to be a problem. Note for later:
if an encoder is added and full rotation could exceed 360°, it needs
turn-counting logic — a bare AS5600 only reports position within one
revolution.

## Electronics: Mega 2560 + RAMPS 1.4 wiring plan

Settled 2026-09-29. Mounting/wiring the 4 drivers: **RAMPS 1.4**, a
shield that plugs directly onto the Mega 2560 and has 5 driver sockets
in the same StepStick footprint as the BigTreeTech TMC2209 V1.3 boards
— no soldering needed for the 3 local drivers, they plug straight in.
Only 3 of its 5 sockets get used (X/Y/Z, for the 3 dial motors) — the
key-turner unit's driver does **not** plug into the shield, per the
driver-placement rule above; it's wired out to the remote unit over the
inter-unit cable instead.

**Correction (revision 2026-10-08.1, 2026-10-08):** the key driver now plugs
into the RAMPS **E0** socket too, so all four drivers are on the shield. The
remote board and the inter-unit signal cable are gone; only the key motor's
own cable runs to the key turner. See the "Cable and driver placement"
correction below and `control/wiring.md` (log 2026-10-08).

**Correction to the earlier "4 hardware UART ports" plan**: the Mega
has 4 hardware serial ports total (`Serial`/`Serial1`/`Serial2`/`Serial3`),
but `Serial` (pins 0/1) is tied up by USB — using it for a driver would
mean losing USB programming/debug output while the robot runs. That
leaves only 3 clean hardware UARTs, not 4. Fixed by using the TMC2209's
built-in **UART multi-drop addressing** instead of 1:1 dedicated lines:
up to 4 drivers can share a single UART bus, each given its own address
(0–3) via its MS1/MS2 pin strapping. So **all 4 drivers (3 local + the
remote key-turner) share one bus on `Serial2`** (Mega pins 16 TX / 17
RX). This is the officially-supported mode, not a hack, and it means
only one UART signal wire needs to extend out to the remote unit rather
than a dedicated pair.

Why `Serial2` specifically, not `Serial1` or `Serial3`: confirmed
against the standard RAMPS 1.4 pin map — `Serial1` (pins 18/19) and
`Serial3` (pins 14/15) are the *same physical Mega pins* as the Z-axis
and Y-axis MIN/MAX endstop headers respectively. Using either of those
serial ports would make the corresponding endstop headers unusable.
`Serial2` (pins 16/17) has no such conflict, so it leaves every
endstop header free.

That matters because the endstop headers are being **repurposed to
carry each local driver's DIAG (stall-output) signal** instead of an
actual mechanical switch — X_MIN (pin 3), Y_MIN (pin 14), Z_MIN (pin
18), one per local dial motor's driver. With UART on `Serial2`, none of
these three are double-booked.
**Correction (2026-10-06, `control/wiring.md`):** the DIAG lines go to
X_MIN (D3), **X_MAX (D2)** and Z_MIN (D18) for dials A/B/C, and the key's
DIAG to Z_MAX (D19). DIAG is a *pulse* (TMC2209 datasheet §11.2), so the
firmware latches it with an interrupt, and Y_MIN's D14 has no external
interrupt on the Mega. Y_MIN now takes the start/stop button.

*(Superseded by revision 2026-10-08.1: the key driver is in the RAMPS E0
socket, so its STEP/DIR/EN come from E0 — D26/D28/D24 — and its DIAG lead
goes to Z_MAX like the dials', with no cable. The paragraph below is kept as
the earlier remote-driver plan.)*

For the remote key-turner driver (off-shield): STEP/DIR/ENABLE + its
DIAG line are wired from 4 free Mega digital pins (exact pins aren't
critical — any spare GPIO broken out on RAMPS' AUX headers or tapped
from the Mega's own header row works) out through the inter-unit cable,
alongside the shared `Serial2` UART tap and 12V/GND motor power. Each
driver (all 4) also needs a ~1kΩ resistor between the MCU's UART TX pin
and its own PDN_UART pin — standard TMC2209 single-wire UART wiring,
one resistor per driver regardless of bus-sharing.

**Correction (2026-10-06, `control/wiring.md`):** (1) one 1kΩ resistor in
total, not one per driver: TX2 → 1kΩ → bus, RX2 and every driver's
PDN_UART straight on the bus — the datasheet's own circuit (TMC2209 DS
Fig. 4.1). (2) The key-turner driver gets only STEP (D23), DIAG (D19),
UART, 12V, GND and 5V over the 6-conductor cable; its EN and DIR are tied
to GND on its board, and the firmware disables it and sets its direction
over UART (CHOPCONF.TOFF, GCONF.shaft).

## Mounting: two independent units, not one frame

Resolved 2026-09-29: photos confirmed the keyhole (socket #4) and the
3-dial cluster are visibly separated on the door face — not adjacent.
Socket #4's key also turned out to use a traditional ornate bow, not
the spline profile (see below), which is a second, independent reason
to decouple it. **Building this as one rigid frame spanning the whole
door was dropped** in favor of two independently-mounted units,
connected by a cable:

- **Dial unit**: all 3 dial-socket motors + drivers, the
  microcontroller (Arduino/Pi), and the power supply. This is the
  "brain" — it's the side with 3 motors and the actual combination
  logic, so centralizing electronics here avoids a third enclosure.
- **Key-turner unit**: a single motor + local driver + a gripper that
  clamps onto the real key's bow (already manually inserted into
  socket #4 before the robot goes on — this unit never touches the
  key's blade, just its protruding head). Connected to the dial unit
  by a cable.

Each unit attaches to the door independently with **neodymium magnets**
— confirmed 2026-09-29 that both the safe body and door are ferrous, so
this is settled, not a fallback. Paul already has ~100 2mm×8mm
neodymium disc magnets on hand from a prior print project ("Poop chute
print for h2d"), which also worked out a tight-press-fit pocket size for
this exact magnet: **8.00mm diameter × 1.9mm depth** (0.1mm undersize on
depth vs. the 2mm-thick magnet, for an interference press fit rather
than a loose slot — glue optional/backup, not load-bearing). Reuse that
pocket geometry directly in both units' mounting faces rather than
re-deriving it. **Superseded 2026-10-06:** both units now mount with
22mm rubber-coated M4 pot magnets (Wukong) — 6 on the dial unit, 3 on the
key turner — in through holes with printed retainers; the disc pockets
printed with strings and bare discs grip poorly sideways. See
`docs/housing_decisions.md`. Splitting avoids one large frame needing to be
dimensionally accurate across the full door width, and each unit is
small enough to print in one piece.

**Cable and driver placement**: originally each driver sat next to its
motor — the key driver on a remote board at the key turner — on the
reasoning that "StallGuard reads back-EMF right at the motor, and long
motor-phase wiring would dull that sensitivity".

**Correction (revision 2026-10-08.1, 2026-10-08):** that reasoning is
withdrawn. StallGuard is measured inside the driver, and sensorless homing
is routinely done with the driver on the mainboard and the motor on a cable
of this length (e.g. 3D printers; Klipper's TMC documentation). So the key
driver moves to the RAMPS **E0** socket like the dials, and the key motor's
own ~1 m cable runs to it. The 6-conductor signal cable, the remote board
and its Phoenix connectors are gone. If bench stage 5 shows the key's
StallGuard too dull through the cable, shorten it. Full reasoning:
`control/wiring.md`, decision log 2026-10-08.

**Alignment**: the key-turner unit has an easier mounting job than the
dial unit — since the real key is already seated in socket #4 by hand
(step 1), the gripper only needs to land on the key's protruding bow,
a much bigger and more forgiving target than the ~8mm star holes the
dial unit has to register precisely.

## Dial drive (v2 housing, 2026-10-05)

Each dial is driven through a **2:1 spur gear pair** (14T on the motor,
28T on the dial shaft): one dial turn = 2 motor turns = 400 full steps =
**20 full steps per dial position**. Motor direction is reversed relative
to the dial (external gears). The gear-shaft is **spring-loaded**: when the
unit is put on the door, a plug that doesn't line up with its star is
pushed back, so the first job of every session is a "seat" routine —
turn each dial motor slowly (at most 1/8 of a dial turn = 45deg of dial,
90deg of motor) until its plug drops into the star, then home as below.
Until the dial torque is measured, run the dial drivers at about 1A RMS:
the reduction doubles what the motor can put into the printed gear and
plug teeth.

**Key torque (measured 2026-10-06): 0.07–0.08 N·m** (0.14–0.16 kg at
50mm). About a quarter of what the motor gives at ~1 A, so the key turner
stays direct drive. Run the key motor at reduced current (~2× the key's
torque) and stop on StallGuard at the end stop, so the drive doesn't push the
housing against its magnets harder than it needs to.

## Operating sequence

1. Real key inserted into hole 4 (manual, one-time per session).
2. Dial unit aligned over the 3 dial holes and attached to the door;
   key-turner unit aligned over the protruding key bow and attached
   separately; the two connected by cable.
3. Dialing process triggered (code or a physical switch, TBD).
4. Each dial key homes: drives backward until stall-detected
   resistance = position 1 of 20. Can run serially or in parallel
   across the 3 dial motors.
5. Key-4 motor calibrates baseline: turns until stall-detected
   resistance (= N°), notes the angle, retracts to start. This
   replaces any need to pre-measure N by hand — the robot learns it
   as its first task, every session.
6. Main loop, for each of the 8,000 combinations:
   a. Drive each of the 3 dial wheels to the target digit.
   b. Attempt to turn key 4 to N + margin°.
   c. Record the *actual angle achieved* (not just pass/fail — see
      False sets below), whether by reaching target or by stalling
      first.
   d. Retract key 4 to start.
   e. If achieved angle clears the success threshold: stop, report
      the combination.

### As implemented (firmware v0.1, 2026-10-06 — `control/firmware/`)

Decisions made while writing the firmware, on top of the sequence above:

- **Start (step 3)**: both — the serial command `start` or the push button
  (on RAMPS Y_MIN). The button also pauses a run and resumes a stored one.
- **Order of the 8,000**: serpentine. Consecutive attempts differ in one dial
  by one position, so each attempt turns one dial one click, and no dial ever
  wraps from position 20 back to 1 (a wheel with a hard stop couldn't).
- **Key home every attempt**: retract until the key stalls at its rest
  (anticlockwise) stop, so every angle is measured from the same point.
  The rest stop exists: the key can't turn anticlockwise from where it goes
  in (Paul, 2026-10-06). A config switch can make the key return by step count
  instead. Paul also found (2026-10-06) that the dials still click with the
  key left at its ~100° stop, so the key wouldn't *have* to come all the way
  back between tries. **Kept anyway (Paul, 2026-10-06)**: see "Return the key
  to rest every attempt, or park it near N?" under Open items.
- **Self-calibration (v0.2, 2026-10-06, Paul's suggestion)**: each session
  measures each motor's free-running StallGuard reading and sets its own
  stall threshold (stall = reading down to 50 % of it). Each dial makes one
  free clockwise turn for this. From the same turn's 18° click ripple it
  finds where the clicks are, so position 1 = the first click clockwise of
  the stop. Where the first click sits relative to the stop can't be measured
  by hand (Paul: evenly spaced, 18° apart). The key is measured over 60° of
  free travel from rest. Datasheet §11.4 recommends this kind of
  in-application threshold. Bench stages 3–4 check the assumptions (the
  50 % rule; the ripple being visible).
- **Key home search 180°** (was 30°): the key stays wherever it is left — it
  doesn't spring back (Paul, 2026-10-06). After a power cut mid-attempt it
  can sit at its ~100° stop, and the session start must find the rest stop
  from there before any dial moves.
- **Seat**: turns each dial 1/8 turn slowly **clockwise**, the direction in
  which the dials never meet their stop. (Changed 2026-10-06 after Paul's
  check: the first version turned toward the stop.)
- **Homing (step 4)** runs twice per dial (stall, back off 2 positions, stall
  again); the two must agree. Before homing, the key is homed, then the slow
  1/8-turn seat runs.
- **N (step 5)** is the median of 3 tries. It is learned at the most recent
  attempt that was a clean fail — never at a possible false set. On a fresh
  run it's learned at the first two combinations, keeping the lower.
- **Each try** drives the key to N + 15°: clean ≤ N + 4°, false set between,
  success ≥ N + 10°, "early" < N − 8°. All are config values, to be set from
  the measured spread. The raw angle is always logged.
- **Re-check every 200 attempts**: re-home the dials (the stall must come
  where the step count says) and re-learn N. On a mismatch (a unit slipped),
  stop and rewind to the last good re-check.
- **Resume after power loss** (or a re-seat): progress lives in EEPROM. A
  resume redoes the whole session start and restarts from the last good
  re-check (≤ 200 attempts redone). A pause re-checks first, so it loses
  nothing.
- **Results reach Paul** as USB serial lines. `tools/logger.py` saves a raw
  log and an attempts CSV, and can re-classify afterwards.

## False sets

Some wheel-pack locks have false sets — positions that let the fence
drop partway, allowing a bit more rotation than a clean wrong
combination but not full opening. Purely a software concern, no
hardware implication. Logging the actual degrees achieved on every
attempt (not just a boolean) means the data can be re-examined after
the fact to tell clean-fail / false-set / success apart, rather than
depending entirely on getting the threshold right on the first pass.

## Open items

Resolved 2026-09-29:
- [x] Socket #4's profile — **not the spline at all**. The real key
      has a traditional ornate bow; the key-turner unit grips that
      bow rather than replicating a blade. See Mounting above.
- [x] Tooth geometry — locked in at HEIGHT 2.00mm / WIDTH 1.04mm, see
      `docs/decisions.md`.
- [x] Socket recess / collar clearance — measured directly at 12.25mm,
      confirms the 11.75mm collar (0.5mm clearance) is fine as-is.
- [x] One frame vs. multiple units — going with two: dial unit
      (3 motors + electronics) and key-turner unit, cabled together.
- [x] Ferrous door confirmed (both body and door) — mounting is
      neodymium magnets, pocket geometry reused from a prior project
      (8.00mm dia × 1.9mm depth for 2mm×8mm disc magnets, press fit).
      ~100 magnets already on hand.
      **Changed 2026-10-06** to 22mm rubber pot magnets (6 + 3), ordered —
      measure them and do a one-magnet sideways pull test on arrival.

Still open:
- [x] Key / lock-hole measurements (Paul, calipers, 2026-10-06): lock hole
      12.05mm; key protrudes 31.89mm, 84.75mm long, turns clockwise ~100deg
      then stops; bow vertical at rest, 24.60 wide, 2.5-2.9 thick on its flat
      part, swelling 9.48 at ~8mm, ring hole 10.75. Key turner v1 grips it with
      a slotted cap (see `docs/housing_decisions.md`). Torque to turn: measure
      with the fit-test lever + a luggage scale.
- [x] Lock hole position relative to the dial cluster — **calipers
      2026-10-06**: top-left dial->lock 110.13mm (far 122.25 / near
      98.01), bottom dial->lock 126.95mm (far 139.4 / near 114.5).
      Trilaterated against the dial triangle: the lock sits **~125mm to
      the left of the dial-cluster centre, essentially level** (1.8mm
      low), matching the door photo. The dial plate is r75, so ~50mm of
      clear door between the plate edge and the lock hole — the two
      units sit side by side with room. Cable run between them ~125mm.
- [x] Center-to-center spacing between the 3 dial holes — **measured with
      calipers 2026-10-05**: isosceles, 33.0mm across the top pair, 42.5mm
      from each to the bottom hole (apex down). Holes 13.0mm dia; the
      star starts 3.14mm below the door face (a real key goes in to
      15.5mm; the slots narrow toward a point, so a 2mm depth gauge
      stops at 8.92mm). In
      `cad/dial_unit_housing.scad` (v2); the 36mm equilateral placeholder
      was wrong by up to ~5mm. See `docs/housing_decisions.md`.
      (Superseded by the caliper measurement above — the old ~55mm
      photo estimate for the dial-to-lock gap was low; it's ~125mm
      centre-to-centre.)
- [x] Verify each dial wheel has a hard stop near position 1, for the
      homing move in step 4 to find — **Paul, 2026-10-06**: each dial turns
      clockwise without limit and stops when turned anticlockwise; 20 clicks
      per turn. Homing is anticlockwise to that stop. The seat turn was
      changed to clockwise so it can never press into it. Still to measure:
      the angle from the stop to the first click (home offset, bringup 4a).
- [x] Where the first click is relative to each dial's stop — Paul
      (2026-10-06): can't be read by hand, but the clicks are evenly spaced,
      18° apart; no marks on the door. The firmware now finds the clicks
      from StallGuard each session (v0.2). Key: stays wherever it's left (no
      spring back).
- [x] Do the dials still turn with the real key inserted at rest? The
      manual's normal use dials the combination *before* inserting the key
      (`docs/photos/complice_manual_normal_use.png`); the robot keeps the
      key in throughout. **Yes (Paul, 2026-10-06): the dials turn with the
      key at its start position, and still click with the key turned to its
      ~100° stop and left there.**
- [ ] **Does a combination dialled with the key already in count?** (Paul,
      2026-10-06.) The dials turn and click with the key in, but nothing
      shows that they still set the wheels then. The manual dials *before*
      inserting the key. If the lock only checks a combination set with the
      key out, the robot as designed can never open it, and it would need
      to pull the key out and push it back in at every attempt (a mechanical
      redesign of the key turner). No source either way: searched
      2026-10-06, but Fichet's manual PDF and the patent sites are blocked
      from the cloud session. A search excerpt mentions a separate Fichet
      "3-tube combination" user manual. How we'll know:
      (1) bench stage 4b.6 compares the dials' calibration with the key out
      and in: a clear difference is a warning sign, while the same numbers
      are only weak reassurance;
      (2) the first full run is the real test (≤ ~2 h of motion).
      If it ends with no success and clean data, this is the first suspect.
- [x] Return the key to rest every attempt, or park it near N? Raised by
      Paul's check above (2026-10-06). Firmware v0.2 returns it to its rest
      stop every attempt, which re-zeroes the angle each time and matches the
      manual's sequence. Parking it ~10° short of N between tries would save
      time. **Estimate** (motion only, from `config.h` speeds and the
      firmware's own ramp code; not measured): a full return costs ~0.82 s
      per attempt (key out 0.30 s + back 0.30 s + one dial click 0.23 s), so
      ~1.8 h for all 8,000. Parked: ~0.34 s, ~0.75 h. That saves ~1.1 h in
      the worst case, ~0.5 h on average. Logging, EEPROM writes and the
      re-checks every 200 attempts are not included; they're the same either
      way. Risks of parking: (1) Paul's caution: the lock may need the key
      back at the start before the bolts can retract. If so, the right
      combination would look like a clean fail, and we'd only find out
      after a whole run without success. (2) The angle would come from step
      counting since the key last touched its rest stop, so a lost step
      would shift later readings until the next re-zero. Recommendation:
      keep the full return for the first full run. Revisit if stage 6 shows
      attempts much slower than this estimate. **Decided (Paul,
      2026-10-06): keep the full return.**
- [ ] Torque/effort needed to turn each dial wheel and the key, to
      size motors and gearing.
- [x] Whether the Fichet-Bauche "Complice" line has any known
      anti-manipulation relocking behavior — **researched 2026-10-06**,
      `control/lock_research.md`. No source mentions an attempt-counting
      lockout. A relocker ("délateur") fires on mechanical or thermal attack,
      so forces stay low. The firmware stops if the key's stop angle changes.
      Confidence medium: only search excerpts were readable from the cloud
      session. Paul to read the manual's "Opening" / "Troubleshooting" pages.
