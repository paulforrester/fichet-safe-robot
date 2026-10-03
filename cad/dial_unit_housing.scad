// ============================================================
// Fichet-Bauche "Complice" safe robot — DIAL UNIT housing (v0.1,
// first pass). Holds the 3 dial-socket motors + couplers, mounts to
// the door over the 3 dial holes via neodymium magnets. See
// control/sequence.md's "Mounting" section for the two-unit
// architecture this implements, and docs/bom.md for the parts it's
// built around.
//
// STATUS: first-pass geometry, not yet bench-fit. Two things are
// placeholders pending real measurement (see docs/decisions.md's
// "Housing v0.1" entry for the full readout):
//
//   dial_spacing (36mm) — read directly off a ruler/tape laid against
//   the real holes in docs/photos/dial-holes-ruler-2.jpg and
//   star-opening-tape-2.jpg (an actual printed tape number next to
//   each hole, not pixel-scaled — same category of source as the
//   confirmed tooth geometry, just read by eye off a photo rather
//   than a caliper in hand, so treat it as +/-5mm until confirmed).
//   The 3 holes read as a compact, roughly equilateral triangle, not
//   a straight line — modeled that way here.
//
//   key_hole_offset (55mm) — rough distance from this cluster to
//   socket #4 (the key-turner unit's hole), same photo source. Only
//   used in a comment/echo below for cable-length planning per
//   sequence.md, not part of this part's geometry (the two units
//   mount independently).
//
// REAL FINDING, not a placeholder: 3 full-size NEMA17 motors (42.3mm
// square) physically cannot sit directly behind 3 holes only ~36mm
// apart — the motor bodies collide. This model mounts the 3 motors on
// a larger, safely-spaced ring (same triangle shape, same centroid,
// just bigger) and bridges each motor's shaft to its coupler with a
// PRINTED Oldham coupler (see common_mounts.scad's oldham_* modules)
// rather than a bought part — deliberately chosen over a bought
// bellows/helical flex coupler, since those work by elastically
// FLEXING the material every cycle, which is a fatigue risk in PETG
// over the ~8,000-combination search's tens of thousands of cycles.
// An Oldham coupler is 3 rigid pieces (two slotted hubs + a sliding
// middle disc) — the offset is absorbed by the disc's tongues sliding
// in each hub's slot, not by anything bending, which is a much better
// match for FDM-printed PETG. See docs/housing_decisions.md for the
// full reasoning and the sizing trade-off this creates (the hub ends
// up fairly large relative to the ~36mm hole spacing).
//
// SECOND ROUND of real bench-fit findings (2026-10-03, after a 3D-print
// of the above): (1) the deck standoff legs sat close enough to the
// motors to physically crowd 2 of the 3 — fixed by moving deck_leg_r
// out from 28mm to 46mm (see that variable's comment) and padding
// motor_plate_outline() to match; (2) the real motors have a 22mm x 2mm
// pilot/register boss around the shaft that held them proud of the
// plate and let them tilt under the first mounting screws — fixed with
// a matching recess in motor_plate() (see boss_recess_d/_h,
// common_mounts.scad's nema17_boss_d/_h); (3) electronics_deck()'s Mega
// mounting holes were a guessed symmetric rectangle, and the real Mega
// 2560 hole pattern isn't one — fixed with the real hole coordinates
// (see mega_hole_pts). See docs/housing_decisions.md for the full
// writeup and sourcing on all three.
//
// THIRD ROUND (2026-10-03, same day, after printing the above): the
// front-to-rear joint (plate_corner_pts, now joint_pts) used to sit on
// the SAME ray from center as each motor — fine when it was drawn, but
// the rotated real motor bodies (fixed in the first round, above) reach
// out far enough along that ray to occupy the joint's old position,
// so "there are no standoff holes to attach the dialer base ... the old
// holes were taken." Paul also asked for front_plate() to become a
// plain 150mm-diameter circle rather than sharing motor_plate()'s
// triangular outline. Both addressed together: front_plate_outline()
// is now that circle, and joint_pts moved to a newly-swept position
// (61mm radius, 54deg) clear of every motor/leg/boss on the plate — see
// joint_pts' own comment, below, for the sweep and the margin it found.
//
// Prints as several separate bodies (see the bottom of this file):
// front_assembly() (front plate + 3 standoff legs), rear_assembly()
// (motor plate + 3 taller standoff legs for the deck below), and
// electronics_deck() (Mega/RAMPS mounting plate) — three SEPARATE
// printed parts that bolt together after printing, at 2 different sets
// of 3 leg positions, instead of any of them being fused into the same
// printed object. The two joints use DIFFERENT hardware as of
// 2026-10-03: front-to-rear is still M3 screws into M3 heat-set
// inserts; rear-to-deck switched to M6 self-tapping screws directly
// into the leg (no insert, corrected from an initial M5 draft after
// real bench self-tap testing — see deck_standoff_legs()'s comment)
// — see that module's comment and docs/housing_decisions.md for why. See
// docs/housing_decisions.md v0.3 and v0.4 for why: v0.3 split front
// from rear because fusing them left motor_plate bridging in mid-air
// between 3 thin pillars; v0.4 did the same for the electronics
// mounting after a real print showed the v0.3 electronics_tray (fused
// to motor_plate, only 4mm proud of it) physically colliding with a
// motor can — the housing never modeled the NEMA17's real ~48mm body
// length behind its mounting face, only a token 0.1mm clearance
// pocket. electronics_deck now sits far enough out to clear the real
// can length, on its own standoff legs rather than a one-sided
// cantilevered bridge. Plus 3 identical rotating dial_coupler() shafts
// (each with an integrated Oldham hub on its rear end); 3 identical
// oldham_motor_hub() pieces (motor-side, mounts on the NEMA17 shaft);
// and 3 identical oldham_disc() pieces (the loose sliding middle
// piece) — none of these fuse to any assembly or to each other,
// they're separate parts assembled by hand.
// ============================================================

include <common_mounts.scad>
use <tube_socket_test_key.scad>  // for tooth_profile()/spline_plug() — see below

$fn = 64;

// ---- placeholders pending real measurement — see header ----
dial_spacing     = 36;  // mm, center-to-center, equilateral triangle side
key_hole_offset  = 55;  // mm, dial cluster to socket #4 — informational only, see header

// ---- tooth geometry — CLOSED, mirrored from tube_socket_test_key.scad
// per docs/decisions.md ("tooth geometry locked in: HEIGHT 2.00mm,
// WIDTH 1.04mm"). Can't pull these in via `use` (it only imports
// modules/functions, not top-level variables) without re-executing
// that file's own tool() call, so they're restated here — keep in
// sync with tube_socket_test_key.scad if that file's values change.
tooth_count   = 8;
key_tip_dia   = 7.73;
tooth_height  = 2.00;
tooth_width   = 1.04;
plug_len      = 5.0;
fit_clearance = 0.35;
collar_dia    = 11.75;
collar_len    = 2;

// ---- motor tier + Oldham coupler sizing ----
// (computed before the plate/bushing section below, since the
// bushing bore now has to be sized around the Oldham hub, not just
// the collar)
motor_min_spacing = 48;   // mm, safe center spacing for 42.3mm-body motors (>42.3 + margin)

hole_ring_r  = dial_spacing / sqrt(3);       // circumradius of the real (door) hole triangle
motor_ring_r = motor_min_spacing / sqrt(3);  // circumradius of the fanned-out motor triangle

hole_pts  = ring_points(3, hole_ring_r, 90);
motor_pts = ring_points(3, motor_ring_r, 90);  // same angles -> pure radial (parallel) offset only

// Per-motor rotation (about each motor's own shaft axis, applied to its
// bolt pattern + body-clearance relief only — NOT to motor_pts itself,
// so the shaft stays exactly centered). Originally added because
// deck_leg_r (28mm, at the time) sat almost exactly at the same radius
// as motor_ring_r (27.7mm), just 60deg offset — a REAL bench fit-test
// (2026-10-03, Paul) found the motor can physically fouls a deck
// standoff leg at the default (unrotated) orientation, and that
// rotating each motor clears it while keeping the shaft centered (no
// need to also shift motor_pts). These three values aren't a guess:
// found by brute-force 2D collision search (motor body modeled as the
// real 42.3mm nema17_body square vs. each deck_leg_pts circle AND vs.
// the other two motors' squares, see scratchpad/motor_rotation_sweep.py)
// over all 3 motors' rotations independently, maximizing the worst-case
// clearance. Best found: worst-case clearance -1.17mm
// (motor0-motor1/motor0-motor2, i.e. the motors' own corners, not a
// leg) — still technically negative in this idealized sharp-corner
// model, but Paul's physical PETG-printed test (real NEMA17 cans,
// which have some corner rounding this flat-square model doesn't
// capture) confirms it actually fits. Growing motor_min_spacing to
// fully clear this in the idealized model was considered and rejected:
// it directly grows oldham_offset (already flagged above as "fairly
// large relative to the ~36mm hole spacing"), which would then collide
// the front_plate() coupler bushings with each other instead — trading
// one tight fit for a worse one. Trusting the real bench result over
// the idealized model here.
//
// KEPT UNCHANGED in the 2026-10-03 deck_leg_r rework below (28mm -> 46mm):
// the worst case driving this rotation was always motor-to-motor (the
// line above), not the leg, so moving the leg doesn't retire this fix —
// and Paul's own bench report on this same round of fixes confirms the
// CURRENT rotated motor positions already give perfect shaft-to-dial-hole
// alignment ("if the standoffs were not there, it would be a perfect
// alignment"), so there's no reason to re-derive it now that the leg
// collision it also used to clear is gone.
motor_rotation = [40, 70, 10]; // degrees, indexed with motor_pts

oldham_offset = motor_ring_r - hole_ring_r;  // mm, the parallel misalignment each coupler bridges
oldham_hub_d  = oldham_hub_dia(oldham_offset); // from common_mounts.scad

dial_hub_len  = 6;   // mm, Hub B's own axial length (integrated into dial_coupler(), below)
motor_hub_len = 6;   // mm, Hub A's own axial length (oldham_motor_hub(), below)
oldham_gap    = 2*oldham_tongue_h + oldham_disc_web + 0.4; // mm, hub-face-to-hub-face gap the disc needs

// ---- plate + bushing ----
plate_thickness   = 5;
// Bushing bore has to be wide enough for dial_coupler()'s Hub B end
// (oldham_hub_d, well over the collar's own 11.75mm) to pass all the
// way through during assembly — the collar itself just rides loosely
// inside it, registration against the real socket happens at the
// actual door, not against this bore.
coupler_bore_clear = oldham_hub_d + 2;

// neck: the plain shaft between the collar and Hub B, long enough to
// clear the bushing (plate_thickness) plus a couple mm of margin.
neck_len = plate_thickness + 2;

// rear_standoff derived directly from the drivetrain stack it has to
// contain: neck + Hub B + the disc's gap + Hub A, minus the plate's
// own thickness (rear_standoff is measured from the plate's BACK
// face, and the neck starts counting from the plate's FRONT face).
rear_standoff = (neck_len + dial_hub_len + oldham_gap + motor_hub_len) - plate_thickness;

// ---- front/rear mounting: M3 screws into heat-set inserts ----
// Joins front_assembly()'s standoff legs to rear_assembly()'s motor
// plate — replaces the v0.2 printed pillars/bridge that fused both
// plates into one object with an unsupported span. See
// docs/housing_decisions.md v0.3.
leg_dia           = 12;   // mm, standoff leg / boss diameter (was 10mm
                           // as a plain pillar; a bit more meat now that
                           // it carries a heat-set insert)
insert_hole_d     = 4.2;  // mm, brass M3 heat-set insert OD (typical)
insert_hole_depth = 6;    // mm, blind hole depth in the leg, opens on
                           // the leg's top (mating) face
m3_clear_d        = 3.4;  // mm, M3 clearance hole through the motor plate
m3_head_d         = 6.2;  // mm, socket-cap-head counterbore diameter
m3_head_depth     = 3.2;  // mm, counterbore depth (screw head sits flush)

// ---- rear/deck mounting hardware, 2026-10-03 rework: self-tap, NOT
// M3 + heat-set insert like the front joint above. Paul's call on head
// style — he has both pan and countersunk M5/M6 screws on hand (the
// same assortment boxes `standoff_screw_fit_test.scad` bench-tested)
// and asked for whichever works best. Going with COUNTERSUNK: this
// joint's whole reason for existing right now is to get the 3 motors'
// drive shafts precisely, repeatably centered on their couplers — a
// countersunk screw draws itself (and the plate) into the same
// position every time via the cone seat, with zero radial play once
// seated. Pan head would give a little wiggle room, which is exactly
// what's NOT wanted once the alignment is dialed in; countersunk's
// self-centering action is the better match for "fits exactly, every
// time", including after the joint is taken apart for maintenance.
//
// SIZE IS M6, NOT M5 — corrected after `standoff_screw_fit_test.scad`'s
// real bench results (merged into main as this change was in progress,
// see docs/housing_decisions.md): M5 flat-out didn't self-tap by hand
// at any size tested; M6 at a 5.4mm pilot did, cleanly, reusably, in
// both head styles. Using that real number rather than a generic
// published soft-plastic pilot-hole table (which is what the first
// draft of this used, and got wrong for this material/application).
//
// UNRESOLVED CAVEAT, carried over from that same entry and worse here:
// the 5.4mm pilot was only bench-tested in a thick-walled test cap
// (~6.3mm wall). leg_dia (12mm) around a 5.4mm bore leaves only ~3.3mm
// of real wall here — thinner than anything actually tested. leg_dia
// was deliberately NOT grown to compensate: that would eat into the
// motor-clearance margin from the rotation fix above, which already
// relies on Paul's bench-confirmed fit at this exact 12mm leg diameter.
// Start this self-tap BY HAND, not a power driver, and treat the first
// real leg as a crack-risk check, not a sure thing — see
// docs/housing_decisions.md for the full reasoning and the fallback
// (revert to M3 + heat-set insert here too) if it splits.
m6_selftap_pilot_d = 5.4;  // mm, self-tap pilot into the leg — bench-confirmed size (see above), not a table lookup
m6_selftap_depth   = 12;   // mm, blind hole depth — sized for ~10mm thread
                            // engagement (2x the M6 major diameter, a
                            // generous rule-of-thumb for thread-forming
                            // screws in plastic — no published minimum
                            // engagement length was found to cite here,
                            // so treat this one number as reasoned, not
                            // sourced, and worth a pull-out check on the
                            // bench alongside the crack-risk check above)
                            // plus ~2mm so the screw tip doesn't bottom
                            // out before the countersunk head seats flush.
m6_clear_d    = 6.4;  // mm, M6 clearance through electronics_deck() (same value as standoff_screw_fit_test.scad's m6_clear_d)
m6_csk_top_d  = 14.0; // mm, ISO 10642 M6 countersunk head dk(max) 13.44mm + margin (same sourcing as standoff_screw_fit_test.scad)
m6_csk_depth  = (m6_csk_top_d - m6_clear_d) / 2; // mm, 90-degree countersink cone depth, ~3.8mm

// ---- front_plate() outline: a plain 150mm-diameter CIRCLE, Paul's own
// call (2026-10-03) — see joint_pts' comment just below for the full
// story of why front_plate() stopped sharing motor_plate()'s rounded-
// triangle outline. Decoupled from every other dimension on this plate:
// the old triangular outline was sized (plate_reach, now retired) to
// just cover hole_ring_r + coupler_bore_clear + a magnet ring, which
// only needed ~35.5mm of radius — this circle's 75mm is far more than
// that, all extra room Paul asked for on purpose, not a sizing
// consequence of anything else on the plate.
front_plate_dia = 150; // mm, Paul's requested diameter
front_plate_r   = front_plate_dia / 2;

module front_plate_outline() {
    circle(r = front_plate_r, $fn = 96);
}

// ---- motor_plate() outline: still a rounded triangle-ish blob (NOT a
// circle — only front_plate() changed, above), hull of 3 corner circles
// at joint_pts.
//
// joint_pts carries the front-to-rear M3+heat-set-insert joint
// (front_standoff_legs() grows from front_plate() here; motor_plate()
// gets the matching clearance+counterbore here) — this used to be
// plate_corner_pts, fixed at the same angles as the motors themselves
// (ring_points(3, plate_reach, 90), radius ~51.46mm). A REAL bench
// finding (2026-10-03, Paul, after re-printing with every fix through
// this point): "there are no standoff holes to attach the dialer base
// ... as the motors were shuffled around, the old holes were taken."
// Checked the geometry: plate_corner_pts sat on the SAME ray from
// center as each motor (both at angle 90/210/330), just 23.75mm farther
// out — and each motor's body-clearance square, rotated up to 70deg
// (motor_rotation), reaches well past that distance along at least one
// direction. The old joint was never re-checked against the rotated
// motor positions when that fix landed, because at the time nothing
// else had moved into its way yet.
//
// Paul also asked that front_plate() become the 150mm circle above —
// freeing this joint from needing to double as that plate's own outline
// corners meant it could move to wherever actually clears the motors,
// not just somewhere on the old triangle. Found by the same brute-force
// 2D sweep approach as every other clearance fix in this file
// (scratchpad/joint_pts_sweep.py): swept radius (capped at 61mm, so the
// joint's own 14mm corner-circle pad stays inside front_plate_r's 75mm
// with no bump needed) and start_angle together, maximizing the
// worst-case clearance against all 3 rotated motor-body squares, all 3
// boss recesses, and all 3 deck-leg pads. Best within that radius cap:
// 61mm at 54deg, worst-case clearance +5.5mm (motor0's body) — a
// genuinely comfortable margin, not a bare-minimum one, and clear of
// every motor/leg/boss angle on the plate (all 6 of those already sit
// every 60deg around the ring; 54/174/294 split the difference).
joint_r           = 61;  // mm
joint_start_angle = 54;  // degrees
joint_pts = ring_points(3, joint_r, joint_start_angle);

// pad_deck_legs: adds a small hull-padding circle at each deck_leg_pts
// position (same technique deck_outline() already uses to pad around
// its own posts), so motor_plate()'s own edge grows out to meet a
// standoff leg sitting out near deck_leg_r rather than leaving it
// hanging past the plain 3-corner hull.
// deck_leg_pad_r is sized to put just leg_edge_margin of material
// beyond the leg's own surface, per Paul's "only 1mm from the edge"
// (2026-10-03) — this one feature is deliberately a tight skin, not
// the generous corner padding (14mm) used elsewhere on this outline.
leg_edge_margin = 1; // mm, Paul's requested plate-edge-to-leg-surface margin
deck_leg_pad_r  = leg_dia/2 + leg_edge_margin;

// REGRESSION, caught by Paul on the 54deg/61mm joint_pts fix above
// (2026-10-03): "the motor sled reverted to a triangle that was an
// issue ... one screw if each motor mount goes through the edge of
// the sled." Checked (scratchpad/check_plate_coverage.py) against the
// actual motor_plate_outline() hull (joint_pts corner circles + the
// deck-leg pads, nothing else) and all 12 real (rotated) motor
// bolt-hole positions: for each motor, exactly the bolt hole nearest
// that motor's own 90/210/330deg ray sat at 0.01mm from the edge —
// i.e. on it, matching what Paul saw.
//
// Root cause: the OLD joint (plate_corner_pts, retired above) sat at
// those SAME 90/210/330deg motor angles, just farther out — so its
// corner circles happened to extend the hull exactly in the direction
// each motor's farthest bolt hole needed. Moving the joint to
// 54/174/294deg (to clear the motor bodies, per joint_pts' own
// comment) was correct for THAT collision, but silently removed this
// accidental coverage — a second, separate requirement
// (motor_plate_outline() must contain every motor bolt hole) that
// nothing in the joint_pts sweep had checked.
//
// Fix: pad the hull with a THIRD set of circles, centered on motor_pts
// itself (not the bolt holes, and not tied to motor_rotation's current
// 40/70/10deg values) — rotation-invariant by construction, so a
// future change to motor_rotation can't silently reopen this. Sized
// to fully contain nema17_body_clearance()'s rotated square (the
// widest thing on the motor, already bigger than the bolt square) at
// ANY rotation: a square of half-width `half` reaches `half*sqrt(2)`
// from its own center at its corners, worst case, regardless of
// orientation; +2mm on top is margin, not a fitted number.
// Verified (scratchpad/check_plate_coverage2.py): all 12 bolt holes
// now clear the edge by 11.33mm worst case (was 0.01mm) — re-checked
// that this doesn't reopen the joint-vs-motor-body or
// leg-vs-motor-body collisions the other two fixes above solved for
// (same script, same hull, all three exclusion pairs together).
motor_pad_r = ((nema17_body + 1.5)/2) * sqrt(2) + 2; // mm, ~32.97mm

module motor_plate_outline(r_pad = 0, pad_deck_legs = false) {
    hull() {
        for (p = joint_pts)
            translate(p) circle(r = 14 + r_pad, $fn = 48);
        for (p = motor_pts)
            translate(p) circle(r = motor_pad_r + r_pad, $fn = 48);
        if (pad_deck_legs)
            for (p = deck_leg_pts)
                translate(p) circle(r = deck_leg_pad_r + r_pad, $fn = 32);
    }
}

// ---- rear/deck mounting: second M3 + heat-set-insert tier ----
// electronics_deck() bolts onto motor_plate() the same way
// front_assembly bolts to it (deck_standoff_legs() grows from
// motor_plate; electronics_deck() gets the matching clearance +
// counterbore holes) — see docs/housing_decisions.md v0.4.
//
// Real STEPPERONLINE 55Ncm/2A NEMA17 body length (the "L" dimension,
// motor can only, not the shaft) — this was NEVER modeled before
// (common_mounts.scad's nema17_body_clearance() is a deliberate 0.1mm
// face-clearance pocket, not the real depth), which is why the v0.3
// electronics_tray (only 4mm proud of motor_plate) physically
// collided with a motor can on the actual print.
//
// CONFIRMED 2026-10-03: Paul identified his actual motor's exact part
// number (STEPPERONLINE 17HE19-2004S, bipolar/4-wire, 59Ncm/2A) and
// cross-checked its manufacturer dimensional drawing against his own
// real motor with calipers — a strictly better source than the earlier
// "well-known 17HS19-2004S1" guess this comment used to cite (right
// torque/current class, but not confirmed as the actual part on hand).
// Product page (has the dimensional drawing tab):
// https://www.omc-stepperonline.com/fr/e-serie-nema-17-bipolaire-59ncm-84oz-in-2a-42x48mm-4-fils-avec-1m-de-cable-et-connecteur-17he19-2004s
// The drawing confirms every NEMA17 figure already in
// common_mounts.scad (42.3MAX body, 31±0.2mm bolt spacing, 5mm shaft,
// 4.5mm flat, 15mm flat length, 48MAX body length) plus the 22mm pilot
// boss Paul measured separately (drawing: Ø22 0/-0.05 x 2mm — see
// nema17_boss_d/_h in common_mounts.scad) and a 24±0.5mm shaft
// protrusion (not currently a named constant — checked against the
// drivetrain stack-up below: motor_plate_h (6mm) + motor_hub_len (6mm)
// = 12mm of shaft needed past the mounting face, well inside the real
// 24mm, so no change needed there).
nema17_can_length = 48; // mm, motor body length behind the mounting face
deck_clearance    = 6;  // mm, margin past the can length for connectors/wiring
deck_standoff_h   = nema17_can_length + deck_clearance;

// Offset 60 deg from the motor positions (motor_pts uses start_angle
// 90; this uses 150) so these legs land in the gaps BETWEEN motors —
// motor_plate has no cutouts at all in these 3 directions (the bolt
// patterns and shaft holes sit at the motor_pts angles), confirmed by
// render. (The front-to-rear M3 joint used to sit at these same motor
// angles too, at plate_corner_pts — since moved to joint_pts/54deg
// start angle for an unrelated reason, see that variable's comment.)
//
// deck_leg_r WAS 28mm (same angular slots, closer in) — a REAL bench
// fit-test (2026-10-03, Paul) found that's too close: the leg body
// crowds 2 of the 3 motors badly enough that they can't seat flush or
// have their mounting screws reached at all, and Paul's own read on it
// ("if the standoffs were not there, it would be a perfect alignment")
// pins the leg itself, not the motor positions/rotation, as the actual
// obstruction. Re-checked the leg-vs-motor geometry the same rigorous
// way the motor_rotation fix above was found — brute-force 2D distance
// sweep (scratchpad/deck_leg_sweep2.py) of deck_leg_r against both (a)
// each leg's clearance to the nearest rotated motor body-clearance
// square (42.3+1.5mm, same square motor_plate() already cuts) and (b)
// each leg's clearance to the nearest motor's own bolt-hole center,
// with a 5mm driver-access radius around each hole (generous room for
// a screwdriver/hex-driver bit, not just the bare 3.4mm clearance
// hole). At the old 28mm the body-square margin was already NEGATIVE
// (-1.8mm — i.e. actually overlapping, not just tight), confirming
// Paul's report. 46mm clears both with real margin to spare: worst
// case +4.8mm leg-to-motor-body, +8.8mm leg-to-bolt-hole — chosen over
// the next few mm up specifically to stop at "comfortable", not
// "maximal" (every extra mm out here also grows the plate below, see
// motor_plate_outline()'s pad_deck_legs).
deck_leg_r   = 46;
deck_leg_pts = ring_points(3, deck_leg_r, 150);

// ============================================================
// Rotating part: one dial coupler. Rear end (z=0) is an integrated
// Oldham hub (Hub B) — a slot cut into its rear face, angled 90 deg
// from the matching oldham_motor_hub()'s slot below — then a plain
// neck shaft through the bushing, then the registration collar, then
// the confirmed spline plug (unchanged from tube_socket_test_key.scad)
// at the socket-facing end.
// ============================================================
module dial_coupler() {
    root_dia_local = (key_tip_dia - 2 * tooth_height) - fit_clearance;
    tip_dia_local  = key_tip_dia - fit_clearance;
    eps = 0.1;
    neck_dia = 6; // mm — thicker than the old 5mm shaft-stub idea now
                  // that it's a printed PETG-CF neck under torsion,
                  // not a metal shaft clamped by a bought coupler
    union() {
        // Hub B — this coupler's half of the Oldham joint
        difference() {
            cylinder(d = oldham_hub_d, h = dial_hub_len, $fn = 64);
            translate([0, 0, -eps_c])
                oldham_slot_cut(oldham_offset, angle = 90);
        }
        // neck, through the bushing
        translate([0, 0, dial_hub_len - eps])
            cylinder(d = neck_dia, h = neck_len + eps, $fn = 32);
        // registration collar
        translate([0, 0, dial_hub_len + neck_len - eps])
            cylinder(d = collar_dia, h = collar_len + eps, $fn = 64);
        // spline plug (confirmed geometry, reused verbatim)
        translate([0, 0, dial_hub_len + neck_len + collar_len - eps])
            spline_plug(tip_dia_local, root_dia_local, tooth_count, plug_len + eps, tooth_width);
    }
}

// ============================================================
// Static frame: front plate (bushings + magnets) + motor tier +
// a first-pass electronics tray. No lid yet — see docs/decisions.md.
// ============================================================
module front_plate() {
    difference() {
        linear_extrude(height = plate_thickness)
            front_plate_outline();
        // 3 coupler bushing bores, through the plate
        for (p = hole_pts)
            translate([p[0], p[1], -eps_c])
                cylinder(d = coupler_bore_clear, h = plate_thickness + 2*eps_c, $fn = 64);
        // magnet ring around the outside, on the door-facing (z=0) side
        translate([0, 0, 0])
            magnet_pocket_ring(6, front_plate_r - 6);
    }
}

// Motor plate: a SOLID plate (not 3 separate floating bosses — those
// wouldn't be physically connected to anything), with the 3 NEMA17 bolt patterns
// + body clearance cut into it at the fanned-out motor positions, plus
// a small through-hole per motor for its shaft (just the shaft — Hub A
// mounts on the shaft in the open gap in front of this plate, it
// doesn't need to pass through the plate itself, only the bare shaft
// does).
// Recess for the real motor's pilot/register boss (see
// common_mounts.scad's nema17_boss_d/_h) — Paul's own requested sizing
// (2026-10-03): +1mm on diameter, +0.5mm on depth past the measured
// boss, a non-interference running clearance rather than a tight
// register, so the boss drops fully into the pocket and the motor's
// flat face lands on the plate instead of standing off on the boss.
boss_recess_d = nema17_boss_d + 1;    // mm
boss_recess_h = nema17_boss_h + 0.5;  // mm

module motor_plate(h = 6) {
    translate([0, 0, plate_thickness + rear_standoff]) {
        difference() {
            linear_extrude(height = h)
                motor_plate_outline(pad_deck_legs = true);
            for (i = [0 : 2]) {
                p = motor_pts[i];
                translate([p[0], p[1], 0]) {
                    // Rotated about the motor's own shaft axis only — the
                    // shaft clearance hole below is circular (rotation
                    // doesn't move it) and p itself is untouched, so the
                    // shaft stays exactly centered. See motor_rotation's
                    // definition above for why this rotation exists.
                    rotate([0, 0, motor_rotation[i]]) {
                        nema17_bolt_holes(depth = h + 4);
                        translate([0, 0, -eps_c])
                            nema17_body_clearance(h = 0.1, clearance = 1.5); // face clearance only, not a through-hole
                    }
                    // Boss recess — round, so it doesn't need motor_rotation
                    // (concentric on the shaft either way). Cut from the
                    // OUTER (motor-facing) face only, same shallow-pocket
                    // style as the body clearance above, not a through-hole.
                    translate([0, 0, h - boss_recess_h + eps_c])
                        cylinder(d = boss_recess_d, h = boss_recess_h, $fn = 48);
                    translate([0, 0, -eps_c])
                        cylinder(d = nema17_shaft_d + 2, h = h + 2*eps_c, $fn = 24); // bare shaft clearance
                }
            }
            // M3 mounting holes to front_assembly()'s standoff legs, at
            // the same joint_pts positions the legs use — clearance hole
            // through the full plate + a counterbore on this plate's
            // OUTER face (h-side, away from front_plate) so a socket-cap
            // screw head sits flush. This is the accessible face once
            // assembled (the back of the whole unit), so screws thread
            // in from here toward the legs below.
            for (p = joint_pts)
                translate([p[0], p[1], -eps_c]) {
                    cylinder(d = m3_clear_d, h = h + 2*eps_c, $fn = 24);
                    translate([0, 0, h - m3_head_depth + eps_c])
                        cylinder(d = m3_head_d, h = m3_head_depth + eps_c, $fn = 24);
                }
        }
    }
}

// 3 standoff legs growing straight up from front_plate at joint_pts
// (originally the old (v0.2) support_pillars' corner positions, since
// moved — see joint_pts' comment) — a plate with posts on it is fully
// self-supporting, no bridging involved. Each leg carries a blind bore
// for an M3 heat-set insert, opening on its top (mating) face, so a
// screw driven in from motor_plate()'s outer face can draw the two
// assemblies together. See docs/housing_decisions.md v0.3.
motor_plate_h = 6;
module front_standoff_legs() {
    leg_h = rear_standoff + eps_c; // overlaps into the plate, like the old pillars did
    for (p = joint_pts)
        translate([p[0], p[1], plate_thickness - eps_c])
            difference() {
                cylinder(d = leg_dia, h = leg_h, $fn = 32);
                translate([0, 0, leg_h - insert_hole_depth])
                    cylinder(d = insert_hole_d, h = insert_hole_depth + eps_c, $fn = 24);
            }
}

// 3 standoff legs growing straight up from motor_plate's OUTER (h-side)
// face at deck_leg_pts, tall enough (deck_standoff_h) to clear the
// full NEMA17 can length before electronics_deck() begins — see the
// deck-mounting section above and docs/housing_decisions.md v0.4.
// Same leg_dia/position as before, but the fastening itself changed
// 2026-10-03: M6 self-tap (m6_selftap_pilot_d/_depth) instead of an M3
// heat-set insert — see that section's comment above for why (and the
// untested-thin-wall caveat logged there).
module deck_standoff_legs() {
    leg_h  = deck_standoff_h + eps_c;
    base_z = plate_thickness + rear_standoff + motor_plate_h - eps_c;
    for (p = deck_leg_pts)
        translate([p[0], p[1], base_z])
            difference() {
                cylinder(d = leg_dia, h = leg_h, $fn = 32);
                translate([0, 0, leg_h - m6_selftap_depth])
                    cylinder(d = m6_selftap_pilot_d, h = m6_selftap_depth + eps_c, $fn = 24);
            }
}

// Electronics mounting plate for the Arduino Mega 2560 (101.52 x
// 53.3mm) + RAMPS 1.4 stacked on it — first pass: open deck, no
// walls/lid/cable glands yet. Centered on the motor tier's own axis
// (not offset to one side, unlike the v0.3 electronics_tray this
// replaces) and bolted onto deck_standoff_legs() via M3 screws driven
// in from this plate's outer face, so it's held clear of every motor
// can by deck_standoff_h rather than cantilevered past just one of them.
mega_x = 101.52; mega_y = 53.3; tray_post_h = 8;
deck_thickness = 5;

// Real Arduino Mega 2560 mounting-hole pattern — REPLACES the old
// 4-corner-inset guess (symmetric rectangle, mega_x/mega_y each inset
// 5mm), which this file's own prior comment already flagged as "no
// exact Mega hole pattern yet." Paul's bench fit-test (2026-10-03)
// confirmed that guess was simply wrong: the Mega's 4 real holes are
// NOT a symmetric rectangle at all — this is a known, long-standing
// quirk of the Arduino Uno/Mega board family (the hole nearest the
// power-jack/USB end is set in further than a plain rectangle would
// put it, to clear those connectors), not a sign of a different motor
// or model. Coordinates below are the real Eagle-PCB-file hole centers
// for the Mega board (2560 is pin/hole-compatible with the original
// 1280, confirmed by both sources), independently reported the same
// way by two sources (both ultimately reading the same official Eagle
// board file, not a photo/caliper guess):
//   https://softsolder.com/2010/09/02/arduino-connector-hole-coordinates-mega-1280-board/
//   https://forum.arduino.cc/t/arduino-mega-mounting-hole-dimensions/17099
// Both give, in mil, origin at the board's lower-left corner (by the
// power jack): (600,100) (600,2000) (3550,2000) (3800,100) — hole dia
// 0.125in/3.175mm. Converted to mm and re-centered on the mega_x x
// mega_y footprint's own centroid (same origin convention as every
// other point list in this file):
mega_hole_pts = [
    [-35.52, -24.11],  // near the power-jack/USB end
    [-35.52,  24.15],  // near the power-jack/USB end
    [ 39.41,  24.15],  // near the analog-pin end — NOT aligned with either
    [ 45.76, -24.11]   // of the two holes above: this is the real asymmetry
];

// The Mega's rotation ON the deck is otherwise free (nothing else in
// this file ties it to a particular facing), so it's used here purely
// to dodge a real clearance problem: at rotation 0, mega_hole_pts[2]
// (39.41, 24.15, radius ~46.2mm from center) lands only ~1.2mm from
// deck_leg_pts' 30deg leg (radius 46mm) — close enough that the leg's
// own M6 countersink cut (electronics_deck(), below) undercuts that
// Mega post's base and leaves it floating, disconnected from the deck
// plate (caught by render + trimesh, not by eye — see
// docs/housing_decisions.md). Found by the same brute-force sweep
// approach as elsewhere in this file (scratchpad/mega_rotation_sweep.py):
// swept rotation 0-359deg, maximizing the worst-case (nearest
// hole-to-leg) clearance. 30deg isn't the mathematical best (88deg is,
// at +24.3mm) but it clears comfortably (+20.1mm, around 2x the
// ~10.5mm actually needed) and is a plain, easy-to-reproduce number —
// not chosen for any cable-routing/orientation reason, which hasn't
// been considered yet (open item, see docs/housing_decisions.md).
mega_rotation = 30; // degrees, about the deck's own center (origin)
mega_hole_pts_rot = [for (p = mega_hole_pts)
    [p[0]*cos(mega_rotation) - p[1]*sin(mega_rotation),
     p[0]*sin(mega_rotation) + p[1]*cos(mega_rotation)]];

module deck_outline() {
    hull() {
        // pad around each real (now rotated) Mega mounting-hole position
        for (p = mega_hole_pts_rot)
            translate(p) circle(r = 11, $fn = 32);
        // the 3 leg-mounting positions
        for (p = deck_leg_pts)
            translate(p) circle(r = 14, $fn = 48);
    }
}

module electronics_deck() {
    deck_z = plate_thickness + rear_standoff + motor_plate_h + deck_standoff_h;
    translate([0, 0, deck_z]) {
        difference() {
            linear_extrude(height = deck_thickness)
                deck_outline();
            // M6 mounting holes to deck_standoff_legs() (2026-10-03
            // rework, see that module) — clearance through the plate +
            // a 90-degree COUNTERSINK on the OUTER face (same face as
            // before: the outermost face of the whole assembly once
            // bolted together) so the countersunk screw head seats flush
            // and self-centers the joint every time it's reassembled.
            for (p = deck_leg_pts)
                translate([p[0], p[1], -eps_c]) {
                    cylinder(d = m6_clear_d, h = deck_thickness + 2*eps_c, $fn = 24);
                    translate([0, 0, deck_thickness - m6_csk_depth + eps_c])
                        cylinder(d1 = m6_clear_d, d2 = m6_csk_top_d, h = m6_csk_depth + eps_c, $fn = 48);
                }
        }
        // 4 standoffs for the Mega, at its REAL hole positions
        // (mega_hole_pts_rot, above) — M3 self-tap posts, same pilot
        // sizing as electronics_deck()'s other self-tap posts already used.
        for (p = mega_hole_pts_rot)
            translate([p[0], p[1], deck_thickness - eps_c])
                difference() {
                    cylinder(d = 7, h = tray_post_h, $fn = 24);
                    translate([0, 0, -eps_c]) cylinder(d = 2.6, h = tray_post_h + 2*eps_c, $fn = 16); // M3 self-tap pilot
                }
    }
}

// ---- the three printed assemblies (v0.3/v0.4 — see docs/housing_decisions.md) ----
// Front: door-facing plate + 3 standoff legs. Self-supporting on its
// own — print with front_plate's door-facing face down, as before.
module front_assembly() {
    union() {
        front_plate();
        front_standoff_legs();
    }
}

// Rear: motor plate + 3 taller standoff legs for the electronics deck
// below. Self-supporting on its own (flat plate + posts, same idea as
// front_assembly) — print with motor_plate's mating face (the one
// with the front-to-rear M3 counterbores) down.
module rear_assembly() {
    union() {
        motor_plate(h = motor_plate_h);
        deck_standoff_legs();
    }
}

// ---- output: all three assemblies + 3 sets of loose drivetrain parts,
// laid out side by side so nothing overlaps. Each top-level call below
// is its own disconnected body in the exported STL — use Bambu
// Studio's "Split to Objects" to separate them for slicing/orientation,
// same as the v0.2 file already relied on for the drivetrain parts.
// Largest outer extent of EITHER printed plate from its own center:
// front_plate_outline() is now just its own radius (a plain circle,
// joint_pts' legs sit well inside it by construction — see that
// variable's comment); motor_plate_outline() is the farthest of its
// corner joints (joint_r+14), its deck-leg pads
// (deck_leg_r+deck_leg_pad_r, ~53mm), or its motor pads
// (motor_ring_r+motor_pad_r, ~60.7mm, added with the motor_pad_r fix
// above — still smaller than joint_r+14 today, but included so this
// can't quietly go stale if motor_ring_r or motor_pad_r change).
// front_plate_r and joint_r+14 come out equal (75mm) by construction
// (joint_r was capped there on purpose), so this works out to 75mm
// today, but it's left as a real max() rather than a restated number
// so it can't quietly go stale if any of these change.
bound_r = max(front_plate_r, joint_r + 14, deck_leg_r + deck_leg_pad_r, motor_ring_r + motor_pad_r);
// deck_outline()'s outer extent from its own center — real Mega hole
// positions (mega_hole_pts) are no longer a tidy symmetric inset, so this
// takes the actual farthest point among both feature sets rather than a
// mega_x/mega_y formula.
deck_bound_r = max(
    max([for (p = mega_hole_pts_rot) norm(p)]) + 11,
    deck_leg_r + 14
);

// front_assembly() sits at the origin (native position).
front_assembly();

// rear_assembly(), shifted clear of front_assembly along +X.
assembly_gap = 2 * bound_r + 30; // clear separation between the two outlines, plus margin
translate([assembly_gap, 0, 0])
    rear_assembly();

// electronics_deck(), shifted clear of rear_assembly along +X.
deck_gap = assembly_gap + bound_r + deck_bound_r + 30;
translate([deck_gap, 0, 0])
    electronics_deck();

// loose drivetrain parts, shifted clear of all three.
layout_x = deck_gap + deck_bound_r + 30;
for (i = [0 : 2]) {
    translate([layout_x, i * 30 - 30, 0])
        dial_coupler();
    translate([layout_x + oldham_hub_d + 15, i * 30 - 30, 0])
        oldham_motor_hub(oldham_offset, len = motor_hub_len, slot_angle = 0);
    translate([layout_x + 2*(oldham_hub_d + 15), i * 30 - 30, 0])
        oldham_disc(oldham_offset);
}

// ============================================================
// PRINT NOTES:
//  - front_assembly() + rear_assembly() + electronics_deck(): PETG is
//    fine (structural, not wear-facing). Print as three SEPARATE parts
//    (split to objects, see above) — each is self-supporting in its
//    natural orientation: front_assembly face-down on its door-facing
//    face (as v0.2 was), rear_assembly face-down on motor_plate's
//    mating (front-to-rear-counterbored) face, electronics_deck
//    face-down on its mating (deck-leg-counterbored) face. None should
//    need support material for the plate/leg/deck geometry itself. See
//    docs/housing_decisions.md v0.3 for why front/rear were split
//    (fusing them left motor_plate bridging unsupported between 3 thin
//    pillars) and v0.4 for why the electronics mounting got the same
//    treatment (the v0.3 electronics_tray, cantilevered only 4mm past
//    motor_plate, physically collided with a motor can on the real
//    print — the housing never modeled the NEMA17's real ~48mm body
//    length there).
//  - Hardware to join them — TWO DIFFERENT joints as of 2026-10-03:
//    * front-to-rear (front_standoff_legs()): 3x M3 brass heat-set
//      threaded inserts (4.2mm OD, ~5mm length, in insert_hole_depth's
//      6mm blind bore) + 3x M3x8 DIN 912 / ISO 4762 socket-head cap
//      screws, machine-thread (not self-tapping — threads into the
//      brass insert). Press the inserts in with a soldering iron after
//      printing, before final assembly. LENGTH MATTERS: a too-long
//      screw bottoms on the leg's solid floor *before* its head seats
//      in the counterbore, leaving the joint proud and not actually
//      clamped. Max before that happens: ~8.8mm (motor_plate is 6mm
//      thick, minus the 3.2mm counterbore, plus the 6mm leg bore =
//      2.8+6). M3x8 clears this with a standard ~5mm insert.
//    * rear-to-deck (deck_standoff_legs()): no insert — 3x M6 screws
//      self-tapping directly into m6_selftap_pilot_d (5.4mm — Paul's own
//      bench-confirmed size, see docs/housing_decisions.md, NOT a
//      generic table value). Head style is COUNTERSUNK (see
//      deck_standoff_legs()/electronics_deck() comments for why —
//      self-centering > pan head's wiggle room, for a joint whose whole
//      job is repeatable shaft alignment). Length: deck_thickness (5mm)
//      + ~10mm thread engagement = ~15mm works without bottoming
//      (m6_selftap_depth's 12mm pilot leaves ~2mm spare below a
//      10mm-engaged screw); anywhere from M6x13 to M6x16 is fine — pick
//      whichever's in Paul's on-hand assortment box closest to 15mm.
//      UNTESTED AT THIS WALL THICKNESS (~3.3mm around the 5.4mm bore in
//      the 12mm leg — the bench test that validated 5.4mm used a much
//      thicker-walled cap, see docs/housing_decisions.md): thread the
//      FIRST one in BY HAND, not a power driver, and check for cracking
//      before trusting the rest. If it splits, fall back to M3 +
//      heat-set insert here too rather than growing leg_dia (which
//      would eat into the motor-clearance margin above).
//  - Build order matters for electronics_deck: bolt it onto
//    deck_standoff_legs() BEFORE mounting the Arduino Mega on its own
//    4 corner posts — 2 of the 3 deck-to-leg screws land under the
//    Mega's footprint once it's installed (same accessible-outer-face
//    logic as the front-to-rear screws, just one Mega-sized board now
//    sitting on top of them). If those screws ever need to come out
//    again, remove the Mega (its own 4 screws) first.
//  - Couplers + Oldham hubs (dial_coupler, oldham_motor_hub): print in
//    PETG-CF per docs/decisions.md's wear-mitigation decision (Bambu
//    Lab order already covers this filament + the tungsten-carbide
//    hotend it needs) — these see the same repeated-engagement wear as
//    the final motorized key coupler, now with sliding Oldham contact
//    surfaces added on top of the spline engagement.
//  - Oldham discs: plain PETG is fine here — thin sliding tongues, not
//    the wear-critical interface (that's the slot walls on the hubs,
//    which see PETG-CF). A light coat of PTFE or silicone grease on
//    the tongues before assembly will help.
//  - No longer needed: the off-the-shelf flexible shaft coupler this
//    file used to call for — replaced by the printed Oldham joint
//    above. docs/bom.md's follow-up item for it should come off.
//  - Motor orientation (motor_rotation, near the top of this file):
//    each motor's bolt pattern + body relief is rotated about its own
//    shaft axis (40/70/10 degrees) — originally to clear both
//    deck_standoff_legs() AND its two neighboring motors, now (after
//    deck_leg_r moved out to 46mm, see below) only the neighboring
//    motors are the tight constraint. See that variable's comment for
//    the full reasoning and how the numbers were found — the
//    motor-to-motor worst case is only -1.17mm in the idealized sharp-
//    corner model, i.e. this is a tight fit by design there, not one
//    with comfortable margin to spare, even though the leg clearance
//    itself is comfortable now. Paul's own bench report on this round
//    of fixes confirms the rotated positions are correct (perfect
//    shaft-to-dial-hole alignment); no need to re-run this search.
//  - Round 2 bench-fit fixes (2026-10-03, this revision): deck_leg_r
//    28mm -> 46mm (standoffs were crowding 2 of 3 motors — now +4.8mm
//    worst-case clearance to the nearest motor body, +8.8mm to the
//    nearest bolt hole, see deck_leg_r's comment); a 23mm x 2.5mm
//    recess added to motor_plate() for the real motor's pilot boss
//    (22mm x 2mm, measured) so motors seat flush instead of standing
//    off and tilting under the first screws; electronics_deck()'s Mega
//    mounting holes moved to the real (non-rectangular) Mega 2560
//    pattern (mega_hole_pts) instead of a guessed symmetric inset.
//    Re-render + re-check fit on all three before trusting this is the
//    last pass — same iterate-on-clearance approach as every other fix
//    in this file.
//  - Bottom-plate mounting: front_plate()'s magnet ring
//    (magnet_pocket_ring) is sized for the LIGHT front_assembly alone,
//    not for the full assembled weight of 3 motors + electronics_deck
//    hanging off it from inside the safe door. Paul flagged
//    (2026-10-03) that the magnets alone likely can't hold that much
//    weight — probably needs magnets PLUS some kind of arm/bracket that
//    transfers load to the top of the safe. NOT designed yet — this is
//    an open TODO, not solved by this revision. See
//    docs/housing_decisions.md.
//  - Bench-fit TODO before trusting dial_spacing: confirm the 36mm
//    triangle with calipers directly on the door (see header). Also
//    test-fit the Oldham disc in its hubs, and the leg/insert/screw
//    fit joining the two assemblies, before committing to a full
//    print — same iterate-on-clearance approach already used for the
//    spline key (docs/decisions.md).
// ============================================================
