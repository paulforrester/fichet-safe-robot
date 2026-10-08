# RAMPS board, hub board and key-turner board — what goes where

A single bench sheet pulling together everything that gets fitted to the
RAMPS, the hub board and the key-turner board, so nothing is missed. It restates `control/wiring.md`
(the reference — read it for the *why* and the sources) and the manual's §2.4,
§2.5 and §2.8. The hub board's part placement is drawn in
`control/harness/hub_board.svg`.

Dial naming: **A = top-left, B = top-right, C = bottom**, standing in front of
the safe.

## The four drivers at a glance

There are **four** TMC2209 drivers in use (plus one spare). Three sit on the
RAMPS; the fourth sits on its own small board at the key turner, next to its
motor, because StallGuard reads the motor's back-EMF and works best with
short motor wires (`control/wiring.md`, Summary and §6).

| Driver | Turns | Where it sits | UART address | DIAG (stall) goes to | Section |
|---|---|---|---|---|---|
| 1 | dial A (top-left) | RAMPS **X** socket | 0 | X_MIN S (D3) | A |
| 2 | dial B (top-right) | RAMPS **Y** socket | 1 | X_MAX S (D2) | A |
| 3 | dial C (bottom) | RAMPS **Z** socket | 2 | Z_MIN S (D18) | A |
| 4 | key | **remote board** at the key turner | 3 | cable pin 7 → hub → Z_MAX S (D19) | C |
| (5) | spare | in the box | — | — | — |

All four share one UART line (one 1 kΩ, on the hub). The key driver gets its
12 V, 5 V, STEP, UART and DIAG through the inter-unit cable from the hub.

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

## C. On the key-turner board (driver 4)

A ~70 × 30 mm perfboard at the key turner. The driver plugs into female
headers so it can be swapped. Full layout, with the grid positions:
`control/wiring.md` §6.1; build steps: manual §2.6.

**The driver itself:**
- **No DIAG mod** on this one. Its down-pointing DIAG pin plugs straight
  into a 2-pin female socket on the board (the INDEX pin beside it goes in
  the other half, connected to nothing).
- Heatsink on. **VREF pot to minimum before its first power-up**: its EN is
  tied to GND, so it switches on as soon as 12 V arrives, at whatever the pot
  says, until the firmware sets the real current.
- Don't bridge R10.

**What each driver pin connects to:**

| Driver pin | Goes to |
|---|---|
| EN, DIR, CLK | GND (direction and on/off are set over UART instead) |
| MS1, MS2 | +5 V (sets UART address 3) |
| RX (= PDN_UART) | Phoenix pin 6 (UART) |
| TX | nothing |
| STEP | Phoenix pin 5 |
| DIAG (in its socket) | Phoenix pin 7 |
| VIO | Phoenix pin 4 (+5 V) |
| VM | Phoenix pin 1 (+12 V), and the + of C1a and C1b |
| GND (both pins) | Phoenix pin 2, and the − of C1a and C1b |
| A2, A1, B1, B2 | 4-pin male header for the key motor, same order as a RAMPS motor header |

**Other parts on this board:**
- **C1a, C1b**: two 100 µF ≥ 25 V electrolytics in parallel, right next to
  VM and GND, short leads. The stripe marks −; both go to GND.
- **8-pin Phoenix header** for the cable. Phoenix pin 3 is empty; pin 8 (the
  shield) is **not** connected at this end: fold the drain wire back under
  heat shrink.
- Female headers: 2 × 1×8 for the driver's two rows, 1 × 1×2 for
  INDEX/DIAG. **VERIFY** before soldering them: lay the driver on the board
  and check the INDEX/DIAG pins land on the 2.54 mm grid.

**Before plugging the driver in:** with the multimeter, check there's no
short between Phoenix pins 1, 2 and 4.

**Not designed yet:** where this board mounts on the key turner (CAD to-do;
size and needs in `control/wiring.md` §6.2).

---

## D. Order of work (from `bringup.md`)

1. RAMPS jumpers (A1) → RAMPS onto Mega → drivers in (A2).
2. Build the hub board (B), fuse holder beside it.
3. Build the key-turner board (C). Driver 4 goes in only after the short check.
4. Power wiring: PSU → DC-jack adapter → hub 12V IN → hub 12V OUT → RAMPS 5A.
   Check adapter polarity with the multimeter first.
5. Signal jumpers (A3); the inter-unit cable last, with 12 V off.
6. Bring-up stage 1: `ping` — every driver must answer before anything moves.
