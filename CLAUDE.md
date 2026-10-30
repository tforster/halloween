# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

An annual Halloween display: WS2812B NeoPixel lightning with synchronised MP3 thunder, driven by a Raspberry Pi Pico 2 running MicroPython. Each season is a new edition on `main`; earlier ones are frozen as year tags (`2024` ESP32, `2025` three independent Pico boards).

**2026 is in progress.** The target is two rigs (reused 300-pixel strips) driven by **one** Pico 2, each striking on its own random 60–120 s timer, with one DFPlayer Mini, amplifier and speaker shared on a latest-strike-wins basis. `src/` holds the two-rig firmware (HALL-3) and `docs/reference/assets/wiring.yml` the two-rig wiring (HALL-4). Where docs disagree, `docs/explanation/2026-blueprint.md` is the target: read it before any firmware, wiring or hardware-doc change. Work is tracked in Paca project `HALL` under epic HALL-1; each story names the blueprint section it builds.

## Commands

```bash
npm test                 # repo convention tests (node:test, tests/)
npm run lint             # oxlint
npm run format           # oxfmt --write (JS, JSON, Markdown, TOML)
npm run format:check     # oxfmt --check
npm run typecheck        # tsc (JSDoc checkJs) + mypy on devops/ (venv/ need not be active)
npm run deploy           # copy src/ to the connected Pico (mpremote)
npm run simulate         # run src/ in a running Wokwi simulation (wokwi/) in test mode
mpremote repl            # REPL on the Pico; Ctrl-C stops main.py
npm run test:py          # pytest: firmware scheduler, DFPlayer frames, wiring harness (source activate.sh first)
npm run wiring           # render docs/reference/assets/wiring.yml to wiring.svg (needs Graphviz)
npm run lint:py          # ruff on devops/
```

**After every change**, run `npm test`, `npm run lint`, `npm run format:check` and `npm run typecheck` before calling the work done. Run `npm run test:py` too.

## Architecture

- **Three places code runs:** `src/` is MicroPython on the Pico; `devops/` and `tests/` run on the host; audio lives on the DFPlayer's MicroSD card, never on the Pico.
- **Firmware:** `main.py` holds the configuration constants, rigs, thunder channel and asyncio scheduler, `lights.py` the lightning patterns as coroutines, `mp3_player.py` the DFPlayer frame writer, `clock.py` the real clock. Module roles and constants are in `docs/reference/project-structure.md`.
- **Hardware boundary:** strips, UART, clock and random source are created once in `main.start()` and passed in, so the scheduler runs under host pytest with fakes. Keep hardware imports (`machine`, `neopixel`) inside `start()` and the REPL helpers only. Patterns must `await` the clock, never `time.sleep()`, or every rig stalls.
- **DFPlayer frames:** frame format, start-up and inter-command delays, and the known-good test frames are in `docs/reference/dfplayer-protocol.md`; check any protocol or timing change against it.
- **Timing:** a full 300-pixel write blocks for about 9 ms. NeoPixel and UART timing gotchas are in `docs/reference/known-issues.md`; read it before touching either.
- **Electrical safety:** common ground, separate amplifier supply and the 12 mA GPIO limit are in `docs/reference/hardware.md`; keep any wiring or power change within them. The 2026 build fits no fuses; each supply's own short-circuit protection is the only guard.
- **Wiring:** `docs/reference/assets/wiring.yml` (WireViz) is the source of truth; change it, run `npm run wiring` and commit the SVG with it, or `npm run test:py` fails.
- **Deployment:** from 2026 there is one board. `npm run deploy` copies all of `src/` to the Pico root.

## Code style

- **MicroPython (`src/`):** camelCase functions and variables, UPPER_CASE constants, no type hints. Memory is tight: prefer buffers and small structures, and add no external libraries.
- **Comments:** explain the why for every GPIO assignment, timing-critical section, protocol detail and workaround, citing the datasheet or spec where one applies.
- **Host Python (`devops/`):** PEP 8 with type hints; ruff, black and mypy configured in `pyproject.toml`.
- **JavaScript (`tests/`):** ESM, `node:test`, formatted by oxfmt (`.oxfmtrc.json`).
- **Spelling:** British/Canadian everywhere: colour, initialise, synchronised, licence.

## Documentation

- `docs/` follows Diátaxis (`tutorials/`, `how-to/`, `reference/`, `explanation/`), each folder indexed by its `README.md`; `docs/README.md` is the entry point. Add a new document to its folder's index.
- Record architectural decisions as ADRs in `docs/reference/adr/`, one `NNNN-slug.md` file each, continuing the numbering; `docs/reference/adr/README.md` indexes them and says how to supersede one.
- Number sections and regenerate tables of contents with the `markdown` skill's scripts. `tests/repo.test.js` fails on a broken internal link or anchor.

## Version control

- The repo is colocated jj; use jj for commits, bookmarks and pushes.
- Work each story on its own bookmark off `main`, named `<key>-<slug>` in lowercase (e.g. `hall-2-repo-cleanup`), and merge by pull request.
- Commit subjects and PR titles are a plain description of the change followed by the Paca ID, e.g. `Repo cleanup and alignment with Dev0/Agents0 (Re: #HALL-2)`.
- At season end, tag `main` with the year and add the season to the README's Previous Years table.
