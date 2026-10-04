// Print-ready export: just the electronics sled (electronics_deck()),
// dropped from its assembled height (deck_z = plate_thickness +
// rear_standoff + motor_plate_h + deck_standoff_h = 85.2mm) to z=0,
// mating face down. Render with:
//   openscad -o electronics_deck.stl print_electronics_deck.scad
use <dial_unit_housing.scad>
translate([0, 0, -85.2]) electronics_deck();
