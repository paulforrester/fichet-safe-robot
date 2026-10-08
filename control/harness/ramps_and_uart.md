# RAMPS board + UART pigtail — what goes where

> **Revision 2026-10-08.2** · all four drivers on the RAMPS (key in E0); UART pigtail replaces the hub board · log: `docs/revisions.md`

A single bench sheet pulling together everything that gets fitted to the
RAMPS, plus the UART pigtail, so nothing is missed. It restates
`control/wiring.md` (the reference — read it for the *why* and the sources)
and the manual's §2.4, §2.5 and §2.7. The pigtail is drawn in
`control/harness/uart_pigtail.svg`. (Until revision 2026-10-08.2 this sheet
was `ramps_and_hub.md`.)

Dial naming: **A = top-left, B = top-right, C = bottom**, standing in front of
the safe.

**Revision 2026-10-08.1:** the key driver is on the RAMPS now (E0 socket), so
all four drivers are here. There is no remote driver board and no inter-unit
signal cable; the key motor's own cable plugs into the E0 motor header.

**Revision 2026-10-08.2:** the hub board is replaced by the **UART pigtail**,
a six-lead harness with R1 in the TX2 lead and one solder splice (B).

---

## A. On the RAMPS board

### A1. Jumpers under the driver sockets (set the UART address)

Fit these **before** pressing the RAMPS onto the Mega and before plugging the
drivers in.

| Socket | Driver | MS1 | MS2 | MS3 | Address |
|---|---|---|---|---|---|
| X | dial A | — | — | — | 0 |
| Y | dial B | **jumper** | — | — | 1 |
| Z | dial C | — | **jumper** | — | 2 |
| **E0** | **key** | **jumper** | **jumper** | — | **3** |
| E1 | (empty) | — | — | — | — |

- **Never fit an MS3 jumper on any socket.** On the BTT V1.3 the MS3 position
  is the UART line; a jumper there ties UART to 5 V and kills the bus.

### A2. Drivers

- **Four** TMC2209: dial A in **X**, dial B in **Y**, dial C in **Z**, the
  **key in E0**. **Orientation:** the driver's motor-side row (VS, GND, A2,
  A1, B1, B2, VIO, GND) goes in the socket row **nearer that axis's 4-pin
  motor header**; EN … DIR in the other row. Check each socket with the
  multimeter first (manual §2.4 step 1). A reversed driver is destroyed.
- Each of the four has its two EN-end pins **cut flush underneath** (manual
  §2.3). No soldering: the DIAG and UART leads clip onto pins on top.
- Heatsink on each. **VREF pot to minimum** on every driver first.
- Leave **E1 empty**. Don't bridge R10 on any driver.

### A3. Jumper wires landing on the RAMPS headers (F–F, ~10 cm)

**Where the headers are** (RAMPS 1.4 KiCad layout, `matt3u/RAMPS-1.4_KiCad`
`ea33bdf`; check the readings below on your Fasizi board):

- **Endstop block** — six 3-pin headers side by side along the top edge,
  under the silkscreen "END STOPS". Left to right: **X−, X+, Y−, Y+, Z−, Z+**.
  The board prints **−** for MIN and **+** for MAX: X_MIN = X−, X_MAX = X+,
  and so on.
- Each header's 3 pins run from the board edge inward: **S** (signal,
  nearest the edge), **GND** (middle), **+5 V** (innermost). The "−"/"+"
  in a header's *name* is MIN/MAX, not the pin.
- **AUX-4** — the long single row of 18 pins along the right-hand edge.
  **Pin 1 = 5 V, pin 2 = GND** at its lower end; pin numbers count up
  toward the top edge. **Pin 18 (TX2, D16)** is the top end pin, **pin 17
  (RX2, D17)** the one just below it.

**Check before fitting** (power off, multimeter on continuity):
1. The **middle** pins of all six endstop headers beep to each other and to
   the "5A" − terminal (GND).
2. The **inner** pins beep to each other (5 V). The **edge** pins (S) beep
   to nothing else in the block.
3. AUX-4: the pin at the lower end beeps to the endstop 5 V pins (pin 1);
   the next one beeps to GND (pin 2). So pin 18 is the far end.

**Nothing on any +5 V pin** except as listed: every lead in the table goes on
an **S** pin (the button also uses that header's GND pin).

| From | To (RAMPS) | Mega pin |
|---|---|---|
| Dial A driver: top of its **DIAG** pin | **X_MIN**, S pin | D3 |
| Dial B driver: top of its **DIAG** pin | **X_MAX**, S pin | D2 |
| Dial C driver: top of its **DIAG** pin | **Z_MIN**, S pin | D18 |
| **Key (E0) driver: top of its DIAG pin** | **Z_MAX**, S pin | D19 |
| Start/stop button | **Y_MIN**, S and − pins | D14 |
| Pigtail lead **TX2** (the one with R1) | **AUX-4 pin 18** | D16 |
| Pigtail lead **RX2** | **AUX-4 pin 17** | D17 |
| Pigtail lead **A** | top of the **RX** pin, driver in X | PDN_UART, dial A |
| Pigtail lead **B** | top of the **RX** pin, driver in Y | PDN_UART, dial B |
| Pigtail lead **C** | top of the **RX** pin, driver in Z | PDN_UART, dial C |
| Pigtail lead **KEY** | top of the **RX** pin, driver in **E0** | PDN_UART, key |

- **RX** is the driver's 4th pin from EN (EN, MS1, MS2, **RX**, TX, CLK, …),
  standing up through the top. Nothing on TX or CLK. Leave the MS3 *jumper*
  off (A1). Revision 2026-10-08.2: this replaced the RAMPS MS3 jumper pin as
  the tap (checked: a Dupont grips RX; RX–TX open).
- **DIAG** is the EN-end pin next to the trimmer pot ("DIAG" printed under
  it). Nothing on the other EN-end pin.
- The key's **STEP, DIR and EN** are in the E0 socket itself (D26, D28, D24):
  the driver plugging into E0 connects them. No jumper wires for those.
- Power to the RAMPS is **not** a jumper: it's the 20 AWG pair from the
  DC-jack adapter into the screw terminal marked **5A** (A4).

### A4. Power into the RAMPS

- 20 AWG pair from the PSU's **DC-jack-to-screw-terminal adapter** straight
  into the RAMPS terminal marked **5A** (+ and − per silkscreen). RAMPS's own
  5 A fuse feeds all four drivers. Nothing else takes 12 V (the pigtail
  carries only UART signals). Leave the **11A** terminal (heated bed) empty.
- **Leave the Mega's own barrel jack empty.** The drivers get 12 V only through
  the 5A terminal; RAMPS diode D1 feeds the Mega's VIN from there.

### A5. The key motor

- The key motor's own ~1 m cable plugs into the **E0 motor header** (the 4-pin
  header beside the E0 socket), like a dial motor into X/Y/Z. It is the only
  wire between the two units.
- Use the supplied cable as it is; shorten it only if the key's StallGuard
  reads too dull in bring-up stage 5. Never plug or unplug it with 12 V on.

### Already on the RAMPS — nothing to add

The 5 A input polyfuse (F1), the diode D1 to VIN, the 100 µF per socket and the
EN pull-ups are all on the board. The parts drawn grey on the schematic are
these.

---

## B. The UART pigtail (`uart_pigtail.svg`) — replaces the hub board

Revision 2026-10-08.2. Six leads, each ending in a female Dupont, soldered
together in one splice. Electrically the same as the hub board it replaces:
the TMC2209 single-wire bus (datasheet Fig. 4.1), TX2 → 1 kΩ → bus; RX2 and
every driver's PDN_UART on the bus. No 12 V, 5 V or GND on it.

**Build:**
1. **Measure**, with the drivers seated: the run from AUX-4 to each driver's
   RX pin (X, Y, Z, E0). Pick a splice point near the middle of the RAMPS.
2. **Make six leads**: cut one end off each of six F–F jumpers (jumper halves
   will do if they're long enough). Each lead keeps its factory-crimped
   female end. Cut each to its measured length + a few cm.
3. **TX2 lead**: solder **R1 (1 kΩ)** in line about 3 cm from its female end;
   heat shrink over it.
4. **Splice**: R1's far lead, RX2, A, B, C and KEY soldered together in one
   joint. Heat shrink over it, then a larger piece over the bundle.
5. **Label** each female end with tape: TX2, RX2, A, B, C, KEY.
6. **Check with the multimeter (Ω), pigtail loose:** TX2 → RX2 about 1 kΩ;
   TX2 → A, B, C, KEY about 1 kΩ each; RX2 → A, B, C, KEY about 0 Ω each. Tug
   each lead at the splice.
7. **Fit** (power off): leads as in A3; zip-tie the splice to the deck so the
   leads can't pull on the joint.

Every driver lead has its own female end: pull it off the RX pin before
unplugging that driver.

---

## C. Order of work (from `bringup.md`)

1. RAMPS jumpers (A1) → RAMPS onto Mega → the four drivers in (A2).
2. Build the UART pigtail (B) and check it with the multimeter.
3. Power wiring: PSU → DC-jack adapter → RAMPS "5A" terminal. Check adapter
   polarity with the multimeter first.
4. Signal jumpers (A3): the four DIAG jumpers, the six pigtail leads, the
   button.
5. The key motor cable into the E0 motor header (A5), 12 V off.
6. Bring-up stage 1: `ping` — all four drivers must answer (A at address 0 …
   key at address 3) before anything moves.
