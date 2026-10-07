# Wiring harness — Mega 2560 + RAMPS 1.4 + 4 × BTT TMC2209 V1.3

Written 2026-10-06 (cloud session, no hardware). Everything below is from the
sources listed at the bottom; anything I could not establish is marked
**ASSUMPTION** or **VERIFY** and gets a bench step in `control/bringup.md`.
The firmware (`control/firmware/`) is built on this pin map
(`safe_robot/pins.h`).
Decision log for this file is at the end (most recent first).

## Summary — what was decided

1. **One UART bus, one 1 kΩ resistor in total**: Mega TX2 (D16) → 1 kΩ → bus;
   RX2 (D17) straight on the bus; every driver's PDN_UART straight on the bus.
   This is the datasheet's own circuit (TMC2209 DS Fig. 4.1). *Correction* of
   `sequence.md`, which said one resistor per driver.
2. **UART on RAMPS needs no soldering**: the BTT V1.3's PDN_UART pin sits in
   the socket's **MS3** position, and RAMPS brings MS3 out to its MS3 jumper
   pin. Leave the MS3 jumper **off** and clip a female jumper onto that pin.
3. **Addresses by RAMPS jumpers**: X = none (addr 0), Y = MS1 (addr 1),
   Z = MS2 (addr 2); remote key driver MS1+MS2 tied to 5 V (addr 3).
   **Never fit an MS3 jumper** (it would tie the UART line to 5 V).
4. **DIAG needs a one-time mod on the 3 dial drivers**: on the V1.3 the DIAG
   pin points *down* (it is meant for BTT boards' DIAG sockets) and lands on
   nothing on a RAMPS. Clip it under the board and solder a lead to its top
   joint (section 3.3). The remote driver needs no mod — its perfboard gets a
   socket for that pin.
5. **DIAG pins moved to interrupt-capable Mega pins** (D2, D3, D18, D19).
   *Correction*: dial B's DIAG was planned on Y_MIN (D14), which has no
   `attachInterrupt` on the Mega, and the datasheet says DIAG is a *pulse*.
   Y_MIN now takes the start/stop button.
6. **The 6-conductor cable carries** 12 V, GND, 5 V (VIO), STEP, UART, DIAG.
   At the key turner, **EN is tied to GND** (disable by UART, CHOPCONF.TOFF=0)
   and **DIR is tied to GND** (direction set by UART, GCONF.shaft, read back
   before every move). Shield drain to GND at the dial end only.
7. **Remote 5 V logic comes from the Mega over the cable**, not from a local
   regulator: a logic input must never be more than 0.5 V above that driver's
   VIO (DS abs. max.), and this way VIO is up whenever the Mega is driving STEP
   or UART.
8. **Remote 12 V is fused**: 1.1 A resettable fuse (PTC) on a small hub board
   at the dial end; RAMPS's own 5 A fuse covers the three dial drivers.
9. **Currents**: dial drivers 1.0 A RMS (hold 0.5 A) until the dial torque is
   measured; key driver starts at 0.6 A RMS and is then set to 2 × the measured
   minimum that turns the key (bench stage 5).
10. **Power order**: everything plugged with power off; USB first, then 12 V;
    12 V off first. Never plug or unplug a motor or the inter-unit cable with
    12 V on.

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
| Key DIAG (from cable) | D19 (INT, no. 4) | **Z_MAX** header, S pin, via hub | Marlin Z_MAX_PIN 19 |
| Key STEP (to cable) | D23 | **AUX-4 pin 16**, via hub | Marlin `AUX4_16 = 23` |
| UART TX2 | D16 | **AUX-4 pin 18** → hub 1 kΩ | Marlin: "Serial2 — TX2 = D16 RX2 = D17 (AUX4-18 and AUX4-17)" |
| UART RX2 | D17 | **AUX-4 pin 17** → hub bus node | same |
| Dial drivers' PDN_UART | — | MS3 jumper pin of X, Y, Z (signal side) → hub bus node | KiCad: socket MS3 ↔ jumper pad 5 |
| Start / stop button | D14 (input, pull-up) | **Y_MIN** header: S and − pins | Marlin Y_MIN_PIN 14 (no interrupt needed) |
| 5 V and GND for the remote | 5 V, GND | **Y_MAX** header + and − pins → hub | KiCad: endstop pin 3 = 5 V, pin 2 = GND |
| Status LED | D13 | on-board LED | Marlin LED_PIN 13 |
| Spare | D15 | Y_MAX header, S pin | — |
| Reserved: key DIR, key EN | D25, D27 | AUX-4 pins 15, 14 | only if the cable ever gets 2 more conductors |
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
| E0, E1 | empty | — | — | — | — |
| (remote perfboard) | key | tied to 5 V | tied to 5 V | n/a | 3 |

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
  through **R10, which is not fitted** (marked NC). So PDN_UART is in the MS3
  position, and on RAMPS the MS3 position goes only to the MS3 jumper pin (KiCad
  net `U2.MS3 ↔ JP1.5`). Clip a female jumper onto **the MS3 jumper pin on the
  side nearer the driver's EN/STEP/DIR row** (KiCad port: the signal pins sit on
  that side, the 5 V pins on the motor-terminal side). **VERIFY** on Paul's
  Fasizi board: the firmware's `ping` answers only if the lead is on the right
  pin; the wrong pin is the 5 V side, which is harmless (the bus just sits high).
- **Don't bridge R10 on any driver**: RAMPS ties the socket's RST and SLP
  pins together (KiCad net `U2.SLP ↔ U2.RST`), which on the V1.3 are TX and
  CLK. With R10 open, CLK sees only its 20 kΩ pull-down (BTT schematic R4) →
  internal clock, as the datasheet wants ("Tie to GND … for internal clock",
  DS §2.2). With R10 bridged, PDN_UART would be wired to CLK.
- RAMPS has a **10 kΩ pull-up on every EN line** (KiCad R16–R20), so the dial
  drivers stay disabled until the firmware drives EN low.

## 3. The open harness issues, resolved

### 3.1 Conductor count (6 conductors + shield)

The remote driver would want STEP, DIR, EN, DIAG, UART, 12 V, GND, 5 V = 8.

**Choice: 12 V, GND, 5 V, STEP, UART, DIAG on the cable; EN and DIR tied to GND
on the remote board.**

- **EN → GND**: the driver can still be switched off: CHOPCONF.TOFF = 0
  is "Driver disable, all bridges off" (DS CHOPCONF, p. 34), and it also
  clears short-circuit flags like ENN does (DS DRV_STATUS, p. 37). The
  datasheet warns that with ENN fixed active, the default IRUN = 31 flows for a
  moment after power-up until the UART sets a lower current (DS §8, p. 52) —
  covered in section 7.
- **DIR → GND, direction by UART**: GCONF bit 3 `shaft` = "Inverse motor
  direction" (DS p. 23). Direction only changes while the key is stopped, so the
  firmware writes `shaft`, reads GCONF back, and refuses to move unless it
  matches. Direction is not time-critical; the stall signal is — so the
  stall signal (DIAG) keeps its own wire.
- **Rejected**: (a) dropping DIAG and polling SG_RESULT over UART during
  moves — puts the time-critical stop on a shared serial bus; (b) a local 5 V
  regulator to free the 5 V wire — the remote driver's VIO would then be off
  whenever 12 V is off while the Mega still drives STEP/UART high, breaking
  the "logic input ≤ VVIO + 0.5 V" absolute maximum (DS §22, p. 75); (c) the
  shield as a ground — it would carry motor current.

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

- **UART**: no soldering — MS3 jumper pin, section 2.
- **DIAG**: the V1.3 has two extra top-edge pins next to the EN corner,
  INDEX and DIAG (schematic header P1B; silkscreen labels the one further from
  EN "DIAG"). They are fitted **pointing down** (BTT manual p. 6 "BOTTOM
  (Factory default)" photo; p. 8 shows them going into the SKR 3's DIAG
  sockets). A RAMPS has no socket there, and the RAMPS sockets are at 20.32 mm
  pitch — the driver boards sit edge to edge, so the pin can't be bent out
  sideways. **Mod for the 3 dial drivers (not the remote one), before fitting
  the heatsinks:**
  1. With flush cutters, cut the two down-pointing pins (INDEX and DIAG) off
     flush with the bottom of their little plastic spacer, so nothing sticks
     down towards the RAMPS.
  2. Cut a female–female jumper in half. Strip 2–3 mm, tin it, and solder it
     to the **top-side joint of the DIAG pin** (the pin labelled DIAG, second
     from the EN corner). Keep the iron off the trimmer pot next to it.
  3. The jumper's female end goes on the S pin of that dial's endstop header
     (section 1).
  Alternative if you prefer: desolder the 2-pin header and solder one straight
  pin into the DIAG hole pointing up.
- **VERIFY**: which pin is DIAG. The firmware's `ping` prints the DIAG state
  both from the Mega pin and from the driver's own IOIN register; bench stage
  3 stalls the motor by hand and both must flip together.

### 3.4 Address strapping

Section 2 table. The firmware reads each driver's IOIN (MS1, MS2 bits and
VERSION, which must read 0x21 — DS IOIN, p. 25) and refuses to run if any
address doesn't answer or reports the wrong MS1/MS2.

### 3.5 Power and 5 V logic for the remote driver

- **5 V (VIO)**: from the RAMPS 5 V rail (Y_MAX header +) over the cable.
  VIO only powers the I/O pins: the chip's logic runs off its internal
  regulator from VS (DS §2.2: VCC_IO "does not supply IC logic part", p. 10).
  So the remote driver needs both 5 V and 12 V before its UART answers. Its VIO
  load is small: the module's EN pull-up (20 kΩ, BTT schematic R1) to the
  grounded EN is 0.25 mA. Voltage drop is negligible on ~0.3 m of 22 AWG
  (~0.05 Ω/m).
- **12 V (VS)**: from the hub, through a 1.1 A PTC; the RAMPS sockets get
  theirs through RAMPS's own 5 A polyfuse (KiCad: input terminal pin 3 → F1
  MF-R500 → `+12V` → all socket VMOT pins).
- **Bulk capacitor**: 100 µF (≥ 25 V, low-ESR electrolytic) across VM–GND right
  at the remote driver. DS §3 (p. 11): "A minimum capacity of 100µF near the
  driver is recommended" and "keep power slopes below 1V/µs". RAMPS has the
  same 100 µF beside each socket (KiCad C3/C4/C6/C7/C9/C10). The V1.3 itself
  only has 2 × 10 µF ceramic (BTT schematic C1/C2).

### 3.6 Mount for the remote board

Section 6.2 gives the board's size and needs. The CAD change is left for a
mechanical session.

## 4. Inter-unit cable and connectors

Cable: QUARKZMAN 22 AWG shielded, 6 conductors. Cut **~300 mm** (units are
~125 mm centre to centre; slack for placing them by hand). Strip 30 mm of
jacket at each end. Connectors: the 5.08 mm 8-pin pluggable screw terminals
(header soldered to each perfboard, screw plug on the cable). **Same pin
numbers at both ends** (straight through).

| Pin | Signal | Dial end (hub board) | Key-turner end (remote board) | Conductor colour |
|---|---|---|---|---|
| 1 | +12 V (after 1.1 A PTC) | PTC output | driver VM + 100 µF (+) | **red** |
| 2 | GND (motor return + logic) | hub GND | driver GND (both pins), 100 µF (−) | **black** |
| 3 | — empty (keeps 12 V/GND away from 5 V logic) | — | — | — |
| 4 | +5 V (VIO) | RAMPS 5 V (Y_MAX +) | driver VIO, MS1, MS2 | **orange** |
| 5 | KEY_STEP | Mega D23 | driver STEP | **yellow** |
| 6 | UART bus | bus node | driver RX (= PDN_UART) | **green** |
| 7 | KEY_DIAG | Mega D19 (Z_MAX S) | driver DIAG (via its socket) | **white** |
| 8 | Shield drain | hub GND | **not connected** — fold back, cover with heat shrink | shield |

- **Colours**: the cable's six are red, green, black, white, orange and
  yellow (Paul, 2026-10-06). The assignment is my choice: red and black for
  12 V and GND by the usual convention, and orange for 5 V, so that red only
  ever means 12 V. Mark it on both plugs.
- **Shield grounded at the dial end only.** That's the usual practice for a
  shield on a single-ended signal cable, so no current flows in it (a design
  convention, not from a datasheet). The motor current returns on pin 2.
- **Keying**: **VERIFY** that the plug only fits one way round. Mark pin 1 on
  both halves with a marker either way. If it were plugged in reversed, dial
  pin 1 (12 V) would meet the remote's empty pin 8 — no 12 V reaches logic.
- **Strain relief**: zip-tie the cable to each housing within ~20 mm of the
  plug, so a tug lands on the tie, not the screw terminals. Keep it clear of
  the key cap's rotation. Label both ends.
- **Never plug or unplug it with 12 V on**: DS §3 "Attention" (p. 11) —
  energy from the motor coils goes back into the supply when a driver gets
  cut off from its supply capacitors.

## 5. Dial-end hub board

A small perfboard (~50 × 30 mm) on the dial unit's electronics deck, next to
the Mega. It is the 12 V split point, holds the one UART resistor and the bus
node, and carries the cable's Phoenix header. **It needs a place on the deck —
add it to the mechanical to-do with the remote board mount.**

| Hub point | Connects to | With |
|---|---|---|
| 12V IN +/− | PSU (Ledmo HTY-1200500, 5.5 × 2.1 mm barrel, **centre +**) via a DC-jack-to-screw-terminal adapter | 20 AWG pair |
| 12V OUT +/− | RAMPS power terminal, the pair marked **5A** (+ and − per silkscreen) | 20 AWG pair |
| F1 PTC 1.1 A hold | 12V IN+ → F1 → Phoenix pin 1 | on board. **For now: a 1.6 A glass cartridge fuse in a printed holder** (log 2026-10-07) |
| R1 1 kΩ | TX2 pin → R1 → BUS | on board (one of the 100 ordered) |
| TX2 pin | AUX-4 pin 18 (D16) | F–F jumper |
| BUS pins ×4 | RX2: AUX-4 pin 17 (D17); X, Y, Z MS3 jumper pins | F–F jumpers; Phoenix pin 6 on board |
| STEP pin | AUX-4 pin 16 (D23) → Phoenix pin 5 | F–F jumper |
| DIAG pin | Z_MAX S (D19) ← Phoenix pin 7 | F–F jumper |
| 5V pin | Y_MAX + → Phoenix pin 4 | F–F jumper |
| GND pin | Y_MAX − → hub GND (also Phoenix pins 2 and 8, 12V IN −) | F–F jumper |

Use 2.54 mm male header pins on the hub for the jumper ends. Keep R1 right at
the TX2 pin, and the bus node short; the dial drivers' UART leads are ~10 cm
F–F jumpers.

## 6. Remote driver board (key turner)

### 6.1 Layout (component side, 2.54 mm grid; columns c0…, rows r0…)

The driver plugs into female headers so it can be swapped. Seen from above,
the board shows the driver's top side (pot and heatsink), so this is BTT's own
"TOP" pin view (manual p. 5).

```
            c0  c1  c2  c3  c4  c5
  r0        EN  IDX DIAG [pot]  VM   <- 1x8 female (c0), 1x2 female (c1-c2), 1x8 female (c5)
  r1        MS1             GND
  r2        MS2             A2  --> motor pin 1
  r3        RX              A1  --> motor pin 2
  r4        TX              B1  --> motor pin 3
  r5        CLK             B2  --> motor pin 4
  r6        STEP            VIO
  r7        DIR             GND
```

| Driver pin | Wire to | Why |
|---|---|---|
| EN (c0 r0) | GND | always enabled; disable with TOFF = 0 (3.1) |
| MS1, MS2 | +5 V | UART address 3 |
| RX (PDN_UART) | Phoenix 6 | UART bus |
| TX | nothing | R10 not fitted |
| CLK | GND | internal clock (DS §2.2); the module also has a 20 kΩ pull-down |
| STEP | Phoenix 5 | |
| DIR | GND | direction via GCONF.shaft (3.1) |
| DIAG socket (c2 r0) | Phoenix 7 | the V1.3's down-pointing DIAG pin plugs straight in; no mod |
| INDEX socket (c1 r0) | nothing | only there so the 2-pin block seats |
| VM | Phoenix 1, C1 + | |
| GND (both) | Phoenix 2, C1 − | |
| VIO | Phoenix 4 | |
| A2, A1, B1, B2 | 4-pin male header, pins 1–4 | same order as a RAMPS motor header (RAMPS socket order 2B, 2A, 1A, 1B are the same positions), so the motor cable plugs in the same way as on RAMPS |

Parts: 2 × 1×8 and 1 × 1×2 female headers (2.54 mm), 1 × 1×4 male header, the
8-pin Phoenix header, C1 100 µF ≥ 25 V. The INDEX/DIAG pins are on the same
2.54 mm grid as EN (BTT size drawing: 2.54 and 5.08 mm from EN along the top
edge) — **VERIFY** on the real board by laying the driver on the perfboard
before soldering the headers.

Motor wiring note (from `docs/bom.md`): on some 17HE19-2004S the two middle
wires are swapped. Symptom: the motor buzzes or jitters instead of turning.
Fix it in the cable's connector, not on the board.

### 6.2 Size and needs, for the key-turner mount (mechanical session)

- **Board**: ~70 × 30 mm perfboard from the kit (**VERIFY** the kit's sizes and
  hole diameter with calipers). Corner mounting holes; 4 mm standoffs under it
  (solder side).
- **Height above the board**: female header 8.5 mm + driver PCB 1.6 mm +
  heatsink (**measure** the supplied heatsink) — allow **~30 mm**, plus
  ≥ 10 mm of free air above the heatsink. At ≤ 1 A RMS the stick-on heatsink is
  enough (BTT: active cooling above 1.2 A).
- **Phoenix plug**: sticks out ~15–20 mm past the header — **measure**. It
  must face the dial unit, with room for a hand to unplug it.
- **Motor cable**: the motor comes with ~1 m of cable — coil and tie it; leave
  the motor-end connector reachable.
- **Keep clear of** the rotating cap/hub, and leave the 3 magnet retainers
  reachable. No magnetic-sensitivity concern for the driver.
- **Thermal**: dissipation is small at 0.6 A; don't enclose it airtight.

## 7. Motor current settings

Sense resistors on the V1.3: **0.11 Ω** (BTT schematic R3/R5 "0R11"; visible as
"R110" on the board, manual p. 6). Current set by UART with the internal
reference (GCONF.I_scale_analog = 0), so the module's VREF pot doesn't matter
once the firmware is running. RMS current = (CS+1)/32 × VFS/(R_SENSE + 20 mΩ)/√2,
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
2. **First power-up of the remote driver**: turn its VREF pot to minimum
   first. Its EN is tied low, so it is enabled as soon as 12 V arrives, at its
   power-on current, until the firmware sets the real one (DS p. 52 warning).
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
5. **Fusing**: PSU (Ledmo HTY-1200500) 5 A max. RAMPS 5 A polyfuse (F1) feeds the three dial
   drivers. 1.1 A PTC on the hub feeds the remote branch. The key motor's
   supply current is below its 0.6 A coil current (chopper), so 1.1 A doesn't
   nuisance-trip, and a short on the cable or remote board trips it.
   Until the PTC arrives, a 1.6 A glass fuse takes its place (log
   2026-10-07).
6. **Emergency stop**: pull the 12 V plug. The button (Y_MIN) pauses a run;
   `!` on the serial line aborts the current move and switches all drivers
   off.

## 9. Diagrams

- **`control/harness/schematic.pdf`: the full wiring schematic**, 7 A4
  landscape sheets in colour, for printing. No text is below 8 pt. It covers
  the overview, power, dial drivers A–C, the DIAG-mod and UART-tap details,
  the Mega/RAMPS headers with the hub board, the cable with the key turner,
  and the tables. It is drawn from this file by `control/harness/schematic.py`
  (reportlab). **Regenerate it after any change here.**
- `control/harness/harness.yml` → `harness.svg` / `harness.png` (WireViz
  0.4.1): the inter-unit cable and both connector ends, plus the jumper
  connections from RAMPS to the hub.
- `control/harness/overview.dot` → `overview.svg` (Graphviz): block diagram
  of everything in this file.

Regenerate: `python3 control/harness/schematic.py` (needs `pip install
reportlab`), `wireviz control/harness/harness.yml` and
`dot -Tsvg control/harness/overview.dot -o control/harness/overview.svg`.

## 10. Shopping list (beyond `docs/bom.md`'s "still to buy")

Every discrete part, with what's ordered and what's already on the RAMPS
or the driver modules: `docs/bom.md`, "Electronics assembly — every
discrete part" (2026-10-07).

| Item | Qty | For |
|---|---|---|
| **Multimeter** — **on hand** (Paul, 2026-10-07). Use it before connecting the remote board | 1 | check 5 V/12 V polarity at the hub and remote board before plugging the driver in; cable continuity |
| F–F Dupont jumpers, 10–20 cm — **ordered** 2026-10-07 | ~20 | UART taps, DIAG leads (3 get cut in half for the mod), hub ↔ RAMPS |
| 2.54 mm female header strips (cuttable) — **on hand** (Paul, 2026-10-07) | 1 pack | remote driver sockets (2 × 1×8, 1 × 1×2) |
| 2.54 mm male header strips — **on hand** (Paul, 2026-10-07) | 1 pack | hub jumper pins, remote motor header |
| Radial PTC resettable fuse, ~1.1 A hold, rated ≥ 16 V (e.g. Bourns MF-R110 class) — **ordered** 2026-10-07; a 1.6 A glass fuse stands in until it arrives | 2 (1 spare) | remote 12 V branch |
| Electrolytic capacitor 100 µF, ≥ 25 V (35 V fine), low ESR — **ordered** 2026-10-07 | 2 (1 spare) | remote driver VM |
| Female DC barrel jack **5.5 × 2.1 mm** → screw terminal adapter (fits the Ledmo HTY-1200500 plug, centre positive) — **ordered** 2026-10-07 | 1 | PSU → hub without cutting the plug. Check its + / − marking against the multimeter before first use |
| 20 AWG wire, red + black, ~1 m each — **ordered** 2026-10-07 | 1 | PSU → hub → RAMPS 12 V |
| Solder — **on hand**: came with the station, with wick (Paul, 2026-10-07) | — | |
| Flush cutters — **on hand** (Paul, 2026-10-07) | 1 | DIAG pin mod |

## 11. Things to verify on the bench (steps in `control/bringup.md`)

- UART lead on the correct MS3 jumper pin (firmware `ping`).
- Which top-edge pin is DIAG (`ping` + a hand stall).
- Phoenix plug keying.
- Perfboard size, heatsink height, Phoenix plug overhang (for the mount).
- Motor step angle 1.8° (one commanded revolution returns to a mark).
- Motor direction vs dial numbering and vs key clockwise (firmware config).

## Sources

1. **Marlin** `Marlin/src/pins/ramps/pins_RAMPS.h`, bugfix-2.1.x at
   [`bbe7c65`](https://github.com/MarlinFirmware/Marlin/blob/bbe7c65573672d8efe49d7777e3ae221f38b6b55/Marlin/src/pins/ramps/pins_RAMPS.h)
   (2026-10-04): stepper, endstop and AUX-1…4 pin numbers; Serial2 on
   AUX4-17/18.
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

### 2026-10-07 — interim fuse for hub F1 (Paul)

- The PTC fuses are ordered, but no amazon.fr listing arrives soon
  (the first pick: 31 Oct – 5 Nov). Paul ordered **1.6 A glass cartridge
  fuses** to sit in F1's place until then, in a holder he prints (no clips
  ordered): an AUKENIEN kit, **T (slow-blow), 5 × 20 mm, 250 V**, 10 of
  each of 12 values from 0.5 to 10 A. Slow-blow is the right kind here,
  because the power-on charging surge into C1 is brief.
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
  Metal-to-metal contact on each end cap, held by spring pressure or by
  a screw threading into a metal nut, not into the plastic: PETG and PLA
  creep under steady load, so a clamp that bears only on plastic
  loosens. Don't solder to the end caps: the heat can melt the solder
  that holds the fuse wire inside.
- **C1 as ordered isn't sold as low ESR.** It's an Innfeeltech
  100 µF 35 V radial, 50 pcs; the listing gives no ESR, ripple-current or
  temperature rating. TMC2209 DS §3 recommends low-ESR electrolytics, with
  at least 100 µF near the driver (§3.5).
  - **Likely fine at the key's current** (0.6 A to start, ≤ 1.0 A),
    because the V1.3 module's own 2 × 10 µF ceramics sit right at the
    chip. This is a judgement, not a measurement: the cap's ESR is
    unknown.
  - **Proposed (Paul to decide):** fit **two in parallel**. That gives
    200 µF at half the ESR of one, and there are 50 in the pack. The
    ~70 × 30 mm remote board has room beside VM/GND (§6.1).
  - **Bench check at stage 5:** after a few minutes of key moves at the
    final current, touch C1. It should feel cool. If it's noticeably
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
