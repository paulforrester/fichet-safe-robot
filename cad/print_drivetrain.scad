// Print-ready export, everything that turns: 3 dial gears (rear face down),
// 3 dial shafts with the 5mm T2 plug (plug tip down, tail up) and 3 motor
// pinions (hub down, teeth up). Gears and shafts: plain PETG (2026-10-16);
// pinions PETG-CF. Elephant-foot compensation ON. Each gear goes onto its
// shaft's tapered hex with an M3x10 countersunk (revision 2026-10-17.2).
// Or print them separately: print_dial_gears / print_dial_shafts_5mm / _7mm.
//   openscad -o dial_drivetrain.stl print_drivetrain.scad
use <dial_unit_housing.scad>
print_drivetrain();
