// 3 dial shafts with the 7mm T2 plug (2026-10-17): plug + journal +
// double-D + twist-lock tail. Tail (lugs) on the bed, plug up. Plain PETG.
// They go into the bearings from the DOOR side, tail first.
// NOTE: a misaligned 7mm plug cannot be pushed back far enough for the unit to
// sit flat (dial_layout_check.py): it holds that side ~0.9mm off the door
// until the seat turn lets it drop in.
//   openscad -o dial_shafts_7mm.stl print_dial_shafts_7mm.scad
use <dial_unit_housing.scad>
print_dial_shafts(7);
