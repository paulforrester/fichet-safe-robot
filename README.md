# Fichet-Bauche "Complice" Safe — Combination Robot

An automated device to determine the combination of an unmarked
Fichet-Bauche "Complice" safe found in the house at 6 Rue du Mulet,
Bordeaux. The project spans three phases: mechanical (tube-socket
coupler and drive), electrical (motor/servo control circuitry), and
firmware/code (dial indexing and combination search).

## Status

Mechanical phase, first subcomponent: a hand-testable tube-socket
**test key**, used to fit-test the 8-tooth spline profile of the
safe's three dial sockets before committing to a motorized coupler
design. Current confirmed dimensions (see `docs/decisions.md` for how
we got here):

| Dimension | Value | Status |
|---|---|---|
| Tooth height (radial, root→tip) | 1.75 mm | confirmed by test print |
| Tooth width (tangential) | 1.04 mm | latest test print, pending fit report |
| Tooth depth (axial, into socket) | 5.0 mm | measured directly off the real key |
| Tip diameter | 7.73 mm (measured), 7.38mm printed (0.35mm clearance) | working |
| Collar diameter | 11.75 mm | confirmed, clears the ~12mm door recess |

## Repo layout

- `cad/` — OpenSCAD source for 3D-printed parts. `tube_socket_test_key.scad`
  is parametric (tooth height, width, and an engraved label are all
  top-level variables — see the file header for CLI override examples).
  `cad/renders/` holds reference renders and the latest STL.
- `docs/` — dimensional decisions, terminology reference, and other
  project notes.
- `control/` — motor/servo control circuitry and firmware (not started).

## Terminology

Tooth dimensions are described consistently as WIDTH (tangential),
HEIGHT (radial), DEPTH (axial into the socket) — see
`docs/tooth_terms_diagram.png`.

## Next steps

- Confirm the 1.75mm / 1.04mm test key's fit (report from bench testing)
- If confirmed, shorten the handle and design the motor-coupler version
  (short hex stub instead of a hand-grip handle)
- Begin `control/`: motor/servo selection and driver circuitry for
  turning and reading each dial
