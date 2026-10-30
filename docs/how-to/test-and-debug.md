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
from mp3_player import testMP3Player

testMP3Player(4, 5)  # volume 20, plays the first file copied to the SD card for 3 s, then stops
```

To send commands yourself, open the UART and wake the module with `startPlayer`. `MP3Player` does not wait between commands, so leave 100 ms between them:

```python
import machine
from mp3_player import startPlayer

player = startPlayer(machine.UART(1, baudrate=9600, tx=machine.Pin(4), rx=machine.Pin(5)))
player.setVolume(20)  # 0-30
player.playTrack(2)
```

Each frame sent is printed as `DFPlayer < 7E FF ...`.

## 2. NeoPixels

```python
from lights import testLightning, testAllPatterns

testLightning(16)    # one random strike on Rig A (GP16)
testAllPatterns(17)  # classic, flickering and rolling on Rig B (GP17), blue then red
```

## 3. Faster Strikes

Set `TEST_MODE = True` in `src/main.py` and every rig strikes every 1–3 s (`TEST_INTERVAL_S`) instead of its configured interval, so overlaps are easy to see. The rigs' own intervals stay as written. Set it back to `False` before deploying.

To try it without editing the file, run the storm from the REPL instead:

```python
import main
main.TEST_MODE = True
main.start()
```

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
npm run typecheck  # tsc on tests/ JS, then mypy on devops/
npm run lint:py    # ruff on devops/
npm run type:py    # mypy on devops/
npm run test:py    # pytest: firmware scheduler and DFPlayer frames, with fake hardware
```

The Python checks need the virtual environment with `requirements-dev.txt` installed (`source activate.sh`). The firmware tests in `tests/` import `src/` under CPython with a virtual clock, fake strips and a fake UART, so a half-hour storm runs in under a second. To watch the firmware run without hardware, see [Simulate in Wokwi](./simulate-in-wokwi.md). When something misbehaves on hardware, check [Known Issues](../reference/known-issues.md) first.

[← Back to How-To Guides](./README.md)
