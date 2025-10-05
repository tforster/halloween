# Developer Guide <!-- omit in toc -->

> **Historical Note:** This guide documents the **2025 Raspberry Pi Pico 2 implementation**.  
> For the 2024 ESP32 version, see the [`2024` tag](https://github.com/tforster/halloween/tree/2024).

A living document of design decisions, challenges, and solutions for the Halloween Lightning & Thunder effect system.

## Table of Contents <!-- omit in toc -->

- [Architecture Decision Records (ADRs)](#architecture-decision-records-adrs)
  - [ADR-005: Migration from ESP32 to Raspberry Pi Pico 2 (2025)](#adr-005-migration-from-esp32-to-raspberry-pi-pico-2-2025)
  - [ADR-006: External MP3 Player Module for Audio](#adr-006-external-mp3-player-module-for-audio)
  - [ADR-007: Random Interval Autonomous Triggering](#adr-007-random-interval-autonomous-triggering)
  - [ADR-008: Multi-Board Independent Operation](#adr-008-multi-board-independent-operation)
- [Technical Challenges \& Solutions](#technical-challenges--solutions)
  - [Challenge: DFPlayer Mini Serial Communication](#challenge-dfplayer-mini-serial-communication)
  - [Challenge: MP3 File Naming Convention](#challenge-mp3-file-naming-convention)
  - [Challenge: Power Distribution for Three Boards](#challenge-power-distribution-for-three-boards)
  - [Challenge: Pico 2 Development Workflow](#challenge-pico-2-development-workflow)
- [Development Environment Setup](#development-environment-setup)
  - [Initial Project Setup (One Time)](#initial-project-setup-one-time)
  - [Daily Development Workflow](#daily-development-workflow)
  - [Virtual Environment Quick Reference](#virtual-environment-quick-reference)
  - [NPM Scripts Reference](#npm-scripts-reference)
  - [Project File Structure](#project-file-structure)
  - [VS Code Pico Extension Setup](#vs-code-pico-extension-setup)
  - [MicroPython on Pico 2](#micropython-on-pico-2)
- [Hardware Assembly Notes](#hardware-assembly-notes)
- [Code Structure](#code-structure)
- [Testing \& Debugging](#testing--debugging)
- [DevOps Scripts \& Tooling](#devops-scripts--tooling)
  - [Virtual Environment Setup](#virtual-environment-setup)
  - [Audio Preparation Script](#audio-preparation-script)
  - [MP3 Serial Communication Tester](#mp3-serial-communication-tester)
  - [Python Code Quality Tools](#python-code-quality-tools)
  - [Project Configuration Files](#project-configuration-files)
  - [Adding New DevOps Scripts](#adding-new-devops-scripts)
  - [Deployment to Pico](#deployment-to-pico)
- [Known Issues \& Gotchas](#known-issues--gotchas)
- [Future Improvements](#future-improvements)
- [Hardware References](#hardware-references)

## Architecture Decision Records (ADRs)

### ADR-005: Migration from ESP32 to Raspberry Pi Pico 2 (2025)

**Status:** Accepted (2025 season)

**Context:**  
2024 implementation used ESP32 with built-in DAC for audio. While functional, several limitations were encountered:

- 8-bit DAC audio quality insufficient for impactful thunder sounds
- Manual WAV parsing added code complexity and memory overhead
- ESP32 cost made scaling to 3 units expensive (~$30-40 per unit)
- Memory constraints limited future expansion possibilities
- DAC volume clipping issues without proper protection

**Decision:**  
Migrate to Raspberry Pi Pico 2 with dedicated MP3 player module for 2025 season.

**Comparison to 2024:**

| Aspect              | 2024 (ESP32)                      | 2025 (Pico 2)                       |
| ------------------- | --------------------------------- | ----------------------------------- |
| **Microcontroller** | ESP32-WROOM                       | Raspberry Pi Pico 2 (RP2350)        |
| **Audio Output**    | Built-in 8-bit DAC                | External MP3 module                 |
| **Audio Format**    | WAV (manual parsing)              | MP3 (hardware decoding)             |
| **Audio Quality**   | 8-bit, ~31kHz sample rate         | 16-bit, 44.1kHz (CD quality)        |
| **Audio Storage**   | ESP32 flash (limited)             | MicroSD card (expandable)           |
| **Code Complexity** | High (WAV parsing, streaming)     | Low (simple serial commands)        |
| **Cost per Unit**   | ~$10-12 (ESP32 alone)             | ~$6 (Pico 2) + $3 (MP3 module) = $9 |
| **Scaling**         | Single unit (costly to replicate) | 3 units (cost-effective)            |
| **Memory**          | ~160KB usable RAM                 | ~520KB SRAM                         |
| **Development**     | esptool, ampy, mpremote           | VS Code Pico extension              |

**Rationale:**

- **Superior audio quality:** Dedicated hardware MP3 decoder delivers true CD-quality sound
- **Simpler code:** No manual audio parsing, streaming, or DAC management
- **Better audio management:** Easy to add/change sounds via SD card
- **More cost-effective:** Lower total cost enables 3-board deployment
- **Easier development:** VS Code Pico extension provides integrated tooling
- **Future-proof:** More memory headroom for additional features
- **Better availability:** Pico 2 easier to source than ESP32

**Consequences:**

- Team must learn Pico 2 platform and tooling
- Existing ESP32 code not reusable (complete rewrite required)
- Additional hardware component (MP3 module) adds complexity
- Serial communication protocol must be implemented for MP3 control
- Logic level shifting still required for NeoPixels

**Historical Reference:** See [2024 ESP32 implementation](https://github.com/tforster/halloween/tree/2024) for comparison.

---

### ADR-006: External MP3 Player Module for Audio

**Status:** Accepted

**Context:**  
Need high-quality audio playback for thunder effects. Options considered:

1. Built-in DAC (like 2024 ESP32 approach)
2. I2S audio codec
3. External MP3 player module
4. PWM audio

**Decision:**  
Use DFPlayer Mini-based MP3 player module with MicroSD card.

**Rationale:**

- **Plug-and-play solution:** No audio codec programming required
- **Hardware MP3 decoding:** Offloads CPU from audio processing
- **High quality output:** 16-bit DAC with 44.1kHz sample rate
- **Simple interface:** Serial UART communication (just send commands)
- **Easy audio management:** Swap SD card to change sounds
- **Low cost:** ~$3-5 per module
- **Proven reliability:** Widely used in Arduino/hobbyist projects
- **Multiple track support:** Can store dozens of thunder variations

**Module Specifications:**

- **Purchased from:** [Universal Solder](https://www.universal-solder.ca/product/mini-mp3-player-module-with-microsd-slot-for-arduino-etc/)
- **Based on:** DFRobot DFPlayer Mini chipset
- **Documentation:** [DFRobot DFPlayer Mini GitHub](https://github.com/DFRobot/DFRobotDFPlayerMini)
- **Communication:** 9600 baud serial UART
- **Audio Output:** 3.5mm jack or direct speaker connection
- **Supported formats:** MP3, WAV
- **Storage:** MicroSD card (up to 32GB FAT32)

**Consequences:**

- Must implement serial protocol for playback control
- Requires UART pins on Pico (limits available GPIO)
- MP3 files must follow naming convention (0001.mp3, 0002.mp3, etc.)
- Audio quality dependent on MP3 encoding settings
- SD card must be formatted FAT32 with specific structure

---

### ADR-007: Random Interval Autonomous Triggering

**Status:** Accepted

**Context:**  
2024 version required manual triggering via switch/sensor. For 2025, want more immersive "storm" atmosphere that doesn't require audience interaction or line-of-sight to sensors.

**Decision:**  
Implement random interval triggering: system automatically fires effect every 60-120 seconds.

**Rationale:**

- **More realistic:** Real storms are unpredictable
- **Better ambiance:** Continuous operation throughout evening
- **No user interaction needed:** Works even when no one is nearby
- **Simpler hardware:** No trigger sensors required (optional feature)
- **Testing-friendly:** Can still support manual trigger for development

**Implementation:**

```python
import random
import time

def autonomous_mode():
    while True:
        interval = random.randint(60, 120)  # 60-120 seconds
        time.sleep(interval)
        trigger_effect()
```

**Consequences:**

- Need reliable random number generator
- Must handle edge cases (no rapid re-triggering if interval is too short)
- Power consumption slightly higher (always-on operation)
- Testing takes longer (must wait for random triggers)
- Can add manual trigger as override for testing

---

### ADR-008: Multi-Board Independent Operation

**Status:** Accepted

**Context:**  
2025 goal is deploying 3 boards across larger display area. Options:

1. **Synchronized:** All boards trigger simultaneously (requires wireless communication)
2. **Master/Slave:** One board controls others (complex wiring)
3. **Independent:** Each board operates autonomously with random timing

**Decision:**  
Three independent boards, each with own random trigger timing.

**Rationale:**

- **Simpler implementation:** No wireless protocol, no inter-board communication
- **More natural effect:** Real storms have multiple lightning strikes at different locations
- **Fault tolerance:** One board failure doesn't affect others
- **Easier testing:** Can develop/test single board in isolation
- **Scalable:** Can add more boards without code changes
- **Cost-effective:** No additional wireless hardware required

**Hardware:**

- 3x complete board assemblies (Pico 2, MP3 module, NeoPixels, amplifier)
- Each board has own power supplies
- Each board operates on own random interval timer
- No physical connection between boards

**Consequences:**

- Boards will NOT be synchronized (this is a feature, not a bug!)
- Must manage 3 separate deployments
- Troubleshooting requires checking each board individually
- Software updates must be applied to all 3 boards

---

## Technical Challenges & Solutions

### Challenge: DFPlayer Mini Serial Communication

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
- `0x3F`: Initialize module

**Code Reference:** `mp3_player.py` (to be created)

---

### Challenge: MP3 File Naming Convention

**Problem:**  
DFPlayer Mini expects specific file naming: `0001.mp3`, `0002.mp3`, etc. Files must be copied to SD card in specific order (first file copied becomes 0001).

**Solution:**

- Create audio preparation script that:
  1. Formats SD card as FAT32
  2. Renames audio files with proper numbering
  3. Copies files in correct order
- Document the process clearly in README
- Keep source audio files separate from numbered versions

**Audio Preparation Steps:**

```bash
# 1. Format SD card as FAT32
# 2. Name files: 0001.mp3, 0002.mp3, 0003.mp3
# 3. Copy to SD card root directory in order
```

---

### Challenge: Power Distribution for Three Boards

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

---

### Challenge: Pico 2 Development Workflow

**Problem:**  
First time using Raspberry Pi Pico platform. Workflow differs from ESP32 development.

**Solution:**

- Use official VS Code Pico extension for integrated development
- Extension handles firmware flashing automatically
- Built-in REPL for interactive testing
- File upload via extension (no need for separate tools like ampy)

**Key Differences from ESP32:**
| Aspect | ESP32 (2024) | Pico 2 (2025) |
|--------|--------------|--------------|
| Firmware flash | esptool (manual) | VS Code extension (automatic) |
| File upload | ampy | VS Code extension |
| REPL | mpremote | VS Code integrated |
| Debugging | Print statements | VS Code debugger support |

---

## Development Environment Setup

### Initial Project Setup (One Time)

**Prerequisites:**

- Python 3.13 or higher
- Node.js (latest LTS version)
- Git
- VS Code

**Setup Steps:**

```bash
# 1. Clone repository
git clone https://github.com/tforster/halloween.git
cd halloween
git checkout 2025

# 2. Install Node.js dependencies (for linting/formatting)
npm install

# 3. Create Python virtual environment
python3.13 -m venv venv

# 4. Activate virtual environment
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 5. Install Python dependencies
pip install -r requirements.txt

# 6. Install development dependencies (optional)
pip install -r requirements-dev.txt

# 7. Install VS Code extensions
# - Raspberry Pi Pico (raspberry-pi.raspberry-pi-pico)
# - Markdown All In One (yzhang.markdown-all-in-one)
```

**Install ffmpeg (for audio conversion):**

```bash
# Linux
sudo apt install ffmpeg

# Mac
brew install ffmpeg

# Windows
# Download from: https://ffmpeg.org/download.html
```

---

### Daily Development Workflow

**Every time you work on the project:**

```bash
# Option 1: Quick activation helper
source activate.sh

# Option 2: Manual activation
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Your terminal prompt will change to show (venv)

# Now you can run Python scripts:
python devops/prepare_audio.py
python devops/test_mp3_serial.py /dev/ttyUSB0

# Or use npm scripts:
npm run audio:prep
npm run audio:prep:dry

# When done, deactivate:
deactivate
```

---

### Virtual Environment Quick Reference

| Task                     | Command                                            |
| ------------------------ | -------------------------------------------------- |
| Create venv              | `python3.13 -m venv venv`                          |
| Activate (Linux/Mac)     | `source venv/bin/activate` or `source activate.sh` |
| Activate (Windows)       | `venv\Scripts\activate`                            |
| Deactivate               | `deactivate`                                       |
| Install requirements     | `pip install -r requirements.txt`                  |
| Install dev requirements | `pip install -r requirements-dev.txt`              |
| Update pip               | `pip install --upgrade pip`                        |
| List installed packages  | `pip list`                                         |
| Freeze requirements      | `pip freeze > requirements.txt`                    |

**Understanding Virtual Environments:**

Virtual environments are Python's equivalent of Node.js's `node_modules/`. They provide isolated Python interpreters and packages per project.

| Concept        | Node.js                            | Python                             |
| -------------- | ---------------------------------- | ---------------------------------- |
| **Isolation**  | `node_modules/` per project        | `venv/` per project                |
| **Setup**      | Automatic with `npm install`       | Manual: `python -m venv venv`      |
| **Activation** | Automatic when running npm scripts | Manual: `source venv/bin/activate` |
| **Location**   | Always `./node_modules`            | Convention: `./venv` or `./.venv`  |

**Why use virtual environments?**

- Isolate project dependencies from system Python
- Avoid version conflicts between projects
- Easy to recreate environments from `requirements.txt`
- Standard practice in Python development

---

### NPM Scripts Reference

```bash
# Audio preparation
npm run audio:prep          # Prepare audio files for SD card
npm run audio:prep:dry      # Preview changes without modifying files

# Python code quality (requires dev dependencies)
npm run lint:py             # Lint Python code with ruff
npm run format:py           # Format Python code with black
npm run type:py             # Type check with mypy
npm run test:py             # Run pytest tests
```

---

### Project File Structure

```
/home/tforster/dev/TroyForster/Halloween/
├── src/                    # MicroPython code (runs ON Pico)
│   ├── boot.py            # Bootstrap loader
│   ├── main.py            # Main application
│   ├── lights.py          # NeoPixel animations
│   └── mp3_player.py      # MP3 player interface
│
├── devops/                 # Python scripts (run on HOST)
│   ├── prepare_audio.py    # Prepare MP3 files for SD card
│   ├── test_mp3_serial.py  # Test DFPlayer communication
│   └── __init__.py         # Package marker
│
├── audio/                  # Audio files (gitignored)
│   ├── (source files)      # Your original audio
│   └── prepared/           # SD card-ready files (created by script)
│
├── docs/                   # Documentation
│   └── Developer-Guide.md  # This file
│
├── venv/                   # Virtual environment (gitignored)
├── node_modules/           # Node dependencies (gitignored)
│
├── pyproject.toml          # Python project config
├── requirements.txt        # Python runtime dependencies
├── requirements-dev.txt    # Python dev dependencies
├── package.json            # Node.js dev tools config
├── activate.sh             # Quick venv activation helper
├── README.md               # User documentation
└── AGENTS.md               # AI agent context file
```

**Key Points:**

- `src/` contains code that runs **ON the Pico** (MicroPython)
- `devops/` contains tools that run **on your host machine** (Python 3.13)
- `venv/` is only needed for `devops/` scripts, not for Pico code
- Audio files go on the MicroSD card in the MP3 module, not on the Pico

---

### VS Code Pico Extension Setup

**Install Extension:**

1. Open VS Code
2. Install "Raspberry Pi Pico" extension by Raspberry Pi
3. Press `Ctrl+Shift+P` → "MicroPython: Configure Project"
4. Select "Raspberry Pi Pico 2"
5. Extension downloads and flashes latest MicroPython firmware

**Workflow:**

```bash
# 1. Connect Pico 2 via USB
# 2. VS Code detects it automatically
# 3. Upload files via command palette: "Upload Project to Pico"
# 4. Or use file explorer right-click: "Upload to Pico"
```

**REPL Access:**

- Bottom panel in VS Code shows Pico REPL automatically
- Can also use Thonny IDE as alternative

---

### MicroPython on Pico 2

**Firmware:**

- VS Code extension installs latest stable MicroPython for RP2350
- Manual download available: https://micropython.org/download/RPI_PICO2/

**Key Modules:**

- `machine`: Hardware control (UART, GPIO, PWM)
- `neopixel`: NeoPixel driver (built-in)
- `random`: Random number generation
- `time`: Delays and timing

**No External Libraries Required:**

- All functionality available in standard MicroPython
- MP3 player interface implemented from scratch

---

## Hardware Assembly Notes

**Per Board Assembly (3x total):**

1. **Raspberry Pi Pico 2**
   - Solder headers if not pre-installed
   - Connect USB cable for development

2. **MP3 Player Module**
   - Wire TX → Pico GPIO X (RX pin)
   - Wire RX → Pico GPIO X (TX pin)
   - Wire VCC → Pico 3.3V or 5V (check module specs)
   - Wire GND → Pico GND
   - Insert formatted MicroSD card with MP3 files
   - Connect audio output to amplifier input

3. **60W BTL Class D Amplifier**
   - [Amazon Product Link](https://www.amazon.ca/dp/B0D8HCV43H)
   - Connect MP3 module audio output to amplifier input
   - Connect 12V power supply
   - Connect speaker(s) to amplifier output
   - Ensure proper polarity

4. **Logic Level Shifter**
   - Wire input side to Pico 3.3V
   - Wire output side to 5V power rail
   - Wire ground to ground rail
   - Wire Pico GPIO → Shifter input
   - Wire Shifter output → NeoPixel data in

5. **NeoPixel Strip (300 LEDs)**
   - Wire data in to logic level shifter output
   - Wire 5V to power supply (ensure 5-6A capacity)
   - Wire ground to ground rail

6. **Optional: Trigger Switch**
   - Wire one terminal to Pico GPIO
   - Wire other terminal to GND
   - Enable pull-up resistor in code

**Power Distribution:**

- 5V supply → Pico + NeoPixels
- 12V supply → Amplifier
- Ensure all grounds are common

---

## Code Structure

```
src/
├── boot.py              # Bootstrap script (runs on Pico startup)
│                        # - Hardware initialization
│                        # - Executes main.py
│
├── main.py              # Primary application logic
│                        # - Random interval timer
│                        # - Effect orchestration
│                        # - Manual trigger handling (optional)
│
├── lights.py            # NeoPixel animation module
│                        # - Lightning flash effect
│                        # - Batched updates (40 pixels)
│                        # - Standalone testing
│
├── mp3_player.py        # MP3 player module interface
│                        # - DFPlayer Mini serial protocol
│                        # - Track playback control
│                        # - Volume management
│
└── test.py              # Development testing script

lib/
└── (none required - using built-in modules)

audio/
└── (stored on MicroSD card in MP3 module)
    ├── 0001.mp3         # Thunder sound 1
    ├── 0002.mp3         # Thunder sound 2
    └── 0003.mp3         # Thunder sound 3
```

**Key Configuration Variables (main.py):**

- `LED_COUNT = 300`: Number of NeoPixels
- `LED_PIN = X`: GPIO for NeoPixel data
- `MP3_TX_PIN = X`: GPIO for MP3 module TX
- `MP3_RX_PIN = X`: GPIO for MP3 module RX
- `TRIGGER_PIN = X`: GPIO for manual trigger (optional)
- `MIN_INTERVAL = 60`: Minimum seconds between effects
- `MAX_INTERVAL = 120`: Maximum seconds between effects

---

## Testing & Debugging

**Standalone NeoPixel Testing:**

```python
# In REPL or test.py
from lights import light_chaser
import machine, neopixel

np = neopixel.NeoPixel(machine.Pin(LED_PIN), 300)
light_chaser(np, wait_ms=2, batch_size=40)
```

**MP3 Player Testing:**

```python
# In REPL
from mp3_player import MP3Player

player = MP3Player(tx_pin=X, rx_pin=X)
player.play_track(1)  # Play 0001.mp3
player.set_volume(20)  # Volume 0-30
```

**Random Interval Testing:**

```python
# Reduce intervals for faster testing
MIN_INTERVAL = 5  # 5 seconds instead of 60
MAX_INTERVAL = 10  # 10 seconds instead of 120
```

**VS Code Debugging:**

- Set breakpoints in code
- Use integrated debugger (Pico extension supports debugging)
- Monitor variables in real-time

---

## DevOps Scripts & Tooling

**Host-Side Development Tools**

The `devops/` directory contains Python scripts that run on your **host machine** (not on the Pico) to assist with development, testing, and deployment. These scripts require a Python virtual environment with dependencies installed.

### Virtual Environment Setup

**One-Time Setup:**

```bash
# Create virtual environment
python3.13 -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

**Daily Usage:**

```bash
# Quick activation
source activate.sh

# Or manual activation
source venv/bin/activate

# Run scripts (see below)
python devops/prepare_audio.py

# Deactivate when done
deactivate
```

### Audio Preparation Script

**Purpose:** Prepares audio files for the DFPlayer Mini MP3 module.

**Script:** `devops/prepare_audio.py`

**Features:**

- Scans `audio/` directory for MP3 and WAV files
- Converts WAV files to MP3 (requires ffmpeg and pydub)
- Renames files to DFPlayer naming convention (0001.mp3, 0002.mp3, etc.)
- Creates `audio/prepared/` directory ready for SD card
- Dry-run mode to preview changes without modifying files

**Usage:**

```bash
# Activate virtual environment
source activate.sh

# Preview changes without modifying files
python devops/prepare_audio.py --dry-run

# Process files and create audio/prepared/ directory
python devops/prepare_audio.py

# Custom source and output directories
python devops/prepare_audio.py --source audio/raw --output audio/sdcard

# Or use npm scripts
npm run audio:prep:dry  # Dry run
npm run audio:prep      # Process files
```

**Requirements:**

- `pydub` Python package (for WAV conversion)
- `ffmpeg` system package (for audio processing)

**Installation:**

```bash
# Install Python package (already in requirements.txt)
pip install pydub

# Install ffmpeg
sudo apt install ffmpeg  # Linux
brew install ffmpeg      # Mac
# Windows: Download from https://ffmpeg.org/download.html
```

**Output:**

```
audio/prepared/
├── 0001.mp3  # First file alphabetically
├── 0002.mp3  # Second file
├── 0003.mp3  # Third file
└── ...
```

**Critical Notes:**

1. **File order matters:** DFPlayer Mini assigns track numbers based on the order files are copied to the SD card
2. **Copy in order:** After script completes, copy files from `audio/prepared/` to SD card root in numerical order
3. **Format SD card:** Use FAT32 format for compatibility
4. **Test playback:** Verify track 1 plays the expected sound before deploying

### MP3 Serial Communication Tester

**Purpose:** Interactive testing tool for DFPlayer Mini serial protocol.

**Script:** `devops/test_mp3_serial.py`

**Features:**

- Direct serial communication with DFPlayer Mini module
- Test commands without deploying code to Pico
- Debug audio playback issues
- Verify protocol implementation

**Usage:**

```bash
# Activate virtual environment
source activate.sh

# Connect DFPlayer to USB-serial adapter, then:
python devops/test_mp3_serial.py /dev/ttyUSB0  # Linux
python devops/test_mp3_serial.py COM3          # Windows

# Interactive commands:
> p 1        # Play track 1 (0001.mp3)
> p 2        # Play track 2 (0002.mp3)
> v 25       # Set volume to 25 (range: 0-30)
> pause      # Pause playback
> resume     # Resume playback
> stop       # Stop playback
> reset      # Reset module
> quit       # Exit tester
```

**Requirements:**

- `pyserial` Python package (already in requirements.txt)
- USB-to-serial adapter (FTDI, CP2102, etc.)
- DFPlayer Mini module with MicroSD card inserted

**Hardware Setup:**

```
USB-Serial Adapter      DFPlayer Mini
-----------------       -------------
TX (output)      →      RX (pin 2)
RX (input)       ←      TX (pin 3)
GND              ←→     GND
5V (optional)    →      VCC (if not separately powered)
```

**DFPlayer Mini Commands (for reference):**

| Command    | Byte Sequence               | Description     |
| ---------- | --------------------------- | --------------- |
| Play track | `0x7E FF 06 03 00 00 01...` | Play 0001.mp3   |
| Set volume | `0x7E FF 06 06 00 00 1E...` | Volume 30       |
| Pause      | `0x7E FF 06 0E...`          | Pause playback  |
| Resume     | `0x7E FF 06 0D...`          | Resume playback |
| Stop       | `0x7E FF 06 16...`          | Stop playback   |
| Reset      | `0x7E FF 06 0C...`          | Reset module    |

Full protocol documentation: https://github.com/DFRobot/DFRobotDFPlayerMini

### Python Code Quality Tools

**Linting:**

```bash
# Check code style with ruff
npm run lint:py
# or: ruff check devops/
```

**Formatting:**

```bash
# Format code with black
npm run format:py
# or: black devops/
```

**Type Checking:**

```bash
# Check types with mypy
npm run type:py
# or: mypy devops/
```

**Testing:**

```bash
# Run pytest tests (when tests exist)
npm run test:py
# or: pytest
```

**Configuration:**

- All tools configured in `pyproject.toml`
- `src/` and `lib/` excluded from linting (MicroPython code)
- British/Canadian English spelling in comments and strings

### Project Configuration Files

**`pyproject.toml`**

- Python project metadata (name, version, author)
- Host-side dependencies (pyserial, pydub)
- Development dependencies (pytest, black, ruff, mypy)
- Tool configuration (black, ruff, mypy, pytest)
- Excludes MicroPython code from linting

**`requirements.txt`**

- Runtime dependencies for devops scripts
- `pyserial>=3.5` - Serial communication
- `pydub>=0.25.1` - Audio processing

**`requirements-dev.txt`**

- Development dependencies
- Testing: pytest, pytest-cov
- Linting: ruff
- Formatting: black
- Type checking: mypy
- Utilities: ipython

**`package.json`**

- Node.js dev dependencies (ESLint, Prettier)
- NPM scripts for running Python tools
- Used for documentation linting/formatting

### Adding New DevOps Scripts

When creating new helper scripts:

1. **Place in `devops/` directory**
2. **Add shebang:** `#!/usr/bin/env python3`
3. **Add docstring:** Module-level documentation with usage examples
4. **Use type hints:** Python 3.13+ supports them
5. **Follow conventions:** British/Canadian English spelling
6. **Document in Developer Guide:** Add usage documentation to this guide
7. **Add npm script:** Add convenience script to `package.json`

**Template:**

```python
#!/usr/bin/env python3
"""
Brief description of what this script does.

Usage:
    python devops/my_script.py --option value
    python devops/my_script.py --help
"""

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Script description"
    )
    parser.add_argument(
        '--option',
        type=str,
        help='Option description'
    )
    args = parser.parse_args()

    # Your code here...
    print("Script executed successfully")
    return 0


if __name__ == '__main__':
    exit(main())
```

### Deployment to Pico

**VS Code Pico Extension (Recommended):**

1. Right-click file in explorer → "Upload to Pico"
2. Or: `Ctrl+Shift+P` → "Upload Project to Pico"
3. Extension handles file transfer over USB serial

**Manual Deployment (Alternative):**

```bash
# Using mpremote (if installed)
mpremote cp src/main.py :main.py
mpremote cp src/lights.py :lights.py
mpremote cp src/mp3_player.py :mp3_player.py
```

**Deployment Checklist:**

- ✅ Test code locally in REPL first
- ✅ Verify audio files on SD card
- ✅ Check pin assignments in configuration
- ✅ Upload all required files (`boot.py`, `main.py`, `lights.py`, `mp3_player.py`)
- ✅ Power cycle Pico to run from `boot.py`

---

## Known Issues & Gotchas

1. **MP3 File Order:**
   - Files must be copied to SD card in specific order
   - First file copied becomes 0001.mp3 regardless of name
   - Safest: Format card, rename files properly BEFORE copying

2. **DFPlayer Mini Initialization:**
   - Module requires ~500ms startup time after power-on
   - Always add delay before sending first command
   - Some modules need explicit initialization command

3. **Serial Communication Reliability:**
   - Use 9600 baud (faster rates unreliable with DFPlayer)
   - Add small delays between commands (50-100ms)
   - Check checksums on responses

4. **NeoPixel Timing (still applies):**
   - WS2812B protocol still timing-sensitive on Pico
   - Avoid long-running operations during updates
   - Logic level shifting still required (3.3V → 5V)

5. **Power Supply Noise:**
   - Amplifier can introduce noise on shared power rails
   - Use separate power supplies for amplifier vs. logic
   - Add decoupling capacitors near Pico and MP3 module

6. **Random Number Generator:**
   - MicroPython `random.randint()` uses pseudo-random generator
   - Seed with `random.seed()` for better randomness
   - Consider using ADC noise for true random seed

---

## Future Improvements

**Planned Enhancements:**

- Web-based configuration interface (Pico W variant)
- Wireless synchronization between boards (optional)
- Multiple lightning patterns (randomized animations)
- Adjustable intensity based on time of night
- Motion sensor integration for proximity triggering
- Weather-resistant enclosure designs
- Battery backup for power outages
- Remote control via IR or RF

**Code Quality:**

- Add comprehensive error handling
- Implement MP3 player response validation
- Unit tests for all modules
- Configuration file support (JSON on filesystem)
- Logging system for debugging deployed boards
- Watchdog timer for automatic recovery

**Hardware:**

- PCB design for cleaner assembly
- 3D-printed enclosures
- Quick-disconnect connectors
- Status LEDs for debugging
- OLED display for configuration

---

## Hardware References

**Raspberry Pi Pico 2:**

- Product page: https://www.raspberrypi.com/products/raspberry-pi-pico-2/
- Datasheet: https://datasheets.raspberrypi.com/pico/pico-2-datasheet.pdf
- MicroPython docs: https://docs.micropython.org/en/latest/rp2/

**MP3 Player Module:**

- Purchase: https://www.universal-solder.ca/product/mini-mp3-player-module-with-microsd-slot-for-arduino-etc/
- GitHub/Docs: https://github.com/DFRobot/DFRobotDFPlayerMini
- Datasheet: https://wiki.dfrobot.com/DFPlayer_Mini_SKU_DFR0299

**60W BTL Class D Amplifier:**

- Purchase: https://www.amazon.ca/dp/B0D8HCV43H
- Specifications: 60W output, 12V input, BTL configuration

**WS2812B NeoPixels:**

- Datasheet: https://cdn-shop.adafruit.com/datasheets/WS2812B.pdf
- Adafruit guide: https://learn.adafruit.com/adafruit-neopixel-uberguide

**VS Code Pico Extension:**

- Marketplace: https://marketplace.visualstudio.com/items?itemName=raspberry-pi.raspberry-pi-pico
- Documentation: https://github.com/raspberrypi/pico-vscode
