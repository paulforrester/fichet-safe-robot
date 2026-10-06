// FIRST key-turner print: the cap (mouth down) + a hand lever that engages its
// tongue like the motor hub does. Try it on the real key; hook a luggage scale
// in the lever hole (50mm from the axis) to measure the key's turning torque.
use <key_turner_housing.scad>
print_cap();
translate([45, 0, 0]) print_fit_lever();
