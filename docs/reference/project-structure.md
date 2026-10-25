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
│   ├── main.py           # Configuration, rigs, thunder channel, asyncio scheduler, start-up
│   ├── lights.py         # NeoPixel lightning patterns (coroutines)
│   ├── mp3_player.py     # DFPlayer Mini frame writer
│   └── clock.py          # Real clock passed to the scheduler and patterns
├── devops/               # Host-side tools (bash and Python 3.13)
│   ├── deploy.sh         # Copy src/ to the Pico
│   ├── deploy-dev.sh     # Copy src/ to the Pico and optionally run it
│   ├── run.sh            # Run a file on the Pico without copying it
│   ├── serve.sh          # Mount src/ on the Pico for live editing
│   ├── simulate.sh       # Copy src/ into a running Wokwi simulation and start it
│   ├── prepare_audio.py  # Number MP3s for the DFPlayer
│   ├── test_mp3_serial.py# Drive a DFPlayer from the host over USB-serial
│   ├── includes/         # Shared bash helpers (parseArgs.sh, colours.sh)
│   └── image/            # MicroPython and flash_nuke .uf2 images
├── tests/                # Repo convention tests (node:test) and firmware tests (pytest)
├── wokwi/                # Wokwi simulation: diagram.json and wokwi.toml
├── docs/                 # Diátaxis documentation
├── audio/                # Thunder recordings (gitignored; they go on the SD card)
├── CLAUDE.md             # Agent context
├── package.json          # npm scripts, oxlint and oxfmt
├── pyproject.toml        # Python tool configuration
├── requirements.txt      # Host Python dependencies
└── requirements-dev.txt  # Host Python dev dependencies
```

Code in `src/` runs on the Pico under MicroPython; code in `devops/` and `tests/` runs on the host. Below `main.start()`, `src/` imports no hardware module, so `tests/` imports it under CPython with fakes. Audio goes on the DFPlayer's MicroSD card, never on the Pico.

## 2. Firmware Modules

| Module          | Responsibility                                                                                                                                                                                                                                                       |
| :-------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `boot.py`       | Start-up hook; hands over to `main.py`                                                                                                                                                                                                                               |
| `main.py`       | Configuration constants; `Rig`, `buildRigs`, the `Thunder` channel (latest strike wins, 100 ms command spacing) and the `Storm` scheduler, one asyncio task per rig plus the manual trigger and heartbeat. `start()` is the only place hardware is created           |
| `lights.py`     | Classic, flickering and rolling patterns as coroutines, chosen at random, with a 10 % chance of a red strike. They await the clock after every strip write, so overlapping strikes interleave. `testColors`, `testLightning` and `testAllPatterns` run from the REPL |
| `mp3_player.py` | `MP3Player`, which formats and writes frames to the UART it is given without sleeping, and `startPlayer`, the blocking start-up sequence; see [DFPlayer Mini Protocol](./dfplayer-protocol.md)                                                                       |
| `clock.py`      | `PicoClock`: `now()`, `since(ticks)` and `sleep(ms)` over `time.ticks_ms` and `asyncio.sleep_ms`. Tests pass a virtual clock instead                                                                                                                                 |

All firmware uses MicroPython built-ins (`asyncio`, `machine`, `neopixel`, `os`, `random`, `time`); there are no external libraries. Why the scheduler is built this way is in [ADR-011](./adr/0011-asyncio-scheduling.md).

## 3. Configuration

Constants at the top of `src/main.py`:

| Constant             | Default      | Meaning                                                                                                                                          |
| :------------------- | :----------- | :----------------------------------------------------------------------------------------------------------------------------------------------- |
| `RIGS`               | Rig A, Rig B | One entry per rig: `name`, data `pin` (GP16, GP17), `pixels` (300) and `intervalS`, the (min, max) wait in seconds after a strike ends (60, 120) |
| `MP3_TX_PIN`         | `4`          | UART1 TX to the DFPlayer                                                                                                                         |
| `MP3_RX_PIN`         | `5`          | UART1 RX, reserved; nothing is read back                                                                                                         |
| `MP3_VOLUME`         | `25`         | DFPlayer volume, 0–30                                                                                                                            |
| `TRACK_COUNT`        | `3`          | Thunder tracks on the SD card                                                                                                                    |
| `TEST_MODE`          | `False`      | Use `TEST_INTERVAL_S` for every rig instead of its own `intervalS`                                                                               |
| `TEST_INTERVAL_S`    | `(5, 10)`    | Wait between strikes in test mode, seconds                                                                                                       |
| `TRIGGER_PIN`        | `15`         | Manual trigger GPIO                                                                                                                              |
| `USE_MANUAL_TRIGGER` | `False`      | Enable the manual trigger: each press strikes a random idle rig                                                                                  |
| `TRIGGER_POLL_MS`    | `50`         | Trigger poll period, which also debounces it                                                                                                     |
| `STATUS_LED_PIN`     | `25`         | Onboard LED: solid while starting, 1 Hz heartbeat while the storm runs                                                                           |

[← Back to Reference](./README.md)
