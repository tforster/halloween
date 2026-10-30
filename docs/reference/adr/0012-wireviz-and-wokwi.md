# ADR-012: WireViz and Wokwi for Hardware Diagrams and Simulation <!-- omit in toc -->

**Status:** Accepted (2026 season)

**Context:**
Mermaid covers the project's system context, runtime flow and state diagrams, but this project is hardware as well as software[^diagram-tools]. Two needs fall outside Mermaid:

1. A wiring diagram of the whole installation that can be reviewed and versioned like code.
2. A way to watch the two-rig firmware run, overlapping strikes included, without building the hardware.

**Decision:**

- **WireViz** for the installation's wiring harness. [`docs/reference/assets/wiring.yml`](../assets/wiring.yml) lists every supply, module, resistor and wire, with physical pin numbers, wire gauges and lengths, including the 2.7 m maximum data runs. `npm run wiring` renders it to [`wiring.svg`](../assets/wiring.svg) beside it, which is committed because GitHub does not render WireViz; the [Assemble the Hardware](../../how-to/assemble-hardware.md) guide shows the SVG. WireViz is a pip package in `requirements-dev.txt` and needs Graphviz on the host.
- **Wokwi** for simulation. `wokwi/diagram.json` holds a Pico (RP2040) with two WS2812 strips on GP16 and GP17, the real rig pins. The installation uses a Pico 2, but Wokwi's Pico 2 (RP2350) corrupted the running MicroPython at random (SyntaxErrors importing byte-identical files, failed attribute lookups, garbled tracebacks) on 1.26.1 and 1.29.0, while its RP2040 ran the same firmware for minutes without fault (HALL-6). The firmware uses nothing RP2350-specific, so the RP2040 shows the same scheduling. The strips have 60 pixels, not the real 300, because Wokwi models every WS2812 bit and two 300-pixel strips ran at about 4% of real time; `npm run simulate` sets each rig to 60 pixels for that run only. `wokwi/wokwi.toml` boots the stock RPI_PICO MicroPython image from `devops/image/`, the same release as the Pico 2 image, and `npm run simulate` mounts `src/` from the host over Wokwi's RFC 2217 serial port and starts the storm in test mode. Wokwi has no DFPlayer part, and its Pico 2 hung inside `machine.UART(1, ...)`, so `npm run simulate` sets `main.SIMULATED` to skip the UART; `MP3Player` prints every frame it sends and the serial output stands in for the DFPlayer.

**Rationale:**

- **Text in the repo:** `wiring.yml`, `diagram.json` and `wokwi.toml` are plain text, so the wiring and the simulated circuit are reviewed and versioned with the firmware
- **One source for the wiring:** the diagram, its parts and its connections come from one YAML file, so the picture cannot drift from the parts list
- **Real firmware:** the simulator runs the same `src/` files that `npm run deploy` copies to the Pico, not a port of them
- **Overlaps on demand:** test mode's 1–3 s intervals make overlapping strikes common enough to watch within seconds

**Consequences:**

- `pytest` re-renders `wiring.yml` and fails when the committed `wiring.svg` is stale, so a wiring change must be re-rendered in the same commit; it also checks the harness against the blueprint (supplies, common ground, data path and level shifter, amp feed)
- The simulation is a manual check (blueprint seam 3); it is not run in CI unless the Wokwi CLI, which needs a licence token, is adopted later
- Wokwi runs in VS Code with the Wokwi extension, or on wokwi.com; neither runs on the Pico
- The firmware is mounted from the host rather than copied, so an edit to `src/` needs only another `npm run simulate`, and `npm run simulate` is run after each simulator start
- The simulation does not exercise RP2350-specific behaviour; that is checked on the bench
- Thunder is checked only as serial frames in simulation; audio is checked on the bench

[^diagram-tools]: WireViz and Wokwi have been added because they fulfil diagramming needs beyond Mermaid that this project requires. It is not just software but also hardware: WireViz documents physical wiring harnesses between modules, and Wokwi provides a breadboard-level view and simulation of the Pico and LED strips.

[← Back to ADR index](./README.md)
