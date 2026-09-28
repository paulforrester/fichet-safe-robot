// Continuing the tooth-HEIGHT sweep: 1.75/1.04mm still had a little
// play, and taller teeth have been trending tighter each round
// (1.65 -> 1.70 -> 1.75), so this plate pushes further: 1.80 / 1.85 /
// 1.90 / 1.95 / 2.00mm, all at WIDTH = 1.04mm (confirmed fine, not
// changed). Each key engraved on the bottom of its handle, height on
// line 1 / width on line 2, same as the 1.75-1.04 key.
//
// See cad/tube_socket_test_key.scad for the geometry, and
// docs/decisions.md for the full round-by-round history.
use <tube_socket_test_key.scad>

spacing = 22; // mm, center-to-center — clears the 16mm hex handles with margin

// Explicit label strings rather than str(height) — OpenSCAD's str()
// drops trailing zeros (str(1.80) -> "1.8", str(2.00) -> "2"), which
// would break the two-decimal-place labeling convention used so far.
heights = [1.80, 1.85, 1.90, 1.95, 2.00];
height_labels = ["1.80", "1.85", "1.90", "1.95", "2.00"];
width = 1.04;
width_label = "1.04";

for (i = [0 : len(heights) - 1])
    translate([(i - (len(heights) - 1) / 2) * spacing, 0, 0])
        tool(th = heights[i], tw = width, lines = [height_labels[i], width_label]);
