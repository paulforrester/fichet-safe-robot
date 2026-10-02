// ============================================================
// Standoff-leg SELF-TAP fit test (temporary hardware), v0.1
// Throwaway PLA test coupons — NOT part of the robot itself. Purpose:
// decide, on the bench today, which on-hand screw self-taps into the
// standoff legs' EXISTING 4.2mm x 6mm blind bore (insert_hole_d /
// insert_hole_depth in dial_unit_housing.scad) well enough for a
// one-time test assembly, while the real M3x8 + brass heat-set-insert
// hardware is still on order — see docs/housing_decisions.md's
// "1. Temporary fastening for today" entry, which this follows up on.
//
// ON HAND (per the two assortment-box labels): both boxes are 1080pcs,
// same M3/M4/M5/M6 length breakdown —
//   black label = countersunk hexagon-socket-head screws
//   red label   = Phillips pan/round-head screws
//
// M3 and M4 are deliberately NOT tested here: the bore is 4.2mm, which
// is a clearance fit for M3 (3mm) and still slightly oversize for M4
// (4mm) — neither has enough interference to cut its own thread, they'd
// just rattle loosely. Only M5 (5mm) and M6 (6mm) are meaningfully
// larger than the hole, so those are the two sizes worth test-fitting,
// in both head styles — 4 combinations total:
//   M5 pan | M5 countersunk | M6 pan | M6 countersunk
//
// Each combination is printed as TWO small parts that bolt together
// the same way the real joint does:
//   - a stand-in LEG: just leg_dia and the real insert_hole_d/depth
//     bore, nothing else (short stub, not a full-height leg)
//   - a stand-in CAP: stands in for the motor plate — a clearance hole
//     sized to that screw plus a head pocket sized for that head style
// Thread the screw through the cap into the leg BY HAND (not a power
// driver — see PRINT NOTES) and see which combination actually draws
// tight without splitting the leg.
//
// This does NOT replace the real M3x8 + heat-set-insert joint —
// whichever screw wins here is for today's fit-check / test assembly
// only. Swap back to the real hardware before the motors are ever
// powered and cycled (see docs/housing_decisions.md).
//
// Kept in sync with dial_unit_housing.scad BY HAND, not shared code:
// leg_dia, insert_hole_d, insert_hole_depth and motor_plate_h are
// plain top-level variables over there, not modules, so there's
// nothing clean to `include`/`use` for just these — if those change in
// dial_unit_housing.scad, update the copies below too.
// ============================================================

include <common_mounts.scad>
$fn = 48;

// ---- copied from dial_unit_housing.scad (see header note) ----
leg_dia           = 12;   // mm, real standoff leg diameter
insert_hole_d     = 4.2;  // mm, real blind-bore diameter (sized for the M3 insert's OD)
insert_hole_depth = 6;    // mm, real blind-bore depth

// ---- this test's own geometry (not shared with the real design) ----
leg_stub_h    = 10;  // mm, tall enough for the 6mm bore + a 4mm solid floor beneath it
cap_dia       = 18;  // mm, roomy enough for the M6 countersunk pocket (14mm) with wall to spare
cap_thickness = 8;   // mm — deliberately thicker than the real 6mm motor plate. A single
                      // uniform thickness that gives every head style room to seat without a
                      // paper-thin floor; what's actually being tested (self-tap bite and
                      // whether the leg splits) happens in the leg, not in this cap.

// ---- per-screw-size dimensions ----
// Clearance holes: nominal + 0.4mm, same convention as dial_unit_housing.scad's m3_clear_d.
// Head pockets: ISO 7045 (pan) / ISO 10642 (countersunk hex-socket) catalog head
// diameters/heights, checked against current published tables rather than estimated,
// plus ~0.5mm margin so the real screw (which may not exactly match either standard —
// these are generic assortment-box screws) still seats without binding.
m5_clear_d = 5.4;
m6_clear_d = 6.4;

m5_pan_pocket_d = 10.0; m5_pan_pocket_depth = 4.8; // ISO 7045 M5: dk 9.5mm, k 3.7mm
m6_pan_pocket_d = 12.5; m6_pan_pocket_depth = 5.6; // ISO 7045 M6: dk 12.0mm, k 4.6mm

m5_csk_top_d = 11.7; // ISO 10642 M5 dk(max) 11.2mm + margin
m6_csk_top_d = 14.0; // ISO 10642 M6 dk(max) 13.44mm + margin
// countersink pocket depth derived from a 90-degree cone: half the
// difference between the top (head) diameter and the clearance-hole
// diameter it tapers down to.
m5_csk_pocket_depth = (m5_csk_top_d - m5_clear_d) / 2; // ~3.15mm
m6_csk_pocket_depth = (m6_csk_top_d - m6_clear_d) / 2; // ~3.8mm

// ---- ID tag: a small flat pad fused to the side of each part, with
// the combo name recessed into its top face — same recessed-engraving
// convention as tube_socket_test_key.scad's engraving() (no bridging/
// overhang, nothing proud to catch). Kept OFF the parts under test
// (the leg's bore wall, the cap's pocket) so labeling can't skew the
// fit/crack result. Both parts here print flat as modeled — no 180
// degree flip needed, so (unlike the test key) no mirror() on the text.
label_size  = 2.6;
label_depth = 0.6;
tag_w = 12; tag_l = 9; tag_h = 2.4;

module id_tag(label_text, attach_r) {
    difference() {
        translate([-tag_w/2, attach_r - eps_c, 0])
            cube([tag_w, tag_l, tag_h]);
        translate([0, attach_r - eps_c + tag_l/2, tag_h - label_depth])
            linear_extrude(height = label_depth + eps_c)
                text(label_text, size = label_size, halign = "center", valign = "center",
                     font = "Liberation Sans:style=Bold");
    }
}

// Stand-in leg: exactly the real bore, nothing else.
module leg_stub(label_text) {
    union() {
        difference() {
            cylinder(d = leg_dia, h = leg_stub_h, $fn = 32);
            translate([0, 0, leg_stub_h - insert_hole_depth])
                cylinder(d = insert_hole_d, h = insert_hole_depth + eps_c, $fn = 24);
        }
        id_tag(label_text, leg_dia / 2);
    }
}

// Stand-in cap: clearance hole + a head pocket, either a flat
// cylindrical counterbore (pan/round head) or a 90-degree conical
// countersink (countersunk head).
module cap_plate(label_text, clear_d, pocket_d, pocket_depth, countersink) {
    union() {
        difference() {
            cylinder(d = cap_dia, h = cap_thickness, $fn = 48);
            translate([0, 0, -eps_c])
                cylinder(d = clear_d, h = cap_thickness + 2 * eps_c, $fn = 32);
            translate([0, 0, cap_thickness - pocket_depth])
                if (countersink)
                    cylinder(d1 = clear_d, d2 = pocket_d, h = pocket_depth + eps_c, $fn = 48);
                else
                    cylinder(d = pocket_d, h = pocket_depth + eps_c, $fn = 48);
        }
        id_tag(label_text, cap_dia / 2);
    }
}

// ---- output: 4 leg+cap pairs, one per combination being tested ----
// [label, clearance hole dia, pocket dia (or cone top dia), pocket depth, is_countersink]
combos = [
    ["M5-PAN", m5_clear_d, m5_pan_pocket_d, m5_pan_pocket_depth, false],
    ["M5-CSK", m5_clear_d, m5_csk_top_d,    m5_csk_pocket_depth, true],
    ["M6-PAN", m6_clear_d, m6_pan_pocket_d, m6_pan_pocket_depth, false],
    ["M6-CSK", m6_clear_d, m6_csk_top_d,    m6_csk_pocket_depth, true],
];

combo_spacing = 30; // mm, x-distance between combo groups
row_spacing   = 30; // mm, y-distance between a group's leg and its cap

for (i = [0 : len(combos) - 1]) {
    c = combos[i];
    translate([i * combo_spacing, 0, 0])
        leg_stub(c[0]);
    translate([i * combo_spacing, row_spacing, 0])
        cap_plate(c[0], c[1], c[2], c[3], c[4]);
}

// ============================================================
// PRINT NOTES:
//  - Basic PLA, as asked — this is a disposable fit-check, not a
//    load-bearing part, so PLA's lower heat resistance/toughness than
//    PETG doesn't matter here.
//  - Both leg stubs and cap plates print flat exactly as modeled (flat
//    bottom down, bore/pocket opening up) — no slicer rotation needed.
//  - Thread each screw through its matching cap into its matching leg
//    BY HAND, not a power driver. Same caution as the real self-tap
//    guidance already given: the wall around the 4.2mm bore is only
//    ~3.9mm of plastic (leg_dia 12mm, bore 4.2mm, centered) — a power
//    driver can split it before you'd feel it going wrong by hand.
//  - What to look for: does it draw the cap down snug against the leg
//    (actually clamping, not just spinning in loosely), and does the
//    leg wall crack or bulge? M6 is the more aggressive of the two —
//    expect it to bite harder but also carry the higher split risk;
//    M5 is the gentler test, closer to the "#10-#12 wood screw" size
//    already recommended for this hole.
//  - Whichever wins, it's for TODAY's test assembly only. Reprint with
//    the real M3x8 DIN 912 + M3 brass heat-set insert (4.2mm OD, ~5mm
//    length) before running the motors under power — see
//    docs/housing_decisions.md.
// ============================================================
