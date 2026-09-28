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

## Mounting

Robot attaches to the door face over the 4 sockets — magnets or
double-stick tape, leaning toward magnets if the door face is ferrous
(likely, but worth confirming). Magnet pockets can be built directly
into the printed frame once the socket layout is measured.

## Operating sequence

1. Real key inserted into hole 4 (manual, one-time per session).
2. Robot frame aligned over all 4 holes and attached to the door.
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

## Open items (measurements/verification for tomorrow)

- [ ] Socket #4's profile — same 8-tooth spline as the 3 dial sockets,
      or a different real-key shape?
- [ ] Physical layout of all 4 holes (photo with a ruler is enough for
      a first pass)
- [ ] Verify each dial wheel has a hard stop near position 1, for the
      homing move in step 4 to find
- [ ] Torque/effort needed to turn each dial wheel and the key, to
      size motors and gearing
- [ ] Whether the door face over the sockets is ferrous (for magnet
      mounting)
- [ ] Whether the Fichet-Bauche "Complice" line has any known
      anti-manipulation relocking behavior, before running thousands
      of automated attempts
