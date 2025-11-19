"""
NeoPixel Lightning Effect Module

This module provides lightning flash animations for WS2812B NeoPixel LEDs.
Uses batched updates for memory efficiency and timing optimisation.

Hardware Requirements:
- WS2812B NeoPixel strip (tested with 300 LEDs)
- 3.3V→5V logic level shifter on data line
- Adequate 5V power supply (see power calculations in Developer Guide)

Timing Considerations:
- WS2812B protocol is timing-sensitive
- Batch updates to minimise blocking time
- Keep animation functions fast to avoid glitches
"""

import time
import random

# Lightning pattern constants
PATTERN_CLASSIC = 0      # Single bold strike
PATTERN_FLICKERING = 1   # Multiple rapid flashes
PATTERN_ROLLING = 2      # Gradual build-up with tail-off

# Lightning colour constants
LIGHTNING_BLUE = (240, 248, 255)  # Alice blue - natural lightning (90%)
LIGHTNING_RED = (255, 0, 0)        # Blood red - supernatural effect (10%)

# Legacy constants (for backward compatibility)
LIGHTNING_COLOUR = LIGHTNING_BLUE  # Alias for existing code
LIGHTNING_COLOUR_TEST = (120, 124, 128)  # 50% brightness for testing

# Dark/off state
OFF_COLOUR = (0, 0, 0)


def selectLightningPattern():
    """
    Randomly select a lightning pattern with equal probability.
    
    Returns:
        int: Pattern constant (PATTERN_CLASSIC, PATTERN_FLICKERING, or PATTERN_ROLLING)
    
    Distribution: 33.3% chance for each pattern
    """
    return random.randint(0, 2)


def selectLightningColour():
    """
    Randomly select lightning colour with weighted probability.
    
    Returns:
        tuple: RGB colour (r, g, b)
    
    Distribution:
        - 90% chance: Alice blue (natural lightning)
        - 10% chance: Blood red (supernatural effect)
    """
    roll = random.randint(1, 10)

    if roll <= 8:  # 1-8 = 80%
        return LIGHTNING_BLUE
    else:          # 9-10 = 20%
        return LIGHTNING_RED


def lightningFlashClassic(np, colour, duration_ms=500, batch_size=40):
    """
    Pattern 1: Classic single bold strike.
    
    Creates a bright flash effect by illuminating all pixels,
    then fading/flickering before turning off. Uses batched updates to
    minimise timing issues and memory overhead.
    
    Args:
        np: neopixel.NeoPixel object (pre-initialised)
        colour: RGB tuple (r, g, b) for lightning colour
        duration_ms: Total flash duration in milliseconds (default 500ms)
        batch_size: Number of pixels to update per write cycle (default 40)
    
    Algorithm:
        1. Rapid flash to full brightness (batched)
        2. Brief hold at peak brightness
        3. Quick flicker (on-off-on pattern)
        4. Fade to off
    
    Memory: ~150 bytes for function stack, no allocations in loop
    Timing: ~500ms total (adjustable via duration_ms)
    """
    pixel_count = len(np)
    
    # Phase 1: Rapid flash to full brightness (batched for efficiency)
    # Lightning travels from sky (highest pixel) down to ground (pixel 0)
    for i in range(pixel_count - 1, -1, -batch_size):
        # Fill batch from current position down to lower bound
        start = max(0, i - batch_size + 1)
        for j in range(start, i + 1):
            np[j] = colour
        np.write()
        time.sleep_ms(1)
    
    # Phase 2: Hold at peak brightness
    time.sleep_ms(int(duration_ms * 0.3))  # 30% of duration
    
    # Phase 3: Flicker effect (on-off-on pattern)
    _clearAllPixels(np, batch_size)
    time.sleep_ms(20)
    
    _setAllPixels(np, colour, batch_size)
    time.sleep_ms(30)
    
    _clearAllPixels(np, batch_size)
    time.sleep_ms(15)
    
    _setAllPixels(np, colour, batch_size)
    time.sleep_ms(int(duration_ms * 0.2))  # 20% of duration
    
    # Phase 4: Fade to off
    _clearAllPixels(np, batch_size)


def lightningFlashFlickering(np, colour, duration_ms=500, batch_size=40):
    """
    Pattern 2: Multiple rapid flashes with varying intensity.
    
    Simulates branching lightning with multiple quick strikes.
    Creates a "chain lightning" effect with random brightness variations.
    
    Args:
        np: neopixel.NeoPixel object (pre-initialised)
        colour: RGB tuple (r, g, b) for lightning colour
        duration_ms: Base duration (pattern overrides to ~400-600ms)
        batch_size: Number of pixels to update per write cycle
    
    Algorithm:
        - 3-5 rapid flashes (randomized)
        - Each flash: 70%, 85%, or 100% brightness
        - Very short hold (30-80ms per flash)
        - Random gaps between flashes (10-50ms)
    
    Memory: Minimal, uses existing helpers
    Timing: ~400-600ms total
    """
    # Determine number of flashes (3-5)
    num_flashes = random.randint(3, 5)
    
    for flash in range(num_flashes):
        # Random brightness: 70%, 85%, or 100%
        brightness_choice = random.randint(0, 2)
        if brightness_choice == 0:
            brightness = 0.7
        elif brightness_choice == 1:
            brightness = 0.85
        else:
            brightness = 1.0
        
        # Scale colour by brightness
        scaled_colour = tuple(int(c * brightness) for c in colour)
        
        # Flash on
        _setAllPixels(np, scaled_colour, batch_size)
        
        # Hold for random duration (30-80ms)
        hold_time = random.randint(30, 80)
        time.sleep_ms(hold_time)
        
        # Flash off
        _clearAllPixels(np, batch_size)
        
        # Gap before next flash (10-50ms), except after last flash
        if flash < num_flashes - 1:
            gap_time = random.randint(10, 50)
            time.sleep_ms(gap_time)


def lightningFlashRolling(np, colour, duration_ms=800, batch_size=40):
    """
    Pattern 3: Gradual build-up with tail-off and optional re-brightening.
    
    Simulates sheet lightning or distant storm illumination.
    Creates a slower, more dramatic effect.
    
    Args:
        np: neopixel.NeoPixel object (pre-initialised)
        colour: RGB tuple (r, g, b) for lightning colour
        duration_ms: Total duration (default 800ms, longer than other patterns)
        batch_size: Number of pixels to update per write cycle
    
    Algorithm:
        - Gradual fade-up (5 steps: 20%, 40%, 60%, 80%, 100%)
        - Quick peak hold (100ms)
        - Gradual fade-down (5 steps)
        - 20% chance of re-brightening (50% brightness, 100ms)
        - Final fade to off
    
    Memory: Minimal, uses existing helpers
    Timing: ~800-1000ms total
    """
    # Phase 1: Fade up (5 steps)
    fade_steps = [0.2, 0.4, 0.6, 0.8, 1.0]
    for brightness in fade_steps:
        scaled_colour = tuple(int(c * brightness) for c in colour)
        _setAllPixels(np, scaled_colour, batch_size)
        time.sleep_ms(40)  # 40ms per step = 200ms total
    
    # Phase 2: Peak hold
    time.sleep_ms(100)
    
    # Phase 3: Fade down (5 steps, reversed)
    fade_steps.reverse()
    for brightness in fade_steps[1:]:  # Skip 1.0 (already at peak)
        scaled_colour = tuple(int(c * brightness) for c in colour)
        _setAllPixels(np, scaled_colour, batch_size)
        time.sleep_ms(60)  # 60ms per step = 240ms total
    
    # Phase 4: Random re-brightening (20% chance)
    if random.randint(1, 5) == 1:  # 1 in 5 = 20%
        time.sleep_ms(50)  # Brief pause
        
        # Re-brighten to 50%
        scaled_colour = tuple(int(c * 0.5) for c in colour)
        _setAllPixels(np, scaled_colour, batch_size)
        time.sleep_ms(100)
    
    # Phase 5: Final fade to off
    _clearAllPixels(np, batch_size)


def executeRandomLightning(np, duration_ms=500, batch_size=40):
    """
    Execute a random lightning flash with random pattern and colour.
    
    Main entry point for randomized lightning effects. Automatically selects
    pattern (equal distribution) and colour (90% blue, 10% red).
    
    Args:
        np: neopixel.NeoPixel object (pre-initialised)
        duration_ms: Base duration hint (patterns may override)
        batch_size: Number of pixels to update per write cycle
    
    Pattern Distribution:
        - 33.3% Classic (single bold strike)
        - 33.3% Flickering (multiple rapid flashes)
        - 33.3% Rolling (gradual build-up)
    
    Colour Distribution:
        - 90% Alice blue (natural lightning)
        - 10% Blood red (supernatural effect)
    
    Usage:
        >>> from lights import executeRandomLightning
        >>> import machine, neopixel
        >>> pin = machine.Pin(16, machine.Pin.OUT)
        >>> np = neopixel.NeoPixel(pin, 300)
        >>> executeRandomLightning(np)
    """
    # Select pattern and colour
    pattern = selectLightningPattern()
    colour = selectLightningColour()
    
    # Execute appropriate pattern
    if pattern == PATTERN_CLASSIC:
        lightningFlashClassic(np, colour, duration_ms, batch_size)
    elif pattern == PATTERN_FLICKERING:
        lightningFlashFlickering(np, colour, duration_ms, batch_size)
    else:  # PATTERN_ROLLING
        lightningFlashRolling(np, colour, duration_ms, batch_size)


def clearLights(np, batch_size=40):
    """
    Turn off all NeoPixels (set to black).
    
    Uses batched updates for efficiency. Safe to call repeatedly.
    
    Args:
        np: neopixel.NeoPixel object
        batch_size: Pixels per write cycle (default 40)
    
    Memory: Minimal stack usage, no allocations
    Timing: ~30ms for 300 pixels with batch_size=40
    """
    _clearAllPixels(np, batch_size)


def _setAllPixels(np, colour, batch_size=40):
    """
    Internal helper: Set all pixels to specified colour using batched writes.
    
    Lightning travels from sky (highest pixel) down to ground (pixel 0).
    Batches start at the top and work downward.
    
    Args:
        np: neopixel.NeoPixel object
        colour: RGB tuple (r, g, b) where each value is 0-255
        batch_size: Pixels per write cycle
    
    Note: Leading underscore indicates internal use only
    """
    pixel_count = len(np)
    # Start from highest pixel and work down to 0
    for i in range(pixel_count - 1, -1, -batch_size):
        # Fill batch from current position down to lower bound
        start = max(0, i - batch_size + 1)
        for j in range(start, i + 1):
            np[j] = colour
        np.write()
        time.sleep_ms(1)  # Prevent timing issues


def _clearAllPixels(np, batch_size=40):
    """
    Internal helper: Clear all pixels (set to off/black) using batched writes.
    
    Args:
        np: neopixel.NeoPixel object
        batch_size: Pixels per write cycle
    
    Note: Leading underscore indicates internal use only
    """
    _setAllPixels(np, OFF_COLOUR, batch_size)


def testColors(pin_number, pixel_count=300):
    """
    Test individual color channels to diagnose color balance issues.
    
    Displays pure red, green, blue, and white in sequence to check
    for color consistency across the strip.
    
    Args:
        pin_number: GPIO pin number connected to NeoPixel data
        pixel_count: Number of NeoPixels in strip (default 300)
    
    Usage:
        >>> from lights import testColors
        >>> testColors(16, 300)
    """
    import machine
    import neopixel
    
    print(f"🎨 Color Test - GPIO {pin_number}, {pixel_count} pixels")
    
    pin = machine.Pin(pin_number, machine.Pin.OUT)
    np = neopixel.NeoPixel(pin, pixel_count)
    
    # Test RED
    print("Testing RED...")
    for i in range(pixel_count):
        np[i] = (255, 0, 0)
    np.write()
    time.sleep(2)
    
    # Test GREEN
    print("Testing GREEN...")
    for i in range(pixel_count):
        np[i] = (0, 255, 0)
    np.write()
    time.sleep(2)
    
    # Test BLUE
    print("Testing BLUE...")
    for i in range(pixel_count):
        np[i] = (0, 0, 255)
    np.write()
    time.sleep(2)
    
    # Test WHITE
    print("Testing WHITE (alice blue)...")
    for i in range(pixel_count):
        np[i] = (240, 248, 255)
    np.write()
    time.sleep(2)
    
    # Clear
    print("Clearing...")
    for i in range(pixel_count):
        np[i] = (0, 0, 0)
    np.write()
    
    print("✅ Color test complete")


def testLightning(pin_number, pixel_count=300):
    """
    Test function for random lightning animation.
    
    Executes a random lightning pattern with random colour.
    Can be called from REPL for testing without full system.
    
    Usage:
        >>> from lights import testLightning
        >>> testLightning(16, 300)  # Test on GPIO 16 with 300 pixels
    
    Args:
        pin_number: GPIO pin number connected to NeoPixel data
        pixel_count: Number of NeoPixels in strip (default 300)
    
    Hardware Requirements:
        - NeoPixel strip connected via level shifter to specified GPIO
        - Adequate 5V power supply for NeoPixels
        - Common ground between Pico and NeoPixel power supply
    """
    import machine
    import neopixel
    
    print(f"🎃 Lightning Test - GPIO {pin_number}, {pixel_count} pixels")
    print("Initialising NeoPixels...")
    
    # Initialise NeoPixel strip
    pin = machine.Pin(pin_number, machine.Pin.OUT)
    np = neopixel.NeoPixel(pin, pixel_count)
    
    print("✅ NeoPixels initialised")
    print("Executing random lightning flash...")
    
    # Execute random flash
    executeRandomLightning(np, duration_ms=500, batch_size=40)
    
    print("⚡ Flash complete")
    print("Clearing lights...")
    
    clearLights(np)
    
    print("✅ Test complete - lights cleared")


def testAllPatterns(pin_number, pixel_count=300):
    """
    Test all three lightning patterns in sequence.
    
    Displays each pattern twice (once blue, once red) for comparison.
    Useful for verifying all patterns work correctly and comparing effects.
    
    Usage:
        >>> from lights import testAllPatterns
        >>> testAllPatterns(16, 300)
    
    Args:
        pin_number: GPIO pin number connected to NeoPixel data
        pixel_count: Number of NeoPixels in strip (default 300)
    
    Test Sequence:
        1. Classic - Blue
        2. Classic - Red
        3. Flickering - Blue
        4. Flickering - Red
        5. Rolling - Blue
        6. Rolling - Red
    """
    import machine
    import neopixel
    
    print(f"🎨 Pattern Test - GPIO {pin_number}, {pixel_count} pixels")
    print("Testing all patterns with both colours...")
    
    pin = machine.Pin(pin_number, machine.Pin.OUT)
    np = neopixel.NeoPixel(pin, pixel_count)
    
    # Test Pattern 1: Classic
    print("\n1️⃣  Pattern: CLASSIC (Blue)")
    lightningFlashClassic(np, LIGHTNING_BLUE, 500, 40)
    time.sleep(2)
    
    print("1️⃣  Pattern: CLASSIC (Red)")
    lightningFlashClassic(np, LIGHTNING_RED, 500, 40)
    time.sleep(2)
    
    # Test Pattern 2: Flickering
    print("\n2️⃣  Pattern: FLICKERING (Blue)")
    lightningFlashFlickering(np, LIGHTNING_BLUE, 500, 40)
    time.sleep(2)
    
    print("2️⃣  Pattern: FLICKERING (Red)")
    lightningFlashFlickering(np, LIGHTNING_RED, 500, 40)
    time.sleep(2)
    
    # Test Pattern 3: Rolling
    print("\n3️⃣  Pattern: ROLLING (Blue)")
    lightningFlashRolling(np, LIGHTNING_BLUE, 800, 40)
    time.sleep(2)
    
    print("3️⃣  Pattern: ROLLING (Red)")
    lightningFlashRolling(np, LIGHTNING_RED, 800, 40)
    time.sleep(2)
    
    # Clear
    clearLights(np)
    print("\n✅ All patterns tested - lights cleared")


# Module-level test when run directly
if __name__ == "__main__":
    print("lights.py - NeoPixel Lightning Effect Module")
    print("Import this module and call executeRandomLightning() or testLightning()")
    print("Example: testLightning(16, 300)")
    print("Example: testAllPatterns(16, 300)")

