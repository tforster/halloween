# AGENTS.md

> **Version:** 2025 season (Raspberry Pi Pico 2 + MP3 Player Module)  
> **Previous versions:** [2024 (ESP32 + DAC)](https://github.com/tforster/halloween/tree/2024)

This file provides context and instructions for AI coding agents working on the 2025 Halloween Lightning & Thunder Effect project.

## Project Overview

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

## Essential Reading for AI Agents

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
- Explains the dual nature of this project: Pico code (`src/`) vs. host tools (`devops/`)
- Documents all setup steps including virtual environments
- Lists known issues and gotchas you need to be aware of
- Provides testing strategies and debugging approaches

**Quick Links:**

- [Development Environment Setup](docs/Developer-Guide.md#development-environment-setup)
- [DevOps Scripts & Tooling](docs/Developer-Guide.md#devops-scripts--tooling)
- [Testing & Debugging](docs/Developer-Guide.md#testing--debugging)
- [Known Issues & Gotchas](docs/Developer-Guide.md#known-issues--gotchas)

## Development Environment

### Host System Setup

**Primary Development:**

- OS: Linux (WSL2 on Windows)
- Shell: zsh
- Python: 3.13+ (for host tools, not deployed code)
- Node.js: Latest LTS (npm for scripts)
- VS Code with Raspberry Pi Pico extension
- Markdown All In One extension (auto-updates table of contents on save)

**Key Difference from 2024:**

- No longer using esptool, ampy, or mpremote
- Official Raspberry Pi Pico extension handles all firmware and file operations
- Integrated development experience in VS Code

**Important VS Code Extensions:**

1. **Raspberry Pi Pico** (raspberry-pi.raspberry-pi-pico)
   - Handles MicroPython firmware flashing
   - File upload to Pico
   - Integrated REPL and debugging

2. **Markdown All In One** (yzhang.markdown-all-in-one)
   - Automatically generates and updates table of contents in Markdown files
   - Updates ToC on file save (no manual editing required)
   - Do NOT manually edit table of contents sections

### Pico Development Tools

**VS Code Pico Extension:**

```bash
# Install from VS Code marketplace
# Extension ID: raspberry-pi.raspberry-pi-pico

# Extension handles:
# - MicroPython firmware flashing
# - File upload to Pico
# - Integrated REPL
# - Debugging support
```

**Extension Setup:**

1. Install "Raspberry Pi Pico" extension
2. Connect Pico 2 via USB
3. Press `Ctrl+Shift+P` → "MicroPython: Configure Project"
4. Select "Raspberry Pi Pico 2"
5. Extension auto-downloads and flashes MicroPython

### Project Setup

```bash
# Clone repository
git clone https://github.com/tforster/halloween.git
cd halloween
git checkout 2025

# Install Node dependencies (if any)
npm install

# No Python virtual environment needed - code runs on Pico, not host
```

## File Structure Context

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
├── docs/                   # Documentation
│   ├── Developer-Guide.md  # Comprehensive technical documentation
│   └── *.pdf              # Hardware references
└── README.md              # User-facing documentation
```

**Important:**

- Files in `src/` are MicroPython code that runs ON the Pico
- Audio files go on the MicroSD card in the MP3 module, NOT on the Pico
- Use VS Code Pico extension for uploading files

## Hardware Configuration

### Pico 2 Pin Assignments

**To be determined during development (update main.py constants):**

- GPIO X: NeoPixel data output (via 3.3V→5V logic level shifter)
- GPIO X: MP3 module TX (serial communication)
- GPIO X: MP3 module RX (serial communication)
- GPIO X: Trigger input (optional - for manual override)

### Hardware Components (3x sets)

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

## Code Style & Conventions

**MicroPython Code (src/):**

- Snake_case for functions and variables
- UPPER_CASE for constants (e.g., `LED_COUNT`, `LED_PIN`)
- Minimal dependencies (memory constrained)
- Comments for non-obvious behaviour
- No type hints (not supported in MicroPython)
- Keep memory usage low - use buffers, avoid large data structures
- Use British/Canadian English spelling (colour, initialise, synchronised, etc.)

**DFPlayer Mini Communication:**

- Protocol implementation in `mp3_player.py`
- Command format: 7E FF 06 <CMD> 00 <DATA_HIGH> <DATA_LOW> <CHECKSUM> EF
- Always add delays between commands (50-100ms)
- Handle module initialisation delay (500ms after power-on)

**Python Development Tools:**

- PEP 8 style guide
- Type hints preferred for host-side code
- Use virtual environments for host tools
- British/Canadian English spelling in comments and strings

**Documentation:**

- Markdown for all docs
- Keep README.md user-focused and concise
- Technical details belong in docs/Developer-Guide.md
- Use ADR format for architectural decisions
- Use British/Canadian English spelling (licence, colour, synchronise, etc.)
- Markdown All In One extension automatically maintains table of contents
- Do NOT manually edit ToC sections - they update automatically on save

## Common Development Tasks

### Flashing MicroPython to Pico 2

```bash
# VS Code Pico extension handles this automatically
# Manual process:
# 1. Hold BOOTSEL button on Pico 2
# 2. Connect USB cable
# 3. Release BOOTSEL (Pico appears as USB drive)
# 4. Drag .uf2 firmware file to Pico drive
# 5. Pico reboots with MicroPython
```

**Firmware Download:** https://micropython.org/download/RPI_PICO2/

### Uploading Files to Pico 2

```bash
# Using VS Code Pico Extension:
# 1. Right-click file in explorer
# 2. Select "Upload to Pico"
# OR
# 3. Ctrl+Shift+P → "Upload Project to Pico"

# Files are transferred over USB serial
```

### Preparing MP3 Files for SD Card

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

### Testing & Debugging

```bash
# Connect to REPL (VS Code integrated terminal)
# Bottom panel shows Pico REPL automatically

# Test NeoPixels
>>> from lights import light_chaser
>>> import machine, neopixel
>>> np = neopixel.NeoPixel(machine.Pin(LED_PIN), 300)
>>> light_chaser(np)

# Test MP3 player
>>> from mp3_player import MP3Player
>>> player = MP3Player(tx_pin=X, rx_pin=X)
>>> player.play_track(1)

# Test random intervals (reduced for testing)
>>> import random
>>> random.randint(5, 10)  # Instead of 60-120
```

### Standalone Module Testing

```python
# Test lights independently
# Upload lights.py to Pico
# In REPL: import lights

# Test MP3 player independently
# Upload mp3_player.py to Pico
# In REPL: import mp3_player
```

## Testing Instructions

**No automated tests currently exist.** Testing is manual:

1. **NeoPixel Test:**
   - Run `lights.py` standalone
   - Should see light chaser pattern
   - Verify all 300 pixels illuminate

2. **MP3 Player Test:**
   - Initialize player in REPL
   - Send play command for track 1
   - Verify audio output through amplifier
   - Test volume control (0-30 range)

3. **Random Interval Test:**
   - Reduce MIN/MAX_INTERVAL to 5-10 seconds
   - Verify effect triggers automatically
   - Confirm no double-triggering (cooldown works)

4. **Full System Test:**
   - Upload all files
   - Power on and wait for autonomous trigger
   - Verify simultaneous lightning + thunder
   - Test multiple cycles

5. **Multi-Board Test:**
   - Deploy code to all 3 Picos
   - Power on all boards
   - Verify independent operation (not synchronized)
   - Confirm each board has different random intervals

**Future Testing Needs:**

- Unit tests for MP3 player protocol
- Mock tests for UART communication
- Integration tests for full effect cycle
- Regression tests before deployment

## Known Limitations & Gotchas

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

5. **Random Number Generator:**
   - MicroPython uses pseudo-random generator
   - Seed with `random.seed()` for better randomness
   - Consider ADC noise as seed source for true randomness

6. **Power Supply Considerations:**
   - 300 NeoPixels at full white = 18A theoretical
   - Lightning effect uses ~30% = 5-6A typical
   - Amplifier can introduce noise on shared rails
   - Use separate power supplies for logic vs. amplifier

7. **Multi-Board Deployment:**
   - Must update code on all 3 boards individually
   - No centralized update mechanism
   - Test each board independently before final deployment

## Important Code Patterns

### DFPlayer Mini Command Structure

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

### Batched NeoPixel Updates (from 2024)

```python
# Still using batched updates for performance
for i in range(0, len(np), batch_size):
    for j in range(batch_size):
        if i + j < len(np):
            np[i + j] = (240, 248, 255)
    np.write()  # Single write for entire batch
```

### Random Interval Triggering

```python
import random
import time

MIN_INTERVAL = 60
MAX_INTERVAL = 120

while True:
    interval = random.randint(MIN_INTERVAL, MAX_INTERVAL)
    time.sleep(interval)
    trigger_effect()  # Play lightning + thunder
    time.sleep(5)  # Cooldown period
```

## Configuration Changes

To modify behavior, edit constants in `src/main.py`:

```python
LED_COUNT = 300           # Number of NeoPixels
LED_PIN = X               # GPIO for LED data
MP3_TX_PIN = X            # GPIO for MP3 module TX
MP3_RX_PIN = X            # GPIO for MP3 module RX
MIN_INTERVAL = 60         # Minimum seconds between effects
MAX_INTERVAL = 120        # Maximum seconds between effects
```

To change animation speed, modify `lights.py`:

```python
light_chaser(np, wait_ms=2, batch_size=40)  # 2ms delay, 40-pixel batches
```

## Migration Notes from 2024

**Major Changes:**

- **No more WAV parsing:** MP3 module handles all audio decoding
- **No more DAC management:** MP3 module has built-in DAC
- **No more audio streaming:** Files stay on SD card
- **New serial protocol:** Must implement DFPlayer Mini communication
- **Different tooling:** VS Code Pico extension vs. esptool/ampy

**Code Reusability:**

- `lights.py` animation logic can be adapted (same NeoPixel library)
- Threading approach replaced with simpler sequential execution
- Boot process similar but simpler
- Configuration constants similar structure

**What's Gone:**

- `parse_wav_header()` function - not needed
- `play_audio()` function - replaced by MP3 player commands
- Audio buffering logic - handled by hardware
- Manual sample rate timing - handled by hardware

## Future Development Notes

**2025 Season Goals:**

- ✅ Multi-board deployment (3 units)
- ✅ Autonomous random triggering
- ✅ Higher quality audio (MP3 vs. WAV)
- ⏳ Multiple lightning patterns (stretch goal)
- ⏳ Motion sensor integration (optional)

**Code Quality Improvements Needed:**

- Implement comprehensive error handling
- Add MP3 player response validation
- Create audio preparation script
- Add retry logic for serial communication
- Implement watchdog timer for reliability
- Add status LED for troubleshooting

**Hardware Improvements:**

- Design PCB for cleaner assembly
- 3D print enclosures for weather resistance
- Add quick-disconnect connectors
- Status display for configuration

## Git Workflow

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

## Security & Safety

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

## Hardware Resource Links

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

5. **VS Code Pico Extension:**
   - Marketplace: https://marketplace.visualstudio.com/items?itemName=raspberry-pi.raspberry-pi-pico
   - GitHub: https://github.com/raspberrypi/pico-vscode

## Questions to Ask Before Making Changes

1. **Will this work with DFPlayer Mini protocol?** (Check GitHub docs)
2. **Does this affect serial timing?** (UART is sensitive to delays)
3. **Will this work on all 3 boards?** (Consider deployment)
4. **Does this need to persist across reboots?** (Pico has no flash filesystem)
5. **Will this affect NeoPixel timing?** (Still timing-critical)
6. **Is this testable without full hardware?** (Plan for mocking)

## When in Doubt

1. Read the `docs/Developer-Guide.md` for architectural context
2. Check DFPlayer Mini GitHub for protocol details: https://github.com/DFRobot/DFRobotDFPlayerMini
3. Test changes on one board before deploying to all three
4. Use VS Code debugger instead of print statements
5. Keep changes small and testable
6. Document decisions in Developer Guide ADRs
