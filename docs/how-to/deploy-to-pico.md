# Deploy to the Pico <!-- omit in toc -->

Flash MicroPython onto a Raspberry Pi Pico 2 and copy the firmware in `src/` onto it.

## Table of Contents <!-- omit in toc -->

- [1. Prerequisites](#1-prerequisites)
- [2. Steps](#2-steps)
  - [2.1. Flash MicroPython (first time only)](#21-flash-micropython-first-time-only)
  - [2.2. Copy the firmware](#22-copy-the-firmware)
  - [2.3. Check before leaving it on display](#23-check-before-leaving-it-on-display)
- [3. Verification](#3-verification)

## 1. Prerequisites

- A [development environment](./set-up-development-environment.md) with the virtual environment active
- A Pico 2 and a USB data cable

## 2. Steps

### 2.1. Flash MicroPython (first time only)

1. Hold the BOOTSEL button on the Pico 2.
2. Connect the USB cable, then release BOOTSEL. The Pico appears as a USB drive.
3. Drag `devops/image/RPI_PICO2-*.uf2` onto the drive. The Pico reboots into MicroPython.

Newer firmware is at <https://micropython.org/download/RPI_PICO2/>. To wipe a Pico's flash first, flash `devops/image/flash_nuke.uf2` the same way.

### 2.2. Copy the firmware

```bash
npm run deploy
```

This runs `devops/deploy.sh`, which copies everything in `src/` to the root of the Pico with mpremote. To copy files individually instead:

```bash
mpremote cp src/main.py :main.py
mpremote cp src/lights.py :lights.py
mpremote cp src/mp3_player.py :mp3_player.py
```

### 2.3. Check before leaving it on display

- Test the code in the REPL first; see [Test and Debug](./test-and-debug.md)
- Audio files are on the SD card; see [Prepare Thunder Audio](./prepare-audio.md)
- Pin assignments in `src/main.py` match the wiring; see [Hardware](../reference/hardware.md#2-pin-assignments)
- `boot.py`, `main.py`, `lights.py` and `mp3_player.py` are all on the Pico

## 3. Verification

Power-cycle the Pico. `boot.py` starts `main.py`, the onboard LED shows the controller is running, and the first strike arrives within the configured interval.

[← Back to How-To Guides](./README.md)
