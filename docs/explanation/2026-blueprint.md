# 2026 Blueprint: Two Rigs, One Pico <!-- omit in toc -->

Technical blueprint for the 2026 Halloween lightning and thunder display. It feeds the 2026 epic and its child stories in Paca (project `HALL`).

## Table of Contents <!-- omit in toc -->

- [1. Problem Statement](#1-problem-statement)
- [2. Solution](#2-solution)
- [3. User Stories](#3-user-stories)
- [4. Implementation Decisions](#4-implementation-decisions)
  - [4.1. Hardware](#41-hardware)
  - [4.2. Software](#42-software)
  - [4.3. Documentation and diagrams](#43-documentation-and-diagrams)
- [5. Testing Decisions](#5-testing-decisions)
- [6. Out of Scope](#6-out-of-scope)
- [7. Further Notes](#7-further-notes)

## 1. Problem Statement

The 2025 display used three complete boards: three Pico 2s, three MP3 players, three amplifiers, three speakers and nine power supplies. Each board had to be flashed, wired, powered and debugged separately. For 2026 the display shrinks to two rigs that reuse last year's 300-pixel strips. Duplicating a whole controller, MP3 player, amplifier and speaker for each rig is more hardware, more wiring and more deployment effort than two rigs need.

## 2. Solution

One Raspberry Pi Pico 2 controls both rigs. Each rig strikes on its own random 60–120 second timer, so the two never fall into a pattern. One DFPlayer Mini, one 60 W amplifier and one speaker provide the thunder for both. A single speaker cannot tell a listener which rig struck, so a second audio path would add nothing audible. The controller, MP3 player, amplifier and speaker sit in the middle, with each strip's first pixel no more than 2.7 m away.

When strikes overlap, both rigs animate at the same time. The thunder for the later strike replaces the one already playing, which sounds like a new roll of thunder.

```text
                 ┌──────── Pico 2 + DFPlayer + amp + speaker (centre) ────────┐
  Rig A strip ◄── ≤2.7 m data ─────────┤                                     ├───────── ≤2.7 m data ──► Rig B strip
                                       └── UART TX ──► DFPlayer ── DAC out ──► 60 W amp ──► speaker
```

## 3. User Stories

1. As the display owner, I want both rigs driven by one Pico 2, so that I flash, power and debug one controller instead of two.
2. As the display owner, I want to reuse the 2025 300-pixel strips unchanged, so that I buy no new LED hardware.
3. As the display owner, I want each rig to strike on its own random 60–120 second timer, so that the storm feels unpredictable rather than mechanical.
4. As the display owner, I want both rigs to animate at the same time when their strikes overlap, so that neither rig visibly stalls while the other strikes.
5. As the display owner, I want one MP3 player, one amplifier and one speaker shared by both rigs, so that the audio hardware and wiring are halved.
6. As the display owner, I want a strike to play a random thunder track, so that repeated strikes do not sound identical.
7. As the display owner, I want a strike during playing thunder to replace that thunder with a new track, so that every strike has audible thunder and nothing queues up.
8. As the display owner, I want the controller placed centrally with each data run no longer than 2.7 m, so that the LED data stays reliable without extra buffer hardware.
9. As the display owner, I want both data lines to go through a single level shifter, so that I wire and power one chip.
10. As the display owner, I want a series resistor at each strip's data input and a ground wire run with each data line, so that long data runs do not corrupt pixels.
11. As the display owner, I want the amplifier fed from the DFPlayer's line-level DAC outputs, so that the 60 W amp gets a clean signal instead of the DFPlayer's built-in 3 W speaker output.
12. As the display owner, I want each strip powered by two 5 V supplies (at pixel 1 and pixel 151) as in 2025, so that the far end of each strip does not suffer voltage drop.
13. As the display owner, I want every supply on a common ground, so that logic signals are clean.
14. As the display owner, I want the system to start autonomously on power-up, so that I plug it in and walk away on Halloween night.
15. As the display owner, I want an optional manual trigger that fires a strike on a random rig, so that I can show the effect on demand while setting up. (Firmware only: the button is not fitted in 2026.)
16. As the display owner, I want the onboard LED to indicate the controller is running, so that I can tell at a glance whether the Pico is alive.
17. As the display owner, I want the number of rigs to be configuration rather than code, so that a third rig or a single rig needs no rewrite.
18. As the display owner, I want each rig's data pin, pixel count and interval range set in configuration, so that I can tune one rig without affecting the other.
19. As the display owner, I want the existing lightning patterns (classic, flickering, rolling, and the rare red strike) available on both rigs, so that 2026 keeps everything that worked in 2025.
20. As the display owner, I want a rendered wiring diagram of the whole installation, so that I can assemble and repair it from one picture.
21. As the display owner, I want the wiring diagram kept as text in the repo, so that changes to the wiring are reviewed and versioned like code.
22. As a developer, I want to run the two-rig firmware in a simulator with both strips visible, so that I can see overlapping strikes without building the hardware.
23. As a developer, I want the simulator project kept as text in the repo, so that the simulated circuit tracks the real one.
24. As a developer, I want the scheduling logic tested on my host machine with fake strips, a fake MP3 player and a controllable clock, so that I can verify timing and overlap behaviour in seconds rather than waiting minutes on hardware.
25. As a developer, I want the DFPlayer command bytes verified by a test, so that a change to the protocol code cannot silently break audio.
26. As a developer, I want hardware objects created only at start-up and passed in, so that the same logic runs on the Pico and in tests.
27. As a developer, I want a reduced-interval test mode, so that I can watch several strikes in a minute during bench testing.
28. As a developer, I want `npm run deploy` to keep working for one board, so that deployment stays one command.
29. As an AI agent, I want CLAUDE.md and the docs updated for the two-rig design, so that I don't work from the three-board 2025 assumptions.
30. As an AI agent, I want each 2026 architectural choice recorded as an ADR, so that I understand why the design changed.
31. As a trick-or-treater, I want lightning and thunder to arrive together, so that the effect is convincing.
32. As a neighbour, I want the thunder to stay at a sensible volume, so that the display is dramatic without being a nuisance.

## 4. Implementation Decisions

### 4.1. Hardware

- **Controller:** one Raspberry Pi Pico 2 (RP2350) running MicroPython, as in 2025.
- **Pins:**
  - Rig A data on GP16.
  - Rig B data on GP17, the adjacent pin, which is also usable by PIO.
  - DFPlayer command on UART1 TX (GP4). UART1 RX (GP5) is reserved for later use but not required, because commands are sent without feedback.
  - GP15 is unwired: the manual trigger button is not fitted in 2026, and `USE_MANUAL_TRIGGER` stays `False`. A button added later goes on GP15 with an external 4.7 kΩ pull-down, because RP2350 erratum E9 can latch the pad at about 2 V, which the internal pull-down cannot clear.
  - The onboard LED (GP25) shows status.
  - Power enters at VSYS through a Schottky diode (1N5817), never VBUS, so a laptop can be plugged into USB while the display is powered without either feeding the other.
- **Level shifting:** the 4-channel BSS138 MOSFET level shifter board reused from 2025, using two channels for the data lines: LV from the Pico's 3V3, HV from the 5 V bus. Its 10 kΩ high-side pull-ups rise too slowly for 2.7 m, so each used channel adds a 1.5 kΩ pull-up from HVn to HV. Each strip has a 330 Ω series resistor at its data input. The first version of this blueprint named a 74AHCT125 in error; the 2025 boards used this board ([ADR-013](../reference/adr/0013-reused-bss138-level-shifter.md)).
- **Data runs:**
  - No more than 2.7 m from the level shifter to pixel 1 of each strip. That is a commonly cited ~3 m unbuffered limit less 10%.
  - Each data wire runs with a ground wire, twisted if practical.
  - Strip starts can be up to about 5.4 m apart.
- **Audio:**
  - One DFPlayer Mini, one 60 W BTL amplifier, one speaker.
  - The amplifier input comes from DAC_L/DAC_R, not SPK_1/SPK_2. This corrects the 2025 wiring guidance.
  - The amplifier (TPA3118, mono) has a 2-position IN+/IN− input, so DAC_L and DAC_R are summed through two 10 kΩ resistors into IN+, with IN− to ground. Wiring DAC_L to IN+ and DAC_R to IN− would cancel the thunder. Confirm the terminals against the board's silkscreen on the bench.
- **Power:**
  - Two 5 V 8 A supplies per strip, injected at pixel 1 and pixel 151, so four in total. They power pixels only.
  - The +5V connection between pixels 150 and 151 is cut, so each supply feeds only its half instead of fighting the other through the strip. GND and data stay continuous.
  - One dedicated 5 V 3 A logic supply for the Pico, DFPlayer and level shifter, so a full-white flash cannot sag the controller and no 5 V power runs the 2.7 m back from a strip.
  - One 12 V 5 A supply for the amplifier.
  - All grounds are common, meeting at a star-ground terminal block in the enclosure; each rig's grounds reach it through its data pair. No fuses are fitted: each supply's own short-circuit protection is the only guard, so polarity is checked before power-on and supplies are powered one at a time.
  - Decoupling capacitors as in 2025, plus 100 nF across the level shifter's HV and GND.
- **Placement:** controller, level shifter, DFPlayer and amplifier in one central enclosure, with the logic and amplifier supplies beside it. Each pixel supply sits at its injection point. Only the speaker cable and the two data/ground pairs run out to the rigs.

### 4.2. Software

- **Concurrency:**
  - `asyncio` replaces the 2025 blocking loop.
  - Each rig runs as an independent task: wait a random interval, strike, repeat. The interval runs from the end of one strike to the start of the next; the 2025 thunder wait and cooldown are dropped, because thunder plays on independently.
  - The clock (`now`, `since`, `sleep`) is passed in like the hardware: `clock.py` on the Pico, a virtual clock in tests.
  - Lightning patterns become coroutines that yield between frames, so overlapping strikes on both rigs interleave frame by frame.
  - A full 300-pixel write takes about 9 ms and blocks. Two rigs interleaved still give roughly 55 frames per second, which is enough for lightning. The second core is not used.
- **Rig:** a rig owns one strip, its pixel count and its interval range. The rigs are a list in configuration, so one, two or more need no code change.
- **Thunder:**
  - One shared thunder channel wraps the single DFPlayer.
  - Every strike asks it to play a random track. If a track is already playing, the new request replaces it ("latest strike wins"); nothing queues.
  - Commands go out with the existing minimum spacing between DFPlayer commands (100 ms). The channel keeps it with an `await`, not a sleep: a strike inside the gap waits out the remainder, and a newer strike during that wait replaces the waiting track.
  - The MP3 player no longer sleeps between commands, so it cannot stall the strips; its blocking wake-up sequence runs once at start-up.
- **Patterns:**
  - The 2025 patterns are reused: classic, flickering and rolling, chosen at random, with a 10% chance of a red strike. (The 2025 code actually used 20%; 2026 corrects it to the documented 10%.)
  - Their visual behaviour does not change; only how they yield control between frames does.
- **Hardware boundary:**
  - Strips, the UART, the clock and the random source are created once at start-up and passed into the rigs and the thunder channel.
  - Nothing below start-up imports hardware modules, so the same logic runs under host Python with fakes.
- **DFPlayer protocol:** the existing MP3 player module is kept. Its public interface (play track, set volume, stop) does not change; its constructor now takes the UART instead of pins. It prints each frame it sends, which stands in for the DFPlayer in simulation.
- **Start-up:** autonomous start on boot stays on by default. A reduced-interval test mode is a configuration switch, not an edit to the interval constants.
- **Manual trigger:** firmware only in 2026; the button is not fitted. When enabled, a press fires one strike on a randomly chosen idle rig, going through the same strike path as a timer. It fires on the press edge (a 50 ms poll that also debounces), a press while every rig is striking is ignored, and rig timers are not reset. A rig's timer that fires during a manual strike on it waits for that strike to end, then starts a fresh interval.
- **Status LED:** solid during start-up, then a 1 Hz heartbeat from its own task, so a stalled scheduler shows as an LED that stops blinking.
- **Random seed:** from `os.urandom` (hardware entropy), not `time.ticks_ms()`, which repeats across boots.

### 4.3. Documentation and diagrams

- **New ADRs in [Architecture Decision Records](../reference/adr/README.md):**
  - ADR-009, single controller for multiple rigs.
  - ADR-010, single shared audio path with latest-strike-wins.
  - ADR-011, `asyncio` scheduling.
  - ADR-012, WireViz and Wokwi for hardware diagrams and simulation[^diagram-tools].
  - ADR-013, the reused BSS138 level shifter board.
- **Superseded ADR:** ADR-008 (independent multi-board) is marked superseded by ADR-009.
- **WireViz:** the installation wiring is a YAML harness file in the repo ([`wiring.yml`](../reference/assets/wiring.yml)). It covers supplies, Pico, level shifter, DFPlayer, amplifier, speaker and both strips' power injection and data. The rendered SVG is committed next to it, because GitHub does not render WireViz itself.
- **ASCII wiring diagram:** the WireViz SVG is about 5:1 and needs a pan-and-zoom viewer, so [Wiring Diagram](../reference/wiring-diagram.md) draws the same parts and pins as ASCII boxes and wires (HALL-7). It is kept in step with `wiring.yml` by hand; `wiring.yml` wins.
- **Wokwi:**
  - A Wokwi project (`wokwi/diagram.json`, `wokwi/wokwi.toml`) holds a Pico (RP2040, because Wokwi's RP2350 corrupts MicroPython; see ADR-012) with two WS2812 strips on the real pins (60 pixels each, because two 300-pixel strips simulate at about 4% of real time), running the real firmware on the stock MicroPython image. `npm run simulate` mounts `src/` from the host over RFC 2217 and starts the storm in test mode.
  - Wokwi has no DFPlayer part, so the DFPlayer UART is watched on the serial monitor in its place.
- **Mermaid** stays for system context, runtime flow and state diagrams.
- **Updates:** README, CLAUDE.md and the hardware, how-to and reference docs are updated from three boards to two rigs on one controller. The "Previous Years" table gains a 2026 row at season end.

## 5. Testing Decisions

- **What a good test is:** it drives the system through its public behaviour (a rig strikes, thunder plays) and checks what can be observed: frames written to a strip and bytes written to the UART. It does not check private helpers, frame counts within a pattern, or exact pixel values beyond on/off/colour family.
- **Seam 1, the main one (scheduler with fake hardware under host Python):**
  - Build the rigs and thunder channel with fake strips that record writes, a fake UART that records bytes, a controllable clock and a seeded random source.
  - Assert:
    - Each rig strikes within its configured interval.
    - Two rigs whose strikes overlap both keep writing frames during the overlap.
    - Every strike sends exactly one play-track command for a track within the configured track count.
    - A strike while thunder is playing sends a new play command and nothing queues.
    - The number of rigs follows configuration.
  - Runs with pytest (`npm run test:py` already exists).
- **Seam 2 (DFPlayer frames):** through the MP3 player's public interface with a fake UART. Assert the exact 10-byte frames, including checksum, for play track, set volume and stop. The [known-good frames](../reference/dfplayer-protocol.md#4-known-good-frames) are the reference values. (The 2025 agent docs gave "play track 1" a wrong checksum, `FE F9`; the correct value is `FE F7`.)
- **Seam 3 (Wokwi simulation):** a manual visual check that both strips animate, overlaps interleave and UART traffic appears at each strike. This is not run in CI unless the Wokwi CLI is adopted later.
- **Seam 4 (bench):** a hardware checklist in the how-to guides covering each data run at full length, thunder through the amplifier, overlap behaviour, and power under a full-white flash.
- **Prior art:** none before 2026. `devops/test_mp3_serial.py` is a manual serial tester and the closest reference for DFPlayer frames. Seams 1 and 2 are now `tests/test_storm.py` and `tests/test_mp3_player.py`.
- **Proposed seams to confirm:** seam 1 is the only new one. It needs the hardware-at-start-up boundary described above and is the highest point at which timing and overlap can be tested without hardware.

## 6. Out of Scope

- A third rig, or any rig count other than two, deployed this season. The code supports it; the installation does not.
- Coordinated strikes, such as a strike rolling from rig A to rig B or thunder delayed by distance.
- A second DFPlayer, mixing two audio paths, or stereo or spatial audio.
- Data runs beyond 2.7 m, RS-485 or other differential LED data links.
- Wireless control, networking or remote configuration.
- New lightning patterns or new thunder recordings.
- PCB design, enclosures beyond a central box, and weatherproofing work.
- Using the Pico's second core.
- Automated Wokwi runs in CI.

## 7. Further Notes

- **Number of supplies:** six (one 5 V logic, four 5 V pixel, one 12 V amplifier), down from nine in 2025.
- **Rig spacing:** 2.7 m is the planning limit for the distance from the level shifter to pixel 1. Measure the actual layout before cutting cables. If a run must be longer, stop and revisit; a buffer or differential link is out of scope.
- **Overlap frequency:** two independent 60–120 s timers with strikes under one second collide only occasionally, so latest-strike-wins thunder should rarely be noticeable.
- **Volume:** 2025's volume of 25/30 assumed one speaker per board. With one speaker for the whole display it may need retuning on site.
- **Dependencies:** WireViz is a pip package that needs Graphviz installed on the host. Wokwi is a VS Code extension or web app; its CLI needs a licence token. Neither runs on the Pico.

[^diagram-tools]: WireViz and Wokwi have been added because they fulfil diagramming needs beyond Mermaid that this project requires. It is not just software but also hardware: WireViz documents physical wiring harnesses between modules, and Wokwi provides a breadboard-level view and simulation of the Pico and LED strips.

[← Back to Explanation](./README.md)
