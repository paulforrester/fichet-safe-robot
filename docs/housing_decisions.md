# Housing — design decision log

Working notes on the two 3D-printed housings (`cad/dial_unit_housing.scad`,
`cad/key_turner_housing.scad`), most recent first. Companion to
`docs/decisions.md` (tube-socket test key geometry) and
`control/sequence.md` (control architecture) — this file covers the
mechanical housings that carry that geometry onto the actual door.

## 2026-10-07: door magnets fall out of the inner side — holes to become a snug fit

**Finding (Paul):** the Wukong magnets measure **21.5 mm**, not the listed
22 mm, so they're loose in the 22.4 mm holes. On the door that doesn't
matter: the pull holds each magnet's retainer on its seat ring. Off the
door, with the unit on its side, a magnet and its retainer slide out of
the inner side of the hole.

**Design flaw (mine, 2026-10-06 entry):** the retainer is screwed only to
the magnet, never to the plate. It stops the magnet moving *toward* the
door; nothing stops it moving the other way.

**Fix:** keep the retainer for the door's pull, and make the hole grip the
rubber so the magnet can't slide inward. How tight a printed hole comes out
depends on the printer, so `cad/magnet_fit_test.stl` has five holes, 21.4 to
21.8 mm, at the real depth (5 mm plate + 0.8 mm ring). Paul picks the
smallest one a magnet presses into by thumb and that holds it upside down;
that diameter becomes `rmag_hole_d` for both plates (dial front assembly,
key-turner base), then re-render, re-run the checks, reprint. Height and
thread depth still to be measured (they set the proud face and the screw
length).

## 2026-10-07: printed holder for the interim 5 × 20 mm fuse (hub F1)

Paul's spec (2026-10-07): one 5 × 20 mm glass fuse, 1.6 A T, in series in a
12 V line under 0.6 A, 20 AWG wire each end; metal-to-metal contact on each
end cap with a force that doesn't depend on the plastic holding its shape
(PETG creeps); no screw point on the glass, no solder on the caps; swap
without tools or with a screwdriver; live parts covered; labelled
"1.6 A T"; perfboard or inline mount; PETG or PLA. Why it's needed:
`control/wiring.md`, log 2026-10-07.

**Design** (`cad/fuse_holder.scad`, print `cad/print_fuse_holder.scad` →
`cad/fuse_holder.stl`):
- **End A, fixed:** an M3 heat-set insert through a 4mm wall, its front face
  flush with the fuse cradle; the fuse cap bears on the brass. Its rear end
  stands 1mm proud into the clamp pocket, so the wire clamp is
  head → washer → wire → brass, with no plastic in the clamp.
- **End B, sprung:** a second insert, *not* heat-set, slides loose as a brass
  piston; its front face bears on the B cap and the B wire is clamped to its
  rear face the same way. One QUARKZMAN 0.5 × 7 × 20 spring (a spare from
  the dial-unit pack) pushes on that washer: 16.5mm long with the fuse out,
  **13mm working (7mm compressed, ≈1.8–2.8 N at the BOM's estimated
  0.25–0.4 N/mm)**, 11mm when the fuse is pushed back to lift it out. The
  spring carries no current (the wire is clamped to the piston), and
  7mm of spring travel makes plastic creep irrelevant to the force.
- **Swap:** slide the lid out by its end flap, push the fuse 2mm toward the
  spring, lift it out; reverse to fit. No tools.
- **Covered:** the lid slides in grooves and stops on end wall B; its flap
  covers the hex-key hole at end A (the A screw head behind it is live).
  Wires leave through notches at each end. Label "1.6 A T" engraved in the
  lid.
- **Prints with no supports or bridges:** every channel is open to the top
  and closed by the lid. Body base-down, lid label-down.
- **Size:** 54.5 × 18.8 × 12.2mm (28.7 wide over the tabs). That's longer
  than the ~50 × 30mm hub board, so mount it **beside** the hub board (four
  tabs, M3 or 3mm zip ties) or inline in the wire, not on the board.

**Checked:** `cad/tools/fuse_holder_check.py` — body, lid, fuse, both
contacts, both screw stacks and the spring, pairwise with manifold3d with the
fuse in, pushed back 2mm, and out: no overlaps; fuse touching both contact
faces when in; body and lid watertight. Asserts in the SCAD: the M3x6 can't
poke out of the insert's front face (it stops 0.5mm short), engages ≥ 3.5mm,
and the spring stays clear of solid when loading.

**Not verified — measure before printing:** insert OD and length (BOM: "4.2mm
OD, ~5mm"; if shorter than 5mm, the M3x6 would reach the fuse — change
`ins_l`); M3 washer size (7 × 0.5 assumed); the spring's coil count (solid
length must stay under 11mm). The heat-set hole is 4.0mm; open it up if the
insert won't go in cleanly.

**Assembly:**
1. Heat-set one insert into wall A from the clamp pocket side, until its
   front face is flush with the cradle face.
2. Strip ~10mm of the A wire, lay it in the end-A notch, wrap it clockwise
   round an M3x6 under an M3 washer, thread it into the insert's rear end
   with your fingers, then tighten with a 2.5mm hex key through the end hole.
3. Piston: wrap the B wire the same way under a washer on the second insert's
   rear end (M3x6); tighten in your fingers/with pliers on the insert.
4. Drop the spring into the spring channel, the piston in front of it, and
   lay the B wire in its side slot and groove to the end-B notch.
5. Push the piston back, lower the fuse into the cradle, let it go. Slide the
   lid in from end A until it stops.
6. Before powering: continuity end to end through the fuse with the
   multimeter, and tug each wire.

## 2026-10-06 (evening): assembly order written up in `docs/manual.md` §1.4–1.6

The print notes at the end of `cad/dial_unit_housing.scad` point to "the
bottom of the v2 entry" for the dial unit's assembly order, but that entry
has none. The manual now gives one, **derived from the CAD, not yet tried**:
magnets → bearings → gear-shafts → motors on the sled (their screws go in
from the sled's inner face, so before the sled meets the front) → pinions →
springs → sled onto the front legs → deck → Mega base plate (deck first: two
of its M6 screws sit under the base plate, 2026-10-04 entry). The magnets go
first because they sit under the sled's outline. The key turner's order is
the one in `cad/key_turner_housing.scad` (motor → hub → plate onto legs),
with the magnets first. Paul to correct either from the real build.

Also noted there:
- the cap's tongue sits in a through-groove, so it may slide out while the
  unit is being placed; if it does, the cap goes on the bow first.

Paul's answers, same evening:
- **Key-turner plate screws: M6 × 16, not M6 × 20.** He has both and found
  the 16 mm work better. That gives 10 mm of thread in the 16 mm pilot,
  the same as the dial unit. The print note in `cad/key_turner_housing.scad`
  is corrected (a comment only; no geometry change), and `docs/bom.md`
  lists them.
- **Slicer:** Bambu Studio's default settings for the H2D, for every part so
  far.
- **Springs:** ordered, arriving 2026-10-07.

## 2026-10-06: key fit test passed; key torque 0.07–0.08 N·m — direct drive is fine

**Fit test (Paul, `key_fit_test.stl`, cap in PETG-CF):** the cap slides onto
the bow without forcing, sits with the key tip just short of the slot bottom,
and turns the key to its stop. Cap geometry confirmed as designed.

**Torque:** luggage scale in the lever hole (50mm from the axis) read
**0.14–0.16 kg** to turn the key: × 9.81 × 0.050 = **0.069–0.078 N·m**.
(Correction: first reported as 1.4 kg, a misread decimal — Paul caught it
the same day. The 1.4 kg version had concluded the motor was too weak and
needed a 4:1 reduction; that conclusion is withdrawn.)

**Motor:** the 17HE19-2004S is rated 0.59 N·m holding at 2.0 A; running
torque is lower and falls with speed, and at the ~1 A the drivers are
planned to run at, expect roughly 0.3 N·m. That is about 4× the key's
torque, so **v1's direct drive stays** — no gearing.

**Housing / magnets:** whatever turns the key pushes back on the housing.
While turning: 0.078 N·m ÷ 0.031m (magnet circle radius) = 2.5 N (~0.26 kgf)
across 3 magnets, ~0.09 kg each — small. The bigger load is at the key's
end stop, where the motor pushes with everything it has until it is
stopped: at full 2 A that could approach 0.59 N·m (~0.65 kg per magnet).
So run the key motor at reduced current — enough for ~2× the key's torque
— and stop on StallGuard at the end stop; that keeps the stop load to a
fraction of what the magnets need to hold anyway. Still confirm with the
one-magnet pull test.

## 2026-10-06: both units mount with 22mm rubber-coated pot magnets (Wukong)

**Why.** Two problems with the 2mm×8mm press-fit disc field: (1) Paul found
strings on the floors of the printed pockets — a floor printed as the first
layer over a pocket can't be cleaned out reliably, so the discs wouldn't seat
flat; (2) on a vertical door what holds the unit up is sideways (shear) grip,
not straight pull. Published supplier figures put a bare neodymium magnet's
shear grip at roughly 15% of its pull, and a rubber-coated pot magnet's at
roughly 31–38% (e.g. a 22mm rubber magnet listed 5.9 kg pull / 1.8 kg
shear). Rubber also won't scratch the door. Paul ordered Wukong 22mm
rubber-coated magnets with an M4 threaded back, listed 6mm tall
(Amazon.fr B0DGQ52DY9 20-pack / B0D5B4TJ7B 10-pack). The listing gives no
pull rating, so the real number comes from a test on the door.

**Mount (shared, `rmag_*` in `common_mounts.scad`).** A 22.4mm **through**
hole — nothing is printed over air, so there's no floor to string. On the
plate's inner face a seat ring (OD 29) stands up to z = 5.8 from the door
face; a printed retainer disc (Ø27 × 3, `print_magnet_retainer.scad`) sits on
the ring and an M4 screw goes through it into the magnet's back. The ring top
sets the depth, so every magnet's rubber stands exactly 0.2mm proud of the
door face, and the door's pull goes magnet → screw → retainer → ring, not into
a press fit. Change `rmag_d` / `rmag_h` if the real magnets differ from the
listing; everything else follows.

**Dial unit.** 6 magnets at r = 53.5mm, first at 26.75°, 60° apart — radius
and rotation brute-force searched for clearance to the three front legs and
the bearing bosses (the first try, r57 / 25°, hit a leg by 0.24mm). The 8×2
disc-pocket field is gone. The plate now rests on the rubber, 0.2mm off the door,
so the dial plugs sit 0.2mm shallower in the stars (3.7 instead of 3.9mm):
not worth anything else changing. `dial_layout_check.py`: seat ring to front
legs 2.39mm, to bearing bosses 2.43mm, 7.0mm inside the plate rim, 24.5mm ring
to ring — ALL PASS. `dial_interference_check.py` (magnets + retainers added as
a part): NO INTERFERENCE.

**Key turner.** 3 magnets at r = 31mm, at 60/180/300° (between the legs); the
legs were re-clocked from 180/60/−60° to 0/120/240° to make room. That puts
one leg toward the dials, but legs sit inside the round base (r36 < r43), so
the footprint on the dial side is unchanged; the base only bulges past r43
where the magnet rings are (to r46.5), and the magnet at 180° is the one
facing away from the dials. Base plate 6 → 5mm to match the dial plate (the
ring adds the other 0.8mm). Asserts: ring to leg ≥ 1.5mm (actual 13.3), ring
to key opening ≥ 1.5mm (actual 2.5). `key_turner_check.py` with magnets added:
NO INTERFERENCE at all 15 poses.

**Load.** Dial unit ~1.3–1.5 kg on 6 magnets, key turner (lighter, one
motor) on 3. Not verified: no pull/shear figure exists for these magnets.
**Test before trusting it:** stick one magnet to the door and pull sideways
(parallel to the door) with the luggage scale. 1.5 kg on six magnets is
0.25 kg each; wanting about 3× margin for the motors' reaction torque and
vibration, if one magnet slips under ~0.8 kg sideways, add magnets or a floor
leg before running the robot. The key turner's three also have to resist the
key's turning torque — still to be measured with `print_key_fit_test.scad`.

**Prints affected:** dial front assembly (reprint), key-turner base, 10
retainers. SketchUp models rebuilt with the magnets (scene "Door side: rubber
magnets" in each).

## Key-turner v1 (2026-10-06): cap over the bow, Oldham-style, motor on the key axis

Replaces v0.1's thumbscrew clamp (sized before the key was measured).
`cad/key_turner_housing.scad`, inputs in the entry below.

- **Grip.** A cap (PETG-CF) slides over the key's flat head: slot 3.3mm
  (bow 2.5-2.9 + 0.4) x 30mm (bow 24.6 + 2.7 each side), mouth at 18.5mm from
  the door (beyond the steep taper, so it only ever touches the flat part),
  lead-in chamfer, slot bottom 0.6mm past the key tip. Its top has a tongue
  at 90deg to the slot that sits in a groove in the motor hub. So the cap is
  the middle disc of an Oldham coupling and the bow is one of its jaws: the
  unit can sit up to 2.7mm off the key axis in any direction and still turn
  the key with no side load on the lock — it is placed by hand and the key
  wobbles in the lock, so exact alignment can't be counted on. Axially the cap
  is trapped between the key tip and the hub (0.6 / 0.5mm).
- **Drive.** NEMA17 straight on the key axis (single motor, no gearing yet:
  the key's torque is unknown; 2:1 can be added later as in the dial unit).
  Hub on the D-shaft, 13.5mm of bore all on the shaft's flat; optional grub.
  Backlash ~3-4deg total (two sliding joints), fine for finding a stop at ~100deg.
- **Frame.** Base plate r43 with a 28mm opening that passes the bow as the unit
  slides on; 3 legs at r36 (180/60/-60deg, none toward the dials); motor plate
  on M6x20 countersunk self-tappers (the dial unit's bench-proven 5.4 pilot;
  **Correction 2026-10-06 evening:** M6x16, Paul's choice, see the top entry);
  motor on 4x M3x10 countersunk in the same 6.3mm countersinks as the dial sled.
- **Fit next to the dial unit.** The keyhole is 125.2mm from the dial plate's
  centre, level with it, so ~50mm from the dial plate's edge: the key turner
  reaches 43mm (base) / 29mm (motor plate) toward the dials. Toward the door's
  left edge (36.5mm away) the motor plate reaches 47mm, which is fine because
  the door sits flush with the safe body (Paul).
- **Door attachment: not decided** — to be chosen together with the dial
  unit's (Paul wants the same magnets in both). The base plate's door face is
  plain for now.
- **Checks.** STLs watertight, one body each. `cad/tools/key_turner_check.py`:
  key dummy (built from the caliper readings) + cap + hub + motor + frame at
  key angles 0/50/100deg and key offsets up to 2.5mm in five directions: no
  overlap (0.000mm^3). Sanity: a 2.0mm slot gives 166mm^3 of overlap, and a 4mm
  offset (past the 2.7mm range) 1.8mm^3, so the check sees real clashes.
- SketchUp review model: `cad/sketchup/key_turner_sketchup_build.py` ->
  `fichet_key_turner_v1_2026-10-06.skp` (4 scenes). Every part closed with outward
  faces; volumes within 1% of the STLs.
- **Not verified:** the key dummy's outline between the measured points
  (swelling width, the bow's exact outline) is approximate — hence the fit
  test print (`print_key_fit_test.scad`: cap + a hand lever with a hole 50mm
  from the axis for a luggage scale, which also measures the key's torque).

## 2026-10-06: key-turner inputs (Paul's measurements)

- Lock hole 12.05mm dia. Centre to centre (caliper far/near average): top-left
  dial hole 110.13mm (far 122.25 / near 98.01), bottom dial hole 126.95mm
  (far 139.4 / near 114.5). Check: far - near should equal the two hole
  diameters (25.0): bottom 24.9, top-left 24.24, so the top-left pair carries
  ~0.4mm of uncertainty. Solving both: the keyhole is at (-125.2, -1.8) in the
  dial unit's frame — 125.2mm from the dial plate's centre, level with it, so
  ~50mm from the 150mm dial plate's edge (the earlier ~55mm "gap" note was a
  photo estimate of something else).
- Key: 84.75mm long; fully inserted it protrudes 31.89mm from the door; turns
  clockwise ~100deg then stops; bow vertical at insertion. Calipers (with
  photos): bow 24.60 wide, 2.90 thick near the top; swelling 9.48 thick at
  ~8mm from the door; collar 7.97 dia to ~5.6mm; shaft 4.72; bow at full width
  from ~12.6mm; steep taper from the swelling over ~10mm, then 2.75 -> 2.5 over
  the last ~13.8mm; ring hole 10.75 with 6.6mm of metal to the bow's end. Door
  flat for 50mm around the lock, flush with the body; keyhole edge 30.45mm from
  the door's left edge.

## 2026-10-06: motor screws countersunk instead of counterbored

Paul printed the motor sled: the 2mm-deep flat counterbores for the motor
screws came out full of stray strings that were hard to dig out. Cause:
the sled prints inner face down, so each counterbore's flat shoulder is
printed in mid-air (an unsupported bridge ring around the 3.4mm hole). He
has M3 countersunk screws, so the 12 counterbores are now **90deg
countersinks**: a cone prints as a 45deg overhang, each 0.2mm layer
stepping in 0.2mm, with no bridge.

- Cone: **6.3mm mouth** on the inner face down to the 3.4mm clearance hole
  (1.45mm deep). Paul's screws are a generic kit (M3x10 ×55) that doesn't
  say which head standard, so the cone works for both: ISO 10642 M3 heads are
  dk 6.72 theoretical, k 1.86 ([Engineers Edge](https://engineersedge.com/hardware/bs_en_iso_10642_14583.htm));
  DIN 7991 M3 heads dk 6.0 max, k 1.7 max ([globalfastener DIN 7991](https://www.globalfastener.com/standards/detail.php?sid=NTUx)).
- Screw: **M3x10 countersunk** (length includes the head). Thread in the motor's
  4.5mm-min holes: ISO head (0.21mm proud) **3.79mm**, DIN head with its 0.2mm
  land **3.95mm**, DIN head without a land **4.15mm**. All three asserted in the
  SCAD (3.5 to 4.2). The first pass used a 7.0mm mouth: fine for ISO heads
  (4.14mm) but a DIN head could have gone 4.5mm deep and bottomed — caught
  before printing; the assert now fails on the 7.0 value. M3x8 would grip only
  ~2mm; M3x12 would bottom out.
- Side benefit: the old cap heads stood 1mm proud into the gear cavity;
  countersunk heads are within 0.21mm of the face (nothing moves within 4.5mm of it).
- Re-checked: layout check all pass (countersink to spring pocket 2.49mm
  over the 2mm requirement, was 2.60 with the 6.5mm counterbore);
  interference check no overlap (largest 0.083mm^3, the dummy screw heads
  touching their own seats — faceting); sled STL watertight, one body,
  90.76cm^3; slices through a screw hole show the cone 6.2 -> 4.9 -> 3.5mm at
  z = 0.05 / 0.7 / 1.4mm as designed; the SketchUp build script's sled
  updated the same way (closed, volume within 0.1% of the STL), and the
  SketchUp model rebuilt from it (`fichet_dial_unit_v2_geared_2026-10-06b.skp`)
  with a new scene 6 showing the sled's door-side face and its countersinks.
- Only the sled changes; the front plate, deck and drivetrain are untouched.

## v2 (2026-10-05): geared drivetrain on 608 bearings — the Oldham coupler could not have worked, and the hole pattern was wrong

**What prompted it.** Paul, with every printed part in hand: "the motor
spindles do not line up with the center of the holes for the dial turners
... see if there is an orientation for the motors where they can all be
mounted to the same sled and align with the holes. If not ... a flexible
coupler, but another option would be to add another level to the robot
and work on gearing ... I do have a stock of 608 bearings ... I want to
nail this on the first try."

### Findings

1. **No orientation exists.** Two NEMA17 cans (42.3mm square) can't have
   shafts closer than 42.3mm in any orientation (the narrowest a square
   gets is its side length). The two top door holes are 33.0mm apart. So
   at least one motor always has to sit off its dial; a coaxial direct
   drive would need the motors stacked at two or three depths (+50-100mm
   of overhang off the door, on magnets) — rejected.
2. **The v1 Oldham coupler could not have worked.** The disc's tongues
   were `slot_length - 1` long inside **closed** slots, so the disc could
   slide only +/-0.5mm, against the +/-6.9mm the 6.93mm offset needs — it
   would have jammed on the first turn. (`oldham_slot_length()` used the
   tongue *width* + 2x offset, which is the rule for a short square key,
   not a full-length tongue.) Separately, the real 24mm motor shaft
   reaches 18mm past the sled into a 20.8mm cavity: through the motor
   hub's 3.5mm bore, through the disc and into the dial hub. The modules
   are removed from `common_mounts.scad` (git history keeps them).
3. **`dshaft_bore()` cut an open slot, not a D.** Its "flat" was a cube
   added to the *cut* from 1.85mm off the axis out past the hub wall, so a
   12mm hub came out as an open "C" (checked with a cross-section render:
   one contour, no closed bore). Only the set screw's friction could have
   driven it. Rewritten as a real D (round bore intersected with the flat
   line at 2.15mm), D only over the flat's length. This also fixes
   `key_turner_housing.scad`'s gripper hub (STL re-rendered).
4. **The hole pattern was wrong.** The 36mm equilateral triangle was a by-
   eye photo read that was never confirmed. Re-measured from the door
   photos with software tick detection it came out isosceles, then Paul
   measured with calipers (far/near jaw readings, centre = average, which
   cancels the jaws sitting off the line of centres):

   | pair | far | near | centre |
   |---|---|---|---|
   | A-B (top, left-right) | 45.90 | 20.12 | **33.01** |
   | A-C, B-C (down to the bottom hole) | 55.0 | 30.0 | **42.50** |

   Holes 12.97 / 13.0mm dia. Depths from the door face: the star starts
   at 3.14mm; the caliper depth gauge (~2mm wide) stops at 8.92mm because
   the star's slots narrow toward a point; a real key goes in to 15.5mm.
   (A first write-up had 8.92 as the star's width at the mouth and 13.3 as
   the hole depth — a terminology mix-up, corrected with Paul the same
   day; what the 13.3 reading was is still to be confirmed.) The real
   key's blade read 0.91mm wide this time, but the printed turner at
   1.04mm is still loose in the socket, so the plug stays at 1.04 (Paul).
   The short side runs across the top; the other two meet pointing down to
   the bottom of the safe (Paul). v1's plate was up to ~5mm off. The two
   photo methods had disagreed by ~1mm (33.3/43.3 from the old angled
   photos, ~32.6/42.5 from the new square-on ones once corrected for the
   scales sitting a few mm above the door), which is why calipers were
   needed.

### Options considered

- **Fix the Oldham** (open slots or short tongues, longer motor hub):
  keeps the floating dial coupler, but a ~7mm-offset disc orbiting every
  turn in PETG-CF, ~2-3deg of backlash from two sliding joints, no torque
  gain, and three floppy couplers to line up with three sockets by hand.
- **Stagger the motors axially** for coaxial drive: long overhang (see 1).
- **Belts**: three belt planes plus tensioners — more parts than gears.
- **Gear stage on 608 bearings (Paul's suggestion) — chosen.** Each motor
  can sit anywhere on a circle around its dial, the dial shafts get real
  bearings, the reduction adds torque headroom (the dial torque is still
  unmeasured), and printed m1 gears have ~1deg of backlash.

### The design (`cad/dial_unit_housing.scad` v2)

- **Gear-shaft** (x3, PETG-CF, one piece): 8-tooth spline plug (same
  geometry as the test key) + 7.85mm journal + 1.5mm spacer + **28T module-1
  spur gear**, 6mm face. Runs in **two stacked 608 bearings** in a 16mm boss
  on the front plate; a 2mm lip on the door side holds the outer ring (lip
  hole 19.5mm, between the shield edge D2 19.2 and the abutment limit Da
  20); the spacer (11mm) bears only on the inner ring (SKF 608-2Z abutment
  da 10-12mm).
- **Spring-loaded plug.** The journal is a sliding fit, so the whole
  gear-shaft slides 7mm. A light compression spring between the gear's
  rear face and the sled pushes it forward against the rear bearing.
  Mounting: put the unit on the door; any plug that doesn't line up with
  its star is pushed back and the plate still seats flush; then turn each
  motor slowly and its plug snaps in. Plug tip at the forward stop is 7mm
  below the plate face = 3.9mm into the star (the star starts 3.14 below
  the door face) — the same depth the hand test key reached. The plug is
  5mm long, the length of the real key's straight-sided section; deeper,
  the socket's slots narrow (shape unmeasured), so it is not lengthened.
- **Pinion** (x3, PETG-CF): **14T module-1**, 14mm face (6mm gear + 7mm
  travel + 1) so the gear never leaves it. **2:1 reduction**: 400 full
  steps per dial turn, 20 per dial position. Profile shift +0.2 pinion /
  -0.2 gear (a 14T pinion undercuts below ~17T; the shifts cancel, so the
  centre distance stays 21mm). Its D-bore is round for the first 2.5mm and
  D only where the shaft's flat is, so the end of the flat locates it
  axially; it is also trapped between the sled and the boss tops, so the
  set screw is optional (grub screw only — a cap screw's head would hit
  the gear).
- **Motors** on a 21mm circle around their dials, directions and rotations
  from an annealing search over every clearance (below). The cans overlap
  the dials only in plan view — they sit behind the sled, the gears in
  front of it.
- **Front-to-sled joint**: 3 legs + M6 countersunk self-tap (bench-proven
  in v1), keyed (asymmetric). **Deck**: 3 legs between the cans, Mega base
  plate re-placed (244deg, offset (-2.5,-5)) so its screws clear the deck
  countersinks by >21mm.
- Stack: door 0 | plate 0-5 | bosses to 16 | gear 17.5-23.5 (24.5-30.5
  pushed back) | pinion 17-31 + hub to 35 | sled 35.5-41.5 | cans to 89.5 |
  deck 95.5-100.5. Motor shaft tip lands 0.5mm inside the pinion. Motor
  screws: M3x10 countersunk, flush in 90deg countersinks, 4.1mm of thread in
  the motor's 4.5mm holes (was M3x8 in 2mm counterbores — see 2026-10-06
  entry above).
- **Pointer** now points up on the door for real (the top pair side).
- Magnet field: 147 pockets, kept clear of the bearing pockets.

### Verification (all re-run with the caliper numbers)

- `cad/tools/dial_layout_check.py` (reads every position from the SCAD's
  own echo output): all 2D clearances pass with >= 1.4mm left over the
  stated requirements (can-to-can >= 6mm, pinion vs the other dials' gears
  >= 3mm, top gear tips 3.4mm apart, countersink + 3mm driver access clear
  of every can, legs clear of gears/pinions/screw heads, everything inside
  the 150mm plate); gear mesh from the SCAD's own tooth outlines: zero
  overlap through a full tooth pitch at zero backlash (conjugate), 0.12mm
  flank gap as printed, still no overlap with the centre distance 0.15mm
  short; contact ratio 1.52; axial stack and pinion float rows all pass.
  What-if: the layout passes with any one hole distance +/-1mm.
- `cad/tools/dial_interference_check.py`: every part rendered in place
  (plus dummy cans, bearings and M3 heads), 36 static pairs + 114 moving
  pairs at 12 poses (gear phase x 4, spring travel 0/3.5/7mm): **no
  overlap** (largest 0.000mm^3). Sanity check: deliberately mis-phasing a
  gear half a tooth gives 20mm^3, so the check does detect real overlaps.
- trimesh: every STL watertight, one body per part.
- SketchUp review model (`fichet_dial_unit_v2_geared.skp`) built from the
  same numbers; per-part volumes match the SCAD STLs within 1%.

### Not verified yet — what the first prints have to confirm

- **2026-10-05: door-pattern test PASSED** (Paul): the plate fits the door perfectly and all three dial turners turn easily. The caliper hole pattern is confirmed on the real door.

- **Door-pattern test first** (`print_dial_pattern_test.scad`): bearing
  press fit (22.15mm pocket), the journal sliding in the bearings (7.85mm),
  and all three plugs seating together on the real door. Three rigid shafts
  into three sockets is over-constrained, and each plug can only float a
  few tenths of a mm sideways (0.35mm diametral clearance at the plug
  tips, 0.15mm journal-to-bearing), so this is the check. (An earlier
  version of this note counted on a wide star mouth for extra room — that
  came from the mislabelled 8.92 reading and was wrong.)
- Springs: none on the BOM yet (<= 8mm OD, ~18-20mm free, solid < 10mm).
- Gear teeth and plug teeth are printed plastic: run the dial motors at
  ~1A (TMC2209) until the dial torque is measured — 2:1 doubles what the
  motor can put into the plug.
- Paul measured the key's blade width at 0.91mm this time (earlier
  1.04-1.06); the plug keeps the bench-tuned 1.04, which clicked the dials.
- Motor cable exits: rotate each can in 90deg steps at assembly so its
  cable side faces a free gap.

## Electronics sled switched to the Mega base-plate mount (2026-10-04): bench results on the coupon and the motor sled

Bench results from Paul, same day as the fourth round below:
- **Motor sled fit is good** (the latest motor sled, with the
  `motor_pad_r` outline and the keyed countersunk joint pattern).
- **Mega base plate vs `cad/mega_base_fit_test.scad`**: the real base
  plate "fits on the screws as placed", but only 3 of the 4 screws would
  go in. Paul's call: 3 is enough to hold it. Which hole binds wasn't
  reported, so the 4 positions are unchanged (a ~0.4mm error against a
  3.1mm hole was the known risk, see the entry below); it just means one
  hole is a spare.

Change: `electronics_deck()` now mounts the Mega only through its base
plate. The 4 standoff posts and the `mega_base_mount` switch are removed;
the 4 M3 self-tap pilot holes (2.6mm, through the deck) at
`mega_base_hole_pts` are always present. `mega_hole_pts` (the board's own
PCB holes) stays only to size the deck outline, and `mega_rotation = 30`
stays because the coupon was fit-checked at that orientation. The deck
outline is unchanged from the previous round's base-plate mode (still
reaching the two end-flange holes). Re-rendered clean; trimesh: 12
watertight bodies; deck now has exactly 4 x 2.6mm pilot holes plus the 3
M6 countersunk holes and no posts. Build order note updated: bolt the deck
to the legs before screwing the base plate on (2 of the 3 M6 screws sit
under the base plate; their heads are flush, so it lies flat over them).

Still open: the pointer direction on the real door, the 2mm magnet wall
(`magnet_wall`), and the first front-leg M6 self-tap (thread it in by
hand). Paul's next step is a full dialer-assembly fit with the new base
plate and sled.

## Fourth round (2026-10-04): countersunk keyed joint, pointer tab, magnet field, and a Mega base-plate mount

Paul's feedback after the previous round was merged (PR #6):

1. Use countersunk screws for the base-plate-to-motor-sled mount "to
   ensure accurate alignment every time", make the sled fit so "the
   same motor is always aligned with the same dialer", and add a key or
   arrow on the base plate so the dialer assembly can always be oriented
   the same way on the safe door.
2. Check for a drawing of the plastic base that ships with the Arduino
   Mega 2560, and try an electronics sled with no standoffs: the base
   plate screwed to the sled with M3 self-tap screws.
3. Fill the base plate's door-facing face with as many magnet pockets as
   feasible, to experiment with screw/magnet mixes.

**1a. Joint hardware: M6 countersunk self-tap, same as the deck.** The
front-to-rear joint was M3 screws into heat-set inserts. It's now 3 M6
countersunk screws through `motor_plate()` (90-degree countersink on the
outer face, `m6_csk_*`) into the same 5.4mm M6 self-tap pilot the deck
legs use (`front_standoff_legs()`). Same reasoning as the deck joint
(logged in the 2026-10-03 entries): the cone seat self-centers each
screw, so the sled lands in the same place every time. The 12mm legs
leave ~3.3mm of wall around the pilot, the case flagged as untested on
2026-10-03. Paul's report that the electronics sled "fits on top using
the m6 cs-screws" is the first real evidence that the deck legs (same
dimensions) are fine, which is why it's safe to reuse here. Still:
thread the first front screw in by hand. Screw length ~15-16mm (6mm plate
+ ~10mm engagement; the 12mm pilot bottoms a screw longer than ~18mm).
The M3 inserts and M3x8 screws are no longer used here (BOM updated).

**1b. Keying: the joint pattern is deliberately not symmetric.** With
the old 61mm/54-degree ring (120-degree symmetric), the motor sled bolted
on in three different rotations. Each of those still lines the shafts up
with the couplers, just with the motors swapped between dials, so a wrong
assembly would look right and quietly mix up the motors. Searched
(`scratchpad/joint_keyed_sweep.py`, same brute-force approach as every
other clearance fix) over each joint's own radius and angle, maximizing
worst-case clearance subject to: M6 countersink (7mm radius) + 3mm
driver access clear of all 3 rotated motor-body squares (motors sit on
this same face); countersink + 1.5mm wall clear of the boss recesses and
deck-leg footprints; leg + 3mm inside the 150mm circle; joints >= 85mm
apart (spread-out cones locate the plate better); and a keying mismatch
(Hausdorff distance between the pattern and itself rotated +/-120
degrees) >= 10mm. Result: all three at 60mm radius, at **62 / 172 / 288
degrees** (gaps 110/116/134). Rechecked with the exact rounded numbers:
**keying mismatch 14.6mm** (in a wrong orientation at least one leg is
14.6mm from every hole, so a screw can't start), and bare clearances from
each countersink's edge of **8.6mm** (nearest deck leg), **8.9mm**
(nearest motor body), **19mm** (boss recess), 9mm from each leg to the
front rim. The earlier regression lesson applies and was checked: the
motor-plate outline still contains all 12 motor bolt holes by construction
(`motor_pad_r`, independent of `joint_pts`), and the render shows all
three countersinks as separate, clean holes (checked by slicing the
rendered mesh, not just by eye).

Limits worth knowing: this keys *rotation*, not mirror-flipping, but the
sled can't be flipped (the countersinks are on one face only). It also
doesn't add a separate locating pin; the three cones do the locating.

**1c. Orientation pointer.** `front_plate()` gets an arrowhead-shaped tab
on the rim at +Y (toward dial 1, `pointer_angle`): 16mm wide, sticking out
10mm past the rim (`pointer_len`, `pointer_w`). A tab, not a drawn arrow,
because the back face's free space (between the motor sled's outline and
the rim) is only ~6-10mm wide, measured in shapely, too small for a
legible arrow. The tab is flat, part of the outline, so it needs no
supports, doesn't interfere with the door-facing magnets, and is visible
from both faces. **Open question:** which way is "up" on the real safe
door hasn't been confirmed. `hole_pts` (apex up) is the only basis for
+Y. Check it against the door and change `pointer_angle` if needed. If
the 10mm sticking out is in the way of anything on the door, shorten
`pointer_len`.

**3. Magnet pocket field.** Replaced the old ring of 6 pockets with a
hexagonal lattice of the same 8.00 x 1.9mm press-fit pockets, clipped to
2.5mm inside the rim and 2mm clear of each coupler bore, 2mm of plastic
between neighbors (`magnet_wall`). Lattice rotation and offset were
brute-force searched for the highest count (`scratchpad/magnet_pack.py`):
**135 pockets** (a hardcoded greedy fill reaches 136, not worth the hand-
placed list). The render and a slice of the rendered mesh both confirm
135 pockets, 3 bores, and a minimum wall of 2.00mm between pockets (2.8mm
to the bores and the rim). Two caveats: **magnet_wall = 2mm is a judgment
call, not bench-tested**. The pockets are interference fits, which stress
the wall between neighbors, and if one cracks while pressing magnets in,
raise `magnet_wall` (each +1mm costs roughly 15-20 pockets). And **135 is
more than the ~100 magnets on hand** (BOM updated): leave some pockets
empty or buy more. Paul's earlier point still stands: magnets alone may
not hold the full assembled weight; this field is for testing the mix.

**2. Arduino Mega base plate: no drawing exists, so the hole positions
were measured from Paul's photo; the standoff-free sled is built but
OFF by default until a bench check.** Searched for a drawing or hole
pattern for the plastic base shipped with the Mega 2560 and found none:
- SparkFun's community forum, asked directly, says they have no drawing
  for the plastic base and only gives its overall size, 114mm x 57.5mm:
  https://community.sparkfun.com/t/arduino-mega-plastic-frame-dimensions/36844
- Arduino forum thread on mounting to the base: no dimensions; says the
  base's own holes are M3 size but its PCB-attach holes leave too little
  clearance for screw heads, which matches Paul's own bench finding
  (screw heads hitting connectors):
  https://forum.arduino.cc/t/mounting-arduino-to-base/1018321
- A vendor listing for the base (reference M-ARD-BASEMEGA) and two
  community-made 3D-printed Mega stands on Thingiverse: none give hole
  coordinates, and the Thingiverse ones are the designers' own bases, not
  copies of the official part:
  https://store.mectronica.it/en/arduino-accessories/1766-transparent-perforated-plastic-base-for-original-mega-2560-card.html

So Paul photographed the real base straight-on with a mm ruler alongside.
Method: calibrated the scale from the ruler's ticks (17.02 px/mm), picked
all 10 hole centers in the 2048x1536 photo, then mapped photo pixels to
the Mega board's own coordinate frame with a rotation+scale fit through
the 6 base-plate holes whose real positions are published: the 4 PCB
holes (same Eagle-file numbers already used for `mega_hole_pts`) and the
2 Uno-compatible holes at (66.04, 7.62) / (66.04, 35.56)mm. The fit
doubles as a self-check, and it passed: the photo matches the board's
published hole pattern (including its mirror-image chirality, which also
fixes which way the base sits relative to the board), all 6 reference
holes land within **0.52mm max / 0.38mm RMS** of their published
positions, and two of them (the Uno holes) weren't used to pick the
orientation. Honest limits: the fitted scale (16.78 px/mm) disagrees with
the ruler's (17.02) by 1.4%, probably because the plate's raised features
sit at a different height than the ruler's top face; hole edges in clear
plastic are hard to pick; so every position below is good to about
**+/-0.4mm, not caliper-grade**.

Which holes: besides the 6 PCB/Uno-pattern holes, the base has 4 more:
two plain ~3.1mm holes inside U-shaped rims at board-frame (56.4, 7.4) and
(56.2, 45.4)mm, and two ringed holes on the end flange just past the
board's jack/USB end at (-5.5, 1.6) and (-5.3, 50.7)mm. These are taken to
be the base's surface-mounting holes (inferred from their position,
style and size, and from the Arduino forum calling the base's mounting
holes M3, not from a drawing).

Implementation (`mega_base_mount` in `dial_unit_housing.scad`): when true,
`electronics_deck()` drops the 4 Mega posts and gets 4 straight-through
M3 self-tap pilot holes (2.6mm, the same PETG thread-forming size already
used for the old posts, `set_screw_pilot_d`) at those 4 positions, rotated
by `mega_rotation` like everything else on the deck; `deck_outline()`
grows pads around them (the two flange holes sit outside the old hull, so
the deck gets ~1350mm2 bigger, 8900 -> 10250). Checked in shapely: the new
holes are 7.5mm+ inside the new edge and 26mm+ from any deck-leg
countersink. Rendered both ways: 12 watertight bodies each. **It was
first added as an option, default OFF** (`mega_base_mount = false`), because a
0.4mm error against a 3.1mm hole holding a 3.0mm screw will bind; the
coupon passed (see the entry above) and it's now the only mode. To
check before spending a deck print, `cad/mega_base_fit_test.scad` is a
4mm coupon with just those 4 holes (same orientation as the deck, notch
on the flange end): lay the real base on it and drive 4 M3 screws by hand.
Whichever holes bind, and by how much and in which direction, tells me
what to correct. Then flip `mega_base_mount` to true.

Screw length: M3x6 to ~M3x8 (base plate is a few mm thick, deck is 5mm,
holes go all the way through, a tip poking out the bottom lands in the
6mm clearance above the motor cans). The base plate's thickness wasn't
measured, so that range is an estimate, not a spec.

**Verification:** re-rendered clean (`Simple: yes`); trimesh confirms 12
separate watertight bodies (default and `mega_base_mount = true`); the
rendered mesh was sliced to confirm the
magnet field and the three countersinks directly (above); previews of the
door-facing face (magnet field, pointer) and the motor sled's outer face
(countersinks) were rendered and viewed.

## Motor bolt holes exposed at the plate edge (2026-10-03): a regression in the previous entry's joint relocation, caught by Paul before printing

A regression in the very next entry below, caught by Paul from looking
at the model, not from a print: "This doesn't look right. The motor
sled reverted to a triangle that was an issue. If you look closely at
the model, you'll see that one screw of each motor mount goes through
the edge of the sled. This feels like a step backward." He was right —
this was a real regression, not a false alarm.

**Diagnosis.** Built `motor_plate_outline()`'s actual hull polygon (as
it stood right after the joint-relocation fix below: corner circles at
the new `joint_pts`, plus the deck-leg pads) in Python/shapely and
checked all 12 real (rotated) motor bolt-hole positions against it
(`scratchpad/check_plate_coverage.py`). Confirmed exactly what Paul
saw: for each of the 3 motors, the one bolt hole nearest that motor's
own 90/210/330deg ray sat at 0.01mm from the hull's edge — on it, for
practical purposes.

**Root cause.** The OLD joint (`plate_corner_pts`, retired by the fix
below) sat at those SAME 90/210/330deg motor angles, just ~24mm
farther out along the same ray. That was never a deliberate design
feature — it was incidental, left over from when the joint and
`motor_plate()`'s own outline were the same triangle — but it happened
to extend the hull exactly far enough in each motor's own direction to
cover that motor's farthest-reaching bolt hole. Moving the joint to
54/174/294deg correctly fixed the joint-vs-motor-body collision it was
meant to fix (that check, and its +5.5mm margin, still holds — it's a
feature-vs-feature check, independent of the outline), but nobody
checked the OTHER requirement this outline has to satisfy — fully
containing every motor bolt hole — against the new joint position,
because at the time the old joint's accidental coverage there had
never been identified as something the design was relying on.

**Fix.** Added a third, independent set of hull-padding circles to
`motor_plate_outline()`, centered on `motor_pts` itself (the motor
shaft centers) rather than on the bolt holes or any rotation-dependent
feature — deliberately rotation-invariant, so a future change to
`motor_rotation` can't silently reopen this the way the joint move
did. Radius (`motor_pad_r`) is sized to fully contain
`nema17_body_clearance()`'s rotated 43.8mm clearance square at ANY
rotation angle, not just the current 40/70/10deg values: a square's
corner is `half*sqrt(2)` from its own center regardless of how it's
rotated, so `motor_pad_r = (43.8/2)*sqrt(2) + 2mm margin ≈ 32.97mm`.

**Verification** (`scratchpad/check_plate_coverage3.py`, built from the
.scad file's own constants after the fix was applied, not just the
standalone concept check that preceded it): all 12 bolt holes now
clear the plate edge by **11.33mm worst case** (up from 0.01mm) —
checked with the real M3 socket-cap counterbore (6.2mm) radius, not
just the bare hole. The joint-vs-motor-body and leg-vs-motor-body
clearances from the other two fixes are unaffected by construction
(this fix only adds hull material, via a feature-vs-feature-independent
check, so it can't reopen either). Re-rendered with OpenSCAD (clean,
`Simple: yes`) and re-ran the trimesh watertightness check: still 12
separate watertight bodies. Rendered fresh top-down and angled previews
of `rear_assembly()` confirming visually that every bolt hole, boss
recess, and deck leg now sits well inside the plate's edge — no more
triangle-shaped outline, no more holes poking through the side.
Pushed as a follow-up commit to the same PR as the fix below, since
that PR hadn't merged yet when Paul caught this.

## Dialer base changed to a circle, front-to-rear joint relocated (2026-10-03): the old joint sat right where the real motors now reach

Paul printed `rear_assembly()` with every fix through the previous
entry and reported a new problem: "there are no standoff holes to
attach the dialer base that attaches to the safe door to the motor
sled. As the motors were shuffled around, the old hole were taken."

**Diagnosis.** "The old holes" is `front_standoff_legs()`/the M3+insert
joint that bolts `front_plate()` (the "dialer base" — it carries the 3
dial couplers and mounts to the safe door) onto `motor_plate()`. Those
joint positions (`plate_corner_pts`, now `joint_pts`) were fixed at
`ring_points(3, plate_reach, 90)` — the SAME 3 angles (90/210/330deg) as
the motors themselves (`motor_pts`), just ~24mm farther out along the
same ray from center. That was harmless when first drawn, but the
motor-reorientation fix (two entries below) later rotated each motor's
body-clearance square up to 70deg about its own axis — on at least one
of the 3 motors, that rotated square now reaches out along that same
ray far enough to occupy the old joint's position. Nobody re-checked
the joint against the rotated motors when that fix landed, because at
the time nothing else had moved into its way yet — this is the same
class of problem as the deck-standoff-leg crowding two entries below,
just a different pair of features that drifted into collision as the
design evolved piecewise.

**Fix, in two parts, both requested by Paul:**

1. `front_plate()` becomes a plain **150mm-diameter circle**
   (`front_plate_outline()`), replacing the rounded-triangle outline it
   used to share with `motor_plate()`. This was Paul's own call, not
   forced by the clearance problem — but it helps the fix, because it
   decouples the joint's position from also having to define that
   plate's own shape. The old triangular outline only needed to be big
   enough to cover `hole_ring_r` + the coupler bushings + a magnet ring
   (~35.5mm of radius) — the 150mm circle is far more than that, all
   headroom Paul asked for on purpose.

2. The joint itself (`joint_pts`) moved off the motors' rays entirely.
   Found the same brute-force way as the deck-leg and Mega-rotation
   fixes earlier today (`scratchpad/joint_pts_sweep.py`): swept radius
   (capped at 61mm, so the joint's own 14mm corner-circle pad — the
   same convention the old corners used — stays inside the new circle's
   75mm radius with no extra bump needed) together with start angle,
   maximizing the worst-case clearance against all 3 rotated motor-body
   squares, all 3 boss recesses, and all 3 deck-leg pads. Best found:
   **61mm radius, 54deg start angle** — worst-case clearance **+5.5mm**
   (against motor 0's body), comfortably positive and not a bare-minimum
   number. Every motor/leg/boss position already sits on one of 6
   directions 60deg apart around this plate (motors at 90/210/330, deck
   legs at 150/270/30); 54/174/294 splits the difference between
   neighboring pairs rather than landing on either.

`motor_plate_outline()` (renamed from `plate_outline()`, since
`front_plate()` no longer uses it) keeps its hull-of-corner-circles
shape, just with the corners now at `joint_pts` instead of the old
`plate_corner_pts`.

**Verification**: re-rendered (clean/manifold) and re-ran the trimesh
watertightness check — still 12 separate bodies, all watertight.
Rendered isolated previews of both `front_assembly()` (confirms a clean
150mm circle with the 3 legs well clear of the coupler bushings) and
`rear_assembly()` (confirms the 3 new joint holes land at the plate's
corners, clear of the boss recesses and the deck legs) to visually
sanity-check the sweep's numbers before shipping them.

## Real motor spec confirmed (2026-10-03): STEPPERONLINE 17HE19-2004S, cross-checked against common_mounts.scad's NEMA17 numbers

Closes the open item at the end of the entry below (real motor
measurements were the most valuable outstanding confirmation). Paul
identified his actual motor's exact part number — STEPPERONLINE
17HE19-2004S, bipolar/4-wire, 59Ncm/2A — and checked its manufacturer
dimensional drawing against the real motor with calipers: "lines up."
Product page (has the dimensional drawing under its "Dimensions" tab):
https://www.omc-stepperonline.com/fr/e-serie-nema-17-bipolaire-59ncm-84oz-in-2a-42x48mm-4-fils-avec-1m-de-cable-et-connecteur-17he19-2004s

This is a strictly better source than what `nema17_can_length`'s
comment in `dial_unit_housing.scad` had been citing — "the well-known
17HS19-2004S1," an inference from an eBay listing's torque/current
class, not a confirmed match to the part actually on hand. Replaced
that citation with the real one.

Every NEMA17 figure already in `common_mounts.scad` checks out against
the drawing: 42.3mm body (42.3MAX), bolt spacing (drawing: 31±0.2mm —
tightened `nema17_bolt_square` from 31.04, a generic "typical" figure,
to the drawing's own 31mm nominal, still inside its own tolerance band
either way), 5mm shaft, 4.5mm flat, 15mm flat length, 48mm body length.
The 22mm×2mm pilot boss from the entry below — measured by Paul with no
vendor drawing available at the time — is also exactly on the drawing
(Ø22 0/-0.05 × 2mm), so that recess fix is now doubly confirmed, not
just caliper-measured. One new figure the drawing gives that wasn't
previously named: 24±0.5mm shaft protrusion from the mounting face —
checked against the drivetrain stack-up (`motor_plate_h` 6mm +
`motor_hub_len` 6mm = 12mm of shaft needed past the face) and it's well
inside the real 24mm, so no geometry change needed there, just a
confirmation nothing was secretly tight.

Net effect: no new clearance problems, and the `motor_rotation` fit
(entry below, idealized worst-case -1.17mm, flagged repeatedly as
having zero spare margin) now rests on a confirmed real `nema17_body`
figure rather than a generic one — doesn't change the number, but
removes the "what if the real motor is bigger than modeled" risk that
number carried.

Re-rendered and re-verified after retightening `nema17_bolt_square`
(31.04mm → 31mm): clean/manifold render, trimesh confirms the same 12
separate watertight bodies as before.

## Second motor-sled bench fit (2026-10-03): deck standoffs crowding motors, a real NEMA17 pilot boss, and the Arduino Mega's real (non-rectangular) hole pattern

Paul printed `rear_assembly()` with the motor-reorientation fix below and
test-fit the real motors again, plus did a first real joint test of
`deck_standoff_legs()` to `electronics_deck()`. Three new problems, one
piece of good news:

**Good news first**: the M6 countersunk self-tap joint from the entry
below (switched from M5 after real bench data) worked as designed —
"the M6 screws nicely tapped the standoff screw hole" attaching
`electronics_deck()` to the motor sled. No crack reported on the first,
hand-started screw (the untested-thin-wall caveat logged below), so
that fix is holding up under its first real test — still only one data
point, so the caution in that entry's print notes stays in place until
more of the joints are assembled.

**Problem 1 — standoffs crowding the motors.** 2 of the 3 motors
couldn't reach their own mounting screws because a `deck_standoff_legs()`
post was in the way, badly enough that Paul's own read on it was "if the
standoffs were not there, it would be a perfect alignment of the motors
to the motor holes" — i.e. the motor positions/rotation from the entry
below are right, the legs are the problem. Re-ran the same style of
brute-force 2D clearance sweep used for that motor rotation
(`scratchpad/deck_leg_sweep2.py` this session), checking `deck_leg_r`
against (a) each leg's clearance to the nearest rotated motor's
42.3+1.5mm body-clearance square and (b) each leg's clearance to the
nearest motor bolt-hole center, with a 5mm driver-access radius around
each hole. At the old `deck_leg_r` (28mm) the body-square margin was
already **-1.8mm** — genuinely overlapping, not just tight, which
matches Paul's report of the legs physically blocking the motors rather
than just making the screws awkward to reach. Moved `deck_leg_r` to
**46mm**: worst case **+4.8mm** to the nearest motor body, **+8.8mm** to
the nearest bolt hole — comfortable margin, chosen to stop there rather
than push further out and grow the plate more than needed.
`plate_outline()` grew a new `pad_deck_legs` option (same hull-padding
technique `deck_outline()` already used for its own posts) so
`motor_plate()`'s edge follows the legs out to their new position,
sized to leave exactly 1mm of material past each leg's surface per
Paul's own suggestion ("only 1mm from the edge") rather than the
corner's more generous padding. `motor_rotation` itself
(`[40, 70, 10]`) is unchanged — its binding case was always motor-to-motor,
not a leg (see the entry below), so moving the legs doesn't retire it,
and Paul's report above confirms the rotated positions are still
correct.

**Problem 2 — a real pilot/register boss nobody had modeled.** The real
motor has a round boss around the shaft, raised off the mounting face —
Paul measured it directly: **22mm diameter x 2mm tall**. Nothing in
`common_mounts.scad`'s NEMA17 dimensions covered this (the existing
`nema17_body_clearance()` relief is a flat 0.1mm face-touch pocket for
the square can outline only), so the boss was holding each motor proud
of the plate by 2mm, and tightening the first corner screw would tip it
off-perpendicular before the others could pull it flat. Added
`nema17_boss_d`/`nema17_boss_h` (22/2mm, measured — not a datasheet
figure, flagged as such) to `common_mounts.scad`, and a matching recess
in `motor_plate()` at Paul's own requested size — **23mm dia x 2.5mm
deep** (`boss_recess_d`/`_h` = measured + 1mm dia / + 0.5mm depth, a
non-interference running clearance, not a tight register).

**Problem 3 — the Arduino Mega's hole pattern was never real.**
`electronics_deck()`'s 4 corner posts were always a guessed symmetric
rectangle (`mega_x`/`mega_y`, each inset 5mm) — flagged as a guess in
the file's own comment since it was written, never sourced. Paul's
question ("perhaps the specs you were going from are for a different
model?") had the right instinct but not quite the right diagnosis: it's
the right model, the Mega's real mounting-hole pattern is just
genuinely **not a rectangle** — a known quirk of the Arduino Uno/Mega
board family (the hole nearest the power-jack/USB end sits in further
than a plain rectangle would put it, to clear those connectors).
Sourced the real hole centers from the Eagle PCB layout, independently
reported the same way by two write-ups (both reading the same official
board file, not a photo/caliper guess):
- https://softsolder.com/2010/09/02/arduino-connector-hole-coordinates-mega-1280-board/
- https://forum.arduino.cc/t/arduino-mega-mounting-hole-dimensions/17099

Both give (600,100) (600,2000) (3550,2000) (3800,100) mil from the
board's lower-left corner (by the power jack) — the Mega 2560 is
pin/hole-compatible with the 1280 these describe, per both sources.
Converted to mm and re-centered on the board footprint's own centroid
as `mega_hole_pts` in `dial_unit_housing.scad`. Fitting these in also
surfaced a second clearance problem: at the Mega's natural (unrotated)
placement, one of its real holes landed only ~1.2mm from a deck leg —
close enough that the leg's own M6 countersink cut undercut that post
and left it floating, disconnected from the deck plate (caught by the
render + trimesh check below, not visible by eye in the CAD). Fixed by
rotating the Mega's hole pattern 30° about the deck's center
(`mega_rotation`, found the same brute-force way, see that variable's
comment) — not the mathematical optimum, just a plain number with a
comfortable ~20mm margin, about 2x what's actually needed. **Open
item**: this rotation was picked purely to clear the standoff legs, not
for any cable-routing/connector-access reason — not yet checked against
how the USB/power/shield headers will actually face once the RAMPS
stack and wiring are in.

**Verification**: re-rendered `dial_unit_housing.scad` after all three
fixes (`openscad`, clean/manifold, no warnings) and re-ran the project's
usual trimesh watertightness check — 12 separate bodies, all watertight
(`front_assembly`, `rear_assembly`, `electronics_deck`, plus 3 complete
sets of `dial_coupler`/`oldham_motor_hub`/`oldham_disc`), matching what
should be printed. The first render after the Mega-hole fix (before the
30° rotation) came back with 13 bodies — one non-watertight-adjacent
floating piece — which is exactly how the leg/post collision above was
actually caught, not by inspection.

**On Paul's question** (does he need to take more measurements/photos
of the motors or the Mega): the Mega fix above didn't need new photos —
it's a standardized part with a sourceable, citable hole pattern, now
fixed from that source rather than a guess. The motors are a different
story: `common_mounts.scad`'s `nema17_body` (42.3mm) and
`nema17_bolt_square` (31.04mm) are still generic NEMA17 datasheet
figures, not measured off Paul's actual motors, and Paul's own earlier
comment ("it may be that the motors I received have a slightly different
size spec") is a real possibility worth closing out — especially since
`motor_rotation`'s -1.17mm idealized worst-case (above) has zero spare
margin to absorb a real motor running larger than spec. A caliper
measurement of the actual bolt-hole spacing and body width on one real
motor would be the most valuable single confirmation outstanding right
now.

## Motor-sled bench fit (2026-10-03): motor reorientation, deck standoffs switched to M6 self-tap, and a flagged mounting-weight problem

Paul printed and bench-fit `rear_assembly()` (motor plate + 3
`deck_standoff_legs()`) with 3 real STEPPERONLINE NEMA17 motors. Two
findings, from photos + his own description:

**Bad news, now fixed**: at the design's default (unrotated) motor
mounting, a motor can physically fouls a `deck_standoff_legs()` post —
the real can and the leg occupy the same space. **Good news**: rotating
each motor about its own shaft axis (no translation) clears all 3 legs
*and* all 3 motors clear each other, while keeping every drive shaft
exactly centered on its hole (translation was never needed — only
rotation).

The 3 rotation angles (`motor_rotation = [40, 70, 10]` in
`dial_unit_housing.scad`) aren't eyeballed off the photos — found by a
brute-force 2D collision search (`scratchpad/motor_indep_sweep.py` this
session, not checked into the repo): model each motor as the real
42.3mm `nema17_body` square, each leg as its 12mm-diameter circle,
search all 3 motors' rotations independently for the one that maximizes
the *worst-case* clearance across every motor-leg and motor-motor pair.
Worth being honest about the result: even at the best rotation found,
the idealized sharp-corner model still shows about **-1.17mm** (a
motor's own corner vs. its neighbor) — technically still interference,
not a clean positive margin. Corner rounding on the real motor can
doesn't rescue this (tested — the binding point isn't near a corner), so
this is a genuinely tight fit, not a modeling approximation that's
secretly fine. The honest read: `motor_min_spacing` (48mm, set when the
motor tier was first fanned out — see the Oldham coupler entry below)
was sized assuming face-to-face clearance between adjacent motors, which
only holds if they sit in a straight line — on a 3-point *ring* 120°
apart, the real closest-approach direction isn't face-on, so that
48mm figure was never quite as safe as its own comment claimed. Fixing
it properly (growing `motor_min_spacing`) was considered and rejected:
it directly grows `oldham_offset`, which was already flagged as "fairly
large relative to the ~36mm hole spacing" — growing it further pushes
the front-plate coupler bushings into colliding with *each other*
instead, trading one tight fit for a worse one. Given Paul's real,
assembled, PETG-printed bench test confirms it physically fits — which
is the actual ground truth, not the idealized flat-square model — this
revision trusts that result and ships the best rotation the search
found, rather than second-guessing a working physical test. Flagged in
`dial_unit_housing.scad`'s print notes: confirm the real fit again after
the next print, since there's no spare margin by design here.

**Deck standoffs switched from M3 + heat-set insert to M5 self-tap.**
Paul's call (he has both pan and countersunk M5/M6 screws on hand — the
same assortment boxes `standoff_screw_fit_test.scad` bench-tested
earlier) was to use whichever head style works best, since source stock
covers either. Went with **countersunk**: this joint exists specifically
to get 3 motor shafts precisely, repeatably centered on their couplers,
and a countersunk screw self-centers via its cone seat with zero radial
play once seated — pan head's looseness is exactly the wrong property
once the alignment is dialed in, including across future
disassembly/reassembly for maintenance.

**Correction while writing this up**: the first pass of this entry
picked M5 at a generic rule-of-thumb pilot size (3.7mm, from a published
soft-plastic self-tapping table), without having read the "Standoff
self-tap test results" entry just below — that PR (#3) merged into
`main` while this one was still in progress, so it wasn't visible yet
when the M5 choice was made. That entry is Paul's own real bench data,
and it says something different: **M5 didn't work at all** (too tight
to self-tap by hand, in either head style, at the 4.2mm bore tested),
while **M6 at a 5.4mm pilot worked well** (both head styles, bit in
cleanly, reusable thread). Going with the real result over the generic
table: **switched to M6**, pilot hole **5.4mm**
(`m6_selftap_pilot_d`), reusing `standoff_screw_fit_test.scad`'s own
already-sourced M6 countersunk head dimensions (`m6_csk_top_d` 14.0mm —
ISO 10642 dk(max) 13.44mm + margin) for the countersink pocket rather
than re-deriving them.

**This isn't a fully closed question, though** — flagging the same
caveat that entry raised, because it applies here *more* strongly, not
less: that bench test's 5.4mm hole was cut into the self-tap test's M5
cap, which has ~6.3mm of wall around it (`cap_dia` 18mm). The real
`deck_standoff_legs()` leg is `leg_dia` 12mm, so a 5.4mm bore there
leaves only **~3.3mm of wall** — thinner than even the 3.9mm the
original entry was already unsure about, let alone the 6.3mm that
actually got tested. `leg_dia` was deliberately NOT grown to compensate
(e.g. to 14 or 15mm for a safer wall): that would eat directly into the
motor-clearance margin from this same revision (above), which is
already down to about -1.17mm in the idealized model and relies on
Paul's bench-confirmed fit at the CURRENT 12mm leg diameter — growing
the leg would invalidate that result. So: self-tap into a thinner wall
than anything bench-tested so far, with a bigger (M6, more torque)
screw than what that wall has seen. Start this one BY HAND, not a power
driver (the test entry's own suggestion for exactly this situation),
and treat the first real leg as a crack-risk check, not a foregone
conclusion — if it splits, the fallback is reverting this joint to M3 +
heat-set insert like the front joint, not pushing to a bigger bore (that
fights the motor clearance again).

Engagement depth (`m6_selftap_depth`, 12mm, ~2x the M6 major diameter)
is a reasoned rule-of-thumb, not a sourced number — no published minimum
engagement length was found, so this is worth a pull-out check on the
bench alongside the crack-risk check above. Screw length: M6x13 to
M6x16 all clear without bottoming (deck_thickness 5mm + up to ~11mm
engagement, pilot hole 12mm deep) — pick whichever's on hand closest to
15mm. **Front standoffs (`front_standoff_legs()`, front-to-rear joint)
are UNCHANGED** — still M3 + heat-set insert + M3x8, per the original
v0.3/v0.4 design below; only the rear-to-deck joint moved to M6. The M3
insert/screw kits ordered for this project (see `docs/bom.md`) are still
needed for that front joint plus other M3 uses (e.g.
`electronics_deck()`'s Mega corner posts), not wasted by this change.

**Open problem, not solved here: bottom-plate mounting.** Paul flagged
that `front_plate()`'s magnet ring — sized and confirmed back when this
unit was envisioned as light (see the Mounting section below) — almost
certainly can't hold the weight of the full assembled unit (3 motors +
electronics_deck) hanging off the door by magnets alone. His own
expectation is "probably a combination of magnets on the base and then
an arm/magnet combination that transfers the weight to the top of the
safe" — not designed yet, and deliberately not attempted in this
revision (no real dimensions or constraints for a top-of-safe arm exist
yet). Logged here as a known TODO so it doesn't get lost, same as the
`dial_spacing` bench-fit TODO already tracked below.

## Standoff self-tap test results — the 4.2mm leg bore is too tight by hand; 5.4mm self-taps M6 well with a driver

Paul printed `standoff_screw_fit_test.scad` and reported back:

**The actual leg stubs (4.2mm/6mm bore) didn't work** — none of the
M5/M6 screws, pan or countersunk, could cut in by hand. Too tight.
Confirms the "today only, don't trust it" framing that test was given
was the right call — the real fix is still the M3x8 + heat-set insert
hardware.

**Unplanned but useful result**: driving an M6 screw (both pan and
countersunk head, with a power driver — some real torque needed to
start the cut) into the *M5 cap's* 5.4mm clearance hole worked well —
bit cleanly into the PLA, no cracking, and the resulting thread was
reusable (removed and re-driven without stripping). The M6 cap's own
6.4mm hole behaved as the plain clearance fit it was designed to be,
as expected.

**Caveat worth flagging before reusing this number on the real
legs**: the M5 cap that worked has a lot more meat around its hole
than the real standoff leg does — `cap_dia` 18mm around a 5.4mm hole
is roughly 6.3mm of wall, versus the real leg's `leg_dia` 12mm around
its bore, ~3.9mm of wall (see the self-tap test's own header). A
power driver biting cleanly into 6.3mm of wall doesn't necessarily
mean it's equally safe on 3.9mm — that's a real difference in crack
risk, not just a detail. If this gets tried on the actual legs, worth
either hand-driving it first (slower, more control) or bumping the
real leg's bore from 4.2mm toward ~5.4mm if self-tapping M6 becomes
the intended path rather than a one-off bench finding.

**Takeaway**: 5.4mm is a good self-tap pilot diameter for M6 (pan or
countersunk) in PLA with a driver, generously walled. Not yet
confirmed on the real, thinner-walled leg geometry.

## Printed internal thread fit test — can a real M5/M6 screw thread directly into PLA?

New file, `cad/printed_thread_test.scad`. Different question from the
self-tap test just below: that one tests a plain pilot hole with a
screw cutting its own grip as it goes in; this one tests an actual
*modeled* ISO-profile thread, printed directly into the hole, that an
ordinary screw threads into with no self-tapping and no insert at all.
Paul specifically wanted the latter — the self-tap test is still kept,
just answers a different question.

**Thread profile**, checked against the ISO basic-profile formulas
rather than guessed: H (fundamental triangle height) = 0.8660254 ×
pitch; major-to-minor diameter difference = 1.0825318 × pitch. From
that, the truncated profile actually cut is a 60° trapezoid: root flat
pitch/4 wide, crest flat pitch/8 wide. Only M5 (×0.8) and M6 (×1.0) are
tested — same reasoning as the earlier printed-thread research: a
0.4mm nozzle is at or past the viable size right around M5/M6, M3/M4
were the ones specifically steered toward inserts instead.

**How it's built**: the thread is cut into each test block by
*subtracting* a solid "male" thread tool (a core cylinder at minor
diameter + a helical ridge out to major diameter, swept with
`linear_extrude(twist=...)`) — the same idea as a tap cutting a nut.
First attempt at the ridge-to-core union left two disconnected
watertight solids instead of one (the ridge's root sat exactly on the
core's surface — a coincident-face issue, same category as the
`eps_c` overlaps used throughout this project) — fixed by giving the
ridge's root a 0.1mm radial overlap into the core, verified in
isolation (rendered, exported, checked with `trimesh` for a single
connected watertight body) before using it as a cutting tool.

**Clearance sweep**: FDM holes tend to print undersized, so rather
than guess the right oversize for Paul's printer, this sweeps +0.0 /
+0.2 / +0.4mm diametral clearance per size (same approach as
`tube_socket_test_key_set.scad`'s tooth-height sweep) — 6 blocks
total, each a short through-hole, generously walled since the thread
holding is what's being tested here, not wall-splitting (that's the
self-tap test's job).

**Verified** the same way as everything else in this file: rendered,
checked `trimesh`-watertight (6 separate, correctly isolated bodies),
and visually inspected close-up before treating it as done. Full
6-block render takes ~50s — cut `$fn` and the twist-extrude `slices`
down from an initial attempt that was far higher resolution than
needed and didn't finish in a reasonable time.

## Standoff screw fit test — throwaway PLA coupons for today's temporary fastening

New file, `cad/standoff_screw_fit_test.scad` — not part of the robot,
a bench aid for the "1. Temporary fastening for today" question raised
in the v0.4 addendum below (self-tapping into the standoff legs' 4.2mm
x 6mm blind bore with an on-hand screw while the real M3 brass
heat-set inserts are still on order).

Paul has two 1080pc assortment boxes on hand (M3/M4/M5/M6, same length
breakdown): black label = countersunk hex-socket, red label = Phillips
pan/round head. Of those, only M5 and M6 are big enough to self-tap the
existing 4.2mm hole at all — M3 and M4 are at or under that diameter
and would just rattle, so they're excluded rather than silently
skipped (noted in the file header). That leaves 4 combinations to
bench-test: M5 pan, M5 countersunk, M6 pan, M6 countersunk.

Each combination prints as two small parts, not the real legs — a
stand-in leg stub (just `leg_dia` + the real `insert_hole_d`/
`insert_hole_depth` bore, copied from `dial_unit_housing.scad` by hand
since those are plain variables there, not shared module state) and a
stand-in cap (a clearance hole + a head pocket sized for that screw —
flat counterbore for pan/round heads, a 90° conical countersink for
the countersunk ones). Head-pocket sizing used current ISO 7045 (pan)
/ ISO 10642 (countersunk) catalog head dimensions rather than guessed
numbers, plus margin since these are generic assortment-box screws,
not parts actually certified to either standard. Each part carries a
small recessed-text ID tag off to the side (same convention as
`tube_socket_test_key.scad`'s engraving), kept off the bore/pocket
being tested so labeling can't skew the fit or crack result.

**Verified** the same way as the structural note below: rendered,
exported to STL, and checked with `trimesh` rather than trusting
OpenSCAD's own "Volumes" count — 8 watertight, correctly separated
bodies (4 legs + 4 caps), matching the 8 intended parts.

**Not a design change** — whichever screw wins on the bench is for
today's test assembly only; the real joint is still M3x8 DIN 912 +
M3 brass heat-set insert, per the v0.4 addendum below.

## Key-turner v0.2 — added the missing motor shaft hole; set-screw fix shared with the dial unit

Paul printed all the parts for both units for a first test assembly.
The dial unit "seems to be in good shape." The key-turner
(`key_turner_housing.scad`) was not: no way for the motor to actually
reach or drive the gripper. Checked by reading the file rather than
guessing, and both turned out to be real, confirmed gaps:

**1. `frame()` had no shaft hole at all.** It bolts the motor to a
raised boss (`nema17_bolt_holes()`), but the only things ever cut from
that boss+plate were the bolt holes and the magnet ring — nothing for
the shaft itself. The motor mounts on the boss's outer face and needs
its shaft to reach all the way through to the door-facing side where
`gripper_hub()` lives; with no hole, the shaft would have driven
straight into solid plastic. This wasn't a sizing mistake, just a
missing cut — fixed by adding a `nema17_shaft_d + 2` clearance hole
through the full `plate_thickness + boss_h` (11mm).

Checked this closes geometrically rather than assuming it does: the
real motor's shaft protrusion is 24mm (STEPPERONLINE 55Ncm/2A, same
source as v0.4's can-length figure). 24mm − 11mm (through `frame()`) =
13mm left for the washer/spacer gap + `gripper_hub()`'s own 10mm-deep
bore — about 3mm of spacer budget, enough for one thin washer, not
several stacked. Noted directly in the file so it isn't rediscovered
the hard way at assembly.

**2. The set-screw hole (`dshaft_bore()` in `common_mounts.scad`,
shared by both units) was a dead end.** It was sized at 3.2mm — a
standard M3 *clearance* size, meant for a screw passing through into
something already threaded. Nothing on either side of that hole was
threaded (no nut, no insert), so a set screw would have slid straight
through with zero grip — it could never have clamped onto the motor
shaft's flat, on either unit. Fixed by shrinking it to 2.6mm, the
right pilot size for an M3 screw to self-tap/thread-form directly into
printed PETG. Because `dshaft_bore()` is shared, this one fix covers
the dial unit's `oldham_motor_hub()` *and* the key-turner's
`gripper_hub()` — worth reprinting both hub parts before relying on the
set screw for anything beyond a loose test fit. Thread engagement once
self-tapped is generous either way — the dial unit's hub wall is
~10.9mm thick there, the key-turner's ~14.4mm, both well past the usual
~4.5mm (1.5x diameter) minimum for M3. A cone-point or cup-point set
screw starts into a self-tapped hole far more easily than a flat-tip
one.

**Verified** with the same render + trimesh check as the dial unit: 3
disconnected, watertight bodies for the key-turner (frame, gripper hub,
clamp bar), 12 for the dial unit (unchanged count — this was a hole
resize, not a structural change), plus a visual render confirming the
through-hole is actually open in `frame()`.

**Not yet done:** same bench-fit caveat as the rest of v0.1 — the key
bow's real dimensions are still unmeasured (`slot_width_max`/
`slot_depth` are placeholders), and the 24mm-shaft/3mm-spacer math
above hasn't been checked against a real assembled stack yet.

**Naming:** this file and the rest of the repo already call it the
key-turner unit / `key_turner_housing.scad` — worth standardizing on
that rather than "door bolt turner" elsewhere, since it's the name
already used throughout `control/sequence.md`, the README, and this
doc.

## v0.4 addendum — screw length corrected to M3x8 (was wrongly M3x10/M3x12)

Asked while Paul was about to do a real test assembly, so it got
checked precisely rather than repeated from the earlier (wrong) print
note. Both bolted joints use a 3.2mm-deep screw-head counterbore and a
6mm-deep blind insert bore in the leg — but the *plate material between
them* differs: 2.8mm for the front-to-rear joint (6mm `motor_plate_h`
minus the counterbore) vs. only 1.8mm for the rear-to-deck joint (5mm
`deck_thickness` minus the counterbore). That sets a hard ceiling on
usable screw length before the tip bottoms on the leg's solid floor
*before* the head seats flush: ~8.8mm front, ~7.8mm deck. The original
note ("M3x10 or M3x12") didn't account for this and would leave the
rear-to-deck joint standing proud rather than actually clamped. **M3x8**
clears both ceilings with a standard ~5mm-long M3 heat-set insert,
confirmed by computing it rather than estimating
(`m3_head_depth` + `insert_hole_depth` + each plate's own thickness, per
joint). `docs/bom.md` and `dial_unit_housing.scad`'s print notes updated
to match.

## v0.4 — electronics deck moved onto its own standoff tier (real print showed it fouling a motor)

Paul printed the v0.3 STL overnight. Two problems surfaced: (1)
`electronics_tray` was still cantilevered (only reachable by
`bridge_arm()` off one edge of `motor_plate`), so Bambu Studio needed
supports for it; (2) worse, once printed, the tray physically sits
where one of the 3 dial motors needs to go — that motor can't be
bolted on.

**Root cause, found by re-deriving the geometry rather than guessing:**
`electronics_tray` was positioned at `tray_z = ...motor_plate_h + 4` —
only 4mm proud of `motor_plate`'s outer face. But that's also the face
the NEMA17 motors themselves bolt to (their shaft has to reach through
`motor_plate` into the `rear_standoff` cavity to hit the Oldham hub,
which by NEMA convention puts the motor's mounting flange — and its
whole can — on the *outer* face, not the cavity side). The housing
never modeled the can's real length: `common_mounts.scad`'s
`nema17_body_clearance()` is a deliberate 0.1mm face-clearance pocket
("a printed bracket only needs to touch the mounting face, not hug the
body"), not a stand-in for the actual body depth. With only 4mm of
clearance against a real ~48mm-long can, the tray was always going to
collide with whichever motor happened to be closest to it — which,
given `bridge_arm`/`electronics_tray` were placed at a fixed `+X`
offset while the 3 motors are arranged in a triangle, was going to be
one specific motor regardless of the placeholder dial-hole numbers.

The real can length wasn't in this repo anywhere, so it was looked up
rather than guessed: the exact ordered part (`docs/bom.md`,
"STEPPERONLINE 55Ncm 2A, pack of 5") is listed at **42×48mm** on the
matching eBay listing —
[ebay.de/itm/204638353437](https://www.ebay.de/itm/204638353437) —
which matches the well-known STEPPERONLINE 17HS19-2004S1 (0.59Nm/59Ncm
class, same torque tier), whose own datasheet confirms the same 48mm
body length and a 24mm shaft protrusion —
[datasheet PDF](https://static.maritex.eu/file/display/5sXxpHH1SP-JwnhJEZ0lhfX-xdYKZRi3/17HS19-2004S1_Full_Datasheet.pdf).

**Fix, per Paul's own suggestion ("build a third level above the
motors"):** `electronics_tray`/`bridge_arm()` are replaced by
`electronics_deck()` — a third bolt-on tier, following the same
bolt-together pattern v0.3 already established rather than a fused
cantilever:

- `deck_standoff_legs()` — 3 more legs (same design as
  `front_standoff_legs()`: heat-set insert bores, M3 screws), this
  time growing from `motor_plate`'s outer face, at `deck_leg_pts` —
  positioned 60° offset from the 3 motor angles (`ring_points(3,
  deck_leg_r, 150)` vs. the motors' `start_angle=90`) so they land on
  solid `motor_plate` material in the gaps between motors, confirmed
  clear of every bolt pattern/shaft hole by render. Height =
  `nema17_can_length + 6mm` clearance — tall enough to clear the full
  real can length, not the old 4mm token gap.
- `electronics_deck()` — the Mega/RAMPS mounting plate itself
  (same 4 corner standoffs as the old tray), now centered on the
  assembly's own axis rather than cantilevered off to one side, bolted
  onto `deck_standoff_legs()` via M3 screws + counterbores, mirroring
  how `motor_plate` bolts onto `front_standoff_legs()`.

Trade-off worth flagging: because the deck sits directly above/behind
the whole motor cluster (by design — that's what clears every motor
regardless of which one the tray used to favor), 2 of its 3 mounting
screws land underneath the Mega board's own footprint once that's
installed on its posts. Servicing those means removing the Mega first
(4 easily-accessible screws) — normal build-order inconvenience, not a
blocker, and noted in the file's print notes.

**Verified** with the same render + trimesh check as v0.3: 12
disconnected, all-watertight bodies (9 drivetrain parts + 3 assemblies,
each its own single solid, none fused to another), plus a manual
top-down render confirming the deck legs land clear of every motor
hole/bolt pattern and the front-to-rear mounting holes.

**Not yet done:** the same bench-fit/insert-press-in caveat as v0.3,
now for 6 inserts instead of 3 (`docs/bom.md` updated accordingly).

## v0.3 — dial unit split into two bolt-together assemblies (fixes unsupported bridge in slicer)

Bambu Studio flagged an unsupported region on `frame()` (the v0.2 static
body: `front_plate()` + `motor_plate()` + `electronics_tray()` fused into
one printed object). Cause: those three plates were connected only by 3
thin (10mm) `support_pillars()` and a `bridge_arm()` across the
~`rear_standoff` (~20mm) gap between `front_plate` and `motor_plate`.
Sliced with `front_plate` on the bed, `motor_plate` — a large flat disc —
and everything beyond it (tray) was floating in mid-air, bridging between
3 thin posts spaced ~50mm apart: far past any safe unsupported span.

**Fix: stop fusing the two plates into one printed body.** `frame()` is
replaced by two independently-printable modules that bolt together after
printing, instead of one part with a bridged gap:

- `front_assembly()` = `front_plate()` (unchanged: 3 Oldham bushings,
  magnet ring) + `front_standoff_legs()` — 3 solid posts (12mm dia, up
  from the old 10mm pillars, for more meat around the insert) growing
  straight up from the plate at the same corner positions the old
  pillars used. A plate with posts standing on it is fully
  self-supporting on its own — no bridging, nothing floating.
- `rear_assembly()` = `motor_plate()` + `bridge_arm()` +
  `electronics_tray()`, unchanged in shape, just no longer fused to
  `front_plate()`. Printed with `motor_plate`'s mating face on the bed,
  it's the same self-supporting shape it always was (a flat plate with
  the tray/gusset built up from it) — the floating problem was *between*
  this and the front plate, not within it.

The two mate at the same 3 corner positions (`plate_corner_pts`) the
pillars used, now joined with **M3 screws into heat-set inserts**:
`front_standoff_legs()` gets a blind bore (4.2mm dia x 6mm deep) in the
top of each leg for a heat-set insert; `motor_plate()` gets a matching M3
clearance hole + a counterbore (6.2mm dia x 3.2mm deep) on its outer
(away-from-front-plate) face so screw heads sit flush. Screws go in from
that outer face — the back of the whole assembly, unobstructed by the
tray, which sits off to one side — down through `motor_plate` and into
the legs' inserts. `rear_standoff` (and therefore the whole drivetrain
stack: neck + Hub B + disc gap + Hub A) is unchanged; only how the two
plates are held apart changed, not how far apart.

**Print orientation:** each assembly is self-supporting in its natural
orientation — `front_assembly` with the front plate's door-facing face
down (as before), `rear_assembly` with `motor_plate`'s mating face down.
Neither needs the other underneath it, so no bridging supports either
way.

**Not yet done:** heat-set insert install (soldering-iron press-in,
after printing, before final assembly) and a real bench test that the 3
legs land accurately enough on the motor plate's holes — same
first-pass-pending-bench-fit caveat as everything else in v0.1/v0.2
below.

## v0.2 — dial unit's motor offset bridged with a printed Oldham coupler, not a bought part

v0.1 (below) resolved the NEMA17-vs-hole-spacing collision by fanning
the 3 motors onto a larger ring and calling for an off-the-shelf 5mm-5mm
flexible shaft coupler per motor to bridge the resulting offset. Revisited
on request ("might it be possible to print the flexible shaft coupler?")
and switched to a printed **Oldham coupler** instead — reasoning below.

**Why not a bought bellows/helical flex coupler (the "obvious" printed
option):** those work by elastically *flexing* the printed material
every cycle. That's a poor match for PETG here — the dial motors cycle
tens of thousands of times over the ~8,000-combination search (3 dials
per attempt), and repeated elastic flexing is PETG's weak point
(fatigue cracking). TPU would flex fine but adds spring-back that works
against positioning accuracy.

**Why an Oldham coupler instead:** it's 3 *rigid* pieces — two hubs,
each with a slot cut across its face 90 deg apart, plus a loose middle
disc with two perpendicular tongues. The offset is absorbed by the
tongues sliding in their slots once per revolution, not by anything
bending. That's a genuinely good match for FDM printing — no fatigue-prone
flexing, just a sliding fit, and it's the same coupler *type* v0.1 had
already pointed at as the right off-the-shelf choice ("Oldham-style...
is specifically designed for parallel misalignment") — this just prints
that idea instead of buying it.

**Implementation** (`common_mounts.scad`'s new `oldham_*` modules, used
by `dial_unit_housing.scad`):
- Hub B is now integrated directly into `dial_coupler()`'s rear end
  (no more separate round shaft stub) — a slotted hub, then a neck
  through the bushing, then the same collar + spline plug as before.
- Hub A (`oldham_motor_hub()`) is a new small loose part that mounts on
  the motor's own D-shaft, slot rotated 90 deg from Hub B's.
- The disc (`oldham_disc()`) is a new small loose part sandwiched
  between them.
- Standard Oldham sizing rule (slot length >= tongue width + 2x max
  offset) applied to the dial unit's actual ~6.9mm offset (derived from
  `motor_ring_r - hole_ring_r`, itself from the placeholder 36mm hole
  spacing and the 48mm motor-safe spacing) — this makes for a fairly
  large hub (~27mm dia) relative to the ~36mm hole spacing, tight but
  workable: the 3 bushing bores (now sized to pass the hub through
  during assembly, not just the collar) leave about a 6-7mm web of
  plate material between adjacent bores. Worth keeping an eye on when
  bench-fitting.

**Bonus effect, not the goal:** the axial stack a printed Oldham joint
needs (a hub, a thin disc, another hub — a few mm total) is much
shorter than the ~25mm a bought coupler plus clearance needed. This let
`rear_standoff` shrink from 42mm to ~20mm — the whole dial unit is
now noticeably more compact front-to-back.

**Superseded by this:** the "buy 3x flexible shaft coupler" line —
removed from `docs/bom.md`, nothing to order for this anymore.
`docs/bom.md` now instead carries a small material note (print in
PETG-CF for the wear-facing hub parts, same as the spline couplers).

**Not yet validated:** this is a first-pass sizing, same caveat as
everything else in v0.1 below — needs a real test-fit of the disc in
its hubs (print, check the tongue/slot clearance feels right, adjust
`oldham_fit` if it binds or rattles) before committing to a full print,
the same iterate-on-clearance approach already used for the spline key.

## v0.1 — first-pass housings, built from photo-read placeholders

Built per Paul's go-ahead to try a first pass now rather than wait on
fresh caliper measurements ("the keys design we have is good enough
for a first pass") — the confirmed tooth geometry (HEIGHT 2.00mm /
WIDTH 1.04mm, see `docs/decisions.md`) carries over unchanged into the
dial unit's motor couplers.

### Where the two open dimensions came from

`control/sequence.md`'s "Still open" list explicitly warns against
reading dimensions off photos rather than calipers ("a caliper/tape
number beats pixel-peeping" — the same lesson as the v0.2 bore-diameter
mistake in `docs/decisions.md`, which was wrong by ~50-60%). That
mistake was scaling a photo by a ruler-tick calibration factor and then
measuring a *different* part of the image in pixels. What's used here
is different in kind but not risk-free: reading the printed number on a
tape/ruler laid directly against the feature being measured, in the
same photo — no pixel-scaling, no calibration factor — but still read
by eye off a photo rather than held in hand with calipers, so treat
both numbers below as **placeholders good enough to make a first-pass
model, not confirmed dimensions**. Neither open item in
`control/sequence.md` is being closed by this.

- **Dial-hole spacing: 36mm placeholder, equilateral triangle.**
  Read from `docs/photos/dial-holes-ruler-2.jpg` (vertical ruler
  directly against 2 of the 3 holes: ~32mm apart) and
  `docs/photos/star-opening-tape-2.jpg` (horizontal tape across all 3:
  the two "top" holes read ~20mm apart). Both readings are in the
  same 20-40mm range and the 3 holes are clearly NOT collinear — they
  read as a compact, roughly equilateral cluster, not a row. Modeled
  as an equilateral triangle, side = 36mm (middle of the observed
  range). Uncertainty: call it +/-5-8mm from eyeballing tape-tick
  alignment in a photo, not a direct caliper read.

- **Dial cluster to socket #4: ~55mm, informational only.**
  Also from `star-opening-tape-2.jpg` — the single key hole reads at
  roughly the "7cm" tick, the dial cluster spans roughly "11-13cm", so
  ~50-60mm gap. `control/sequence.md` only needs this for cable-length
  planning ("doesn't need precision"), so this is good enough as-is —
  not fed into either housing's geometry, since the two units mount
  independently.

- **Key bow dimensions: still genuinely unmeasured.**
  `docs/photos/real-key-bow-closeup.jpg` confirms the bow is an ornate
  4-lobed/cross shape (matches `control/sequence.md`'s "traditional
  ornate bow" note) but has no ruler/tape in frame — no legible
  reading available at all, photo or otherwise. Rather than guess a
  tight pocket around an unmeasured decorative outline, the key-turner
  gripper (below) is designed as an adjustable clamp instead, which
  doesn't need the exact shape.

### New finding: NEMA17 motors don't physically fit at the real hole spacing

Not a placeholder — a real geometric conflict, discovered by combining
the photo-read 36mm hole spacing with the STEPPERONLINE NEMA17 motors
already ordered (`docs/bom.md`): the motor body is 42.3mm square, so 3
of them cannot sit directly, coaxially behind 3 holes only 36mm apart —
the bodies collide regardless of what the true spacing turns out to be
(even the low end of the observed 20-40mm range is tighter than a
single motor body).

`cad/dial_unit_housing.scad` resolves this by mounting the 3 motors on
a second, larger ring (48mm side, safely clear of body collisions) at
the *same* triangle angles as the real holes — a pure radial
(parallel, non-angular) offset of a few mm per motor — and bridging
each motor shaft to its coaxial spline coupler. The 18°-per-step
resolution this needs (20 positions/wheel, re-homed every run via
stall detection) tolerates a bit of coupler backlash far better than a
precision positioning task would.

**Superseded by v0.2 above:** this originally called for an
off-the-shelf 5mm-5mm flexible shaft coupler per motor. Switched to a
*printed* Oldham coupler instead — same coupler type, printed rather
than bought. Nothing to order for this anymore.

### Key-turner gripper: adjustable clamp instead of a fitted pocket

Since the bow's real dimensions aren't available (see above), the
gripper is a hub with an open slot (9mm wide, 20mm deep — generous
versus a typical ornate bow's few-mm thickness) that the bow slides
into after the key is already hand-seated in the lock, plus a separate
thumbscrew-tightened clamp bar that closes the slot once positioned.
This sidesteps needing the exact ornate outline entirely — a clamp
only cares about thickness and grip width, both of which the slot's
range accommodates without a precise number. Single motor, so no
flex-coupler offset problem here — the motor mounts directly behind
the hub.

### Structural note

Both housings originally modeled their motor mounts as geometry
sitting in space near the front plate but not actually connected to
it — an easy mistake with parametric `translate()`-heavy OpenSCAD, and
one `openscad --render` alone didn't catch (its "Volumes" count turned
out to include a degenerate coplanar sliver as its own "volume" in one
case, which was a red herring). Caught by exporting to STL and checking
connected components with `trimesh` in Python instead — a more reliable
check than reading OpenSCAD's own render statistics. Fixed by adding
explicit support pillars between the two plates and a bridging gusset
out to the electronics tray. Worth doing the same trimesh check on any
future revision of these files before treating a render as done.

### What's still first-pass / explicitly deferred

- No enclosure lid, walls, or cable glands on the electronics tray —
  just a floor + standoff posts sized for the Arduino Mega's outline
  (not its exact hole pattern yet either).
- Motor mounting bosses use generous body clearance, not exact NEMA17
  can dimensions (standard, low-risk simplification, not a measured
  placeholder).
- Neither housing has been bench-fit — both are first-pass geometry
  pending a real print and fit check.

### Bench-fit TODO before the real print

- Confirm the 36mm dial-hole triangle with calipers directly on the
  door (per `control/sequence.md`'s own standing caution against
  trusting photo reads for this).
- Test-print and check the fit of one Oldham hub pair + disc (see v0.2
  above) before committing to a full dial-unit print.
- Measure the real key bow's thickness and grip-section width; confirm
  both sit inside the gripper's 9mm/20mm slot range before relying on
  it, resize and reprint if not (cheap — it's a small standalone part).
