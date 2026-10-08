# Wiring harness — Mega 2560 + RAMPS 1.4 + 4 × BTT TMC2209 V1.3

> **Revision 2026-10-08.2** · all four drivers on the RAMPS (key in E0); UART pigtail replaces the hub board · log: `docs/revisions.md`

Written 2026-10-06 (cloud session, no hardware). Everything below is from the
sources listed at the bottom; anything I could not establish is marked
**ASSUMPTION** or **VERIFY** and gets a bench step in `control/bringup.md`.
The firmware (`control/firmware/`) is built on this pin map
(`safe_robot/pins.h`).
Decision log for this file is at the end (most recent first).

**Revision 2026-10-08.1 (2026-10-08):** the key driver moved from a remote
board at the key turner into the RAMPS **E0** socket. Sections 3.1, 3.5, 3.6
and 6 (the remote board and its cable) are retired; section 4 is now the key
motor's own cable; section 5 (hub) shrinks to the UART junction. Reasoning in
the decision log, 2026-10-08.

**Revision 2026-10-08.2 (2026-10-08):** the hub board is replaced by the
**UART pigtail** (section 5): six leads with female Dupont ends, R1 in line in
the TX2 lead, one solder splice. Same circuit. Its driver leads clip onto the
**top of each driver's RX pin**, and DIAG is a plain jumper on the top of the
DIAG pin (no soldering on the drivers; two snips each). Decision log,
2026-10-08 (pigtail) and 2026-10-08 (evening).

## Summary — what was decided

1. **One UART bus, one 1 kΩ resistor in total**: Mega TX2 (D16) → 1 kΩ → bus;
   RX2 (D17) straight on the bus; every driver's PDN_UART straight on the bus.
   This is the datasheet's own circuit (TMC2209 DS Fig. 4.1). *Correction* of
   `sequence.md`, which said one resistor per driver. Built as the **UART
   pigtail** (section 5, revision 2026-10-08.2).
2. **UART needs no soldering**: the BTT V1.3's PDN_UART pin (**RX**, the 4th
   pin) stands up through the top of the driver as a tall pin (Paul's drivers,
   2026-10-08). Clip a female Dupont onto the **top of each driver's RX pin**
   (section 3.3). Leave the MS3 jumper **off** (RX also sits in the socket's MS3
   position). *Revision 2026-10-08.2*: until then the tap was the RAMPS MS3
   jumper pin under the driver, which was never checked for room.
3. **Addresses by RAMPS jumpers**: X = none (addr 0), Y = MS1 (addr 1),
   Z = MS2 (addr 2), **E0 = MS1 + MS2 (addr 3, the key)**.
   **Never fit an MS3 jumper** (it would tie the UART line to 5 V).
4. **DIAG: two snips per driver, no soldering** (all four drivers): on Paul's
   V1.3s the two EN-end pins (DIAG and its neighbour) stick out both above
   and below the board. Cut the **bottom** ends flush, so nothing points down
   at the RAMPS, and clip a plain F–F jumper onto the **top of the DIAG pin**
   (section 3.3). *Revision 2026-10-08.2*: until then the docs assumed the
   pins pointed down only and had a lead soldered to the DIAG joint.
5. **DIAG pins moved to interrupt-capable Mega pins** (D2, D3, D18, D19).
   *Correction*: dial B's DIAG was planned on Y_MIN (D14), which has no
   `attachInterrupt` on the Mega, and the datasheet says DIAG is a *pulse*.
   Y_MIN now takes the start/stop button.
6. **Between the units runs only the key motor's own cable** (~1 m, 4 wires,
   from the motor to the RAMPS E0 motor header). *Revision 2026-10-08.1*:
   until then a 6-conductor cable carried 12 V, GND, 5 V, STEP, UART and DIAG
   to a remote driver board (sections 3.1, 4 and 6, now retired).
7. **The key driver has its own STEP, DIR and EN** from the E0 socket (D26,
   D28, D24), like the dial drivers. The UART direction workaround
   (GCONF.shaft) and the TOFF disable are gone (firmware v0.4).
8. **Fusing**: RAMPS's own 5 A polyfuse feeds all four drivers (every socket's
   VMOT). *Revision 2026-10-08.1*: the hub's 1.1 A fuse on a separate key
   branch is gone with the branch. 12 V goes from the PSU adapter straight
   into the RAMPS "5A" terminal; nothing else carries it.
9. **Currents**: dial drivers 1.0 A RMS (hold 0.5 A) until the dial torque is
   measured; key driver starts at 0.6 A RMS and is then set to 2 × the measured
   minimum that turns the key (bench stage 5).
10. **Power order**: everything plugged with power off; USB first, then 12 V;
    12 V off first. Never plug or unplug a motor with 12 V on (the key motor
    included: its cable runs between the units).

## 1. Pin map

Dial naming follows `cad/dial_unit_housing.scad`: **A = top-left, B =
top-right, C = bottom** (standing in front of the safe).

| Function | Mega pin | Where to connect | Source / note |
|---|---|---|---|
| Dial A STEP / DIR / EN | D54 (A0) / D55 (A1) / D38 | RAMPS **X** socket (driver plugs in) | Marlin `pins_RAMPS.h` X_STEP/DIR/ENABLE; KiCad port nets `/X-STEP` etc. |
| Dial B STEP / DIR / EN | D60 (A6) / D61 (A7) / D56 (A2) | RAMPS **Y** socket | Marlin Y_*; KiCad `/Y-*` |
| Dial C STEP / DIR / EN | D46 / D48 / D62 (A8) | RAMPS **Z** socket | Marlin Z_*; KiCad `/Z-*` |
| Dial A DIAG | D3 (INT, `attachInterrupt` no. 1) | **X_MIN** header, S pin | Marlin X_MIN_PIN 3 |
| Dial B DIAG | D2 (INT, no. 0) | **X_MAX** header, S pin | Marlin X_MAX_PIN 2 — *moved from Y_MIN* |
| Dial C DIAG | D18 (INT, no. 5) | **Z_MIN** header, S pin | Marlin Z_MIN_PIN 18 |
| Key STEP / DIR / EN | D26 / D28 / D24 | RAMPS **E0** socket (driver plugs in) | Marlin E0_STEP/DIR/ENABLE (`pins_RAMPS.h`) — *rev 2026-10-08.1* |
| Key DIAG | D19 (INT, no. 4) | **Z_MAX** header, S pin (F–F jumper from the top of the E0 driver's DIAG pin) | Marlin Z_MAX_PIN 19 |
| UART TX2 | D16 | **AUX-4 pin 18** ← pigtail lead TX2 (R1 1 kΩ in line) | Marlin: "Serial2 — TX2 = D16 RX2 = D17 (AUX4-18 and AUX4-17)" |
| UART RX2 | D17 | **AUX-4 pin 17** ← pigtail lead RX2 (to the splice) | same |
| Drivers' PDN_UART | — | top of the **RX pin** of the drivers in X, Y, Z **and E0** ← pigtail leads A, B, C, KEY | BTT V1.3 schematic: RX = `UART_RX` = PDN_UART |
| Start / stop button | D14 (input, pull-up) | **Y_MIN** header: S and − pins | Marlin Y_MIN_PIN 14 (no interrupt needed) |
| Spare (was 5 V/GND for the remote board until rev 2026-10-08.1) | 5 V, GND | Y_MAX header + and − pins | KiCad: endstop pin 3 = 5 V, pin 2 = GND |
| Status LED | D13 | on-board LED | Marlin LED_PIN 13 |
| Spare | D15 | Y_MAX header, S pin | — |
| Spare (key STEP until rev 2026-10-08.1) | D23 | AUX-4 pin 16 | — |
| USB serial (log) | D0 / D1 | USB | keep free |

Pins to avoid: D0/D1 (USB). D20/D21 carry 4.7 kΩ pull-ups to 5 V on RAMPS
(KiCad R21/R22). Using D14/D15 and D18/D19 as plain I/O means `Serial3` and
`Serial1` can't be used — the firmware doesn't need them.

Interrupt numbers are from the Arduino AVR core's `digitalPinToInterrupt()` for
the Mega (`variants/mega/pins_arduino.h`): only D2, D3 and D18–D21 have one.

RAMPS endstop headers are 3 pins: **S** (signal), **−** (GND), **+** (5 V)
(KiCad port: pad 1 = signal, 2 = GND, 3 = VCC). RAMPS has no pull-up or filter
on these lines; the firmware uses the Mega's internal pull-up, so an unplugged
DIAG wire reads *high* = "stalled" and the firmware refuses to move (fail safe).

## 2. Drivers on RAMPS: placement, jumpers, UART tap

| RAMPS socket | Dial | MS1 jumper | MS2 jumper | MS3 jumper | UART address |
|---|---|---|---|---|---|
| X | A (top-left) | off | off | **off** | 0 |
| Y | B (top-right) | **on** | off | **off** | 1 |
| Z | C (bottom) | off | **on** | **off** | 2 |
| **E0** | **key** | **on** | **on** | **off** | **3** |
| E1 | empty | — | — | — | — |

- **E0 (rev 2026-10-08.1) — VERIFY on the bench**: E0's MS jumpers and MS3
  jumper pin are wired like X/Y/Z's (the netlist reading above covers every
  socket; E0 itself is confirmed only when the key driver answers `ping` at
  address 3 with MS1 = MS2 = 1).
- Address table: TMC2209 DS §3.4 "MS1/MS2" (p. 14): MS2,MS1 = GND,GND → 0;
  GND,VCC_IO → 1; VCC_IO,GND → 2; VCC_IO,VCC_IO → 3. MS1/MS2 have internal
  pull-downs (DS §2.2, "DI (pd)", p. 9); RAMPS adds 100 kΩ on MS1 (KiCad
  R3/R5/R6/R8/R10). A RAMPS jumper ties its pin to 5 V (KiCad: jumper pads
  2/4/6 = VCC, pads 1/3/5 = MS1/MS2/MS3 of the socket).
- **Driver orientation**: match the driver's EN, DIR, VM and GND corner pins to
  the RAMPS silkscreen. A reversed driver is destroyed (BTT manual,
  "Safety Precautions" 1).
- **UART tap**: the V1.3's header pins in the StepStick order are EN, MS1, MS2,
  **RX**, TX, CLK, STEP, DIR (BTT manual p. 5). Its schematic shows **RX =
  PDN_UART** (net `UART_RX`, chip pin 14) and **TX** connected to it only
  through **R10, which is not fitted** (marked NC). **Measured (Paul,
  2026-10-08):** RX to TX is open on his drivers (no continuity), so R10 is
  open as the schematic says. Paul's drivers have the RX, TX and CLK pins
  standing up through the top (tall pins; all five alike, Paul 2026-10-08),
  and a female Dupont on the top of RX grips and conducts (Paul checked
  continuity pin → far end of the lead). **The tap is the top of the RX
  pin** (revision 2026-10-08.2). Put nothing on TX or CLK.
- On the RAMPS, the RX pin also goes into the socket's MS3 hole, which leads
  only to that socket's MS3 jumper pad (KiCad net `U2.MS3 ↔ JP1.5`; each
  socket's MS3 is its own net, checked for all five sockets 2026-10-08, so
  the unused E1 block can't be used as a tap). With the MS3 jumper off,
  nothing else is on the line. *Until revision 2026-10-08.2* the tap was that
  MS3 jumper pin, under the seated driver.
- **Don't bridge R10 on any driver**: RAMPS ties the socket's RST and SLP
  pins together (KiCad net `U2.SLP ↔ U2.RST`), which on the V1.3 are TX and
  CLK. With R10 open, CLK sees only its 20 kΩ pull-down (BTT schematic R4) →
  internal clock, as the datasheet wants ("Tie to GND … for internal clock",
  DS §2.2). With R10 bridged, PDN_UART would be wired to CLK.
- RAMPS has a **10 kΩ pull-up on every EN line** (KiCad R16–R20), so the dial
  drivers stay disabled until the firmware drives EN low.

## 3. The open harness issues, resolved

### 3.1 Conductor count — retired (revision 2026-10-08.1)

This section chose which six signals the inter-unit cable carried to a remote
key driver (EN and DIR tied low there, direction by GCONF.shaft). With the
key driver on the RAMPS (E0) there is no such cable: only the key motor's own
cable runs between the units (section 4). The old text is in git history
(`main` at `76a4167`).

### 3.2 UART resistor topology

**Choice: one 1 kΩ in total, between TX2 and the bus; RX2 on the bus; all four
PDN_UART pins on the bus.** DS §4.3 Fig. 4.1 (p. 20) shows exactly this: master
TXD → 1 kΩ → line; RXD and every node's PDN_UART on the line; addresses by
MS1/MS2. The 1 kΩ lets a driver pull the line while TX2 idles high.
Consequences:

- The Mega receives its own transmissions (DS §4.4, p. 21: "all transmitted
  data also is received by the RXD input"). TMCStepper handles this: its read
  skips bytes until it sees the reply header `0x05 0xFF <reg>` (replies use
  master address 0xFF, DS p. 19) — `TMC2208Stepper::_sendDatagram()`, v0.7.3.
- Multi-node: set **SENDDELAY ≥ 2** on every driver (DS p. 19: "In a
  multi-node system, set SENDDELAY to min. 2 for all nodes"). The firmware does.
- Baud: 115200 (valid range 9000 baud to fCLK/16 = 750 k, DS p. 18).
- `sequence.md`'s "one resistor per driver" is corrected in place.

### 3.3 BTT TMC2209 V1.3 pin access on RAMPS

- **UART**: no soldering. A pigtail lead (section 5) clips onto the top of the
  driver's **RX** pin (section 2).
- **DIAG**: the V1.3 has extra pins at the EN end (BTT schematic header P1B
  lists INDEX, DIAG and VREF). On Paul's drivers (photos, 2026-10-08) the top
  edge reads, from the EN corner: the EN pin, a short unlabelled pin, an
  empty hole, then the pin with **"DIAG"** printed under it, next to the
  trimmer pot. Both fitted pins stick out **above and below** the board (Paul,
  all five drivers). BTT's manual shows them pointing down only ("BOTTOM
  (Factory default)", p. 6); Paul's are through-pins. **For all four drivers
  (X, Y, Z, E0), before fitting the heatsinks:**
  1. With flush cutters, cut the **bottom** ends of both EN-end pins off flush
     with the underside (or their plastic spacer). Seated, they would point
     down between the socket rows at the EN end. The RAMPS KiCad puts the MS
     jumper block toward the DIR end, so they're probably clear, but what's
     under them on Paul's Fasizi board isn't checked; cutting removes the
     question. Leave the top ends.
  2. A plain F–F jumper (~10 cm) from the **top of the DIAG pin** (the one
     next to the trimmer pot) to the S pin of that driver's endstop header
     (section 1): X_MIN (A), X_MAX (B), Z_MIN (C), Z_MAX (key).
  Put nothing on the other EN-end pin. *Until revision 2026-10-08.2* this was
  a soldered lead on the DIAG joint (the docs assumed down-only pins).
- **VERIFY**: which pin is DIAG. The firmware's `ping` prints the DIAG state
  both from the Mega pin and from the driver's own IOIN register; bench stage
  3 stalls the motor by hand and both must flip together.

### 3.4 Address strapping

Section 2 table. The firmware reads each driver's IOIN (MS1, MS2 bits and
VERSION, which must read 0x21 — DS IOIN, p. 25) and refuses to run if any
address doesn't answer or reports the wrong MS1/MS2.

### 3.5 Power and 5 V logic for the remote driver — retired (revision 2026-10-08.1)

The key driver now sits in E0 and gets VS (12 V, through RAMPS's 5 A
polyfuse: KiCad input terminal pin 3 → F1 MF-R500 → `+12V` → all socket VMOT
pins) and VIO (the RAMPS 5 V rail) from its socket, like the dial drivers,
with RAMPS's own 100 µF near the sockets. The remote board's 5 V-over-cable
and its two 100 µF capacitors (C1a, C1b) are gone. DS §3 (p. 11): "A minimum
capacity of 100µF near the driver is recommended"; the V1.3 itself only has
2 × 10 µF ceramic (BTT schematic C1/C2).

### 3.6 Mount for the remote board — retired (revision 2026-10-08.1)

No remote board, so no mount on the key turner.

## 4. Key motor cable (revision 2026-10-08.1)

The only connection between the units. The key motor's own cable (supplied
with the 17HE19-2004S, ~1 m, 4 wires and a connector) runs from the key
turner to the RAMPS **E0 motor header**, the same kind of 4-pin header the
dial motors plug into.

- **Length (Paul, 2026-10-08):** use the supplied cable as it is. If bench
  stage 5 shows the key's StallGuard reading too dull to tell the stop
  apart, shorten it. Standard practice (3D printers home with StallGuard on
  mainboard drivers over cables of this length) suggests 1 m is fine; not
  yet confirmed on this hardware.
- **Strain relief**: zip-tie it to the key turner within ~20 mm of the motor
  and to the electronics deck near the RAMPS, so a tug lands on the ties.
  Coil the spare length; keep it clear of the key cap's rotation.
- **Never plug or unplug it with 12 V on**: DS §3 "Attention" (p. 11) —
  energy from the motor coils goes back into the supply when a driver gets
  cut off from its motor.
- **Wire order**: as for the dial motors (`docs/manual.md` §2.9): on some
  17HE19-2004S the two middle wires are swapped. Symptom: the
  motor buzzes or jitters instead of turning. Fix it in the connector.
- *Until revision 2026-10-08.1* this section described a 6-conductor
  shielded cable with Phoenix 8-pin connectors to a remote driver board; see
  git history (`76a4167`).

## 5. UART pigtail — the UART junction (revision 2026-10-08.2)

The bus node and R1 are built into a small harness instead of a board
(Paul, 2026-10-08): six leads, each ending in a female Dupont, joined in one
solder splice. Drawing: `control/harness/uart_pigtail.svg`. Build steps:
`docs/manual.md` §2.5.

| Lead (tape label) | Female end goes on | Other end |
|---|---|---|
| **TX2** — R1 1 kΩ in line, ~3 cm from the female end | AUX-4 pin 18 (D16) | R1 → splice |
| **RX2** | AUX-4 pin 17 (D17) | splice |
| **A** | top of the RX pin, driver in X (dial A, addr 0) | splice |
| **B** | top of the RX pin, driver in Y (dial B, addr 1) | splice |
| **C** | top of the RX pin, driver in Z (dial C, addr 2) | splice |
| **KEY** | top of the RX pin, driver in E0 (key, addr 3) | splice |

- **The splice is the bus node** of DS Fig. 4.1: R1's far end, RX2 and the
  four PDN_UART leads. Heat shrink over the joint and over R1; zip-tie the
  splice to the deck so the leads can't pull on it.
- **Leads**: six F–F jumpers with one end cut off each (or jumper halves if
  long enough), cut to the measured run from AUX-4 / each driver's RX pin to a
  splice near the middle of the RAMPS, plus a few cm.
- **Signals only**: no 12 V, 5 V or GND. The Mega and all four drivers share
  ground through the RAMPS.
- **Check before fitting** (multimeter, Ω): TX2 → RX2 ≈ 1 kΩ; TX2 → A, B, C,
  KEY ≈ 1 kΩ each; RX2 → A, B, C, KEY ≈ 0 Ω each.
- Each driver lead keeps its own female end, so a driver can still be
  unplugged (pull the lead off its RX pin first).

*Until revision 2026-10-08.2* this was a perfboard ("hub board") with male
pins for six F–F jumpers: the same circuit and the same six jumpers, but six
more plug-in joints (one at each hub pin) and a part to mount.
Before revision 2026-10-08.1 it also split 12 V to a fused key branch.

## 6. Remote driver board (key turner) — retired (revision 2026-10-08.1)

The key driver plugs into the RAMPS E0 socket instead (section 2). The
remote board's layout (6.1) and mount needs (6.2) are in git history
(`main` at `76a4167`).

## 7. Motor current settings

Sense resistors on the V1.3: **0.11 Ω** (BTT schematic R3/R5 "0R11"; visible as
"R110" on the board, manual p. 6). Current set by UART with the internal
reference (GCONF.I_scale_analog = 0), so the module's VREF pot doesn't matter
once the firmware is running. **Correction (2026-10-07):** it does after a
driver reset (its supply dipping), until the firmware notices: so every
driver's pot goes to minimum (decision log, 2026-10-07).
RMS current = (CS+1)/32 × VFS/(R_SENSE + 20 mΩ)/√2,
VFS = 0.325 V (vsense = 0) or 0.18 V (vsense = 1) (DS §9, p. 53). TMCStepper's
`rms_current()` implements this and switches vsense when CS would be < 16; the
datasheet asks for IRUN 8…31 in StealthChop (p. 42).

| Driver | Run (IRUN) | Hold (IHOLD) | Why |
|---|---|---|---|
| Dial A, B, C | **1.0 A RMS** (CS 17 → 0.99 A) | 0.5 A | `sequence.md`: ~1 A until dial torque is measured; the 2:1 gearing doubles what reaches the printed teeth |
| Key | **0.6 A RMS to start** (vsense=1, CS 18 → 0.58 A) | 0.3 A | measured key torque 0.07–0.08 N·m; want ~2×. Bench stage 5 finds the lowest current that still turns the key through its free travel; set 2 × that (torque ∝ current), max 1.0 A |
| Ceiling (firmware clamps) | 1.2 A | — | DS: 1.4 A RMS design guideline (p. 75); BTT: active cooling above 1.2 A |

**ASSUMPTION**: the motor's "2.0 A" rating is RMS per phase. Not confirmed
(vendor site unreachable from here); it only matters if we ever go above 1 A.

StealthChop (SPREAD open = StealthChop, DS §3.4; firmware also clears
GCONF.en_spreadCycle) — StallGuard4 only works in StealthChop (DS §11).

## 8. Power-up and power-down order, fusing

1. **All connections with power off** (USB unplugged, 12 V off).
2. **Before the first power-up, turn every driver's VREF pot to minimum**
   (decision log, 2026-10-07: a driver that resets runs on its pot until the
   firmware notices). *Revision 2026-10-08.1*: every driver, the key's
   included, now has its EN on a Mega pin with RAMPS's 10 kΩ pull-up, so all
   four stay off at power-up until the firmware enables them. (Before, the
   remote key driver's EN was tied low and it came on with 12 V, DS p. 52
   warning.)
   Expect the key to twitch by up to ±2 full steps (±3.6°) when the motor is
   first energised (DS p. 15: the motor pulls into the driver's step position
   at power-up).
3. **Power-up**: USB first (Mega + every driver's VIO), then 12 V. The firmware
   pings all 4 drivers and won't move anything until all answer — so it just
   waits for 12 V. (RAMPS also feeds 12 V to the Mega's VIN through a diode,
   KiCad D1, so the Mega runs without USB too. **The Mega's own barrel jack
   stays empty.** It feeds only VIN, and D1 conducts only from the RAMPS
   +12 V rail to VIN, so a supply there would never reach the drivers'
   VMOT (netlist: `/AM-VIN` = U1.VIN + D1 cathode only). USB first is so the logger sees
   the start.)
4. **Power-down**: 12 V off first, then USB.
5. **Fusing**: PSU (Ledmo HTY-1200500) 5 A max. RAMPS 5 A polyfuse (F1)
   feeds all four drivers (revision 2026-10-08.1). Four motors at their set
   currents stay well inside it: a stepper driver's supply current is below
   its coil current (chopper). *Until revision 2026-10-08.1* a 1.1 A PTC (for
   a while a 1.6 A glass fuse in a printed holder) on the hub fed a separate
   key branch; it went with the branch.
6. **Emergency stop**: pull the 12 V plug. The button (Y_MIN) pauses a run;
   `!` on the serial line aborts the current move and switches all drivers
   off.

## 9. Diagrams

- **`control/harness/schematic.pdf`: the full wiring schematic**, A4
  landscape sheets in colour, for printing. No text is below 8 pt. It is
  drawn from this file by `control/harness/schematic.py` (reportlab), and
  prints the project revision (`REVISION`) in every title block.
  **Regenerate it after any change here.**
- `control/harness/harness.yml` → `harness.svg` / `harness.png` (WireViz):
  the UART pigtail between the RAMPS pins and its splice, and the key motor
  cable to E0.
- `control/harness/overview.dot` → `overview.svg` (Graphviz): block diagram
  of everything in this file.
- `control/harness/uart_pigtail.py` → `uart_pigtail.svg` / `.png`: the
  UART pigtail (revision 2026-10-08.2; replaced `hub_board.py`).
- `control/harness/ramps_and_uart.md`: one bench sheet of everything fitted
  to the RAMPS, and the pigtail (was `ramps_and_hub.md`).

Regenerate: `python3 control/harness/schematic.py` (needs `pip install
reportlab`), `wireviz control/harness/harness.yml`,
`dot -Tsvg control/harness/overview.dot -o control/harness/overview.svg` and
`python3 control/harness/uart_pigtail.py`. Then `python3 tools/check_revision.py`.

## 10. Shopping list (beyond `docs/bom.md`'s "still to buy")

Every discrete part, with what's ordered and what's already on the RAMPS
or the driver modules: `docs/bom.md`, "Electronics assembly — every
discrete part" (2026-10-07).

| Item | Qty | For |
|---|---|---|
| **Multimeter** — **on hand** (Paul, 2026-10-07) | 1 | 12 V polarity at the DC-jack adapter before first power-up |
| F–F Dupont jumpers, 10–20 cm — **ordered** 2026-10-07 | ~20 | UART pigtail (6 leads, one end cut off each), DIAG leads (4 plain jumpers, rev 2026-10-08.2), the button |
| Heat shrink — **ordered** | — | over R1 and the pigtail splice |
| Female DC barrel jack **5.5 × 2.1 mm** → screw terminal adapter (fits the Ledmo HTY-1200500 plug, centre positive) — **ordered** 2026-10-07 | 1 | PSU → RAMPS "5A" terminal without cutting the plug. Check its + / − marking with the multimeter before first use |
| 20 AWG wire, red + black, ~1 m each — **ordered** 2026-10-07 | 1 | adapter → RAMPS 12 V |
| Solder — **on hand**: came with the station, with wick (Paul, 2026-10-07) | — | |
| Flush cutters — **on hand** (Paul, 2026-10-07) | 1 | DIAG pin mod |

**No longer needed from revision 2026-10-08.1** (bought; keep as spares):
the 1.1 A PTC fuses and the 5 × 20 mm fuse kit + printed holder (no separate
key branch), the 100 µF capacitors (no remote board), the 6-conductor
QUARKZMAN cable and the Phoenix 8-pin connectors (no inter-unit signal
cable), the female header strips (no driver socket on a perfboard).
**And from revision 2026-10-08.2:** the perfboard and the male header strip
for the hub board (the UART pigtail replaces it).

## 11. Things to verify on the bench (steps in `control/bringup.md`)

- UART pigtail: the multimeter readings in section 5 before fitting.
- **Done (Paul, 2026-10-08):** a female Dupont grips the top of the RX pin and
  conducts; RX–TX open (R10 not fitted); all five drivers alike, EN-end pins
  through the board. (This replaces the old "Dupont under the driver on the
  MS3 jumper pin" check.)
- UART: every driver answers `ping` with its lead on RX (stage 1).
- Which EN-end pin is DIAG: silkscreen says the one next to the pot; stage 3
  confirms it (`ping` + a hand stall).
- The E0 socket: the key driver answers `ping` at address 3 (MS1 = MS2 = 1).
- The key's StallGuard through the 1 m motor cable (stage 5); shorten the
  cable if it reads too dull (Paul, 2026-10-08).
- Motor step angle 1.8° (one commanded revolution returns to a mark).
- Motor direction vs dial numbering and vs key clockwise (firmware config).

## Sources

1. **Marlin** `Marlin/src/pins/ramps/pins_RAMPS.h`, bugfix-2.1.x at
   [`bbe7c65`](https://github.com/MarlinFirmware/Marlin/blob/bbe7c65573672d8efe49d7777e3ae221f38b6b55/Marlin/src/pins/ramps/pins_RAMPS.h)
   (2026-10-04): stepper, endstop and AUX-1…4 pin numbers; Serial2 on
   AUX4-17/18. E0_STEP 26, E0_DIR 28, E0_ENABLE 24 re-read from
   bugfix-2.1.x on 2026-10-08 (rev 2026-10-08.1).
2. **TMC2209 datasheet** rev 1.09 (2023-02-16), Trinamic/ADI. analog.com is
   blocked from this session; read from the copy in
   [janelia-arduino/TMC2209 `d9f138d`](https://github.com/janelia-arduino/TMC2209/blob/d9f138d049a51c2300d557b47bb5f4dfea4e9b29/datasheet/TMC2209_datasheet_rev1.09.pdf).
   Page numbers above are that PDF's.
3. **BIGTREETECH TMC2209 V1.3** user manual v1.00 (2024-01-26), schematic
   `TMC2209 V1.3-SCH.pdf`, size drawing `TMC2209 V1.3-SIZE.pdf` —
   [bigtreetech/BIGTREETECH-Stepper-Motor-Driver `9f96800`](https://github.com/bigtreetech/BIGTREETECH-Stepper-Motor-Driver/tree/9f9680040e7f696f132b1c0d75a6f79c9f288b13/TMC2209/V1.3).
4. **RAMPS 1.4 netlist**: the KiCad port
   [matt3u/RAMPS-1.4_KiCad `ea33bdf`](https://github.com/matt3u/RAMPS-1.4_KiCad/blob/ea33bdf253b7a8aa695ff820b05b6ff0bcea4b7c/RAMPS_1-41.kicad_pcb)
   — nets read pad by pad from the `.kicad_pcb`. The original Eagle files on
   reprap.org were unreachable from here. Paul's board is a Fasizi clone; the
   things that matter (UART pin, DIAG, addresses) are checked by the firmware
   on the bench.
5. **TMCStepper** 0.7.3, [teemuatlut/TMCStepper](https://github.com/teemuatlut/TMCStepper/tree/v0.7.3):
   `TMC2208Stepper::read()` / `_sendDatagram()` (echo handling, CRC, retries),
   `rms_current()`.
6. **Arduino AVR core** 1.8.6, `variants/mega/pins_arduino.h`
   (`digitalPinToInterrupt`).
7. Motor: STEPPERONLINE 17HE19-2004S (see `docs/housing_decisions.md`,
   2026-10-03). The step angle is still not confirmed against its data sheet.

## Decision log (most recent first)

### 2026-10-08 (evening) — UART on the driver's RX pin; DIAG without soldering (revision 2026-10-08.2)

**What Paul found on his drivers** (BTT TMC2209 V1.3, all five alike; photos
and bench checks, 2026-10-08):
- The **RX, TX and CLK** pins stand up through the top of the board as tall
  pins. BTT's pinout card labels RX and TX both "PDN"; the V1.3 schematic has
  RX = `UART_RX` = the chip's PDN_UART (pin 14), and TX joins it only through
  R10 (NC). **RX–TX measured open** on Paul's driver, so R10 is open.
- A female Dupont on the top of RX grips well and conducts (continuity from
  the pin to the far end of the lead).
- The two EN-end pins go **through** the board (above and below). The
  silkscreen prints "DIAG" under the one next to the trimmer pot; between it
  and the other fitted pin is an empty hole. BTT's manual photo shows them
  pointing down only, which is what the old DIAG mod assumed.
- Also checked (RAMPS 1.4 KiCad, 2026-10-08): each socket's MS3 is its own
  net (socket MS3 ↔ its jumper pad 5 only). Paul's idea of tapping the
  unused E1 block wouldn't reach any driver.

**Decision:**
- **UART tap = top of each driver's RX pin.** It avoids the RAMPS MS3 jumper
  pin under a seated driver, whose clearance was never checked, and needs no
  soldering. Electrically identical (RX is the pin in the socket's MS3 hole).
  The MS3 jumper stays off.
- **DIAG = plain F–F jumper on the top of the DIAG pin.** Still cut the
  bottom ends of both EN-end pins: seated, they'd point down between the
  socket rows, and what's under them on Paul's board isn't checked.
- Leave TX, CLK and the other EN-end pin free. Don't bridge R10.

**Correction** to the pigtail entry below: its "move the lead to the other
MS3 pin" fallback no longer applies; the lead goes on RX, which has been
checked.

### 2026-10-08 — hub board → UART pigtail (revision 2026-10-08.2)

**Paul:** with only a resistor and a junction left, the hub "feels more like a
custom cable than a full daughter board".

**Agreed.** After revision 2026-10-08.1 the hub held only R1 and the bus node
(section 5's old table): one resistor and a six-way junction, all signals.
A harness does the same with less:
- no part to mount on the deck (that mount was still an open CAD item), and
  the area over the drivers stays clear for cooling and bring-up access
  (Paul had considered stacking a perfboard over the RAMPS on its three
  holes; the heatsinks' height and airflow would have had to be checked);
- six fewer plug-in joints: the same six jumpers, but their hub ends are
  now one solder splice instead of six Dupont-on-pin contacts;
- nothing lost for debugging: every lead keeps its own female end, so the
  "move the lead to the other MS3 pin" fallback in stage 1 still works.

**Same circuit** as DS Fig. 4.1: TX2 → 1 kΩ → bus; RX2 and every PDN_UART on
the bus. R1 now sits ~3 cm from the TX2 female end instead of "right at the
TX2 pin" on the board. **Assumption** (not from a source): at 115200 baud
and these lead lengths (tens of cm), where R1 sits along the TX2 lead makes
no difference; the old "right at the pin" note was neatness, not a
datasheet requirement. If stage 1 shows UART errors, this is one thing to
look at.

**Changed:** section 5 rewritten; pin map rows for TX2/RX2/PDN; diagrams
(`uart_pigtail.svg` replaces `hub_board.svg`; schematic sheets 1, 2, 5, 6, 7;
harness; overview); `ramps_and_hub.md` renamed `ramps_and_uart.md`. Also
fixed on schematic sheet 1: the 12 V line was drawn into the hub block
instead of the RAMPS (**Correction**: it was wrong in revision 2026-10-08.1
too; 12 V has gone to the RAMPS "5A" terminal since then).

### 2026-10-08 — key driver onto the RAMPS, E0 socket (revision 2026-10-08.1)

**Paul's question:** couldn't the key driver go on the existing board, with
just the motor cable running to the key turner?

**Why it was remote:** `control/sequence.md` (2026-09-29) put each driver
next to its motor because "StallGuard reads back-EMF right at the motor, and
long motor-phase wiring would dull that sensitivity". **No source supports
that.** StallGuard is measured inside the driver, from the coil current
regulation; and the usual practice contradicts it: 3D printers do
sensorless (StallGuard) homing with TMC2209s on the mainboard and the motors
at the end of their cables (Klipper's TMC driver documentation describes it
for exactly that layout). The key motor comes with ~1 m of cable, and the key
turner is ~125 mm from the dial unit. *Correction*: the premise is withdrawn,
in `sequence.md` too.

**Decision: the key driver goes in the RAMPS E0 socket** (empty until now).
- It gets STEP / DIR / EN from E0 (D26 / D28 / D24, Marlin `pins_RAMPS.h`),
  so the UART workarounds go: EN no longer tied low (TOFF disable),
  DIR no longer tied low (GCONF.shaft read back before every key move).
- VS and VIO come from the socket, through RAMPS's 5 A polyfuse and its own
  100 µF capacitors, like the dials. That removes the supply path whose dips
  could reset the key driver (fuse-holder contacts, PTC, the cable): the
  case firmware v0.3's GSTAT check was written for. The check stays: a
  driver can still reset.
- Address 3 by the MS1 + MS2 jumpers under E0, like the others.
- The key motor's own cable plugs into the E0 motor header. Paul will use it
  as supplied and shorten it if the key's StallGuard reads too dull (bench
  stage 5).

**What it costs:** a fourth DIAG mod; four motor wires between the units
instead of six signals; firmware v0.4 (key pins; DIR/EN like the dials).

**What goes:** the remote driver board (section 6) and its mount on the key
turner (a CAD to-do, now closed), the 6-conductor cable and Phoenix
connectors (section 4), the hub's 12 V branch, fuse and Phoenix header
(section 5), the two 100 µF (C1a, C1b). The interim fuse holder
(`cad/fuse_holder.scad`) printed well (Paul) but has no job now.

**Not verified:** anything on hardware. E0's MS3/MS jumpers are assumed
wired like X/Y/Z's (bench `ping` at address 3 confirms); the key's StallGuard
through 1 m of cable is confirmed in stage 5.

### 2026-10-07 — every driver's VREF pot to minimum (firmware v0.3)

- Firmware v0.3 reads each driver's GSTAT before and after every move and
  stops on a reset (`control/firmware/README.md`, "Driver resets").
- A reset *during* a move is seen only when the move ends. Until then, the
  driver runs on its power-on registers. That means `I_scale_analog` = 1,
  so the current is set by the VREF pot, with `IRUN` = 31 (DS pp. 23, 28).
- The longest moves are the dials' homing passes, up to 1.15 dial turns
  into the stop. A dial pressed there at an unknown pot current is the kind
  of force the relocker research says to avoid (`control/lock_research.md`).
- So every pot goes to minimum, not just the key's (§8). There's no
  downside: the firmware always selects the internal reference, and it
  holds the dial drivers disabled (EN high) from its start until it has
  set them up.
- **Paul agreed (2026-10-07).** `docs/manual.md` 2.3, step 4; §8, step 2;
  schematic sheet 7.

### 2026-10-07 — interim fuse for hub F1 (Paul)

- The PTC fuses are ordered, but no amazon.fr listing arrives soon
  (the first pick: 31 Oct – 5 Nov). Paul ordered **1.6 A glass cartridge
  fuses** to sit in F1's place until then, in a holder he prints (no clips
  ordered): an AUKENIEN kit, **T (slow-blow), 5 × 20 mm, 250 V**, 10 of
  each of 12 values from 0.5 to 10 A. Slow-blow is the right kind here,
  because the power-on charging surge into C1a/C1b is brief.
- **Why 1.6 A works:** the key branch draws less than 0.6 A (§8, item 5),
  and 1.6 A is well below the 5 A the PSU can deliver into a short. A
  short on the cable, the plug or the remote board blows the fuse instead
  of drawing the PSU's full current.
- **Not resettable:** a blown fuse means a real fault. Find it with the
  multimeter before fitting a new one.
- **What leaving F1 out would have meant:** a fault in the key branch
  gets the PSU's full current until the plug is pulled. That's the same
  protection the dial drivers already have: the RAMPS polyfuse holds 5 A,
  so on a 5 A supply it's effectively the supply's own limit. Whether
  the Ledmo shuts down on a short is not known (no data sheet).
- **The holder's contacts must be solid.** A contact that drops out for a
  moment cuts the key driver's VS, and its logic runs from VS (§3.5), so
  it resets to its power-on registers. The firmware writes the driver's
  setup once per session and doesn't check for a reset before a key
  move, so a reset would go unnoticed (follow-up for the firmware).
  **Update 2026-10-07: done in firmware v0.3.** It reads each driver's
  GSTAT around every move and before every attempt, and stops with
  `DRVFAULT` on a reset (`control/firmware/README.md`, "Driver resets").
  Solid contacts still matter: each dropout now stops the run.
  Metal-to-metal contact on each end cap, held by spring pressure or by
  a screw threading into a metal nut, not into the plastic: PETG and PLA
  creep under steady load, so a clamp that bears only on plastic
  loosens. Don't solder to the end caps: the heat can melt the solder
  that holds the fuse wire inside.
- **C1 as ordered isn't sold as low ESR** (now C1a + C1b, below). It's an Innfeeltech
  100 µF 35 V radial, 50 pcs; the listing gives no ESR, ripple-current or
  temperature rating. TMC2209 DS §3 recommends low-ESR electrolytics, with
  at least 100 µF near the driver (§3.5).
  - **Likely fine at the key's current** (0.6 A to start, ≤ 1.0 A),
    because the V1.3 module's own 2 × 10 µF ceramics sit right at the
    chip. This is a judgement, not a measurement: the cap's ESR is
    unknown.
  - **Decided (Paul, 2026-10-07): two in parallel**, C1a and C1b. That
    gives 200 µF at half the ESR of one, and there are 50 in the pack.
    The ~70 × 30 mm remote board has room beside VM/GND (§6.1).
  - **Bench check at stage 5:** after a few minutes of key moves at the
    final current, touch C1a and C1b. They should feel cool. If it's noticeably
    warm, order a low-ESR part (`docs/order_remaining_parts.md`).

### 2026-10-07 — printable schematic

- Added `control/harness/schematic.pdf` and its generator. Nothing in the
  wiring changed.
- RAMPS parts it shows, checked in the RAMPS 1.4 KiCad netlist (Sources,
  item 4):
  - the power input terminal is **X4**. Its '5A' pair: pin 3 goes through
    **F1 (MF-R500)** to the `+12V` net; pins 2 and 4 are GND. Its '11A' pair
    feeds the heated-bed outputs through **F2**, and is not used here;
  - on `+12V` sit every socket's VMOT, the 100 µF capacitors **C3, C4, C6,
    C7, C9, C10**, and the anode of **D1 (1N4004)**;
  - D1's cathode goes to the Mega's VIN.

  So the RAMPS F1 protects the three dial drivers and the Mega's VIN feed.
  That confirms §3.5 and §8.
- Not new: the schematic labels interrupt pins "(irq)". The numbers in §1
  ("attachInterrupt no. 1", …) are Arduino interrupt numbers, not the
  ATmega2560's INTn pin names: D2 is INT4, D3 is INT5, D18 is INT3 and D19
  is INT2.

### 2026-10-06 (evening) — PSU plug and cable colours, from Paul

- PSU: **Ledmo HTY-1200500**, 5.5 × 2.1 mm barrel, centre positive. The
  shopping list now names a 5.5 × 2.1 DC-jack-to-screw-terminal adapter
  (§5, §10).
- Cable colours: red, green, black, white, orange, yellow. Assigned in §4:
  red 12 V, black GND, orange 5 V, yellow STEP, green UART, white DIAG.
  The WireViz harness has been re-rendered with these colours.

### 2026-10-06 — harness v1 (this file)

- Settled CLAUDE.md harness issues 1–6 as above.
- **Correction** to `control/sequence.md` (2026-09-29 wiring plan): "a ~1 kΩ
  resistor between the MCU's UART TX pin and its own PDN_UART pin … one
  resistor per driver" is wrong for a shared bus. The datasheet's circuit has
  one 1 kΩ between TX and RX/the bus (Fig. 4.1).
- **Correction**: dial B's DIAG moves from Y_MIN (D14) to X_MAX (D2): DIAG is
  a pulse (DS §11.2, p. 59), the firmware latches it in an interrupt, and D14
  has no external interrupt in the Arduino core. Y_MIN takes the button.
- **Change**: the key-turner driver uses STEP + DIAG + UART only; DIR and EN
  are tied low on its board (was "STEP/DIR/EN + DIAG").
- New: hub board at the dial end; remote 12 V branch fused at 1.1 A.
