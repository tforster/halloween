# Developer Guide <!-- omit in toc -->

A living document of design decisions, challenges, and solutions encountered during the development of the Halloween Lightning & Thunder effect using ESP32 and MicroPython.

## Table of Contents <!-- omit in toc -->

- [Architecture Decision Records (ADRs)](#architecture-decision-records-adrs)
  - [ADR-001: Use ESP32 with MicroPython](#adr-001-use-esp32-with-micropython)
  - [ADR-002: Parallel Audio and Visual Effects via Threading](#adr-002-parallel-audio-and-visual-effects-via-threading)
  - [ADR-003: DAC for Audio Output](#adr-003-dac-for-audio-output)
  - [ADR-004: Batched NeoPixel Updates](#adr-004-batched-neopixel-updates)
- [Technical Challenges \& Solutions](#technical-challenges--solutions)
  - [Challenge: Memory Constraints on ESP32](#challenge-memory-constraints-on-esp32)
  - [Challenge: Audio Timing and Sample Rate](#challenge-audio-timing-and-sample-rate)
  - [Challenge: NeoPixel Level Shifting](#challenge-neopixel-level-shifting)
  - [Challenge: USB Device Passthrough in WSL](#challenge-usb-device-passthrough-in-wsl)
- [Development Environment Setup](#development-environment-setup)
  - [Python 3.13 Installation (WSL/Linux)](#python-313-installation-wsllinux)
  - [MicroPython Tools](#micropython-tools)
    - [adafruit-ampy 1.1.0](#adafruit-ampy-110)
    - [MicroPython Remote Control (mpremote)](#micropython-remote-control-mpremote)
    - [ESPtool](#esptool)
- [Hardware Assembly Notes](#hardware-assembly-notes)
- [Code Structure](#code-structure)
- [Testing \& Debugging](#testing--debugging)
- [Known Issues \& Gotchas](#known-issues--gotchas)
- [References](#references)

## Architecture Decision Records (ADRs)

### ADR-001: Use ESP32 with MicroPython

**Status:** Accepted

**Context:**  
Need a microcontroller capable of:

- Driving 300+ NeoPixel LEDs
- Playing audio through DAC
- Multi-threading for parallel effects
- Easy development/deployment workflow

**Decision:**  
Use ESP32-WROOM with MicroPython firmware.

**Rationale:**

- ESP32 has dual-core processor supporting `_thread` module
- Built-in DAC (GPIO25/26) eliminates need for external audio hardware
- MicroPython provides rapid prototyping vs. C/C++ Arduino
- Strong community support and libraries (neopixel, machine)
- Sufficient flash storage for audio files
- Cost-effective (~$5-10 per board)

**Consequences:**

- MicroPython has memory overhead vs. compiled languages
- Limited RAM requires careful buffer management
- Slower execution than native code (acceptable for this use case)
- Requires firmware flashing workflow vs. USB-serial upload

### ADR-002: Parallel Audio and Visual Effects via Threading

**Status:** Accepted

**Context:**  
Lightning and thunder must occur simultaneously for realistic effect. Sequential execution would appear unnatural.

**Decision:**  
Use MicroPython's `_thread` module to run audio and LED animations in parallel.

**Rationale:**

- ESP32's dual-core architecture supports threading
- MicroPython `_thread` module available on ESP32 port
- Allows both effects to start at same instant
- Simpler than interrupt-driven or state machine approaches

**Consequences:**

- Requires thread-safe flags (`audio_playing`, `light_playing`)
- Potential for race conditions if not careful with shared state
- Cannot use global interpreter lock (GIL) sensitive operations in threads
- 5-second cooldown prevents trigger spam and thread exhaustion

### ADR-003: DAC for Audio Output

**Status:** Accepted

**Context:**  
Need to play WAV audio files through amplifier and speakers. ESP32 has limited options:

1. PWM audio (requires filtering)
2. I2S DAC (requires external hardware)
3. Built-in DAC (GPIO25/26)

**Decision:**  
Use ESP32's built-in 8-bit DAC on GPIO26.

**Rationale:**

- No external DAC hardware required
- Direct analog output to amplifier input
- Sufficient quality for thunder sound effects
- Simple implementation via `machine.DAC`

**Consequences:**

- 8-bit resolution (256 levels) vs. 16-bit CD quality
- Maximum ~127 Hz PWM frequency limitation
- Must parse WAV headers and stream data manually
- Volume control via software multiplication (potential clipping)

### ADR-004: Batched NeoPixel Updates

**Status:** Accepted

**Context:**  
Updating 300 NeoPixels individually is slow. Each `np.write()` call blocks for ~30μs per pixel.

**Decision:**  
Update LEDs in batches (default: 40 pixels) before calling `np.write()`.

**Rationale:**

- Reduces number of blocking `write()` calls from 300 to ~8
- Creates more rapid "flash" effect suitable for lightning
- Allows tuning via `batch_size` parameter
- 2ms delay between batches creates realistic flicker

**Consequences:**

- Less granular control over individual pixel timing
- Batch size affects overall animation duration
- Must ensure batch boundaries don't create visible patterns

## Technical Challenges & Solutions

### Challenge: Memory Constraints on ESP32

**Problem:**  
ESP32 has limited RAM (~160KB usable by MicroPython). Loading entire WAV file into memory fails.

**Solution:**

- Stream audio data from flash in 128-byte buffers
- Use `file.readinto(buffer)` for efficient memory reuse
- Parse WAV header once at start (44 bytes)
- Discard audio data after playback

**Code Reference:** `main.py:play_audio()`, line ~70-140

### Challenge: Audio Timing and Sample Rate

**Problem:**  
Maintaining accurate audio sample rate while streaming from flash.

**Solution:**

- Calculate microsecond interval between samples: `1000000 / sample_rate`
- Use calculated interval for `time.sleep_us()` between samples (attempted but commented out in code)
- In practice, continuous DAC writes with minimal delay proved sufficient for effect quality
- Volume multiplier applied before DAC write: `dac.write(int(sample * volume))`

**Code Reference:** `main.py:parse_wav_header()`, `main.py:play_audio()`

### Challenge: NeoPixel Level Shifting

**Problem:**  
ESP32 GPIO outputs 3.3V logic, but WS2812B NeoPixels expect 5V data signal. Unreliable communication results in flickering or non-responsive pixels.

**Solution:**

- Use bi-directional logic level shifter (e.g., 74AHCT125, TXS0108E)
- Connect ESP32 GPIO14 → Low side of shifter
- Connect High side of shifter → NeoPixel data in
- Power shifter's high side with 5V from LED power supply

**Hardware Note:** See assembly checklist in this document.

### Challenge: USB Device Passthrough in WSL

**Problem:**  
Developing on Windows with WSL requires USB serial device access for ESP32.

**Solution:**

- Use `usbipd-win` for USB passthrough to WSL
- Device appears as `/dev/ttyUSB0` in WSL
- Alternative: Native Windows with COM port access via Thonny

**Code Reference:** See setup commands in this guide

**Reference:** https://learn.microsoft.com/en-us/windows/wsl/connect-usb

## Development Environment Setup

### Python 3.13 Installation (WSL/Linux)

Prerequisites:

```bash
sudo apt-get install build-essential autoconf libssl-dev zlib1g-dev \
  libncurses5-dev libncursesw5-dev libreadline-dev libsqlite3-dev \
  libgdbm-dev libdb5.3-dev libbz2-dev libexpat1-dev liblzma-dev tk-dev
```

Install Python 3.13:

```bash
wget https://www.python.org/ftp/python/3.13.0/Python-3.13.0.tgz
tar xf Python-3.13.0.tgz
cd Python-3.13.0
./configure --enable-optimizations
make -j $(nproc)
sudo make altinstall
python3.13 --version
```

Create virtual environment:

```bash
cd /path/to/halloween/project
python3.13 -m venv venv
source venv/bin/activate
```

Configure VS Code:

1. Open Command Palette (`Ctrl+Shift+P`)
2. Select **Python: Select Interpreter**
3. Choose `venv/bin/python3.13`

### MicroPython Tools

#### adafruit-ampy 1.1.0

File transfer utility for MicroPython devices.

See: https://pypi.org/project/adafruit-ampy/

```bash
pip install adafruit-ampy

# List files on device
ampy --port /dev/ttyUSB0 ls

# Upload file
ampy --port /dev/ttyUSB0 put src/main.py

# Download file
ampy --port /dev/ttyUSB0 get main.py

# Remove file
ampy --port /dev/ttyUSB0 rm main.py
```

#### MicroPython Remote Control (mpremote)

Interactive REPL and file management.

See: https://docs.micropython.org/en/latest/reference/mpremote.html

```bash
pip install mpremote

# Connect to REPL
mpremote connect /dev/ttyUSB0

# Run script without uploading
mpremote connect /dev/ttyUSB0 run src/test.py

# Soft reset device
mpremote connect /dev/ttyUSB0 reset
```

#### ESPtool

Firmware flashing utility.

```bash
pip3.13 install esptool
pip install setuptools

# Verify installation
python -m esptool

# Erase flash (full reset)
esptool.py --port /dev/ttyUSB0 erase_flash

# Flash MicroPython firmware
# Download latest from: https://micropython.org/download/ESP32_GENERIC/
python -m esptool --chip esp32 --port /dev/ttyUSB0 --baud 460800 \
  write_flash -z 0x1000 ESP32_GENERIC-20240602-v1.23.0.bin
```

## Hardware Assembly Notes

**Original Assembly Checklist (2024):**

1. **Prepare second amplifier**

   - Solder ground and left channel leads

2. **Prepare Power Supply #1**

   - Identify 5V and 12V leads
   - Connect 5V lead to breadboard power rail
   - Connect ground lead to breadboard ground rail and amplifier negative
   - Connect 12V lead to amplifier positive

3. **ESP32 Connections**

   - Breakout ESP32 ground to breadboard ground rail
   - Wire GPIO14 to logic level shifter input
   - Wire GPIO26 to amplifier input
   - Wire GPIO5 to trigger switch

4. **Logic Level Shifter**

   - Wire input side to ESP32 3.3V power
   - Wire output side to 5V power rail
   - Wire ground to ground rail
   - Wire output data line to NeoPixel data in

5. **NeoPixel Strip**
   - Wire data in to logic level shifter output
   - Wire 5V to power rail (ensure adequate amperage)
   - Wire ground to ground rail

**Power Budget Notes:**

- Each NeoPixel draws ~60mA at full white
- 300 pixels × 60mA = 18A theoretical maximum
- In practice, lightning effect uses <30% capacity (~5-6A)
- Use appropriately rated 5V power supply

## Code Structure

```shell
src/
├── boot.py          # Bootstrap script (runs on ESP32 startup)
│                    # - Checks for main.py existence
│                    # - Executes main.py if found
│
├── main.py          # Primary application logic
│                    # - Configuration constants (pins, LED count)
│                    # - WAV file parsing
│                    # - Audio playback via DAC
│                    # - Thread management
│                    # - Trigger detection loop
│
├── lights.py        # LED animation module (standalone testing)
│                    # - NeoPixel initialization
│                    # - Light chaser effect
│                    # - LED cleanup functions
│
└── test.py          # Development testing script

lib/
└── neopixel.py      # MicroPython NeoPixel driver

audio/
└── Storm_exclamation.wav  # Thunder sound effect (16-bit WAV)
```

**Key Configuration Variables (main.py):**

- `LED_COUNT = 300`: Number of NeoPixels
- `LED_PIN = 14`: GPIO for NeoPixel data
- `SWITCH_PIN = 5`: GPIO for trigger input
- `DAC_PIN = 26`: GPIO for audio output
- `volume = 5.0`: Audio volume multiplier (in play_audio call)

## Testing & Debugging

**Standalone LED Testing:**

```bash
# Upload and run lights.py independently
mpremote connect /dev/ttyUSB0 run src/lights.py
```

**Audio Testing:**

```python
# In REPL or test.py
import machine
dac = machine.DAC(machine.Pin(26))
dac.write(128)  # Mid-level output (test tone)
```

**Serial Monitor:**

```bash
# View print statements and errors
mpremote connect /dev/ttyUSB0
# OR
screen /dev/ttyUSB0 115200
```

**Common Debug Print Locations:**

- WAV header parsing (main.py, commented out)
- Buffer hex dumps (main.py:hex_dump(), commented out)
- Touch/switch state (lights.py, active)

## Known Issues & Gotchas

1. **Threading Limitations:**

   - MicroPython threads don't support daemon mode
   - Ensure threads complete before new trigger
   - Cooldown period prevents thread exhaustion

2. **DAC Write Clipping:**

   - Volume multiplier can exceed DAC's 0-255 range
   - No clipping protection implemented
   - Consider: `dac.write(min(255, int(sample * volume)))`

3. **NeoPixel Timing Sensitivity:**

   - WS2812B protocol requires precise timing
   - Avoid long-running operations in main loop
   - Threading helps isolate blocking operations

4. **File System Limitations:**

   - Limited flash write cycles
   - Avoid frequent file writes during operation
   - Audio files stored in flash, read-only during runtime

5. **USB Serial Device Names:**
   - `/dev/ttyUSB0` may change if multiple devices connected
   - Use `ls /dev/tty*` to identify correct port
   - May appear as `/dev/ttyACM0` on some systems

## References

- **WSL USB Passthrough:** https://learn.microsoft.com/en-us/windows/wsl/connect-usb
- **MicroPython Documentation:** https://docs.micropython.org/
- **ESP32 Pinout:** See `docs/Freenove_ESP32_WROOM_Board_Pinout.pdf`
- **WS2812B Datasheet:** https://cdn-shop.adafruit.com/datasheets/WS2812B.pdf
- **adafruit-ampy:** https://pypi.org/project/adafruit-ampy/
- **mpremote:** https://docs.micropython.org/en/latest/reference/mpremote.html
- **ESPtool:** https://github.com/espressif/esptool
