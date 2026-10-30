# ADR-009: Single Controller for Multiple Rigs <!-- omit in toc -->

**Status:** Accepted (2026 season). Supersedes [ADR-008](./0008-independent-multi-board-operation.md).

**Context:**
In 2025 three complete boards each drove one strip: three Pico 2s, three MP3 players, three amplifiers, three speakers and nine supplies, each flashed, wired and debugged separately ([ADR-008](./0008-independent-multi-board-operation.md)). For 2026 the display shrinks to two rigs that reuse the 2025 300-pixel strips ([2026 blueprint](../../explanation/2026-blueprint.md#1-problem-statement)). Options:

1. **Two independent boards:** repeat 2025 with two boards. Twice the controller, audio and deployment work.
2. **One controller, rigs far apart:** one Pico 2 with long data runs. Past about 3 m unbuffered, WS2812B data needs a buffer or a differential link.
3. **One controller, central placement:** one Pico 2 between the rigs, each strip's pixel 1 no more than 2.7 m from the level shifter.

**Decision:**
One Raspberry Pi Pico 2 in a central enclosure drives both rigs: rig A data on GP16, rig B on GP17, through two channels of the reused BSS138 level shifter board ([ADR-013](./0013-reused-bss138-level-shifter.md); this record first named a 74AHCT125 in error) and a 330 Ω series resistor at each strip's data input. Each data run is a twisted data/ground pair of at most 2.7 m. The rigs are a configuration list, so the firmware is not tied to two. The wiring is in the [WireViz harness](../assets/wiring.yml).

**Rationale:**

- **One deployment:** one board to flash, power and debug
- **Still independent timing:** each rig runs its own random 60–120 s timer as an `asyncio` task ([ADR-011](./0011-asyncio-scheduling.md)), so the storm keeps the 2025 unpredictability without a second board
- **No extra data hardware:** 2.7 m is a commonly cited ~3 m unbuffered limit less 10%, so no buffer or differential link is needed
- **Clean logic power:** a dedicated 5 V logic supply feeds the Pico, DFPlayer and level shifter, so a full-white flash on a strip never sags the controller's rail, and no 5 V power runs the 2.7 m back from a strip

**Consequences:**

- Strip starts can be at most about 5.4 m apart; a wider layout means revisiting this decision
- One controller fault darkens both rigs, where 2025 lost only one
- Six supplies instead of nine: one 5 V logic, two 5 V per rig and one 12 V for the amplifier
- The Pico takes its power through a Schottky diode into VSYS, so a laptop can be plugged in to debug while the display is powered

[← Back to ADR index](./README.md)
