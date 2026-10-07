// ============================================================
// Printed holder for one 5 x 20 mm glass cartridge fuse (1.6 A T),
// interim hub F1 until the PTC arrives (control/wiring.md, log 2026-10-07).
// 12 V DC, under 0.6 A, 20 AWG wire at each end.
//
// How it works (all contacts metal-to-metal, no solder on the fuse):
//   END A (fixed):  an M3 brass heat-set insert goes through wall A. The
//     fuse's A cap bears on the insert's FRONT face. The wire is clamped on
//     the insert's REAR face (which stands 1mm proud of the plastic) by an
//     M3x6 socket screw + M3 washer: head -> washer -> wire -> brass.
//   END B (sprung): a second M3 insert, NOT heat-set, is a loose brass
//     piston. Its front face bears on the B cap. The B wire is clamped on its
//     rear face by an M3x6 + washer, the same way. A compression spring
//     (QUARKZMAN 0.5 x 7 x 20, one of the 7 spares from the dial-unit pack)
//     pushes on that washer and presses the fuse against end A. The spring
//     carries no current: the wire is clamped to the piston itself.
//   Contact force comes from the spring, so slow creep of the PETG only
//   changes the force a little (spring travel 7mm >> creep).
//   Swap without tools: slide the lid off, push the fuse toward the spring,
//   lift it out. The lid covers every live part.
//
// Frame: x along the fuse (end A at x = 0), z up, fuse axis at y = 0,
// z = axis_z. Printed: body base-down, lid label-face down. No bridges:
// every channel is cut from the top and closed by the lid.
//
// MEASURE BEFORE PRINTING (calipers): insert OD and length (ins_d, ins_l;
// the BOM only says "4.2mm OD, ~5mm"), M3 washer OD/thickness, and the
// spring's coil count (solid length must stay under 11mm). See the asserts.
// ============================================================

part = "assembled";   // "body" | "lid" | "assembled" | dummies for the check: "fuse","insA","screwA","piston","spring"
state = "work";       // "work" (fuse in) | "load" (fuse pushed 2mm toward the spring) | "empty" (no fuse)

eps = 0.05;
$fn = 64;

// ---- bought parts (nominal; confirm the starred ones) ----
fuse_d   = 5.2;   // 5 x 20: caps up to ~5.2
fuse_l   = 20;
ins_d    = 4.2;   // * M3 heat-set insert OD
ins_l    = 5.0;   // * insert length
ins_hole = 4.0;   // heat-set hole (slightly under the knurl OD) — adjust if the insert goes in too loose/tight
wsh_d    = 7.0;   // * M3 washer DIN 125
wsh_t    = 0.5;
head_d   = 5.5;   // M3 DIN 912 socket head
head_k   = 3.0;
scr_l    = 6;     // M3x6 (shortest in the Taiss kit)
wire_t   = 1.0;   // clamped 20 AWG conductor (0.81mm) + a little
wire_od  = 2.2;   // 20 AWG insulated, slot width
spr_od   = 7.0;  spr_free = 20;  spr_work = 13;  spr_solid_max = 10;

assert(scr_l <= wsh_t + wire_t + ins_l, "screw would poke out of the insert's front face and push the fuse");
assert(scr_l - wsh_t - wire_t >= 3.5, "screw engages under 3.5mm of thread");

// ---- layout (x) ----
wall      = 2.0;              // side and end walls
endA_t    = 2.0;
compA_l   = 7.0;              // A clamp: insert stub 1 + wire 1 + washer 0.5 + head 3 + 1.5 room
wallA_t   = ins_l - 1.0;      // insert front flush with the cradle face, rear 1mm proud
xA        = endA_t + compA_l + wallA_t;          // A contact face = 13
load_push = 2.0;                                  // how far you push the fuse to lift it out
cradle_end = xA + fuse_l + load_push + 0.5;       // 35.5
xf_work   = xA + fuse_l;                          // piston front, fuse in
xf_load   = xf_work + load_push;
xf_empty  = cradle_end - (ins_l + wire_t);        // washer front stops on the 7.6 -> 5.6 step
spr_ch_d  = spr_od + 0.6;                          // 7.6
backB_x   = xf_work + ins_l + wire_t + wsh_t + spr_work;   // spring seat
total_l   = backB_x + wall;

function xf(s) = s == "load" ? xf_load : s == "empty" ? xf_empty : xf_work;
function spring_len(s) = backB_x - (xf(s) + ins_l + wire_t + wsh_t);
assert(spring_len("load") > spr_solid_max + 0.5, "spring near solid when loading");
assert(spring_len("empty") < spr_free, "spring has no preload with the fuse out");
echo(SPRING_EMPTY_WORK_LOAD = [spring_len("empty"), spring_len("work"), spring_len("load")],
     TOTAL_L = total_l);

// ---- section (y, z) ----
floor_t  = 1.4;
axis_z   = floor_t + spr_ch_d/2;            // 5.2
inner_top = axis_z + spr_ch_d/2 + 0.4;       // lid underside
lid_t    = 1.6;
grv_d    = 0.8;   grv_c = 0.12;              // lid groove depth, clearance
grv_z0   = inner_top;  grv_z1 = inner_top + lid_t + 2*grv_c;
body_h   = grv_z1 + 1.0;
route_y0 = spr_ch_d/2 + 1.2;                 // wire groove, +y side
route_y1 = route_y0 + wire_od + 0.2;
half_w   = route_y1 + wall;
tab_w    = 5;   tab_t = 2.4;

module ucut(x0, x1, d, ztop = 99) {  // U channel along x, round bottom at the axis, open to the top
    translate([x0, 0, axis_z]) rotate([0, 90, 0]) cylinder(d = d, h = x1 - x0);
    translate([x0, -d/2, axis_z]) cube([x1 - x0, d, ztop]);
}

module body() {
    difference() {
        union() {
            translate([0, -half_w, 0]) cube([total_l, 2*half_w, body_h]);
            for (x = [8, total_l - 8]) for (sd = [-1, 1])    // mounting tabs (M3 screw or 3mm zip tie)
                translate([x - 4, sd > 0 ? half_w - eps : -half_w - tab_w + eps, 0]) cube([8, tab_w, tab_t]);
        }
        for (x = [8, total_l - 8]) for (sd = [-1, 1])
            translate([x, sd*(half_w + tab_w/2), -1]) cylinder(d = 3.2, h = tab_t + 2, $fn = 24);
        // compartment A (clamp), widened to +y for the wire
        translate([endA_t, -wsh_d/2 - 0.6, axis_z - wsh_d/2 - 0.6]) cube([compA_l, wsh_d/2 + 0.6 + route_y1, 99]);
        // wall A: heat-set hole
        translate([endA_t + compA_l - eps, 0, axis_z]) rotate([0, 90, 0]) cylinder(d = ins_hole, h = wallA_t + 2*eps, $fn = 32);
        // end A: hex-key access on the axis, wire notch on +y
        translate([-eps, 0, axis_z]) rotate([0, 90, 0]) cylinder(d = 3.2, h = endA_t + 2*eps, $fn = 24);
        translate([-eps, route_y0, axis_z - wire_od/2]) cube([endA_t + 2*eps, route_y1 - route_y0, 99]);
        // cradle
        ucut(xA - eps, cradle_end, fuse_d + 0.4);
        // piston / washer / spring channel
        ucut(cradle_end - eps, backB_x, spr_ch_d);
        // wire B: side slot over the clamp's travel, then a groove to end B
        translate([xf_empty + ins_l - 1, 0, axis_z - wire_od/2]) cube([xf_load + ins_l + wire_t + 1 - (xf_empty + ins_l - 1), route_y1, 99]);
        translate([xf_empty + ins_l - 1, route_y0, axis_z - wire_od/2]) cube([total_l, route_y1 - route_y0, 99]);
        // lid: open the top over the whole inside, grooves in the long walls, end A lowered
        translate([-eps, -(half_w - wall), inner_top]) cube([backB_x + eps, 2*(half_w - wall), 99]);
        translate([-eps, -(half_w - wall + grv_d), grv_z0]) cube([backB_x + eps, 2*(half_w - wall + grv_d), grv_z1 - grv_z0]);
    }
}

lid_w = 2*(half_w - wall + grv_d - grv_c);
lid_l = backB_x - 0.3;
lid_z = grv_z0 + grv_c;          // lid underside when in place
flap_t = 1.2;
module lid() {
    // Slides in from end A until its end flap meets the body's end face. The
    // flap covers the hex-key hole (the A screw head behind it is live) and is
    // the grip for sliding the lid out. It stops short of the wire notch.
    difference() {
        union() {
            translate([0, -lid_w/2, 0]) cube([lid_l, lid_w, lid_t]);
            // flap hangs 0.1 clear of the end face (lid sits at x = 0.1); joined at lid level, above end wall A
            translate([-flap_t - 0.2, -lid_w/2, -(lid_z - 1)]) cube([flap_t, route_y0 - 0.4 + lid_w/2, lid_z - 1 + lid_t]);
            translate([-0.2 - eps, -lid_w/2, 0]) cube([0.2 + 2*eps, route_y0 - 0.4 + lid_w/2, lid_t]);
        }
        translate([lid_l/2, 0, lid_t - 0.6]) linear_extrude(1)
            text("1.6 A T", size = 5, halign = "center", valign = "center", font = "Liberation Sans:style=Bold");
    }
}

// ---- dummies (for the check script and the assembled view) ----
module fuse_dummy(s) { if (s != "empty") translate([xA + (s == "load" ? load_push : 0), 0, axis_z]) rotate([0, 90, 0]) cylinder(d = fuse_d, h = fuse_l); }
module insA_dummy() { translate([xA - ins_l, 0, axis_z]) rotate([0, 90, 0]) difference() { cylinder(d = ins_hole, h = ins_l, $fn = 32); translate([0,0,-eps]) cylinder(d = 3, h = ins_l + 2*eps); } }
module screwA_dummy() {  // head + washer + wire layer, shank inside the insert
    x1 = xA - ins_l;  // insert rear face
    translate([x1 - wire_t, 0, axis_z]) rotate([0, 90, 0]) cylinder(d = 4.8, h = wire_t);      // wire wrapped round the 3mm shank
    translate([x1 - wire_t - wsh_t, 0, axis_z]) rotate([0, 90, 0]) cylinder(d = wsh_d, h = wsh_t);
    translate([x1 - wire_t - wsh_t - head_k, 0, axis_z]) rotate([0, 90, 0]) cylinder(d = head_d, h = head_k);
}
module piston_dummy(s) {
    x0 = xf(s);
    translate([x0, 0, axis_z]) rotate([0, 90, 0]) cylinder(d = ins_d, h = ins_l);
    translate([x0 + ins_l, 0, axis_z]) rotate([0, 90, 0]) cylinder(d = 4.8, h = wire_t);
    translate([x0 + ins_l + wire_t, 0, axis_z]) rotate([0, 90, 0]) cylinder(d = wsh_d, h = wsh_t);
    translate([x0 + ins_l + wire_t + wsh_t, 0, axis_z]) rotate([0, 90, 0]) cylinder(d = head_d, h = head_k);
}
module spring_dummy(s) {
    x0 = xf(s) + ins_l + wire_t + wsh_t;
    translate([x0, 0, axis_z]) rotate([0, 90, 0]) difference() { cylinder(d = spr_od, h = backB_x - x0); translate([0,0,-eps]) cylinder(d = spr_od - 1, h = 99); }
}
module lid_in_place() { translate([0.1, 0, lid_z]) lid(); }

module assembled(s, with_lid = true) {
    color("gold", 0.9) body();
    if (with_lid) color("white", 0.6) lid_in_place();
    color("silver") { fuse_dummy(s); insA_dummy(); screwA_dummy(); piston_dummy(s); }
    color("gray") spring_dummy(s);
}

if (part == "body") body();
else if (part == "lid") lid();
else if (part == "lid_placed") lid_in_place();
else if (part == "fuse") fuse_dummy(state);
else if (part == "insA") insA_dummy();
else if (part == "screwA") screwA_dummy();
else if (part == "piston") piston_dummy(state);
else if (part == "spring") spring_dummy(state);
else if (part == "open") assembled(state, false);
else assembled(state);
