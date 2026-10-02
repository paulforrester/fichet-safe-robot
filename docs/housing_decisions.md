# Housing — design decision log

Working notes on the two 3D-printed housings (`cad/dial_unit_housing.scad`,
`cad/key_turner_housing.scad`), most recent first. Companion to
`docs/decisions.md` (tube-socket test key geometry) and
`control/sequence.md` (control architecture) — this file covers the
mechanical housings that carry that geometry onto the actual door.

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
