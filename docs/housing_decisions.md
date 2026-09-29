# Housing — design decision log

Working notes on the two 3D-printed housings (`cad/dial_unit_housing.scad`,
`cad/key_turner_housing.scad`), most recent first. Companion to
`docs/decisions.md` (tube-socket test key geometry) and
`control/sequence.md` (control architecture) — this file covers the
mechanical housings that carry that geometry onto the actual door.

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
each motor shaft to its coaxial spline coupler with a short off-the-shelf
flexible shaft coupler (5mm-5mm). Parallel-offset shafts are exactly
what an Oldham-style coupler is designed for (cheap, common — widely
sold for 3D-printer Z-axis couplings), and the 18°-per-step resolution
this needs (20 positions/wheel, re-homed every run via stall detection)
tolerates the small amount of backlash a flex coupler adds far better
than a precision positioning task would.

**Follow-up for `docs/bom.md`: 3x 5mm-5mm flexible shaft coupler
(Oldham or jaw type, ~25mm long) — not yet ordered, not on the BOM
before this.**

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
- Order the 3 flexible shaft couplers (see follow-up above) before
  attempting the dial unit.
- Measure the real key bow's thickness and grip-section width; confirm
  both sit inside the gripper's 9mm/20mm slot range before relying on
  it, resize and reprint if not (cheap — it's a small standalone part).
