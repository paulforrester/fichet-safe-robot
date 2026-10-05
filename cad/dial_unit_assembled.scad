// Assembled view of the v2 geared dial unit, for looking at and for
// cad/tools/dial_interference_check.py. Not for printing.
//   openscad -D 'part="gearshaft0"' -D retract=7 -D phase=6 -o x.stl dial_unit_assembled.scad
// part = "all" | "front" | "sled" | "deck" | "gearshaft0..2" | "pinion0..2" |
//        "motor0..2" | "bearings0..2" | "m3heads0..2"
use <dial_unit_housing.scad>
part    = "all";
retract = 0;    // 0..7mm, gear-shafts pushed back
phase   = 0;    // pinion rotation, degrees
assembled(part, retract, phase);
