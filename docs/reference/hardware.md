# Hardware <!-- omit in toc -->

Specifications for the 2026 installation: two rigs on one Raspberry Pi Pico 2, with one shared MP3 player, amplifier and speaker. This page covers the components, GPIO pin assignments, power budget and supply choices. The full wiring is the [wiring diagram](./assets/wiring.svg) (or the [ASCII version](./wiring-diagram.md)), rendered from [`wiring.yml`](./assets/wiring.yml). Assembly steps are in [Assemble the Hardware](../how-to/assemble-hardware.md), and the parts list is in the [Bill of Materials](./bill-of-materials.md).

## Table of Contents <!-- omit in toc -->

- [1. Components](#1-components)
- [2. Pin Assignments](#2-pin-assignments)
- [3. Power Requirements](#3-power-requirements)
- [4. Power Supplies](#4-power-supplies)
- [5. Wire Gauges and Runs](#5-wire-gauges-and-runs)

## 1. Components

| Component                  | Role                                   | Notes                                                                                                                                                                                                                                                                                          |
| :------------------------- | :------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Raspberry Pi Pico 2        | Controller for both rigs               | RP2350, 520 KB SRAM, MicroPython. [Product page](https://www.raspberrypi.com/products/raspberry-pi-pico-2/), [datasheet](https://datasheets.raspberrypi.com/pico/pico-2-datasheet.pdf), [pinout](./assets/pico-2-pinout.pdf)                                                                   |
| DFPlayer Mini MP3 module   | Thunder playback, shared by both rigs  | 9600 baud UART, 16-bit DAC, 44.1 kHz, MicroSD up to 32 GB FAT32. [Universal Solder](https://www.universal-solder.ca/product/mini-mp3-player-module-with-microsd-slot-for-arduino-etc/), [DFRobot wiki](https://wiki.dfrobot.com/DFPlayer_Mini_SKU_DFR0299), [protocol](./dfplayer-protocol.md) |
| 60 W BTL Class D amplifier | Drives the speaker                     | CANADUINO TPA3118, mono, 12 V input. Fed from the DFPlayer's DAC_L/DAC_R line outputs. [Amazon](https://www.amazon.ca/dp/B0D8HCV43H)                                                                                                                                                           |
| Speaker                    | Thunder                                | One for the whole display, beside the central enclosure                                                                                                                                                                                                                                        |
| WS2812B NeoPixel strip     | Lightning, one per rig                 | 300 pixels each, reused from 2025. [Datasheet](https://cdn-shop.adafruit.com/datasheets/WS2812B.pdf)                                                                                                                                                                                           |
| BSS138 level shifter board | 3.3 V → 5 V data for both strips       | Generic 4-channel MOSFET board (HV1–4, LV1–4, HV, LV, GND), two channels used, reused from 2025 ([ADR-013](./adr/0013-reused-bss138-level-shifter.md)). WS2812B data needs 5 V logic for noise margin. [Pin guide](./assets/level-shifter.jpg)                                                 |
| 1.5 kΩ resistors (2)       | Pull-ups on HV1 and HV2                | Soldered across HV1–HV and HV2–HV; the board's own 10 kΩ rises too slowly over 2.7 m ([Known Issues](./known-issues.md))                                                                                                                                                                       |
| 1N5817 Schottky diode      | Pico power from the logic rail         | Into VSYS, so USB and the logic rail never feed each other ([Pico 2 datasheet](https://datasheets.raspberrypi.com/pico/pico-2-datasheet.pdf), Powering Pico)                                                                                                                                   |
| 330 Ω resistors (2)        | Series resistor at each strip's DIN    | Damps reflections on the long data runs                                                                                                                                                                                                                                                        |
| 10 kΩ resistors (2)        | Sum DAC_L and DAC_R into the amp input | Mixes both channels into the mono input without shorting the DAC outputs together                                                                                                                                                                                                              |
| 5 V logic supply           | Pico, DFPlayer and level shifter       | See [Power Supplies](#4-power-supplies)                                                                                                                                                                                                                                                        |
| 5 V pixel supplies (4)     | Two per rig                            | At pixel 1 and pixel 151 of each strip                                                                                                                                                                                                                                                         |
| 12 V supply                | Amplifier                              | Kept separate from the 5 V rails                                                                                                                                                                                                                                                               |

![DFPlayer Mini pinout](./assets/dfplayer-mini.png)

## 2. Pin Assignments

| GPIO (pin)    | Function   | Direction | Hardware Connection                       | Rationale                                                                                                                         |
| ------------- | ---------- | --------- | ----------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| **GP16** (21) | Rig A data | Output    | BSS138 LV1 → HV1 → 330 Ω → rig A DIN      | Not used by either UART; PIO drives the WS2812B timing                                                                            |
| **GP17** (22) | Rig B data | Output    | BSS138 LV2 → HV2 → 330 Ω → rig B DIN      | Next to GP16, also PIO-capable                                                                                                    |
| **GP4** (6)   | MP3 TX     | Output    | Pico UART1 TX → DFPlayer RX (pin 2)       | UART1, so UART0 stays free for USB serial debugging                                                                               |
| **GP5** (7)   | MP3 RX     | Input     | Unwired                                   | UART1 RX, reserved; commands are sent without feedback                                                                            |
| **GP15** (20) | —          | —         | Unwired                                   | Manual trigger not fitted in 2026 ([blueprint](../explanation/2026-blueprint.md#41-hardware)); `USE_MANUAL_TRIGGER` stays `False` |
| **GP25**      | Status LED | Output    | Onboard LED                               | Solid during start-up, then a 1 Hz heartbeat                                                                                      |
| **VSYS** (39) | Power in   | —         | 5 V logic rail through the 1N5817 cathode | Diode-OR with USB; see [Components](#1-components)                                                                                |
| **3V3** (36)  | Power out  | —         | BSS138 LV                                 | Sets the level shifter's low-side reference                                                                                       |
| **VBUS** (40) | —          | —         | Unwired                                   | Feeding it would back-feed a laptop's USB port                                                                                    |

Pico GPIO pins source at most 12 mA each; drive nothing heavier than the level shifter directly. With the 1.5 kΩ pull-ups, GP16 and GP17 each sink about 3.6 mA when low.

The BSS138 board's HV is the 5 V side and LV the 3.3 V side. Channels 3 and 4 stay unwired; the board's own pull-ups hold them.

## 3. Power Requirements

| Component           | Voltage    | Typical Current     | Maximum Current  | Notes                                                |
| ------------------- | ---------- | ------------------- | ---------------- | ---------------------------------------------------- |
| **Pico 2**          | 5 V (VSYS) | 50–100 mA           | 150 mA           | About 4.7 V after the Schottky; VSYS takes 1.8–5.5 V |
| **DFPlayer Mini**   | 5 V        | 20–30 mA idle       | 200 mA peak      |                                                      |
| **BSS138 board**    | 5 V        | <1 mA idle          | 8 mA             | Through the HV pull-ups while the data lines are low |
| **NeoPixels (150)** | 5 V        | 2.5–3 A (lightning) | 9 A (full white) | Lightning uses about 30% duty cycle per segment      |
| **60 W amplifier**  | 12 V       | Variable            | 5 A              | 60 W needs 24 V into 2 Ω; at 12 V it delivers less   |

A full-white flash of one 300-pixel strip draws about 18 A in theory; the lightning effect averages about 30% of that, 5–6 A per rig.

## 4. Power Supplies

Six supplies, all on one common ground. No fuses are fitted in 2026 ([blueprint](../explanation/2026-blueprint.md#41-hardware)): each supply's own short-circuit protection is the only guard.

| Supply  | Rating   | Powers                 | Location                 |
| ------- | -------- | ---------------------- | ------------------------ |
| PSU_L   | 5 V 3 A  | Pico, DFPlayer, BSS138 | By the central enclosure |
| PSU_A1  | 5 V 8 A  | Rig A pixels 1–150     | At rig A pixel 1         |
| PSU_A2  | 5 V 8 A  | Rig A pixels 151–300   | At rig A pixel 151       |
| PSU_B1  | 5 V 8 A  | Rig B pixels 1–150     | At rig B pixel 1         |
| PSU_B2  | 5 V 8 A  | Rig B pixels 151–300   | At rig B pixel 151       |
| PSU_AMP | 12 V 5 A | Amplifier only         | By the central enclosure |

- **Logic supply:** powers only the Pico, DFPlayer and level shifter. Why the logic rail is separate is in [ADR-009](./adr/0009-single-controller-for-multiple-rigs.md).
- **Pixel supplies:** 5 V 8 A or larger, such as the reused 2025 supplies, one per 150-pixel half. One supply on 300 pixels over 5 m drops to 4.2–4.5 V at the far end, below the WS2812B specification.
- **Split +5V at pixel 150/151:** cut or leave open only the +5V connection between pixels 150 and 151, so each supply feeds only its own half. GND and data stay continuous.
- **Amplifier supply:** 12 V, kept off the 5 V rails because Class D amplifiers put switching noise on their supply. Its ground joins the star ground.
- **Common ground:** every ground meets at one star-ground terminal block in the enclosure. Each rig's grounds reach it through the ground wire in that rig's data pair, which carries signal reference, not pixel current. That holds only while the supplies' DC outputs are isolated from mains earth, as plug-in switch-mode supplies normally are; check before using any supply whose V− is earth-bonded.

## 5. Wire Gauges and Runs

| Run                                     | Gauge           | Length                                |
| --------------------------------------- | --------------- | ------------------------------------- |
| Pixel supply to its injection point     | 18 AWG silicone | Short, about 0.5 m                    |
| Amp supply, amp to star ground          | 18 AWG          | Short, inside or beside the enclosure |
| Logic rail, Pico, DFPlayer, line audio  | 22 AWG          | Inside the enclosure                  |
| Data/ground pair to each strip, twisted | 22 AWG          | 2.7 m maximum, U1 to pixel 1          |
| Speaker cable                           | 16 AWG          | As short as the layout allows         |

Strip starts can be up to about 5.4 m apart; where 2.7 m comes from is in [ADR-009](./adr/0009-single-controller-for-multiple-rigs.md). Measure the site before cutting cables; a longer run needs a buffer or differential link, which is out of scope for 2026.

[← Back to Reference](./README.md)
