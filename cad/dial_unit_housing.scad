// ============================================================
// Fichet-Bauche "Complice" safe robot — DIAL UNIT housing, v2 (GEARED)
// 2026-10-05. Holds the 3 dial motors and mounts to the door over the 3
// dial holes with neodymium magnets. Full reasoning, sources and the
// v0.1-v1 history: docs/housing_decisions.md (newest entry first).
//
// WHY v2 EXISTS (Paul, 2026-10-05: "the motor spindles do not line up
// with the center of the holes for the dial turners ... see if there is
// an orientation for the motors where they can all be mounted to the same
// sled and align with the holes. If not ... another option would be to
// add another level to the robot and work on gearing ... I do have a
// stock of 608 bearings"):
//
//  1. No orientation exists. Two NEMA17 cans (42.3mm square) need >= 42.3mm
//     between their shafts in ANY orientation (the narrowest a square gets
//     is its side), and the two top door holes are only ~33mm apart.
//  2. v1 bridged the offset with a printed Oldham coupler that could not
//     have worked: its disc tongues were 1mm shorter than CLOSED slots
//     (+/-0.5mm of slide, +/-6.9mm needed), and the real 24mm motor shaft
//     ran 18mm into a 20.8mm cavity, straight through the motor hub into
//     the disc and the dial hub.
//  3. v1's hole pattern (36mm equilateral) was a by-eye photo read that was
//     never confirmed. Re-measured from the door photos with software tick
//     detection: an ISOSCELES triangle, ~33.3mm across the top pair and
//     ~43.3mm from each to the bottom hole — up to ~6mm off v1's plate.
//
// v2 DRIVETRAIN: each dial gets a gear-shaft (spline plug + 8mm journal +
// 28T spur gear, one printed piece) running in TWO 608 bearings stacked in
// a boss on the front plate. Each motor drives it through a 14T pinion
// (2:1 reduction), so a motor can sit anywhere on a 21mm circle around its
// dial — far enough out that the three cans clear each other with room for
// the legs. The gear-shaft is free to SLIDE axially 7mm in its bearings and
// is pushed forward by a light compression spring: put the unit on the door
// (plugs that don't line up with their star just get pushed back, so the
// plate still seats flush), then turn each motor slowly and its plug snaps
// into the star when the teeth line up. The pinion is 14mm wide so the gear
// stays meshed over the whole 7mm of travel.
//
// FRAME: x right, y UP ON THE DOOR, z out of the door (z=0 is the door
// face). OpenSCAD's top view (looking down -z) is exactly the view of the
// door from in front of the safe — no mirroring anywhere. Origin = the
// circumcentre of the 3 dial holes.
//
// PRINTED PARTS (all separate bodies — see the PRINT NOTES at the bottom):
//   front_assembly()   front plate + magnet field + 3 bearing bosses + 3 legs
//   rear_assembly()    motor sled + 3 deck legs
//   electronics_deck() Mega base-plate mount (unchanged in principle from v1)
//   dial_gear_shaft()  x3, PETG-CF
//   motor_pinion()     x3, PETG-CF
//   dial_pattern_test() — 3 bosses only, to check the hole pattern on the
//                       real door BEFORE printing the big parts (see notes).
// ============================================================

include <common_mounts.scad>
use <tube_socket_test_key.scad>  // spline_plug()

$fn = 64;

// ============================================================
// 1. DOOR HOLE PATTERN
// ============================================================
// Centre-to-centre distances between the 3 dial holes, A = top-left,
// B = top-right, C = bottom (as seen standing in front of the safe).
// STATUS: PHOTO ESTIMATE, NOT CALIPERS. From docs/photos: dial-holes-ruler-2
// (all 3 holes + ruler, 7.51 px/mm from 71 detected ticks): AB 33.67,
// AC 43.31, BC 43.65; dial-holes-ruler-1 (9.64 px/mm): one pair 32.91;
// dial-holes-ruler-3 (11.3 px/mm): one pair 43.14; the un-scaled closeup
// and tape photos give the same shape (top pair ~0.80x the other two).
// Hole centres from Hough circle fits. Treat as +/-0.5mm until Paul's
// caliper numbers replace them — then re-run cad/tools/dial_layout_check.py.
dial_ab = 33.3;  // mm, A-B (top pair)
dial_ac = 43.3;  // mm, A-C
dial_bc = 43.3;  // mm, B-C

// [A, B, C] relative to the circumcentre (works for any triangle, not just
// isosceles, so the caliper numbers can go straight in).
function _tri(ab, ac, bc) =
    let(cx = (ac*ac - bc*bc) / (2*ab),
        cy = -sqrt(ac*ac - (cx + ab/2)*(cx + ab/2)))
    [[-ab/2, 0], [ab/2, 0], [cx, cy]];
function _circumcentre(P) =
    let(ax = P[0][0], ay = P[0][1], bx = P[1][0], by = P[1][1], cx = P[2][0], cy = P[2][1],
        d = 2*(ax*(by-cy) + bx*(cy-ay) + cx*(ay-by)))
    [((ax*ax+ay*ay)*(by-cy) + (bx*bx+by*by)*(cy-ay) + (cx*cx+cy*cy)*(ay-by)) / d,
     ((ax*ax+ay*ay)*(cx-bx) + (bx*bx+by*by)*(ax-cx) + (cx*cx+cy*cy)*(bx-ax)) / d];
_raw     = _tri(dial_ab, dial_ac, dial_bc);
_cc      = _circumcentre(_raw);
hole_pts = [for (p = _raw) p - _cc];

// ============================================================
// 2. GEARS — module 1, 20deg involute, 28T on the dial / 14T on the motor
// ============================================================
// 2:1 reduction: a full-step NEMA17 (200 steps/rev) gives 400 steps per dial
// revolution = 20 full steps per dial position (20 positions per wheel,
// control/sequence.md), and doubles the torque at the dial — the dial
// torque is still unmeasured (sequence.md open item), and docs/bom.md
// already named gearing as the fix if the motor alone isn't enough.
// Size limit: the two TOP dial gears sit side by side 33.3mm apart, so the
// 28T tip diameter (29.6mm) leaves 3.7mm between them.
// Profile shift +0.2 on the pinion / -0.2 on the gear: a 14T pinion cuts
// into its own tooth roots ("undercut") below about 17T without it
// (minimum shift (17-14)/17 = 0.18); shifting the gear the other way by the
// same amount keeps the standard 21mm centre distance. Verified in 2D
// (cad/tools/dial_layout_check.py): zero overlap through a full tooth
// pitch with zero backlash, contact ratio 1.52, 0.25mm tip/root clearance.
gear_m        = 1;
gear_teeth    = 28;
pinion_teeth  = 14;
gear_x        = -0.2;
pinion_x      =  0.2;
gear_pa       = 20;
gear_backlash = 0.25;  // mm, total circular backlash of the pair (~1.0deg at the dial).
                       // FDM teeth print slightly fat; 0.2-0.3mm is the usual
                       // range for printed gears (judgment, not a cited figure).
gear_cd       = gear_m * (gear_teeth + pinion_teeth) / 2;  // 21mm (shifts cancel)

function inv_deg(a) = (tan(a) - a*PI/180) * 180/PI;   // involute function, in degrees
// one flank as [radius, half-thickness angle] pairs, root -> tip
function _flank(m, N, x, pa, bl, steps) =
    let(r  = m*N/2, rb = r*cos(pa), ra = r + m*(1 + x), rf = r - m*(1.25 - x),
        s  = m*(PI/2 + 2*x*tan(pa)) - bl/2,    // tooth thickness at the pitch circle
        th = s/(2*r) * 180/PI,                  // half-thickness angle there
        r0 = max(rb, rf),
        fl = [for (k = [0 : steps]) let(R = r0 + (ra - r0)*k/steps)
                 [R, th + inv_deg(pa) - inv_deg(acos(min(1, rb/R)))]])
    rf < rb ? concat([[rf, fl[0][1]]], fl) : fl;   // radial line below the base circle
function gear_profile(m, N, x = 0, pa = 20, bl = 0, steps = 10) =
    let(fl = _flank(m, N, x, pa, bl, steps), nf = len(fl),
        rf = m*N/2 - m*(1.25 - x), p = 360/N, h0 = fl[0][1])
    [for (i = [0 : N - 1]) let(c = i*p) each concat(
        [for (k = [0 : nf - 1]) [fl[k][0]*cos(c - fl[k][1]), fl[k][0]*sin(c - fl[k][1])]],
        [for (k = [nf - 1 : -1 : 0]) [fl[k][0]*cos(c + fl[k][1]), fl[k][0]*sin(c + fl[k][1])]],
        [for (j = [1 : 4]) let(t = c + h0 + (p - 2*h0)*j/5) [rf*cos(t), rf*sin(t)]])];

gear_tip_r   = gear_m * (gear_teeth/2 + 1 + gear_x);      // 14.8
pinion_tip_r = gear_m * (pinion_teeth/2 + 1 + pinion_x);  // 8.2

// ============================================================
// 3. MOTOR LAYOUT
// ============================================================
// Each motor's shaft sits gear_cd (21mm) from its dial, in direction
// motor_dir[i]; motor_rot[i] turns the can (and its bolt square) about its
// own shaft. NOT picked by eye: annealing search (cad/tools/dial_layout_
// check.py --optimise) over all 6 angles AND the 6 leg positions below,
// maximising the worst margin over every clearance listed there (can-to-can
// >= 6mm, pinion vs the OTHER dials' gears, counterbores vs spring pockets,
// legs vs gears/pinions/cans, screw-driver access to every countersink,
// everything inside the 150mm front plate). Re-run it if dial_* change.
motor_dir = [216.4, 114.1, 337.1];  // degrees, dial -> motor shaft
motor_rot = [36.3, 36.3, 56.2];     // degrees, can rotation about its own shaft
motor_pts = [for (i = [0 : 2])
    hole_pts[i] + gear_cd * [cos(motor_dir[i]), sin(motor_dir[i])]];

// ============================================================
// 4. AXIAL STACK (z = 0 is the door face; every number below is derived
//    from the one before it, so changing one moves everything after it)
// ============================================================
plate_thickness    = 5;      // front plate
lip_h              = 2;      // door-side lip that the front bearing sits on
// 608 bearing: 8 x 22 x 7mm. SKF 608-2Z abutment data (im-tek.com/skf-608-2z):
// inner-ring shoulder da 10-12mm, outer-ring shoulder Da max 20mm, shield
// edge D2 19.2mm.
bearing_od         = 22;
bearing_id         = 8;
bearing_w          = 7;
bearings_per_shaft = 2;      // stacked in one boss; 1 also works (shorter boss), see notes
bearing_pocket_d   = 22.15;  // light press fit for the outer ring — CONFIRM on
                             // dial_pattern_test() before the big print
lip_hole_d         = 19.5;   // between D2 (19.2) and Da max (20): the lip touches
                             // only the outer ring, never the shield or inner ring
boss_wall          = 2.5;
boss_d             = bearing_pocket_d + 2*boss_wall;
boss_h             = lip_h + bearings_per_shaft * bearing_w;   // 16

journal_d   = 7.85;  // printed shaft through the 8.00mm bearing bore: a SLIDING fit
                     // on purpose (the shaft has to slide for the spring-loaded
                     // plug). Printed vertical cylinders usually come out a
                     // little fat — CONFIRM it slides on the test print.
spacer_d    = 11;    // SKF da 10-12: bears on the rear bearing's inner ring only
spacer_h    = 1.5;
gear_face   = 6;
travel      = 7;     // plug can be pushed back this far (plug tip ends flush with the plate)

// tooth geometry for the plug (restated from tube_socket_test_key.scad —
// `use` doesn't import variables; same values as v1, locked in docs/decisions.md)
tooth_count_v   = 8;
key_tip_dia_v   = 7.73;
tooth_height_v  = 2.00;
tooth_width_v   = 1.04;
fit_clearance_v = 0.35;
plug_len        = 5.0;

// gear-shaft in its FORWARD position (spacer against the rear bearing):
gear_z0     = boss_h + spacer_h;        // 17.5, gear front face
gear_z1     = gear_z0 + gear_face;      // 23.5, gear rear face
plug_z0     = -2;                       // plug root: same place v1's collar/plug put it
                                        // (2mm into the door's ~12mm recess, like the
                                        // hand test key that clicked the dials)
plug_z1     = plug_z0 - plug_len;       // -7, plug tip

pinion_z0   = gear_z0 - 0.5;                       // 17
pinion_face = gear_face + travel + 1;              // 14: gear stays meshed at full travel
pinion_z1   = pinion_z0 + pinion_face;             // 31
pinion_hub_h = 4;                                  // set-screw collar on the motor side
pinion_hub_d = 12;
cavity_top  = pinion_z1 + pinion_hub_h + 0.5;      // 35.5 = motor sled's inner face
motor_plate_h = 6;
motor_face_z  = cavity_top + motor_plate_h;        // 41.5, motors bolt to this face
nema17_shaft_len = 24;  // 17HE19-2004S drawing: 24 +/-0.5 from the mounting face
shaft_tip_z   = motor_face_z - nema17_shaft_len;   // 17.5 — ends inside the pinion

// spring: compression spring between the gear's rear face and the sled
spring_pocket_d   = 8.6;  // for a spring up to ~8mm OD
gear_spring_depth = 2;    // pocket in the gear's rear face
sled_spring_depth = 3;    // pocket in the sled's inner face
spring_len_fwd = (cavity_top + sled_spring_depth) - (gear_z1 - gear_spring_depth);   // 17
spring_len_back = spring_len_fwd - travel;                                           // 10

nema17_can_length = 48;   // 17HE19-2004S drawing: 48 MAX
deck_clearance    = 6;
deck_standoff_h   = nema17_can_length + deck_clearance;
deck_z            = motor_face_z + deck_standoff_h;   // 95.5
deck_thickness    = 5;

// ============================================================
// 5. JOINTS AND LEGS (positions from the same search as motor_dir)
// ============================================================
// Front-to-sled joint: 3 legs on the front plate, M6 countersunk self-tap
// screws down through the sled (bench-proven hardware, v1). Not a
// symmetric pattern, so the sled bolts on one way only (keying mismatch
// under +/-120deg rotation is in the check script's report).
joint_pts    = [[59.5, -8.3], [-25.8, -50.5], [-18.7, 60.6]];
// Sled-to-deck legs, between the motor cans.
deck_leg_pts = [[-4.5, -59.4], [29.7, 8.2], [-50.5, 43.5]];

leg_dia            = 12;
m6_selftap_pilot_d = 5.4;   // bench-confirmed (standoff_screw_fit_test.scad)
m6_selftap_depth   = 12;
m6_clear_d         = 6.4;
m6_csk_top_d       = 14.0;  // ISO 10642 M6 dk max 13.44 + margin
m6_csk_depth       = (m6_csk_top_d - m6_clear_d) / 2;

// motor mounting
boss_recess_d  = nema17_boss_d + 1;    // 23 (Paul's sizing, v1)
boss_recess_h  = nema17_boss_h + 0.5;  // 2.5
motor_shaft_hole_d = nema17_shaft_d + 2;
m3_cbore_d     = 6.5;   // M3 socket head 5.5 + 1
m3_cbore_depth = 2;     // leaves 4mm under the head: an M3x8 then engages 4mm of the
                        // motor's "M3 DEPTH 4.5 MIN" holes without bottoming

function rot2(p, a) = [p[0]*cos(a) - p[1]*sin(a), p[0]*sin(a) + p[1]*cos(a)];
motor_bolt_pts = [for (i = [0 : 2]) [for (k = [0 : 3])
    motor_pts[i] + rot2([nema17_bolt_square/2 * (k < 2 ? 1 : -1),
                         nema17_bolt_square/2 * (k % 2 == 0 ? 1 : -1)], motor_rot[i])]];

// ============================================================
// 6. FRONT PLATE: 150mm circle, pointer, magnets
// ============================================================
front_plate_dia = 150;
front_plate_r   = front_plate_dia / 2;
// Pointer tab: now points UP ON THE DOOR for real (+y = the side the
// two close-together holes are on — the top pair in docs/photos/
// dial-holes-ruler-4.jpg). Mount with the arrow up.
pointer_len   = 10;
pointer_w     = 16;
pointer_angle = 90;

module front_plate_outline() {
    circle(r = front_plate_r, $fn = 96);
    rotate([0, 0, pointer_angle - 90])
        polygon([[-pointer_w/2, front_plate_r - 5], [pointer_w/2, front_plate_r - 5],
                 [0, front_plate_r + pointer_len]]);
}

// Magnet field (door face), same hex-lattice idea as v1: pocket centres
// magnet_pitch apart, magnet_rim_wall inside the rim, and clear of the
// bearing pocket that sits above each dial (a pocket under it would leave
// 0.1mm of plastic between the magnet and the bearing).
magnet_wall     = 2;
magnet_rim_wall = 2.5;
magnet_pitch    = magnet_pocket_d + magnet_wall;
magnet_offset   = [5, 3];
magnet_dial_excl_r = bearing_pocket_d/2 + magnet_wall + magnet_pocket_d/2;
function magnet_ok(p) =
    norm(p) <= front_plate_r - magnet_rim_wall - magnet_pocket_d/2
    && min([for (h = hole_pts) norm(p - h)]) >= magnet_dial_excl_r;
magnet_pts = [for (i = [-12 : 12]) for (j = [-12 : 12])
    let(p = [(i + j/2) * magnet_pitch + magnet_offset[0],
             j * magnet_pitch * sqrt(3)/2 + magnet_offset[1]])
    if (magnet_ok(p)) p];
echo(magnet_pocket_count = len(magnet_pts));
show_magnets = true;   // false only speeds up check renders (cad/tools/)

// the bearing bores (lip hole + pocket), shared by the plate and the test coupon
module bearing_bores() {
    for (p = hole_pts) translate([p[0], p[1], 0]) {
        translate([0, 0, -eps_c]) cylinder(d = lip_hole_d, h = lip_h + 2*eps_c, $fn = 64);
        translate([0, 0, lip_h]) cylinder(d = bearing_pocket_d, h = boss_h, $fn = 96);
    }
}
module bearing_bosses() {
    for (p = hole_pts) translate([p[0], p[1], plate_thickness - eps_c])
        cylinder(d = boss_d, h = boss_h - plate_thickness + eps_c, $fn = 96);
}

module front_plate() {
    difference() {
        union() {
            linear_extrude(height = plate_thickness) front_plate_outline();
            bearing_bosses();
        }
        bearing_bores();
        if (show_magnets) for (p = magnet_pts) translate([p[0], p[1], -eps_c]) magnet_pocket();
    }
}

module front_standoff_legs() {
    leg_h = cavity_top - plate_thickness + eps_c;
    for (p = joint_pts) translate([p[0], p[1], plate_thickness - eps_c])
        difference() {
            cylinder(d = leg_dia, h = leg_h, $fn = 32);
            translate([0, 0, leg_h - m6_selftap_depth])
                cylinder(d = m6_selftap_pilot_d, h = m6_selftap_depth + eps_c, $fn = 24);
        }
}

module front_assembly() { union() { front_plate(); front_standoff_legs(); } }

// ============================================================
// 7. MOTOR SLED (rear_assembly)
// ============================================================
can_clear = 1.5;  // relief around the 42.3mm can, same as v1
module motor_plate_outline() {
    hull() {
        for (i = [0 : 2]) translate(motor_pts[i]) rotate([0, 0, motor_rot[i]])
            square(nema17_body + can_clear + 6, center = true);   // 3mm of plate past each can
        for (p = joint_pts)    translate(p) circle(r = m6_csk_top_d/2 + 4, $fn = 48);
        for (p = deck_leg_pts) translate(p) circle(r = leg_dia/2 + 1, $fn = 48);
        for (p = hole_pts)     translate(p) circle(r = spring_pocket_d/2 + 3, $fn = 32);
    }
}

module motor_plate() {
    translate([0, 0, cavity_top]) difference() {
        linear_extrude(height = motor_plate_h) motor_plate_outline();
        for (i = [0 : 2]) {
            translate([motor_pts[i][0], motor_pts[i][1], -eps_c])
                cylinder(d = motor_shaft_hole_d, h = motor_plate_h + 2*eps_c, $fn = 32);
            translate([motor_pts[i][0], motor_pts[i][1], motor_plate_h - boss_recess_h])
                cylinder(d = boss_recess_d, h = boss_recess_h + eps_c, $fn = 64);
            for (b = motor_bolt_pts[i]) translate([b[0], b[1], -eps_c]) {
                cylinder(d = nema17_bolt_clear, h = motor_plate_h + 2*eps_c, $fn = 24);
                cylinder(d = m3_cbore_d, h = m3_cbore_depth + eps_c, $fn = 32);  // heads on the cavity side
            }
        }
        // spring pockets above each dial (inner face)
        for (p = hole_pts) translate([p[0], p[1], -eps_c])
            cylinder(d = spring_pocket_d, h = sled_spring_depth + eps_c, $fn = 48);
        // front joint: M6 clearance + countersink on the OUTER (motor) face
        for (p = joint_pts) translate([p[0], p[1], -eps_c]) {
            cylinder(d = m6_clear_d, h = motor_plate_h + 2*eps_c, $fn = 24);
            translate([0, 0, motor_plate_h - m6_csk_depth + eps_c])
                cylinder(d1 = m6_clear_d, d2 = m6_csk_top_d, h = m6_csk_depth + eps_c, $fn = 48);
        }
    }
}

module deck_standoff_legs() {
    leg_h = deck_standoff_h + eps_c;
    for (p = deck_leg_pts) translate([p[0], p[1], motor_face_z - eps_c])
        difference() {
            cylinder(d = leg_dia, h = leg_h, $fn = 32);
            translate([0, 0, leg_h - m6_selftap_depth])
                cylinder(d = m6_selftap_pilot_d, h = m6_selftap_depth + eps_c, $fn = 24);
        }
}

module rear_assembly() { union() { motor_plate(); deck_standoff_legs(); } }

// ============================================================
// 8. DRIVETRAIN PARTS (local print frames: flat face on the bed at z=0)
// ============================================================
// Gear-shaft. Print frame: z=0 is the gear's REAR face (spring side) on the
// bed; the plug is the top. Assembly z = gear_z1 - local z.
module dial_gear_shaft() {
    root_d = (key_tip_dia_v - 2*tooth_height_v) - fit_clearance_v;
    tip_d  = key_tip_dia_v - fit_clearance_v;
    journal_len = gear_z0 - spacer_h - plug_z0;   // 18: from the spacer to the plug root
    difference() {
        union() {
            linear_extrude(height = gear_face, convexity = 10)
                polygon(gear_profile(gear_m, gear_teeth, gear_x, gear_pa, gear_backlash));
            translate([0, 0, gear_face - eps_c])
                cylinder(d = spacer_d, h = spacer_h + eps_c, $fn = 48);
            translate([0, 0, gear_face + spacer_h - eps_c])
                cylinder(d = journal_d, h = journal_len + eps_c, $fn = 64);
            translate([0, 0, gear_face + spacer_h + journal_len - eps_c])
                spline_plug(tip_d, root_d, tooth_count_v, plug_len + eps_c, tooth_width_v);
        }
        translate([0, 0, -eps_c])
            cylinder(d = spring_pocket_d, h = gear_spring_depth + eps_c, $fn = 48);
    }
}

// Pinion. Print frame: z=0 is the hub end (motor side) on the bed, teeth on
// top. Assembly z = cavity_top - 0.5 - local z. The motor shaft enters from
// the hub end; its D-flat is the last 15mm toward the tip, so the bore is
// ROUND at the hub end and D-shaped only where the flat actually is (a D
// over the round part of the shaft would stop it going in).
pinion_len = pinion_hub_h + pinion_face;   // 18
pinion_tip_local = (cavity_top - 0.5) - shaft_tip_z;   // 17.5: where the shaft tip sits (local z)
pinion_round_len = 2.5; // round bore at the hub end, D-bore from here to the tip end.
                        // This also SETS THE PINION'S AXIAL POSITION: push it onto the
                        // shaft until it stops — the D can't pass the round part of the
                        // shaft, so it stops where the shaft's flat ends (15mm from the
                        // tip). Nominal shaft (24mm) -> hub end 0.5mm clear of the sled.
                        // Shaft tolerance (+/-0.5) and the flat's run-out move that by
                        // about +/-1mm; either way the pinion is trapped between the sled
                        // face and the bearing-boss tops (1.5mm of room) and stays fully
                        // meshed (checked in cad/tools/dial_layout_check.py), so the set
                        // screw is optional. If used: a GRUB screw (M3x3/x4) only — a cap
                        // screw's head would stand proud and hit the gear and the sled.
module motor_pinion() {
    difference() {
        union() {
            cylinder(d = pinion_hub_d, h = pinion_hub_h + eps_c, $fn = 48);
            translate([0, 0, pinion_hub_h])
                linear_extrude(height = pinion_face, convexity = 10)
                    polygon(gear_profile(gear_m, pinion_teeth, pinion_x, gear_pa, gear_backlash));
        }
        dshaft_bore(bore_len = pinion_len + eps_c, screw_z = pinion_hub_h/2, round_len = pinion_round_len);
    }
}

// ============================================================
// 9. ELECTRONICS DECK (Mega via its own base plate — bench-checked v1 mount)
// ============================================================
mega_hole_pts = [[-35.52, -24.11], [-35.52, 24.15], [39.41, 24.15], [45.76, -24.11]];
mega_base_hole_pts = [[5.6, -19.3], [5.4, 18.7], [-56.3, -25.0], [-56.1, 24.0]];
mega_rotation = 244;       // re-searched for the v2 deck legs (2deg x 2.5mm grid): keeps every
mega_offset   = [-2.5, -5]; // base-plate screw >= 19mm clear of the deck-leg countersinks, and
                            // the board footprint inside r=64. Jack/USB end faces up-right.
function mega_place(p) = rot2(p, mega_rotation) + mega_offset;
mega_hole_pts_rot      = [for (p = mega_hole_pts) mega_place(p)];
mega_base_hole_pts_rot = [for (p = mega_base_hole_pts) mega_place(p)];
mega_base_pilot_d = set_screw_pilot_d;   // 2.6mm M3 self-tap (bench-checked coupon)

module deck_outline() {
    hull() {
        for (p = mega_hole_pts_rot)      translate(p) circle(r = 11, $fn = 32);
        for (p = mega_base_hole_pts_rot) translate(p) circle(r = 7.5, $fn = 32);
        for (p = deck_leg_pts)           translate(p) circle(r = 14, $fn = 48);
    }
}
module electronics_deck() {
    translate([0, 0, deck_z]) difference() {
        linear_extrude(height = deck_thickness) deck_outline();
        for (p = deck_leg_pts) translate([p[0], p[1], -eps_c]) {
            cylinder(d = m6_clear_d, h = deck_thickness + 2*eps_c, $fn = 24);
            translate([0, 0, deck_thickness - m6_csk_depth + eps_c])
                cylinder(d1 = m6_clear_d, d2 = m6_csk_top_d, h = m6_csk_depth + eps_c, $fn = 48);
        }
        for (p = mega_base_hole_pts_rot) translate([p[0], p[1], -eps_c])
            cylinder(d = mega_base_pilot_d, h = deck_thickness + 2*eps_c, $fn = 24);
    }
}

// ============================================================
// 10. DOOR PATTERN TEST — print and try on the door FIRST
// ============================================================
// Just the 3 bearing bosses on a thin web, same bores as front_plate(),
// with a small arrow on the top edge. Put 2 bearings in each, slide the 3
// printed gear-shafts in from the back, hold it on the door (arrow up) and
// check: (1) bearings press in and stay, (2) shafts slide freely, (3) all 3
// plugs go into their stars at the same time and turn by hand (use the
// gears as knobs). If a plug binds, note which one and which way — the
// dial_* numbers get corrected before the big print.
module dial_pattern_test() {
    difference() {
        union() {
            linear_extrude(height = plate_thickness) hull() {
                for (p = hole_pts) translate(p) circle(d = boss_d + 6, $fn = 64);
                translate([0, max([for (p = hole_pts) p[1]]) + boss_d/2 + 8]) circle(r = 1);
            }
            bearing_bosses();
        }
        bearing_bores();
    }
}

// ============================================================
// 11a. ASSEMBLED VIEW (for checking; dial_unit_assembled.scad calls it)
// ============================================================
// retract: how far the gear-shafts are pushed back (0 = forward stop,
// travel = plug flush with the plate). phase: pinion rotation in degrees;
// the gears turn with it at the right ratio and the right tooth phase,
// so gear-vs-pinion can be checked for overlap at any point in the mesh.
// Dummies (motors, bearings, M3 heads) are plain solids at their real
// size, for interference checks only.
module motor_dummy(i, phase = 0) {
    beta = motor_dir[i] + 180;
    translate([motor_pts[i][0], motor_pts[i][1], 0]) {
        translate([0, 0, motor_face_z]) rotate([0, 0, motor_rot[i]])
            translate([-nema17_body/2, -nema17_body/2, 0]) cube([nema17_body, nema17_body, nema17_can_length]);
        translate([0, 0, motor_face_z - nema17_boss_h]) cylinder(d = nema17_boss_d, h = nema17_boss_h + eps_c, $fn = 48);
        // shaft: round above the flat, D over the 15mm flat, flat in the
        // same orientation as the pinion's D-bore
        translate([0, 0, shaft_tip_z + nema17_flat_len]) cylinder(d = nema17_shaft_d, h = nema17_shaft_len - nema17_flat_len, $fn = 32);
        rotate([0, 0, beta + phase]) rotate([180, 0, 0])
            translate([0, 0, -(shaft_tip_z + nema17_flat_len)])
                linear_extrude(height = nema17_flat_len) intersection() {
                    circle(d = nema17_shaft_d, $fn = 32);
                    translate([-5, -5]) square([10, 5 + nema17_shaft_flat - nema17_shaft_d/2]);
                }
    }
}
module assembled(part = "all", retract = 0, phase = 0) {
    if (part == "all" || part == "front") front_assembly();
    if (part == "all" || part == "sled")  rear_assembly();
    if (part == "all" || part == "deck")  electronics_deck();
    for (i = [0 : 2]) {
        beta = motor_dir[i] + 180;   // direction pinion -> gear
        if (part == "all" || part == str("gearshaft", i))
            translate([hole_pts[i][0], hole_pts[i][1], gear_z1 + retract])
                rotate([0, 0, beta + 180 + 180/gear_teeth - phase*pinion_teeth/gear_teeth])
                    rotate([180, 0, 0]) dial_gear_shaft();
        if (part == "all" || part == str("pinion", i))
            translate([motor_pts[i][0], motor_pts[i][1], cavity_top - 0.5])
                rotate([0, 0, beta + phase]) rotate([180, 0, 0]) motor_pinion();
        if (part == "all" || part == str("motor", i)) motor_dummy(i, phase);
        if (part == "all" || part == str("bearings", i))
            for (k = [0 : bearings_per_shaft - 1])
                translate([hole_pts[i][0], hole_pts[i][1], lip_h + k*bearing_w]) difference() {
                    cylinder(d = bearing_od, h = bearing_w, $fn = 96);
                    translate([0, 0, -eps_c]) cylinder(d = bearing_id, h = bearing_w + 2*eps_c, $fn = 64);
                }
        if (part == "all" || part == str("m3heads", i))
            for (b = motor_bolt_pts[i])
                translate([b[0], b[1], cavity_top + m3_cbore_depth - 3]) cylinder(d = 5.5, h = 3, $fn = 24);
    }
}

// machine-readable layout for cad/tools/dial_layout_check.py
echo(LAYOUT = [
    ["dial_abc", [dial_ab, dial_ac, dial_bc]], ["hole_pts", hole_pts],
    ["motor_dir", motor_dir], ["motor_rot", motor_rot], ["motor_pts", motor_pts],
    ["motor_bolt_pts", motor_bolt_pts], ["joint_pts", joint_pts], ["deck_leg_pts", deck_leg_pts],
    ["mega_base_hole_pts_rot", mega_base_hole_pts_rot], ["mega_hole_pts_rot", mega_hole_pts_rot],
    ["gear", [gear_m, gear_teeth, pinion_teeth, gear_x, pinion_x, gear_pa, gear_backlash, gear_cd]],
    ["gear_tip_r", gear_tip_r], ["pinion_tip_r", pinion_tip_r],
    ["z", [boss_h, gear_z0, gear_z1, pinion_z0, pinion_z1, cavity_top, motor_face_z, shaft_tip_z, deck_z, travel, plug_z0, plug_z1]],
    ["spring", [spring_len_fwd, spring_len_back, spring_pocket_d]], ["pinion_hub_h", pinion_hub_h],
    ["boss_d", boss_d], ["bearing_pocket_d", bearing_pocket_d], ["leg_dia", leg_dia], ["m6_csk_top_d", m6_csk_top_d],
    ["m3_cbore_d", m3_cbore_d], ["boss_recess_d", boss_recess_d], ["front_plate_r", front_plate_r],
    ["magnet_count", len(magnet_pts)]
]);
echo(GEAR_PROFILE = gear_profile(gear_m, gear_teeth, gear_x, gear_pa, gear_backlash));
echo(PINION_PROFILE = gear_profile(gear_m, pinion_teeth, pinion_x, gear_pa, gear_backlash));
echo(GEAR_PROFILE_NOBL = gear_profile(gear_m, gear_teeth, gear_x, gear_pa, 0));
echo(PINION_PROFILE_NOBL = gear_profile(gear_m, pinion_teeth, pinion_x, gear_pa, 0));

// print-ready placements (each part alone, flat face on the bed at z=0) —
// the print_*.scad wrappers call these
module print_front_assembly()   front_assembly();
module print_rear_assembly()    translate([0, 0, -cavity_top]) rear_assembly();
module print_electronics_deck() translate([0, 0, -deck_z]) electronics_deck();
module print_drivetrain() {
    for (i = [0 : 2]) {
        translate([i*36, 0, 0]) dial_gear_shaft();
        translate([i*36, 30, 0]) motor_pinion();
    }
}

// ============================================================
// 11. OUTPUT: everything laid out flat for printing, nothing overlapping.
//     (Assembled view for checking: dial_unit_assembled.scad.)
// ============================================================
bound_r  = front_plate_r + pointer_len;
gap      = 2*bound_r + 20;
show_print_layout = true;
if (show_print_layout) {
front_assembly();
translate([gap, 0, -cavity_top]) rear_assembly();
translate([2*gap, 0, -deck_z]) electronics_deck();
for (i = [0 : 2]) {
    translate([-bound_r - 25, -45 + i*45, 0]) dial_gear_shaft();
    translate([-bound_r - 60, -45 + i*45, 0]) motor_pinion();
}
}

// ============================================================
// PRINT NOTES — see the bottom of docs/housing_decisions.md's v2 entry
// for the assembly order. Short version:
//  - FIRST print dial_pattern_test() + the 3 gear-shafts and try them on
//    the door (see section 10). Only then print the plate and sled.
//  - front_assembly(): door face down (PETG). rear_assembly(): INNER face
//    down (the face with the spring pockets/counterbores), legs up (PETG).
//    electronics_deck(): flat (PETG).
//  - dial_gear_shaft(): gear face down, plug up, PETG-CF (wear part).
//    motor_pinion(): hub down, teeth up, PETG-CF. Turn elephant-foot
//    compensation on for both, or the bottom layer of the teeth binds.
//  - Hardware: 6x 608 bearings, 3x compression springs (<= 8mm OD,
//    ~18-20mm free, solid length < 10mm), 12x M3x8 socket head (motors),
//    optional 3x M3x3/M3x4 GRUB screws for the pinions (never a cap screw —
//    see pinion_round_len), 6x M6 countersunk ~16mm
//    (6mm plate + 10mm engagement, both joints), 4x M3 (Mega base).
// ============================================================
