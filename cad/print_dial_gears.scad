// 3 dial gears (28T, tapered hex bore, back wall with an M3 countersink,
// front boss, 1mm spring pocket), revision 2026-10-17.2. Rear (pocket) face
// down. Plain PETG, elephant-foot compensation ON.
// The bore fit comes from taper_hex_coupon (hex_fit in dial_unit_housing.scad).
//   openscad -o dial_gears.stl print_dial_gears.scad
use <dial_unit_housing.scad>
print_dial_gears();
