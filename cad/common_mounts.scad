// ============================================================
// Shared mounting geometry for the housing parts
// (dial_unit_housing.scad, key_turner_housing.scad) — pulled into
// its own file so both use the exact same NEMA17 bolt pattern,
// magnet-pocket geometry, and D-shaft coupler bore rather than
// risking two slightly different copies drifting apart.
//
// `use`d, not `include`d, by the housing files: this file has no
// bottom-line geometry of its own, only modules/functions, so `use`
// is enough and avoids re-executing anything.
// ============================================================

eps_c = 0.1; // generic small overlap, same role as `eps` in tube_socket_test_key.scad

// ---- NEMA17 — dimensions below were generic/standard-part figures
// until 2026-10-03, when Paul identified his actual motor's exact part
// (STEPPERONLINE 17HE19-2004S, bipolar/4-wire, 59Ncm/2A) and
// cross-checked its manufacturer dimensional drawing against the real
// motor with calipers — "lines up." Product page (dimensional drawing
// under its "Dimensions" tab):
// https://www.omc-stepperonline.com/fr/e-serie-nema-17-bipolaire-59ncm-84oz-in-2a-42x48mm-4-fils-avec-1m-de-cable-et-connecteur-17he19-2004s
// Every figure below is now a confirmed match to that drawing, not just
// a generic NEMA17 assumption (NEMA17 is a standardized footprint
// across vendors regardless, but it's better to know this one's
// actually on spec than to rely on that alone):
nema17_body        = 42.3;  // mm, square motor face — drawing: 42.3MAX
nema17_bolt_square = 31;    // mm, bolt-hole center spacing — drawing: 31+/-0.2mm
                             // (was 31.04, a generic "typical" figure;
                             // tightened to the drawing's own nominal,
                             // still well inside its tolerance band)
nema17_bolt_clear  = 3.4;   // mm, M3 clearance hole — drawing calls the
                             // motor's own holes "4-M3 DEPTH 4.5MIN"
                             // (tapped into the can, not a clearance
                             // hole — 3.4mm is this file's own M3
                             // clearance choice for the printed plate)
nema17_shaft_d     = 5.0;   // mm, shaft diameter — drawing: dia5 0/-0.012
nema17_shaft_flat  = 4.5;   // mm, across-the-flat dimension (D-shaft) — drawing: 4.5+/-0.1
nema17_flat_len    = 15;    // mm, length of the flat back from the shaft tip — drawing: 15+/-0.25

// Pilot/register boss: a shallow round step raised around the shaft on
// the motor's mounting face — NOT in any of the generic NEMA17 numbers
// above, and nema17_body_clearance() below only relieves the square can
// outline (a flat 0.1mm face-touch pocket), so it does nothing for this
// round boss. Real finding (bench fit test, 2026-10-03, Paul): the boss
// holds the motor's face proud of the plate by its own height, so the 4
// mounting screws draw down unevenly and tip the motor off-perpendicular
// before it seats. Originally MEASURED directly off the real part (no
// vendor drawing was found for it at the time); now doubly confirmed —
// the dimensional drawing cited above shows the same boss at dia22
// 0/-0.05 x 2mm, matching Paul's caliper reading exactly:
nema17_boss_d = 22;  // mm, measured + drawing-confirmed
nema17_boss_h = 2;   // mm, measured + drawing-confirmed

// 4-hole M3 bolt pattern, centered on the origin, in the XY plane.
module nema17_bolt_holes(depth = 20) {
    for (x = [-1, 1]) for (y = [-1, 1])
        translate([x * nema17_bolt_square/2, y * nema17_bolt_square/2, -eps_c])
            cylinder(d = nema17_bolt_clear, h = depth + 2*eps_c, $fn = 24);
}

// Oversize square clearance for the motor can — a printed bracket
// only needs to touch the mounting face, not hug the body — so this
// is deliberately a bit bigger than the real 42.3mm can, not a fitted
// pocket.
module nema17_body_clearance(h = 30, clearance = 1.5) {
    translate([0, 0, -eps_c])
        cube([nema17_body + clearance, nema17_body + clearance, h + eps_c], center = true);
}

// ---- magnet mounting pocket ----
// 8.00mm dia x 1.9mm depth, interference press-fit for the 2mm x 8mm
// neodymium discs already on hand (see docs/decisions.md's Mounting
// section — this is the exact geometry worked out there, reused
// as-is, not re-derived).
magnet_pocket_d     = 8.00;
magnet_pocket_depth = 1.9;

module magnet_pocket() {
    cylinder(d = magnet_pocket_d, h = magnet_pocket_depth + eps_c, $fn = 48);
}

// Places `n` magnet pockets evenly around a circle of radius r in the
// XY plane, pockets cut going in -Z (call inside a translate/rotate to
// aim them at whichever face is the door-facing one).
module magnet_pocket_ring(n, r, start_angle = 90) {
    for (i = [0 : n - 1])
        rotate([0, 0, start_angle + i * 360/n])
            translate([r, 0, -eps_c])
                magnet_pocket();
}

// ---- rubber-coated pot magnet mount (both units, 2026-10-06) ----
// Wukong 22mm rubber-coated neodymium magnets, M4 threaded hole in the back,
// listed 6mm tall (Amazon.fr B0DGQ52DY9 / B0D5B4TJ7B; no pull rating listed —
// test one on the door). CONFIRM rmag_d / rmag_h / thread depth with calipers
// when they arrive; everything below follows from these numbers.
//
// The magnet drops into a THROUGH hole (no floor printed over air -> no
// strings). On the plate's inner face a ring stands up around the hole; a
// flat printed retainer disc sits on the ring and the magnet's own M4 screw
// goes through it into the magnet. The ring's top sets the magnet's depth,
// so the rubber stands rmag_proud past the door face on every magnet, and
// the door's pull goes retainer -> ring, not into a press fit.
rmag_d        = 22;      // listed 22; MEASURED 21.5 (Paul, 2026-10-07): rmag_hole_d to be set from cad/magnet_fit_test.stl
rmag_h        = 6;
rmag_proud    = 0.2;     // rubber face past the plate's door face
rmag_hole_d   = rmag_d + 0.4;
rmag_ring_od  = 29;
rmag_ret_d    = 27;      // retainer bears on the ring from 22.4 to 27
rmag_ret_t    = 3;
rmag_screw_d  = 4.5;     // M4 clearance
rmag_seat_z   = rmag_h - rmag_proud;   // 5.8: ring top / magnet back, from the door face

// holes, cut from z = 0 (door face) up through a plate of thickness t
module rmag_holes(pts, t) {
    for (p = pts) translate([p[0], p[1], -eps_c]) cylinder(d = rmag_hole_d, h = max(t, rmag_seat_z) + 2*eps_c, $fn = 96);
}
// seat rings on the plate's inner face (plate top at z = t)
module rmag_rings(pts, t) {
    assert(t <= rmag_seat_z, "plate thicker than the magnet seat: magnet would sit too deep");
    for (p = pts) translate([p[0], p[1], t - eps_c]) difference() {
        cylinder(d = rmag_ring_od, h = rmag_seat_z - t + eps_c, $fn = 96);
        translate([0, 0, -eps_c]) cylinder(d = rmag_hole_d, h = rmag_seat_z - t + 3*eps_c, $fn = 96);
    }
}
// the retainer disc (print flat, any quantity)
module rmag_retainer() {
    difference() {
        cylinder(d = rmag_ret_d, h = rmag_ret_t, $fn = 96);
        translate([0, 0, -eps_c]) cylinder(d = rmag_screw_d, h = rmag_ret_t + 2*eps_c, $fn = 32);
    }
}
// assembled dummies for the 3D checks: magnet (rubber face rmag_proud below z = 0) + retainer
module rmag_dummies(pts) {
    for (p = pts) translate([p[0], p[1], 0]) {
        translate([0, 0, -rmag_proud]) cylinder(d = rmag_d, h = rmag_h, $fn = 96);
        translate([0, 0, rmag_seat_z]) rmag_retainer();
    }
}

// ---- D-shaft coupler bore + set screw ----
// Standard NEMA17 5mm shaft with a D-flat on one side (17HE19-2004S
// drawing: 4.5mm across the flat, flat 15mm long from the tip). The bore is
// a true D over the length where the shaft's flat actually is, so the flat
// drives the hub by itself, plus a radial M3 set-screw hole normal to the
// flat to hold it axially. Subtract this from a solid hub; the bore opens
// on -Z (shaft inserts from below) by convention — flip with the caller's
// transform if needed. bore_len = how far the shaft inserts; screw_z =
// height (in this module's local frame) of the set-screw hole above the
// bore's open face; round_len = length at the OPEN end that stays round,
// for a bore deeper than the flat (the shaft's round part has to pass
// through there — a D over the round part would stop it going in). Default
// round_len puts the D over the deepest nema17_flat_len, i.e. assumes the
// shaft tip reaches the bottom of the bore.
//
// FIXED 2026-10-05: until now the "flat" here was a cube ADDED TO THE CUT,
// running from 1.85mm off the axis out past the hub wall — so instead of
// leaving a flat of material for the shaft's flat to bear on, it cut an
// open slot through one side of the hub (checked with a cross-section
// render: the hub section came out as one open "C" contour, no closed
// bore). Nothing but the set screw's friction could ever have driven a hub
// made with it. Affected the v1 Oldham motor hub (now retired) and
// key_turner_housing.scad's gripper hub (fixed by this, re-render it).
//
// set_screw_pilot_d: this used to be 3.2mm — a standard M3 CLEARANCE
// size (for a screw passing through metal into a nut or tapped hole
// elsewhere), not a thread-forming pilot. With nothing threaded on
// either side, that hole let an M3 set screw slide straight through
// with zero grip — it could never actually clamp onto the shaft.
// 2.6mm is the right size for an M3 screw to cut/form its own threads
// directly in printed PETG as it's driven in (a "thread-forming" or
// "self-tapping" fit, standard practice for light-duty printed
// fasteners). A cone-point or cup-point set screw starts into this
// much more easily than a flat-tip one. See docs/housing_decisions.md.
set_screw_pilot_d = 2.6;
dshaft_fit = 0.15; // mm radial printing clearance
module dshaft_bore(bore_len = 10, screw_z = 6, round_len = -1) {
    rl = round_len < 0 ? max(0, bore_len - nema17_flat_len) : round_len;
    r  = nema17_shaft_d/2 + dshaft_fit;
    flat_y = (nema17_shaft_flat - nema17_shaft_d/2) + dshaft_fit;  // 2.15: flat 2.0mm off the axis + fit
    union() {
        // round part (open end)
        translate([0, 0, -eps_c])
            cylinder(r = r, h = rl + 2*eps_c, $fn = 32);
        // D part: the round bore with everything beyond the flat line left solid
        translate([0, 0, rl])
            linear_extrude(height = bore_len - rl + eps_c)
                intersection() {
                    circle(r = r, $fn = 32);
                    translate([-r - 1, -r - 1]) square([2*r + 2, flat_y + r + 1]);
                }
        // M3 set screw, radial, normal to the flat (along +/-Y), through the
        // side wall — self-taps into the hub's own wall (see set_screw_pilot_d).
        translate([0, 0, screw_z])
            rotate([90, 0, 0])
                cylinder(d = set_screw_pilot_d, h = nema17_body, center = true, $fn = 24);
    }
}

// Returns [x, y] positions of `n` points evenly spaced on a circle of
// radius r, first point at start_angle. Used to lay out both the real
// (door-matched) hole positions and the motor tier's larger, fanned-out
// ring from the same angular pattern — see dial_unit_housing.scad.
function ring_points(n, r, start_angle = 90) =
    [for (i = [0 : n - 1])
        let(a = start_angle + i * 360/n)
        [r * cos(a), r * sin(a)]];

// ---- Oldham coupler: REMOVED 2026-10-05 ----
// The printed Oldham coupler (oldham_* modules) lived here until the dial
// unit's v2 geared redesign. It could not have worked as modeled: the
// disc's tongues were 1mm shorter than CLOSED slots, so the disc could
// slide only +/-0.5mm against the +/-6.9mm the dial unit needed. See git
// history and docs/housing_decisions.md (v2 entry) if it is ever revived:
// a working version needs open-ended slots, or tongues shorter than the
// slot by at least 2x the offset.
