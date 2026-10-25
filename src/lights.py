"""
NeoPixel Lightning Effect Module

Lightning flash animations for WS2812B NeoPixel strips, written as coroutines so several rigs
can strike at once: every pattern awaits the clock between frames, which lets the asyncio
scheduler interleave the frames of overlapping strikes on different strips.

Hardware Requirements:
- WS2812B NeoPixel strip (tested with 300 LEDs)
- 3.3V->5V logic level shifter on data line
- Adequate 5V power supply (see power calculations in docs/reference/hardware.md)

Timing Considerations:
- WS2812B protocol is timing-sensitive, and a full 300-pixel write blocks for about 9 ms
  (docs/reference/known-issues.md). Each write() is one frame; patterns yield after it.
- The strip, clock and random source are passed in, so the patterns run under host Python with
  fakes. Only the REPL test helpers at the bottom import machine/neopixel, and only when called.
"""

import time

# Pixels filled between strip writes. Each write is one frame, so the batch size sets the speed
# of the sky-to-ground sweep that every pattern shares (2025's LED_BATCH_SIZE)
BATCH_SIZE = 40

# Lightning colour constants
LIGHTNING_BLUE = (240, 248, 255)  # Alice blue - natural lightning (90%)
LIGHTNING_RED = (255, 0, 0)        # Blood red - supernatural effect (10%)

# Dark/off state
OFF_COLOUR = (0, 0, 0)


def selectLightningColour(rng):
    """
    Pick the strike colour: 90% Alice blue (natural), 10% blood red (supernatural).

    2025 shipped with red on rolls 9-10 (20%) despite documenting 10%; the 2026 blueprint
    settles it at 10%.
    """
    return LIGHTNING_RED if rng.randint(1, 10) == 10 else LIGHTNING_BLUE


async def lightningFlashClassic(strip, colour, clock, rng):
    """
    Pattern 1: Classic single bold strike.

    1. Sweep to full brightness from sky (highest pixel) down to ground (pixel 0)
    2. Hold at peak for 150ms (30% of the 2025 500ms duration)
    3. Flicker off-on-off-on
    4. Hold for 100ms (20%), then clear

    rng is unused: it keeps the three patterns' signatures the same so one can be picked from
    PATTERNS. Timing: ~500ms total
    """
    await _setAllPixels(strip, colour, clock)
    await clock.sleep(150)

    await _setAllPixels(strip, OFF_COLOUR, clock)
    await clock.sleep(20)
    await _setAllPixels(strip, colour, clock)
    await clock.sleep(30)
    await _setAllPixels(strip, OFF_COLOUR, clock)
    await clock.sleep(15)
    await _setAllPixels(strip, colour, clock)
    await clock.sleep(100)

    await _setAllPixels(strip, OFF_COLOUR, clock)


async def lightningFlashFlickering(strip, colour, clock, rng):
    """
    Pattern 2: Multiple rapid flashes with varying intensity ("chain lightning").

    - 3-5 flashes, each at 70%, 85% or 100% brightness
    - Each held 30-80ms, with 10-50ms gaps between flashes

    Timing: ~400-600ms total
    """
    flashCount = rng.randint(3, 5)
    for flash in range(flashCount):
        brightness = (0.7, 0.85, 1.0)[rng.randint(0, 2)]
        await _setAllPixels(strip, _scale(colour, brightness), clock)
        await clock.sleep(rng.randint(30, 80))
        await _setAllPixels(strip, OFF_COLOUR, clock)
        if flash < flashCount - 1:
            await clock.sleep(rng.randint(10, 50))


async def lightningFlashRolling(strip, colour, clock, rng):
    """
    Pattern 3: Sheet lightning: gradual build-up with tail-off and optional re-brightening.

    - Fade up in 5 steps (20%-100%, 40ms each), hold 100ms
    - Fade down in 4 steps (80%-20%, 60ms each)
    - 20% chance of a 50% re-brightening for 100ms after a 50ms pause
    - Clear

    Timing: ~800-1000ms total
    """
    for brightness in (0.2, 0.4, 0.6, 0.8, 1.0):
        await _setAllPixels(strip, _scale(colour, brightness), clock)
        await clock.sleep(40)

    await clock.sleep(100)

    for brightness in (0.8, 0.6, 0.4, 0.2):  # Already at peak, so start below it
        await _setAllPixels(strip, _scale(colour, brightness), clock)
        await clock.sleep(60)

    if rng.randint(1, 5) == 1:
        await clock.sleep(50)
        await _setAllPixels(strip, _scale(colour, 0.5), clock)
        await clock.sleep(100)

    await _setAllPixels(strip, OFF_COLOUR, clock)


PATTERNS = (lightningFlashClassic, lightningFlashFlickering, lightningFlashRolling)


async def executeRandomLightning(strip, clock, rng):
    """
    Run one strike: a random pattern (one third each) in a random colour (10% red).
    Returns when the strip is dark again.
    """
    pattern = PATTERNS[rng.randint(0, len(PATTERNS) - 1)]
    await pattern(strip, selectLightningColour(rng), clock, rng)


def _scale(colour, brightness):
    return tuple(int(channel * brightness) for channel in colour)


async def _setAllPixels(strip, colour, clock):
    """
    Fill the strip batch by batch from the highest pixel down, writing after each batch.

    Lightning travels from sky (highest pixel) down to ground (pixel 0); the batched writes
    are what give the 2025 patterns their downward sweep. Each write is a frame, and the 1 ms
    sleep after it is where another rig's strike gets its turn.
    """
    for top in range(len(strip) - 1, -1, -BATCH_SIZE):
        for index in range(max(0, top - BATCH_SIZE + 1), top + 1):
            strip[index] = colour
        strip.write()
        await clock.sleep(1)


# ============================================================================
# REPL TEST HELPERS (Pico only: they create their own strip)
# ============================================================================


def _openStrip(pinNumber, pixelCount):
    import machine
    import neopixel

    return neopixel.NeoPixel(machine.Pin(pinNumber, machine.Pin.OUT), pixelCount)


def testColours(pinNumber, pixelCount=300):
    """
    Show pure red, green, blue and Alice blue for 2 s each to check colour balance.

        >>> from lights import testColours
        >>> testColours(16, 300)
    """
    strip = _openStrip(pinNumber, pixelCount)
    for colour in ((255, 0, 0), (0, 255, 0), (0, 0, 255), LIGHTNING_BLUE):
        strip.fill(colour)
        strip.write()
        time.sleep(2)
    strip.fill(OFF_COLOUR)
    strip.write()


def testLightning(pinNumber, pixelCount=300):
    """
    Run one random strike on a strip.

        >>> from lights import testLightning
        >>> testLightning(16, 300)
    """
    import asyncio
    import random
    from clock import PicoClock

    asyncio.run(executeRandomLightning(_openStrip(pinNumber, pixelCount), PicoClock(), random))


def testAllPatterns(pinNumber, pixelCount=300):
    """
    Run each pattern in blue then red, 2 s apart, to compare them.

        >>> from lights import testAllPatterns
        >>> testAllPatterns(17, 300)
    """
    import asyncio
    import random
    from clock import PicoClock

    async def showAll(strip, clock):
        for pattern in PATTERNS:
            for colour in (LIGHTNING_BLUE, LIGHTNING_RED):
                await pattern(strip, colour, clock, random)
                await clock.sleep(2000)

    asyncio.run(showAll(_openStrip(pinNumber, pixelCount), PicoClock()))
