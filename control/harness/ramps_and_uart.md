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
  **key in E0**. Orientation: match the driver's **EN / DIR / VM / GND** corner
  pins to the RAMPS silkscreen. A reversed driver is destroyed.
- Each of the four has the **DIAG mod** (manual §2.3): the two down-pointing
  pins clipped, a flying lead soldered to the DIAG joint.
- Heatsink on each. **VREF pot to minimum** on every driver first.
- Leave **E1 empty**. Don't bridge R10 on any driver.

### A3. Jumper wires landing on the RAMPS headers (F–F, ~10 cm)

Endstop headers are 3-pin: **S** signal, **−** GND, **+** 5 V.

| From | To (RAMPS) | Mega pin |
|---|---|---|
| Dial A driver DIAG lead | **X_MIN**, S pin | D3 |
| Dial B driver DIAG lead | **X_MAX**, S pin | D2 |
| Dial C driver DIAG lead | **Z_MIN**, S pin | D18 |
| **Key (E0) driver DIAG lead** | **Z_MAX**, S pin | D19 |
| Start/stop button | **Y_MIN**, S and − pins | D14 |
| Pigtail lead **TX2** (the one with R1) | **AUX-4 pin 18** | D16 |
| Pigtail lead **RX2** | **AUX-4 pin 17** | D17 |
| Pigtail lead **A** | X socket **MS3 jumper pin** (signal side) | PDN_UART, dial A |
| Pigtail lead **B** | Y socket **MS3 jumper pin** (signal side) | PDN_UART, dial B |
| Pigtail lead **C** | Z socket **MS3 jumper pin** (signal side) | PDN_UART, dial C |
| Pigtail lead **KEY** | **E0 socket MS3 jumper pin** (signal side) | PDN_UART, key |

- The four **MS3 jumper pins** carry each driver's UART line to the pigtail's
  splice. Leave the MS3 *jumper* off (A1); clip the pigtail lead onto the pin
  **on the side nearer the driver's EN/STEP/DIR row**. If `ping` gets no answer
  in bring-up stage 1, move it to the other pin (the 5 V side — harmless).
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
1. **Test-fit one female Dupont** on the X socket's MS3 jumper pin under the
   seated, heatsinked driver (**VERIFY**, unchecked so far). Then **measure**
   the run from AUX-4 to each socket's MS3 jumper pin (X, Y, Z, E0) with the
   drivers in. Pick a splice point near the middle of the RAMPS.
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

Because every lead has its own female end, a driver lead can still be moved
to the other MS3 pin if `ping` gets no answer (bring-up stage 1).

---

## C. Order of work (from `bringup.md`)

1. RAMPS jumpers (A1) → RAMPS onto Mega → the four drivers in (A2).
2. Build the UART pigtail (B) and check it with the multimeter.
3. Power wiring: PSU → DC-jack adapter → RAMPS "5A" terminal. Check adapter
   polarity with the multimeter first.
4. Signal jumpers (A3): the four DIAG leads, the six pigtail leads, the
   button.
5. The key motor cable into the E0 motor header (A5), 12 V off.
6. Bring-up stage 1: `ping` — all four drivers must answer (A at address 0 …
   key at address 3) before anything moves.
