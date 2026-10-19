// ============================================================
// Fichet-Bauche "Complice" safe robot — KEY-TURNER UNIT (v2.1, 2026-10-19)
//
// v2.1 (Paul's first print, 2026-10-19): M3x6 instead of M3x10 in the key
// shaft (the 10mm's thread-cutting torque snapped the shaft at the gear),
// a root fillet there, and a bearing retainer ring with 4 tabs (Paul's design).
//
// Turns the real key (hand-inserted into the lock first) clockwise up to
// ~100deg and back. v2: through a 5:1 printed spur-gear pair (12T pinion on
// the motor, 60T gear on the key axis). v1 drove the key directly; on the
// door the key turned out to need 0.74 N·m from ~55deg to its stop and
// >= 0.98 N·m to start back from the stop (Paul, luggage scale, 2026-10-18),
// and the motor could take it out but not bring it back
// (docs/housing_decisions.md, 2026-10-18 entries).
//
// HOW IT GRIPS (unchanged from v1): a printed CAP slides over the key's
// flat head (the "bow"). The bow sits in a slot in the cap; a tongue on the
// cap's other face sits in a groove in the KEY SHAFT, at 90deg to the slot:
// the cap is the middle disc of an Oldham coupling with the bow as one of
// its jaws, so the shaft axis does NOT have to line up exactly with the key
// axis — up to ~2.5mm of offset is taken up by sliding, with no side load
// on the lock. v2: the groove is cut into the underside of the 60T gear,
// closed at both ends (the gear is wider than the groove's travel).
//
// FRAME: z = 0 is the DOOR FACE, +z out of the door, key axis = z axis.
// x right, y up. At insertion the bow is VERTICAL. The dial cluster is to
// the RIGHT (+x): its plate edge is ~50mm from the key centre, so the unit
// stays within 43mm of the key on that side. The motor sits gear_cd to the
// LEFT (-x), where the door is flat for ~150mm (photo docs/photos/door-
// overall.jpg, scaled from the 125mm key-to-dials distance).
//
// AXIAL STACK (key axis): cap 18.5-34.5 (tongue to 38.5) | key shaft:
// gear 35.0-46.5 with the groove in its underside, spacer to 50.5, journal
// in two 608 bearings 50.5-64.5 in the motor plate's boss | washer + M3x6
// countersunk on top. Motor axis: pinion teeth 34.5-47.0, hub to 57.5,
// plate 58.5-64.5, motor face on the plate's top (z 64.5).
//
// PARTS (print_key_turner_*.scad):
//   base_assembly()   door plate + 4 legs + 3 magnet seats (door face down, PETG)
//   motor_plate()     motor mount + bearing boss (inner face down, PETG)
//   key_cap()         slot + tongue (slot mouth down, PETG-CF) — unchanged from v1
//   key_shaft()       60T gear + groove + spacer + journal (groove face down, plain PETG)
//   key_pinion()      12T on the motor's D-shaft (hub end down, PETG-CF)
//   shaft_washer()    clamps the bearings' inner rings (flat, plain PETG)
//   bearing_retainer() holds the 608s in the boss (v2.1, countersunk face down, plain PETG)
//   key_fit_test()    cap + a hand lever (v1; still the torque-measuring tool)
//
// DOOR ATTACHMENT: 3 of the same 22mm rubber-coated pot magnets as v1: two
// beside the key (+/-30deg), one under the motor's far end.
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

// ---------------- cap (Oldham middle disc) — unchanged from v1 ----------------
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

// ---------------- gears: 5:1, module 1.25, 20deg ----------------
// 12T pinion / 60T gear. Torque: >= 0.98 N·m breakaway at the key; the motor
// (~0.3-0.4 N·m at 1 A, docs/housing_decisions.md 2026-10-06) x 5 x ~0.9
// gives ~1.4-1.8 N·m, ~1.5-1.8x the breakaway. Module 1.25 and 12mm faces for
// the tooth load: at 2 N·m the 60T's pitch circle (r 37.5) carries ~53 N,
// Lewis bending on the 12T (Y ~0.25) ~14 MPa — under half of printed PETG's
// strength (judgment, not a cited fatigue figure; the motor's current limit
// keeps the real load below this). Size limit: the 60T's tip radius has to
// stay under the 43mm allowed toward the dials.
// Profile shift +0.3 on the pinion / -0.3 on the gear: a 12T pinion cuts into
// its own roots below ~17T without it (minimum (17-12)/17 = 0.29); shifting
// the gear the other way keeps the standard centre distance. Checked in 2D
// (cad/tools/key_turner_check.py): no overlap through a tooth pitch.
kg_m        = 1.25;
kg_gear_t   = 60;
kg_pinion_t = 12;
kg_gear_x   = -0.3;
kg_pinion_x =  0.3;
kg_pa       = 20;
kg_backlash = 0.25;   // mm, as the dial pair: ~0.4deg at the key
kg_ratio    = kg_gear_t / kg_pinion_t;                    // 5
gear_cd     = kg_m * (kg_gear_t + kg_pinion_t) / 2;       // 45mm (shifts cancel)
kg_gear_tip_r   = kg_m * (kg_gear_t/2 + 1 + kg_gear_x);   // 38.375
kg_gear_root_r  = kg_m * (kg_gear_t/2 - 1.25 + kg_gear_x);   // 35.56
kg_pinion_tip_r = kg_m * (kg_pinion_t/2 + 1 + kg_pinion_x);  // 9.125
kg_pinion_root_r = kg_m * (kg_pinion_t/2 - 1.25 + kg_pinion_x);  // 6.31
motor_xy    = [-gear_cd, 0];

// ---------------- key shaft (gear + groove + spacer + journal) ----------------
hub_od      = 30;                          // the fit lever's hub (v1 size)
hub_gap     = 0.5;                         // cap top to gear underside
hub_z0      = cap_top + hub_gap;           // 34.99: gear underside
groove_w    = tongue_w + 0.5;              // 6.5
groove_top  = cap_top + tongue_h + 0.5;    // 38.99: tongue top + 0.5 axial play
// The cap slides along the groove by up to max_offset each way; the tongue's
// ends follow the cap's outline (d cap_od - 2), so the groove is closed at
// tongue half-length + offset + 0.5.
gear_z0     = hub_z0;
gear_z1     = 46.5;                        // 11.5mm face
spacer_d    = 11;                          // SKF 608 da 10-12: the inner ring only
bearing_od  = 22; bearing_id = 8; bearing_w = 7;
bearing_pocket_d = 22.15;                  // the dial unit's light press fit (confirmed there)
lip_hole_d  = 19.5;                        // lip touches the outer ring only (as the dial unit)
lip_h       = 2;
boss_wall   = 2.5;
boss_d      = bearing_pocket_d + 2*boss_wall;   // 27.15
boss_z0     = gear_z1 + 2;                 // 48.5: 2mm over the gear
bear_z0     = boss_z0 + lip_h;             // 50.5
bear_z1     = bear_z0 + 2*bearing_w;       // 64.5
journal_d   = 7.85;                        // as the dial shafts: slides in the 8.00 bore
shaft_top_z = bear_z1 - 0.3;               // 64.2: below the bearing top, so the washer clamps the inner ring
m3_pilot_d  = 2.7;                         // as the dial gear-shafts (self-tapping M3)
m3_lead_in_d = 3.4; m3_lead_in = 1.0;
// v2.1 (Paul, 2026-10-19): an M3x10 cutting its thread 9mm into the journal
// took enough torque to snap the shaft where it meets the gear. Now an M3x6
// countersunk: ~3mm of thread below the washer (ISO head 0.25 proud: tip at
// 64.5 + 2.5 + 0.25 - 6 = 61.25, i.e. 2.95mm into the shaft; DIN flush 3.2mm),
// enough for a clamp that is only snugged; the pilot stops 1.5mm past the tip.
screw_len   = 6;
pilot_depth = 5;
// Root fillet where the spacer meets the gear (the break was there): a cone
// from fillet_d on the gear's top face to the spacer over fillet_h, clear of
// the boss (its lip hole is 19.5, 2mm up).
fillet_d    = 18;
fillet_h    = 1.5;
washer_d    = 11;
washer_t    = 2.5;
m3_csk_top_d  = 6.3;        // same countersink as the motor screws (M3x10, ISO or DIN heads)
m3_csk_depth  = (m3_csk_top_d - nema17_bolt_clear) / 2;
// Bearing retainer (v2.1, Paul's design 2026-10-19): nothing kept the 608s in
// the boss but their light press fit (the dial unit's springs hold its
// bearings; here nothing does). A ring over the top bearing's outer ring with
// 4 tabs, 4x M3x6 countersunk self-tapping into the plate's top. Its 0.3mm
// lip touches only the outer ring (ID 19.5, as the boss's lip: clear of the
// shield and the inner ring) and stands proud of the plate, so the screws
// clamp the bearings down onto the boss lip.
ret_t        = 2.5;
ret_ring_od  = 27;
ret_id       = lip_hole_d;            // 19.5
ret_lip_od   = bearing_pocket_d - 0.25;   // 21.9: enters the pocket, presses the outer ring
ret_lip_h    = 0.3;
ret_screw_r  = 19;                    // screw circle, on the diagonals (clear of the motor can)
ret_tab_r    = 4.5;
ret_angles   = [45, 135, 225, 315];
ret_screw_pts = [for (a = ret_angles) ret_screw_r * [cos(a), sin(a)]];
ret_pilot_depth = 5;                  // into the 6mm plate (1mm floor over the gear)

// ---------------- motor, plate, pinion ----------------
motor_plate_t  = 6;
motor_face_z   = bear_z1;                  // 64.5: the plate's top is flush with the boss top
motor_plate_z0 = motor_face_z - motor_plate_t;   // 58.5
shaft_tip_z    = motor_face_z - 24;        // 40.5: 17HE19-2004S shaft is 24mm from the face
flat_end_z     = shaft_tip_z + nema17_flat_len;   // 55.5: where the D-flat ends
pin_z0   = 34.5;                           // pinion teeth from here (0.5 wider than the gear each way)
pin_z1   = gear_z1 + 0.5;                  // 47.0: teeth end, hub from here
pin_top  = motor_plate_z0 - 1;             // 57.5: 1mm under the plate
pin_hub_d = 16;
pin_round_len = pin_top - flat_end_z;      // 2.0: round bore at the hub end; the D stops the pinion where the flat ends
boss_recess_d = nema17_boss_d + 1;
boss_recess_h = nema17_boss_h + 0.5;
shaft_hole_d  = nema17_shaft_d + 2;
can_clear     = 1.5;

// ---------------- frame ----------------
base_t        = 5;        // = the dial plate; the magnet seat ring adds 0.8
base_hole_d   = 28;       // passes the bow (24.6 wide) as the unit goes on
leg_d         = 12;
leg_pts       = [[21.1, 45.3], [21.1, -45.3], [-gear_cd, 31], [-gear_cd, -31]];
rmag_r_pos    = 31;
kt_magnet_pts = [[rmag_r_pos*cos(30), rmag_r_pos*sin(30)], [rmag_r_pos*cos(-30), rmag_r_pos*sin(-30)], [-62, 0]];
m6_selftap_pilot_d = 5.4;   // bench-confirmed in the dial unit
m6_selftap_depth   = 16;
m6_clear_d    = 6.4;
m6_csk_top_d  = 14.0;
m6_csk_depth  = (m6_csk_top_d - m6_clear_d) / 2;
dial_side_limit = 43;       // max +x of anything (the dial unit's plate edge is ~50)

// max offset the coupling takes, and the clearances that depend on it
max_offset    = (slot_l - key_bow_w) / 2;                       // 2.7
cap_orbit_r   = cap_od/2 + max_offset;                          // 20.7
groove_half_l = tongue_l/2 + max_offset + 0.5;                  // 17.2
min_leg_to_key = min([for (l = leg_pts) norm(l)]) - leg_d/2;

assert(gear_z0 >= cap_top + 0.4, "gear too close to the cap");
assert(groove_half_l < kg_gear_root_r - 8, "groove too long for the gear");
assert(min_leg_to_key - kg_gear_tip_r >= 3, "a leg too close to the gear's teeth");
assert(min([for (l = leg_pts) norm(l - motor_xy)]) - leg_d/2 - pin_hub_d/2 >= 5, "a leg too close to the pinion");
assert(pin_round_len >= 1.5, "pinion's D-bore would sit on the round part of the shaft");
assert(shaft_tip_z > pin_z0 + 3 && shaft_tip_z < pin_z1, "motor shaft tip should end inside the pinion's teeth");
assert(pin_z1 >= gear_z1 + 0.5, "pinion hub would rub the gear's top face");
assert(boss_z0 - gear_z1 >= 1.5, "boss too close to the gear");
assert(motor_plate_z0 - pin_top >= 1, "pinion too close to the plate");
assert(kg_gear_tip_r + 2 < dial_side_limit, "gear reaches toward the dials");
assert(max([for (m = kt_magnet_pts) m[0]]) + rmag_ring_od/2 + 1 <= dial_side_limit, "magnet ring reaches toward the dials");
assert(min([for (m = kt_magnet_pts) for (l = leg_pts) norm(m - l)]) - rmag_ring_od/2 - leg_d/2 >= 1.5, "magnet ring too close to a leg");
assert(min([for (m = kt_magnet_pts) norm(m)]) - rmag_ring_od/2 >= base_hole_d/2 + 1.5, "magnet ring too close to the key opening");
assert(min([for (l = [leg_pts[2], leg_pts[3]]) abs(l[1])]) - m6_csk_top_d/2 >= (nema17_body + can_clear)/2 + 1, "M6 head under the motor can");
assert(min_leg_to_key - cap_orbit_r >= 5, "legs too close to the cap's orbit");
assert(fillet_d < lip_hole_d - 1 && gear_z1 + fillet_h <= boss_z0 - 0.5, "shaft root fillet would touch the boss");
assert(shaft_top_z - pilot_depth < bear_z1 + washer_t + 0.25 - screw_len - 1, "shaft pilot shorter than the screw");
assert(ret_pilot_depth <= motor_plate_t - 1, "retainer pilots would break through the plate");
assert(ret_screw_r - nema17_bolt_clear/2 - bearing_pocket_d/2 >= 5, "retainer pilot too close to the bearing pocket");
assert(min([for (q = ret_screw_pts) q[0]]) - ret_tab_r > motor_xy[0] + (nema17_body + can_clear)/2 + 3, "retainer tab under the motor can");
assert(min([for (q = ret_screw_pts) for (l = leg_pts) norm(q - l)]) - ret_tab_r - m6_csk_top_d/2 >= 3, "retainer tab on an M6 head");
assert(base_hole_d/2 > key_bow_w/2 + 1, "base opening won't pass the bow");

// ============================================================
module base_outline() {
    hull() {
        circle(r = base_hole_d/2 + 6);
        for (p = leg_pts) translate(p) circle(d = leg_d + 4);
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
        translate(motor_xy) square(nema17_body + can_clear + 6, center = true);
        circle(d = boss_d);
        for (p = leg_pts) translate(p) circle(r = m6_csk_top_d/2 + 4);
    }
}
module motor_plate() {
    difference() {
        union() {
            translate([0, 0, motor_plate_z0]) linear_extrude(height = motor_plate_t) motor_plate_outline();
            translate([0, 0, boss_z0]) cylinder(d = boss_d, h = bear_z1 - boss_z0, $fn = 96);
        }
        // bearing pocket from the top, lip hole below it
        translate([0, 0, bear_z0]) cylinder(d = bearing_pocket_d, h = bear_z1 - bear_z0 + 1, $fn = 96);
        translate([0, 0, boss_z0 - eps_c]) cylinder(d = lip_hole_d, h = lip_h + 2*eps_c, $fn = 96);
        // motor: shaft hole, boss recess, 4 countersunk M3 from the plate's inner face
        translate([motor_xy[0], motor_xy[1], motor_plate_z0]) {
            translate([0, 0, -eps_c]) cylinder(d = shaft_hole_d, h = motor_plate_t + 2*eps_c, $fn = 32);
            translate([0, 0, motor_plate_t - boss_recess_h]) cylinder(d = boss_recess_d, h = boss_recess_h + eps_c);
            for (x = [-1, 1]) for (y = [-1, 1])
                translate([x * nema17_bolt_square/2, y * nema17_bolt_square/2, -eps_c]) {
                    cylinder(d = nema17_bolt_clear, h = motor_plate_t + 2*eps_c, $fn = 24);
                    cylinder(d1 = m3_csk_top_d + 2*eps_c, d2 = nema17_bolt_clear, h = m3_csk_depth + eps_c, $fn = 32);
                }
        }
        // legs: M6 countersunk from the top
        for (p = leg_pts) translate([p[0], p[1], motor_plate_z0 - eps_c]) {
            cylinder(d = m6_clear_d, h = motor_plate_t + 2*eps_c, $fn = 24);
            translate([0, 0, motor_plate_t - m6_csk_depth + eps_c])
                cylinder(d1 = m6_clear_d, d2 = m6_csk_top_d, h = m6_csk_depth + eps_c, $fn = 48);
        }
        // bearing retainer: 4 blind M3 pilots from the top (self-tapping, v2.1)
        for (q = ret_screw_pts) translate([q[0], q[1], motor_face_z - ret_pilot_depth])
            cylinder(d = m3_pilot_d, h = ret_pilot_depth + eps_c, $fn = 24);
    }
}

// ---------------- cap (v1) ----------------
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

// ---------------- key shaft: 60T gear + groove + spacer + journal ----------------
// One print, groove face down: teeth and journal both vertical (the journal
// prints as a vertical cylinder, like the dial shafts).
module key_shaft() {
    difference() {
        union() {
            translate([0, 0, gear_z0]) linear_extrude(height = gear_z1 - gear_z0, convexity = 10)
                polygon(gear_profile(kg_m, kg_gear_t, kg_gear_x, kg_pa, kg_backlash));
            translate([0, 0, gear_z1 - eps_c]) cylinder(d = spacer_d, h = bear_z0 - gear_z1 + eps_c, $fn = 64);
            translate([0, 0, gear_z1 - eps_c]) cylinder(d1 = fillet_d, d2 = spacer_d, h = fillet_h + eps_c, $fn = 64);   // root fillet (v2.1)
            translate([0, 0, bear_z0 - eps_c]) cylinder(d = journal_d, h = shaft_top_z - bear_z0 + eps_c, $fn = 64);
        }
        // closed groove for the cap's tongue, along x, square ends (the tongue's are square)
        translate([-groove_half_l, -groove_w/2, gear_z0 - eps_c]) cube([2*groove_half_l, groove_w, groove_top - gear_z0 + eps_c]);
        // M3 pilot from the top (self-tapping), with a lead-in
        translate([0, 0, shaft_top_z - pilot_depth]) cylinder(d = m3_pilot_d, h = pilot_depth + eps_c, $fn = 24);
        translate([0, 0, shaft_top_z - m3_lead_in]) cylinder(d = m3_lead_in_d, h = m3_lead_in + eps_c, $fn = 24);
        // direction mark on the gear's top face, along the groove
        translate([kg_gear_root_r - 3, 0, gear_z1 - 0.6]) cylinder(d = 2.5, h = 1, $fn = 16);
    }
}

// Washer on the top bearing's inner ring; the M3x6 countersunk (v2.1) through it
// self-taps into the shaft and pulls the spacer up against the lower inner
// ring: both inner rings clamped, no axial play.
module shaft_washer() {
    translate([0, 0, bear_z1]) difference() {
        cylinder(d = washer_d, h = washer_t, $fn = 48);
        translate([0, 0, -eps_c]) cylinder(d = nema17_bolt_clear, h = washer_t + 2*eps_c, $fn = 24);
        translate([0, 0, washer_t - m3_csk_depth]) cylinder(d1 = nema17_bolt_clear, d2 = m3_csk_top_d, h = m3_csk_depth + eps_c, $fn = 32);
    }
}

// Bearing retainer (v2.1), in its assembled position resting on the top
// bearing's outer ring: lip bottom at the plate top, body 0.3 above it until
// the screws pull the tabs down.
module bearing_retainer() {
    translate([0, 0, bear_z1]) difference() {
        union() {
            translate([0, 0, ret_lip_h]) linear_extrude(height = ret_t) union() {
                circle(d = ret_ring_od, $fn = 96);
                for (q = ret_screw_pts) hull() {
                    translate(q) circle(r = ret_tab_r, $fn = 48);
                    translate(q * (ret_ring_od/2 - ret_tab_r) / ret_screw_r) circle(r = ret_tab_r, $fn = 48);
                }
            }
            cylinder(d = ret_lip_od, h = ret_lip_h + eps_c, $fn = 96);
        }
        translate([0, 0, -eps_c]) cylinder(d = ret_id, h = ret_lip_h + ret_t + 2*eps_c, $fn = 96);
        for (q = ret_screw_pts) translate([q[0], q[1], -eps_c]) {
            cylinder(d = nema17_bolt_clear, h = ret_lip_h + ret_t + 2*eps_c, $fn = 24);
            translate([0, 0, ret_lip_h + ret_t - m3_csk_depth + eps_c])
                cylinder(d1 = nema17_bolt_clear, d2 = m3_csk_top_d, h = m3_csk_depth + eps_c, $fn = 32);
        }
    }
}

// Pinion on the motor's D-shaft. Bore round at the hub end, D from where the
// shaft's flat ends: push it on until the D meets the round part of the
// shaft — that sets its height (as the dial pinions). Optional M3 grub in the hub.
module key_pinion() {
    translate([motor_xy[0], motor_xy[1], 0]) difference() {
        union() {
            translate([0, 0, pin_z0]) linear_extrude(height = pin_z1 - pin_z0 + eps_c, convexity = 10)
                polygon(gear_profile(kg_m, kg_pinion_t, kg_pinion_x, kg_pa, kg_backlash));
            translate([0, 0, pin_z1]) cylinder(d = pin_hub_d, h = pin_top - pin_z1, $fn = 64);
        }
        // shaft enters from the hub end (top); bore blind 0.5 below the shaft tip
        translate([0, 0, pin_top + eps_c]) mirror([0, 0, 1])
            dshaft_bore(bore_len = pin_top - shaft_tip_z + 0.5, screw_z = (pin_top - pin_z1)/2, round_len = pin_round_len);
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
    translate([motor_xy[0], motor_xy[1], 0]) {
        translate([-nema17_body/2, -nema17_body/2, motor_face_z]) cube([nema17_body, nema17_body, 48]);
        translate([0, 0, motor_face_z - nema17_boss_h]) cylinder(d = nema17_boss_d, h = nema17_boss_h);
        translate([0, 0, shaft_tip_z]) cylinder(d = nema17_shaft_d, h = 24, $fn = 24);
    }
}
module bearing_dummies() {
    for (k = [0, 1]) translate([0, 0, bear_z0 + k*bearing_w]) difference() {
        cylinder(d = bearing_od, h = bearing_w, $fn = 64);
        translate([0, 0, -eps_c]) cylinder(d = bearing_id, h = bearing_w + 2*eps_c, $fn = 48);
    }
}
module screw_dummy() {   // M3x6 countersunk (v2.1), head in the washer
    translate([0, 0, bear_z1 + washer_t]) mirror([0, 0, 1]) {
        cylinder(d1 = 6.0, d2 = 3.0, h = 1.5, $fn = 32);
        cylinder(d = 2.7, h = screw_len, $fn = 24);   // core diameter: it cuts its own thread in the pilot
    }
}

// assembled view / checks. angle = key rotation (0..100, CW). off = [x, y]
// offset of the KEY axis from the unit's key-shaft axis, i.e. how far
// off-centre the unit was put on; the cap takes up the difference. The
// motor (and pinion) turn kg_ratio times as far, the other way.
module assembled(part = "all", angle = 0, off = [0, 0]) {
    a = -angle;
    if (part == "all" || part == "base") base_assembly();
    if (part == "all" || part == "plate") motor_plate();
    if (part == "all" || part == "key") translate([off[0], off[1], 0]) key_dummy(angle);
    u = [-sin(a), cos(a)];
    k = off;
    c = k - (k[0]*u[0] + k[1]*u[1]) * u;
    if (part == "all" || part == "cap") translate([c[0], c[1], 0]) rotate([0, 0, a]) key_cap();
    if (part == "all" || part == "shaft") rotate([0, 0, a]) key_shaft();
    if (part == "all" || part == "washer") shaft_washer();
    if (part == "all" || part == "retainer") bearing_retainer();
    if (part == "all" || part == "screw") screw_dummy();
    if (part == "all" || part == "bearings") bearing_dummies();
    // pinion phase: 180/N so a pinion tooth sits in the gear's tooth gap on the line of centres
    if (part == "all" || part == "pinion")
        translate([motor_xy[0], motor_xy[1], 0]) rotate([0, 0, 180/kg_pinion_t - a * kg_ratio])
            translate([-motor_xy[0], -motor_xy[1], 0]) key_pinion();
    if (part == "all" || part == "motor") motor_dummy();
    if (part == "all" || part == "rmags") {
        rmag_dummies(kt_magnet_pts);
        for (p = kt_magnet_pts) translate([p[0], p[1], rmag_seat_z + rmag_ret_t]) cylinder(d = 8, h = 3.2, $fn = 32);
    }
}

echo(KEY_TURNER = [["cap_z0", cap_z0], ["slot_top", slot_top], ["cap_top", cap_top],
                   ["gear", [kg_m, kg_gear_t, kg_pinion_t, kg_gear_x, kg_pinion_x, kg_pa, kg_backlash, gear_cd]],
                   ["gear_z", [gear_z0, gear_z1]], ["pinion_z", [pin_z0, pin_z1, pin_top]],
                   ["tips", [kg_gear_tip_r, kg_pinion_tip_r]], ["boss", [boss_z0, bear_z0, bear_z1]],
                   ["shaft_tip_z", shaft_tip_z], ["motor_face_z", motor_face_z], ["max_offset", max_offset],
                   ["leg_to_gear", min_leg_to_key - kg_gear_tip_r], ["leg_to_cap_orbit", min_leg_to_key - cap_orbit_r],
                   ["key_ring_z", key_ring_z]]);
echo(KG_GEAR_PROFILE = gear_profile(kg_m, kg_gear_t, kg_gear_x, kg_pa, kg_backlash));
echo(KG_PINION_PROFILE = gear_profile(kg_m, kg_pinion_t, kg_pinion_x, kg_pa, kg_backlash));
echo(KG_GEAR_PROFILE_NOBL = gear_profile(kg_m, kg_gear_t, kg_gear_x, kg_pa, 0));
echo(KG_PINION_PROFILE_NOBL = gear_profile(kg_m, kg_pinion_t, kg_pinion_x, kg_pa, 0));

// print placements
module print_base()        base_assembly();
module print_motor_plate() translate([0, 0, motor_face_z]) mirror([0, 0, 1]) motor_plate();   // motor face (plate top) down, boss up
module print_cap()         translate([0, 0, -cap_z0]) key_cap();                     // mouth down
module print_key_shaft()   translate([0, 0, -gear_z0]) key_shaft();                  // groove face down
module print_pinion()      translate([-motor_xy[0], -motor_xy[1], pin_top]) mirror([0, 0, 1]) key_pinion();   // hub end down
module print_washer()      translate([0, 0, -bear_z1]) shaft_washer();
module print_retainer()    translate([0, 0, bear_z1 + ret_lip_h + ret_t]) mirror([0, 0, 1]) bearing_retainer();   // countersunk face down, lip up
module print_fit_lever()   translate([0, 0, -hub_z0]) key_fit_lever();

show_print_layout = true;
if (show_print_layout) {
    print_base();
    translate([0, 130, 0]) print_motor_plate();
    translate([-110, -10, 0]) print_cap();
    translate([90, 0, 0]) print_key_shaft();
    translate([90, 60, 0]) print_pinion();
    translate([90, -55, 0]) print_washer();
    translate([140, -55, 0]) print_retainer();
}

// ============================================================
// PRINT / ASSEMBLY NOTES (v2)
//  1. Materials: cap and pinion PETG-CF (wear surfaces); key shaft (gear),
//     washer, base and motor plate plain PETG. Elephant-foot compensation on
//     for the cap, the key shaft and the pinion (their teeth / slot mouth
//     are on the bed).
//  2. Hardware: 3x Wukong 22mm rubber magnets + M4 screws + 3 printed
//     retainers (print_magnet_retainer.scad); 2x 608 bearings; 4x M3x10
//     countersunk (motor, from the plate's inner face); 5x M3x6 countersunk
//     (v2.1: 1 key shaft through the washer, 4 bearing retainer), all
//     self-tapping; 4x M6x16 countersunk (plate to legs, self-tapping);
//     optional M3x3/x4 grub in the pinion's hub.
//  3. Assembly: press both 608s into the boss from the plate's top; bearing
//     retainer on top, lip down into the pocket, 4x M3x6. Motor onto the
//     plate's top (4x M3x10 from below). Pinion onto the motor shaft from
//     below until it stops (the D meets the shaft's round part). Key shaft up
//     through the bearings from below; washer on top; M3x6 into the shaft
//     until the washer clamps the inner ring (snug: the shaft should still
//     turn freely by hand, with no end play; hold the gear, not the motor).
//     Plate onto the legs (4x M6). Turn the gear by hand: the motor should
//     turn 5x, smoothly.
//  4. Mounting: key in the lock, bow vertical; turn the gear so its top-face
//     mark (along the groove) points left or right, i.e. the groove is
//     horizontal; turn the cap so its two roof marks are top and bottom
//     (tongue horizontal) and drop it into the groove... in practice: put
//     the cap on the key first, tongue horizontal, then slide the unit
//     straight on with the groove horizontal.
// ============================================================
