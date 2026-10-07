# RAMPS board + hub board — what goes where

A single bench sheet pulling together everything that gets fitted to the
RAMPS and the hub board, so nothing is missed. It restates `control/wiring.md`
(the reference — read it for the *why* and the sources) and the manual's §2.4,
§2.5 and §2.8. The hub board's part placement is drawn in
`control/harness/hub_board.svg`.

Dial naming: **A = top-left, B = top-right, C = bottom**, standing in front of
the safe.

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
| E0, E1 | (empty) | — | — | — | — |

- **Never fit an MS3 jumper on any socket.** On the BTT V1.3 the MS3 position
  is the UART line; a jumper there ties UART to 5 V and kills the bus.
- The key-turner driver is **not** on the RAMPS — it lives on the remote board
  at the key turner, address 3 (MS1+MS2 to 5 V there).

### A2. Drivers

- Three TMC2209 in **X, Y, Z**. Orientation: match the driver's **EN / DIR /
  VM / GND** corner pins to the RAMPS silkscreen. A reversed driver is
  destroyed.
- Each of the three dial drivers has had the **DIAG mod** (manual §2.3): the
  two down-pointing pins clipped, a flying lead soldered to the DIAG joint.
- Heatsink on each. **VREF pot to minimum** on every driver first.
- Leave **E0 and E1 empty**. Don't bridge R10 on any driver.

### A3. Jumper wires landing on the RAMPS headers (F–F, ~10 cm)

Endstop headers are 3-pin: **S** signal, **−** GND, **+** 5 V.

| From | To (RAMPS) | Mega pin |
|---|---|---|
| Dial A driver DIAG lead | **X_MIN**, S pin | D3 |
| Dial B driver DIAG lead | **X_MAX**, S pin | D2 |
| Dial C driver DIAG lead | **Z_MIN**, S pin | D18 |
| Hub DIAG pin | **Z_MAX**, S pin (key DIAG, from cable) | D19 |
| Start/stop button | **Y_MIN**, S and − pins | D14 |
| Hub 5V pin ← | **Y_MAX**, + pin | 5 V |
| Hub GND pin ← | **Y_MAX**, − pin | GND |
| Hub TX2 pin ← | **AUX-4 pin 18** | D16 |
| Hub BUS pin ← | **AUX-4 pin 17** (RX2) | D17 |
| Hub STEP pin ← | **AUX-4 pin 16** | D23 |
| X socket **MS3 jumper pin** (signal side) → hub BUS | — | PDN_UART, dial A |
| Y socket **MS3 jumper pin** (signal side) → hub BUS | — | PDN_UART, dial B |
| Z socket **MS3 jumper pin** (signal side) → hub BUS | — | PDN_UART, dial C |

- The three **MS3 jumper pins** carry each dial driver's UART line to the hub
  bus node. Leave the MS3 *jumper* off (A1); clip the F–F jumper onto the pin
  **on the side nearer the driver's EN/STEP/DIR row**. If `ping` gets no answer
  in bring-up stage 1, move it to the other pin (the 5 V side — harmless).
- Power to the RAMPS is **not** a jumper: it's the 20 AWG pair from the hub's
  12V OUT into the screw terminal marked **5A** (A4).

### A4. Power into the RAMPS

- 20 AWG pair from **hub 12V OUT** into the RAMPS terminal marked **5A**
  (+ and − per silkscreen).
- **Leave the Mega's own barrel jack empty.** The drivers get 12 V only through
  the 5A terminal; RAMPS diode D1 feeds the Mega's VIN from there.

### Already on the RAMPS — nothing to add

The 5 A input polyfuse (F1), the diode D1 to VIN, the 100 µF per socket and the
EN pull-ups are all on the board. The parts drawn grey on the schematic are
these.

---

## B. On the hub board (`hub_board.svg`)

A ~50 × 30 mm perfboard beside the Mega. It splits the 12 V, holds the one UART
resistor and the bus node, and carries the 8-pin Phoenix header for the cable.

**Parts fitted:**
- **R1, 1 kΩ** — from the TX2 header pin to the bus node. Keep it right at the
  TX2 pin.
- **Bus node** — a junction joining R1's output, RX2 (hub BUS pin), the three
  dial PDN_UART leads, and Phoenix pin 6.
- **8-pin Phoenix header** (board half; the plug is on the cable).
- **2.54 mm male header pins** for the F–F jumpers to the RAMPS: TX2, BUS,
  STEP, DIAG, 5V, GND.
- **F1 fuse** in series on 12V+ to Phoenix pin 1 — the printed holder is a
  **separate part beside the board** (it's 54.5 mm long): 1.1 A PTC when it
  arrives, the 1.6 A glass fuse for now.
- **GND rail** — 12V IN −, 12V OUT −, the Y_MAX − lead, the shield drain, and
  Phoenix pins 2 and 8 all land here.

**Phoenix header (same pin numbers at both ends of the cable):**

| Pin | Net | On the hub |
|---|---|---|
| 1 | +12 V (fused) | F1 holder out |
| 2 | GND | GND rail |
| 3 | — | empty (keeps 12 V off the 5 V logic) |
| 4 | +5 V | 5V header pin (← Y_MAX +) |
| 5 | KEY_STEP | STEP header pin (← D23) |
| 6 | UART | bus node |
| 7 | KEY_DIAG | DIAG header pin (→ Z_MAX S, D19) |
| 8 | shield | GND rail (dial end only) |

---

## C. Order of work (from `bringup.md`)

1. RAMPS jumpers (A1) → RAMPS onto Mega → drivers in (A2).
2. Build the hub board (B), fuse holder beside it.
3. Power wiring: PSU → DC-jack adapter → hub 12V IN → hub 12V OUT → RAMPS 5A.
   Check adapter polarity with the multimeter first.
4. Signal jumpers (A3).
5. Bring-up stage 1: `ping` — every driver must answer before anything moves.
