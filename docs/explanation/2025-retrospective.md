# 2025 Retrospective <!-- omit in toc -->

What happened in the 2025 season, the Pico 2 edition: what worked, what was hard, and what it led to in 2026. The decisions are recorded in [Architecture Decision Records](../reference/adr/README.md); the code is frozen at the [`2025` tag](https://github.com/tforster/halloween/tree/2025).

## Table of Contents <!-- omit in toc -->

- [1. Outcome](#1-outcome)
- [2. Timeline](#2-timeline)
- [3. What Went Well](#3-what-went-well)
- [4. What Was Hard](#4-what-was-hard)
  - [4.1. DFPlayer Mini Serial Protocol](#41-dfplayer-mini-serial-protocol)
  - [4.2. MP3 File Order](#42-mp3-file-order)
  - [4.3. Power for Duplicated Boards](#43-power-for-duplicated-boards)
  - [4.4. Pico 2 Development Workflow](#44-pico-2-development-workflow)
- [5. 2026 Actions](#5-2026-actions)
- [6. Carried-Over Fixes](#6-carried-over-fixes)
- [7. As-Built Photos](#7-as-built-photos)

## 1. Outcome

Halloween 2025 was a success. Two rigs ran, each a complete, independent board: a Pico 2, a DFPlayer Mini, an amplifier and a speaker driving one 300-pixel WS2812B strip, each striking on its own random 60–120 s timer ([ADR-008](../reference/adr/0008-independent-multi-board-operation.md)). The lightning could be seen from a block away and drew people in.

The cost was duplication. Every part was doubled: two Picos, two DFPlayers, two amplifiers, two speakers and six power supplies (two 5 V supplies per strip for power injection, plus a 12 V supply per amplifier), and each board was flashed, wired and debugged on its own.

## 2. Timeline

| Date       | Event                                                                       |
| :--------- | :-------------------------------------------------------------------------- |
| 2025-10-04 | 2025 edition started: ESP32 replaced by the Pico 2 and DFPlayer Mini        |
| 2025-10-31 | Two independent rigs ran on Halloween                                       |
| 2025-11-18 | Last work-in-progress commit                                                |
| 2026-10-25 | 2025 edition merged, cleaned up and tagged `2025` at the start of 2026 work |

## 3. What Went Well

- **The lightning was bright and far-reaching.** Two 300-pixel strips, visible from a block away, drew people to the display.
- **MP3 audio was a big step up from 2024.** The DFPlayer Mini played 16-bit, 44.1 kHz thunder from MicroSD, where the 2024 ESP32 played 8-bit WAV from its DAC.
- **Independent boards were simple and fault-tolerant.** Each rig ran on its own random timer with no communication between boards, so the strikes never fell into a pattern and one board's failure could not stop the other.
- **Autonomous start.** The boards started the storm on power-up with no laptop or button.
- **The BSS138 level shifter board worked over 1 m data runs.** The same board was reused in 2026 ([ADR-013](../reference/adr/0013-reused-bss138-level-shifter.md)).

## 4. What Was Hard

### 4.1. DFPlayer Mini Serial Protocol

The DFPlayer uses its own serial protocol with checksums, documentation is sparse, and most examples are for Arduino. The protocol was implemented from scratch in MicroPython from the [DFRobot library](https://github.com/DFRobot/DFRobotDFPlayerMini), wrapped in a helper class (`src/mp3_player.py`), and each command was tested on its own before integration. The frame format and known-good frames are in [DFPlayer Protocol](../reference/dfplayer-protocol.md).

### 4.2. MP3 File Order

The DFPlayer numbers tracks by the order files were copied to the card, not by name. The fix was to keep source audio separate, number the prepared files `0001.mp3`, `0002.mp3`, …, and copy them in order to a freshly formatted FAT32 card ([Prepare Thunder Audio](../how-to/prepare-audio.md)).

### 4.3. Power for Duplicated Boards

Each board drew about 6 A at 5 V during the lightning effect (300 pixels could draw about 18 A at full white), so each strip took two 5 V supplies, at pixel 1 and pixel 151, and each amplifier its own 12 V supply. Separate supplies per board kept the boards modular and easy to troubleshoot, but meant six supplies and their cabling.

### 4.4. Pico 2 Development Workflow

2025 was the first year on the Pico, and its workflow differs from the ESP32's. mpremote was wrapped in `devops/` shell scripts and exposed as npm scripts ([npm Scripts](../reference/npm-scripts.md)). Each board still had to be flashed separately.

## 5. 2026 Actions

What the 2025 season fed into the [2026 Blueprint](./2026-blueprint.md):

1. **Stop duplicating:** one Pico 2 drives both rigs, with one DFPlayer, amplifier and speaker shared on a latest-strike-wins basis ([ADR-009](../reference/adr/0009-single-controller-for-multiple-rigs.md), [ADR-010](../reference/adr/0010-single-shared-audio-path.md)). Done in 2026.
2. **Run both rigs from one program** with `asyncio`, one task per rig ([ADR-011](../reference/adr/0011-asyncio-scheduling.md)). Done in 2026.
3. **Test the firmware off the device:** the scheduler and DFPlayer frames under host pytest with fakes, plus a Wokwi simulation. Done in 2026.

## 6. Carried-Over Fixes

Found in the 2025 code and docs during 2026 work, and fixed in 2026:

- **Amplifier feed:** the 2025 guide fed the amplifier from SPK_1/SPK_2, the DFPlayer's own 3 W speaker driver. 2026 uses the line outputs DAC_L/DAC_R.
- **Repeating storm:** the random generator was seeded from `time.ticks_ms()`, which is much the same on every boot. 2026 seeds it from `os.urandom` ([Known Issues](../reference/known-issues.md#6-randomness)).
- **Red strike:** the code struck red 20% of the time against a documented 10%. 2026 fixed it to 10%.
- **Play-track checksum:** the documented play-track-1 frame ended `FE F9`; the correct checksum is `FE F7`.

## 7. As-Built Photos

No photos of the 2025 build were kept in the repo.

[← Back to Explanation](./README.md)
