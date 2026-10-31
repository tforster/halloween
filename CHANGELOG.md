# Change Log <!-- omit in toc -->

_A detailed history of project versions and associated release notes._

- This project uses **Semantic Versioning 2.0.0**. Please see [SemVer](https://semver.org/) to read the specification.
- All released versions are available as [Releases on this repository](https://github.com/tforster/halloween/releases).

## Table of Contents <!-- omit in toc -->

- [v2026 **Two rigs, one Pico (thunder only)**](#v2026-two-rigs-one-pico-thunder-only)
- [v2025 **Raspberry Pi Pico 2 edition**](#v2025-raspberry-pi-pico-2-edition)
- [v2024 **Initial creation**](#v2024-initial-creation)

## v2026 **Two rigs, one Pico (thunder only)**

Effects for Halloween 2026. See the [2026 Retrospective](docs/explanation/2026-retrospective.md).

- One Pico 2 designed to drive two rigs, each on its own random 60-120 second timer, using `asyncio`
- One shared DFPlayer Mini, amplifier and speaker, latest strike wins; amp fed from DAC_L/DAC_R
- Scheduler and DFPlayer frames tested under host pytest with fakes; Wokwi simulation
- MicroPython v1.29.0; oxlint and oxfmt replace ESLint and Prettier
- WireViz and ASCII wiring diagrams; reused BSS138 level shifter with 1.5 kΩ pull-ups
- Ran thunder only on the night, one timer every 30 seconds: the strips' data signal was corrupt

## v2025 **Raspberry Pi Pico 2 edition**

Effects for Halloween 2025.

- Migrated from ESP32 to Raspberry Pi Pico 2 (RP2350)
- Replaced 8-bit DAC WAV playback with DFPlayer Mini MP3 module (16-bit, 44.1kHz, MicroSD)
- Autonomous random triggering every 60-120 seconds; manual trigger optional
- Three lightning patterns (classic, flickering, rolling) with occasional red "supernatural" strike
- Two independent rigs, each a complete board, with dual 5V supply power injection
- mpremote-based `devops/` scripts for deploy and run

## v2024 **Initial creation**

Effects for Halloween 2024.
