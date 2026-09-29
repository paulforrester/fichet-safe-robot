// ============================================================
// Fichet-Bauche "Complice" safe robot — KEY-TURNER UNIT housing
// (v0.1, first pass). One motor + a gripper that clamps the real
// key's protruding bow (already hand-inserted into socket #4 before
// this unit goes on) — see control/sequence.md's "Mounting" section.
//
// STATUS: first-pass geometry. Key bow dimensions are still an open
// item in control/sequence.md ("Key bow dimensions ... needed to
// design the key-turner's gripper") — docs/photos/real-key-bow-closeup.jpg
// shows the bow is an ornate 4-lobed/cross shape, not a simple
// rectangle, and has no ruler/tape in frame, so there's no legible
// direct measurement to use (unlike the dial-hole spacing — see
// dial_unit_housing.scad). Rather than guess a tight-fit pocket
// around a shape that isn't actually measured, this uses an
// adjustable clamp: a generous open slot the bow slides into (after
// the key is already seated by hand) plus a thumbscrew-tightened bar
// that closes the slot and clamps whatever thickness/width the real
// bow turns out to be, within the slot's working range. That also
// sidesteps needing an exact ornate-shape pocket at all — a clamp
// doesn't care about the bow's decorative outline, only its
// thickness and the width of the section being gripped.
//
// No motor-offset problem here — it's a single motor, so it mounts
// directly behind the gripper hub, coaxially, no flex coupler needed.
// ============================================================

include <common_mounts.scad>

$fn = 64;

// ---- gripper — generous placeholder dims, see header ----
hub_dia         = 34;   // mm, gripper hub diameter
hub_thickness   = 8;    // mm
slot_width_max  = 9;    // mm, clamp fully open — generous vs. a typical
                          // ornate key bow's a few-mm thickness
slot_depth      = 20;   // mm, how far the slot reaches toward the hub center
                          // (captures bows roughly up to ~2*slot_depth across)
clamp_screw_d   = 3.4;  // M3 clearance, for the clamp bolt

// ---- motor mount + shaft ----
shaft_len       = 10;   // mm, hub's D-bore depth onto the motor shaft
plate_thickness = 5;
plate_dia       = 56;

// ============================================================
// Rotating part: hub + open slot + two clamp-bar mounting ears.
// Motor's D-shaft inserts directly into the hub (no flex coupler —
// single motor, no offset to bridge).
// ============================================================
module gripper_hub() {
    ear_r = hub_dia/2 + 6;
    difference() {
        union() {
            cylinder(d = hub_dia, h = hub_thickness);
            // two ears either side of the slot opening, to bolt the clamp bar across
            for (s = [-1, 1])
                translate([s * (slot_width_max/2 + 4), hub_dia/2 - 2, 0])
                    cylinder(d = 8, h = hub_thickness);
        }
        // the open slot itself — cut in from the rim toward the center
        translate([-slot_width_max/2, hub_dia/2 - slot_depth, -eps_c])
            cube([slot_width_max, slot_depth + 6, hub_thickness + 2*eps_c]);
        // D-shaft bore for the motor, from the underside
        translate([0, 0, -eps_c])
            dshaft_bore(bore_len = shaft_len, screw_z = shaft_len - 3);
        // clamp bolt holes through both ears
        for (s = [-1, 1])
            translate([s * (slot_width_max/2 + 4), hub_dia/2 - 2, -eps_c])
                cylinder(d = clamp_screw_d, h = hub_thickness + 2*eps_c, $fn = 24);
    }
}

// Clamp bar: a separate small printed part. One M3 bolt + nut (or a
// captive nut in the far ear) draws it down across the slot opening
// once the bow is in place, taking up whatever thickness the real bow
// turns out to be within slot_width_max.
module clamp_bar() {
    bar_len = (slot_width_max/2 + 4) * 2 + 8;
    difference() {
        translate([-bar_len/2, -4, 0])
            cube([bar_len, 8, 5]);
        for (s = [-1, 1])
            translate([s * (slot_width_max/2 + 4), 0, -eps_c])
                cylinder(d = clamp_screw_d, h = 5 + 2*eps_c, $fn = 24);
    }
}

// ============================================================
// Static frame: mounting plate (magnets) + NEMA17 boss, directly
// behind the gripper hub — no offset needed for a single motor.
// ============================================================
module frame() {
    difference() {
        union() {
            cylinder(d = plate_dia, h = plate_thickness, $fn = 64);
            translate([0, 0, plate_thickness - eps_c])
                cylinder(d = nema17_bolt_square + 10, h = 6, $fn = 64);
        }
        magnet_pocket_ring(3, plate_dia/2 - 6);
        translate([0, 0, plate_thickness])
            nema17_bolt_holes(depth = 12);
    }
}
// Note: the gripper hub is a separate printed part (below), not
// touching this frame — the real running clearance between hub and
// plate comes from a washer/spacer at assembly, not from geometry
// here. An earlier version cut a shallow clearance notch for this
// directly into the plate; it was purely cosmetic (a fraction of a
// mm) and produced a degenerate coplanar sliver in the exported STL,
// so it was dropped rather than fought.

// ---- output: static frame, gripper hub, and clamp bar as 3 loose parts ----
frame();
translate([80, 0, 0]) gripper_hub();
translate([80, 40, 2.5]) clamp_bar();

// ============================================================
// PRINT NOTES:
//  - Frame: PETG, same as the dial unit frame — structural, not
//    wear-facing.
//  - Gripper hub + clamp bar: also fine in plain PETG (low duty cycle,
//    hand-tightened once per session, unlike the dial couplers' ~8,000
//    repeated engagements) — no need for the PETG-CF used on the dial
//    couplers here.
//  - Bench-fit TODO: once the unit's built, measure the real bow's
//    thickness and the width of the section you want to grip, and
//    confirm both fit inside slot_width_max (9mm) / slot_depth (20mm)
//    — resize and reprint the hub if not. This is a cheap, fast
//    reprint since it's a small standalone part.
// ============================================================
