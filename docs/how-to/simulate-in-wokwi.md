# Simulate in Wokwi <!-- omit in toc -->

Run the real firmware on a simulated Pico with both strips, watch overlapping strikes and read the thunder commands, without building the hardware. Why Wokwi is used is in [ADR-012](../reference/adr/0012-wireviz-and-wokwi.md).

## Table of Contents <!-- omit in toc -->

- [1. Prerequisites](#1-prerequisites)
- [2. Steps](#2-steps)
- [3. Verification](#3-verification)
- [4. Troubleshooting](#4-troubleshooting)

## 1. Prerequisites

- VS Code with the [Wokwi extension](https://docs.wokwi.com/vscode/getting-started) and a Wokwi licence activated in it
- The Python virtual environment with `requirements.txt` installed, which provides `mpremote` ([Set Up the Development Environment](./set-up-development-environment.md))

## 2. Steps

1. In VS Code, run **Wokwi: Select Config File** and choose `wokwi/wokwi.toml`, then **Wokwi: Start Simulator**. The Pico boots the RPI_PICO MicroPython image from `devops/image/`; the strips stay dark. The simulation uses an RP2040 Pico, not the installation's Pico 2, because Wokwi's RP2350 corrupts MicroPython ([ADR-012](../reference/adr/0012-wireviz-and-wokwi.md)).
2. Keep the simulator tab visible (a hidden tab can pause the simulation), and in a terminal run:

   ```bash
   npm run simulate
   ```

   This mounts `src/` on the simulated Pico over Wokwi's RFC 2217 port (4000) and starts the storm in test mode, so each rig strikes every 1–3 s. The simulated strips have 60 pixels, not 300, and each rig drives 60 for this run: Wokwi models every WS2812 bit, and two 300-pixel strips run at about 4% of real time. `src/main.py` is not edited.

   For a lighter run with one strip, use `npm run simulate -- --rigs=1`.

3. Press Ctrl-C to stop. `src/` is mounted, not copied, so nothing is stored on the Pico. Run `npm run simulate` again after restarting the simulator.

## 3. Verification

- Rig A (top strip, GP16) and Rig B (bottom strip, GP17) strike at different times.
- Within a few minutes the two rigs strike together, and both strips keep animating through the overlap.
- Each strike prints `Rig A strikes` (or B) followed by a play-track frame such as `DFPlayer < 7E FF 06 03 00 00 02 FE F6 EF`; Wokwi has no DFPlayer part, so the simulated run opens no UART (`main.SIMULATED`) and this output stands in for the DFPlayer. The frame format is in [DFPlayer Mini Protocol](../reference/dfplayer-protocol.md).

## 4. Troubleshooting

| Symptom                                                  | Fix                                                                                                                                              |
| :------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------- |
| `failed to access rfc2217://localhost:4000`              | The simulator is not running, or another program holds the port. Start it, or pass `npm run simulate -- --port=<n>` to match `rfc2217ServerPort` |
| `could not enter raw repl`                               | A storm from an earlier run is still going. Restart the simulator (or press Ctrl-A in its serial monitor), then run `npm run simulate` again     |
| `mpremote` errors that mention the protocol or a version | Install the `mpremote` release matching the image (`pip install mpremote==1.29.0`)                                                               |

[← Back to How-To Guides](./README.md)
