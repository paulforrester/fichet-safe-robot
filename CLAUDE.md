# CLAUDE.md — Fichet-Bauche safe combination robot

Context for any Claude session working in this repo. Read this first, then
the doc that matches your task (table below). Last updated 2026-10-06.

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
  plus the electronics (Arduino Mega 2560 + RAMPS 1.4 + 3 TMC2209 drivers).
- **Key-turner unit** — 1 NEMA17 on the key axis, driving a cap that slips
  over the key's bow; its own TMC2209 sits locally, cabled to the dial unit.

Project phases: mechanical (nearly done, being printed), wiring harness and
firmware (not started — see "Where things stand" below).

## How Paul works — follow these

- **Don't guess.** If a fact isn't in the repo or a source you can cite,
  research it (datasheets, library source, vendor pages). If you still
  can't establish it, say "I don't know" and ask Paul or design a bench
  test that answers it. Flag every assumption explicitly in the docs.
- **Git: branch + pull request, never commit to `main`.** One topic per
  branch. Paul reviews and merges. Check whether a PR is already merged
  before pushing more to its branch — if it is, start a new branch/PR.
- **Ground decisions in measured or sourced data**, and record the
  reasoning in the matching decision log (most recent entry first, dated).
  When something earlier turns out wrong, correct it in place and say so
  ("Correction: …") rather than silently rewriting history.
- **Verify before claiming.** CAD: render + run the check scripts. Code:
  compile and run host-side tests. Say what you verified and how.
- **Check the date** (`date`; Paul is in Europe/Paris) rather than assuming.
- Paul is a retired engineer (ex-Apple), comfortable with Arduino,
  Raspberry Pi and 3D printing (Bambu H2D; PETG, PETG-CF, PLA). He has
  calipers, a luggage scale, a soldering station, heat gun. **No
  multimeter yet** (on the to-buy list). He runs every hardware test
  himself and reports results — give him short, numbered bench steps and
  say exactly what number or observation to send back.
- Keep explanations plain and concise; lead with the conclusion.

## Repo map

| Path | What |
|---|---|
| `README.md` | Overview + status |
| `control/sequence.md` | **Control architecture, wiring plan, operating sequence, open items — the main input for firmware and harness work** |
| `docs/bom.md` | Bill of materials, tracked against what was actually ordered (vendor, price, status) |
| `docs/housing_decisions.md` | Mechanical decision log for both housings (most recent first) |
| `docs/decisions.md` | Dial-plug (tube-socket) tooth geometry log |
| `docs/photos/` | Door, dial holes, key reference photos |
| `cad/*.scad` | OpenSCAD sources. `common_mounts.scad` (shared NEMA17, magnet, D-bore), `dial_unit_housing.scad`, `key_turner_housing.scad`; `print_*.scad` export one printable part each; `*_assembled.scad` for checks |
| `cad/*.stl` | Rendered parts Paul prints |
| `cad/tools/` | `dial_layout_check.py`, `dial_interference_check.py`, `key_turner_check.py` — run after any CAD change |
| `cad/sketchup/` | Build scripts for SketchUp review models (run via the Trimble SketchUp connector, not locally) |
| `control/` | Firmware and harness go here (nothing yet besides docs) |

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
  level with it. The inter-unit cable run is short (~125 mm centre to
  centre; allow slack for placing the units by hand).
- Real key goes in by hand before each session; the cap slides over it.

## Electronics as ordered (all on hand or arriving — see `docs/bom.md`)

- Arduino **Mega 2560 REV3** (genuine), USB-B (USB-C→B cable).
- **RAMPS 1.4** shield (Fasizi). 5 StepStick sockets; X/Y/Z used for the
  3 dial drivers. Screw-terminal 12 V input.
- **BigTreeTech TMC2209 V1.3** ×5 (with heatsinks), StallGuard + UART.
- **12 V / 5 A** supply (ledmo).
- **1 kΩ resistors** ×100 (UART).
- Inter-unit cable: **QUARKZMAN 22 AWG shielded, 6-conductor**, ~5.5 m roll.
- Connectors: **Phoenix-style 5.08 mm 8-pin pluggable screw terminals**
  (substituted for the JST-XH originally planned).
- Double-sided perfboard kit (for the remote driver board), heat shrink.
- **AS5600** magnetic encoders ×4 (optional, only if step counting on the
  key proves unreliable), 7 mm momentary pushbuttons ×12 (start trigger).
- Still to buy: multimeter, F–F / M–F jumpers, possibly solder.

## Wiring decisions already made (`control/sequence.md`)

- Each TMC2209 sits **next to its motor** (StallGuard reads back-EMF at
  the motor; long phase wires would dull it). Only logic signals + 12 V
  cross the cable to the key turner.
- **All 4 drivers share one UART bus on `Serial2`** (Mega pins 16 TX /
  17 RX), using TMC2209 multi-drop addresses 0–3 set by MS1/MS2 strapping.
  `Serial` stays free for USB; `Serial1` (18/19) and `Serial3` (14/15)
  would collide with RAMPS endstop headers.
- **DIAG (stall) outputs** of the 3 dial drivers → RAMPS endstop headers
  X_MIN (pin 3), Y_MIN (pin 14), Z_MIN (pin 18).
- Key-turner driver: STEP/DIR/EN/DIAG on spare Mega pins (RAMPS AUX
  headers), exact pins not chosen yet.

## Known open issues for the harness — resolve with sources, not assumptions

1. **Conductor count.** The 6-conductor cable can't carry STEP, DIR, EN,
   DIAG, UART, 12 V, GND *and* 5 V logic (VIO) for the remote driver.
   Options to evaluate: EN tied low locally + disable via UART; StallGuard
   read over UART (SG_RESULT) instead of a DIAG wire; local 5 V regulator
   at the key turner; shield as ground. Pick one and justify it.
2. **UART resistor topology.** `sequence.md` says one 1 kΩ per driver;
   the common single-wire scheme is TX → one 1 kΩ → shared PDN_UART bus,
   RX straight to the bus. Check the TMC2209 datasheet and the TMCStepper
   library docs and settle it.
3. **BTT TMC2209 V1.3 pin access on RAMPS.** RAMPS doesn't route the
   driver's UART pin to the Mega, and whether DIAG reaches a socket pin on
   this board revision needs checking (BTT's V1.3 manual/schematic).
   Expect flying leads from each driver's UART (and maybe DIAG) pin.
4. **Address strapping on RAMPS:** the MS1/MS2/MS3 jumpers under each
   socket set the UART address in UART mode — confirm the mapping for this
   board and specify the jumpers for X/Y/Z, and the strapping on the
   remote driver's perfboard.
5. **Where the key-turner driver board mounts.** The key turner housing
   (v1) has no mount for it. That's a mechanical change — specify the
   board's size and needs, and leave the CAD change for a mechanical
   session (or do it there with the CAD checks).
6. Cable routing/strain relief and the Phoenix connector pin-out at both
   ends; fuse/power-up order; motor current settings per driver.

## Firmware — what's decided and what's open

Decided (see `control/sequence.md`, "Operating sequence" and "False
sets"): seat → home each dial by stalling against its stop → learn the
key's stop angle N° each session → loop over 8,000 combinations: set
dials, try the key to N + margin, **record the actual angle reached**
(not just pass/fail), retract → stop and report on a clear success.
Logging every attempt's angle lets false sets be told apart afterwards.

Open (don't build in assumptions about these; make them configurable or
detect them):
- Whether each dial wheel has a hard stop near position 1 to home on.
- Dial torque (sizes the current and StallGuard thresholds).
- Motor-direction ↔ dial-numbering and key-direction mapping.
- Whether the Complice line has anti-manipulation relocking — research
  before running thousands of attempts.
- How a run is started (button vs. serial command), resumed after a power
  loss or a unit slipping, and how results reach Paul (USB serial log to a
  computer is the obvious baseline).

Safety rules for any motion code: start at low current and low speed;
bound every move (never an unbounded "turn until stall"); stop on stall
or timeout; make it easy to abort; never drive the key past what the run
asks for.

## Working in a cloud session (no hardware)

- There is no Mega, motor or safe here. Do the work that doesn't need
  hardware (design, pin maps, code, host-side tests, bench procedures) and
  hand Paul the hardware steps.
- Network goes through an allowlist (package registries and GitHub are
  usually reachable; other sites often aren't). Arduino/PlatformIO
  toolchain downloads may be blocked. If you can't compile for the Mega,
  say so, keep the search/sequencing logic in plain C++ with no Arduino
  dependency, and unit-test it on the host with `g++`; keep the hardware
  layer thin.
- CAD checks (only if you touch `cad/`): `openscad` renders, then
  `python3 cad/tools/dial_layout_check.py`, `dial_interference_check.py`,
  `key_turner_check.py`; check STLs are watertight (trimesh). Paul has no
  OpenSCAD; he prints the STLs and reviews SketchUp models.
