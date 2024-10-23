# AGENTS.md

This file provides context and instructions for AI coding agents working on the Halloween Lightning & Thunder Effect project.

## Project Overview

This is an ESP32 MicroPython project that creates synchronized lightning and thunder effects for Halloween displays. The system:

- Runs on an ESP32-WROOM microcontroller with MicroPython firmware
- Controls 300+ WS2812B NeoPixel LEDs for lightning animation
- Plays WAV audio through the built-in DAC to amplified speakers for thunder
- Uses multi-threading to run both effects simultaneously
- Triggers via GPIO switch/touch sensor

**Key Technologies:**

- MicroPython 1.23.0+ on ESP32
- NeoPixel (WS2812B) LED control
- Digital-to-Analog Converter (DAC) audio
- Threading (`_thread` module)
- Flash storage for audio files

## Development Environment

### Host System Setup

**Primary Development:**

- OS: Linux (WSL2 on Windows)
- Shell: zsh
- Python: 3.13+ (for development tools, not deployed code)
- Node.js: Latest LTS (npm for scripts)
- VS Code with Python extension

**USB Access (WSL):**

- Requires `usbipd-win` for USB device passthrough
- ESP32 appears as `/dev/ttyUSB0` or `/dev/ttyACM0`

### MicroPython Tools Installation

```bash
# Install Python development tools
pip3.13 install esptool adafruit-ampy mpremote setuptools

# Verify installations
python -m esptool
ampy --help
mpremote --help
```

### Project Setup

```bash
# Clone repository
git clone https://github.com/tforster/halloween.git
cd halloween

# Install Node dependencies (if any)
npm install

# No Python virtual environment needed - code runs on ESP32, not host
```

## File Structure Context

```
/home/tforster/dev/TroyForster/Halloween/
├── src/                    # MicroPython source code (deployed to ESP32)
│   ├── boot.py            # Bootstrap loader (runs on ESP32 startup)
│   ├── main.py            # Main application (210 lines)
│   ├── lights.py          # LED animation module
│   └── test.py            # Development testing
├── lib/                    # MicroPython libraries
│   └── neopixel.py        # NeoPixel driver
├── audio/                  # WAV audio files for thunder sounds
│   └── Storm_exclamation.wav  # Primary thunder effect (deployed to ESP32)
├── docs/                   # Documentation
│   ├── Developer-Guide.md  # Comprehensive technical documentation
│   └── *.pdf              # Hardware reference (ESP32 pinout)
├── devops/                 # (empty - future deployment scripts)
└── README.md              # User-facing documentation
```

**Important:** Files in `src/` and `lib/` are MicroPython code that runs ON the ESP32, not on the host. They must be uploaded to the device using `ampy` or `mpremote`.

## Hardware Configuration

**ESP32 Pin Assignments (main.py constants):**

- GPIO 14: NeoPixel data output (via 3.3V→5V logic level shifter)
- GPIO 26: DAC audio output to amplifier
- GPIO 5: Trigger input (switch/touch sensor)

**Hardware Requirements:**

- ESP32-WROOM development board
- 300 WS2812B NeoPixels (configurable via `LED_COUNT`)
- Logic level shifter (3.3V→5V)
- Audio amplifier + speakers
- 5V power supply (5-6A minimum for LEDs)
- 12V power supply for amplifier

## Code Style & Conventions

**MicroPython Code (src/, lib/):**

- Snake_case for functions and variables
- UPPER_CASE for constants (e.g., `LED_COUNT`, `LED_PIN`)
- Minimal dependencies (memory constrained)
- Comments for non-obvious behavior
- No type hints (not supported in MicroPython)
- Keep memory usage low - use buffers, streaming, avoid large data structures

**Python Development Tools:**

- PEP 8 style guide
- Type hints preferred for new host-side code
- Use virtual environments for host tools

**Documentation:**

- Markdown for all docs
- Keep README.md user-focused and concise
- Technical details belong in docs/Developer-Guide.md
- Use ADR format for architectural decisions

## Common Development Tasks

### Flashing MicroPython Firmware

```bash
# Erase existing flash
esptool.py --port /dev/ttyUSB0 erase_flash

# Flash firmware (download from micropython.org first)
python -m esptool --chip esp32 --port /dev/ttyUSB0 --baud 460800 \
  write_flash -z 0x1000 ESP32_GENERIC-20240602-v1.23.0.bin
```

### Uploading Files to ESP32

```bash
# Upload Python files
ampy --port /dev/ttyUSB0 put src/boot.py
ampy --port /dev/ttyUSB0 put src/main.py
ampy --port /dev/ttyUSB0 put lib/neopixel.py

# Upload audio (create directory first if needed)
ampy --port /dev/ttyUSB0 mkdir audio
ampy --port /dev/ttyUSB0 put audio/Storm_exclamation.wav audio/Storm_exclamation.wav

# List files on device
ampy --port /dev/ttyUSB0 ls
```

### Testing & Debugging

```bash
# Connect to REPL for interactive testing
mpremote connect /dev/ttyUSB0

# Run code without permanently uploading
mpremote connect /dev/ttyUSB0 run src/test.py

# Monitor serial output (alternative to mpremote)
screen /dev/ttyUSB0 115200  # Ctrl+A, K to exit
```

### Standalone Module Testing

```bash
# Test LED animation independently
mpremote connect /dev/ttyUSB0 run src/lights.py
```

## Testing Instructions

**No automated tests currently exist.** Testing is manual:

1. **LED Test:** Run `src/lights.py` standalone - should see light chaser pattern
2. **Audio Test:** In REPL, manually initialize DAC and write test values
3. **Full System Test:** Upload all files, trigger via GPIO5, verify simultaneous lightning + thunder
4. **Cooldown Test:** Verify 5-second delay between triggers prevents rapid re-triggering

**Future Testing Needs:**

- Unit tests for WAV header parsing (`parse_wav_header()`)
- Mock tests for GPIO/hardware interactions
- Integration tests with virtual hardware
- Regression tests before each season

## Known Limitations & Gotchas

1. **Memory Constraints:** ESP32 has ~160KB usable RAM in MicroPython. Avoid loading entire files into memory. Use streaming/buffering.

2. **Threading:** MicroPython threading is cooperative, not preemptive. Threads must yield control. No daemon threads - ensure threads complete.

3. **DAC Clipping:** Volume multiplier in `play_audio()` can cause values >255. No clipping protection exists (potential improvement).

4. **USB Device Names:** `/dev/ttyUSB0` may change if multiple devices connected. Check with `ls /dev/tty*`.

5. **NeoPixel Timing:** WS2812B protocol is timing-sensitive. Avoid blocking operations during LED updates.

6. **Flash Writes:** Limited write cycles on ESP32 flash. Audio files are read-only during runtime.

## Important Code Patterns

### Audio Streaming Pattern

Audio files are streamed in 128-byte buffers to avoid memory exhaustion:

```python
buffer_size = 128
buffer = bytearray(buffer_size)
byte_offset = wav_file.readinto(buffer)  # Reuse buffer
```

### Batched LED Updates

LEDs updated in batches (default 40 pixels) for performance:

```python
for i in range(0, len(np), batch_size):
    for j in range(batch_size):
        if i + j < len(np):
            np[i + j] = (240, 248, 255)
    np.write()  # Single write for entire batch
```

### Thread Safety

Use flags to prevent concurrent triggers:

```python
audio_playing = False
light_playing = False

# Check before starting new thread
if not audio_playing and not light_playing:
    _thread.start_new_thread(play_effects, ())
```

## Configuration Changes

To modify behavior, edit constants in `src/main.py`:

```python
LED_COUNT = 300      # Number of NeoPixels
LED_PIN = 14         # GPIO for LED data
SWITCH_PIN = 5       # GPIO for trigger
DAC_PIN = 26         # GPIO for audio output
```

To change animation speed, modify `lights.py`:

```python
light_chaser(np, wait_ms=2, batch_size=40)  # 2ms delay, 40-pixel batches
```

## Future Development Notes

**2025 Season Plans:**

- Multiple trigger zones with different effects
- WiFi/ESP-NOW wireless triggering
- Multiple audio tracks with randomization
- Web-based configuration interface
- Weather-resistant enclosure

**Code Quality Improvements Needed:**

- Add error handling (try/except blocks minimal/absent)
- Implement DAC clipping protection
- Refactor threading into reusable class
- Add JSON configuration file support
- Document all functions with docstrings
- Add type hints to host-side scripts

## Git Workflow

**Current State:**

- Branch: `wip` (work in progress)
- No `main` branch yet (will be created from squashed `wip`)

**Planned Workflow:**

1. Clean up `wip` branch (this documentation effort)
2. Squash commits on `wip`
3. Rename `wip` → `main`
4. Tag `main` as `2024`
5. Create `2025` branch for new season work
6. Each year gets a new branch, previous year tagged with year number

**Commit Messages:**

- Follow conventional commits format when possible
- Reference issues/features in commit messages
- Keep commits atomic and focused

## Security & Safety

**Electrical Safety:**

- Verify power supply ratings before connecting LEDs (5-6A minimum)
- Use appropriate wire gauge for high-current LED power
- Isolate 5V (logic/LEDs) from 12V (amplifier) circuits
- Never exceed ESP32 GPIO current limits (12mA per pin, 40mA total)

**Code Safety:**

- No network connectivity in current implementation (air-gapped)
- No sensitive data stored on device
- Audio files are static, no user uploads
- GPIO inputs use pull-down resistors to prevent floating

## Additional Resources

- **Full Technical Documentation:** `docs/Developer-Guide.md`
- **User Guide:** `README.md`
- **ESP32 Pinout:** `docs/Freenove_ESP32_WROOM_Board_Pinout.pdf`
- **MicroPython Docs:** https://docs.micropython.org/
- **WS2812B Datasheet:** https://cdn-shop.adafruit.com/datasheets/WS2812B.pdf

## Questions to Ask Before Making Changes

1. **Will this change increase memory usage?** (ESP32 RAM is very limited)
2. **Does this affect timing-critical code?** (NeoPixel updates, audio streaming)
3. **Is this change needed on the device or host?** (Don't add host dependencies to device code)
4. **Will this work with MicroPython?** (Not all Python libraries are available)
5. **Does this need to persist across reboots?** (Consider flash storage implications)
6. **Will this affect thread safety?** (Check for shared state access)

## When in Doubt

1. Read the `docs/Developer-Guide.md` for architectural context
2. Check MicroPython documentation for ESP32 specifics
3. Test changes on actual hardware (simulators don't capture timing issues)
4. Keep changes small and testable
5. Document non-obvious decisions in code comments or Developer Guide
