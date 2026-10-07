// Magnet hole fit test (2026-10-07). The Wukong magnets measure 21.5mm
// (Paul), loose in the 22.4mm holes: with nothing fastening the retainer to
// the plate, a magnet + retainer can slide out of the inner side when the
// unit is off the door. Fix: a hole the rubber grips. This strip has five
// holes, same depth as the real ones (5mm plate + 0.8mm seat ring = 5.8mm),
// diameters engraved beside each. Print it like the plates (PETG, door face
// on the bed), then press a magnet into each: pick the smallest hole the
// magnet goes into by thumb pressure and that holds it upside down.
include <common_mounts.scad>
diams = [21.4, 21.5, 21.6, 21.7, 21.8];
pitch = 28; t = 5; w = 42;
difference() {
    union() {
        translate([-pitch/2, -w/2, 0]) cube([pitch * len(diams), w, t]);
        for (i = [0 : len(diams) - 1]) translate([i * pitch, 0, 0]) cylinder(d = rmag_ring_od, h = rmag_seat_z, $fn = 96);
    }
    for (i = [0 : len(diams) - 1]) {
        translate([i * pitch, 0, -0.1]) cylinder(d = diams[i], h = rmag_seat_z + 0.2, $fn = 128);
        translate([i * pitch, -w/2 + 1.6, t - 0.6]) linear_extrude(1)
            text(str(diams[i]), size = 3.2, halign = "center", font = "Liberation Sans:style=Bold");
    }
}
