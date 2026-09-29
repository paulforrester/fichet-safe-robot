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

Housings for both units (dial unit, key-turner unit) have a **first
pass** (v0.1) built — `cad/dial_unit_housing.scad` and
`cad/key_turner_housing.scad`, see `docs/housing_decisions.md`. Not yet
bench-fit; two dimensions (dial-hole spacing, key bow size) are
placeholders pending real measurement — see that doc and
`control/sequence.md`'s open items.

Electronics ordering is done — four orders placed 2026-09-29 cover
essentially the full `docs/bom.md`, tracked there against every line.

## Repo layout

- `cad/` — OpenSCAD source for 3D-printed parts.
  - `tube_socket_test_key.scad` — the confirmed spline/tooth geometry,
    parametric (tooth height, width, and an engraved label are all
    top-level variables — see the file header for CLI override examples).
  - `common_mounts.scad` — shared NEMA17 bolt pattern, magnet-pocket,
    and D-shaft coupler-bore modules, used by both housings below.
  - `dial_unit_housing.scad` / `key_turner_housing.scad` — the two
    mounting housings (v0.1, first pass — see `docs/housing_decisions.md`).
  - `cad/renders/` holds reference renders and STLs of specific
    iterations.
- `docs/` — dimensional decisions (`decisions.md` for the test key,
  `housing_decisions.md` for the housings), the bill of materials
  (`bom.md`, tracked against actual orders), terminology reference, and
  reference photos (`docs/photos/`).
- `control/` — motor/servo control architecture and operating sequence
  (`sequence.md`); firmware itself not started.

## Terminology

Tooth dimensions are described consistently as WIDTH (tangential),
HEIGHT (radial), DEPTH (axial into the socket) — see
`docs/tooth_terms_diagram.png`.

## Next steps

- Bench-fit the v0.1 housings once printed; confirm the placeholder
  dial-hole spacing and key-bow clamp range against the real door/key
  (see `docs/housing_decisions.md`'s "Bench-fit TODO").
- Order the 3 flexible shaft couplers the dial-unit design surfaced
  (see `docs/bom.md`'s new-item note).
- Begin `control/`: firmware for turning and reading each dial.
