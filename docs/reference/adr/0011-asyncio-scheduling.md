# ADR-011: asyncio Scheduling <!-- omit in toc -->

**Status:** Accepted (2026 season)

**Context:**
The 2025 firmware ran one strip in a blocking loop: `time.sleep()` between strikes and between animation frames. In 2026 one Pico 2 drives two rigs, each on its own random 60–120 s timer ([2026 blueprint](../../explanation/2026-blueprint.md#42-software)). When their strikes overlap, a blocking pattern on one strip would freeze the other for the whole strike. Options:

1. **Blocking loop with a combined schedule:** compute both rigs' next strike times and run one pattern at a time. Overlapping strikes serialise, so the second rig visibly stalls.
2. **Second core (`_thread`):** one rig per core. Caps the design at two rigs, shares the DFPlayer across threads and makes testing harder.
3. **`asyncio`:** one task per rig, with patterns as coroutines that yield between frames.

**Decision:**
Use `asyncio`, one task per rig. Lightning patterns are coroutines that await the clock after every strip write, so overlapping strikes interleave frame by frame. A shared thunder channel keeps the DFPlayer's 100 ms command spacing with an `await` instead of a sleep, and the latest strike wins. The strips, UART, clock and random source are created once in `main.start()` and passed in.

**Rationale:**

- **No stalls:** a full 300-pixel write blocks for about 9 ms; two rigs interleaved still get roughly 55 frames per second, which is enough for lightning
- **Any number of rigs:** rigs are a configuration list, and each is just another task
- **Testable on the host:** with the clock and hardware passed in, the same scheduler runs under pytest with a virtual clock, fake strips and a fake UART, so minutes of storm run in milliseconds
- **Built in:** `asyncio` ships with MicroPython; no external library

**Consequences:**

- Every pattern step must `await` the clock; a stray `time.sleep()` would stall every rig
- `MP3Player` no longer sleeps between commands; whoever sends frames keeps the spacing (the thunder channel during the show, `startPlayer()` at start-up)
- The interval is measured from the end of a strike to the next one; the 2025 four-second thunder wait and five-second cooldown are gone, because thunder plays on independently
- The second core stays unused

[← Back to ADR index](./README.md)
