// Split sleeves to make the existing 22.4mm magnet holes grip the 21.5mm
// magnets, without reprinting the plates (Paul's idea, 2026-10-07).
//
// A thin C-shaped sleeve drops into the hole (relaxed OD 22.0, under the
// hole). Pushing a magnet in opens the slit until the sleeve meets the hole
// wall; from there the rubber is squeezed between magnet and sleeve. Grip
// needs 21.5 + 2 x wall > the printed hole. On a true 22.4 hole that is a
// wall over 0.45mm; printed holes usually come out a bit small, so the set
// spans 0.40-0.60mm. The sleeve is the full hole length (5.8 = plate + seat
// ring) with no flange: a flange on the ring top would lift the retainer and
// pull the magnet's face back into the plate.
//
// ID: count the nicks on the top edge, opposite the slit: 1 nick = 0.40,
// 2 = 0.45, 3 = 0.50, 4 = 0.55, 5 = 0.60. Print standing up (as laid out),
// PETG, Arachne walls (Bambu default); check in the slicer preview that every
// sleeve prints as a closed single line (the 0.40 is near a 0.4 nozzle's
// limit).
walls = [0.40, 0.45, 0.50, 0.55, 0.60];
od = 22.0; h = 5.8; slit = 1.5;
nick_w = 0.8; nick_d = 0.8;
module sleeve(t, n) {
    difference() {
        cylinder(d = od, h = h, $fn = 160);
        translate([0, 0, -0.1]) cylinder(d = od - 2*t, h = h + 0.2, $fn = 160);
        translate([0, -slit/2, -0.1]) cube([od, slit, h + 0.2]);           // slit at +x
        for (k = [0 : n - 1]) rotate([0, 0, 180 + (k - (n - 1)/2) * 8])   // nicks opposite
            translate([-od/2 - 0.1, -nick_w/2, h - nick_d]) cube([t + 0.4, nick_w, nick_d + 0.1]);
    }
}
for (i = [0 : len(walls) - 1]) translate([i * 26, 0, 0]) sleeve(walls[i], i + 1);
