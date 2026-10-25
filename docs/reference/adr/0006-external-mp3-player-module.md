# ADR-006: External MP3 Player Module for Audio <!-- omit in toc -->

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

[← Back to ADR index](./README.md)
