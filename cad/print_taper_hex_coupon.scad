// Fit coupon for the tapered-hex gear-shaft (revision 2026-10-17.2): three
// gear hubs with the hex bore drawn 0.0 / 0.1 / 0.2 mm over across the flats
// (1, 2, 3 notches on the rim), each with the gear's back wall, countersink
// and spring pocket, and three shaft tails (journal + tapered hex + M3 pilot).
// Print before the gears. Plain PETG, as exported: hubs pocket face down,
// tails journal end down (a brim helps).
//   openscad -o taper_hex_coupon.stl print_taper_hex_coupon.scad
use <dial_unit_housing.scad>
print_taper_hex_coupon();
