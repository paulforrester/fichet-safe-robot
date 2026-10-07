// Magnet wrap strips (Paul's idea, 2026-10-07): a flat PLA strip wrapped
// once round a 21.5mm magnet before it goes into one of the already-printed
// 22.4mm holes. 69mm long (the magnet's circumference is ~67.5mm, so the ends
// overlap ~1.5mm), 5mm wide, 1, 2 or 3 layers thick at 0.2mm layers.
// The gap each side in a true 22.4 hole is (22.4 - 21.5)/2 = 0.45mm, so the
// 2-layer (0.4) strip is the nominal match; 0.6 is tight, 0.2 loose.
// ID: notches in one end, 1 notch = 1 layer, 2 = 2, 3 = 3.
// Print flat, PLA, 0.2mm layer height (first layer 0.2 too, or the 1-layer
// strip comes out at the first-layer height).
lay = 0.2; L = 69; Wd = 5;
module strip(n) {
    difference() {
        cube([L, Wd, n * lay]);
        for (k = [0 : n - 1]) translate([1.2 + k * 2.0, -0.01, -0.1]) cube([0.8, 0.9, n * lay + 0.2]);
    }
}
for (n = [1 : 3]) translate([0, (n - 1) * 9, 0]) strip(n);
