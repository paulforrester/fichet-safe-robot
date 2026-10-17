// 3 dial gear-shafts with a 7mm T2 plug (Paul's variant, 2026-10-17). Gear
// face down, plug up. Plain PETG. NOTE: a misaligned 7mm plug can't be pushed
// back far enough for the unit to sit on the door (dial_layout_check.py):
// it holds that side ~0.9mm off until the seat turn lets the plug drop in.
//   openscad -o gear_shafts_7mm.stl print_gear_shafts_7mm.scad
use <dial_unit_housing.scad>
print_gear_shafts(7);
