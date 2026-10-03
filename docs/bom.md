# Bill of materials

What to buy, based on decisions locked in so far (two-unit architecture,
StallGuard force feedback on all 4 motors — see `control/sequence.md` and
`docs/decisions.md`). Prices are rough EUR estimates for common hobbyist
parts (Amazon.fr / AliExpress / RobotShop-class pricing as of late 2026) —
**verify at purchase time**, they weren't pulled from a live listing.

Quantities assume the confirmed layout: 3 dial motors + 1 key-turner motor
= 4 motors total, 4 drivers total (one per motor, co-located — see the
driver-placement rationale in `control/sequence.md`).

## Order status (as of 2026-09-29)

Four orders placed 2026-09-29, checked against every line below:

| # | Vendor | Total (incl. VAT) | Contents |
|---|---|---|---|
| 1 | Amazon.fr | €46.81 | PCB/perfboard kit, AS5600 encoder ×4, 12V/5A power supply, heat shrink tube assortment |
| 2 | Amazon.fr | €286.52 | TMC2209 drivers ×5, shielded 6-conductor cable (18 ft), RAMPS 1.4 shield, Arduino Mega 2560, M–M jumper wires ×2 kits, 1kΩ resistors ×100, heat gun, soldering station, NEMA17 motors ×5, USB-C→B cable, momentary pushbuttons ×12 |
| 3 | Amazon.fr | €13.99 | Phoenix 5.08mm 8-pin screw-terminal connectors (substituted for the JST-XH spec below) |
| 4 | Bambu Lab | €428.42 (order also includes general printer supplies not on this BOM) | PETG-CF filament (1kg), tungsten carbide hotend — plus PETG Basic ×2, PLA Basic ×2, and a Bambu Lab AMS 2 Pro, none of which are BOM items |

Status is marked inline in each table below: ✅ ordered, ⬜ still to buy.

**Still to buy:**
- **Multimeter** — on the prototyping-basics checklist, not in any order.
- **F–F / M–F jumper wires** — both jumper-wire items ordered are M–M only; the RAMPS DIAG-to-endstop-header wiring and other point-to-point hookups will likely need female-ended jumpers too.
- **Solder wire** (consumable) — unconfirmed whether it's bundled with the Yofuly soldering station kit; check contents on arrival and buy separately if not included.

**Substitution to be aware of:** the JST-XH 8-pin connector pair specified below was replaced with a Phoenix-style 5.08mm screw-terminal 8-pin connector (Order 3). Still detachable and keyed for the same purpose (unplugging the key-turner unit), just a different connector family than originally planned — flagging in case it wasn't deliberate, otherwise no action needed.

**Housing design note (nothing to order):** `cad/dial_unit_housing.scad` needs to bridge a several-mm parallel offset between each dial motor and its coaxial coupler — the real dial-hole spacing is too tight for 3 full-size NEMA17 bodies to sit directly behind their sockets. Originally flagged here as a need for 3x off-the-shelf flexible shaft couplers; as of the v0.2 housing revision this is instead a **printed Oldham coupler** (rigid sliding joint, no bought part) — see `docs/housing_decisions.md`. No BOM impact beyond using the PETG-CF already on hand for the wear-facing hub parts.

## Core electronics — locked in

| Item | Qty | Est. unit price | Est. total | Status | Notes |
|---|---|---|---|---|---|
| NEMA17 stepper motor — **STEPPERONLINE 55Ncm 2A, pack of 5** | 1 pack (5, one spare) | €55.42 | €55.42 | ✅ Ordered (Order 2, €55.42) | 3 for dial wheels, 1 for key-turner, 1 spare. Checked live on Amazon.fr 2026-09-29: 55Ncm/2A is essentially the same torque class as the ~59Ncm hedge target (headroom against the still-open torque/effort unknown, see below), and STEPPERONLINE is a genuinely reputable brand here — 661 ratings at 4.7★, #1 best seller in category. The 5-pack is also cheaper than buying 4 singles (€55.42 vs. ~€84.52), with the 5th motor as a spare rather than waste. Note from the listing: on some units the 2 middle motor wires are swapped from the expected color coding — easy fix (lift the connector's white pins and swap), just don't mistake it for a wiring fault elsewhere. |
| TMC2209 stepper driver module (StallGuard, UART) — **BigTreeTech TMC2209 V1.3, 5-pack w/ heatsinks** | 1 pack (5, one spare) | €35.99 | €35.99 | ✅ Ordered (Order 2, €35.99) | Checked live on Amazon.fr 2026-09-29, settled on this after ruling out two others: a no-name GERUI 2-pack whose reviews show a real failure pattern ("1 of 2 doesn't work," repeated across several countries), and a listing badged "TMC2209" whose actual product-variant names ("R3-V3-4988") and description described A4988 hardware instead — a mislabeled/wrong-part risk, not just a lesser board. BigTreeTech is an established brand in this exact space (makes the SKR/Octopus boards much of the 3D-printer Klipper/Marlin community runs) and this listing had 491 ratings at 4.5★, a real sample size. The 5-pack also solves the quantity problem in one order (4 needed + 1 spare) rather than splitting across sellers, and includes heatsinks. |
| Arduino Mega 2560 (or genuine-compatible clone) | 1 | €15–40 | €15–40 | ✅ Ordered (Order 2, genuine Arduino Mega 2560 REV3, €49.19) | Chosen over an Uno/Nano for having enough hardware UART capacity for this design. (Correction from the earlier "4 dedicated UARTs" reasoning: `Serial` is tied up by USB, and all 4 drivers now share one UART bus on `Serial2` via TMC2209's built-in multi-drop addressing — see `control/sequence.md`'s new wiring-plan section. The Mega is still the right pick, just for a slightly different reason.) A genuine board is pricier but avoids clone USB-chip driver headaches — went genuine, hence €49.19 vs. the €15–40 estimate. |
| RAMPS 1.4 shield (for the Mega 2560) | 1 | €9–17 | €9–17 | ✅ Ordered (Order 2, Fasizi RAMPS 1.4, €10.99) | Plugs directly onto the Mega; 5 StepStick-footprint sockets, same physical pinout as the BigTreeTech TMC2209 boards above — no soldering for the 3 local dial drivers, they plug straight in. Only 3 of its 5 sockets get used (X/Y/Z); the 4th driver (key-turner) is wired off-shield per the driver-placement rule. Well-established part, e.g. ARCELI (4.2★, 255 ratings, €9.99) or DollaTek (4.2★, 124 ratings, €8.99). |
| 1kΩ resistors | ~10 (need 4) | €2–4 for an assorted kit | €2–4 | ✅ Ordered (Order 2, Innfeeltech 1K ohm ×100, €6.99) | One per TMC2209, between the Mega's UART TX pin and that driver's PDN_UART pin — standard single-wire UART wiring, needed even with all 4 sharing one bus. Ordered a 100-pack of the exact value rather than an assorted kit — covers this need plus plenty of spares. |

## Power

| Item | Qty | Est. unit price | Est. total | Status | Notes |
|---|---|---|---|---|---|
| 12V DC power supply, 5A | 1 | €12–18 | €12–18 | ✅ Ordered (Order 1, ledmo 12V/5A-6A, €14.98) | Sized up from an earlier 3A estimate to match the higher-torque (2A/phase) motors above and avoid a reorder if all 4 motors draw current together — 4× 2A would be 8A peak, but they rarely all stall simultaneously, so 5A is a reasonable working budget with headroom, not a hard minimum. RAMPS 1.4 has its own screw-terminal power input, so no separate barrel jack adapter is needed — if the supply ends in a barrel plug, cut it off and wire the bare leads straight into RAMPS's terminal (or get a supply with bare leads/screw terminals to begin with). |

## Inter-unit cable and connectors

Per `control/sequence.md`'s Mounting section: only logic signals + motor
power cross the cable, drivers stay local to each motor.

| Item | Qty | Est. unit price | Est. total | Status | Notes |
|---|---|---|---|---|---|
| Multi-conductor cable, 6–8 conductor | ~1–2m | €3–8/m | €3–15 | ✅ Ordered (Order 2, QUARKZMAN 22AWG shielded, 6-conductor, 18ft/~5.5m, €23.69) | Needs to carry step/dir/enable + UART (4 signal lines) plus motor power (2 lines) to the key-turner unit. Ordered length (~5.5m) is well over the 1–2m estimate — fine as a bulk roll, just explains the higher line cost than estimated. Shielded, 22AWG — heavier gauge than the "cheap alarm cable" fallback originally considered, comfortably covers motor current. |
| JST-XH connector pair (or similar keyed connector), 8-pin | 2 | €1–3 | €2–6 | ⚠️ Substituted (Order 3, Ausi 5.08mm 8-pin Phoenix screw-terminal connectors, €13.99) | One pair per end, so the key-turner unit can be unplugged for repositioning as noted in the mounting doc. What arrived is a Phoenix-style screw-terminal connector rather than JST-XH — still detachable and keyed, arguably more robust for the motor-power conductors, but a different part than specified here. Flagging for awareness, not necessarily a problem. |

## Filament (final motorized coupler only — not the hand-test keys)

| Item | Qty | Est. price | Status | Notes |
|---|---|---|---|---|
| PETG-CF or nylon filament, small spool | 1 | €25–40 | ✅ Ordered (Bambu Lab, PETG-CF Black 1kg, €33.27) | Wear-resistance mitigation from `docs/decisions.md`'s closed tooth-geometry decision — only needed for the coupler that will actually do the ~8,000-attempt motorized search, not the plain-PETG hand-test keys already printed. PETG-CF branch chosen (not nylon). |
| Hardened (steel/ruby-tipped) nozzle, if not already owned | 1 | €10–20 | ✅ Ordered (Bambu Lab, Tungsten Carbide Hotend – H2/P2S/X2D, €60.49) | CF-filled filament is abrasive and will wear a brass nozzle quickly. What was ordered is a full tungsten-carbide hotend assembly (H2D-specific) rather than just a nozzle tip, hence the higher cost vs. the €10–20 estimate — same purpose, tungsten carbide is even more wear-resistant than ruby-tipped. |

## Mounting

| Item | Qty | Est. price | Status | Notes |
|---|---|---|---|---|
| Neodymium disc magnets, 2mm×8mm | already on hand (~100) | €0 | ✅ On hand, nothing to buy | Door confirmed ferrous 2026-09-29 (both body and door), so magnets are the mounting method. Paul already has enough on hand from a prior print project, which also worked out the press-fit pocket geometry to reuse: **8.00mm diameter × 1.9mm depth** per magnet, in both units' mounting faces. No purchase needed. |
| M3 brass heat-set threaded inserts (4.2mm OD, ~5mm length) | 3 (+ spares) | €8.99 | ✅ Ordered (HANGLIFE M3 knurled brass insert kit, 100pcs, Amazon.fr "HANGLIFE Thread Inserts for Hot Melting, M3 Threaded Insert", €8.99) | New with `dial_unit_housing.scad` v0.3/v0.4 (see `docs/housing_decisions.md`) — the housing's `frame()` was split into 3 bolt-together tiers (`front_assembly()` / `rear_assembly()` / `electronics_deck()`) to fix unsupported bridges Bambu Studio flagged, and a real fouled-motor collision on the printed v0.3 part. One insert per standoff leg, 3 legs joining front-to-rear (`front_standoff_legs()`). ~5mm length fits the 6mm-deep leg bore with a little clearance; a small multi-size kit covers this and is useful elsewhere. **Qty dropped from 6 to 3** by the 2026-10-03 motor-sled rework: the OTHER 3 (rear-to-deck, `deck_standoff_legs()`) switched to a direct M5 self-tap screw instead of M3+insert (see `docs/housing_decisions.md`) — this kit is still needed for the front joint, `electronics_deck()`'s Mega posts, and general shop stock. |
| M3×8 DIN 912 / ISO 4762 socket-head cap screws | 3 (+ spares) | €12.99 | ✅ Ordered (Taiss M3 screw kit, 550pcs, M3x6/8/12/16/20/25/30mm, 304 stainless, hex socket head, Amazon.fr "Taiss 550pcs M3 Screw Kit", €12.99) | Pairs with the inserts above — 3 through `motor_plate()`'s counterbored holes into the front legs' inserts (`front_standoff_legs()`). Machine-thread, not self-tapping (threads into the brass insert). **M3x8, not x10/x12**: a longer screw bottoms on the leg's solid floor before its head seats flush — max before that happens is ~8.8mm — see the print notes in `dial_unit_housing.scad` for the math. **Qty dropped from 6 to 3**: the deck joint now uses M5 (see row below), so only the front joint's 3 screws come from this kit — the kit's other 6 lengths (M3x6/12/16/20/25/30) are still useful elsewhere in the build. |
| M6 self-tapping screws, countersunk head, ~13–16mm (M6x15 nominal) | 3 (+ spares) | €0 | ✅ On hand (Paul's existing M5/M6 assortment box, same one bench-tested in `standoff_screw_fit_test.scad`) | New with the 2026-10-03 motor-sled rework — replaces M3+insert for `deck_standoff_legs()` (rear-to-deck joint) only. **M6, not M5**: corrected after `standoff_screw_fit_test.scad`'s real bench results (logged just above/below in `docs/housing_decisions.md`) showed M5 didn't self-tap at all, while M6 at a 5.4mm pilot worked cleanly. Self-taps directly into that 5.4mm pilot hole (`m6_selftap_pilot_d`), no insert needed. Countersunk chosen over pan head for repeatable, self-centering shaft alignment — both head styles tested fine. **Caveat**: the 5.4mm pilot was only bench-tested in a thicker-walled test coupon than the real leg (`leg_dia` 12mm leaves ~3.3mm wall here, vs. ~6.3mm tested) — thread the first one in by hand, not a power driver, and check for cracking. No purchase needed if the on-hand assortment box has countersunk M6 in this length range; if not, buy a small pack. |

## Optional / contingency

| Item | Qty | Est. unit price | Est. total | Status | Notes |
|---|---|---|---|---|---|
| AS5600 magnetic encoder breakout | 1 | €2–5 | €2–5 | ✅ Ordered (Order 1, AS5600 ×4, €9.86) | Only needed if bench testing shows the printed coupler slipping under torque on key-4's angle count. Cheap enough to buy speculatively; `control/sequence.md` flags it as an easy later add-on rather than a day-one requirement. Ordered 4 rather than 1 — extra spares. |
| Momentary pushbutton (dialing-trigger switch) | 1 | €1–2 | €1–2 | ✅ Ordered (Order 2, Lewttyer 7mm pushbutton ×12, €10.90) | For "triggered by a physical switch" in the operating sequence, if that's preferred over a serial/USB command to start a run. Ordered a 12-pack rather than 1 — extra spares. |

## Prototyping basics (skip anything already on hand)

Called out explicitly since the goal is one order, not a string of
"oh, also need..." trips back to a supplier:

- ✅ **Small perfboard or a couple of 2/3-pin screw terminal blocks** — Ordered (Order 1, RUNCCI-YUN 82pc double-sided PCB kit, €12.98; also see the Phoenix screw-terminal connectors in Order 3, which can double as terminal blocks). For the key-turner unit — it has no shield to plug into, so its driver's STEP/DIR/ENABLE/DIAG/UART/power connections from the cable need a small hand-wired board rather than a socket.
- ⚠️ **Jumper wire assortment** (M-M, M-F, F-F) — Partially ordered: two M–M kits (Order 2, GTIWUNG 150pcs + a 560pc breadboard kit, €11.99 + €8.99), but **no M-F or F-F jumpers**. Still needed for the RAMPS DIAG-to-endstop-header wiring, the UART tap to `Serial2`, and general point-to-point connections — worth a small follow-up order.
- ⚠️ **Soldering iron + solder** — Iron ordered (Order 2, Yofuly 75W soldering station, €49.99); solder wire itself unconfirmed — check what's in the kit on arrival.
- ⬜ **A basic multimeter** — **Not ordered.** Useful for checking continuity on the inter-unit cable and current-limit setup on the drivers.
- ✅ Heat shrink tubing, small assortment — Ordered (Order 1, 800-piece assortment, €8.99).
- ✅ USB cable for the Arduino Mega — Ordered (Order 2, GIANAC USB-C→USB-B, 2m, €5.99) — matches the genuine Mega 2560's USB-B port, assuming USB-C on the computer end.

Not on the original list, added during ordering: a heat gun (Order 2, €16.39) — useful for shrinking the heat-shrink tubing above.

## Rough total

Core electronics (motors, drivers, Mega, RAMPS shield, resistors — all
now priced against real listings) + power + cable/connectors + filament
+ optional AS5600 and switch: **roughly €150–245**, plus €0 for
mounting (magnets already on hand), plus whatever's missing from the
prototyping-basics list above (perfboard, jumper wires, soldering iron,
multimeter — skip anything already owned).

**Actual spend so far (2026-09-29, across all four orders): €775.74**,
including €60.49 for the tungsten-carbide hotend and €291.43 for the
AMS 2 Pro / general filament restock — both well above the original core
estimate since they weren't priced against real listings when this total
was first drafted, and the AMS 2 Pro isn't a BOM item at all.

## Single-order readiness

Everything on this list has now been ordered across four orders placed
2026-09-29, **except**:
- a multimeter (not ordered anywhere)
- M-F / F-F jumper wires (only M-M was ordered)
- solder wire (unconfirmed — check the soldering station kit on arrival)

The JST-XH connector was substituted with a Phoenix screw-terminal
connector (see Order status above) — not a gap, just a part swap worth
noting.

The only previously-open item, torque/effort to turn each dial wheel and
the key, is still hedged rather than blocking: the higher-torque NEMA17
pick and the 5A supply above both build in headroom against an
unmeasured load, so the plan is to bench-test once hardware arrives and
only revisit if that headroom genuinely isn't enough — at which point
gearing, not a different motor class, is the likely fix.
