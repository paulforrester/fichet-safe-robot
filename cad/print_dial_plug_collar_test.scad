// Dial plug collar keys: the first set's 2mm collar with a 10mm plug (C10)
// and with an 8mm plug (C8, same 10mm reach as the L10 probe), end tapers
// T0-T5 (see cad/dial_plug_taper_test.scad, "Collar keys"). Plain PETG, as
// exported: hex handles flat on the bed, plugs up.
DEPTH_SET = true;
include <dial_plug_taper_test.scad>
collar_key_set();
