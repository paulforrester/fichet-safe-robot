# Fichet-Bauche "Complice" Safe — Combination Robot

An automated device to determine the combination of an unmarked
Fichet-Bauche "Complice" safe found in the house at 6 Rue du Mulet,
Bordeaux. The project spans three phases: mechanical (tube-socket
coupler and drive), electrical (motor/servo control circuitry), and
firmware/code (dial indexing and combination search).

## Status

Mechanical phase. Tooth geometry is **CLOSED** (see `docs/decisions.md`
for how we got here):

| Dimension | Value | Status |
|---|---|---|
| Tooth height (radial, root→tip) | 2.00 mm | **locked in** — see `docs/decisions.md` |
| Tooth width (tangential) | 1.04 mm | **locked in** |
| Tooth depth (axial, into socket) | 5.0 mm | measured directly off the real key |
| Tip diameter | 7.73 mm (measured), 7.38mm printed (0.35mm clearance) | working |
| Collar diameter | 11.75 mm | confirmed, clears the ~12mm door recess |

Housings: the **dial unit v2** (`cad/dial_unit_housing.scad`, geared, on 608
bearings — door-pattern test passed on the real door) and the **key turner v1**
(`cad/key_turner_housing.scad`, slotted cap over the key's bow, motor on the key
axis — print `print_key_fit_test.scad` first). Both attach to the door with
22mm rubber-coated M4 pot magnets (6 + 3) held by printed retainers
(`print_magnet_retainer.scad`) — pull-test one on the door when they arrive. See `docs/housing_decisions.md` and `control/sequence.md`.

Electronics ordering is done — four orders placed 2026-09-29 cover
essentially the full `docs/bom.md`, tracked there against every line.

**How to build and run it:** `docs/manual.md` (mechanical and electrical
assembly, building and uploading the firmware, operating and monitoring).

## Repo layout

- `CLAUDE.md` — context and working rules for Claude sessions (cloud or
  local): project facts, decisions, open issues, how Paul works.
- `cad/` — OpenSCAD source for 3D-printed parts.
  - `tube_socket_test_key.scad` — the confirmed spline/tooth geometry,
    parametric (tooth height, width, and an engraved label are all
    top-level variables — see the file header for CLI override examples).
  - `common_mounts.scad` — shared NEMA17 bolt pattern, rubber-magnet
    mount (`rmag_*`), and D-shaft coupler-bore modules, used by both housings below.
  - `dial_unit_housing.scad` / `key_turner_housing.scad` — the two
    mounting housings (see `docs/housing_decisions.md`). The dial unit is
    v2 (geared); `dial_unit_assembled.scad` shows it assembled and the
    `print_*.scad` wrappers export each printable part.
  - `cad/tools/` — `dial_layout_check.py` (clearances, gear mesh, axial
    stack, read straight from the SCAD) and `dial_interference_check.py`
    (3D overlap check of the whole assembly through its range of motion).
  - `cad/sketchup/` — the build script for a SketchUp review model of the
    dial unit (run through the SketchUp connector; the SCAD files are what
    gets printed).
  - `cad/renders/` holds reference renders and STLs of specific
    iterations.
- `docs/` — dimensional decisions (`decisions.md` for the test key,
  `housing_decisions.md` for the housings), the bill of materials
  (`bom.md`, tracked against actual orders), terminology reference, and
  reference photos (`docs/photos/`).
- `control/` — control architecture and operating sequence
  (`sequence.md`), the wiring harness (`wiring.md`, diagrams in
  `control/harness/`), the firmware (`control/firmware/`), the bench
  bring-up plan (`bringup.md`) and the lock research (`lock_research.md`).

## Terminology

Tooth dimensions are described consistently as WIDTH (tangential),
HEIGHT (radial), DEPTH (axial into the socket) — see
`docs/tooth_terms_diagram.png`.

## Next steps

- Bench-fit the v0.1 housings once printed; confirm the placeholder
  dial-hole spacing and key-bow clamp range against the real door/key
  (see `docs/housing_decisions.md`'s "Bench-fit TODO").
- Dial unit v2 (geared, 608 bearings — see `docs/housing_decisions.md`):
  print the door-pattern test (`cad/print_dial_pattern_test.scad`) and the
  three gear-shafts first, and check them on the real door, before the
  big parts. Buy 3 small compression springs.
- Wiring harness designed (`control/wiring.md`); firmware written and
  host-tested (`control/firmware/`); next: the bench bring-up
  (`control/bringup.md`).
