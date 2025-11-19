# Developer Guide <!-- omit in toc -->

> [!NOTE]
> This guide documents the **2025 Raspberry Pi Pico 2 implementation**.  
> For the 2024 ESP32 version, see the [`2024` tag](https://github.com/tforster/halloween/tree/2024).

A living document of design decisions, challenges, and solutions for the Halloween Lightning & Thunder effect system.

## Table of Contents <!-- omit in toc -->

- [1. Architecture Decision Records (ADRs)](#1-architecture-decision-records-adrs)
  - [1.1. ADR-005: Migration from ESP32 to Raspberry Pi Pico 2 (2025)](#11-adr-005-migration-from-esp32-to-raspberry-pi-pico-2-2025)
  - [1.2. ADR-006: External MP3 Player Module for Audio](#12-adr-006-external-mp3-player-module-for-audio)
  - [1.3. ADR-007: Random Interval Autonomous Triggering](#13-adr-007-random-interval-autonomous-triggering)
  - [1.4. ADR-008: Multi-Board Independent Operation](#14-adr-008-multi-board-independent-operation)
- [2. Technical Challenges \& Solutions](#2-technical-challenges--solutions)
  - [2.1. Challenge: DFPlayer Mini Serial Communication](#21-challenge-dfplayer-mini-serial-communication)
  - [2.2. Challenge: MP3 File Naming Convention](#22-challenge-mp3-file-naming-convention)
  - [2.3. Challenge: Power Distribution for Three Boards](#23-challenge-power-distribution-for-three-boards)
  - [2.4. Challenge: Pico 2 Development Workflow](#24-challenge-pico-2-development-workflow)
- [3. Development Environment Setup](#3-development-environment-setup)
  - [3.1. Initial Project Setup (One Time)](#31-initial-project-setup-one-time)
  - [3.2. Daily Development Workflow](#32-daily-development-workflow)
  - [3.3. NPM Scripts Reference](#33-npm-scripts-reference)
  - [3.4. Project File Structure](#34-project-file-structure)
  - [3.5. MicroPython on Pico 2](#35-micropython-on-pico-2)
- [4. Hardware Assembly Notes](#4-hardware-assembly-notes)
  - [Pin Assignments (Final Configuration)](#pin-assignments-final-configuration)
  - [Wiring Diagrams](#wiring-diagrams)
    - [Complete System Wiring (Dual 5V Supply Configuration)](#complete-system-wiring-dual-5v-supply-configuration)
    - [Level Shifter Detail](#level-shifter-detail)
    - [DFPlayer Mini Wiring Detail](#dfplayer-mini-wiring-detail)
  - [Power Supply Specifications](#power-supply-specifications)
    - [Component Power Requirements](#component-power-requirements)
    - [Recommended Power Supplies (Per Board)](#recommended-power-supplies-per-board)
    - [Dual Supply Wiring Diagram](#dual-supply-wiring-diagram)
    - [Safety Considerations](#safety-considerations)
    - [Multi-Board Deployment (3 Boards Total)](#multi-board-deployment-3-boards-total)
- [5. Code Structure](#5-code-structure)
- [6. Testing \& Debugging](#6-testing--debugging)
- [7. DevOps Scripts \& Tooling](#7-devops-scripts--tooling)
  - [7.1. MP3 Serial Communication Tester](#71-mp3-serial-communication-tester)
  - [7.2. Python Code Quality Tools](#72-python-code-quality-tools)
  - [7.3. Adding New DevOps Scripts](#73-adding-new-devops-scripts)
- [8. TODO List](#8-todo-list)
- [9. Known Issues \& Gotchas](#9-known-issues--gotchas)

## 1. Architecture Decision Records (ADRs)

### 1.1. ADR-005: Migration from ESP32 to Raspberry Pi Pico 2 (2025)

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

### 1.2. ADR-006: External MP3 Player Module for Audio

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

### 1.3. ADR-007: Random Interval Autonomous Triggering

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

### 1.4. ADR-008: Multi-Board Independent Operation

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

## 2. Technical Challenges & Solutions

### 2.1. Challenge: DFPlayer Mini Serial Communication

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

### 2.2. Challenge: MP3 File Naming Convention

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

### 2.3. Challenge: Power Distribution for Three Boards

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

### 2.4. Challenge: Pico 2 Development Workflow

**Problem:**  
First time using Raspberry Pi Pico platform. Workflow differs from ESP32 development.

**Solution:**

- Use mpremote wrapped in a shell script and aliased in package.json as `npm run {cmd}`

## 3. Development Environment Setup

### 3.1. Initial Project Setup (One Time)

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

# Note that venv is not used since the local src folder will be synchronised to the Pico 2 directly.

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

### 3.2. Daily Development Workflow

> [!note]
> Common development procedures (flashing firmware, uploading files, preparing audio) are documented in AGENTS.md.
> See [Common Development Tasks](../AGENTS.md#common-development-tasks) for step-by-step instructions.

**Every time you work on the project:**

```bash
# Connect the Pico 2 to the USB port
# Use deployment scripts from devops/ folder
# See Common Development Tasks in AGENTS.md
```

### 3.3. NPM Scripts Reference

```bash
# TODO: Add the new mpremote shell scripts from devops folder
# Audio preparation
npm run audio:prep          # Prepare audio files for SD card
npm run audio:prep:dry      # Preview changes without modifying files

# Python code quality (requires dev dependencies)
npm run lint:py             # Lint Python code with ruff
npm run format:py           # Format Python code with black
npm run type:py             # Type check with mypy
npm run test:py             # Run pytest tests
```

### 3.4. Project File Structure

```text
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
- Audio files go on the MicroSD card in the MP3 module, not on the Pico

### 3.5. MicroPython on Pico 2

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

## 4. Hardware Assembly Notes

**Per Board Assembly (3x total):**

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

**Power Distribution:**

- 5V 8A supply → Pico + MP3 Module + NeoPixels
- 12V 5A supply → Amplifier (isolated)
- Ensure all grounds are common

> [!note]
> Hardware component specifications, purchase links, and datasheets are maintained in AGENTS.md.
> See [Hardware Configuration](../AGENTS.md#hardware-configuration) for complete details.

### Pin Assignments (Final Configuration)

| GPIO Pin | Function       | Direction | Hardware Connection                | Rationale                                                    |
| -------- | -------------- | --------- | ---------------------------------- | ------------------------------------------------------------ |
| **GP16** | NeoPixel Data  | Output    | Level Shifter Input → NeoPixel DIN | Available GPIO, not needed for UART, suitable for PIO timing |
| **GP4**  | MP3 TX         | Output    | Pico TX → DFPlayer Mini RX (Pin 2) | UART1 TX - dedicated hardware UART                           |
| **GP5**  | MP3 RX         | Input     | Pico RX ← DFPlayer Mini TX (Pin 3) | UART1 RX - paired with GP4                                   |
| **GP15** | Manual Trigger | Input     | Button to 3.3V (optional)          | Available GPIO with pull-down support                        |
| **GP25** | Status LED     | Output    | Onboard LED                        | Built-in LED for status indication                           |

**Pin Selection Rationale:**

- **UART1 (GP4/GP5)**: Chosen over UART0 to avoid conflicts with USB serial debugging
- **GPIO 16**: Not required for either UART, suitable for NeoPixel PIO operations
- **GPIO 15**: Readily available for future expansion features
- **All pins verified** against [Pico 2 Datasheet](https://datasheets.raspberrypi.com/pico/pico-2-datasheet.pdf)

### Wiring Diagrams

#### Complete System Wiring (Dual 5V Supply Configuration)

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

#### Level Shifter Detail

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

#### DFPlayer Mini Wiring Detail

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

### Power Supply Specifications

#### Component Power Requirements

| Component               | Voltage   | Typical Current    | Maximum Current | Notes                                      |
| ----------------------- | --------- | ------------------ | --------------- | ------------------------------------------ |
| **Pico 2**              | 5V (VBUS) | 50-100mA           | 150mA           | Powered via USB or VBUS pin                |
| **DFPlayer Mini**       | 5V        | 20-30mA idle       | 200mA peak      | Use 5V for best performance                |
| **NeoPixels (150)**     | 5V        | 2.5-3A (lightning) | 9A (full white) | Lightning uses ~30% duty cycle per segment |
| **Logic Level Shifter** | 5V + 3.3V | <10mA              | 50mA            | Bidirectional, minimal power               |
| **60W Amplifier**       | 12V       | Variable           | 5A (60W/12V)    | Separate power required                    |

#### Recommended Power Supplies (Per Board)

**⚠️ CRITICAL: Use Dual 5V Supplies for Reliable NeoPixel Operation**

**Why Two Supplies?**

A single 5V 8A supply powering 300 NeoPixels over 5 meters causes:

- **Voltage drop:** 5.0V at start → 4.2-4.5V at end (below WS2812B spec)
- **Color shift:** Especially in white/blue
- **Capacity issues:** 6A load on 8A supply = 75% (too close to limit)
- **Thermal stress:** Supply runs hot, reduced reliability

**Solution: Split into Two Segments**

Each 150-pixel segment gets its own supply → eliminates voltage drop, distributes load.

---

**Power Supply 1: 5V 8A for Logic + Pixels 1-150**

- **Powers:** Raspberry Pi Pico 2, DFPlayer Mini, NeoPixels 1-150, Logic Level Shifter
- **Rating:** 5V 8A (40W)
- **Typical Load:** ~3.2A during lightning effect
- **Load Percentage:** 40% (comfortable headroom)
- **Location:** Start of NeoPixel strip (pixel 1)
- **Recommended:** Mean Well RS-50-5 (5V 10A, 50W) or equivalent
- **Wire Gauge:**
  - 5V to NeoPixels 1-150: 18 AWG
  - 5V to Pico/MP3: 22 AWG sufficient
  - Ground returns: 18 AWG

**Power Supply 2: 5V 8A for Pixels 151-300**

- **Powers:** NeoPixels 151-300 only
- **Rating:** 5V 8A (40W)
- **Typical Load:** ~3A during lightning effect
- **Load Percentage:** 37% (comfortable headroom)
- **Location:** Midpoint of NeoPixel strip (~2.5m, pixel 150)
- **Recommended:** Mean Well RS-50-5 (5V 10A, 50W) or equivalent
- **Wire Gauge:**
  - 5V to NeoPixels 151-300: 18 AWG
  - Ground return: 18 AWG
  - **IMPORTANT:** Do NOT connect data signal here (data flows through from pixel 1)

**Power Supply 3: 12V 5A for Amplifier**

- **Powers:** 60W Class D Amplifier only
- **Rating:** 12V 5A (60W)
- **Typical Load:** Variable by volume
- **Peak Load:** 5A at full power
- **Why Isolated:** Audio amplifiers generate switching noise
- **Recommended:** 12V 5A wall adapter or Mean Well equivalent
- **Ground:** Connect to common ground with 5V supplies
- **Wire Gauge:** 18 AWG adequate

#### Dual Supply Wiring Diagram

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
   - Minimize distance from supply to injection point
   - Use stranded wire for flexibility

#### Safety Considerations

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

#### Multi-Board Deployment (3 Boards Total)

**Total Power Requirements:**

- 6× 5V 8A supplies (2 per board) = 48A at 5V (240W total)
- 3× 12V 5A supplies (1 per board) = 15A at 12V (180W total)
- **Combined: ~420W** for complete installation

**Recommended Deployment:**

- Each board has:
  - 2× dedicated 5V 8A supplies (one per 150-pixel segment)
  - 1× dedicated 12V 5A supply (amplifier)
- Simplest deployment and troubleshooting
- Each board is independent
- **Total: 9 power supplies** (6× 5V + 3× 12V)

**Per-Board Power Budget:**

| Board   | Supply 1 (5V 8A)          | Supply 2 (5V 8A) | Supply 3 (12V 5A) | Total Power |
| ------- | ------------------------- | ---------------- | ----------------- | ----------- |
| Board 1 | Pico + MP3 + Pixels 1-150 | Pixels 151-300   | Amplifier         | ~140W       |
| Board 2 | Pico + MP3 + Pixels 1-150 | Pixels 151-300   | Amplifier         | ~140W       |
| Board 3 | Pico + MP3 + Pixels 1-150 | Pixels 151-300   | Amplifier         | ~140W       |

**Alternative: Canaduino Breadboard Power Module**

If using CANADUINO Breadboard Power Supply Module:

- **Use for:** Pico 2 and DFPlayer Mini only
- **Configuration:**
  - One rail: 3.3V or 5V for Pico
  - Other rail: 3.3V or 5V for MP3 module
  - 12V rail: Not used (insufficient current for amplifier)
- **Benefits:** Clean regulated power for logic circuits, USB-C input
- **NeoPixel Power:** Still requires two dedicated 5V 8A supplies per board
- **Total per board:** Canaduino (USB-C 2.1A) + 2× 5V 8A + 1× 12V 5A

**Logic Level Shifter Consideration:**

If using Canaduino with 3.3V rails:

- **Option 1 (Recommended):** Omit logic level shifter, run NeoPixels with 3.3V data signal
  - WS2812B will work reliably with 3.3V logic when powered at 5V
  - Simplifies wiring, one less component
  - Pico GP16 connects directly to NeoPixel DIN
- **Option 2 (Original Design):** Keep logic level shifter
  - Use Canaduino 5V rail as HV (high voltage) reference
  - Use Canaduino 3.3V rail for Pico LV (low voltage)
  - Maintains 5V data signal for maximum noise immunity

**Pin Assignments (Replaced - See Table Above):**

-

## 5. Code Structure

```text
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

> [!note]
> Code style conventions and naming guidelines are maintained in AGENTS.md.
> See [Code Style & Conventions](../AGENTS.md#code-style--conventions) for complete details.

**Key Configuration Variables (main.py):**

- `LED_COUNT = 300`: Number of NeoPixels
- `LED_PIN = X`: GPIO for NeoPixel data
- `MP3_TX_PIN = X`: GPIO for MP3 module TX
- `MP3_RX_PIN = X`: GPIO for MP3 module RX
- `TRIGGER_PIN = X`: GPIO for manual trigger (optional)
- `MIN_INTERVAL = 60`: Minimum seconds between effects
- `MAX_INTERVAL = 120`: Maximum seconds between effects

## 6. Testing & Debugging

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

## 7. DevOps Scripts & Tooling

**Host-Side Development Tools**

The `devops/` directory contains Python scripts that run on your **host machine** (not on the Pico) to assist with development, testing, and deployment. These scripts require a Python virtual environment with dependencies installed.

**Critical Notes:**

1. **File order matters:** DFPlayer Mini assigns track numbers based on the order files are copied to the SD card
2. **Copy in order:** After script completes, copy files from `audio/prepared/` to SD card root in numerical order
3. **Format SD card:** Use FAT32 format for compatibility
4. **Test playback:** Verify track 1 plays the expected sound before deploying

### 7.1. MP3 Serial Communication Tester

**Purpose:** Interactive testing tool for DFPlayer Mini serial protocol.

**Script:** `devops/test_mp3_serial.py`

**Features:**

- Direct serial communication with DFPlayer Mini module
- Test commands without deploying code to Pico
- Debug audio playback issues
- Verify protocol implementation

**Hardware Setup:**

```text
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

### 7.2. Python Code Quality Tools

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

**`package.json`**

- Node.js dev dependencies (ESLint, Prettier)
- NPM scripts for running Python tools
- Used for documentation linting/formatting

### 7.3. Adding New DevOps Scripts

When creating new helper scripts:

1. **Place in `devops/` directory**
2. **Add shebang:** `#!/usr/bin/env python3`
3. **Add docstring:** Module-level documentation with usage examples
4. **Use type hints:** Python 3.13+ supports them
5. **Follow conventions:** British/Canadian English spelling
6. **Document in Developer Guide:** Add usage documentation to this guide
7. **Add npm script:** Add convenience script to `package.json`

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

## 8. TODO List

This is a high level todo list for now.

- [ ] SD Cards
  - [ ] Format as FAT32 x3
  - [ ] Copy prepared audio files x3
- [ ] Amplifier
  - [ ] Solder connection blocks
  - [ ] Connect female barrel jacks
  - [ ] Connect to MP3 module audio out
  - [ ] Connect to speaker input
- [ ] defg
- [ ] hijk

4. [ ]

## 9. Known Issues & Gotchas

> [!note]
> Hardware and protocol-level constraints are documented in AGENTS.md.
> See [Known Limitations & Gotchas](../AGENTS.md#known-limitations--gotchas) for hardware-specific constraints.

**This section tracks implementation-specific issues discovered during development:**

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

> [!note]
> Hardware component specifications, purchase links, datasheets, and resource documentation are maintained in AGENTS.md.
> See [Hardware Resource Links](../AGENTS.md#hardware-resource-links) for complete details.
