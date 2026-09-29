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

// ---- NEMA17 — standard part dimensions, not measured off anything.
// Matches the STEPPERONLINE 55Ncm/2A motors in docs/bom.md, and NEMA17
// is a standardized mounting footprint across vendors regardless.
nema17_body        = 42.3;   // mm, square motor face (for clearance, not a tight fit)
nema17_bolt_square = 31.04;  // mm, bolt-hole center spacing (square pattern)
nema17_bolt_clear  = 3.4;    // mm, M3 clearance hole
nema17_shaft_d     = 5.0;    // mm, shaft diameter
nema17_shaft_flat  = 4.5;    // mm, across-the-flat dimension (D-shaft), typical
nema17_flat_len    = 15;     // mm, length of the flat back from the shaft tip

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
module dshaft_bore(bore_len = 10, screw_z = 6) {
    fit = 0.15; // mm radial printing clearance
    union() {
        translate([0, 0, -eps_c])
            cylinder(d = nema17_shaft_d + 2*fit, h = bore_len + eps_c, $fn = 32);
        // flat: shave the bore wall down to the shaft's across-the-flat
        // dimension, over the flat's known length from the shaft tip
        translate([-(nema17_shaft_d/2 + 2), nema17_shaft_flat - nema17_shaft_d/2 - fit, -eps_c])
            cube([nema17_shaft_d + 4, nema17_shaft_d, min(bore_len, nema17_flat_len) + eps_c]);
        // M3 set screw, radial, through the side wall, centered on the flat
        translate([0, 0, screw_z])
            rotate([90, 0, 0])
                cylinder(d = 3.2, h = nema17_body, center = true, $fn = 24);
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
