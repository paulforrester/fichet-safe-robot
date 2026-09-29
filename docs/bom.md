# Bill of materials

What to buy, based on decisions locked in so far (two-unit architecture,
StallGuard force feedback on all 4 motors — see `control/sequence.md` and
`docs/decisions.md`). Prices are rough EUR estimates for common hobbyist
parts (Amazon.fr / AliExpress / RobotShop-class pricing as of late 2026) —
**verify at purchase time**, they weren't pulled from a live listing.

Quantities assume the confirmed layout: 3 dial motors + 1 key-turner motor
= 4 motors total, 4 drivers total (one per motor, co-located — see the
driver-placement rationale in `control/sequence.md`).

## Core electronics — locked in

| Item | Qty | Est. unit price | Est. total | Notes |
|---|---|---|---|---|
| NEMA17 stepper motor | 4 | €8–15 | €32–60 | 3 for dial wheels, 1 for key-turner. Any standard NEMA17 (e.g. 1.5–1.7A/phase, 200 steps/rev) works to start — torque sizing is a still-open item (see below), so don't buy a large batch yet in case a stronger/weaker motor turns out to be needed. |
| TMC2209 stepper driver module (StallGuard, UART) — **Adafruit 6121 breakout** | 4 | €14.40 | ~€58 | Checked live on Amazon.fr 2026-09-29: the Adafruit board (genuine, well-documented, UART to 1/256 microstepping, screw terminals) over a cheaper no-name (GERUI) 2-pack — that clone's reviews show a real failure pattern ("1 of 2 doesn't work," repeated across several countries, one report of a board failing outright), which isn't worth the ~€8/unit saved on a part this build depends on for force feedback, especially the one buried in the harder-to-debug remote key-turner unit. That Amazon.fr listing had **only 2 in stock** at check time — order the other 2 from adafruit.com or a distributor (Mouser/DigiKey) rather than waiting on restock. Add a heatsink per board (not included, a couple euros each). |
| Arduino Mega 2560 (or genuine-compatible clone) | 1 | €15–40 | €15–40 | Chosen over an Uno/Nano for its 4 hardware UART ports — lines up 1:1 with the 4 TMC2209s' UART needs for StallGuard config, no software-serial juggling. A genuine board is pricier but avoids clone USB-chip driver headaches. |

## Power

| Item | Qty | Est. unit price | Est. total | Notes |
|---|---|---|---|---|
| 12V DC power supply, ≥3A | 1 | €10–15 | €10–15 | 4× NEMA17 rarely all stall simultaneously at full current, so 3A is a reasonable starting budget; bump to 5A if bench testing shows brownouts. **Contingent on actual motor current draw once motors are picked** — revisit after the torque/effort open item is answered. |
| DC barrel jack or terminal block (power supply → dial-unit board) | 1 | €2–5 | €2–5 | Whatever matches the chosen supply's connector. |

## Inter-unit cable and connectors

Per `control/sequence.md`'s Mounting section: only logic signals + motor
power cross the cable, drivers stay local to each motor.

| Item | Qty | Est. unit price | Est. total | Notes |
|---|---|---|---|---|
| Multi-conductor cable, 6–8 conductor | ~1–2m | €3–8/m | €3–15 | Needs to carry step/dir/enable + UART (4 signal lines) plus motor power (2 lines) to the key-turner unit. A cut length of cheap 8-conductor alarm/CAT cable is plenty for signal-level current; keep motor-power conductors reasonably heavy gauge (22 AWG or better) since that's actual motor current, not just logic. |
| JST-XH connector pair (or similar keyed connector), 8-pin | 2 | €1–3 | €2–6 | One pair per end, so the key-turner unit can be unplugged for repositioning as noted in the mounting doc. |

## Filament (final motorized coupler only — not the hand-test keys)

| Item | Qty | Est. price | Notes |
|---|---|---|---|
| PETG-CF or nylon filament, small spool | 1 | €25–40 | Wear-resistance mitigation from `docs/decisions.md`'s closed tooth-geometry decision — only needed for the coupler that will actually do the ~8,000-attempt motorized search, not the plain-PETG hand-test keys already printed. |
| Hardened (steel/ruby-tipped) nozzle, if not already owned | 1 | €10–20 | CF-filled filament is abrasive and will wear a brass nozzle quickly. Skip if going with plain nylon instead of PETG-CF. |

## Mounting — resolved, nothing to buy

| Item | Qty | Est. price | Notes |
|---|---|---|---|
| Neodymium disc magnets, 2mm×8mm | already on hand (~100) | €0 | Door confirmed ferrous 2026-09-29 (both body and door), so magnets are the mounting method. Paul already has enough on hand from a prior print project, which also worked out the press-fit pocket geometry to reuse: **8.00mm diameter × 1.9mm depth** per magnet, in both units' mounting faces. No purchase needed. |

## Optional / contingency

| Item | Qty | Est. unit price | Est. total | Notes |
|---|---|---|---|---|
| AS5600 magnetic encoder breakout | 1 | €2–5 | €2–5 | Only needed if bench testing shows the printed coupler slipping under torque on key-4's angle count. Cheap enough to buy speculatively; `control/sequence.md` flags it as an easy later add-on rather than a day-one requirement. |
| Momentary pushbutton (dialing-trigger switch) | 1 | €1–2 | €1–2 | For "triggered by a physical switch" in the operating sequence, if that's preferred over a serial/USB command to start a run. |

## Prototyping basics (skip anything already on hand)

- Breadboard or perfboard for the dial-unit electronics
- Jumper wires (M-M, M-F)
- Heat shrink tubing, small assortment
- USB cable for the Arduino Mega (type depends on the board — check before ordering)

## Rough total

Core electronics + power + cable/connectors + filament + optional AS5600
and switch: **roughly €160–250** (bumped up from the earlier rough
estimate now that the driver line is priced against a real listing —
Adafruit boards at €14.40 each rather than a €4–7 generic estimate),
plus €0 for mounting (magnets already on hand) and anything already on
hand (breadboard, jumper wires, etc.).

## Before ordering, worth resolving first

Buying the motors now is reasonable — NEMA17 is a safe generic starting
point — but one open item from `control/sequence.md` could still change
this list once answered:

- **Torque/effort to turn each dial wheel and the key** — if it turns out
  to need much more torque than a standard NEMA17 delivers, a geared
  stepper or a gear-reduction print becomes part of the BOM.

Everything else on this list (drivers, MCU, cable, filament, mounting)
is settled and safe to order now.
