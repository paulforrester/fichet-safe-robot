# CLAUDE.md — Fichet-Bauche safe combination robot

Context for any Claude session working in this repo. Read this first, then
the doc that matches your task (table below). Last updated 2026-10-08.

> **Project revision 2026-10-08.2** — all four TMC2209 drivers are on the
> RAMPS (the key in the **E0** socket); there is no remote driver board or
> inter-unit signal cable, only the key motor's own cable. The UART junction
> is a six-lead **UART pigtail** (R1 in the TX2 lead, one splice), not a
> board (2026-10-08.2). The current
> revision ID lives in `REVISION`; the log is `docs/revisions.md`. When a
> design change affects how the robot is built, wired or run, bump `REVISION`,
> add a `docs/revisions.md` entry, and run `python3 tools/check_revision.py`
> (it lists any document whose revision line is stale).

## What this is

I am building this project to open a safe that was included when I bought my
house in Bordeaux. The safe was included in the sale along with the "dial-keys",
but the old owner did not have the combination.  Rather than throw it away and
add to the landfill I decided to brute force the combination wiht the robot dialer.
It is strictly a hobby project for use on my own property.
The project entails opening an old Fichet-Bauche "Complice" safe in my house in Bordeaux. The lock is a
3-wheel pack: three star-shaped "dial" sockets on the door each turn one
wheel (20 positions each → 20³ = 8,000 combinations), and a real key in a
4th hole turns a cam against a fence. Wrong combination: the key stops at
some angle N°. Right combination: the fence drops into the aligned gates
and the key turns further. The robot sets the three dials, tries the key,
records how far it got, and repeats.

Two 3D-printed units sit on the steel door (rubber-coated magnets):

- **Dial unit** — 3 NEMA17 motors driving the 3 dials through 2:1 gears,
  plus all the electronics (Arduino Mega 2560 + RAMPS 1.4 + **four** TMC2209
  drivers: three dials and the key — revision 2026-10-08.1).
- **Key-turner unit** — 1 NEMA17 on the key axis, driving a cap that slips
  over the key's bow. Its driver is in the RAMPS **E0** socket on the dial
  unit; only the key motor's own cable runs between the units.

Project phases: mechanical (nearly done, being printed); wiring harness
designed (`control/wiring.md`, revision 2026-10-08.2: all four drivers on the
RAMPS, UART pigtail); firmware written and host-tested
(`control/firmware/`), bench bring-up next (`control/bringup.md`).

## How Paul works — follow these

- **Don't guess.** If a fact isn't in the repo or a source you can cite,
  research it (datasheets, library source, vendor pages). If you still
  can't establish it, say "I don't know" and ask Paul or design a bench
  test that answers it. Flag every assumption explicitly in the docs.
- **Git: branch + pull request, never commit to `main`.** One topic per
  branch. Paul reviews and merges. Check whether a PR is already merged
  before pushing more to its branch — if it is, start a new branch/PR.
  **Don't stack PRs** (a PR whose base is another PR's branch): GitHub
  merges it into that branch, not `main`, unless the base branch is deleted
  first. That's how #14 (firmware v0.1) missed `main` on 2026-10-06. Target
  `main` every time.
- **Ground decisions in measured or sourced data**, and record the
  reasoning in the matching decision log (most recent entry first, dated).
  When something earlier turns out wrong, correct it in place and say so
  ("Correction: …") rather than silently rewriting history.
- **Verify before claiming.** CAD: render + run the check scripts. Code:
  compile and run host-side tests. Say what you verified and how.
- **Check the date** (`date`; Paul is in Europe/Paris) rather than assuming.
- Paul is a retired engineer (ex-Apple), comfortable with Arduino,
  Raspberry Pi and 3D printing (Bambu H2D; PETG, PETG-CF, PLA). He has
  calipers, a luggage scale, a soldering station (with solder and wick),
  heat gun, flush cutters and **a multimeter** (Paul, 2026-10-07: bench
  steps can use it). He runs every hardware test
  himself and reports results — give him short, numbered bench steps and
  say exactly what number or observation to send back.
- Keep explanations plain and concise; lead with the conclusion.

## Repo map

| Path | What |
|---|---|
| `README.md` | Overview + status |
| `docs/manual.md` | **Build and operating manual for Paul**: print + assembly, electrical assembly, building and uploading the firmware, running and monitoring. Procedure only; the docs below are the reference — keep it in step when they change |
| `control/sequence.md` | **Control architecture, wiring plan, operating sequence, open items — the main input for firmware and harness work** |
| `control/wiring.md` | **Wiring harness: full pin map, driver jumpers/addresses (all four drivers on the RAMPS, key in E0), the key motor cable, the UART pigtail, currents, power order, sources** |
| `control/harness/ramps_and_uart.md` | **One bench sheet: everything fitted to the RAMPS, and the UART pigtail** |
| `REVISION` / `docs/revisions.md` | Current project revision ID / the revision log |
| `control/harness/` | **`schematic.pdf`: the full wiring schematic, 7 A4 sheets for printing** (generated by `schematic.py` from `wiring.md`; regenerate after any wiring change, keep text ≥ 8 pt), WireViz harness (`harness.yml` → `.svg/.png`), Graphviz overview (`overview.dot` → `.svg`), UART pigtail drawing (`uart_pigtail.py` → `.svg/.png`) |
| `control/firmware/` | **Firmware** (Arduino sketch + plain-C++ core), host tests, serial logger — see its README |
| `control/bringup.md` | Bench bring-up, stage by stage, with what Paul sends back |
| `control/lock_research.md` | Complice relocking / anti-manipulation research |
| `docs/bom.md` | Bill of materials, tracked against what was actually ordered (vendor, price, status) |
| `docs/housing_decisions.md` | Mechanical decision log for both housings (most recent first) |
| `docs/decisions.md` | Dial-plug (tube-socket) tooth geometry log |
| `docs/photos/` | Door, dial holes, key reference photos |
| `cad/*.scad` | OpenSCAD sources. `common_mounts.scad` (shared NEMA17, magnet, D-bore), `dial_unit_housing.scad`, `key_turner_housing.scad`; `print_*.scad` export one printable part each; `*_assembled.scad` for checks |
| `cad/*.stl` | Rendered parts Paul prints |
| `cad/tools/` | `dial_layout_check.py`, `dial_interference_check.py`, `key_turner_check.py` — run after any CAD change |
| `cad/sketchup/` | Build scripts for SketchUp review models (run via the Trimble SketchUp connector, not locally) |

## Mechanical facts the software and wiring depend on

- **Motors:** STEPPERONLINE **17HE19-2004S** NEMA17 (Paul identified the
  exact part 2026-10-03 and checked its drawing with calipers): bipolar,
  4-wire, 2.0 A rated, 59 N·cm holding. 5 on hand (4 used + 1 spare).
  Step angle: `sequence.md` assumes 1.8° (200 full steps/rev) — **not yet
  confirmed against this part's data sheet; confirm before relying on it.**
  Vendor note: on some units the two middle wires of the connector are
  swapped from the expected colour code.
- **Dial drive:** 14T pinion on the motor → 28T gear on the dial shaft
  (2:1). Under the 200-step assumption: 400 full steps per dial turn,
  **20 full steps per dial position**. Motor turns opposite to the dial.
  Each dial shaft is **spring-loaded**: when the unit goes on the door, a
  plug that doesn't line up with its star is pushed back. So every session
  starts with a **seat routine** — turn each dial motor slowly, at most
  1/8 dial turn (45° dial = 90° motor), until the plug drops in — then home.
- **Dial torque: not measured yet.** Until it is, run dial drivers at
  ~1 A RMS.
- **Key turner:** direct drive, motor on the key axis. The key turns
  **clockwise (seen from in front of the safe) to ~100° and stops** with a
  wrong combination. Measured key torque **0.07–0.08 N·m** (0.14–0.16 kg on
  a 50 mm lever, 2026-10-06; an earlier "1.4 kg" was a misread decimal).
  Motor direction vs. key direction is not established — determine it on
  the bench at low current. Run the key motor at reduced current (~2× the
  key's torque) and stop on StallGuard at the end stop, so it doesn't push
  the housing off its magnets.
- **Attachment:** 22 mm rubber-coated M4 pot magnets (6 on the dial unit,
  3 on the key turner). Pull-test pending. Excess motor torque at a hard
  stop loads these magnets sideways — another reason for current limits
  and early stall detection.
- **Geometry:** the key hole is ~125 mm left of the dial-cluster centre,
  level with it. The key motor cable run between the units is short (~125 mm
  centre to centre; allow slack for placing them by hand).
- Real key goes in by hand before each session; the cap slides over it. It
  goes in one way only, can't turn anticlockwise from there, turns ~100°
  clockwise to its stop, **stays wherever it is left (no spring back)**, and
  comes out only at the start (Paul, 2026-10-06). The dials turn with the
  key in at its start, and still click with it at its ~100° stop (Paul,
  2026-10-06). The robot returns the key to its start after every attempt
  (Paul's decision, 2026-10-06).
- **Dials (Paul, 2026-10-06):** each turns clockwise without limit and stops
  turning anticlockwise; 20 evenly spaced clicks (18°); where the first click
  sits relative to the stop can't be read by hand; no marks on the door. The
  manual has no warning about wrong combinations. Manual (`docs/photos/
  complice_manual_normal_use.png`): dial the combination, then insert the key
  and turn it clockwise, then pull the key to open.

## Electronics as ordered (all on hand or arriving — see `docs/bom.md`)

- Arduino **Mega 2560 REV3** (genuine), USB-B (USB-C→B cable).
- **RAMPS 1.4** shield (Fasizi). 5 StepStick sockets; X/Y/Z/**E0** used for
  the four drivers (key in E0, revision 2026-10-08.1). Screw-terminal 12 V
  input feeds all four through its 5 A fuse.
- **BigTreeTech TMC2209 V1.3** ×5 (with heatsinks), StallGuard + UART.
- **12 V / 5 A** supply (Ledmo HTY-1200500, 5.5 × 2.1 mm barrel, centre +).
- **1 kΩ resistors** ×100 (UART).
- The key motor's own ~1 m cable plugs into the RAMPS **E0 motor header**
  (revision 2026-10-08.1). No inter-unit signal cable.
- F–F jumpers (six of them, one end cut off each, make the UART pigtail; four
  cut in half make the DIAG leads), heat shrink, a zip tie.
- **No longer used** (bought earlier, keep as spares): the 6-conductor
  QUARKZMAN cable, the Phoenix 8-pin connectors, the 1.1 A PTC and glass-fuse
  kit + printed holder, the two 100 µF capacitors, the female header strips,
  and (revision 2026-10-08.2) the hub perfboard and male header strip.
- **AS5600** magnetic encoders ×4 (optional, only if step counting on the
  key proves unreliable), 7 mm momentary pushbuttons ×12 (start trigger).
- Nothing left to buy. On hand: multimeter, solder + wick, flush cutters,
  F–F jumpers, DC-jack adapter, 20 AWG wire, the start button. **Revision
  2026-10-08.1:** the PTC fuse + glass-fuse kit + printed holder, the 100 µF
  capacitors, the 6-conductor cable and Phoenix connectors, and the female
  header strips were all bought but are no longer used — keep them as spares
  (`docs/bom.md`, revision banner). Every discrete part:
  `docs/bom.md`, "Electronics assembly — every discrete part". The
  fuses, diode, capacitors and resistors drawn in grey on the schematic
  are already on the RAMPS.

## Wiring — `control/wiring.md`, revision 2026-10-08.2 (read it for details and sources)

- **All four TMC2209 are in RAMPS sockets**: X = dial A (top-left), Y = dial B
  (top-right), Z = dial C (bottom), **E0 = key**. The key motor's own ~1 m
  cable plugs into the E0 motor header — the only wire between the units.
- **One UART bus on `Serial2`** (TX2 D16 / RX2 D17 on AUX-4 18/17), **one
  1 kΩ in total** (TX2 → 1 kΩ → bus; RX2 and every PDN_UART on the bus —
  TMC2209 DS Fig. 4.1). Addresses by MS1/MS2 jumpers: X 0 (none), Y 1 (MS1),
  Z 2 (MS2), **E0 3 (MS1 + MS2)**. **No MS3 jumpers** — on the BTT V1.3
  PDN_UART is in the MS3 position, tapped at the MS3 jumper pin.
- STEP/DIR/EN come from each socket: X D54/D55/D38, Y D60/D61/D56,
  Z D46/D48/D62, **E0 (key) D26/D28/D24** (Marlin `pins_RAMPS.h`). The key is
  an ordinary axis now — no UART direction/enable workaround.
- DIAG, via a one-time mod on **all four** drivers (clip the down pin, solder
  a lead to its top joint): A → X_MIN D3, B → X_MAX D2, C → Z_MIN D18,
  **key → Z_MAX D19** (all interrupt pins; DIAG is a pulse). Start/stop button
  on Y_MIN D14.
- The UART junction is the **UART pigtail** (revision 2026-10-08.2, replaced
  the hub board): six F–F leads with female ends (TX2, RX2, A, B, C, KEY), R1
  in line in TX2, all joined in one solder splice (`control/wiring.md` §5,
  `control/harness/uart_pigtail.svg`). 12 V goes from the PSU's DC-jack
  adapter straight to the RAMPS "5A" terminal; RAMPS's own 5 A fuse feeds all
  four drivers.
- Currents: dials 1.0 A RMS (hold 0.5 A); key 0.6 A to start, then 2 × the
  measured minimum. Power: USB first, then 12 V; 12 V off first; never
  (un)plug a motor (the key motor cable included) with 12 V on.

## Harness: what's left (bench, not design)

Verify on the bench (steps go in `control/bringup.md`): UART lead on the
right MS3 jumper pin (all four sockets, E0 included); which top-edge pin is
DIAG; the key answers at address 3 (E0); the key's StallGuard through the 1 m
motor cable (shorten it if too dull); the pigtail's multimeter check (manual
§2.5). No board mount is needed any more (the pigtail's splice zip-ties to the
deck); the start button's place on the deck is still a mechanical to-do.

## Firmware — `control/firmware/` (v0.4, 2026-10-08; read its README)

Built and host-tested, **not yet run on hardware**. Sequence as in
`control/sequence.md`: session start = ping/configure drivers → key home
(rest stop, search 180°) → key calibration → seat (clockwise) → one free
clockwise calibration turn per dial (StallGuard threshold + click positions)
→ home each dial (two passes on its stop; position 1 = first click) → learn
N (3 tries, median) → attempt loop in **serpentine order** (each attempt moves one
dial one position) → key to N + 15°, **log the angle reached** → retract →
save progress (EEPROM journal). Re-check every 200 attempts (re-home +
re-learn N at the last clean fail); on a mismatch, stop and rewind to the last
good check. Success (≥ N + 10°) stops and holds the key. Resume after power
loss redoes the session start and continues from the last check.

- Layout: `safe_robot/` Arduino sketch (`config.h` = **every unmeasured
  value**, `pins.h`, thin `hw_mega.*`), `safe_robot/src/core/` plain C++
  (no Arduino), `test/` host tests + simulated lock, `tools/logger.py`.
- Library: TMCStepper 0.7.3 (the version Marlin 2.0.x used for TMC2209 over
  UART). Step pulses are generated by the firmware itself (bounded trapezoid).
- Interface: USB serial 115200, commands (`help`), CSV-like log lines; the
  start/stop button on Y_MIN pauses or resumes; `!` aborts a move.
- Lock research (`control/lock_research.md`): no evidence of an
  attempt-counting lockout; a relocker ("délateur") fires on mechanical or
  thermal attack → keep forces low (done).

Self-calibration (v0.2, Paul's idea): StallGuard thresholds come from each
motor's measured free-running load every session (stall at 50 % of it), the
click positions from the dials' 18° StallGuard ripple; `calibrate` does it as
a separate step and EEPROM keeps the last result (the key needs it to home
at the next session start).

Key driver on E0 (v0.4, revision 2026-10-08.1): the key is an ordinary axis —
STEP/DIR/EN from the E0 socket (D26/D28/D24), direction from its DIR pin,
enable from its EN pin. The UART direction/enable workaround (`setKeyShaft`,
TOFF disable) is gone, and RAMPS's EN pull-up keeps the key driver off at
power-up. `pins.h` has the pins.

Driver resets (v0.3, kept in v0.4): a TMC2209 whose 12 V (or 5 V) dips resets
to its power-on registers: no current setting, no StallGuard, other
microsteps. Unseen, a reset can make an open-loop move read as a false
SUCCESS. The
core reads GSTAT through the HAL hook `Hal::gstat()`, before and after every
move, for all drivers before each attempt, and before re-writing a driver's
settings. A flag logs a `GSTAT` line and stops with `ERR DRVFAULT`, rewound
to the last re-check; `resume` recovers. Bench check: `control/bringup.md`
stage 6, step 6.

Biggest unknown (no source; `control/sequence.md` Open items): **whether a
combination dialled with the key already in counts.** The manual dials
before inserting the key. If it doesn't count, the key turner needs a way to
pull the key out and push it back in at every attempt. Only a weak hint is
available on the bench (stage 4b.6); the first full run is the real test.

Still open — each has a `config.h` entry and a stage in `control/bringup.md`:
motor↔dial/key directions (4b, 5), whether the 50 % rule and the click
ripple hold on the real hardware (3, 4), key current (5), step angle (2),
the classification bands (5–6).

Safety rules for any motion code: start at low current and low speed;
bound every move (never an unbounded "turn until stall"); stop on stall
or timeout; make it easy to abort; never drive the key past what the run
asks for; never move a driver without checking its GSTAT (it may have
reset). Keep the sequencing in `src/core` and add a simulated test for
any change (`make -C control/firmware/test`).

## Working in a cloud session (no hardware)

- There is no Mega, motor or safe here. Do the work that doesn't need
  hardware (design, pin maps, code, host-side tests, bench procedures) and
  hand Paul the hardware steps.
- Network goes through an allowlist. Worked on 2026-10-06: `git clone` from
  GitHub (but not github.com web pages), raw.githubusercontent.com, PyPI,
  archive.ubuntu.com (apt). Blocked: analog.com, arduino.cc downloads,
  PlatformIO registry, vendor sites (BTT shop, STEPPERONLINE), reprap.org,
  ManualsLib, Google Patents. The TMC2209 datasheet is mirrored in
  `janelia-arduino/TMC2209` (`datasheet/`); BTT's V1.3 docs are in
  `bigtreetech/BIGTREETECH-Stepper-Motor-Driver`.
- **Compiling for the Mega works via apt**: `apt-get install gcc-avr avr-libc
  arduino-core-avr arduino-mk`, clone TMCStepper (tag v0.7.3) into a
  libraries folder, then
  `make -C control/firmware/safe_robot -f ../Makefile.mega USER_LIB_PATH=<dir>`.
- Host tests: `make -C control/firmware/test` (g++), and
  `python3 -m pytest control/firmware/tools` (logger).
- CAD checks (only if you touch `cad/`): `openscad` renders, then
  `python3 cad/tools/dial_layout_check.py`, `dial_interference_check.py`,
  `key_turner_check.py`; check STLs are watertight (trimesh). Paul has no
  OpenSCAD; he prints the STLs and reviews SketchUp models.
