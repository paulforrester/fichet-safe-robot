// Print-ready: retainer discs for the 22mm rubber-coated door magnets
// (9 needed: 6 dial unit + 3 key turner; 10 here incl. a spare). Flat, PETG.
// Each sits on a magnet's seat ring; the magnet's own M4 screw goes through
// it into the magnet. See rmag_* in common_mounts.scad.
include <common_mounts.scad>
for (i = [0 : 9]) translate([(i % 5) * 31, floor(i / 5) * 31, 0]) rmag_retainer();
