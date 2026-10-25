# Simulate in Wokwi <!-- omit in toc -->

Run the real firmware on a simulated Pico 2 with both 300-pixel strips, watch overlapping strikes and read the thunder commands, without building the hardware. Why Wokwi is used is in [ADR-012](../reference/adr/0012-wireviz-and-wokwi.md).

## Table of Contents <!-- omit in toc -->

- [1. Prerequisites](#1-prerequisites)
- [2. Steps](#2-steps)
- [3. Verification](#3-verification)
- [4. Troubleshooting](#4-troubleshooting)

## 1. Prerequisites

- VS Code with the [Wokwi extension](https://docs.wokwi.com/vscode/getting-started) and a Wokwi licence activated in it
- The Python virtual environment with `requirements.txt` installed, which provides `mpremote` ([Set Up the Development Environment](./set-up-development-environment.md))

## 2. Steps

1. In VS Code, run **Wokwi: Select Config File** and choose `wokwi/wokwi.toml`, then **Wokwi: Start Simulator**. The Pico 2 boots the MicroPython image from `devops/image/`; the strips stay dark.
2. Keep the simulator tab visible (a hidden tab can pause the simulation), and in a terminal run:

   ```bash
   npm run simulate
   ```

   This copies `src/` into the simulated Pico over Wokwi's RFC 2217 port (4000) and starts the storm in test mode, so each rig strikes every 5–10 s. `src/main.py` is not edited.

3. Press Ctrl-C to stop. The simulator's filesystem is empty on each start, so run `npm run simulate` again after restarting it.

## 3. Verification

- Rig A (top strip, GP16) and Rig B (bottom strip, GP17) strike at different times.
- Within a few minutes the two rigs strike together, and both strips keep animating through the overlap.
- Each strike prints `⚡ Rig A strikes` (or B) followed by a play-track frame such as `DFPlayer < 7E FF 06 03 00 00 02 FE F6 EF`; Wokwi has no DFPlayer part, so this output stands in for it. The frame format is in [DFPlayer Mini Protocol](../reference/dfplayer-protocol.md).

## 4. Troubleshooting

| Symptom                                                  | Fix                                                                                                                                              |
| :------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------- |
| `failed to access rfc2217://localhost:4000`              | The simulator is not running, or another program holds the port. Start it, or pass `npm run simulate -- --port=<n>` to match `rfc2217ServerPort` |
| `could not enter raw repl`                               | Press Ctrl-A in the Wokwi serial monitor, then run `npm run simulate` again                                                                      |
| `mpremote` errors that mention the protocol or a version | Install the `mpremote` release matching the image (`pip install mpremote==1.26.1`)                                                               |

[← Back to How-To Guides](./README.md)
