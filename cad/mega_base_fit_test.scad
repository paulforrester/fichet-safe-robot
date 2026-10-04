// ============================================================
// Mega base-plate fit coupon (2026-10-04) — a small, fast print to check
// the 4 M3 self-tap hole positions in dial_unit_housing.scad's
// mega_base_hole_pts against the REAL clear plastic base plate that ships
// with the Arduino Mega 2560, BEFORE printing the whole electronics deck
// with the base-plate mount (now the only Mega mounting).
//
// Why a coupon: those 4 positions were not read off a drawing (none was
// found) — they were measured from a photo of the real base with a ruler
// beside it, good to about +/-0.4mm (see mega_base_hole_pts' comment).
// The base's own holes are ~3.1mm and an M3 screw is 3.0mm, so a hole
// that's 0.4mm off will bind. Better to find out on a 4mm plate than on
// the deck.
//
// How to use: print this (PETG, same material as the deck), lay the base
// plate on it so the two end-flange holes and the two mid-plate U-rim
// holes line up with the coupon's holes (the coupon is in the same
// orientation as the deck: jack/USB end of the Mega toward -X, i.e. the
// "FLANGE" end marked below), and drive 4 M3 screws (M3x6 or x8) through
// the base into the coupon by hand. Report which holes are off, and by
// roughly how much and in which direction; the numbers in
// mega_base_hole_pts get corrected and the deck re-rendered.
//
// KEEP IN SYNC with dial_unit_housing.scad's mega_base_hole_pts (copied,
// not included, same convention as standoff_screw_fit_test.scad — pulling
// in the whole housing file would render the whole assembly too).
// ============================================================

include <common_mounts.scad>

coupon_thickness = 5;   // mm, same as the deck's deck_thickness (thread engagement)
pilot_d          = set_screw_pilot_d; // 2.6mm, same M3 self-tap pilot as the deck

// Deck frame, UNROTATED (the deck rotates these by mega_rotation = 30deg;
// the coupon doesn't need to).
hole_pts = [
    [   5.6, -19.3],  // U-rim hole, mid-plate
    [   5.4,  18.7],  // U-rim hole, mid-plate
    [ -56.3, -25.0],  // end-flange hole
    [ -56.1,  24.0]   // end-flange hole
];

module coupon() {
    difference() {
        // rounded rectangle around the 4 holes, ~9mm of material past each
        translate([-65, -34, 0])
            cube([80, 68, coupon_thickness]);
        for (p = hole_pts)
            translate([p[0], p[1], -eps_c])
                cylinder(d = pilot_d, h = coupon_thickness + 2*eps_c, $fn = 24);
        // orientation mark: a small notch on the flange (-X) edge, so the
        // coupon can't be laid on the base the wrong way round
        translate([-65 - eps_c, -3, -eps_c])
            cube([6, 6, coupon_thickness + 2*eps_c]);
    }
}

coupon();
