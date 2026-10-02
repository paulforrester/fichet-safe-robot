// ============================================================
// PRINTED internal thread fit test, v0.1
// Paul's actual ask: not self-tapping (see standoff_screw_fit_test.scad
// for that one — still useful, just a different question) but whether
// a REAL ISO-profile thread, modeled and printed directly into the
// hole, can be threaded into with an ordinary M5/M6 screw with no
// self-tapping and no heat-set insert at all.
//
// Only M5 and M6 are tested, same reasoning as the earlier research in
// docs/housing_decisions.md: a 0.4mm nozzle is right at (M3/M4) or past
// (M5/M6+) the size where directly-printed threads are commonly viable;
// M3/M4 were the ones specifically called out as needing inserts
// instead, so they're not worth a print here.
//
// THREAD PROFILE: standard ISO 60-degree basic profile (verified
// against the ISO/Wikipedia formulas rather than guessed):
//   H (height of the fundamental sharp-V triangle) = 0.8660254 * pitch
//   major-to-minor diameter difference = 1.0825318 * pitch
//   (basic truncated profile: root flat = pitch/4, crest flat =
//   pitch/8, 30-degree flanks between them — derived from H above,
//   not separately looked up)
// This is the TOOL shape (sized at the real screw's nominal diameter,
// plus a clearance sweep — see below) that gets SUBTRACTED from each
// test block, the same way a tap cuts a thread into a drilled hole:
// the void left behind is shaped like the (slightly oversized) screw,
// so the screw can thread into it.
//
// CLEARANCE SWEEP: FDM prints routinely come out a bit undersized at
// small internal features (over-extrusion, rounded inside corners), so
// a hole cut at the exact textbook ISO profile is likely to come out
// too tight for a real screw to even start. Rather than guess the
// right oversize for Paul's printer/filament, this sweeps 3 values per
// size — same approach as tube_socket_test_key_set.scad's tooth-height
// sweep — and lets the bench decide:
//   +0.0mm (nominal profile, as a baseline — probably too tight)
//   +0.2mm
//   +0.4mm
// (diametral, i.e. added to both major and minor diameter equally)
//
// Each block is a short through-hole cylinder, generously walled (the
// goal here is to find out whether the THREAD holds, not to also
// retest wall-splitting risk — that question belongs to
// standoff_screw_fit_test.scad). Thread the real screw in BY HAND from
// either face; expect the first turn or two to need a bit of a
// wiggle/back-off to find its start, same as starting into any tapped
// hole or nut.
// ============================================================

include <common_mounts.scad>
$fn = 32; // kept modest — 6 copies of a twisted-extrude thread boolean
          // against a cylinder is CGAL-expensive; see slices note below

eps_thread = 0.1; // radial overlap between the helical ridge and its
                   // core cylinder so they fuse into one manifold
                   // instead of two coincident-face volumes (same
                   // trick as eps_c elsewhere in this project) —
                   // separate name from eps_c since it's used inside
                   // the thread module at a different, finer scale.

// The cutting tool: a solid core cylinder (at the thread's minor
// diameter) plus a helical ridge wound around it out to the major
// diameter, built by sweeping one pitch-period of the truncated ISO
// profile with linear_extrude(twist=...) — verified by rendering in
// isolation and checking with trimesh that it comes out as a single
// watertight, connected solid before being used as a subtraction tool
// here (see chat history; not re-derived from scratch per revision).
module male_thread_tool(d, pitch, length, clearance = 0) {
    major_r = d / 2 + clearance / 2;
    minor_r = (d - 1.0825318 * pitch) / 2 + clearance / 2;
    root_r  = minor_r - eps_thread; // ridge's root dips slightly into the core
    rf = pitch / 4;      // root flat width
    cf = pitch / 8;      // crest flat width
    fr = 5 * pitch / 16; // flank z-run
    profile = [
        [root_r, -rf / 2],
        [root_r,  rf / 2],
        [major_r, rf / 2 + fr],
        [major_r, rf / 2 + fr + cf],
        [root_r,  rf / 2 + fr + cf + fr],
    ];
    n_turns = length / pitch;
    union() {
        cylinder(r = minor_r, h = length, $fn = 32);
        // slices controls twist resolution — enough per turn to keep
        // the trapezoid profile crisp (confirmed by render/trimesh
        // check) without the render time blowing up across 6 copies
        // of a 12-15 turn thread
        linear_extrude(height = length, twist = 360 * n_turns,
                        slices = max(16, round(16 * n_turns)), convexity = 10)
            polygon(profile);
    }
}

// ---- test block geometry ----
block_h = 12; // mm, through-hole length — 15 turns at M5x0.8, 12 at M6x1.0

// label: a single-line recessed engraving on the flat top annulus
// around the hole — the annulus is only ~5-6mm wide radially (block
// radius minus the thread's major radius), too narrow to stack
// multiple lines like tube_socket_test_key.scad does on its much
// bigger handle face, so both values go on one line instead
// ("M5 +0.2"). Explicit strings for the clearance values, not str() on
// the number, for the same reason noted in
// tube_socket_test_key_set.scad: str() drops trailing zeros
// (str(0.20) -> "0.2"), which would make the 0.0/0.2/0.4 columns
// inconsistent-looking.
label_size  = 2.2;
label_depth = 0.6;

module thread_label(line, r_offset) {
    translate([0, r_offset, block_h - label_depth + eps_thread])
        linear_extrude(height = label_depth)
            text(line, size = label_size, halign = "center", valign = "center",
                 font = "Liberation Sans:style=Bold");
}

module threaded_test_block(line, d, pitch, clearance, block_dia) {
    difference() {
        cylinder(d = block_dia, h = block_h, $fn = 48);
        translate([0, 0, -eps_thread])
            male_thread_tool(d, pitch, block_h + 2 * eps_thread, clearance);
        // label sits at the midpoint of the flat annulus between the
        // hole's (clearance-widened) major radius and the block's
        // outer edge, well clear of both
        thread_label(line, (d / 2 + clearance / 2 + block_dia / 2) / 2);
    }
}

// ---- output: 2 sizes x 3 clearance values ----
// [size label, nominal dia, pitch, block outer dia]
sizes = [
    ["M5x0.8", 5, 0.8, 16],
    ["M6x1.0", 6, 1.0, 18],
];
clearances = [0.0, 0.2, 0.4];
clearance_labels = ["+0.0", "+0.2", "+0.4"]; // explicit strings, see note above

col_spacing = 24; // mm between clearance columns
row_spacing = 24; // mm between the M5 and M6 rows

for (r = [0 : len(sizes) - 1]) {
    s = sizes[r];
    for (c = [0 : len(clearances) - 1]) {
        cl = clearances[c];
        line = str(s[0], " ", clearance_labels[c]);
        translate([c * col_spacing, r * row_spacing, 0])
            threaded_test_block(line, s[1], s[2], cl, s[3]);
    }
}

// ============================================================
// PRINT NOTES:
//  - Print upright exactly as modeled (hole axis vertical, matching
//    the printer's Z) — the favorable orientation for printed threads,
//    same reasoning as the standoffs' vertical screw holes discussed
//    earlier; this is NOT the radial/sideways case that was steered
//    away from for the set-screw hole.
//  - 0.2mm layers. Slow down for these — a lower print speed through
//    the threaded region generally prints small threads more
//    accurately than rushing it.
//  - Test with a real M5x0.8 / M6x1.0 screw (coarse ISO metric, the
//    common hardware-store pitch for each size) by hand. Expect the
//    first turn or two to need a small back-and-forth wiggle to find
//    the start, same as threading into any nut or tapped hole.
//  - What to look for across the three clearance columns: +0.0 is
//    likely too tight to even start: if even +0.4 is still too tight,
//    the oversize needs to go further than this sweep covers (rerun
//    with larger values, e.g. +0.5 / +0.6); if +0.2 or +0.4 threads in
//    cleanly and holds without stripping, that clearance is the one to
//    carry into a real part.
//  - Whichever clearance wins here is a printer/filament-specific
//    calibration number, not a universal constant — worth re-checking
//    if the nozzle, filament, or slicer settings change later.
// ============================================================
