# Project Structure <!-- omit in toc -->

Where things live in the repo, what each firmware module does and the configuration constants in `src/main.py`.

## Table of Contents <!-- omit in toc -->

- [1. Layout](#1-layout)
- [2. Firmware Modules](#2-firmware-modules)
- [3. Configuration](#3-configuration)

## 1. Layout

```text
halloween/
├── src/                  # MicroPython firmware, copied to the Pico
│   ├── boot.py           # Runs on power-up and starts main.py
│   ├── main.py           # Configuration, random-interval scheduler, manual trigger
│   ├── lights.py         # NeoPixel lightning patterns
│   └── mp3_player.py     # DFPlayer Mini UART driver
├── devops/               # Host-side tools (bash and Python 3.13)
│   ├── deploy.sh         # Copy src/ to the Pico
│   ├── deploy-dev.sh     # Copy src/ to the Pico and optionally run it
│   ├── run.sh            # Run a file on the Pico without copying it
│   ├── serve.sh          # Mount src/ on the Pico for live editing
│   ├── prepare_audio.py  # Number MP3s for the DFPlayer
│   ├── test_mp3_serial.py# Drive a DFPlayer from the host over USB-serial
│   ├── includes/         # Shared bash helpers (parseArgs.sh, colours.sh)
│   └── image/            # MicroPython and flash_nuke .uf2 images
├── tests/                # Repo convention tests (node:test)
├── docs/                 # Diátaxis documentation
├── audio/                # Thunder recordings (gitignored; they go on the SD card)
├── CLAUDE.md             # Agent context
├── package.json          # npm scripts, oxlint and oxfmt
├── pyproject.toml        # Python tool configuration
├── requirements.txt      # Host Python dependencies
└── requirements-dev.txt  # Host Python dev dependencies
```

Code in `src/` runs on the Pico under MicroPython; code in `devops/` and `tests/` runs on the host. Audio goes on the DFPlayer's MicroSD card, never on the Pico.

## 2. Firmware Modules

| Module          | Responsibility                                                                                                                                                                                                         |
| :-------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `boot.py`       | Start-up hook; hands over to `main.py`                                                                                                                                                                                 |
| `main.py`       | Holds the configuration constants, waits a random interval, then fires a strike: a lightning pattern and a thunder track together                                                                                      |
| `lights.py`     | Classic, flickering and rolling patterns, chosen at random, with a 10 % chance of a red strike. Writes pixels in batches of `LED_BATCH_SIZE` to limit memory use. `testLightning` and `testAllPatterns` run standalone |
| `mp3_player.py` | `MP3Player` class; see [DFPlayer Mini Protocol](./dfplayer-protocol.md)                                                                                                                                                |

All firmware uses MicroPython built-ins (`machine`, `neopixel`, `random`, `time`); there are no external libraries.

## 3. Configuration

Constants at the top of `src/main.py`:

| Constant             | Default | Meaning                                |
| :------------------- | :------ | :------------------------------------- |
| `LED_COUNT`          | `300`   | Pixels in the strip                    |
| `LED_PIN`            | `16`    | NeoPixel data GPIO                     |
| `LED_BATCH_SIZE`     | `40`    | Pixels per update batch                |
| `MP3_TX_PIN`         | `4`     | UART1 TX to the DFPlayer               |
| `MP3_RX_PIN`         | `5`     | UART1 RX from the DFPlayer             |
| `MP3_VOLUME`         | `25`    | DFPlayer volume, 0–30                  |
| `TRACK_COUNT`        | `3`     | Thunder tracks on the SD card          |
| `MIN_INTERVAL`       | `60`    | Shortest wait between strikes, seconds |
| `MAX_INTERVAL`       | `120`   | Longest wait between strikes, seconds  |
| `COOLDOWN_PERIOD`    | `5`     | Pause after a strike, seconds          |
| `TRIGGER_PIN`        | `15`    | Manual trigger GPIO                    |
| `USE_MANUAL_TRIGGER` | `False` | Enable the manual trigger              |
| `STATUS_LED_PIN`     | `25`    | Onboard status LED                     |

[← Back to Reference](./README.md)
