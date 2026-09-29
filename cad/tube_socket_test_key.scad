// ============================================================
// Fichet-Bauche "Complice" safe — tube-socket TEST key (v0.4)
// First-pass FIT-TEST print. This is not the final tool — its job
// is to tell us, cheaply, whether the measured envelope and tooth
// geometry are in the right ballpark before we commit to a real
// coupler design (motor shaft interface, longer plug, etc).
// ============================================================
//
// TERMINOLOGY (agreed on with Paul, see tooth_terms_diagram.png):
//   WIDTH  — tangential thickness of a tooth (side-to-side). Constant
//            root-to-tip.
//   HEIGHT — radial extent of a tooth, root circle to tip circle.
//   DEPTH  — axial length the tooth reaches into the socket (plug_len).
//
// v0.2 -> v0.3: HEIGHT was previously DERIVED as (tip_dia - root_dia)/2
// from the two directly-measured diameters, giving ~1.4mm — too shallow,
// left rotational play. Made HEIGHT a directly-settable parameter, with
// root_dia computed FROM it (key_tip_dia held fixed at 7.73mm, the
// dimension that governs bore fit and was already working — only the
// root is adjusted, deepening the valley rather than growing the
// envelope). Tested 1.65 / 1.70 / 1.75mm side by side: 1.75mm was the
// winner — dials click reliably.
//
// v0.3 -> v0.4: 1.75mm height still had play. Re-measured WIDTH on the
// real key with calipers: 1.04-1.06mm, not the 1.0mm used so far — so
// WIDTH (tangential), not just height, was undersized. Both are now
// locked in from this round's results: HEIGHT = 1.75mm (the v0.3
// winner), WIDTH = 1.04mm (low end of the new caliper range — the
// closer starting point; if there's still play, 1.06mm is the next
// step up). Like width before it, height is printed with the full
// fit_clearance subtracted (radial/diametral clearance, unchanged at
// 0.35mm); width is still printed at the full measured value with NO
// clearance subtracted, consistent with every round so far.
//
// WHAT'S MEASURED, directly off the real key with calipers:
//   - 8 teeth, evenly spaced 45 deg apart
//   - Tip-to-tip (major) diameter: 7.73 mm
//   - Tooth width: 1.04-1.06 mm, constant/parallel-sided — NOT tapered
//   - Tooth depth (axial, pre-taper section): 5 mm
//
// WHAT'S BEING TUNED BY TEST PRINT:
//   - Tooth height (radial): 1.65 / 1.70 / 1.75mm tested -> 1.75mm won.
//   - Tooth width (tangential): now 1.04mm, up from 1.0mm.
//   This print is labeled on the bottom of the handle with both values,
//   one per line ("1.75" / "1.04"), so it's unambiguous on the bench.
//
// HOW TO USE THIS PRINT:
//   1. Print in PETG (see notes at bottom of file).
//   2. Try it in the tube sockets. Looking for: dials click reliably
//      AND minimal rotational play before you feel the teeth engage.
//   3. Report back how it feels. If still loose, width is the next
//      thing to bump (1.06mm), since height already won its round.
// ============================================================

// ---- measured, directly off the real key with calipers -----------
tooth_count  = 8;
key_tip_dia  = 7.73;  // mm — max diameter across two opposing tooth tips (HEIGHT term: tip circle)
plug_len     = 5.0;   // mm — DEPTH: the key's measured straight (pre-taper) section

// ---- HEIGHT and WIDTH: the two tuning parameters -------------------
// Top-level so either can be overridden from the command line, e.g.:
//   openscad -D "tooth_height=1.75" -D "tooth_width=1.06" -o out.stl tube_socket_test_key.scad
tooth_height = 2.00;  // mm, radial extent of a tooth, root circle -> tip circle — LOCKED IN, see docs/decisions.md
tooth_width  = 1.04;  // mm, constant tangential WIDTH of each tooth — LOCKED IN, see docs/decisions.md
engrave_lines = ["2.00", "1.04"]; // label engraved on the bottom of the handle, one value per line

// key_root_dia is DERIVED from tip + height (see v0.2 -> v0.3 note above).
key_root_dia = key_tip_dia - 2 * tooth_height;

// ---- fit tuning ----------------------------------------------------
fit_clearance = 0.35; // mm, total diametral (radial) clearance — unchanged, this dimension was already close

// ---- handle geometry -----------------------------------------------
// Sized for hand-testing: long enough to hold and turn with your
// fingers, clear of the door hardware around the socket.
collar_dia = 11.75;  // mm — measured recess ~12mm, sized down for clearance
collar_len = 2;
handle_dia = 16;                    // across-flats-ish grip size for the hex handle
handle_len = 32;                    // hand-turning length

$fn = 96;

// Single closed polygon tracing the whole star outline (root-left,
// tip-left, tip-right, root-right, repeat). Deliberately NOT built as
// a union of per-tooth wedges sharing a center point — that
// degenerate shared vertex silently corrupted the CGAL boolean when
// unioned with the collar/handle cylinders (looked fine in the
// preview, but the exported STL was missing the plug entirely). This
// form renders correctly through to STL.
//
// Each tooth is built with its OWN half-width angle at the tip and at
// the root, computed from the same linear WIDTH (chord width) at
// each radius — that keeps the tooth's actual width constant/
// parallel-sided as measured, instead of tapering to a point. Because
// the root sits at a smaller radius than the tip, the same linear
// width subtends a slightly bigger angle there, so the tooth flares a
// hair wider at its base rather than narrowing.
function tooth_profile(r_tip, r_root, teeth, width) =
    let(pitch = 360 / teeth,
        half_w_tip  = asin(min(1, (width/2) / r_tip)),
        half_w_root = asin(min(1, (width/2) / r_root)))
    [for (i = [0 : teeth - 1])
        each [
            [r_root * cos(i*pitch - half_w_root), r_root * sin(i*pitch - half_w_root)],
            [r_tip  * cos(i*pitch - half_w_tip),  r_tip  * sin(i*pitch - half_w_tip)],
            [r_tip  * cos(i*pitch + half_w_tip),  r_tip  * sin(i*pitch + half_w_tip)],
            [r_root * cos(i*pitch + half_w_root), r_root * sin(i*pitch + half_w_root)],
        ]
    ];

module spline_plug(tip_d, root_d, teeth, length, width) {
    linear_extrude(height = length, convexity = 10)
        polygon(points = tooth_profile(tip_d/2, root_d/2, teeth, width));
}

// small overlap between stacked sections so the union produces one
// closed manifold solid instead of three coincident-face volumes
eps = 0.1;

// Engraved (recessed) into the flat bottom face of the hex handle
// (z=0 in this module's local frame) — that face is the free end of
// the handle, not anything that touches the safe. Recessed rather
// than raised so it doesn't need bridging/overhang support and
// doesn't add anything proud that could rub on your hand. Mirrored in
// X because text() draws for a viewer looking down the +Z axis (from
// above); this face points the other way (-Z, down), so without the
// mirror it would print backwards to anyone reading it from below.
// Two lines now (height on top, width on bottom) instead of one —
// sized down a bit from the single-line version so both fit inside
// the hex face with margin.
engrave_size    = 3.3;   // mm, text height per line
engrave_spacing = 4.0;   // mm, vertical distance between line centers
engrave_depth   = 0.6;   // mm, deep enough to read, shallow enough not to weaken the handle

module engraving(lines) {
    n = len(lines);
    for (i = [0 : n - 1])
        translate([0, (n - 1) / 2 * engrave_spacing - i * engrave_spacing, -0.1])
            linear_extrude(height = engrave_depth + 0.1)
                mirror([1, 0, 0])
                    text(lines[i], size = engrave_size, halign = "center", valign = "center",
                         font = "Liberation Sans:style=Bold");
}

// tool(): builds one test key. th = tooth HEIGHT (radial, mm), tw =
// tooth WIDTH (tangential, mm), lines = engrave text lines on the
// bottom of the handle. Defaults come from the top-level globals above
// (so a plain CLI -D override still works for a single-key export);
// pass explicit values to get multiple different keys out of one file.
module tool(th = tooth_height, tw = tooth_width, lines = engrave_lines) {
    root_dia_local = (key_tip_dia - 2 * th) - fit_clearance;
    tip_dia_local  = key_tip_dia - fit_clearance;

    difference() {
        union() {
            // hex handle for hand-turning now, wrench-turning later
            cylinder(d = handle_dia, h = handle_len, $fn = 6);
            // registration collar — shoulder/stop, sits against the door
            // face once the plug is fully inserted
            translate([0, 0, handle_len - eps])
                cylinder(d = collar_dia, h = collar_len + eps);
            // spline plug (the part that goes into the socket) — leads,
            // at the top/free end
            translate([0, 0, handle_len + collar_len - eps])
                spline_plug(tip_dia_local, root_dia_local, tooth_count, plug_len + eps, tw);
        }
        engraving(lines);
    }
}

tool();

// ============================================================
// PRINT NOTES (PETG):
//  - In this file the plug is at the TOP (z=max) and the handle at
//    the BOTTOM (z=0) — that's just how the model reads in a viewer.
//    For printing, rotate the part 180° in your slicer so the plug
//    end faces DOWN onto the plate (flat collar face down) — that's
//    what gives the tooth tips clean vertical walls instead of
//    overhangs, regardless of which way the source file is built.
//  - 0.2mm layers, 3-4 perimeters — this part is all about the walls,
//    not infill; 20% infill is plenty.
//  - PETG oozes/strings more than PLA and tends to print very slightly
//    OVER-size on fine features (stringing fills small gaps). If this
//    is still loose, try width=1.06mm next (the top of the measured
//    range) before touching height again.
//  - First-layer squish can fatten the collar's bottom edge — a light
//    single pass with a deburring tool/knife on the collar edge after
//    printing is normal and fine.
// ============================================================
