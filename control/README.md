# Control (motors, drivers, wiring, firmware)

> **Revision 2026-10-08.1** · key driver on the RAMPS E0 socket · log: `../docs/revisions.md`

- `sequence.md` — control architecture and the operating sequence (seat,
  home, learn the key's stop angle, the 8,000-combination loop, false sets),
  plus what the firmware decided on top of it.
- `wiring.md` — the wiring harness: pin map, driver jumpers and UART
  addresses (all four drivers on the RAMPS, key in E0), the dial-end hub
  board (the UART junction), the key motor cable, motor currents, power-up
  order, shopping list, with sources.
- `harness/ramps_and_hub.md` — one bench sheet of everything fitted to the
  RAMPS and the hub.
- `harness/` — WireViz harness diagram and a Graphviz overview (sources +
  rendered SVG/PNG).
- `firmware/` — Arduino Mega sketch (TMCStepper), its plain-C++ core with
  host tests against a simulated lock, and the serial logger. See
  `firmware/README.md`.
- `bringup.md` — bench bring-up in seven stages, with what to send back.
- `lock_research.md` — does the Complice relock or lock out? (No evidence of
  an attempt lockout; a relocker fires on attack.)
