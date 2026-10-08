# Fichet safe robot — build and operating manual

> **Revision 2026-10-08.2** · key driver on the RAMPS E0 socket; UART pigtail replaces the hub board · log: `docs/revisions.md`

For Paul. Covers the robot as of **revision 2026-10-08.2**: dial unit v2, key
turner v1, wiring with all four drivers on the RAMPS and the UART pigtail
(`control/wiring.md`), firmware **0.4** (unchanged by 2026-10-08.2).

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

1. **Plug or unplug anything with 12 V off.** That means every motor (the
   key motor cable included) and the drivers. A driver cut off from its
   supply while its motor turns can be damaged (TMC2209 datasheet §3).
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

**Magnet holes:** the dial front assembly and key-turner base you already
printed (22.4 mm holes) stay in use, with a 2-layer wrap strip on each
magnet (§1.3a). The current STLs have 21.7 mm holes, for any future reprint
(no strips needed then). Print the retainers if you haven't yet.

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
| M4 screws for the magnets | 6 | 3 | the ones in the magnet pack, if any. Otherwise **pan, button or socket head — not countersunk** (the retainer is flat). Length: see §1.3a. Any head up to 9 mm across and 6 mm tall clears the other parts on both units (CAD check, 2026-10-07) |
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

### 1.3a Fitting the door magnets (both units)

How it works: each magnet sits in a **through hole** in the plate. On the
plate's inner face a raised **seat ring** (29 mm across) stands around each
hole. A flat printed **retainer disc** (27 mm, 3 mm thick) lies on the ring,
and an M4 screw through the retainer into the magnet's threaded back holds
the magnet up against it. The ring's top sets the depth, so the rubber ends
up 0.2 mm proud of the door face. On the door, the pull goes magnet →
screw → retainer → ring (`common_mounts.scad`, `rmag_*`). The dial front
plate has 6, the key-turner base 3.

**Measure first** (one magnet, calipers):
- **Diameter D.** Measured 21.5 mm (Paul, 2026-10-07). The holes are now
  **21.7 mm**, chosen from the fit-test strip (snug at 21.8, worked in at
  21.7): the rubber grips, so the magnet can't slide out of the inner side.
- **Height H: measured 6.0–6.1 mm, back flush, no boss** (Paul,
  2026-10-07). The rubber stands 0.2–0.3 mm proud: fine. For reference, the
  rule: the magnet's back must be
  level with the ring top (5.8 mm above the door face), so the rubber stands
  H − 5.8 proud. 5.9–6.3 mm is fine (0.1–0.5 proud). Under 5.9 the rubber
  would sit flush or below the plate; over 6.3 the dial plugs sit too
  shallow in the stars. Either way, tell me before fitting: it's one number
  in the CAD and a reprint.
- **Thread depth T** (depth rod into the threaded hole).
- **Screw length** = 3 (retainer) + T − 0.5, rounded **down** to a length
  you have. It must not bottom in the hole, or it stops before it clamps.
  Example: T = 4 → 6.5 → use M4 × 6.

**Before you start:**
- Work on a wooden or plastic table, no steel within ~20 cm. Keep the
  magnets apart: they snap together hard and pinch fingers.
- Look at every seat ring top. It sets the depth, so it must be flat:
  trim any string or blob with a blade. Trim any elephant's foot inside the
  hole at the door face too: the magnet has to go in from that side.
- Check the retainers: the screw should pass through the 4.5 mm hole freely.

**Which plates you have:**
- **Plates printed before 2026-10-07 (22.4 mm holes; the ones in use):**
  wrap each magnet's side once with a **2-layer wrap strip**
  (`cad/magnet_wrap_strips.stl`, 69 × 5 mm × 0.4 mm, PLA; Paul: "the
  2-layer version is perfect"). Wrap it round the middle of the magnet's
  side, ends overlapping, then follow the steps below. The strip goes into
  the hole with the magnet.
- **Plates reprinted from the current STLs (21.7 mm holes):** no strip.
  The hole grips the rubber directly.

Nine strips cover both units (6 + 3); print a couple of spares.

**Steps (per plate).** The hole grips the magnet, so its depth is set by
how far you press it in. The table sets it for you:
1. Lay the plate **inner face down** on the table, so the seat-ring tops sit
   flat on it.
2. From the door side, press a magnet into a hole, **threaded back first**,
   until its back stops on the table. Its back is now level with the ring
   top, and the rubber stands just proud of the door face. Press straight;
   a thumb is usually enough. If it's very stiff, press with a flat block of
   wood over the rubber.
3. Repeat for every hole, then turn the plate over (inner face up).
4. Lay a retainer on each ring, centred on the thread. It rests on the ring
   and on the magnet's back together.
5. Start the M4 screw by hand, then snug it with a screwdriver until the
   retainer can't turn. **Snug, not tight**: the retainer is PETG and the
   thread is in the magnet. No thread-locker (some attack plastic).
6. **Check:**
   - Every retainer sits flat on its ring, no gap.
   - Put the plate door face down on the table and slide a sheet of
     printer paper under its edge between two magnets: it should go under
     (the plate rests on the magnets, not on its face). Do it all round.
   - Turn the plate on its side and shake it gently: nothing moves.
     **Correction (2026-10-07):** an earlier version said a magnet moving
     inward was fine. It wasn't: in the old 22.4 mm holes the 21.5 mm
     magnets and their retainers fell out of the inner side when the unit
     was off the door (Paul). That's why the holes are now 21.7 mm.
7. **Order:** on the dial unit, fit the magnets before anything else (they're
   under the sled). On the key turner, before the motor plate goes on.

**Pull test (once, before the robot runs; §1.3 item 1):**
1. One magnet with its screw part-way in. Tie a loop of string round the
   screw under its head.
2. Stick the magnet flat on the door where the units go.
3. Hook the luggage scale in the loop and pull **along** the door face
   (sideways, not away from it), slowly, until it slides. Note the peak.
4. Three times, plus once pulling straight down. Send me all four readings.
   The units need ~0.8 kg sideways per magnet (1.5 kg dial unit on 6, with
   ~3× margin, `docs/housing_decisions.md` 2026-10-06). Below that, more
   magnets or a floor leg.

**Taking a unit off the door:** pull it straight off, peeling from one edge
if the magnets hold hard. Don't slide it: the dial plugs are in the stars
(§4, shutting down).

### 1.4 Dial unit

**ASSUMPTION: the order below is derived from the CAD.** The repo has no
written assembly order for the dial unit (the pointer to one in
`dial_unit_housing.scad` leads nowhere). Two things fix the order:
- the motor screws go in from the sled's inner face, so the motors must be
  on the sled before it's joined to the front;
- the magnets sit under the sled's outline, so they go in first.

Tell me if a different order works better, and I'll record it.

1. **Magnets.** Six, as in §1.3a: plate door face down, magnet rubber face
   down into each hole, retainer on top, M4 snug. Check with the paper test.
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
11. **Not designed yet:** where the start button goes on the deck. Fix it
    temporarily (double-sided tape) until the CAD has a place (1.7). The
    UART pigtail's splice (2.5) just zip-ties to the deck.

### 1.5 Key turner

From the notes at the end of `cad/key_turner_housing.scad`:

1. **Magnets.** Three, in the base, as in §1.3a (before the motor plate
   goes on).
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
6. **Key motor cable.** Its own ~1 m cable runs to the dial unit and plugs
   into the RAMPS **E0** motor header (revision 2026-10-08.1 — the driver is
   on the RAMPS now, so there is no board to mount here). Leave the three
   magnet retainers reachable; zip-tie the cable clear of the rotating cap.

### 1.6 Putting the units on the door

1. **12 V off**, key motor cable unplugged from E0.
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
5. Plug the key motor cable into the RAMPS E0 motor header. Zip-tie it at the
   key turner and near the RAMPS, clear of the cap.

### 1.7 Mechanical items still open

- Magnet pull test (1.3), and whether the magnets alone hold the units.
- Reprint the dial front assembly and key-turner base with magnet holes.
- CAD: a place on the deck for the button, and a zip-tie point for the
  UART pigtail's splice. (Revision 2026-10-08.1 removed the remote-board
  mount; 2026-10-08.2 removed the hub board, so it needs no mount either.)
- Access to the Mega's connectors at its position on the deck.
- Only if the first full run fails: a key turner that pulls the key out and
  pushes it back in at every attempt (`control/sequence.md`, Open items).

---

## 2. Electrical assembly

The full design, with sources, is `control/wiring.md`. **Print
`control/harness/schematic.pdf`** (the full schematic in colour) and keep
`control/harness/ramps_and_uart.md` (one bench sheet of everything on the
RAMPS, and the UART pigtail) beside you. Other drawings:
`control/harness/overview.svg` (block diagram),
`control/harness/uart_pigtail.svg` (the pigtail) and
`control/harness/harness.png` (the pigtail leads and the key motor cable).

**Revision 2026-10-08.1 (2026-10-08):** all four drivers now sit in RAMPS
sockets — the key in **E0**, beside the three dials. There is no remote
driver board and no inter-unit signal cable; the only wire between the units
is the key motor's own cable, into the E0 motor header.

**Revision 2026-10-08.2 (2026-10-08):** the hub board is replaced by the
**UART pigtail**: six leads, R1 in line in the TX2 lead, one solder splice
(2.5). See `docs/revisions.md`.

### 2.1 Build it in bring-up order

Don't wire everything and then switch on. Each block below is tested by a
bring-up stage before the next one is added:

| Build | Then test with |
|---|---|
| 2.3 Drivers: cut the EN-end pins underneath (all four), heatsinks. Flash the firmware (section 4) | `control/bringup.md` stage 0 |
| 2.4 Mega + RAMPS + the four drivers; 2.5 UART pigtail; 2.6 power; 2.7 jumpers | stage 1 (one driver, then all four) |
| 2.8 one motor on the bench | stages 2 and 3 |
| Dial unit assembled (section 1) with its three motors | stage 4 |
| Key motor cable to E0, key turner (section 1) | stage 5 |
| Everything on the door | stage 6 (short dry run) |

### 2.2 Tools and parts

- Soldering station, solder, flush cutters, heat shrink and heat gun,
  calipers, a marker.
- **Multimeter** (you have one). Use it to check the DC-jack adapter's
  polarity before the first power-up, and the UART pigtail (2.5).
- Masking tape, for the pigtail's lead labels.
- Parts: **`docs/bom.md`, "Electronics assembly — every discrete part"**
  lists each one. What you fit beyond what's already on the boards is small
  (revision 2026-10-08.2):
  - **R1, 1 kΩ**, in line in the UART pigtail's TX2 lead (the only UART
    resistor), and heat shrink;
  - the **DC-jack-to-screw-terminal adapter** (5.5 × 2.1 mm) and **20 AWG**
    red + black wire, PSU → RAMPS "5A" terminal;
  - about **20 F–F jumpers** and the 7 mm **start/stop button**.

  The fuses, diode, capacitors and resistors drawn in grey on the schematic
  are already on the RAMPS. **No longer used** (bought earlier; keep as
  spares): the 1.1 A PTC and the fuse kit + printed holder, the two 100 µF
  capacitors, the 6-conductor cable and the Phoenix connectors, the female
  header strips; and (2026-10-08.2) the hub's perfboard and male header
  pins.

### 2.3 Prepare the drivers (BTT TMC2209 V1.3)

Four drivers are used (three dials + the key), plus one spare.

1. **Two snips per driver, on all four** (`control/wiring.md` §3.3), before
   the heatsinks. Revision 2026-10-08.2: no soldering on the drivers.
   1. At the EN end, two pins go through the board (above and below). Cut
      the **bottom** ends of both off flush underneath. Leave the top ends.
   2. Find **DIAG** on top: the EN-end pin next to the trimmer pot, with
      "DIAG" printed under it. Its DIAG lead (2.7) clips onto its top.
   3. Find **RX** on top: the 4th pin from EN (EN, MS1, MS2, **RX**, TX, CLK,
      …), one of the three tall pins. Its UART lead (2.5) clips onto its top.
      Nothing ever goes on TX or CLK.

   (Leave the spare untouched.) Stage 3 confirms DIAG electrically.
2. **Heatsinks** on all drivers you'll use. At ≤ 1 A RMS no fan is needed
   (BTT: active cooling above 1.2 A).
3. **Don't bridge R10** on any driver (`control/wiring.md` §2).
4. **Turn the VREF pot to minimum on every driver.** The firmware sets the
   current over UART, but a driver whose 12 V drops out for a moment comes
   back using its pot, until the firmware notices at the end of that move
   (`control/wiring.md` §7).

### 2.4 Mega, RAMPS and the four drivers

*One-sheet summary of everything on the RAMPS, and the pigtail:
`control/harness/ramps_and_uart.md`.*

1. **RAMPS jumpers**, under the X, Y, Z and E0 sockets. They set each
   driver's UART address:

   | Socket | Role | MS1 | MS2 | MS3 | Address |
   |---|---|---|---|---|---|
   | X | dial A (top-left) | off | off | **off** | 0 |
   | Y | dial B (top-right) | **on** | off | **off** | 1 |
   | Z | dial C (bottom) | off | **on** | **off** | 2 |
   | **E0** | **key** | **on** | **on** | **off** | **3** |

   **Never fit an MS3 jumper.** On the V1.3 the MS3 position is the UART
   line, and a jumper there would tie it to 5 V.
2. **Check which way the drivers go**, before the RAMPS goes on the Mega.
   The sockets have no pin-1 marking on top. Power off, no drivers,
   multimeter on continuity, for the **X** socket:
   1. Underneath, look for a **square** solder pad on each socket: that's
      pin 1, **EN**.
   2. "5A" terminal **−** to each hole of the socket row nearer the X motor
      header: **two** beep, one at each end. Those are the driver's GND pins.
   3. "5A" terminal **+** to the end hole beside a GND hole: beeps (through
      the RAMPS fuse; a low resistance reading is fine). That's **VS**.
   4. Each X motor-header pin beeps to one of the four middle holes of that
      row.

   So the row nearer the motor header takes the driver's **VS, GND, A2, A1,
   B1, B2, VIO, GND** side, and EN sits directly across from VS. Repeat step
   2 on Y, Z and E0. (From the RAMPS 1.4 KiCad layout; your Fasizi board is
   checked by these readings.) **Send back:** the X results and whether you
   saw the square pads.
3. Press the RAMPS onto the Mega.
4. Plug each driver in: **VS/GND/motor side in the row nearer that socket's
   motor header**, EN across from VS. A reversed driver is destroyed. The
   key driver goes in **E0**. Leave **E1 empty**.
5. **Mount the Mega**: four M3 × 6–8 screws through the Mega's own plastic
   base into the electronics deck (three are enough).

### 2.5 UART pigtail (replaces the hub board, revision 2026-10-08.2)

Six leads, each ending in a female Dupont, joined in one solder splice. R1
sits in line in the TX2 lead. No 12 V, 5 V or GND on it. Drawing:
`control/harness/uart_pigtail.svg`; reference `control/wiring.md` §5.

1. **Measure**, with the drivers seated: AUX-4 to each driver's **RX** pin
   (X, Y, Z, E0). Pick a splice point near the middle of the RAMPS. (A
   female Dupont on top of RX is checked: it grips and conducts, Paul
   2026-10-08.)
2. **Make six leads**: cut one end off each of six F–F jumpers (halves will
   do if long enough). Cut each to its measured length + a few cm.
3. **TX2 lead:** solder **R1 (1 kΩ)** in line, ~3 cm from the female end.
   Heat shrink over it.
4. **Splice:** R1's far lead + RX2 + A + B + C + KEY in one joint. Heat
   shrink over it, then a larger piece over the bundle.
5. **Label** each female end with tape: TX2, RX2, A, B, C, KEY.
6. **Check (multimeter on Ω), pigtail loose:**
   - TX2 → RX2: about **1 kΩ**
   - TX2 → A, B, C, KEY: about **1 kΩ** each
   - RX2 → A, B, C, KEY: about **0 Ω** each

   Then tug each lead at the splice.
7. Fit the leads in 2.7; zip-tie the splice to the deck.

**Send back:** whether the test-fit in step 1 worked, and the readings from
step 6.

### 2.6 Power wiring

PSU (Ledmo HTY-1200500, 12 V 5 A, 5.5 × 2.1 mm barrel, centre +) → DC-jack
adapter → **RAMPS "5A" terminal**, 20 AWG red for + and black for −. That's
all: the RAMPS's own 5 A fuse feeds all four drivers. Nothing else takes
12 V. Leave the **11A** terminal (heated bed) empty.

**Leave the Mega's own barrel jack empty.** It feeds only the Mega (VIN);
the drivers get 12 V only through the "5A" terminal, and diode D1 passes
power from there to VIN, never back. A PSU in the Mega's jack would run the
Mega but leave every driver missing on `ping`.

**Check the adapter's + / − with the multimeter** before the first power-up.

### 2.7 Signal jumpers on the RAMPS

DIAG leads and the button: F–F jumpers about 10 cm long. Pigtail leads: as
built in 2.5. The endstop headers are **S** (signal), **−** (GND) and **+**
(5 V).

| From | To |
|---|---|
| Top of dial A driver's **DIAG** pin (X socket) | **X_MIN S** (D3) |
| Top of dial B driver's **DIAG** pin (Y) | **X_MAX S** (D2) |
| Top of dial C driver's **DIAG** pin (Z) | **Z_MIN S** (D18) |
| Top of the **key** driver's **DIAG** pin (E0) | **Z_MAX S** (D19) |
| Pigtail leads **A, B, C, KEY** | top of the **RX** pin of the drivers in X, Y, Z, **E0** |
| Pigtail leads **TX2 / RX2** | AUX-4 pin 18 / 17 (D16 / D17) |
| Start/stop button (7 mm) | **Y_MIN S** and **Y_MIN −** (D14) |

DIAG leads are plain F–F jumpers (revision 2026-10-08.2; no cut-in-half
leads). Before unplugging a driver, pull its DIAG and RX leads off. The
button's mount isn't designed yet; a loose button on its leads is fine for
the bench.

### 2.8 Motors

- **Dials**: dial A's motor on the **X** motor header, B on **Y**, C on
  **Z**.
- **Key**: the key motor's own ~1 m cable plugs into the **E0** motor header
  (revision 2026-10-08.1 — no remote board). It's the only wire between the
  two units. Use the supplied cable as it is; shorten it only if the key's
  StallGuard reads too dull in stage 5. Zip-tie it at the key turner and near
  the RAMPS so a tug lands on the ties, and keep the spare length clear of
  the key cap.
- If a motor **buzzes or jitters instead of turning**: 12 V off, then swap
  the two middle wires in its connector. Some 17HE19-2004S have them swapped.
- **Never plug or unplug a motor with 12 V on**, the key motor included.
- Currents are set over UART (pots at minimum): dials 1.0 A RMS; the key
  starts at 0.6 A and stage 5 sets its final value.

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

Expect `53 tests, 36489 checks, 0 failures` and `3 passed`. I check these
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
   `# Fichet safe robot 0.4 (2026-10-08, rev 2026-10-08.1) - type help`. If it
   says 0.3 or older, the old code is still on the Mega.
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
5. Plug the key motor cable into E0 (12 V still off).
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
- **On screen:** progress lines (`EV`, `ERR`, `GSTAT`, `HOME`, `LEARN`,
  `CAL`, `RECHECK`, `SUCCESS`, …), every attempt that isn't a clean fail, and
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
| DRVFAULT | a driver reset or reported a fault. The `GSTAT` line just before says which driver and what (below) | fix the cause, then `resume`. In a run it has already rewound to the last good check |
| ABORT | you typed `!` | `resume` when ready |

**`GSTAT,<time>,<driver>,<value>,<when>`** comes just before a `DRVFAULT`.
`<driver>` is A, B, C or K (key). The robot checks every driver before and
after each of its moves and before each attempt, because a driver whose power
dips comes back with no current setting and no stall detection. Without the
check, the key could then turn without stopping, and that looks like a
success. `<value>`:
- `1`: the driver **reset**: its 12 V (or its 5 V) dropped out for a moment.
  Type `ping`: the second-to-last field of each `DRV` line is that driver's
  GSTAT, so it shows which ones reset.
  - Only one driver: that driver's seating in its socket (push it down
    with 12 V off).
  - All four: the 12 V supply, its plug, or the RAMPS "5A" terminal screws.
  - Check those contacts with 12 V off (multimeter on continuity, while
    you wiggle them), fix, then `resume`.
- `2`: the driver shut itself down: **overheated or a short**. 12 V off, let
  it cool, check the motor's wires, and send me the log before resuming.
- `4`: its **12 V is too low** right now: the supply or its wiring.
- `80`: **no answer**: no 12 V at that driver, or its UART pigtail lead is
  off its RX pin. All four at once: the RAMPS 5 A fuse or the supply, or the
  pigtail's TX2 / RX2 leads, R1 or the splice (redo the 2.5 multimeter
  check).
- Flags add up: `5` = 1 + 4.
- On the bench, if you switched the 12 V off and on yourself since the last
  command (without `release`), a `1` is expected: run the command again.

`<when>` is `before` or `after` (a move of that driver), `attempt` (the check
before each attempt) or `config` (before its settings are written again).

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
2. Unplug the key motor cable from E0.
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
