# ADR-012: WireViz and Wokwi for Hardware Diagrams and Simulation <!-- omit in toc -->

**Status:** Accepted (2026 season)

**Context:**
Mermaid covers the project's system context, runtime flow and state diagrams, but this project is hardware as well as software[^diagram-tools]. Two needs fall outside Mermaid:

1. A wiring diagram of the whole installation that can be reviewed and versioned like code.
2. A way to watch the two-rig firmware run, overlapping strikes included, without building the hardware.

**Decision:**

- **WireViz** for the installation's wiring harness: decision and harness are added by the wiring story (HALL-4).
- **Wokwi** for simulation. `wokwi/diagram.json` holds a Pico 2 with two 300-pixel WS2812 strips on GP16 and GP17, the real rig pins. `wokwi/wokwi.toml` boots the stock MicroPython image from `devops/image/`, and `npm run simulate` copies `src/` in over Wokwi's RFC 2217 serial port and starts the storm in test mode. Wokwi has no DFPlayer part, so `MP3Player` prints every frame it sends and the serial output stands in for the DFPlayer.

**Rationale:**

- **Text in the repo:** `diagram.json` and `wokwi.toml` are plain text, so the simulated circuit is reviewed and versioned with the firmware
- **Real firmware:** the simulator runs the same `src/` files that `npm run deploy` copies to the Pico, not a port of them
- **Overlaps on demand:** test mode's 5–10 s intervals make overlapping strikes common enough to watch

**Consequences:**

- The simulation is a manual check (blueprint seam 3); it is not run in CI unless the Wokwi CLI, which needs a licence token, is adopted later
- Wokwi runs in VS Code with the Wokwi extension, or on wokwi.com; neither runs on the Pico
- The simulator's filesystem is empty on every start, so `npm run simulate` is run each time
- Thunder is checked only as serial frames in simulation; audio is checked on the bench

[^diagram-tools]: WireViz and Wokwi have been added because they fulfil diagramming needs beyond Mermaid that this project requires. It is not just software but also hardware: WireViz documents physical wiring harnesses between modules, and Wokwi provides a breadboard-level view and simulation of the Pico and LED strips.

[← Back to ADR index](./README.md)
