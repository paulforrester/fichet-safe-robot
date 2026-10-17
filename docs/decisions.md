# Tube-socket test key — dimensional decision log

> **Revision 2026-10-17.2** · project revision baseline (mechanical log; not affected by the wiring changes) · log: `./revisions.md`


Working notes on how the test key's dimensions were arrived at, most
recent first. Terminology (WIDTH / HEIGHT / DEPTH) is defined in
`tooth_terms_diagram.png` in this folder.

## 2026-10-17 (evening) — Correction: the twist-lock is replaced by a tapered hex and an M3 screw

Paul printed the twist-lock parts (revision 2026-10-17.1, below): the caps
were hard to impossible to fit, and the double-D had far too much play. His
design replaces both (revision 2026-10-17.2, `docs/housing_decisions.md`
has the detail): a tapered hex (10° per flat) on the shaft and in the gear,
pulled together by an M3×10 countersunk from the back, self-tapping into the
shaft. The plug (T2) is unchanged. Fit coupon first: `taper_hex_coupon.stl`.

## 2026-10-17 (later) — Correction: the T2 gear-shaft couldn't be assembled; now three parts

Paul spotted it (2026-10-17) before printing: the one-piece gear-shaft goes
into its bearings from the back, **plug first**, and the T2 plug's 9.65mm
fins can't pass a 608's 8mm bore. My checks only looked at the assembled
unit, not the way in. Paul asked for a twist-lock (¼-turn) at the base of
the shaft. The fix (`cad/dial_unit_housing.scad`, revision 2026-10-17.1;
`docs/housing_decisions.md` has the detail):
- **Shaft:** plug + journal + double-D + tail with two lugs. Everything
  behind the plug is under 8mm (7.85 journal, 7.0 double-D, 5.6 lugs), so it
  goes in **from the door side**, tail first.
- **Gear:** 28T with a double-D bore and the old spacer as its front boss.
  It slides onto the shaft from the back; the double-D carries the torque
  both ways.
- **Twist-lock cap (Paul's idea):** it goes over the lugs and turns ¼; the
  spring presses its two nubs into two notches in the gear's pocket floor.
  It only keeps the shaft from being pulled out forward. A bayonet carries
  torque only in its locking direction, and the dials are driven both ways
  (hardest into the stop when homing), so it doesn't drive.
- **Fit coupon first:** `twist_lock_coupon.stl` (double-D bores drawn 0.2 /
  0.3 / 0.4 over; 0.3 is the default, an ASSUMPTION from the hole
  compensation).
- `dial_layout_check.py` now checks the way in (everything behind the plug
  under the bearing bore), the lugs inside the spring, and the cap in the
  pocket. The spring now sits on the cap: 15.6mm installed, 10.6mm pushed
  back.
- `gear_shafts_5mm/7mm.stl` (#48) are withdrawn: don't print them.

## 2026-10-17 — T2 picked; onto the gear-shaft, 5mm and 7mm

**Result (Paul, 2026-10-17):** of the collar keys, **T2 C8** (collar + 8mm
plug, fins tapering over the last 2mm) fits well; it's the shallowest
taper that still goes all the way in. T1 C8 wouldn't go all the way. T3–T5
also fit. Every C10 (collar + 10mm) bottomed out ~1mm before the collar
seated, so the socket's usable depth from the collar is ~11mm. (The engraved
labels are hard to read: make them bigger next time.)

**Gear-shaft** (`cad/dial_unit_housing.scad`, `dial_gear_shaft()`): the T2
plug, root 2mm below the door face as before, in two lengths Paul will
print (`gear_shafts_5mm.stl` default, `gear_shafts_7mm.stl`), plain PETG.
- **New constraint, found on the way:** the 9.65mm fins can't pass the front
  bearing's 8mm bore, so a plug pushed back stops when its fins reach the
  bearing face (z = 2mm), not at the 7mm spring travel. The fins now start
  1mm in front of the plug root (that 1mm sits in the door's recess; the star
  starts 3.14mm down), so a plug can go back 5mm.
- A misaligned plug only has to go back until its tip rests on the star's
  face. **5mm plug:** 3.86mm needed, 5mm available: OK.
  **7mm plug:** 5.86mm needed, 5mm available. It holds that side of the unit
  ~0.9mm off the door until the seat turn lets it drop in. Paul's test.
- `dial_layout_check.py` now checks that (it used to check the tip came
  flush with the plate at 7mm). `dial_interference_check.py` poses go to
  5mm. SketchUp script updated (tapered plug, fins 1mm forward).

## REOPENED 2026-10-16 — the plug was sized for the wrong part of the socket

**What happened (Paul, 2026-10-16).** On the door, dial A's printed plug
(PETG-CF gear-shaft, the locked 7.73mm / 2.00 / 1.04mm star below) snapped
off inside its socket; the next `home A` turned 1.15 dial turns without
meeting the stop or any load. With the broken head lying in the socket
(photo, 2026-10-16) the star was plainly far smaller than the socket's star.

**New measurements (Paul, calipers, 2026-10-16).**
- The socket's star at its mouth: **10mm tip to tip** across opposite slots.
- The real key's 7.73mm tip section **flares out to ~10mm**, and those outer
  fins are **0.95mm** wide. Paul had assumed the flare never touched the
  star; it does, and it's what engages.
- Where the socket (or the key) narrows from 10mm to 7.73mm: not
  measurable by hand.

**Correction** (to the v0.2 note below): the 12.5mm photo estimate was too
big, but the 7.73mm that replaced it is only the key's TIP section, which
reaches deeper than our plug does. The plug sits 2–7mm below the door face,
in the socket's 10mm section, so its 7.73mm teeth only touched the slots
near their tips. That explains the "rotational play" of every round below
(v0.3, v0.4 and the height sweep). Making the teeth taller deepened the
valleys and shrank the core to 3.38mm, which is probably why it snapped.
The "CLOSED" verdict below is withdrawn.

**Next: taper test keys** (`cad/dial_plug_taper_test.scad` →
`dial_plug_taper_test.stl`, six hand keys, plain PETG). Same 5mm plug at the
same depth as the robot's: 8 fins, 10.0mm tip to tip − 0.35 clearance, fins
0.95mm wide, core 4.94mm (the key's hub) − 0.35, tapering at the plug's end
to the key's 7.73mm (− 0.35) over T = 0, 1, 2, 3, 4, 5mm. Paul snug-tests
each one: does it go all the way in (handle on the door face, else the gap),
and how much play? The winner goes onto the gear-shaft, printed in plain
PETG (Paul, 2026-10-16: the PETG-CF was brittle).

**Depth probes** (Paul's request, 2026-10-16; `cad/print_dial_plug_depth_test.scad`
→ `dial_plug_depth_test.stl`, 12 keys): the same plug at 10mm and 15mm long
(two and three times), the same six end tapers, and no collar, so the
socket stays visible. Each goes in until it bottoms out; insertion depth =
plug length − gap between the hex handle and the door face. For reference,
the real key goes in 15.5mm and the star starts 3.14mm below the door face
(Paul, 2026-10-05).

**Result (Paul, 2026-10-17):** the 10mm probes with a taper fit very well.
Next, **collar keys** (`cad/print_dial_plug_collar_test.scad` →
`dial_plug_collar_test.stl`, 12 keys, T0–T5): the first set's 2mm collar
back on, with a 10mm plug ("C10", 12mm reach from the handle) and with an
8mm plug ("C8", 10mm − the collar: the same 10mm reach as L10).

## CLOSED — tooth geometry locked in: HEIGHT 2.00mm, WIDTH 1.04mm

> **Withdrawn 2026-10-16** (entry above): this geometry fits the key's tip, not the socket's 10mm mouth where the plug sits.

Printed a second height-sweep plate (1.80 / 1.85 / 1.90 / 1.95 /
2.00mm, all at width 1.04mm). All five felt equivalent by hand on the
bench, so going with **2.00mm height / 1.04mm width** — the tightest
of the batch, on the reasoning that a snugger fit means less slop
under repeated motorized engagement, which matters more for wear than
it does for one-off hand testing.

Open concern, not a geometry problem: repeated engagement may wear the
printed teeth over the ~8,000-combination search. Two mitigations,
both deferred to when the final motorized coupler (not this hand-test
key) is built:
- Print the final coupler in a tougher material than plain PETG —
  PETG-CF or nylon.
- The StallGuard-based force-feedback motor control (see
  `control/sequence.md`) backs off at first resistance rather than
  grinding, which should wear the teeth less than hand-forcing did
  during testing.

This closes the tooth-geometry tuning item. `cad/tube_socket_test_key.scad`'s
top-level `tooth_height`/`tooth_width` defaults should be updated to
2.00/1.04 the next time that file is touched.

## v0.4 — width corrected to 1.04mm

Re-measured tooth WIDTH on the real key with calipers: 1.04-1.06mm, not
the 1.0mm used through v0.3. Height stays at 1.75mm (the v0.3 winner).
Printed and labeled "1.75" / "1.04" (two lines) on the bottom of the
handle. Width is still printed at the full measured value with no
clearance subtracted, same as every round so far. Pending: fit report
from the bench. If still loose, 1.06mm (top of the measured range) is
the next step, before touching height again.

## v0.3 — height made a direct parameter, tested 1.65 / 1.70 / 1.75mm

HEIGHT (radial, root→tip) had been DERIVED as
`(tip_dia - root_dia) / 2` from two directly-measured diameters,
giving ~1.4mm. That print clicked the dials but had noticeable
rotational play. Rather than trust the derived value further, height
became a directly-settable parameter, with root_dia computed FROM it.
Tip diameter (7.73mm measured) was deliberately held fixed — it
governs whether the part fits in the socket bore at all, and was
already working — so only the root was adjusted (deepening the valley
between teeth), which can only improve engagement, not risk making the
part too big to insert.

Printed three variants on one plate (1.65 / 1.70 / 1.75mm), each
labeled on the bottom of the handle with its own height value.
**1.75mm won** — most reliable click, least play of the three.

## v0.2 — root cause: photo-derived bore diameter was wrong by ~50-60%

The original socket bore diameter (12.5mm) came from pixel-measuring
the socket in macro photos (ruler-tick calibration, Hough circle fit
on the bore). That print came out geometrically correct relative to
what was modeled (normal ~0.3mm PETG shrink) — the print pipeline was
never the problem. The INPUT was wrong: direct calipers on the real
key read 7.73mm tip-to-tip and 4.94mm hub-to-hub, both ~60% smaller
than the photo estimate. Likely cause: ruler px/mm miscalibration, or
the Hough fit locking onto a chamfer/counterbore ring rather than the
true bore. Replaced all bore-diameter-derived parameters with direct
caliper measurements.

Also fixed in this round:
- Stacking order bug: the registration collar (wider than the bore)
  was ahead of the teeth, so the collar hit the door face before the
  teeth could reach the socket. Fixed to plug → collar → handle.
- Tooth profile: rebuilt as a single closed polygon tracing the whole
  star outline (not a union of per-tooth wedges sharing a center
  point) — the shared vertex was silently corrupting the STL export
  even though the OpenSCAD preview looked correct.
- Handle lengthened to 32mm (from a 9mm robot-coupling stub) so it can
  be gripped and turned by hand for bench testing.

## Measured directly off the real key (calipers), unchanged since v0.2

- 8 teeth, evenly spaced 45° apart
- Tip-to-tip (major) diameter: 7.73mm
- Tooth depth (axial, pre-taper section): 5.0mm
- Collar clearance: door recess measures ~12mm; collar set to 11.75mm

## Fit clearance

`fit_clearance = 0.35mm` (total diametral/radial clearance) has been
unchanged since v0.2 and was never the source of the reported play —
it applies to the tip/root diameters, not to tooth width. Tooth width
has always been printed at the full measured value with zero
clearance subtracted.
