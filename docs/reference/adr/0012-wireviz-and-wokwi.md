# ADR-012: WireViz and Wokwi for Hardware Diagrams and Simulation <!-- omit in toc -->

**Status:** Accepted (2026 season)

**Context:**
Mermaid covers the project's system context, runtime flow and state diagrams, but this project is hardware as well as software[^diagram-tools]. Two needs fall outside Mermaid:

1. A wiring diagram of the whole installation that can be reviewed and versioned like code.
2. A way to watch the two-rig firmware run, overlapping strikes included, without building the hardware.

**Decision:**

- **WireViz** for the installation's wiring harness: decision and harness are added by the wiring story (HALL-4).
- **Wokwi** for simulation. `wokwi/diagram.json` holds a Pico 2 with two WS2812 strips on GP16 and GP17, the real rig pins. The strips have 60 pixels, not the real 300, because Wokwi models every WS2812 bit and two 300-pixel strips ran at about 4% of real time; `npm run simulate` sets each rig to 60 pixels for that run only. `wokwi/wokwi.toml` boots the stock MicroPython image from `devops/image/`, and `npm run simulate` mounts `src/` from the host over Wokwi's RFC 2217 serial port and starts the storm in test mode. Wokwi has no DFPlayer part, and its Pico 2 hangs inside `machine.UART(1, ...)` on MicroPython 1.26.1 and 1.29.0, so `npm run simulate` sets `main.SIMULATED` to skip the UART; `MP3Player` prints every frame it sends and the serial output stands in for the DFPlayer.

**Rationale:**

- **Text in the repo:** `diagram.json` and `wokwi.toml` are plain text, so the simulated circuit is reviewed and versioned with the firmware
- **Real firmware:** the simulator runs the same `src/` files that `npm run deploy` copies to the Pico, not a port of them
- **Overlaps on demand:** test mode's 1–3 s intervals make overlapping strikes common enough to watch within seconds

**Consequences:**

- The simulation is a manual check (blueprint seam 3); it is not run in CI unless the Wokwi CLI, which needs a licence token, is adopted later
- Wokwi runs in VS Code with the Wokwi extension, or on wokwi.com; neither runs on the Pico
- The simulated Pico 2's flash is not writable, so the firmware is mounted from the host rather than copied, and `npm run simulate` is run after each simulator start
- Thunder is checked only as serial frames in simulation; audio is checked on the bench

[^diagram-tools]: WireViz and Wokwi have been added because they fulfil diagramming needs beyond Mermaid that this project requires. It is not just software but also hardware: WireViz documents physical wiring harnesses between modules, and Wokwi provides a breadboard-level view and simulation of the Pico and LED strips.

[← Back to ADR index](./README.md)
