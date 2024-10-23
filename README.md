# Halloween Lightning & Thunder Effect <!-- omit in toc -->

An ESP32-based Halloween display controller that creates synchronized lightning and thunder effects using NeoPixel LED strips and amplified audio. This project was built to enhance a neighbor's annual Halloween front-yard display with a dramatic weather effect on a 12-foot display board.

## Table of Contents <!-- omit in toc -->

- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Hardware Requirements](#hardware-requirements)
  - [Installation](#installation)
- [Usage](#usage)
- [High Level Architecture Overview](#high-level-architecture-overview)
- [Policies](#policies)
- [Authors](#authors)
- [License](#license)

## Getting Started

This project uses an ESP32 microcontroller running MicroPython to orchestrate a Halloween lightning and thunder effect. When triggered (via a switch or touch sensor), the system simultaneously:

1. **Plays a lightning animation** across 300+ NeoPixel LEDs in a rapid "chaser" pattern
2. **Plays thunder sound effects** through a DAC (Digital-to-Analog Converter) connected to an amplifier and speakers

The effect runs in parallel using threading, creating a convincing lightning strike with accompanying thunder. When mounted on a tall black board, it's surprisingly effective at creating an ominous atmosphere.

### Prerequisites

**Development Environment:**

- VS Code with Python extension
- [Thonny IDE](https://thonny.org/) (useful for MicroPython development)
- Python 3.13+ (for development tools)
- Node.js/npm (latest LTS version)
- Git client

**Python Tools & Packages:**

```bash
# Install ESPtool for flashing firmware
pip3.13 install esptool

# Install ampy for file transfer
pip install adafruit-ampy

# Install mpremote for MicroPython REPL
pip install mpremote
```

**MicroPython Firmware:**

- Download the latest ESP32 firmware from [micropython.org](https://micropython.org/download/ESP32_GENERIC/)

### Hardware Requirements

- **ESP32 development board** (ESP32-WROOM recommended, see `docs/Freenove_ESP32_WROOM_Board_Pinout.pdf`)
- **300+ WS2812B/NeoPixel LED strip** (or adjust `LED_COUNT` in code)
- **Logic level shifter** (3.3V to 5V for NeoPixel data line)
- **Audio amplifier** with speaker(s)
- **Power supplies:**
  - 5V supply for ESP32 and NeoPixels (ensure adequate amperage for LED count)
  - 12V supply for amplifier
- **Trigger mechanism** (switch, touch sensor, or PIR motion sensor)
- **Breadboard and jumper wires** for prototyping

**Pin Connections (configurable in `main.py`):**

- GPIO 14: NeoPixel data (via logic level shifter)
- GPIO 26: DAC output to amplifier
- GPIO 5: Switch/trigger input

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/tforster/halloween.git
   cd halloween
   ```

2. **Install Node dependencies:**

   ```bash
   npm install
   ```

3. **Flash MicroPython firmware to ESP32:**

   ```bash
   # Erase existing flash
   esptool.py --port /dev/ttyUSB0 erase_flash

   # Flash MicroPython firmware (adjust path to your downloaded .bin file)
   python -m esptool --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 ESP32_GENERIC-20240602-v1.23.0.bin
   ```

4. **Upload project files to ESP32:**

   ```bash
   # Using ampy
   ampy --port /dev/ttyUSB0 put src/boot.py
   ampy --port /dev/ttyUSB0 put src/main.py
   ampy --port /dev/ttyUSB0 put lib/neopixel.py

   # Upload audio file
   ampy --port /dev/ttyUSB0 mkdir audio
   ampy --port /dev/ttyUSB0 put audio/Storm_exclamation.wav audio/Storm_exclamation.wav
   ```

5. **Connect to the device for testing:**
   ```bash
   # Using mpremote
   mpremote connect /dev/ttyUSB0
   ```

## Usage

Once deployed, the system operates autonomously:

1. **Power on** the ESP32 and connected hardware
2. The system boots and enters **standby mode**, monitoring the trigger input
3. When the trigger is activated (switch pressed, touch detected, etc.):
   - Lightning animation plays across the LED strip (300 pixels in ~2ms batches)
   - Thunder sound plays through the amplifier simultaneously
   - System enters a 5-second cooldown before accepting the next trigger
4. **Repeat** for continuous operation throughout your Halloween display

**Development & Testing:**

- Use `src/lights.py` to test the LED animation independently
- Use `src/test.py` for standalone testing
- Modify configuration constants in `src/main.py` (LED_COUNT, pin assignments, timing)

## High Level Architecture Overview

**Components:**

1. **boot.py**: Bootstrap script that runs on ESP32 startup. Checks for and executes `main.py`.

2. **main.py**: Main application logic featuring:

   - Multi-threaded execution (separate threads for audio and lights)
   - WAV file parsing and playback via DAC
   - Trigger detection and cooldown management
   - Configuration parameters (pin assignments, LED count)

3. **lights.py**: NeoPixel animation module with:

   - Light chaser effect (batched updates for performance)
   - LED initialization and cleanup functions
   - Standalone testing capability

4. **neopixel.py**: MicroPython NeoPixel driver library

**Audio Subsystem:**

- Parses WAV file headers to extract sample rate and format
- Streams audio data from flash storage to DAC output
- Buffered playback (128-byte buffer) for memory efficiency
- Configurable volume control

**LED Subsystem:**

- Batch updates (default: 40 pixels at a time) for faster animation
- White flash color (240, 248, 255 RGB) for lightning effect
- ~2ms delay between batches for flicker effect

**Concurrency:**

- Threading via `_thread` module allows simultaneous audio and visual effects
- Thread-safe flags (`audio_playing`, `light_playing`) prevent overlapping triggers

## Policies

- [Changelog](CHANGELOG.md) - Project changes and version history
- [Code of Conduct](CODE_OF_CONDUCT.md) - Community guidelines
- [Contributing](CONTRIBUTING.md) - How to contribute to this project

## Authors

**Troy Forster**

- Email: troy.forster@gmail.com
- GitHub: [@tforster](https://github.com/tforster)
- Website: [https://www.tforster.com](https://www.tforster.com)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
