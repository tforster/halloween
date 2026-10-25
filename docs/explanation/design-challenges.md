# Design Challenges <!-- omit in toc -->

Problems met while building the 2025 Pico 2 edition and how each was solved. The decisions they led to are recorded in [Architecture Decision Records](../reference/adr/README.md).

## Table of Contents <!-- omit in toc -->

- [1. DFPlayer Mini Serial Communication](#1-dfplayer-mini-serial-communication)
- [2. MP3 File Naming Convention](#2-mp3-file-naming-convention)
- [3. Power Distribution for Three Boards](#3-power-distribution-for-three-boards)
- [4. Pico 2 Development Workflow](#4-pico-2-development-workflow)

## 1. DFPlayer Mini Serial Communication

**Problem:**  
DFPlayer Mini uses proprietary serial protocol with checksums and specific command structure. Documentation is sparse and examples are mostly for Arduino.

**Solution:**

- Implement protocol from scratch in MicroPython based on [DFRobot specs](https://github.com/DFRobot/DFRobotDFPlayerMini)
- Command format: `7E FF 06 <CMD> 00 <DATA_HIGH> <DATA_LOW> <CHECKSUM_HIGH> <CHECKSUM_LOW> EF`
- Create helper class to encapsulate protocol complexity
- Test each command individually before integration

**Key Commands:**

- `0x03`: Specify track to play
- `0x0D`: Play track from root folder
- `0x06`: Set volume (0-30)
- `0x3F`: Initialise module

**Code Reference:** `src/mp3_player.py`

## 2. MP3 File Naming Convention

**Problem:**  
DFPlayer Mini expects specific file naming: `0001.mp3`, `0002.mp3`, etc. Files must be copied to SD card in specific order (first file copied becomes 0001).

**Solution:**

- Create audio preparation script that:
  1. Formats SD card as FAT32
  2. Renames audio files with proper numbering
  3. Copies files in correct order
- Keep source audio files separate from numbered versions

The steps are in [Prepare Thunder Audio](../how-to/prepare-audio.md).

## 3. Power Distribution for Three Boards

**Problem:**  
Three complete boards means:

- 3x 5V supplies for Pico + NeoPixels (5-6A each)
- 3x 12V supplies for amplifiers
- Cable management for 6 power supplies

**Solution:**

- **Option 1:** Single high-capacity 5V supply (18A+) with distribution
- **Option 2:** Three separate 5V supplies (simpler, more modular)
- **Amplifiers:** Three separate 12V supplies (already purchased)

**Recommendation:** Use separate 5V supplies for modularity and easier troubleshooting.

**Power Budget (per board):**

- Pico 2: ~100mA
- MP3 Module: ~50mA
- NeoPixels (300 @ white): ~18A maximum (theoretical)
- NeoPixels (lightning effect): ~5-6A typical (30% duty cycle)
- **Total per board:** 6A at 5V (30W)

## 4. Pico 2 Development Workflow

**Problem:**  
First time using Raspberry Pi Pico platform. Workflow differs from ESP32 development.

**Solution:**

- Wrap mpremote in `devops/` shell scripts and expose them as npm scripts. See [npm Scripts](../reference/npm-scripts.md).

[← Back to Explanation](./README.md)
