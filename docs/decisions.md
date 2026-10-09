# Tube-socket test key — dimensional decision log

> **Revision 2026-10-09.1** · project revision baseline (mechanical log; not affected by the wiring changes) · log: `./revisions.md`


Working notes on how the test key's dimensions were arrived at, most
recent first. Terminology (WIDTH / HEIGHT / DEPTH) is defined in
`tooth_terms_diagram.png` in this folder.

## CLOSED — tooth geometry locked in: HEIGHT 2.00mm, WIDTH 1.04mm

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
