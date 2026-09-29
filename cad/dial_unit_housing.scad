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
// short off-the-shelf flexible shaft coupler (5mm-5mm, NOT printed —
// not yet on docs/bom.md, added as a follow-up item). The needed
// offset is a few mm of pure PARALLEL shaft misalignment (not
// angular), which is exactly what an Oldham-style flex coupler is
// designed for — cheap and common, e.g. widely sold for 3D-printer
// Z-axis motor-to-leadscrew couplings.
//
// Prints as several separate bodies on one plate (see the bottom of
// this file): the static frame (plate + motor mounts + electronics
// tray) as one part, and 3 identical rotating dial_coupler() shafts
// as separate parts (they rotate inside the frame, so must not be
// fused to it).
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

// ---- plate + bushing ----
plate_thickness   = 5;
coupler_bore_clear = collar_dia + 1.2;   // clearance dia so the coupler spins freely
bushing_shaft_clear = nema17_shaft_d + 0.4; // the coupler's own rear shaft stub rides here

// ---- motor tier ----
motor_min_spacing = 48;   // mm, safe center spacing for 42.3mm-body motors (>42.3 + margin)
rear_standoff     = 42;   // mm, plate back face to motor mounting face — fits the coupler's
                           // rear shaft stub + an off-the-shelf ~25mm flex coupler + a few mm slack

hole_ring_r  = dial_spacing / sqrt(3);       // circumradius of the real (door) hole triangle
motor_ring_r = motor_min_spacing / sqrt(3);  // circumradius of the fanned-out motor triangle

hole_pts  = ring_points(3, hole_ring_r, 90);
motor_pts = ring_points(3, motor_ring_r, 90);  // same angles -> pure radial (parallel) offset only

// ---- plate outline: rounded triangle-ish blob big enough for the
// hole cluster + bushings + a magnet ring, via hull of 3 corner circles
plate_reach = hole_ring_r + coupler_bore_clear/2 + 16; // outer radius the plate must cover
plate_corner_pts = ring_points(3, plate_reach, 90);

module plate_outline(r_pad = 0) {
    hull() {
        for (p = plate_corner_pts)
            translate(p) circle(r = 14 + r_pad, $fn = 48);
    }
}

// ============================================================
// Rotating part: one dial coupler. Motor-side end is a plain round
// shaft stub sized for an off-the-shelf 5mm flex coupler (NOT the
// D-bore — that stays on the motor's own shaft, on the coupler side
// the flex coupler just clamps a round shaft same as it clamps the
// motor's); socket-side end is the confirmed spline plug, unchanged
// from tube_socket_test_key.scad.
// ============================================================
module dial_coupler(rear_shaft_len = 14) {
    root_dia_local = (key_tip_dia - 2 * tooth_height) - fit_clearance;
    tip_dia_local  = key_tip_dia - fit_clearance;
    eps = 0.1;
    union() {
        // rear shaft stub (into the flex coupler)
        cylinder(d = nema17_shaft_d, h = rear_shaft_len, $fn = 32);
        // registration collar
        translate([0, 0, rear_shaft_len - eps])
            cylinder(d = collar_dia, h = collar_len + eps, $fn = 64);
        // spline plug (confirmed geometry, reused verbatim)
        translate([0, 0, rear_shaft_len + collar_len - eps])
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
            plate_outline();
        // 3 coupler bushing bores, through the plate
        for (p = hole_pts)
            translate([p[0], p[1], -eps_c])
                cylinder(d = coupler_bore_clear, h = plate_thickness + 2*eps_c, $fn = 64);
        // magnet ring around the outside, on the door-facing (z=0) side
        translate([0, 0, 0])
            magnet_pocket_ring(6, plate_reach - 6);
    }
}

// Motor plate: a SOLID plate using the same outline/footprint as
// front_plate() (not 3 separate floating bosses — those wouldn't be
// physically connected to anything), with the 3 NEMA17 bolt patterns
// + body clearance cut into it at the fanned-out motor positions.
module motor_plate(h = 6) {
    translate([0, 0, plate_thickness + rear_standoff]) {
        difference() {
            linear_extrude(height = h)
                plate_outline();
            for (p = motor_pts)
                translate([p[0], p[1], 0]) {
                    nema17_bolt_holes(depth = h + 4);
                    translate([0, 0, -eps_c])
                        nema17_body_clearance(h = 0.1, clearance = 1.5); // face clearance only, not a through-hole
                }
            // clearance so each dial_coupler's rear shaft stub + flex
            // coupler has room to pass through on its way to the motor
            for (p = hole_pts)
                translate([p[0], p[1], -eps_c])
                    cylinder(d = coupler_bore_clear, h = h + 2*eps_c, $fn = 64);
        }
    }
}

// 3 solid pillars connecting front_plate to motor_plate across
// rear_standoff — without these the two plates are just floating in
// space relative to each other. Placed at the same outer positions
// used to build both plates' outline (plate_corner_pts), so they land
// solidly inside both hulls, clear of the coupler bores in the middle.
motor_plate_h = 6;
module support_pillars() {
    for (p = plate_corner_pts)
        translate([p[0], p[1], plate_thickness - eps_c])
            cylinder(d = 10, h = rear_standoff + 2*eps_c, $fn = 32);
}

// 4 standoff posts + a floor for the Arduino Mega 2560 (101.52 x
// 53.3mm) + RAMPS 1.4 stacked on it — first pass: open tray, no
// walls/lid/cable glands yet. Positioned off to one side of the motor
// plate so it doesn't collide with the fanned-out motors, and bridged
// to the motor plate by bridge_arm() below so it's not left floating.
mega_x = 101.52; mega_y = 53.3; tray_post_h = 8;
tray_z = plate_thickness + rear_standoff + motor_plate_h + 4;
tray_x_offset = motor_ring_r + mega_x/2 + 20;

module electronics_tray() {
    translate([tray_x_offset, 0, tray_z]) {
        // floor
        translate([-mega_x/2 - 4, -mega_y/2 - 4, 0])
            cube([mega_x + 8, mega_y + 8, 3]);
        // 4 corner standoffs, generic M3 self-tap posts (no exact Mega
        // hole pattern yet — see docs/decisions.md TODO)
        for (x = [-1, 1]) for (y = [-1, 1])
            translate([x * (mega_x/2 - 5), y * (mega_y/2 - 5), 3])
                difference() {
                    cylinder(d = 7, h = tray_post_h, $fn = 24);
                    translate([0, 0, -eps_c]) cylinder(d = 2.6, h = tray_post_h + 2*eps_c, $fn = 16); // M3 self-tap pilot
                }
    }
}

// Solid gusset from the motor plate's edge up and across to the tray
// floor's near edge — generously overlaps both so the tray isn't a
// separate floating body. Not pretty, but this is a first pass; a
// cleaner integrated bracket is a follow-up.
module bridge_arm() {
    x0 = plate_reach * 0.5;
    x1 = tray_x_offset - mega_x/2 - 4 + 8; // overlaps into the tray floor
    translate([x0, -12, plate_thickness + rear_standoff])
        cube([max(x1 - x0, 10), 24, motor_plate_h + 10]);
}

module frame() {
    union() {
        front_plate();
        support_pillars();
        motor_plate(h = motor_plate_h);
        bridge_arm();
        electronics_tray();
    }
}

// ---- output: static frame + 3 loose coupler shafts laid out beside it ----
frame();

for (i = [0 : 2])
    translate([plate_reach * 2.6, i * 30 - 30, 0])
        dial_coupler();

// ============================================================
// PRINT NOTES:
//  - Frame: PETG is fine (structural, not wear-facing). Print with
//    the front plate face-down for a clean door-facing surface.
//  - Couplers: print in PETG-CF per docs/decisions.md's wear-mitigation
//    decision (Bambu Lab order already covers this filament + the
//    tungsten-carbide hotend it needs) — same reasoning as the final
//    motorized key coupler, these see the same repeated-engagement wear.
//  - Needed but not yet on docs/bom.md: 3x off-the-shelf 5mm-5mm
//    flexible shaft coupler (Oldham or jaw type, ~25mm long) to bridge
//    each motor to its dial_coupler(). Flag for a follow-up order.
//  - Bench-fit TODO before trusting dial_spacing: confirm the 36mm
//    triangle with calipers directly on the door (see header).
// ============================================================
