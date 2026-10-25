# Halloween Lightning & Thunder Effect

A Raspberry Pi Pico 2-based Halloween display controller that creates synchronised lightning and thunder effects using NeoPixel LED strips and high-quality MP3 audio playback.

**Key Features:**

- 🎵 High-quality MP3 audio via dedicated hardware module
- ⚡ 300+ NeoPixel LED lightning animations
- 🎲 Autonomous random triggering (60-120 second intervals)
- 📦 Multi-board deployment (3 independent units)

**For detailed technical documentation, see [the docs](docs/README.md).**

## Previous Years

| Year | Highlights                                                                                                                                                                                      | Source                                                        |
| :--- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------ |
| 2025 | • Raspberry Pi Pico 2 + DFPlayer Mini MP3 module (16-bit audio from MicroSD)<br>• Autonomous random triggering every 60-120 seconds<br>• Three independent boards with three lightning patterns | [`2025` tag](https://github.com/tforster/halloween/tree/2025) |
| 2024 | • ESP32 with built-in 8-bit DAC playing WAV thunder<br>• Threaded, simultaneous lightning and thunder<br>• Single board, manually triggered by switch                                           | [`2024` tag](https://github.com/tforster/halloween/tree/2024) |

## Quick Start

### What You Need

**Hardware:**

- Raspberry Pi Pico 2
- Mini MP3 Player Module ([Universal Solder](https://www.universal-solder.ca/product/mini-mp3-player-module-with-microsd-slot-for-arduino-etc/))
- 60W BTL Amplifier ([Amazon](https://www.amazon.ca/dp/B0D8HCV43H))
- 300+ WS2812B NeoPixel LED strip
- Logic level shifter (3.3V→5V)
- Power supplies (5V 6A, 12V for amplifier)

**Software:**

- mpremote (installed via `requirements.txt`)
- Python 3.13+
- Node.js/npm

> 📖 **Full hardware details and assembly:** [Assemble the Hardware](docs/how-to/assemble-hardware.md)

### Installation

```bash
# 1. Clone and setup
git clone https://github.com/tforster/halloween.git
cd halloween
npm install

# 2. Setup Python environment
python3.13 -m venv venv
source venv/bin/activate  # or: source activate.sh
pip install -r requirements.txt

# 3. Flash MicroPython firmware (first time only)
# Hold BOOTSEL, connect USB, drag devops/image/RPI_PICO2-*.uf2 onto the Pico drive

# 4. Prepare audio files
python devops/prepare_audio.py
# Copy audio/prepared/*.mp3 to MicroSD card

# 5. Upload to Pico (uses mpremote)
npm run deploy
```

> 📖 **Detailed setup instructions:** [Set Up the Development Environment](docs/how-to/set-up-development-environment.md)

## Usage

**Autonomous Mode** (default): System automatically triggers lightning and thunder effects every 60-120 seconds.

**Triggered Mode** (optional): Connect a switch/sensor to trigger effects manually.

> 📖 **Configuration, testing, and debugging:** [Test and Debug](docs/how-to/test-and-debug.md)

## Architecture

**System Components:**

- `src/boot.py` - Bootstrap loader
- `src/main.py` - Main application with random triggering
- `src/lights.py` - NeoPixel lightning animations
- `src/mp3_player.py` - DFPlayer Mini serial interface

**Host Tools:**

- `devops/prepare_audio.py` - Prepare MP3 files for DFPlayer
- `devops/test_mp3_serial.py` - Test MP3 module communication

> 📖 **Complete architecture and ADRs:** [Architecture Decision Records](docs/reference/adr/README.md)

## Documentation

- **[Documentation home](docs/README.md)** - Tutorials, how-to guides, reference and explanation
- **[2026 Blueprint](docs/explanation/2026-blueprint.md)** - The two-rig, one-Pico design in progress
- **[CLAUDE.md](CLAUDE.md)** - AI agent context and conventions
- **[CHANGELOG.md](CHANGELOG.md)** - Version history

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Policies

- [Code of Conduct](CODE_OF_CONDUCT.md) - Community guidelines
- [Contributing](CONTRIBUTING.md) - How to contribute to this project

## Authors

**Troy Forster**

- Email: troy.forster@gmail.com
- GitHub: [@tforster](https://github.com/tforster)
- Website: [https://www.tforster.com](https://www.tforster.com)

## Licence

This project is licensed under the MIT Licence. See [LICENSE](LICENSE).
