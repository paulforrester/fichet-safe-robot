# Project revisions

> **Revision 2026-10-08.2** · this file is the revision log · current ID in `REVISION`

Every project document and drawing carries the project revision it was last
brought up to date in, so a printed or downloaded copy can be told apart from
a newer one. The ID is the date plus a sequence number for that day:
`2026-10-08.1` is the first revision of 8 October 2026.

**Rules (for Paul and for any Claude session):**
- The current ID lives in one place: the `REVISION` file at the repo root.
- A design change that affects how the robot is built, wired or run gets a
  new ID. Bump `REVISION`, add an entry below, and update the revision line
  in every document (`python3 tools/check_revision.py` lists any that don't
  match). Typo fixes and notes don't need a new ID.
- Markdown documents carry the line near the top:
  `> **Revision 2026-10-08.1** · …`. Generated drawings (schematic PDF,
  harness, overview, UART pigtail) print it in their title block, read from
  `REVISION` when they're regenerated.
- The firmware has its own version (`FW_VERSION` in `safe_robot.ino`),
  which also names the project revision it was built for.

## Log (most recent first)

### 2026-10-08.2 — UART pigtail replaces the hub board

**Change.** After 2026-10-08.1 the hub board held only R1 (1 kΩ) and the UART
bus node. It becomes a small harness instead (Paul: "more like a custom cable
than a full daughter board"): the **UART pigtail**, six leads with female
Dupont ends (TX2, RX2, A, B, C, KEY), R1 in line in the TX2 lead, all joined
in one solder splice that zip-ties to the deck. Same circuit (TMC2209 DS
Fig. 4.1). Reasoning: `control/wiring.md`, log 2026-10-08 (pigtail).

**Gone:** the hub perfboard and its male header pins. The same six F–F
jumpers are used, cut, with their hub ends soldered into one splice (six
fewer plug-in joints). The hub's place on the deck is no longer a mechanical
to-do.

**Changed:**
- TX2 / RX2 pigtail leads go straight onto AUX-4 pins 18 / 17; leads A, B,
  C, KEY onto the X, Y, Z, E0 MS3 jumper pins (signal side), as before.
- New build step with a multimeter check (manual §2.5).
- `control/harness/hub_board.*` → `uart_pigtail.*`;
  `control/harness/ramps_and_hub.md` → `ramps_and_uart.md`.
- Schematic sheet 1: the 12 V line now goes to the RAMPS block
  (**Correction**: in 2026-10-08.1 it was drawn into the hub block).
- Manual fault table (GSTAT 1 / 80 for the key): the stale "hub fuse"
  advice from before 2026-10-08.1 is replaced.

**Also in 2026-10-08.2 (later the same day, before the PR merged): taps on
the drivers, no soldering.** Paul's BTT V1.3s have RX/TX/CLK as tall pins
through the top, and the two EN-end pins go through the board. Measured:
RX–TX open (R10 not fitted); a Dupont grips the top of RX and conducts.
- Pigtail leads A, B, C, KEY clip onto the **top of each driver's RX pin**,
  not the RAMPS MS3 jumper pin (whose clearance under a seated driver was
  never checked). MS3 jumper still off.
- **DIAG mod → two snips**: cut both EN-end pins' bottom ends flush; DIAG is
  a plain F–F jumper on the top of the DIAG pin (next to the pot). No
  soldering on the drivers; no cut-in-half jumpers.
- **Driver orientation check** added (manual §2.4 step 2): the RAMPS
  sockets have no pin-1 mark on top; the VS/GND/motor row goes nearer the
  motor header, checked by continuity to the "5A" terminal.
- Schematic sheets 3–7, the pigtail drawing, harness and overview, the
  bench sheet, manual §2.3/2.4/2.5/2.7, bring-up stages 0–1, `CLAUDE.md`,
  `docs/bom.md` and two firmware comments updated. Reasoning:
  `control/wiring.md`, log 2026-10-08 (evening).

**Not changed:** firmware (still v0.4; its boot line names rev
2026-10-08.1, the revision it was built for, and it runs unchanged), pin map,
addresses, currents, power order.

**Documents updated:** `control/wiring.md`, `control/harness/*` (schematic,
harness, overview, pigtail drawing, bench sheet), `control/bringup.md`
(stage 1), `docs/manual.md`, `docs/bom.md`, `CLAUDE.md`, `control/README.md`,
`tools/check_revision.py`, and the revision line of every document.

**Previous state:** `main` at commit `b5c4124` (revision 2026-10-08.1).

### 2026-10-08.1 — key driver moves onto the RAMPS (E0 socket)

**Change.** The key turner's TMC2209 moves from its own perfboard at the key
turner to the RAMPS **E0** socket, beside the three dial drivers (Paul's
suggestion; analysis in `control/wiring.md`, log 2026-10-08). The key motor's
own ~1 m cable plugs into the E0 motor header.

**Gone:** the remote driver board, the 6-conductor inter-unit cable and its
Phoenix connectors, the 12 V branch on the hub board with its fuse (PTC, or
the interim 1.6 A glass fuse and its printed holder), and the remote board's
two 100 µF capacitors.

**Changed:**
- Key pins: STEP D26, DIR D28, EN D24 (E0 socket); DIAG D19 (Z_MAX) as
  before, now through the E0 driver's own DIAG-mod lead. Address 3 = MS1 +
  MS2 jumpers under E0.
- DIAG mod on **four** drivers, not three.
- The hub board shrinks to the UART junction: R1 (1 kΩ) and the bus node.
  12 V goes from the PSU adapter straight into the RAMPS "5A" terminal.
- Firmware v0.4: the key is an ordinary axis (DIR and EN pins); the UART
  direction workaround is gone; the key driver now stays off at power-up.

**Documents updated:** `control/wiring.md`, `control/harness/*` (schematic,
harness, overview, hub board, RAMPS/hub sheet), `control/sequence.md`,
`control/bringup.md`, `control/firmware/` (code, tests, README),
`docs/manual.md`, `docs/bom.md`, `docs/order_remaining_parts.md`,
`CLAUDE.md`, `README.md`, `control/README.md`. Every document now carries
this revision line.

**Previous state:** `main` at commit `76a4167` (2026-10-07), before this
revision. There were no revision IDs before this one.
