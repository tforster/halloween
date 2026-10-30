# Bill of Materials (2026) <!-- omit in toc -->

Parts list for the 2026 installation: two rigs on one Pico 2, with one shared DFPlayer Mini, amplifier and speaker. Quantities are for the whole installation. Parts marked _reused_ are left over from the three 2025 boards. Every part appears in the [wiring diagram](./assets/wiring.svg); specifications are in [Hardware](./hardware.md).

## Table of Contents <!-- omit in toc -->

- [1. Modules](#1-modules)
- [2. Power](#2-power)
- [3. Components](#3-components)
- [4. Wire and Fittings](#4-wire-and-fittings)

## 1. Modules

- 1 × Raspberry Pi Pico 2 (_reused_)
- 1 × DFPlayer Mini MP3 module with a FAT32 MicroSD card (_reused_)
- 1 × CANADUINO 60 W BTL amplifier, TPA3118 (_reused_)
  - https://www.amazon.ca/dp/B0D8HCV43H
- 1 × speaker (_reused_)
- 2 × WS2812B 300-pixel strips, one per rig (_reused_)
- 1 × 4-channel BSS138 bidirectional level shifter board, for the two rigs' data lines (_reused_)

## 2. Power

- 1 × 5 V 3 A supply for the logic rail (Pico, DFPlayer, level shifter)
- 4 × 5 V 8 A (or larger) supplies, two per rig (_reused_)
  - https://www.amazon.ca/dp/B0DYHCD21G
- 1 × 12 V 5 A supply for the amplifier (_reused_)
  - https://www.amazon.ca/dp/B01GEA8PQA

## 3. Components

- 1 × 1N5817 Schottky diode (logic rail into the Pico's VSYS)
- 2 × 330 Ω 1/4 W resistors (series, at each strip's DIN)
- 2 × 10 kΩ 1/4 W resistors (sum DAC_L and DAC_R into the amp input)
- 2 × 1.5 kΩ 1/4 W resistors (pull-ups across the level shifter's HV1–HV and HV2–HV)
- 4 × 1000 µF 10 V electrolytic capacitors (one at each injection point)
- 2 × 100 µF 10 V electrolytic capacitors (Pico VSYS, DFPlayer VCC)

## 4. Wire and Fittings

- 1 × central enclosure for the Pico, DFPlayer, level shifter and amplifier
- 1 × 4-way terminal block (5 V logic bus)
- 1 × 8-way terminal block (star ground)
- Barrel jack to screw terminal adapters (female), one per supply that ends in a barrel jack
  - https://www.amazon.ca/dp/B0BHYTRP1M
- Barrel jack (PCB-mount male) for the amplifier
- 2-position green screw terminal blocks for the amplifier's input and speaker output
  - https://www.amazon.ca/dp/B088LSS14J
- 18 AWG silicone stranded wire (red + black), about 5 m, for supply leads
  - https://www.amazon.ca/dp/B0C7T5H9DP
- 22 AWG stranded wire, about 2 × 2.7 m twisted pairs for the two data runs plus short runs in the enclosure
- 16 AWG speaker cable
- Ferrules: 18 AWG (30 pcs), 22 AWG (20 pcs) and 16 AWG (4 pcs)
- Heat shrink kit
  - https://www.amazon.ca/dp/B08XXGNJHG

[← Back to Reference](./README.md)
