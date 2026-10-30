# Wiring Diagram <!-- omit in toc -->

The two-rig installation as boxes and wires, readable in a terminal or on GitHub without panning. It is kept by hand in step with [`wiring.yml`](./assets/wiring.yml), which wins wherever the two disagree; for wire colours, gauges and lengths, see the rendered [WireViz diagram](./assets/wiring.svg).

## Table of Contents <!-- omit in toc -->

- [1. Diagram](#1-diagram)
- [2. Legend](#2-legend)

## 1. Diagram

Numbers beside pin names are physical pin numbers, as `wiring.yml` uses them. The drawing is 144 columns wide.

```text
┌───────────┐                     +5 V logic bus (TB_5V)                                        ┌────────────────────┐            ┌────────────┐
│   PSU_L   ├─[F_L 2 A]──┬──────────────────────────────────┬────────────────┐                  │ Rig A      +5V px1 ├[F_A1 10 A]─┤   PSU_A1   │
│  5 V 3 A  │            │                                  │                │                  │ WS2812B    GND px1 ├────────────┤  5 V 8 A   │
│       GND │      ┌─────┴─────┐                            │                │                  │ 300 px             │            └────────────┘
└──┬────────┘      │ D1 1N5817 │                            │                │      ┌[R_A 330Ω]►┤ DIN                │
   │               └─────┬─────┘                            │                │      │           │                    │            ┌────────────┐
   │                     │                                  │+100 nF         │      │           │          +5V px151 ├[F_A2 10 A]─┤   PSU_A2   │
   │                     │                                  │                │      │           │          GND px151 ├────────────┤  5 V 8 A   │
   │  ┌──────────────────┴─────┐              ┌─────────────┴────────────┐   │      │           │ +1000 µF ×2        │            └────────────┘
   │  │ Pico 2        VSYS 39  │              │      74AHCT125 (U1)      │   │      │           └────────────────────┘
   │  │                        │              │         VCC 14           │   │      │2.7 m
   │  │ +100 µF        GP16 21 ├─────────────►┤ 2 1A                1Y 3 ├───┼──────┘
   │  │ VSYS–GND               │              │                          │   │                  ┌────────────────────┐            ┌────────────┐
   │  │                GP17 22 ├─────────────►┤ 5 2A                2Y 6 ├───┼──────┐           │ Rig B      +5V px1 ├[F_B1 10 A]─┤   PSU_B1   │
   │  │                        │              │ OE + unused → GND        │   │      │2.7 m      │ WS2812B    GND px1 ├────────────┤  5 V 8 A   │
   │  │                        │              └──┬───────────────────────┘   │      │           │ 300 px             │            └────────────┘
   │  │                        │                 │                           │      └[R_B 330Ω]►┤ DIN                │
   │  │                        │                 │GND 7                      │                  │                    │            ┌────────────┐
   │  │                        │                 │                           │                  │          +5V px151 ├[F_B2 10 A]─┤   PSU_B2   │
   │  │                        │                 │                           │                  │          GND px151 ├────────────┤  5 V 8 A   │
   │  │                        │                 │    ┌──────────────────────┴──┐               │ +1000 µF ×2        │            └────────────┘
   │  │                        │                 │    │      DFPlayer Mini      │               └────────────────────┘
   │  │                        │                 │    │                         │
   │  │                        │   UART1 TX 9600 │    │                 VCC 1   │                 ┌────────────────┐
   │  │                 GP4  6 ├─────────────────┼───►┤ 2 RX                    │                 │  TPA3118 amp   │      ┌───────────┐
   │  │                        │     ┌───────┐   │    │                         │                 │   CANADUINO    │      │  Speaker  │
   │  │                        │     │  SW1  │   │    │                 DAC_L 5 ├[R_SUM_L 10k]┐   │          OUT+  ├──────┤ +         │
   │  │                GP15 20 ├──●──┤1      │   │    │ +100 µF                 │             ├───┤ IN+            │      │           │
   │  │ VBUS 40                │  │  │       │   │    │                 DAC_R 4 ├[R_SUM_R 10k]┘   │          OUT−  ├──────┤ −         │
   │  │ unwired         3V3 36 ├──┼──┤2      │   │    │ SPK_1/2, TX unwired     │               ┌─┤ IN−            │      └───────────┘
   │  │         GND 38         │  │  └───────┘   │    │                         │               │ │ +12V       GND │
   │  └────────────┬───────────┘  │              │    │   GND 7                 │               │ └───┬──────────┬─┘
   │               │              │              │    └─────┬───────────────────┘               │     │          ●─────┐
   │               │          ┌───┴───────┐      │          │                                   │     │[F_AMP 5A]│     │
   │               │          │R_PD 4.7kΩ │      │          │                                   │     │          │     │
   │               │          └─────┬─────┘      │          │                                   │ ┌───┴──────────┴─┐   │
   │               │                │            │          │                                   │ │PSU_AMP 12 V 5 A│   │
   │               │                │ RP2350 E9  │          │                                   │ │ +12V       GND │   │
   │               │                │            │          │                                   │ └────────────────┘   │
   │               │                │            │          │                                   │                      │
   └───────────────┴────────────────┴────────────┴──────────┴───────────────────────────────────┴──────────────────────┘
                              star ground (TB_GND): every ground joins here
```

## 2. Legend

- `┼` is two wires crossing without connecting: the UART line crosses U1's ground, and the DFPlayer's VCC crosses both rig data lines. `●`, `┬`, `├` and `┴` are joins.
- `[F_… n A]` is an inline fuse at that supply's positive terminal; `[R_… n Ω]` is a resistor in the wire.
- Each 2.7 m rig data run is a twisted pair. Its ground conductor joins the rig's GND px1 to the star ground, and is not drawn as a separate wire.
- Each strip's +5V copper is cut between pixels 150 and 151, so each supply feeds only its own half; GND and data stay continuous.
- `+100 µF`, `+100 nF` and `+1000 µF ×2` are decoupling capacitors across that part's supply and GND.
- SW1 and R_PD are the optional manual trigger and its RP2350 erratum E9 pull-down; leave both out when `USE_MANUAL_TRIGGER` is `False`.

[← Back to Reference](./README.md)
