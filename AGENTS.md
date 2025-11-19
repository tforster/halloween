# AGENTS.md <!-- omit from toc -->

> **Version:** 2025 season (Raspberry Pi Pico 2 + MP3 Player Module)  
> **Previous versions:** [2024 (ESP32 + DAC)](https://github.com/tforster/halloween/tree/2024)

This file provides context and instructions for AI coding agents working on the 2025 Halloween Lightning & Thunder Effect project.

## Table of Contents <!-- omit from toc -->

- [1. Project Overview](#1-project-overview)
- [2. Essential Reading for AI Agents](#2-essential-reading-for-ai-agents)
- [3. Development Environment](#3-development-environment)
  - [3.1. Host System Setup](#31-host-system-setup)
  - [3.2. Pico Development Tools](#32-pico-development-tools)
  - [3.3. Project Setup](#33-project-setup)
- [4. File Structure Context](#4-file-structure-context)
- [5. Hardware Configuration](#5-hardware-configuration)
  - [5.1. Hardware Components (3x sets)](#51-hardware-components-3x-sets)
- [6. Code Style \& Conventions](#6-code-style--conventions)
- [7. Common Development Tasks](#7-common-development-tasks)
  - [7.1. Flashing MicroPython to Pico 2](#71-flashing-micropython-to-pico-2)
  - [7.2. Uploading Files to Pico 2](#72-uploading-files-to-pico-2)
  - [7.3. Preparing MP3 Files for SD Card](#73-preparing-mp3-files-for-sd-card)
  - [7.4. Testing \& Debugging](#74-testing--debugging)
- [8. Known Limitations \& Gotchas](#8-known-limitations--gotchas)
- [9. Important Code Patterns](#9-important-code-patterns)
  - [9.1. DFPlayer Mini Command Structure](#91-dfplayer-mini-command-structure)
- [10. Future Development Notes](#10-future-development-notes)
- [11. Git Workflow](#11-git-workflow)
- [12. Security \& Safety](#12-security--safety)
- [13. Hardware Resource Links](#13-hardware-resource-links)
- [14. Questions to Ask Before Making Changes](#14-questions-to-ask-before-making-changes)
- [15. When in Doubt](#15-when-in-doubt)

## 1. Project Overview

This is a Raspberry Pi Pico 2 + MicroPython project that creates synchronized lightning and thunder effects for Halloween displays. The system:

- Runs on Raspberry Pi Pico 2 microcontroller with MicroPython
- Controls 300+ WS2812B NeoPixel LEDs for lightning animation
- Plays high-quality MP3 audio through a dedicated DFPlayer Mini module connected to a 60W amplifier
- Operates autonomously with random triggering (60-120 second intervals)
- Deploys across 3 independent boards for multi-zone effects

**Key Technologies:**

- MicroPython on Raspberry Pi Pico 2 (RP2350)
- NeoPixel (WS2812B) LED control
- DFPlayer Mini MP3 player module (UART serial communication)
- Random interval triggering
- Multi-board independent operation

**Key Changes from 2024:**

- **Microcontroller:** ESP32 → Raspberry Pi Pico 2
- **Audio:** Built-in DAC → External MP3 module with SD card
- **Audio Quality:** 8-bit WAV → 16-bit MP3 (CD quality)
- **Triggering:** Manual only → Autonomous random intervals
- **Scale:** 1 board → 3 independent boards

## 2. Essential Reading for AI Agents

**⚠️ IMPORTANT: Before making any changes, read these documents:**

1. **[Developer Guide](docs/Developer-Guide.md)** - **READ THIS FIRST**
   - Architecture Decision Records (ADRs) explaining why choices were made
   - Technical challenges and their solutions
   - Complete setup instructions (virtual environments, dependencies)
   - DevOps scripts documentation
   - Hardware assembly notes
   - Testing and debugging strategies
   - Known issues and gotchas

2. **This file (AGENTS.md)** - Context and conventions
   - Project overview and key technologies
   - Development environment setup
   - Code style conventions
   - File structure
   - Common development tasks

3. **README.md** - User-facing documentation
   - High-level overview
   - Quick start guide
   - Basic usage instructions

**Why read the Developer Guide?**

- Contains complete context on **why** decisions were made (ADRs)
- Documents all setup steps and daily workflow
- Provides detailed testing strategies and debugging approaches
- Tracks implementation-specific bugs and workarounds
- Includes code patterns and configuration details

**Why read AGENTS.md?**

- Hardware specifications and purchase links
- Code style conventions and naming guidelines
- Common development procedures
- Hardware/protocol constraints and limitations
- Project structure and workflow

**Quick Links to Developer Guide:**

- [Development Environment Setup](docs/Developer-Guide.md#development-environment-setup)
- [DevOps Scripts & Tooling](docs/Developer-Guide.md#devops-scripts--tooling)
- [Testing & Debugging](docs/Developer-Guide.md#testing--debugging)
- [Known Issues & Gotchas](docs/Developer-Guide.md#known-issues--gotchas)

## 3. Development Environment

### 3.1. Host System Setup

**Primary Development:**

- System 1 OS: Linux (WSL2 on Windows)
- System 2 OS: Debian 13 (ChromeOS with Linux development environment enabled)
- Shell: zsh
- Node.js: Latest LTS (npm for devops scripts)
- VS Code
- Markdown All In One extension (auto-updates table of contents on save)

**Key Difference from 2024:**

- No longer using esptool or ampy

**Important VS Code Extensions:**

1. **Markdown All In One** (yzhang.markdown-all-in-one)
   - Automatically generates and updates table of contents in Markdown files
   - Updates ToC on file save (no manual editing required)
   - Do NOT manually edit table of contents sections

### 3.2. Pico Development Tools

- mpremote is installed in Linux environment for Pico interaction.
- `devops/deploy.sh` and `devops/run.sh` scripts use mpremote under the hood.

### 3.3. Project Setup

> [!note]
>
> Complete development environment setup instructions including prerequisites, dependencies, and daily workflow are maintained in the Developer Guide.
> See [Development Environment Setup](docs/Developer-Guide.md#development-environment-setup) for detailed instructions.

## 4. File Structure Context

```shell
/home/tforster/dev/TroyForster/Halloween/
├── src/                    # MicroPython source code (deployed to Pico)
│   ├── boot.py            # Bootstrap loader (runs on Pico startup)
│   ├── main.py            # Main application with random triggering
│   ├── lights.py          # NeoPixel animation module
│   ├── mp3_player.py      # DFPlayer Mini serial interface
│   └── test.py            # Development testing
├── lib/                    # (empty - using built-in modules)
├── audio/                  # MP3 files (deployed to SD card, not Pico)
│   ├── 0001.mp3           # Thunder sound 1
│   ├── 0002.mp3           # Thunder sound 2
│   └── 0003.mp3           # Thunder sound 3
├── devops/                 # Host-side development tools
│   ├── prepare_audio.py   # MP3 file preparation script
│   └── test_mp3_serial.py # Serial communication tester
├── docs/                   # Documentation
│   ├── Developer-Guide.md  # Comprehensive technical documentation
│   └── *.pdf              # Hardware references
└── README.md              # User-facing documentation
```

**Important:**

- Files in `src/` are MicroPython code that runs ON the Pico
- Files in `devops/` are mostly bash scripts that run on your HOST machine
- Audio files go on the MicroSD card in the MP3 module, NOT on the Pico

> [!note]
> Detailed file structure with comprehensive explanations of each directory and file is maintained in the Developer Guide.
> See [Project File Structure](docs/Developer-Guide.md#project-file-structure) for complete details.

## 5. Hardware Configuration

> [!note]
> Pin assignments are determined during development and documented in the Developer Guide.
> See [Hardware Assembly Notes](docs/Developer-Guide.md#hardware-assembly-notes) for current pin mappings.

### 5.1. Hardware Components (3x sets)

**Per Board:**

1. **Raspberry Pi Pico 2**
   - RP2350 dual-core processor
   - 520KB SRAM (vs. 160KB on ESP32)
   - MicroPython support
   - Cost: ~$6

2. **Mini MP3 Player Module (DFPlayer Mini)**
   - Purchase: https://www.universal-solder.ca/product/mini-mp3-player-module-with-microsd-slot-for-arduino-etc/
   - Documentation: https://github.com/DFRobot/DFRobotDFPlayerMini
   - 9600 baud UART serial communication
   - 16-bit DAC, 44.1kHz sample rate
   - MicroSD card for MP3 storage
   - Cost: ~$3

3. **60W BTL Class D Amplifier**
   - Purchase: https://www.amazon.ca/dp/B0D8HCV43H
   - 12V input
   - 60W output power
   - Connect to MP3 module audio output

4. **300 WS2812B NeoPixels** (configurable via `LED_COUNT`)

5. **Logic Level Shifter** (3.3V→5V for NeoPixel data)

6. **Power Supplies:**
   - 5V supply for Pico + NeoPixels (5-6A minimum)
   - 12V supply for amplifier

## 6. Code Style & Conventions

**MicroPython Code (src/):**

- camelCase for functions and variables
- UPPER_CASE for constants (e.g., `LED_COUNT`, `LED_PIN`)
- Minimal dependencies (memory constrained)
- **Comprehensive inline code comments required:**
  - Document hardware constraints and GPIO pin assignments
  - Explain timing-critical sections (NeoPixel updates, UART delays)
  - Document protocol implementations (DFPlayer command format, checksums)
  - Explain non-obvious behaviour and workarounds
  - Include references to datasheets/specs where applicable
- No type hints (not supported in MicroPython)
- Keep memory usage low - use buffers, avoid large data structures
- Use British/Canadian English spelling (colour, initialise, synchronised, etc.)

**DFPlayer Mini Communication:**

- Protocol implementation in `mp3_player.py`
  <!-- eslint-disable-next-line markdown/no-html-->
- Command format: 7E FF 06 <CMD> 00 <DATA_HIGH> <DATA_LOW> <CHECKSUM> EF
- Always add delays between commands (50-100ms)
- Handle module initialisation delay (500ms after power-on)

**Python Development Tools:**

- PEP 8 style guide
- Type hints preferred for host-side code
- British/Canadian English spelling in comments and strings

**Documentation:**

- Markdown for all docs
- Do not use `---` for horizontal rules (conflicts with current markdown stylesheet)
- Keep README.md user-focused and concise
- Technical details belong in docs/Developer-Guide.md
- Use ADR format for architectural decisions
- Use British/Canadian English spelling (licence, colour, synchronise, etc.)
- Markdown All In One extension automatically maintains table of contents
- Do NOT manually edit ToC sections - they update automatically on save

## 7. Common Development Tasks

### 7.1. Flashing MicroPython to Pico 2

```bash
# Manual process:
# 1. Hold BOOTSEL button on Pico 2
# 2. Connect USB cable
# 3. Release BOOTSEL (Pico appears as USB drive)
# 4. Drag .uf2 firmware file to Pico drive
# 5. Pico reboots with MicroPython
```

**Firmware Download:** https://micropython.org/download/RPI_PICO2/

### 7.2. Uploading Files to Pico 2

```bash
devops/deploy.sh
```

### 7.3. Preparing MP3 Files for SD Card

```bash
# CRITICAL: File naming and order matter!

# 1. Format MicroSD card as FAT32
# 2. Rename audio files:
#    thunder1.mp3 → 0001.mp3
#    thunder2.mp3 → 0002.mp3
#    thunder3.mp3 → 0003.mp3
# 3. Copy files to SD card ROOT directory in numerical order
# 4. First file copied becomes track 1 (regardless of name)

# Pro tip: Format card, then copy files in order to avoid confusion
```

### 7.4. Testing & Debugging

```bash
# Connect to REPL and test modules independently

# Test NeoPixels
>>> from lights import light_chaser
>>> import machine, neopixel
>>> np = neopixel.NeoPixel(machine.Pin(LED_PIN), 300)
>>> light_chaser(np)

# Test MP3 player
>>> from mp3_player import MP3Player
>>> player = MP3Player(tx_pin=X, rx_pin=X)
>>> player.play_track(1)
```

> [!note]
> Comprehensive testing procedures, debugging strategies, and detailed test cases are maintained in the Developer Guide.
> See [Testing & Debugging](docs/Developer-Guide.md#testing--debugging) for complete details.

## 8. Known Limitations & Gotchas

1. **MP3 File Naming is CRITICAL:**
   - DFPlayer Mini expects specific format: 0001.mp3, 0002.mp3, etc.
   - Order files are copied matters (first = track 1)
   - Recommend: Format card fresh, copy files in numerical order
   - Test playback BEFORE deploying to display

2. **DFPlayer Mini Initialization:**
   - Module needs 500ms startup time after power-on
   - Always add `time.sleep(0.5)` before first command
   - Some modules need explicit init command (0x3F)

3. **Serial Communication Reliability:**
   - Use 9600 baud (faster rates unreliable)
   - Add 50-100ms delays between commands
   - Implement checksum validation for responses
   - Module sometimes doesn't respond - add retries

4. **NeoPixel Timing (still applies):**
   - WS2812B protocol is timing-sensitive
   - Avoid blocking operations during updates
   - Logic level shifting still required (3.3V → 5V)

5. **Power Supply Considerations:**
   - 300 NeoPixels at full white = 18A theoretical
   - Lightning effect uses ~30% = 5-6A typical
   - Amplifier can introduce noise on shared rails
   - Use separate power supplies for logic vs. amplifier

6. **Multi-Board Deployment:**
   - Must update code on all 3 boards individually
   - No centralized update mechanism
   - Test each board independently before final deployment

> [!note]
> Implementation-specific bugs, workarounds, and development gotchas are tracked in the Developer Guide.
> See [Known Issues & Gotchas](docs/Developer-Guide.md#known-issues--gotchas) for current implementation issues.

## 9. Important Code Patterns

### 9.1. DFPlayer Mini Command Structure

```python
# Command format (10 bytes):
# [0] 0x7E - Start byte
# [1] 0xFF - Version
# [2] 0x06 - Length (always 6)
# [3] CMD - Command byte
# [4] 0x00 - Feedback (no feedback)
# [5] DATA_HIGH - Parameter high byte
# [6] DATA_LOW - Parameter low byte
# [7] CHECKSUM_HIGH - Checksum high byte
# [8] CHECKSUM_LOW - Checksum low byte
# [9] 0xEF - End byte

# Example: Play track 1
cmd = bytearray([0x7E, 0xFF, 0x06, 0x03, 0x00, 0x00, 0x01, 0xFE, 0xF9, 0xEF])
uart.write(cmd)
```

> [!note]
> Implementation-specific code patterns and examples are maintained in the Developer Guide.
> See [Code Structure](docs/Developer-Guide.md#code-structure) for detailed code patterns and configuration options.

> [!note]
> Detailed migration notes from the 2024 ESP32 implementation are documented in the Developer Guide.
> See [ADR-005: Migration from ESP32 to Raspberry Pi Pico 2](docs/Developer-Guide.md#adr-005-migration-from-esp32-to-raspberry-pi-pico-2-2025) for complete comparison and rationale.

## 10. Future Development Notes

**2025 Season Goals:**

- ✅ Multi-board deployment (3 units)
- ✅ Autonomous random triggering
- ✅ Higher quality audio (MP3 vs. WAV)
- ⏳ Multiple lightning patterns (stretch goal)

## 11. Git Workflow

**Current State:**

- Branch: `2025` (active development)
- Main branch: Tagged as `2024`
- Previous implementation: `2024` tag

**Workflow:**

- All 2025 development happens on `2025` branch
- Commit messages follow conventional commits format
- Reference issues/features in commit messages
- Keep commits atomic and focused
- End of 2025 season: Squash, merge to main, tag as `2025`

## 12. Security & Safety

**Electrical Safety:**

- Verify power supply ratings before connecting LEDs (5-6A minimum)
- Use appropriate wire gauge for high-current LED power
- Isolate 5V (logic/LEDs) from 12V (amplifier) circuits
- Never exceed Pico GPIO current limits (12mA per pin)
- Add fuses to power supplies

**Code Safety:**

- No network connectivity (air-gapped system)
- No sensitive data stored on devices
- Audio files are static, no user uploads
- GPIO inputs use pull-up/pull-down resistors

## 13. Hardware Resource Links

**Must-Reference Documentation:**

1. **MP3 Player Module:**
   - Purchase: https://www.universal-solder.ca/product/mini-mp3-player-module-with-microsd-slot-for-arduino-etc/
   - DFRobot GitHub (protocol specs): https://github.com/DFRobot/DFRobotDFPlayerMini
   - DFRobot Wiki: https://wiki.dfrobot.com/DFPlayer_Mini_SKU_DFR0299

2. **60W Amplifier:**
   - Purchase: https://www.amazon.ca/dp/B0D8HCV43H
   - Specifications: 60W BTL, 12V input

3. **Raspberry Pi Pico 2:**
   - Product: https://www.raspberrypi.com/products/raspberry-pi-pico-2/
   - Datasheet: https://datasheets.raspberrypi.com/pico/pico-2-datasheet.pdf
   - MicroPython: https://docs.micropython.org/en/latest/rp2/

4. **WS2812B NeoPixels:**
   - Datasheet: https://cdn-shop.adafruit.com/datasheets/WS2812B.pdf

## 14. Questions to Ask Before Making Changes

1. **Will this work with DFPlayer Mini protocol?** (Check GitHub docs)
2. **Does this affect serial timing?** (UART is sensitive to delays)
3. **Will this work on all 3 boards?** (Consider deployment)
4. **Does this need to persist across reboots?** (Pico has no flash filesystem)
5. **Will this affect NeoPixel timing?** (Still timing-critical)
6. **Is this testable without full hardware?** (Plan for mocking)

## 15. When in Doubt

1. Read the `docs/Developer-Guide.md` for architectural context
2. Check DFPlayer Mini GitHub for protocol details: https://github.com/DFRobot/DFRobotDFPlayerMini
3. Test changes on one board before deploying to all three
4. Use VS Code debugger instead of print statements
5. Keep changes small and testable
6. Document decisions in Developer Guide ADRs
