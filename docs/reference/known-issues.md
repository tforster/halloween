# Known Issues <!-- omit in toc -->

Hardware and protocol constraints that cause problems if forgotten, with the workaround for each.

## Table of Contents <!-- omit in toc -->

- [1. SD Card Track Order](#1-sd-card-track-order)
- [2. DFPlayer Start-Up](#2-dfplayer-start-up)
- [3. Serial Reliability](#3-serial-reliability)
- [4. NeoPixel Timing](#4-neopixel-timing)
- [5. Power and Noise](#5-power-and-noise)
- [6. Randomness](#6-randomness)
- [7. Multi-Board Updates](#7-multi-board-updates)

## 1. SD Card Track Order

The DFPlayer numbers tracks by the order files were written to the card, not by file name. Format the card and copy `0001.mp3`, `0002.mp3`, … in order; see [Prepare Thunder Audio](../how-to/prepare-audio.md). Test track 1 before deploying.

## 2. DFPlayer Start-Up

The module ignores commands until it has booted, and some modules also need the initialise command (`0x3F`). `MP3Player` waits and initialises; the delays are in [Timing](./dfplayer-protocol.md#5-timing).

## 3. Serial Reliability

Faster baud rates and back-to-back commands both lose frames; keep to the [serial settings](./dfplayer-protocol.md#1-serial-settings) and [command spacing](./dfplayer-protocol.md#5-timing). The module still misses an occasional command, and since feedback is off, a retry is the only remedy.

## 4. NeoPixel Timing

WS2812B data is timing-sensitive. A full 300-pixel write blocks for about 9 ms; keep other work out of that window. The data line still needs 3.3 V → 5 V level shifting.

The reused BSS138 level shifter board ([ADR-013](./adr/0013-reused-bss138-level-shifter.md)) pulls each high-side output up through only 10 kΩ. Over a 2.7 m twisted pair, about 140 pF, that rising edge takes about 1.4 µs, longer than a 1.25 µs WS2812B bit, so pixels glitch or stay dark; 1 m worked in 2025. A 1.5 kΩ resistor across HV1–HV and HV2–HV brings the time constant to about 0.2 µs, while each Pico pin sinks only about 3.6 mA when low. Bench-test each rig through its real cable. If it still glitches, feed pixel 1's +5V through a 1N400x diode: pixel 1 then runs at about 4.3 V, reads 3.3 V data as high, and passes a clean signal down the strip.

## 5. Power and Noise

- 300 pixels at full white draw about 18 A in theory; the lightning effect averages 5–6 A.
- The amplifier injects switching noise into a shared rail. Give it its own 12 V supply, share only ground, and fit decoupling capacitors near the Pico and DFPlayer. Details are in [Hardware](./hardware.md#4-power-supplies).

## 6. Randomness

MicroPython's `random` is pseudo-random. 2025 seeded it from `time.ticks_ms()`, which is much the same on every boot, so the storm repeated itself. `main.start()` now seeds it from `os.urandom`, which draws on the RP2350's hardware entropy. Since MicroPython 1.28 the rp2 port takes `os.urandom` from the pico-sdk's `pico_rand` (which uses the RP2350's TRNG) instead of the ring oscillator, and `os.urandom` raises on a negative length; the seed reads a fixed 4 bytes, so neither changes the firmware.

## 7. Multi-Board Updates

There is no central update mechanism: each board is flashed separately. Test one board before updating the rest.

[← Back to Reference](./README.md)
