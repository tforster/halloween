# Wiring Diagram <!-- omit in toc -->

The two-rig installation as boxes and wires, readable in a terminal or on GitHub without panning. It is kept by hand in step with [`wiring.yml`](./assets/wiring.yml), which wins wherever the two disagree; for wire colours, gauges and lengths, see the rendered [WireViz diagram](./assets/wiring.svg).

## Table of Contents <!-- omit in toc -->

- [1. Diagram](#1-diagram)
- [2. Legend](#2-legend)

## 1. Diagram

Numbers beside pin names are physical pin numbers, as `wiring.yml` uses them. The drawing is 144 columns wide.

```text
┌───────────┐                     +5 V logic bus (TB_5V)                                        ┌────────────────────┐            ┌────────────┐
│   PSU_L   ├────────────┬──────────────────────────────────┬────────────────┐                  │ Rig A      +5V px1 ├────────────┤   PSU_A1   │
│  5 V 3 A  │            │                                  │                │                  │ WS2812B    GND px1 ├────────────┤  5 V 8 A   │
│       GND │      ┌─────┴─────┐                            │                │                  │ 300 px             │            └────────────┘
└──┬────────┘      │ D1 1N5817 │                            │                │      ╔[R_A 330Ω]►╡ DIN                │
   │               └─────┬─────┘                            │                │      ║           │                    │            ┌────────────┐
   │                     │                                  │                │      ║           │          +5V px151 ├────────────┤   PSU_A2   │
   │                     │                                  │                │      ║           │          GND px151 ├────────────┤  5 V 8 A   │
   │  ┌──────────────────┴─────┐              ┌─────────────┴────────────┐   │      ║           │ +1000 µF ×2        │            └────────────┘
   │  │ Pico 2        VSYS 39  │              │       BSS138 (U1)        │   │      ║           └────────────────────┘
   │  │                        │              │            HV            │   │      ║2.7 m pair
   │  │ +100 µF        GP16 21 ├─────────────►┤ LV1                 HV1  ╞═══╪══════╝
   │  │ VSYS–GND               │              │                          │   │                  ┌────────────────────┐            ┌────────────┐
   │  │                GP17 22 ├─────────────►┤ LV2                 HV2  ╞═══╪══════╗           │ Rig B      +5V px1 ├────────────┤   PSU_B1   │
   │  │                        │              │     R_PU_A 1.5kΩ HV1–HV  │   │      ║2.7 m pair │ WS2812B    GND px1 ├────────────┤  5 V 8 A   │
   │  │                        │              │     R_PU_B 1.5kΩ HV2–HV  │   │      ║           │ 300 px             │            └────────────┘
   │  │                 3V3 36 ├─────────────►┤ LV                       │   │      ╚[R_B 330Ω]►╡ DIN                │
   │  │                        │              │     +100 nF HV–GND       │   │                  │                    │            ┌────────────┐
   │  │                        │              └──┬───────────────────────┘   │                  │          +5V px151 ├────────────┤   PSU_B2   │
   │  │                        │                 │GND                        │                  │          GND px151 ├────────────┤  5 V 8 A   │
   │  │                        │                 │    ┌──────────────────────┴──┐               │ +1000 µF ×2        │            └────────────┘
   │  │                        │                 │    │      DFPlayer Mini      │               └────────────────────┘
   │  │                        │                 │    │                         │
   │  │                        │   UART1 TX 9600 │    │                 VCC 1   │                 ┌────────────────┐
   │  │                 GP4  6 ├─────────────────┼───►┤ 2 RX                    │                 │  TPA3118 amp   │      ┌───────────┐
   │  │                        │                 │    │                         │                 │   CANADUINO    │      │  Speaker  │
   │  │                        │                 │    │                 DAC_L 5 ├[R_SUM_L 10k]┐   │          OUT+  ├──────┤ +         │
   │  │                        │                 │    │ +100 µF                 │             ├───┤ IN+            │      │           │
   │  │ VBUS 40                │                 │    │                 DAC_R 4 ├[R_SUM_R 10k]┘   │          OUT−  ├──────┤ −         │
   │  │ unwired                │                 │    │ SPK_1/2, TX unwired     │               ┌─┤ IN−            │      └───────────┘
   │  │         GND 38         │                 │    │                         │               │ │ +12V       GND │
   │  └────────────┬───────────┘                 │    │   GND 7                 │               │ └───┬──────────┬─┘
   │               │                             │    └─────┬───────────────────┘               │     │          ●─────┐
   │               │                             │          │                                   │     │          │     │
   │               │                             │          │                                   │     │          │     │
   │               │                             │          │                                   │ ┌───┴──────────┴─┐   │
   │               │                             │          │                                   │ │PSU_AMP 12 V 5 A│   │
   │               │                             │          │                                   │ │ +12V       GND │   │
   │               │                             │          │                                   │ └────────────────┘   │
   │               │                             │          │                                   │                      │
   └───────────────┴─────────────────────────────┴──────────┴───────────────────────────────────┴──────────────────────┘
                              star ground (TB_GND): every ground joins here
```

## 2. Legend

- `┼` and `╪` are two wires crossing without connecting: the UART line crosses U1's ground, and the DFPlayer's VCC crosses both rig data lines. `●`, `┬`, `├` and `┴` are joins.
- `[R_… n Ω]` is a resistor in the wire. R_PU_A and R_PU_B sit across the BSS138 board's HV1–HV and HV2–HV pins, soldered or on the breadboard; the board prints labels, not numbers ([pin guide](./assets/level-shifter.jpg)).
- `═` is a 2.7 m twisted pair, data and GND, from the level shifter to the rig. R_A and R_B sit at the strip's DIN pad. The pair's GND conductor joins the star ground to the rig's GND px1 and is not drawn separately.
- Each strip's +5V copper is cut between pixels 150 and 151, so each supply feeds only its own half; GND and data stay continuous.
- `+100 µF`, `+100 nF HV–GND` and `+1000 µF ×2` are decoupling capacitors across that part's supply and GND.
- The 2026 installation fits no fuses and no manual trigger button ([blueprint](../explanation/2026-blueprint.md#41-hardware)); the level shifter is the reused BSS138 board ([ADR-013](./adr/0013-reused-bss138-level-shifter.md)).

[← Back to Reference](./README.md)
