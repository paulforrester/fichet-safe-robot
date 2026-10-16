// ============================================================
// Dial plug TAPER test keys (2026-10-16)
// ============================================================
// Why: the printed dial plug (7.73mm tip-to-tip star, the real key's TIP
// section) snapped in dial A's socket on the door, and once out it was
// plain it was far too small for the socket. Paul's measurements
// (2026-10-16, docs/decisions.md): the socket's star is 10mm tip to tip
// at its mouth, and the real key's 7.73mm tip flares out to ~10mm fins,
// 0.95mm wide, which engage that mouth. Where the flare starts couldn't be
// measured. So: six hand keys, the same 5mm plug length and depth as the
// robot's plug (root 2mm below the door face, tip 7mm), with 10mm fins
// that taper down to the key's 7.73mm tip over T = 0..5mm at the plug's
// end. Paul snug-tests each one.
//
// What each key tells (control/bringup.md is not involved; report to the
// session): does it go all the way in (hex handle flat on the door face)?
// If not, the gap between handle and door face. Then the play: how far it
// turns back and forth before the fins catch.
//   T0: straight 10mm fins over the whole 5mm. All the way in => the
//       socket's 10mm section reaches at least 7mm deep.
//   T5: a cone over the whole plug.
//
// Dimensions (all ASSUMPTIONS to be confirmed by this test except where
// a measurement is quoted):
//   fins       10.0mm tip to tip (Paul, socket, 2026-10-16) - 0.35 clearance
//   fin width  0.95mm (Paul, the key's outer fins, 2026-10-16), printed at
//              the full value as every earlier round
//   tip end    7.73mm (key tip section, calipers, docs/decisions.md) - 0.35
//   core       4.94mm (key hub-to-hub, calipers, docs/decisions.md) - 0.35.
//              The snapped plug's core was 3.38mm (2.00mm teeth on a 7.73
//              star): this one is ~2.5x stiffer in torsion.
//   8 fins at 45deg, as the key.
//
// PRINT: as exported, hex handle flat on the bed, plugs up (the taper then
// narrows upward: no overhang). Plain PETG (not PETG-CF: Paul,
// 2026-10-16, the CF plug was brittle). 0.2mm layers, 4 perimeters.
// Labels on the bottom of each handle: "T<n>" over "0.95".
use <tube_socket_test_key.scad>   // engraving()

fin_tip_d  = 10.0 - 0.35;
end_tip_d  = 7.73 - 0.35;
core_d     = 4.94 - 0.35;
fin_w      = 0.95;
fins       = 8;
plug_len   = 5.0;            // same as the robot's plug (cad/dial_unit_housing.scad)

handle_d   = 16;             // hex across corners, as tube_socket_test_key
handle_len = 24;             // a little shorter than the 32mm hand key: six of them
collar_d   = 11.75;          // into the door's ~12mm recess (docs/decisions.md)
collar_len = 2;              // so the plug root sits 2mm below the door face
eps        = 0.1;

// The plug, z = 0 at its root (collar side), z = length at its tip. Each fin
// is a flat plate of constant width; its outer edge is straight at tip_d,
// then tapers to end_d over the last taper_len. Also meant for the robot's
// gear-shaft once a taper wins.
module tapered_star_plug(tip_d, end_d, root_d, n, width, length, taper_len) {
    t = max(0, min(taper_len, length));
    // radial edge set so the fin's CORNERS sit on tip_d / end_d (as the old
    // tooth_profile(): the diameter a caliper reads across two fins)
    a = sqrt(pow(tip_d/2, 2) - pow(width/2, 2));
    b = sqrt(pow(end_d/2, 2) - pow(width/2, 2));
    prof = t > 0
        ? [[0, 0], [a, 0], [a, length - t], [b, length], [0, length]]
        : [[0, 0], [a, 0], [a, length], [0, length]];
    union() {
        cylinder(d = root_d, h = length, $fn = 48);
        for (i = [0 : n - 1])
            rotate([0, 0, i * 360 / n])
                rotate([90, 0, 0])
                    linear_extrude(height = width, center = true)
                        polygon(prof);
    }
}

module taper_key(taper_len, label) {
    difference() {
        union() {
            cylinder(d = handle_d, h = handle_len, $fn = 6);
            translate([0, 0, handle_len - eps])
                cylinder(d = collar_d, h = collar_len + eps, $fn = 96);
            translate([0, 0, handle_len + collar_len - eps])
                tapered_star_plug(fin_tip_d, end_tip_d, core_d, fins, fin_w, plug_len + eps, taper_len);
        }
        engraving([label, "0.95"]);
    }
}

tapers       = [0, 1, 2, 3, 4, 5];
taper_labels = ["T0", "T1", "T2", "T3", "T4", "T5"];
spacing      = 21;

module taper_key_set() {
    for (i = [0 : len(tapers) - 1])
        translate([(i % 3 - 1) * spacing, (floor(i / 3) - 0.5) * spacing, 0])
            taper_key(tapers[i], taper_labels[i]);
}

taper_key_set();
