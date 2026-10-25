# Test and Debug <!-- omit in toc -->

Exercise the lights and the MP3 player on real hardware from the REPL, talk to a DFPlayer directly from the host, and run the host-side checks.

## Table of Contents <!-- omit in toc -->

- [1. MP3 Player](#1-mp3-player)
- [2. NeoPixels](#2-neopixels)
- [3. Faster Strikes](#3-faster-strikes)
- [4. DFPlayer Without the Pico](#4-dfplayer-without-the-pico)
- [5. Host-Side Checks](#5-host-side-checks)

## 1. MP3 Player

Copy the firmware to the Pico ([Deploy to the Pico](./deploy-to-pico.md)), open a REPL with `mpremote repl`, press Ctrl-C to stop `main.py`, then:

```python
from mp3_player import MP3Player

player = MP3Player(tx_pin=4, rx_pin=5)
player.setVolume(20)  # 0-30
player.playTrack(1)   # plays the first file copied to the SD card
```

## 2. NeoPixels

```python
from lights import testLightning, testAllPatterns

testLightning(16)    # one random strike on GP16
testAllPatterns(16)  # classic, flickering and rolling in turn
```

## 3. Faster Strikes

`src/main.py` carries commented-out short intervals for bench testing. Swap them in to see a strike every few seconds:

```python
MIN_INTERVAL = 5
MAX_INTERVAL = 10
```

Restore 60 and 120 before deploying.

## 4. DFPlayer Without the Pico

`devops/test_mp3_serial.py` drives a DFPlayer Mini from the host through a USB-serial adapter, which isolates protocol problems from Pico problems.

```text
USB-serial adapter      DFPlayer Mini
TX (output)      →      RX (pin 2)
RX (input)       ←      TX (pin 3)
GND              ↔      GND
5V (optional)    →      VCC (if not powered separately)
```

```bash
python devops/test_mp3_serial.py /dev/ttyUSB0
```

The frames it sends are described in [DFPlayer Mini Protocol](../reference/dfplayer-protocol.md).

## 5. Host-Side Checks

```bash
npm test           # repo convention tests (node:test)
npm run lint       # oxlint
npm run format:check
npm run lint:py    # ruff on devops/
npm run type:py    # mypy on devops/
npm run test:py    # pytest
```

The Python checks need `requirements-dev.txt` installed. When something misbehaves on hardware, check [Known Issues](../reference/known-issues.md) first.

[← Back to How-To Guides](./README.md)
