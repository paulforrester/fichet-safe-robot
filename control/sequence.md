# Control architecture and operating sequence

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

For the remote key-turner driver (off-shield): STEP/DIR/ENABLE + its
DIAG line are wired from 4 free Mega digital pins (exact pins aren't
critical — any spare GPIO broken out on RAMPS' AUX headers or tapped
from the Mega's own header row works) out through the inter-unit cable,
alongside the shared `Serial2` UART tap and 12V/GND motor power. Each
driver (all 4) also needs a ~1kΩ resistor between the MCU's UART TX pin
and its own PDN_UART pin — standard TMC2209 single-wire UART wiring,
one resistor per driver regardless of bus-sharing.

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
re-deriving it. Splitting avoids one large frame needing to be
dimensionally accurate across the full door width, and each unit is
small enough to print in one piece.

**Cable and driver placement**: the stepper driver (TMC2209) stays
physically next to its motor, including at the remote key-turner unit
— StallGuard reads back-EMF right at the motor, and long motor-phase
wiring would dull that sensitivity, which both units depend on for
force feedback. So only logic-level signals cross the cable to the
key-turner unit (step/dir/enable + UART for the stall threshold) plus
motor power — a 6-8 conductor cable with a small keyed connector
(e.g. JST-XH) at each end, so the key-turner unit can be unplugged
for repositioning.

**Alignment**: the key-turner unit has an easier mounting job than the
dial unit — since the real key is already seated in socket #4 by hand
(step 1), the gripper only needs to land on the key's protruding bow,
a much bigger and more forgiving target than the ~8mm star holes the
dial unit has to register precisely.

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

Still open:
- [ ] Key bow dimensions (width, thickness, how far it protrudes from
      the socket face) — needed to design the key-turner's gripper.
      `cad/key_turner_housing.scad` v0.1 sidesteps this with an
      adjustable clamp rather than a fitted pocket — see
      `docs/housing_decisions.md` — but the clamp's own working range
      (9mm slot) still needs the real bow checked against it.
- [ ] Center-to-center spacing between the 3 dial holes (or a simple
      coordinate layout) — needed to place the 3 motors in the dial
      unit's frame. Get this as plain numbers rather than read off
      ruler photos — same reasoning as the v0.1 bore-diameter mistake
      in `docs/decisions.md`: a caliper/tape number beats pixel-peeping.
      `cad/dial_unit_housing.scad` v0.1 uses a 36mm placeholder read
      (by eye, not calipers) off `docs/photos/dial-holes-ruler-2.jpg`
      and `star-opening-tape-2.jpg` — good enough to build a first-pass
      model, explicitly NOT good enough to close this item. See
      `docs/housing_decisions.md` for the full readout and the real
      NEMA17-body-collision problem that spacing surfaced.
- [ ] Rough distance from the dial cluster to socket #4 (doesn't need
      precision — just enough to plan cable length between the two
      units, now that they're not one rigid frame). Same photos give
      ~55mm — see `docs/housing_decisions.md`. This one probably can be
      treated as answered, given the stated precision bar.
- [ ] Verify each dial wheel has a hard stop near position 1, for the
      homing move in step 4 to find.
- [ ] Torque/effort needed to turn each dial wheel and the key, to
      size motors and gearing.
- [ ] Whether the Fichet-Bauche "Complice" line has any known
      anti-manipulation relocking behavior, before running thousands
      of automated attempts.
