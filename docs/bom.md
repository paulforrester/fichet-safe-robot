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
| NEMA17 stepper motor — **STEPPERONLINE 55Ncm 2A, pack of 5** | 1 pack (5, one spare) | €55.42 | €55.42 | 3 for dial wheels, 1 for key-turner, 1 spare. Checked live on Amazon.fr 2026-09-29: 55Ncm/2A is essentially the same torque class as the ~59Ncm hedge target (headroom against the still-open torque/effort unknown, see below), and STEPPERONLINE is a genuinely reputable brand here — 661 ratings at 4.7★, #1 best seller in category. The 5-pack is also cheaper than buying 4 singles (€55.42 vs. ~€84.52), with the 5th motor as a spare rather than waste. Note from the listing: on some units the 2 middle motor wires are swapped from the expected color coding — easy fix (lift the connector's white pins and swap), just don't mistake it for a wiring fault elsewhere. |
| TMC2209 stepper driver module (StallGuard, UART) — **BigTreeTech TMC2209 V1.3, 5-pack w/ heatsinks** | 1 pack (5, one spare) | €35.99 | €35.99 | Checked live on Amazon.fr 2026-09-29, settled on this after ruling out two others: a no-name GERUI 2-pack whose reviews show a real failure pattern ("1 of 2 doesn't work," repeated across several countries), and a listing badged "TMC2209" whose actual product-variant names ("R3-V3-4988") and description described A4988 hardware instead — a mislabeled/wrong-part risk, not just a lesser board. BigTreeTech is an established brand in this exact space (makes the SKR/Octopus boards much of the 3D-printer Klipper/Marlin community runs) and this listing had 491 ratings at 4.5★, a real sample size. The 5-pack also solves the quantity problem in one order (4 needed + 1 spare) rather than splitting across sellers, and includes heatsinks. |
| Arduino Mega 2560 (or genuine-compatible clone) | 1 | €15–40 | €15–40 | Chosen over an Uno/Nano for having enough hardware UART capacity for this design. (Correction from the earlier "4 dedicated UARTs" reasoning: `Serial` is tied up by USB, and all 4 drivers now share one UART bus on `Serial2` via TMC2209's built-in multi-drop addressing — see `control/sequence.md`'s new wiring-plan section. The Mega is still the right pick, just for a slightly different reason.) A genuine board is pricier but avoids clone USB-chip driver headaches. |
| RAMPS 1.4 shield (for the Mega 2560) | 1 | €9–17 | €9–17 | Plugs directly onto the Mega; 5 StepStick-footprint sockets, same physical pinout as the BigTreeTech TMC2209 boards above — no soldering for the 3 local dial drivers, they plug straight in. Only 3 of its 5 sockets get used (X/Y/Z); the 4th driver (key-turner) is wired off-shield per the driver-placement rule. Well-established part, e.g. ARCELI (4.2★, 255 ratings, €9.99) or DollaTek (4.2★, 124 ratings, €8.99). |
| 1kΩ resistors | ~10 (need 4) | €2–4 for an assorted kit | €2–4 | One per TMC2209, between the Mega's UART TX pin and that driver's PDN_UART pin — standard single-wire UART wiring, needed even with all 4 sharing one bus. A generic resistor assortment kit is the easiest way to get these plus spares for other values you'll likely want. |

## Power

| Item | Qty | Est. unit price | Est. total | Notes |
|---|---|---|---|---|
| 12V DC power supply, 5A | 1 | €12–18 | €12–18 | Sized up from an earlier 3A estimate to match the higher-torque (2A/phase) motors above and avoid a reorder if all 4 motors draw current together — 4× 2A would be 8A peak, but they rarely all stall simultaneously, so 5A is a reasonable working budget with headroom, not a hard minimum. RAMPS 1.4 has its own screw-terminal power input, so no separate barrel jack adapter is needed — if the supply ends in a barrel plug, cut it off and wire the bare leads straight into RAMPS's terminal (or get a supply with bare leads/screw terminals to begin with). |

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

Called out explicitly since the goal is one order, not a string of
"oh, also need..." trips back to a supplier:

- **Small perfboard or a couple of 2/3-pin screw terminal blocks**, for
  the key-turner unit — it has no shield to plug into, so its driver's
  STEP/DIR/ENABLE/DIAG/UART/power connections from the cable need a
  small hand-wired board rather than a socket.
- **Jumper wire assortment** (M-M, M-F, F-F) — for the RAMPS DIAG-to-
  endstop-header wiring, the UART tap to `Serial2`, and general
  point-to-point connections.
- **Soldering iron + solder**, if you don't already have one — needed
  for the key-turner unit's perfboard and any wire-to-connector joints.
- **A basic multimeter**, if you don't already have one — useful for
  checking continuity on the inter-unit cable and current-limit setup
  on the drivers.
- Heat shrink tubing, small assortment
- USB cable for the Arduino Mega (type depends on the board — check
  before ordering; often USB-B, sometimes USB-C on clones)

## Rough total

Core electronics (motors, drivers, Mega, RAMPS shield, resistors — all
now priced against real listings) + power + cable/connectors + filament
+ optional AS5600 and switch: **roughly €150–245**, plus €0 for
mounting (magnets already on hand), plus whatever's missing from the
prototyping-basics list above (perfboard, jumper wires, soldering iron,
multimeter — skip anything already owned).

## Single-order readiness

Everything on this list is safe to order in one go now — motors, driver
5-pack, Mega, RAMPS shield, resistors, power supply, cable/connectors,
filament, and the prototyping-basics checklist above. The only
remaining open item, torque/effort to turn each dial wheel and the key,
is hedged rather than blocking: the higher-torque NEMA17 pick and the
5A supply above both build in headroom against an unmeasured load, so
the plan is to order now and only revisit if bench testing shows it
genuinely isn't enough — at which point gearing, not a different motor
class, is the likely fix.
