# ADR-013: Reused BSS138 Level Shifter Board <!-- omit in toc -->

**Status:** Accepted (2026 season)

**Context:**
The 2026 build reuses the 2025 parts wherever it can ([ADR-009](./0009-single-controller-for-multiple-rigs.md)). The first version of the [2026 blueprint](../../explanation/2026-blueprint.md#41-hardware) named a 74AHCT125 as the level shifter in error. The 2025 boards actually used a generic 4-channel BSS138 MOSFET level shifter board (HV1–4, LV1–4, HV, LV, GND), and that is the part on hand.

The BSS138 board drives a low actively, but its high side rises only through a 10 kΩ pull-up. In 2025 each data run was about 1 m, and the edge was fast enough. In 2026 each run is up to 2.7 m. At about 50 pF/m of twisted pair, the time constant becomes about 1.4 µs, longer than a 1.25 µs WS2812B bit.

**Decision:**

- **Level shifter:** use the reused BSS138 board. LV comes from the Pico's 3V3 and HV from the 5 V bus. GP16 and GP17 drive LV1 and LV2, and HV1 and HV2 go out to the rigs through the 330 Ω series resistors. Channels 3 and 4 stay unwired.
- **Pull-up:** solder a 1.5 kΩ pull-up across HV1–HV and HV2–HV.
  - In parallel with the board's 10 kΩ, that is about 1.3 kΩ, which cuts the time constant over 2.7 m to about 0.2 µs.
  - When the line is low, the Pico pin sinks about 3.6 mA, within its default 4 mA drive and the 12 mA limit.
- **Pin guide:** the board prints labels, not pin numbers. [`level-shifter.jpg`](../assets/level-shifter.jpg) labels each pin with its connection.

The blueprint, [`wiring.yml`](../assets/wiring.yml) and the hardware docs are corrected to this board.

**Rationale:**

- **Reuse:** the board is already on hand, so it costs nothing, and it worked in 2025.
- **Smallest fix for the longer runs:** the rise time is a property of the board's pull-ups, so two resistors fix it; the firmware does not change.

**Consequences:**

- Data integrity over 2.7 m depends on the pull-ups. Bench-test each rig through its real cable before installing.
- If pixels still glitch, feed pixel 1's +5V through a 1N400x diode. Pixel 1 then runs at about 4.3 V and reads 3.3 V data as high ([Known Issues](../known-issues.md#4-neopixel-timing)).
- A buffer with active high and low drive, such as a 74AHCT125, would remove the dependence on the pull-ups. It is a candidate if a future season needs longer runs.

[← Back to ADR index](./README.md)
