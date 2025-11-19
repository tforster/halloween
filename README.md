# Halloween Lightning & Thunder Effect

> **📦 Looking for the 2024 ESP32 version?**  
> This is the **2025 implementation** using Raspberry Pi Pico 2. For the original ESP32-based system with built-in DAC audio, see the [`2024` tag](https://github.com/tforster/halloween/tree/2024).

A Raspberry Pi Pico 2-based Halloween display controller that creates synchronised lightning and thunder effects using NeoPixel LED strips and high-quality MP3 audio playback.

**Key Features:**

- 🎵 High-quality MP3 audio via dedicated hardware module
- ⚡ 300+ NeoPixel LED lightning animations
- 🎲 Autonomous random triggering (60-120 second intervals)
- 📦 Multi-board deployment (3 independent units)

**For detailed technical documentation, see [Developer Guide](docs/Developer-Guide.md)**

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

- VS Code with [Raspberry Pi Pico extension](https://marketplace.visualstudio.com/items?itemName=raspberry-pi.raspberry-pi-pico)
- Python 3.13+
- Node.js/npm

> 📖 **Full hardware details and assembly:** [Developer Guide - Hardware Assembly](docs/Developer-Guide.md#hardware-assembly-notes)

### Installation

```bash
# 1. Clone and setup
git clone https://github.com/tforster/halloween.git
cd halloween
git checkout 2025
npm install

# 2. Setup Python environment
python3.13 -m venv venv
source venv/bin/activate  # or: source activate.sh
pip install -r requirements.txt

# 3. Configure VS Code
# Install Raspberry Pi Pico extension
# Press Ctrl+Shift+P → "MicroPython: Configure Project"
# Select "Raspberry Pi Pico 2"

# 4. Prepare audio files
python devops/prepare_audio.py
# Copy audio/prepared/*.mp3 to MicroSD card

# 5. Upload to Pico
# Right-click src/ folder → "Upload to Pico"
```

> 📖 **Detailed setup instructions:** [Developer Guide - Development Environment Setup](docs/Developer-Guide.md#development-environment-setup)

## Usage

**Autonomous Mode** (default): System automatically triggers lightning and thunder effects every 60-120 seconds.

**Triggered Mode** (optional): Connect a switch/sensor to trigger effects manually.

> 📖 **Configuration, testing, and debugging:** [Developer Guide - Testing & Debugging](docs/Developer-Guide.md#testing--debugging)

## Architecture

**System Components:**

- `src/boot.py` - Bootstrap loader
- `src/main.py` - Main application with random triggering
- `src/lights.py` - NeoPixel lightning animations
- `src/mp3_player.py` - DFPlayer Mini serial interface

**Host Tools:**

- `devops/prepare_audio.py` - Prepare MP3 files for DFPlayer
- `devops/test_mp3_serial.py` - Test MP3 module communication

> 📖 **Complete architecture and ADRs:** [Developer Guide - Architecture Decision Records](docs/Developer-Guide.md#architecture-decision-records-adrs)

## Documentation

- **[Developer Guide](docs/Developer-Guide.md)** - Complete technical documentation
  - Architecture Decision Records (ADRs)
  - Setup and configuration
  - Hardware assembly
  - DevOps tools
  - Testing and debugging
  - Known issues
- **[AGENTS.md](AGENTS.md)** - AI agent context and conventions
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

This project is licensed under the MIT Licence.
