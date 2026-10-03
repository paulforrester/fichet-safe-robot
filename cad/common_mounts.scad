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

// ---- D-shaft coupler bore + set screw ----
// Standard NEMA17 5mm shaft with a D-flat milled on one side. Bore is
// round with a flat subtracted in, plus a radial M3 set-screw hole
// through the wall so it can be clamped onto the flat once seated.
// Subtract this from a solid hub; bore opens on -Z (shaft inserts
// from below) by convention — flip with the caller's transform if
// needed. bore_len = how far the shaft inserts; screw_z = height (in
// this module's local frame) of the set-screw hole above the bore's
// open face.
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
module dshaft_bore(bore_len = 10, screw_z = 6) {
    fit = 0.15; // mm radial printing clearance
    union() {
        translate([0, 0, -eps_c])
            cylinder(d = nema17_shaft_d + 2*fit, h = bore_len + eps_c, $fn = 32);
        // flat: shave the bore wall down to the shaft's across-the-flat
        // dimension, over the flat's known length from the shaft tip
        translate([-(nema17_shaft_d/2 + 2), nema17_shaft_flat - nema17_shaft_d/2 - fit, -eps_c])
            cube([nema17_shaft_d + 4, nema17_shaft_d, min(bore_len, nema17_flat_len) + eps_c]);
        // M3 set screw, radial, through the side wall, centered on the
        // flat — self-taps into the hub's own wall (see set_screw_pilot_d
        // above), not a clearance hole into anything threaded.
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

// ---- Oldham coupler (printed) ----
// Bridges a small PARALLEL offset between two coaxial shafts — e.g. a
// motor shaft and a dial coupler shaft that don't line up because the
// real dial holes are spaced too tightly for full-size NEMA17 motors
// to sit directly behind them (see docs/housing_decisions.md). Two
// rigid hubs, each with a slot cut across its face, plus a loose
// middle disc with two perpendicular tongues that ride in those
// slots — all rigid parts, no flexing material, chosen deliberately
// over a bought/molded flex coupler for exactly that reason (repeated
// elastic flexing is a fatigue risk in printed PETG; sliding rigid
// tongues aren't).
oldham_tongue_width = 3.5;  // mm, tongue thickness
oldham_fit          = 0.25; // mm clearance per side, slot vs. tongue
oldham_tongue_h      = 2.2;  // mm, how far a tongue protrudes into its slot
oldham_slot_depth    = oldham_tongue_h + 0.3; // mm, slot depth (a bit deeper than the tongue, axial running clearance)
oldham_disc_web      = 1.4;  // mm, disc material between the two tongues (sets the hub-to-hub gap)

// Standard Oldham sizing rule: slot length >= tongue width + 2x the
// max offset being bridged, so the tongue stays fully engaged at
// worst-case offset. +4mm margin on top of the rule-of-thumb minimum
// — kept tight deliberately: at the dial unit's ~7mm offset this
// already makes for a fairly large hub relative to the ~36mm hole
// spacing (see docs/housing_decisions.md), so margin is trimmed to
// the minimum that's still comfortable to print and slide.
function oldham_slot_length(max_offset) = oldham_tongue_width + 2*max_offset + 4;
// Hub diameter: slot length plus enough rim to keep the slot's ends
// from breaking out the side of the hub.
function oldham_hub_dia(max_offset) = oldham_slot_length(max_offset) + 6;

// Cuts one slot into whatever it's subtracted from, at the origin,
// starting at z=0 and going up by `depth`. angle rotates it in the XY
// plane (0 = along X) — a hub pair must use angles 90 degrees apart.
module oldham_slot_cut(max_offset, angle = 0, depth = oldham_slot_depth) {
    slot_len = oldham_slot_length(max_offset);
    slot_w   = oldham_tongue_width + 2*oldham_fit;
    rotate([0, 0, angle])
        translate([-slot_len/2, -slot_w/2, -eps_c])
            cube([slot_len, slot_w, depth + eps_c]);
}

// Motor-side hub: NEMA17 D-shaft bore from the back face, slot cut
// into the front face. This is the only piece that needs a D-bore —
// the dial-coupler-side hub is printed as part of dial_coupler()
// itself (see dial_unit_housing.scad), not a separate piece.
module oldham_motor_hub(max_offset, len = 6, slot_angle = 0) {
    dia = oldham_hub_dia(max_offset);
    difference() {
        cylinder(d = dia, h = len, $fn = 64);
        translate([0, 0, -eps_c])
            dshaft_bore(bore_len = len - oldham_slot_depth, screw_z = (len - oldham_slot_depth) * 0.6);
        translate([0, 0, len - oldham_slot_depth])
            oldham_slot_cut(max_offset, slot_angle);
    }
}

// The loose middle disc: two perpendicular tongues, one per face —
// slightly undersized relative to the hubs so it's a free sliding fit
// once printed.
module oldham_disc(max_offset) {
    dia      = oldham_hub_dia(max_offset) - 3;
    slot_len = oldham_slot_length(max_offset) - 1;
    tw       = oldham_tongue_width;
    union() {
        cylinder(d = dia, h = oldham_disc_web, $fn = 64);
        // tongue A, +Z side, along X — mates with a slot_angle=0 hub
        translate([-slot_len/2, -tw/2, oldham_disc_web - eps_c])
            cube([slot_len, tw, oldham_tongue_h + eps_c]);
        // tongue B, -Z side, along Y — mates with a slot_angle=90 hub
        translate([-tw/2, -slot_len/2, -oldham_tongue_h])
            cube([tw, slot_len, oldham_tongue_h + eps_c]);
    }
}
