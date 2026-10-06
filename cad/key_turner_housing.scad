// ============================================================
// Fichet-Bauche "Complice" safe robot — KEY-TURNER UNIT (v1, 2026-10-06)
//
// Turns the real key (hand-inserted into the lock first) clockwise up to
// ~100deg and back, one NEMA17 directly on the key axis. Replaces the v0.1
// thumbscrew clamp, which was sized before the key was measured.
//
// HOW IT GRIPS: a printed CAP slides over the key's flat head (the "bow").
// The bow sits in a slot in the cap; a tongue on the cap's other face sits
// in a groove in the MOTOR HUB, at 90deg to the slot. That makes the cap
// the middle disc of an Oldham coupling with the bow as one of its jaws:
// the motor axis does NOT have to line up exactly with the key axis
// (hand-placed unit, key wobbles in the lock) — up to ~2.5mm of offset in
// any direction is taken up by sliding, with no side load on the lock.
// Axially the cap is trapped between the key's tip (slot bottom) and the
// hub (tongue in groove), ~0.6 / 0.5mm each way.
//
// FRAME: z = 0 is the DOOR FACE, +z out of the door, key axis = z axis.
// x right, y up. At insertion the bow is VERTICAL: its 24.6mm width runs
// along y, its 2.5-2.9mm thickness along x. The dial cluster is to the
// RIGHT (+x): its 150mm plate edge is ~50mm from the key centre, so the
// unit stays within 43mm of the key on that side (see layout notes).
//
// KEY (Paul's calipers, 2026-10-06 — docs/housing_decisions.md):
//   fully in, protrudes 31.89 from the door face; turns CW ~100deg to a stop
//   collar dia 7.97 from the door to z ~5.6; swelling 9.48 thick at z ~8;
//   bow reaches its full 24.60 width at z ~12.6; thickness tapers steeply
//   from 9.48 (z 8) to ~2.75 over ~10mm, then 2.75 -> 2.5 to the tip
//   (an earlier reading near the top was 2.90); ring hole dia 10.75,
//   6.6mm of metal between the hole and the bow's outer end.
//   Lock hole 12.05; door flat for 50mm around it; door flush with the body.
//
// PARTS (print_key_turner_*.scad):
//   base_assembly()  door plate + 3 legs (door face down, PETG)
//   motor_plate()    motor mount (inner face down, PETG)
//   key_cap()        slot + tongue (slot mouth down, PETG-CF)
//   motor_hub()      groove + D-bore (groove face down, PETG-CF)
//   key_fit_test()   cap + a hand lever: try it on the real key FIRST
//
// DOOR ATTACHMENT: 3 of the same 22mm rubber-coated pot magnets as the dial
// unit (rmag_* in common_mounts.scad): through holes + seat rings + printed
// retainers, rubber 0.2mm proud of the base. They sit between the legs at
// 60/180/300deg, so nothing extra reaches toward the dial unit.
// ============================================================

include <common_mounts.scad>
$fn = 64;

// ---------------- key (measured) ----------------
key_protrusion   = 31.89;
key_collar_d     = 7.97;
key_bow_w        = 24.60;
key_bow_t_max    = 2.90;    // the thickest reading on the flat part
key_bow_full_z   = 12.6;    // full width from here out
key_flat_from_z  = 18.0;    // ~8 + 10: beyond here the bow is <= ~2.9 thick
key_swell_t      = 9.48;
key_swell_z      = 8.0;
key_ring_d       = 10.75;
key_ring_rim     = 6.6;     // metal between the ring hole and the bow's end
key_ring_z       = key_protrusion - key_ring_rim - key_ring_d/2;   // 19.9
lock_hole_d      = 12.05;

// ---------------- cap (Oldham middle disc) ----------------
cap_od        = 36;
cap_z0        = key_flat_from_z + 0.5;     // 18.5: mouth, clear of the thick swelling
slot_w        = key_bow_t_max + 0.4;       // 3.3: bow thickness + clearance
slot_l        = 30;                        // bow 24.6 + 2.7 each side of sliding room
slot_top      = key_protrusion + 0.6;      // 32.49: key tip 0.6 short of the slot bottom
slot_mouth_w  = 6;                         // lead-in at the mouth
slot_mouth_h  = 1.5;
cap_roof      = 2;
cap_top       = slot_top + cap_roof;       // 34.49
tongue_w      = 6;
tongue_h      = 4;
tongue_l      = 28;

// ---------------- motor hub ----------------
hub_od        = 30;
hub_gap       = 0.5;                       // cap top to hub bottom
hub_z0        = cap_top + hub_gap;         // 34.99
groove_w      = tongue_w + 0.5;            // 6.5
groove_top    = cap_top + tongue_h + 0.5;  // tongue top + 0.5 axial play
hub_web       = 1.5;
shaft_tip_z   = groove_top + hub_web;      // 40.49
motor_face_z  = shaft_tip_z + 24;          // 64.49: 17HE19-2004S shaft is 24mm from the face
hub_z1        = motor_face_z - 10.5;       // 53.99: 4.5mm under the motor plate
hub_bore_len  = hub_z1 - shaft_tip_z;      // 13.5, all within the 15mm flat
assert(hub_bore_len <= nema17_flat_len, "hub bore longer than the shaft's flat");

// ---------------- frame ----------------
base_t        = 5;        // = the dial plate; the magnet seat ring adds 0.8
base_r        = 43;                        // 7mm short of the dial plate's edge
base_hole_d   = 28;                        // passes the bow (24.6 wide) as the unit goes on
motor_plate_t = 6;
motor_plate_z0 = motor_face_z - motor_plate_t;   // 58.49
leg_r_pos     = 36;
leg_angles    = [0, 120, 240];
rmag_angles   = [60, 180, 300];           // magnets between the legs, one away from the dials
rmag_r_pos    = 31;
kt_magnet_pts = [for (a = rmag_angles) [rmag_r_pos * cos(a), rmag_r_pos * sin(a)]];
leg_d         = 12;
leg_pts       = [for (a = leg_angles) [leg_r_pos * cos(a), leg_r_pos * sin(a)]];
m6_selftap_pilot_d = 5.4;   // bench-confirmed in the dial unit
m6_selftap_depth   = 16;
m6_clear_d    = 6.4;
m6_csk_top_d  = 14.0;
m6_csk_depth  = (m6_csk_top_d - m6_clear_d) / 2;
m3_csk_top_d  = 6.3;        // same countersink as the dial sled (M3x10, ISO or DIN heads)
m3_csk_depth  = (m3_csk_top_d - nema17_bolt_clear) / 2;
boss_recess_d = nema17_boss_d + 1;
boss_recess_h = nema17_boss_h + 0.5;
shaft_hole_d  = nema17_shaft_d + 2;
can_clear     = 1.5;

// max offset the coupling takes, and the clearances that depend on it
max_offset    = (slot_l - key_bow_w) / 2;                       // 2.7
cap_orbit_r   = cap_od/2 + max_offset;                          // 20.7
leg_inner_r   = leg_r_pos - leg_d/2;                            // 30
assert(leg_inner_r - cap_orbit_r >= 5, "legs too close to the cap's orbit");
assert(base_hole_d/2 > key_bow_w/2 + 1, "base opening won't pass the bow");
assert(motor_plate_z0 - hub_z1 >= 3, "hub too close to the motor plate");
assert(min([for (m = kt_magnet_pts) for (l = leg_pts) norm(m - l)]) - rmag_ring_od/2 - leg_d/2 >= 1.5, "magnet ring too close to a leg");
assert(min([for (m = kt_magnet_pts) norm(m)]) - rmag_ring_od/2 >= base_hole_d/2 + 1.5, "magnet ring too close to the key opening");

// ============================================================
module base_outline() {
    hull() {
        circle(r = base_r);
        for (p = kt_magnet_pts) translate(p) circle(d = rmag_ring_od + 2);
    }
}
module base_plate() {
    difference() {
        union() {
            linear_extrude(height = base_t) base_outline();
            rmag_rings(kt_magnet_pts, base_t);
        }
        translate([0, 0, -eps_c]) cylinder(d = base_hole_d, h = base_t + 2*eps_c);
        // marker notch at 12 o'clock: the bow points this way at insertion
        translate([0, base_hole_d/2, -eps_c]) cylinder(d = 3, h = base_t + 2*eps_c, $fn = 24);
        rmag_holes(kt_magnet_pts, base_t);
    }
}
module base_legs() {
    for (p = leg_pts) translate([p[0], p[1], base_t - eps_c])
        difference() {
            cylinder(d = leg_d, h = motor_plate_z0 - base_t + eps_c);
            translate([0, 0, motor_plate_z0 - base_t - m6_selftap_depth])
                cylinder(d = m6_selftap_pilot_d, h = m6_selftap_depth + 1, $fn = 24);
        }
}
module base_assembly() { union() { base_plate(); base_legs(); } }

module motor_plate_outline() {
    hull() {
        square(nema17_body + can_clear + 6, center = true);
        for (p = leg_pts) translate(p) circle(r = m6_csk_top_d/2 + 4);
    }
}
module motor_plate() {
    translate([0, 0, motor_plate_z0]) difference() {
        linear_extrude(height = motor_plate_t) motor_plate_outline();
        translate([0, 0, -eps_c]) cylinder(d = shaft_hole_d, h = motor_plate_t + 2*eps_c, $fn = 32);
        translate([0, 0, motor_plate_t - boss_recess_h]) cylinder(d = boss_recess_d, h = boss_recess_h + eps_c);
        for (x = [-1, 1]) for (y = [-1, 1])
            translate([x * nema17_bolt_square/2, y * nema17_bolt_square/2, -eps_c]) {
                cylinder(d = nema17_bolt_clear, h = motor_plate_t + 2*eps_c, $fn = 24);
                cylinder(d1 = m3_csk_top_d + 2*eps_c, d2 = nema17_bolt_clear, h = m3_csk_depth + eps_c, $fn = 32);
            }
        for (p = leg_pts) translate([p[0], p[1], -eps_c]) {
            cylinder(d = m6_clear_d, h = motor_plate_t + 2*eps_c, $fn = 24);
            translate([0, 0, motor_plate_t - m6_csk_depth + eps_c])
                cylinder(d1 = m6_clear_d, d2 = m6_csk_top_d, h = m6_csk_depth + eps_c, $fn = 48);
        }
    }
}

// Cap in its assembled position (z = door frame).
module key_cap() {
    difference() {
        union() {
            translate([0, 0, cap_z0]) cylinder(d = cap_od, h = cap_top - cap_z0, $fn = 96);
            intersection() {   // tongue along x, ends rounded to the cap's outline
                translate([-tongue_l/2, -tongue_w/2, cap_top - eps_c]) cube([tongue_l, tongue_w, tongue_h + eps_c]);
                cylinder(d = cap_od - 2, h = 100, $fn = 96);
            }
        }
        // bow slot along y, open at the mouth
        translate([-slot_w/2, -slot_l/2, cap_z0 - eps_c]) cube([slot_w, slot_l, slot_top - cap_z0 + eps_c]);
        // lead-in: wider at the mouth, narrowing to the slot over slot_mouth_h
        hull() {
            translate([-slot_mouth_w/2, -slot_l/2 - 1, cap_z0 - eps_c]) cube([slot_mouth_w, slot_l + 2, eps_c]);
            translate([-slot_w/2, -slot_l/2, cap_z0 + slot_mouth_h]) cube([slot_w, slot_l, eps_c]);
        }
        // outer bottom edge chamfer
        translate([0, 0, cap_z0 - eps_c]) difference() {
            cylinder(d = cap_od + 1, h = 1.2);
            cylinder(d1 = cap_od - 2.4, d2 = cap_od + 0.01, h = 1.2 + eps_c, $fn = 96);
        }
        // direction marks on the roof edge: the slot direction (= bow, vertical at insertion)
        for (s = [-1, 1]) translate([0, s * (cap_od/2), cap_top - 1]) cylinder(d = 2.5, h = 2, $fn = 16);
    }
}

module motor_hub() {
    difference() {
        translate([0, 0, hub_z0]) cylinder(d = hub_od, h = hub_z1 - hub_z0, $fn = 96);
        // groove along x (perpendicular to the bow slot), through
        translate([-hub_od, -groove_w/2, hub_z0 - eps_c]) cube([2*hub_od, groove_w, groove_top - hub_z0 + eps_c]);
        // D-bore from the motor side; the inserted 13.5mm is all on the shaft's flat
        translate([0, 0, hub_z1]) mirror([0, 0, 1]) dshaft_bore(bore_len = hub_bore_len, screw_z = hub_bore_len / 2);
    }
}

// FIRST PRINT: the cap plus a lever that engages the cap's tongue like the
// hub does. Slide it onto the real key by hand and turn it to the stop:
// checks the slot, the lead-in and the Oldham joint. The lever's hole is
// lever_r from the axis: hook a luggage scale there and pull square to the
// lever to measure the key's turning torque (torque = reading x lever_r).
lever_r = 50;
module key_fit_lever() {
    difference() {
        union() {
            translate([0, 0, hub_z0]) cylinder(d = hub_od, h = 10, $fn = 96);
            translate([0, -6, hub_z0]) cube([lever_r + 8, 12, 8]);
        }
        translate([-hub_od, -groove_w/2, hub_z0 - eps_c]) cube([2*hub_od, groove_w, groove_top - hub_z0 + eps_c]);
        translate([lever_r, 0, hub_z0 - eps_c]) cylinder(d = 5, h = 10, $fn = 24);
    }
}

// ---------------- key dummy (from the measurements, for checks only) ----------------
module key_dummy(angle = 0) {
    rotate([0, 0, -angle]) {   // clockwise as seen from in front = -angle about +z
        translate([0, 0, -5]) cylinder(d = key_collar_d, h = 5.6 + 5, $fn = 48);
        hull() {   // collar top -> swelling -> where the bow is thin
            translate([0, 0, 5.6]) cylinder(d = key_collar_d, h = 0.01, $fn = 48);
            translate([-key_swell_t/2, -5, key_swell_z]) cube([key_swell_t, 10, 0.01]);
            translate([-key_bow_t_max/2, -key_bow_w/2, key_flat_from_z]) cube([key_bow_t_max, key_bow_w, 0.01]);
            translate([-key_bow_t_max/2, -key_bow_w/2, key_bow_full_z]) cube([key_bow_t_max, key_bow_w, 0.01]);
        }
        difference() {   // flat bow: full width from 12.6, round end reaching the tip
            rotate([0, 90, 0]) linear_extrude(height = key_bow_t_max, center = true)
                hull() {
                    translate([-key_bow_full_z, 0]) square([0.01, key_bow_w], center = true);
                    translate([-(key_protrusion - key_bow_w/2), 0]) circle(d = key_bow_w, $fn = 96);
                }
            translate([0, 0, key_ring_z]) rotate([0, 90, 0]) cylinder(d = key_ring_d, h = 10, center = true, $fn = 48);
        }
    }
}
module motor_dummy() {
    translate([-nema17_body/2, -nema17_body/2, motor_face_z]) cube([nema17_body, nema17_body, 48]);
    translate([0, 0, motor_face_z - nema17_boss_h]) cylinder(d = nema17_boss_d, h = nema17_boss_h);
    translate([0, 0, shaft_tip_z]) cylinder(d = nema17_shaft_d, h = 24, $fn = 24);
}

// assembled view / checks. angle = key rotation (0..100, CW). off = [x, y]
// offset of the KEY axis from the unit's (motor) axis, i.e. how far off-centre
// the unit was put on; the cap takes up the difference.
module assembled(part = "all", angle = 0, off = [0, 0]) {
    if (part == "all" || part == "base") base_assembly();
    if (part == "all" || part == "plate") motor_plate();
    if (part == "all" || part == "key") translate([off[0], off[1], 0]) key_dummy(angle);
    // the cap can slide along the bow (slot direction u, turning with the key)
    // relative to the key, and along the hub groove (perpendicular to u)
    // relative to the motor axis -> its centre is the key position minus its
    // component along u... i.e. the projection of the key offset onto v.
    a = -angle;
    u = [-sin(a), cos(a)];
    k = off;
    c = k - (k[0]*u[0] + k[1]*u[1]) * u;
    if (part == "all" || part == "cap") translate([c[0], c[1], 0]) rotate([0, 0, a]) key_cap();
    if (part == "all" || part == "hub") rotate([0, 0, a]) motor_hub();
    if (part == "all" || part == "motor") motor_dummy();
    if (part == "all" || part == "rmags") {
        rmag_dummies(kt_magnet_pts);
        for (p = kt_magnet_pts) translate([p[0], p[1], rmag_seat_z + rmag_ret_t]) cylinder(d = 8, h = 3.2, $fn = 32);
    }
}

echo(KEY_TURNER = [["cap_z0", cap_z0], ["slot_top", slot_top], ["cap_top", cap_top], ["hub", hub_z0, hub_z1],
                   ["shaft_tip_z", shaft_tip_z], ["motor_face_z", motor_face_z], ["max_offset", max_offset],
                   ["leg_clear", leg_inner_r - cap_orbit_r], ["key_ring_z", key_ring_z]]);

// print placements
module print_base()       base_assembly();
module print_motor_plate() translate([0, 0, -motor_plate_z0]) motor_plate();
module print_cap()        translate([0, 0, -cap_z0]) key_cap();                     // mouth down
module print_hub()        translate([0, 0, -hub_z0]) motor_hub();                   // groove face down
module print_fit_lever()  translate([0, 0, -hub_z0]) key_fit_lever();

show_print_layout = true;
if (show_print_layout) {
    print_base();
    translate([100, 0, 0]) print_motor_plate();
    translate([-70, 30, 0]) print_cap();
    translate([-70, -20, 0]) print_hub();
}

// ============================================================
// PRINT / ASSEMBLY NOTES
//  1. Print key_fit_test (cap + lever) FIRST and try it on the real key:
//     it should slide over the bow without forcing, sit with the key tip
//     just short of the slot bottom, and turn the key to its stop. Then
//     hang a luggage scale on the lever hole and note the force at the
//     stop and while turning — that sizes the motor current and the door
//     attachment.
//  2. Cap + hub in PETG-CF (wear surfaces), base and motor plate in PETG.
//     Elephant-foot compensation on for the cap (the slot mouth is on the bed).
//  3. Hardware: 3x Wukong 22mm rubber magnets + their M4 screws, 3 printed
//     retainers (print_magnet_retainer.scad), 4x M3x10 countersunk (motor, from the plate's inner face),
//     3x M6x20 countersunk (plate to legs, self-tapping, same as the dial unit),
//     optional M3x3/x4 grub in the hub.
//  4. Assembly: motor onto the plate, hub onto the shaft, plate onto the
//     legs. Mounting: key in the lock, bow vertical; turn the cap so its
//     two roof marks are top and bottom; slide the unit straight on.
// ============================================================
