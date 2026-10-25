# ADR-005: Migration from ESP32 to Raspberry Pi Pico 2 (2025) <!-- omit in toc -->

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
| **Development**     | esptool, ampy, mpremote           | mpremote via `devops/` scripts      |

**Rationale:**

- **Superior audio quality:** Dedicated hardware MP3 decoder delivers true CD-quality sound
- **Simpler code:** No manual audio parsing, streaming, or DAC management
- **Better audio management:** Easy to add/change sounds via SD card
- **More cost-effective:** Lower total cost enables 3-board deployment
- **Easier development:** mpremote wrapped in `devops/` scripts (`npm run deploy`, `npm run run`)
- **Future-proof:** More memory headroom for additional features
- **Better availability:** Pico 2 easier to source than ESP32

**Consequences:**

- Team must learn Pico 2 platform and tooling
- Existing ESP32 code not reusable (complete rewrite required)
- Additional hardware component (MP3 module) adds complexity
- Serial communication protocol must be implemented for MP3 control
- Logic level shifting still required for NeoPixels

**Historical Reference:** See [2024 ESP32 implementation](https://github.com/tforster/halloween/tree/2024) for comparison.

[← Back to ADR index](./README.md)
