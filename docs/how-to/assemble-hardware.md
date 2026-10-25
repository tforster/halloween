# Assemble the Hardware <!-- omit in toc -->

Wire one 2025 board: Pico 2, DFPlayer Mini, 60 W amplifier, level shifter and a 300-pixel strip with dual power injection. Part specifications and pin assignments are in [Hardware](../reference/hardware.md).

> [!WARNING]
>
> This is the 2025 single-board wiring. The [2026 blueprint](../explanation/2026-blueprint.md#41-hardware) drives two rigs from one Pico and feeds the amplifier from the DFPlayer's DAC_L/DAC_R outputs instead of SPK_1/SPK_2. Follow the blueprint for 2026 builds until this guide is updated.

## Table of Contents <!-- omit in toc -->

- [1. Steps](#1-steps)
- [2. Wiring Diagrams](#2-wiring-diagrams)
  - [2.1. Complete System Wiring (Dual 5V Supply Configuration)](#21-complete-system-wiring-dual-5v-supply-configuration)
  - [2.2. Level Shifter Detail](#22-level-shifter-detail)
  - [2.3. DFPlayer Mini Wiring Detail](#23-dfplayer-mini-wiring-detail)
- [3. Power Injection](#3-power-injection)
  - [3.1. Dual Supply Wiring Diagram](#31-dual-supply-wiring-diagram)
- [4. Safety](#4-safety)
- [5. Alternative: Canaduino Power Module](#5-alternative-canaduino-power-module)
  - [5.1. Level Shifter With Canaduino](#51-level-shifter-with-canaduino)
- [6. Verification](#6-verification)

## 1. Steps

1. **Raspberry Pi Pico 2**
   - Solder headers if not pre-installed
   - Connect USB cable for development

2. **MP3 Player Module**
   - Wire TX → Pico GPIO 4 (Pico TX → Module RX, Pin 2)
   - Wire RX → Pico GPIO 5 (Pico RX ← Module TX, Pin 3)
   - Wire VCC → 5V power rail
   - Wire GND → Common GND
   - Insert formatted MicroSD card with MP3 files
   - Connect audio output to amplifier input (SPK_1/SPK_2 pins recommended)

3. **60W BTL Class D Amplifier**
   - Connect MP3 module audio output to amplifier input
   - Connect 12V power supply
   - Connect speaker(s) to amplifier output
   - Ensure proper polarity

4. **Logic Level Shifter**
   - Wire LV (low voltage) side to Pico 3.3V
   - Wire HV (high voltage) side to 5V power rail
   - Wire both grounds to common ground rail
   - Wire Pico GPIO 16 → Shifter input
   - Wire Shifter output → NeoPixel data in

5. **NeoPixel Strip (300 LEDs)**
   - Wire data in to logic level shifter output
   - Wire 5V to power supply (ensure 8A capacity)
   - Wire ground to ground rail

6. **Optional: Trigger Switch**
   - Wire one terminal to Pico GPIO 15
   - Wire other terminal to 3.3V (active high)
   - Set USE_MANUAL_TRIGGER = True in main.py

## 2. Wiring Diagrams

### 2.1. Complete System Wiring (Dual 5V Supply Configuration)

```text
5V Supply 1 (8A)              5V Supply 2 (8A)              12V Supply (5A)
      │                             │                            │
      │                             │                            │
      ├──→ Pico 2 VBUS              │                            │
      │                             │                            │
      ├──→ DFPlayer Mini VCC        │                            │
      │                             │                            │
      ├──→ Level Shifter HV         │                            │
      │                             │                            │
      │                             │                            │
      └──→ NeoPixels 1-150          └──→ NeoPixels 151-300       └──→ Amplifier 12V
           (at pixel 1)                  (at pixel 150/151)
           │                             │                             │
           ├─ 5V ─────────────────────┐  ├─ 5V ──────────────────-─┐   │
           ├─ GND ────────────────────┼──┼─ GND ─────────────────-─┼───┼─→ Common GND
           └─ DIN ← GP16 (via shifter)   │                         │   │
                    │                    │                         │   │
                    │                    │                         │   │
         ┌──────────┴─────-───┐    ┌──────────────┐         ┌──────┴──────────┐
         │  Raspberry Pi      │    │  DFPlayer    │         │   60W Amplifier │
         │    Pico 2          │    │    Mini      │         │   (Class D BTL) │
         │                    │    │              │         │                 │
         │  GP16 ─────────────┼────┼──────────────┼─────┐   │  Audio In       │
         │  (via Level        │    │              │     │   │   ↑             │
         │   Shifter)         │    │              │     │   │   │             │
         │                    │    │              │     │   │   │             │
         │  GP4 (TX) ─────────┼────┼──→ RX (2)    │     │   │   │             │
         │  GP5 (RX) ←────────┼────┼─── TX (3)    │     │   │   │             │
         │                    │    │              │     │   │   │             │
         │  3.3V ─────────────┼────┼──────────────┼─────┼───┼───┘             │
         │                    │    │  SPK_1 ──────┼─────┘   │                 │
         │                    │    │  SPK_2 ──────┼─────────│→ Speaker Out 🔊 │
         └────────────────────┘    └──────────────┘         └─────────────────┘

Key Connections:
  • Data Signal: Pico GP16 → Level Shifter → Pixel 1 → ... → Pixel 300
  • Power: Supply 1 powers pixels 1-150, Supply 2 powers pixels 151-300
  • Common GND: All three supplies must share common ground
  • Audio: DFPlayer SPK_1/SPK_2 → Amplifier Input
```

### 2.2. Level Shifter Detail

```text
Level Shifter (Bidirectional)
┌────────────────────────────┐
│                            │
│   LV (Low Voltage Side)    │         HV (High Voltage Side)
│   ────────────────────     │         ────────────────────
│                            │
│   VCC_L ←── 3.3V (Pico)    │         VCC_H ←── 5V (LED Rail)
│   GND   ←── Common GND     │         GND ←── Common GND
│   I/O1  ←── GP16 (Pico)    │         I/O1 ──→ NeoPixel DIN
│                            │
└────────────────────────────┘
```

### 2.3. DFPlayer Mini Wiring Detail

```text
DFPlayer Mini Module (Top View)
┌─────────────────────────────┐
│  [MicroSD Card Slot]        │
│                             │
│  Pin 1: VCC ←── 5V          │
│  Pin 2: RX  ←── GP4 (TX)    │
│  Pin 3: TX  ──→ GP5 (RX)    │
│  Pin 4: (not used)          │
│  Pin 5: (not used)          │
│  Pin 6: SPK_1 ──→ Amp In+   │
│  Pin 7: GND ←── Common GND  │
│  Pin 8: SPK_2 ──→ Amp In-   │
│                             │
│  [3.5mm Audio Jack]         │
└─────────────────────────────┘

Note: Use either SPK pins OR 3.5mm jack, not both
      SPK pins provide higher quality output to amplifier
```

## 3. Power Injection

### 3.1. Dual Supply Wiring Diagram

```text
Supply 1 (5V 8A)              Supply 2 (5V 8A)              Supply 3 (12V 5A)
     │                             │                              │
     ├─→ Pico 2 (VBUS)             │                              │
     ├─→ DFPlayer Mini             │                              │
     ├─→ Logic Level Shifter       │                              │
     │                             │                              │
     ├─→ NeoPixels 1-150           ├─→ NeoPixels 151-300          │
     │   (5V + GND)                │   (5V + GND only)            │
     │   Data: GP16 → Pixel 1      │   Data flows through strip   │
     │                             │                              │
     └─→ Common GND ←──────────────┴──────────────────────────────┴─→ Amplifier
                                                                       (12V + GND)
```

**Critical Wiring Notes:**

1. **Data Signal:** Pico GP16 → Pixel 1 → cascades to pixel 300
   - Data connects ONLY at start (pixel 1)
   - Do NOT inject data at midpoint
2. **Power Injection Points:**
   - Supply 1: Pixel 1 (start of strip)
   - Supply 2: Pixel 150/151 (midpoint ~2.5m)
   - Each supply provides 5V + GND to its segment
3. **Common Ground:**
   - Connect GND from all three supplies together
   - Use single heavy wire (18 AWG) between supply GND terminals
   - Ensures clean logic signals and prevents ground loops

4. **Wire Runs:**
   - Keep 5V wires short and thick (18 AWG)
   - Minimise distance from supply to injection point
   - Use stranded wire for flexibility

## 4. Safety

**Fusing:**

- 10A fast-blow fuse on each 5V supply output
- 5A fast-blow fuse on 12V supply output

**Decoupling Capacitors:**

- 1000µF 10V electrolytic at pixel 1 (Supply 1 injection point)
- 1000µF 10V electrolytic at pixel 150 (Supply 2 injection point)
- 100µF 10V electrolytic near Pico VBUS pin
- 100µF 10V electrolytic near DFPlayer Mini VCC pin

**Grounding:**

- All grounds MUST be common for logic signals
- Use star grounding topology (all grounds meet at one point)
- Keep ground wires short and thick (18 AWG minimum)
- If experiencing EMI/noise: use single-point ground connection to amplifier

**Wire Selection:**

- 18 AWG for all 5V power distribution (rated 10A)
- 22 AWG for logic signals (3.3V, GPIO)
- Use stranded wire for flexibility
- Keep power wires as short as practical

## 5. Alternative: Canaduino Power Module

If using CANADUINO Breadboard Power Supply Module:

- **Use for:** Pico 2 and DFPlayer Mini only
- **Configuration:**
  - One rail: 3.3V or 5V for Pico
  - Other rail: 3.3V or 5V for MP3 module
  - 12V rail: Not used (insufficient current for amplifier)
- **Benefits:** Clean regulated power for logic circuits, USB-C input
- **NeoPixel Power:** Still requires two dedicated 5V 8A supplies per board
- **Total per board:** Canaduino (USB-C 2.1A) + 2× 5V 8A + 1× 12V 5A

### 5.1. Level Shifter With Canaduino

If using Canaduino with 3.3V rails:

- **Option 1 (Recommended):** Omit logic level shifter, run NeoPixels with 3.3V data signal
  - WS2812B will work reliably with 3.3V logic when powered at 5V
  - Simplifies wiring, one less component
  - Pico GP16 connects directly to NeoPixel DIN
- **Option 2 (Original Design):** Keep logic level shifter
  - Use Canaduino 5V rail as HV (high voltage) reference
  - Use Canaduino 3.3V rail for Pico LV (low voltage)
  - Maintains 5V data signal for maximum noise immunity

## 6. Verification

Before connecting the strip's data line, check with a meter that every supply shares a common ground and that each fuse is in circuit. Then follow [Test and Debug](./test-and-debug.md).

[← Back to How-To Guides](./README.md)
