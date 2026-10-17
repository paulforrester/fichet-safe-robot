// Print-ready export, everything that turns: 3 dial gears (rear face down),
// 3 dial shafts with the 5mm T2 plug (tail down, plug up), 3 twist-lock caps
// (nubs up) and 3 motor pinions (hub down, teeth up). Gears, shafts, caps:
// plain PETG (2026-10-16); pinions PETG-CF. Elephant-foot compensation ON.
// Or print them separately: print_dial_gears / print_dial_shafts_5mm / _7mm.
//   openscad -o dial_drivetrain.stl print_drivetrain.scad
use <dial_unit_housing.scad>
print_drivetrain();
