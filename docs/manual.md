# Fichet safe robot — build and operating manual

For Paul. Covers the robot as of **2026-10-06**: dial unit v2, key turner v1,
harness v1 (`control/wiring.md`), firmware **0.2**.

**Status:** nothing has run on hardware yet. The first time through, follow
the bench bring-up (`control/bringup.md`) instead of section 5. It builds
and tests the electronics one stage at a time, and its results fill in the
values that `config.h` still guesses. Every step here that rests on an
unchecked fact says **VERIFY** or **ASSUMPTION**.

**This manual is the procedure; the detailed docs are the reference.** If
the two ever disagree, the reference wins. Tell me, and I'll fix the
manual:

| Topic | Reference |
|---|---|
| Housings, print and fit history | `docs/housing_decisions.md` |
| Parts and orders | `docs/bom.md` |
| Wiring, pin map, currents, power order | `control/wiring.md` |
| Firmware commands and log lines | `control/firmware/README.md` |
| Values not yet measured | `control/firmware/safe_robot/config.h` |
| First power-up and tuning | `control/bringup.md` |
| How the robot works; open questions | `control/sequence.md` |

## Contents

0. [Read first: safety rules](#0-read-first-safety-rules)
1. [Mechanical assembly](#1-mechanical-assembly)
2. [Electrical assembly](#2-electrical-assembly)
3. [Building the software](#3-building-the-software)
4. [Loading the software onto the Mega](#4-loading-the-software-onto-the-mega)
5. [Operating and monitoring](#5-operating-and-monitoring)
6. [Quick reference](#6-quick-reference)

---

## 0. Read first: safety rules

1. **Plug or unplug anything with 12 V off.** That means motors, drivers and
   the inter-unit cable. A driver cut off from its supply while its motor
   turns can be damaged (TMC2209 datasheet §3).
2. **Power order:** USB first, then 12 V. To switch off: 12 V first, then USB.
3. **Emergency stop: pull the 12 V plug.** Typing `!` in the logger stops the
   current move and switches all drivers off. The button pauses a run after
   the current attempt.
4. **Keep forces low.** The lock has a relocker ("délateur") that blocks it
   for good if it's forced (`control/lock_research.md`). The firmware limits
   current and stops on stall, so never raise currents above what
   `control/bringup.md` sets.
5. **Fingers out of the gears** while 12 V is on.
6. **Fit drivers the right way round.** Match EN / DIR / VM / GND on the
   driver to the RAMPS silkscreen. A reversed driver is destroyed (BTT
   manual, safety note 1).

---

## 1. Mechanical assembly

There are two units:
- **Dial unit**: three motors turn the three dial plugs through 14T/28T
  gears. Each plug is on a spring-loaded shaft running in two 608 bearings.
  The Mega and RAMPS sit on a deck at the back.
- **Key turner**: one motor straight on the key axis. A printed cap slides
  over the key's bow.

Both hold to the door with 22 mm rubber-coated M4 pot magnets: 6 on the dial
unit, 3 on the key turner. Design history: `docs/housing_decisions.md`.
Renders (drawn before the magnet change): `cad/renders/dial_unit_v2_section.png`,
`cad/renders/dial_unit_v2_door_view.png`,
`cad/renders/key_turner_v1_overview.png`.

### 1.1 What to print

Print from the per-part STLs in `cad/`. Material and orientation are from
the print notes in `cad/dial_unit_housing.scad` (end of file) and
`cad/key_turner_housing.scad` (end of file).

| STL | Part | Qty | Material | Bed side |
|---|---|---|---|---|
| `dial_front_assembly.stl` | dial front plate: 6 magnet holes, 3 bearing bosses, 3 legs, pointer tab | 1 | PETG | door face |
| `dial_motor_sled.stl` | motor sled + 3 deck legs | 1 | PETG | inner face (spring pockets, countersinks); legs up |
| `electronics_deck.stl` | deck for the Mega | 1 | PETG | flat, mating face down |
| `dial_drivetrain.stl` | 3 gear-shafts + 3 pinions, one plate | 1 plate | **PETG-CF** | gear face / pinion hub. **Elephant-foot compensation on**, or the bottom layer of the teeth binds |
| `magnet_retainers.stl` | 10 retainer discs (9 needed) | 1 plate | PETG | flat |
| `key_turner_base.stl` | key-turner base + 3 legs | 1 | PETG | door face |
| `key_turner_motor_plate.stl` | key motor plate | 1 | PETG | inner face |
| `key_turner_cap.stl` | slotted cap | 1 | **PETG-CF** | slot mouth. **Elephant-foot compensation on** |
| `key_turner_hub.stl` | grooved motor hub | 1 | **PETG-CF** | groove face |

PETG-CF needs the hardened (tungsten carbide) hotend.

**Slicer:** Bambu Studio's default settings for the H2D, which is what
you've used so far (Paul, 2026-10-06). Turn on elephant-foot compensation
where the table says so.

**Don't print:**
- `dial_unit_housing.stl` and `key_turner_housing.stl`: whole-unit layouts
  that mix PETG and PETG-CF parts;
- `standoff_screw_fit_test.stl`, `printed_thread_test.stl` and
  `tube_socket_test_key_set.stl`: old test pieces;
- `Fichet_robot.3mf` and `dial_unit_housing.3mf`: pre-v2 geometry.

**Already printed and passed** (`docs/housing_decisions.md`):
- the door-pattern test (2026-10-05: "plate fits the door perfectly and all
  three dial turners turn easily");
- the key fit test (2026-10-06: the cap slides on and turns the key to its
  stop);
- the Mega base coupon (2026-10-04: 3 of 4 screws go in; 3 are enough).

**Needs a reprint for the magnets:** the dial front assembly and the
key-turner base (both changed 2026-10-06), plus the retainers.

### 1.2 Hardware

| Item | Dial unit | Key turner | Status |
|---|---|---|---|
| 608 bearings (8 × 22 × 7) | 6 (2 per dial) | — | on hand |
| Compression springs ≤ 8 mm OD, ~18–20 mm free, solid < 10 mm | 3 | — | ordered: QUARKZMAN 0.5 × 7 × 20 mm, 304 stainless, arriving 2026-10-07 (Paul). Count the coils on arrival |
| M3 × 10 countersunk, hex socket (motor screws; the length includes the head) | 12 | 4 | on hand (kit has 55) |
| M6 countersunk self-tapping, 16 mm | 6 | 3 | on hand. On the key turner, 16 mm works better than the 20 mm the CAD notes listed (Paul, 2026-10-06) |
| M3 × 6–8, self-tapping into PETG (Mega base plate to deck) | 4 (3 go in) | — | on hand |
| M3 × 3 or × 4 **grub** screws (pinion / hub), optional | 3 | 1 | optional. **Never a cap screw**: its head would hit the gear |
| 22 mm rubber pot magnets, M4 back (Wukong) | 6 | 3 | ordered |
| M4 screws for the magnets | 6 | 3 | the ones in the magnet pack, if any. Otherwise flat or pan head, length = 3 mm (retainer) + the magnet's thread depth. Measure it; the screw must not bottom out |
| Motors 17HE19-2004S | 3 | 1 | on hand (+1 spare) |

### 1.3 Checks before the big parts

1. **Magnets** (`docs/housing_decisions.md`, 2026-10-06):
   1. Measure one magnet's diameter, height and thread depth. If they're
      not 22 mm and 6 mm, tell me before printing: the holes are sized from
      the listing.
   2. **Pull test:** stick one magnet on the door and pull *sideways*
      (along the door) with the luggage scale. **If it slips under about
      0.8 kg**, the units need more magnets or a floor leg before the robot
      runs.

   Send me the three measurements and the slip force.
2. **Springs:** count the coils, and check the spring closes to under 10 mm.
3. **First M6 into a printed leg: drive it by hand**, not with a power
   driver, and check the leg doesn't crack. The legs have ~3.3 mm of wall
   around the 5.4 mm pilot (`docs/bom.md`).

### 1.4 Dial unit

**ASSUMPTION: the order below is derived from the CAD.** The repo has no
written assembly order for the dial unit (the pointer to one in
`dial_unit_housing.scad` leads nowhere). Two things fix the order:
- the motor screws go in from the sled's inner face, so the motors must be
  on the sled before it's joined to the front;
- the magnets sit under the sled's outline, so they go in first.

Tell me if a different order works better, and I'll record it.

1. **Magnets.** Put each magnet in its through hole in the front plate,
   rubber face toward the door. Lay a retainer disc on the seat ring, then
   drive an M4 screw through the retainer into the magnet's back. The ring
   sets the depth: the rubber ends up 0.2 mm proud of the door face. The
   door's pull goes magnet → screw → retainer → ring.
2. **Bearings.** Press two 608s into each boss from the back (the boss top).
   A 2 mm lip on the door side stops the outer ring. It's a light press fit
   (22.15 mm pocket).
3. **Gear-shafts.** Slide each gear-shaft into its bearings from the back,
   plug first. Its Ø11 spacer stops on the rear bearing's inner ring: that's
   the plug's forward position. Each shaft slides 7 mm back from there; it
   must slide freely.
4. **Motors on the sled.** Each motor goes on the sled's outer face, its
   front boss in the recess. Four M3 × 10 countersunk screws go in from the
   sled's **inner** face. Before tightening, turn each motor in 90° steps so
   its cable leaves into a free gap. Which motor is A, B and C follows the
   holes: A top-left, B top-right, C bottom. **Label each motor's cable.**
5. **Pinions.** Push each pinion onto its motor shaft, hub end first, until
   it stops. The D-shaped bore stops where the shaft's flat ends, and that
   sets its position. The grub screw is optional: the pinion is trapped
   between the sled and the boss tops.
6. **Springs.** Sit one spring in each gear's rear pocket (Ø8.6, 2 mm deep).
7. **Join sled to front.** Bring the sled down onto the three front legs.
   Each pinion has to mesh with its gear, and each spring has to go into
   the sled's pocket. The screw pattern is asymmetric, so it fits only one
   way. Drive three M6 countersunk (~16 mm) from the sled's outer face into
   the legs, the first by hand.
8. **Check by hand:**
   - Push each plug in from the door side. It should go back about 7 mm and
     spring forward again.
   - Turn each plug by hand from the door side, a full turn. It turns its
     motor through the gears, so expect the motor's slight notchiness, but
     no tight spot.
9. **Deck.** Three M6 countersunk (~16 mm) through the deck's top face into
   the deck legs. Do this *before* fitting the Mega base plate: two of the
   three screws sit under it (`docs/housing_decisions.md`, 2026-10-04).
10. **Mega.** Screw the Mega's plastic base plate to the deck with the M3
    self-tappers (3 of the 4 go in). Its position and turn are fixed by the
    pilot holes ("Jack/USB end faces up-right" in `dial_unit_housing.scad`).
    **VERIFY** that you can reach the USB and RAMPS connectors there; that
    hasn't been checked.
11. **Not designed yet:** where the hub board (2.5) and the start button go
    on the deck. Fix them temporarily (double-sided tape) until the CAD has
    a place (1.7).

### 1.5 Key turner

From the notes at the end of `cad/key_turner_housing.scad`:

1. **Magnets.** Three, in the base, the same way as on the dial unit
   (retainer + M4).
2. **Motor onto the motor plate.** Four M3 × 10 countersunk from the plate's
   inner face.
3. **Hub onto the shaft.** Its D-bore sits entirely on the shaft's flat.
   Push it on until the shaft tip bottoms in the bore. The grub screw is
   optional.
4. **Plate onto the legs.** Three M6 × 16 countersunk self-tappers, the first
   by hand. That's 10 mm of thread in each leg, as on the dial unit.
5. **Cap.** It's a loose part that sits between the key and the hub: its
   slot takes the bow, and its tongue sits in the hub's groove. It lets the
   unit sit up to 2.7 mm off the key axis without side-loading the lock.
6. **Not designed yet:** the mount for the remote driver board
   (`control/wiring.md` §6.2: ~70 × 30 mm, ~30 mm tall plus 10 mm of air,
   Phoenix plug facing the dial unit, magnet retainers left reachable).

### 1.6 Putting the units on the door

1. **12 V off**, cable unplugged.
2. **Key** in the lock by hand, at its start position (bow vertical).
3. **Dial unit:** pointer tab **up** (it points at the top pair of holes).
   Bring it straight onto the door over the three dial holes and let the
   magnets take it. A plug that doesn't line up with its star is pushed
   back on its spring; the plate still seats flat. The robot's seat routine
   turns each plug slowly until it drops in.
4. **Key turner:** turn the cap so its two roof marks are **top and bottom**
   (its slot is then vertical, like the bow). Slide the unit straight on
   over the key. The keyhole is about 125 mm left of the dial-cluster
   centre, and the base reaches 43 mm toward the dials, so the two units
   don't touch.

   **VERIFY:** the cap's tongue sits in a through-groove in the hub, so the
   cap may slide out while you hold the unit. If it does, put the cap on the
   bow first (marks top and bottom), then slide the unit on. Turn the hub
   by hand (motor unpowered) until its groove takes the cap's tongue.
5. Plug in the inter-unit cable. Zip-tie it within about 20 mm of each plug,
   clear of the cap.

### 1.7 Mechanical items still open

- Magnet pull test (1.3), and whether the magnets alone hold the units.
- Reprint the dial front assembly and key-turner base with magnet holes.
- CAD: mount for the remote driver board; a place on the deck for the hub
  board and the button.
- Access to the Mega's connectors at its position on the deck.
- Only if the first full run fails: a key turner that pulls the key out and
  pushes it back in at every attempt (`control/sequence.md`, Open items).

---

## 2. Electrical assembly

The full design, with sources, is `control/wiring.md`. Diagrams:
`control/harness/overview.svg` (block diagram) and
`control/harness/harness.png` (cable and connector ends).

### 2.1 Build it in bring-up order

Don't wire everything and then switch on. Each block below is tested by a
bring-up stage before the next one is added:

| Build | Then test with |
|---|---|
| 2.3 Drivers: DIAG mod, heatsinks, jumpers. Flash the firmware (section 4) | `control/bringup.md` stage 0 |
| 2.4 Mega + RAMPS + one driver; 2.5 hub board; 2.7 power; 2.8 jumpers | stage 1 (one driver, then three) |
| 2.9 one motor on the bench | stages 2 and 3 |
| Dial unit assembled (section 1) with its three motors | stage 4 |
| 2.6 remote board, 2.10 inter-unit cable, key turner (section 1) | stage 5 |
| Everything on the door | stage 6 (short dry run) |

### 2.2 Tools and parts

- Soldering station, solder, flush cutters, heat shrink and heat gun,
  calipers, a marker.
- **Multimeter: buy it before connecting the remote driver board**
  (`control/wiring.md` §10). Sections 2.5, 2.6 and 2.10 need it for
  polarity and continuity checks.
- Parts: `docs/bom.md`, plus the harness parts in `control/wiring.md` §10:
  - 2.54 mm female and male header strips;
  - 1.1 A PTC fuse;
  - 100 µF ≥ 25 V capacitor;
  - 5.5 × 2.1 mm DC-jack-to-screw-terminal adapter;
  - 20 AWG red and black wire;
  - F–F jumpers.

### 2.3 Prepare the drivers (BTT TMC2209 V1.3)

There are five drivers: three for the dials, one for the key turner, one spare.

1. **DIAG mod, on the three dial drivers only** (`control/wiring.md` §3.3):
   do this before fitting the heatsinks.
   1. Two short pins point *down* at the EN end: INDEX and DIAG. Cut both
      flush with their plastic spacer.
   2. Cut an F–F jumper in half. Strip 2–3 mm and tin it.
   3. Solder it to the **top-side joint of the pin labelled DIAG** (second
      from the EN corner). Keep the iron off the trimmer pot next to it.

   Leave the key-turner driver and the spare untouched: the remote board
   has a socket for the down-pointing pin.
   **VERIFY:** which pin is DIAG. Stage 3 confirms it.
2. **Heatsinks** on all drivers you'll use. At ≤ 1 A RMS no fan is needed
   (BTT: active cooling above 1.2 A).
3. **Don't bridge R10** on any driver (`control/wiring.md` §2).

### 2.4 Mega, RAMPS and the dial drivers

1. **RAMPS jumpers**, under the X, Y and Z sockets. They set each driver's
   UART address (TMC2209 datasheet §3.4):

   | Socket | Dial | MS1 | MS2 | MS3 | Address |
   |---|---|---|---|---|---|
   | X | A (top-left) | off | off | **off** | 0 |
   | Y | B (top-right) | **on** | off | **off** | 1 |
   | Z | C (bottom) | off | **on** | **off** | 2 |

   **Never fit an MS3 jumper.** On the V1.3, the MS3 position is the UART
   line, and a jumper there would tie the UART line to 5 V.
2. Press the RAMPS onto the Mega.
3. Plug each driver into its socket, **EN / DIR / VM / GND matching the
   silkscreen**. Leave E0 and E1 empty.
4. **Mount the Mega**: four M3 × 6–8 screws go through the Mega's own
   plastic base into the electronics deck. Three are enough
   (`docs/bom.md`, 2026-10-04).

### 2.5 Hub board (dial end)

A small perfboard, about 50 × 30 mm, next to the Mega. It's where the 12 V
supply splits, it holds the one UART resistor, and it carries the cable's
8-pin Phoenix header (`control/wiring.md` §5). The layout is free; keep R1
right at the TX2 pin.

| Hub point | Connects to |
|---|---|
| 12V IN + / − | PSU, through the 5.5 × 2.1 DC-jack adapter (centre +), 20 AWG |
| 12V OUT + / − | RAMPS power terminal, the pair marked **5A**, 20 AWG |
| F1 (1.1 A PTC) | 12V IN + → F1 → Phoenix pin 1 |
| R1 (1 kΩ) | TX2 pin → R1 → BUS |
| TX2 pin | AUX-4 pin 18 (D16) |
| BUS pins × 4 | RX2 = AUX-4 pin 17 (D17); the X, Y and Z **MS3 jumper pins** (see 2.8); Phoenix pin 6 |
| STEP pin | AUX-4 pin 16 (D23) → Phoenix pin 5 |
| DIAG pin | Z_MAX **S** (D19) ← Phoenix pin 7 |
| 5V pin | Y_MAX **+** → Phoenix pin 4 |
| GND pin | Y_MAX **−** → hub GND; also Phoenix pins 2 and 8, and 12V IN − |

Use 2.54 mm male header pins for the jumper ends. **Where it mounts on the
deck isn't designed yet** (mechanical to-do; see 1.7).

### 2.6 Remote driver board (key turner)

A perfboard of about 70 × 30 mm. The driver plugs into female headers, so it
can be swapped. Follow the layout in `control/wiring.md` §6.1 exactly.
In short:

| Driver pin | Goes to |
|---|---|
| EN, DIR, CLK | GND |
| MS1, MS2 | +5 V (sets UART address 3) |
| RX (= PDN_UART) | Phoenix 6 |
| TX | nothing |
| STEP | Phoenix 5 |
| DIAG (its own down-pointing pin, in a 2-pin socket) | Phoenix 7 |
| VM | Phoenix 1, and C1 + (100 µF) |
| GND (both) | Phoenix 2, and C1 − |
| VIO | Phoenix 4 |
| A2, A1, B1, B2 | 4-pin motor header, same order as a RAMPS motor header |

1. **VERIFY before soldering the headers**: lay the driver on the perfboard
   and check that INDEX/DIAG fall on the 2.54 mm grid.
2. **Before its first power-up**: turn the driver's VREF pot to minimum.
   Its EN is tied low, so it switches on at its power-up current as soon as
   12 V arrives, until the firmware sets the real one (`control/wiring.md`
   §8).
3. With the multimeter, check there's no short between Phoenix pins 1, 2
   and 4 before plugging the driver in.

**Where it mounts on the key turner isn't designed yet**
(`control/wiring.md` §6.2 lists the size and needs; see 1.7).

### 2.7 Power wiring

PSU (Ledmo HTY-1200500, 12 V 5 A, 5.5 × 2.1 mm barrel, centre +) → DC-jack
adapter → hub 12V IN → hub 12V OUT → RAMPS **5A** terminal. Use 20 AWG red
for + and black for −.

**Check the adapter's + / − marking with the multimeter** before the first
power-up (`control/wiring.md` §10).

### 2.8 Signal jumpers on the RAMPS

Use F–F jumpers about 10 cm long. The RAMPS endstop headers are
**S** (signal), **−** (GND) and **+** (5 V).

| From | To |
|---|---|
| Dial A driver DIAG lead (from the 2.3 mod) | **X_MIN S** (D3) |
| Dial B driver DIAG lead | **X_MAX S** (D2) |
| Dial C driver DIAG lead | **Z_MIN S** (D18) |
| X, Y, Z **MS3 jumper pin**, signal side (nearer the driver's EN/STEP/DIR row) | hub BUS |
| AUX-4 pins 18 / 17 / 16 (D16 / D17 / D23) | hub TX2 / BUS / STEP |
| Z_MAX S (D19) | hub DIAG |
| Y_MAX + / − | hub 5V / GND |
| Start/stop button (7 mm pushbutton) | **Y_MIN S** and **Y_MIN −** (D14) |

**VERIFY:** which MS3 pin is the signal side on your Fasizi board. If
`ping` gets no answer in stage 1, move the lead to the other pin. The wrong
pin is the 5 V side, which does no harm.

**ASSUMPTION:** where the button mounts is not designed yet. A loose button
on its leads is fine for the bench.

### 2.9 Motors

- **Dials**: dial A's motor goes on the **X** motor header, B on **Y**, C
  on **Z**. The key motor goes on the remote board's 4-pin header.
- If a motor **buzzes or jitters instead of turning**: 12 V off, then swap
  the two middle wires in its connector. Some 17HE19-2004S motors have them
  swapped (`docs/bom.md`).
- Motor currents are set by the firmware over UART, so the drivers' VREF
  pots don't matter once it runs (`control/wiring.md` §7). Dials run at
  1.0 A RMS; the key starts at 0.6 A, and stage 5 sets its final value.

### 2.10 Inter-unit cable

QUARKZMAN 22 AWG shielded 6-core. Cut **about 300 mm** and strip 30 mm of
jacket at each end. It's wired **straight through**: same pin numbers at
both ends (`control/wiring.md` §4).

| Pin | Signal | Colour |
|---|---|---|
| 1 | +12 V (after the PTC) | red |
| 2 | GND | black |
| 3 | — empty | — |
| 4 | +5 V (VIO) | orange |
| 5 | KEY_STEP | yellow |
| 6 | UART bus | green |
| 7 | KEY_DIAG | white |
| 8 | shield drain: **hub end only**; at the remote end fold it back under heat shrink | shield |

1. Mark pin 1 on both plug halves. **VERIFY** that the plug fits only one way.
2. Zip-tie the cable to each housing within about 20 mm of the plug. Keep it
   clear of the key cap's rotation.
3. With the multimeter, check continuity pin to pin, and no short between
   neighbouring pins.

---

## 3. Building the software

There are three pieces:

- **The firmware** (`control/firmware/safe_robot/`) runs on the Mega.
- **The logger** (`control/firmware/tools/logger.py`) runs on your Mac. It
  saves every line the robot prints and lets you type commands.
- **Host tests** (`control/firmware/test/`) are optional. They check the
  firmware's logic on the Mac against a simulated lock.

Written for a Mac (Paul, 2026-10-06).

### 3.1 Get the code

- With git (it comes with the Mac's command-line tools):
  `git clone https://github.com/paulforrester/fichet-safe-robot.git`.
  To update later: `git checkout main`, then `git pull`.
- Without git: on the repo's GitHub page, Code → Download ZIP.

Always build from `main` after I tell you a PR is merged.

### 3.2 Arduino IDE (once)

1. Install Arduino IDE 2 from arduino.cc.
2. Tools → Board: if **Arduino Mega or Mega 2560** isn't listed, open
   Boards Manager and install **Arduino AVR Boards**.
3. Tools → Manage Libraries → search **TMCStepper** (by teemuatlut) → choose
   version **0.7.3** → Install. That's the version the firmware was built
   and checked against; `control/firmware/README.md` says why. SPI,
   SoftwareSerial and EEPROM come with the board package.

### 3.3 Compile

1. File → Open → `control/firmware/safe_robot/safe_robot.ino`. The IDE
   also compiles everything under `safe_robot/src/`. Those files don't
   show as tabs, which is normal.
2. Tools → Board → **Arduino Mega or Mega 2560**. Tools → Processor →
   **ATmega2560 (Mega 2560)**.
3. Click **Verify** (✓). Expect "Sketch uses about 51 KB (20%) of program
   storage space" and "Global variables use about 1.4 KB (16%)". The
   checked build gave 51,480 and 1,356 bytes; the IDE's compiler may differ
   by a little. Any error means something's wrong: send me the text.

### 3.4 Changing settings

- **Every value that isn't measured yet is in
  `control/firmware/safe_robot/config.h`**, in one block, with where each
  came from. Bring-up gives the real numbers. I'll normally send them as a
  PR. If you edit it yourself, change only the numbers and recompile.
- To try a value without recompiling, use `set <name> <value>` in the
  logger (the names are in `control/firmware/README.md`). It's lost at the
  next reset, so copy the good value into `config.h` afterwards.

### 3.5 The logger (once)

The logger needs Python 3 and pyserial. Install pyserial in its own folder
(a "venv") so it can't clash with anything else on the Mac:

```
python3 -m venv ~/safe-robot-venv
~/safe-robot-venv/bin/python -m pip install pyserial
```

If `python3` asks to install the command-line developer tools, say yes. To
check: `~/safe-robot-venv/bin/python control/firmware/tools/logger.py --help`.

### 3.6 Host tests (optional)

These need the command-line tools (`xcode-select --install`). From the repo
folder:

```
make -C control/firmware/test
~/safe-robot-venv/bin/python -m pip install pytest        # once
~/safe-robot-venv/bin/python -m pytest control/firmware/tools
```

Expect `45 tests, 36127 checks, 0 failures` and `3 passed`. I check these
in every PR (also built with clang, which is the Mac's compiler). Running
them yourself is only needed if you change the code.

---

## 4. Loading the software onto the Mega

### 4.1 Upload

1. **12 V off.** Connect only the USB cable (USB-C → USB-B). The RAMPS can
   stay on the Mega.
2. Close the logger and the IDE's Serial Monitor. Only one program can use
   the port, and an open port makes the upload fail.
3. Tools → Port → the Mega. On a Mac it looks like
   `/dev/cu.usbmodemXXXX (Arduino Mega or Mega 2560)`. The genuine Mega
   needs no driver.
4. Click **Upload** (→). It compiles, then uploads. Expect "Done
   uploading".

### 4.2 Check it's the right build

1. Start the logger (5.3). Opening the port restarts the Mega.
2. The first line is
   `# Fichet safe robot 0.2 (2026-10-06) - type help`. If it says 0.1, the
   old code is still on the Mega.
3. Type `status`. Expect `# state=IDLE run=… next=…`.
4. Type `cfg` to see the settings it was built with.

### 4.3 What an upload keeps

**An upload doesn't erase the stored progress or calibration.** They live in
the Mega's EEPROM, and the upload writes only program memory. The IDE runs
avrdude with `-D` and only a flash write (Arduino AVR core 1.8.6
`platform.txt`), and the Mega's bootloader refuses a chip erase
(`stk500boot.c`).

- If the new build changes a setting that defines the dial positions,
  `resume` stops with `CFGHASH`. Those settings are the dial directions,
  steps per turn, gearing, microsteps, positions per dial, home modes and
  click-finding on/off (and the home offsets, if click-finding is off).
  Then:
  - `resume force` if you know the positions still mean the same;
  - otherwise `reset yes` and start over.
- To wipe the stored progress on purpose: `reset yes`. The calibration is
  kept and re-measured every session anyway.

### 4.4 If the upload fails

- "Port busy", "not in sync" or "programmer is not responding": close the
  logger or Serial Monitor. Check the port, then retry.
- No port listed: try another USB cable (some are charge-only) or another
  USB port.

---

## 5. Operating and monitoring

### 5.1 Before the first real run

1. Complete `control/bringup.md` stages 0–6, sending me what each stage asks
   for.
2. I send back a `config.h` with the measured values (directions, key
   current, classification bands). Upload it (section 4).
3. Run `calibrate` once with everything on the door, as in 5.4.

**The biggest unknown:** whether a combination dialled with the key already
in counts. The safe's own manual dials with the key out
(`control/sequence.md`, Open items). The first full run is the real test.

### 5.2 Setting up for a session

Placing the units is described in more detail in 1.6.

1. 12 V off.
2. **Key:** insert the real key (it goes in one way only) and leave it at
   its start position. If it was left turned, turn it back anticlockwise by
   hand until it stops.
3. **Dial unit:** place it over the three dial holes, A top-left, B
   top-right, C bottom, and let the magnets take it. Plugs that don't line
   up with their star get pushed back on their springs. That's expected:
   the session start seats them.
4. **Key turner:** cap roof marks top and bottom, slide it over the key's
   bow, and let the magnets take it.
5. Plug in the inter-unit cable (12 V still off).
6. USB to the Mac. Start the logger (5.3).
7. 12 V on.
8. Type `ping`. Expect four lines starting `DRV,A,1,21`, `DRV,B,1,21`,
   `DRV,C,1,21` and `DRV,K,1,21`. The `1` means the driver answered; `21` is
   its version.

### 5.3 Starting the logger

```
cd fichet-safe-robot
ls /dev/cu.usbmodem*                        # find the port
caffeinate -i ~/safe-robot-venv/bin/python control/firmware/tools/logger.py --port /dev/cu.usbmodemXXXX
```

- **`caffeinate -i`** stops the Mac from sleeping while the logger runs.
  Keep the Mac on its charger with the lid open.
- **Files:** `runs/<date-time>_raw.log` holds every line, with the Mac's
  time; `runs/<date-time>_attempts.csv` has one row per attempt. Both grow
  as the run goes, so a crash or Ctrl-C loses nothing already written.
- **Commands:** type them in the logger window and press Return. `!` aborts
  at once.
- **On screen:** progress lines (`EV`, `ERR`, `HOME`, `LEARN`, `CAL`,
  `RECHECK`, `SUCCESS`, …), every attempt that isn't a clean fail, and
  every 50th attempt. A success also rings the terminal bell.
- **Opening the port restarts the Mega** (Arduino auto-reset). So start the
  logger *before* `start`, and don't quit and restart it during a run. If
  you do, the run stops, its progress is safe in EEPROM, and `resume`
  continues it.

### 5.4 Starting a run

**The very first time** (or if you get `TUNE … no key calibration yet`):
with the key at its start, type `calibrate`. It:
- turns the key 60° and back, onto its rest stop;
- seats the dials and turns each one once clockwise;
- homes each dial, prints `CAL` and `OFFSET` lines, and saves the result.

It ends with `# calibration saved`.

**A new run:** `start`, or press the button when nothing is stored. If a run
is already stored, `start` refuses: use `resume`, or `reset yes` to throw
the old run away.

**Continuing a stored run:** `resume`, or press the button.

Either way the robot first does the **session start**, about 40 s
(estimate):
1. checks all four drivers;
2. finds the key's rest stop (it searches up to 180°, because the key stays
   wherever it was left) and calibrates the key;
3. seats the dials, then turns each one free once to measure its load and
   find its clicks;
4. homes each dial on its stop, twice;
5. learns **N**, the angle where the key stops with a wrong combination
   (3 tries; `NSTOP` line).

Then the attempts begin (`EV,…,RUN,…`).

### 5.5 What a run does

- **Each attempt** turns **one dial by one click** (serpentine order, so no
  dial ever wraps from 20 back to 1). It then turns the key to N + 15°,
  records the angle reached, turns the key back to its start, and saves
  progress.
- **Every 200 attempts** it re-checks: it re-homes the dials and re-learns N.
  If anything moved, it stops and rewinds to the last good check (5.8).
- **8,000 combinations** in all.
  - **Time (estimate, not measured):** from the `config.h` speeds, motor
    movement alone is about 0.8 s per attempt, so about 1.8 h for all
    8,000, plus the re-checks. On average the right combination comes
    halfway. Stage 6 measures the real time.

### 5.6 Monitoring

- **Logger window:** a line every 50 attempts, for example
  `14:02:11 attempt 1250 4-13-7 101.3 deg (+0.4) CLEAN  [1250 logged]`.
  The `+0.4` is how far past N the key got, in degrees.
  Any non-clean attempt prints straight away.
- **`status`** works mid-run:
  `# state=RUN run=1 next=1250 verified=1200 attempts=… N=101.0 homed=ABCK`.
  `next` is the next combination; `verified` is the last good re-check.
- **LED**, the Mega's "L" LED (it may be hidden under the RAMPS):
  - fast blink: running;
  - slow blink: idle, paused, or all combinations done;
  - steady: success;
  - double blink: error.
- **Watch and listen** during the first runs: nothing should slide on the
  door, and no dial should ever move while the key is turned.

Attempt classes, all relative to this session's N (`config.h`;
stage 6 sets the bands):

| Class | Key reached | Robot does |
|---|---|---|
| CLEAN | up to N + 4° | next combination |
| FALSESET | between N + 4° and N + 10° | logs it and carries on. The raw angle is kept for later |
| SUCCESS | N + 10° or more | stops and holds the key (5.10) |
| EARLY | below N − 8° | retries. Three in a row: stops with `EARLY` (5.9) |

### 5.7 Pausing, stopping, aborting

| You want to | Do |
|---|---|
| Stop cleanly (to leave it, or move something) | press the button, or type `pause`. It finishes the attempt, re-checks, then switches the drivers off. Nothing is lost |
| Stop a move *now* | type `!` (or `abort`). Drivers off; `resume` continues from the last check |
| Emergency | pull the 12 V plug |
| Finish for the day | `pause`, wait for it, then 12 V off, then USB |

A run can be left paused with power off for as long as you like. Progress is
in EEPROM.

### 5.8 Resuming after a pause, power cut, reset or re-seat

1. Make sure both units are seated on the door. If one was knocked, re-place
   it.
2. Power up in order (USB, logger, 12 V).
3. Type `resume` (or press the button). It redoes the session start, rewinds
   to the last good re-check (≤ 200 attempts redone), and carries on.

After a power cut mid-attempt the key may be left turned. That's fine: the
session start finds its rest stop from anywhere in its travel.

### 5.9 Errors

An error prints `ERR,<time>,<code>,<text>`, switches all drivers off, and
double-blinks the LED. Fix the cause, then `resume` (or `ping`, to clear
the error before a bench command). If you're not sure, send me the raw log.

| Code | Meaning | What to do |
|---|---|---|
| DRIVER | a driver didn't answer, or has the wrong address | 12 V on? Cable plugged? UART leads and jumpers (2.4, 2.8)? Then `ping` |
| CONFIG, DIR | a driver setting didn't read back over UART | check the UART leads; `ping`; retry |
| DIAG | a stall line was already high before a move | DIAG lead off, or driver fault. Check the lead; `ping` shows both readings |
| TUNE | no stall threshold, or no key calibration yet | `calibrate`, with the key at its start (5.4) |
| KEYHOME | the key found no rest stop | key not inserted, or the cap slipped off the bow? Re-seat; `resume` |
| KEYCAL | key calibration failed | key not at its start? Turn it back by hand; `resume` |
| SGCAL | a dial's calibration turn failed | plug jammed or not seated? Re-place the dial unit; `resume` |
| HOME, HOMEREP | homing didn't find the stop, or the two passes disagree | plug not seated, or the unit moved. Re-place; `resume` |
| JAM | unexpected stall mid-move | something blocking? Look, clear it, `resume` |
| TIMEOUT | a move took too long | `resume`; if it repeats, send me the log |
| KEYOUT | refused to turn dials with the key out of rest | a protection. `resume` (the session start homes the key) |
| LEARN | N didn't repeat within 5° | key turner loose? Re-seat; `resume` |
| EARLY | the key stopped well short of N three times | a unit has moved. Re-seat both; `resume` |
| RECHECK | a re-check found a dial home or N moved | it has already rewound to the last good check. Re-seat; `resume` |
| CFGHASH | dial position settings changed since the run started | see 4.3 |
| NOHOME | (only if a dial's home mode is set to "no stop") | `resume force` or `reset yes` |
| ABORT | you typed `!` | `resume` when ready |

### 5.10 Success

The logger rings and prints:

```
SUCCESS,<time>,<index>,<a>,<b>,<c>,<key deg>,<doorA>,<doorB>,<doorC>
```

The robot holds the key where it got to. The success is saved in EEPROM,
so it's shown again at every restart until `reset yes`.

1. **Write the combination down**: dials A, B, C as positions 1–20 (see
   below). Keep the raw log.
2. Type `release`. The motors switch off, and the key stays where it is
   (no spring back).
3. 12 V off, then take the key turner off its magnets. Don't turn the key
   back, and leave the dial unit where it is.
4. As the safe's manual says: turn the key on clockwise by hand, then
   **pull on the key** to open the door.
5. **Before you ever close the door again**, check you can do it by hand
   with the door open: dial the combination, insert the key, and turn it
   clockwise past ~100°.

**Positions:** there are no marks on the door, so the robot counts clicks.
To set position *p* on a dial by hand, turn it anticlockwise until it
stops, then clockwise, counting clicks: position *p* is the *p*-th click.
If a click sits right at the stop, the robot doesn't count it. So **if the
hand-dialled combination doesn't work, try one click either side on each
dial**.

### 5.11 All 8,000 tried, no success

The run ends with `EV,…,DONE` and the state shows `DONE`.

1. Run `logger.py --analyse` on the run's attempts CSV (5.12).
2. Send me both run files.

The first suspect is the biggest unknown above: a combination dialled with
the key in may not count. The next suspects are a dial parked between
clicks, and the success band. The angles logged on every attempt let us
tell these apart.

### 5.12 After a run: analysis and what to send

```
~/safe-robot-venv/bin/python control/firmware/tools/logger.py --analyse runs/<stamp>_attempts.csv
```

It re-classifies every attempt from its raw angle, using the spread of this
run's clean fails. It prints the counts and the 20 attempts that got
furthest past N. A false set or a near-miss shows up there.

Send me the `runs/<stamp>_raw.log` and `_attempts.csv` from any run that
did something unexpected.

If you lost the CSV, rebuild it from the raw log:
`logger.py --replay runs/<stamp>_raw.log`.

### 5.13 Taking the robot off the door

1. `pause` (if running), wait for it, then 12 V off, then USB.
2. Unplug the inter-unit cable.
3. Pull each unit straight off the door, peeling from one edge if the
   magnets hold hard. Don't slide it along the door: the plugs are in the
   stars.
4. Turn the key back to its start by hand and pull it out. It only comes
   out at the start.

---

## 6. Quick reference

**Power:** on = USB, logger, 12 V. Off = 12 V, then USB. Never plug or
unplug with 12 V on. Emergency: pull the 12 V plug.

**Session:** key in at its start → dial unit on → key turner on → cable →
USB → logger → 12 V → `ping` → `resume` (or `start` for a new run; the
first time ever, `calibrate` first).

| Command | What |
|---|---|
| `help`, `status`, `cfg` | list commands; state and progress; settings |
| `ping` | check all four drivers |
| `calibrate` | key + dials, saved to EEPROM (key must be at its start) |
| `start` | new run from combination 0 |
| `resume [force]` | continue the stored run |
| `pause` or the button | stop after this attempt, re-check, drivers off |
| `!` or `abort` | stop the current move now, drivers off |
| `release` | all drivers off (also lets go of the key after a success) |
| `reset yes` | erase the stored progress |
| `seat`, `home [A\|B\|C]`, `learn`, `goto a b c`, `try`, `key <deg>`, `jog`, `sg`, `set` | bench commands: `control/firmware/README.md` and `control/bringup.md` |

**LED:** fast blink running · slow blink idle, paused or done · steady
success · double blink error.

**Logger:** `caffeinate -i ~/safe-robot-venv/bin/python
control/firmware/tools/logger.py --port /dev/cu.usbmodemXXXX`.
