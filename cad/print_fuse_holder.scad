// Print plate for the 5 x 20 mm fuse holder (cad/fuse_holder.scad):
// body base-down, lid label-face down (its end flap points up). PETG or PLA,
// 0.2mm layers, 3 walls; no supports needed.
use <fuse_holder.scad>
body();
translate([0, 32, 1.6]) rotate([180, 0, 0]) lid();
