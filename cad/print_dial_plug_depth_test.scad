// Dial plug depth probes: 10mm and 15mm plugs, end tapers T0-T5, no collar
// (see cad/dial_plug_taper_test.scad, "Depth probes"). Plain PETG, as
// exported: hex handles flat on the bed, plugs up.
DEPTH_SET = true;
include <dial_plug_taper_test.scad>
depth_key_set();
