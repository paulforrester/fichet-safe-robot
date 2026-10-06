// Pin map — must match control/wiring.md §1 (sources there: Marlin
// pins_RAMPS.h, RAMPS 1.4 netlist, Arduino AVR core).
#pragma once

// Dial A (top-left) — RAMPS X socket, UART address 0 (no MS jumpers)
#define PIN_A_STEP   54   // A0
#define PIN_A_DIR    55   // A1
#define PIN_A_EN     38
#define PIN_A_DIAG   3    // X_MIN header S; external interrupt

// Dial B (top-right) — RAMPS Y socket, UART address 1 (MS1 jumper)
#define PIN_B_STEP   60   // A6
#define PIN_B_DIR    61   // A7
#define PIN_B_EN     56   // A2
#define PIN_B_DIAG   2    // X_MAX header S; external interrupt

// Dial C (bottom) — RAMPS Z socket, UART address 2 (MS2 jumper)
#define PIN_C_STEP   46
#define PIN_C_DIR    48
#define PIN_C_EN     62   // A8
#define PIN_C_DIAG   18   // Z_MIN header S; external interrupt

// Key turner — remote board over the cable, UART address 3. Its DIR and EN
// are tied to GND on the remote board: direction = GCONF.shaft, enable =
// CHOPCONF.TOFF, both over UART.
#define PIN_K_STEP   23   // AUX-4 pin 16
#define PIN_K_DIAG   19   // Z_MAX header S; external interrupt

#define PIN_BUTTON   14   // Y_MIN header S, button to GND
#define PIN_LED      13   // on-board LED

// UART bus: Serial2 = TX2 D16 (AUX-4 18) -> 1k -> bus, RX2 D17 (AUX-4 17)
#define TMC_SERIAL   Serial2
