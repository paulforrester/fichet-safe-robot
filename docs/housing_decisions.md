# Housing — design decision log

Working notes on the two 3D-printed housings (`cad/dial_unit_housing.scad`,
`cad/key_turner_housing.scad`), most recent first. Companion to
`docs/decisions.md` (tube-socket test key geometry) and
`control/sequence.md` (control architecture) — this file covers the
mechanical housings that carry that geometry onto the actual door.

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
