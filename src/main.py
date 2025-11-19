"""
Halloween Lightning & Thunder Effect - Main Application

Autonomous lightning and thunder effect system using:
- Raspberry Pi Pico 2 (RP2350)
- 300 WS2812B NeoPixels for lightning animation
- DFPlayer Mini MP3 module for thunder sounds
- Random interval triggering (60-120 seconds)

Hardware Configuration:
- GPIO 16: NeoPixel data (via 3.3V→5V level shifter)
- GPIO 4:  MP3 player TX (Pico → DFPlayer Mini RX)
- GPIO 5:  MP3 player RX (Pico ← DFPlayer Mini TX)
- GPIO 15: Optional manual trigger (pull-down, active high)

Power Requirements:
- 5V 8A supply for Pico + NeoPixels + MP3 module
- 12V 5A supply for amplifier (separate)
- Common ground between all components

System Behaviour:
1. On startup, initialise all hardware
2. Enter main loop with random interval timer
3. Every 60-120 seconds, trigger lightning + thunder effect
4. Lightning and thunder synchronised for realistic storm effect
5. Optional manual trigger for testing/demonstration

For testing, reduce intervals to 5-10 seconds in configuration below.
"""

import machine
import neopixel
import time
import random
from lights import executeRandomLightning, clearLights
from lights import testLightning as _lights_testLightning, testAllPatterns as _lights_testAllPatterns
from mp3_player import MP3Player

# ============================================================================
# CONFIGURATION CONSTANTS
# ============================================================================
# Modify these values to customise system behaviour

# NeoPixel Configuration
LED_COUNT = 300          # Number of NeoPixels in strip
LED_PIN = 16             # GPIO pin for NeoPixel data (via level shifter)
LED_BATCH_SIZE = 40      # Pixels per update batch (memory optimisation)

# MP3 Player Configuration
MP3_TX_PIN = 4           # GPIO pin for UART TX (Pico → DFPlayer Mini RX)
MP3_RX_PIN = 5           # GPIO pin for UART RX (Pico ← DFPlayer Mini TX)
MP3_VOLUME = 25          # Volume level 0-30 (25 recommended for 60W amp)
TRACK_COUNT = 3          # Number of thunder tracks (0001.mp3, 0002.mp3, 0003.mp3)

# Timing Configuration
MIN_INTERVAL = 20        # Minimum seconds between effects (production: 60)
MAX_INTERVAL = 45       # Maximum seconds between effects (production: 120)
COOLDOWN_PERIOD = 5      # Seconds to wait after effect before next trigger

# Testing Configuration
# For faster testing, uncomment these lines:
# MIN_INTERVAL = 5       # 5 seconds for testing
# MAX_INTERVAL = 10      # 10 seconds for testing

# Optional Manual Trigger
TRIGGER_PIN = 15         # GPIO pin for manual trigger button (optional)
USE_MANUAL_TRIGGER = False  # Set to True to enable manual trigger

# Status LED (onboard Pico LED)
STATUS_LED_PIN = 25      # GPIO 25 (onboard LED for status indication)

# ============================================================================
# HARDWARE INITIALISATION
# ============================================================================

# Lazy singletons for REPL/testing convenience
_np_singleton = None
_mp3_singleton = None
_status_led_singleton = None

def _get_neopixels():
    """
    Lazy-initialise a NeoPixel instance using LED_PIN/LED_COUNT.
    Safe to call multiple times; reuses the same object.
    """
    global _np_singleton
    if _np_singleton is None:
        led_pin = machine.Pin(LED_PIN, machine.Pin.OUT)
        _np_singleton = neopixel.NeoPixel(led_pin, LED_COUNT)
        clearLights(_np_singleton, LED_BATCH_SIZE)
    return _np_singleton

def _get_status_led():
    """
    Lazy-initialise the onboard status LED (GPIO 25).
    """
    global _status_led_singleton
    if _status_led_singleton is None:
        _status_led_singleton = machine.Pin(STATUS_LED_PIN, machine.Pin.OUT)
        _status_led_singleton.off()
    return _status_led_singleton

def _get_mp3_player():
    """
    Lazy-initialise the MP3 player using configured pins and volume.
    Safe to call multiple times; reuses the same object.
    """
    global _mp3_singleton
    if _mp3_singleton is None:
        _mp3_singleton = MP3Player(MP3_TX_PIN, MP3_RX_PIN)
        _mp3_singleton.setVolume(MP3_VOLUME)
    return _mp3_singleton

def initialiseHardware():
    """
    Initialise all hardware components.
    
    Returns:
        Tuple of (neopixels, mp3_player, status_led, trigger_button)
        trigger_button will be None if USE_MANUAL_TRIGGER is False
    
    Raises:
        Exception if hardware initialisation fails
    """
    print("🎃 Halloween Lightning & Thunder Effect System")
    print("=" * 50)
    print()
    
    # Initialise status LED
    print("💡 Initialising status LED...")
    status_led = machine.Pin(STATUS_LED_PIN, machine.Pin.OUT)
    status_led.on()  # LED on during initialisation
    print(f"✅ Status LED ready (GPIO {STATUS_LED_PIN})")
    print()
    
    # Initialise NeoPixels
    print(f"🌈 Initialising {LED_COUNT} NeoPixels...")
    print(f"   Pin: GPIO {LED_PIN}")
    print(f"   Batch size: {LED_BATCH_SIZE} pixels")
    led_pin = machine.Pin(LED_PIN, machine.Pin.OUT)
    neopixels = neopixel.NeoPixel(led_pin, LED_COUNT)
    
    # Clear all pixels to start
    clearLights(neopixels, LED_BATCH_SIZE)
    print("✅ NeoPixels initialised and cleared")
    print()
    
    # Initialise MP3 player
    print("🎵 Initialising MP3 player...")
    mp3_player = MP3Player(MP3_TX_PIN, MP3_RX_PIN)
    mp3_player.setVolume(MP3_VOLUME)
    print(f"✅ MP3 player ready (Volume: {MP3_VOLUME}/30)")
    print()
    
    # Initialise manual trigger (if enabled)
    trigger_button = None
    if USE_MANUAL_TRIGGER:
        print("🔘 Initialising manual trigger button...")
        print(f"   Pin: GPIO {TRIGGER_PIN} (pull-down, active high)")
        # Configure as input with pull-down (button connects to 3.3V)
        trigger_button = machine.Pin(TRIGGER_PIN, machine.Pin.IN, machine.Pin.PULL_DOWN)
        print("✅ Manual trigger enabled")
        print()
    
    status_led.off()  # LED off after successful initialisation
    
    print("=" * 50)
    print("✅ All hardware initialised successfully")
    print()
    
    return neopixels, mp3_player, status_led, trigger_button


# ============================================================================
# EFFECT TRIGGERING
# ============================================================================

def triggerEffect(neopixels, mp3_player, status_led):
    """
    Trigger synchronised lightning and thunder effect.
    
    Sequence:
        1. Turn on status LED
        2. Start lightning flash animation
        3. Simultaneously start thunder sound (random track)
        4. Wait for effect to complete
        5. Turn off status LED
    
    Args:
        neopixels: Initialised NeoPixel object
        mp3_player: Initialised MP3Player object
        status_led: Status LED Pin object
    
    Timing:
        - Lightning flash: ~500ms duration
        - Thunder sound: ~3-5 seconds (depends on MP3 file)
        - Total effect: ~3-5 seconds
    """
    status_led.on()  # Visual indicator that effect is active
    
    # Select random thunder track (1 to TRACK_COUNT)
    track = random.randint(1, TRACK_COUNT)
    
    print(f"⚡ Triggering effect - Track {track}")
    
    # Start thunder playback
    # Do this first so sound starts immediately
    mp3_player.playTrack(track)
    
    # Simultaneously trigger lightning flash
    # Lightning duration is shorter than thunder, creating realistic effect
    executeRandomLightning(neopixels, duration_ms=500, batch_size=LED_BATCH_SIZE)
    
    # Wait for thunder sound to finish
    # Typical thunder duration: 3-5 seconds
    # This prevents rapid re-triggering and allows effect to complete
    time.sleep(4)
    
    print("✅ Effect complete")
    
    status_led.off()  # Effect finished


# ============================================================================
# REPL/TEST HELPERS EXPOSED VIA main.py
# ============================================================================

def testLightning():
    """
    Run a single random lightning flash using configured LED_PIN/LED_COUNT.

    REPL usage (after exec-ing main.py):
        >>> testLightning()
    """
    return _lights_testLightning(LED_PIN, LED_COUNT)


def testAllPatterns():
    """
    Run all lightning patterns (blue/red) using configured LED_PIN/LED_COUNT.

    REPL usage:
        >>> testAllPatterns()
    """
    return _lights_testAllPatterns(LED_PIN, LED_COUNT)


def playTrack(track=None, volume=None):
    """
    Play a thunder track via the MP3 player.

    Args:
        track: Optional track number (1..TRACK_COUNT). If None, chooses random.
        volume: Optional volume override (0..30). If provided, applies before play.

    REPL usage:
        >>> playTrack()        # random track at configured volume
        >>> playTrack(2)       # play specific track
        >>> playTrack(3, 22)   # set volume, then play track 3
    """
    player = _get_mp3_player()
    if volume is not None:
        player.setVolume(volume)
    if track is None:
        track = random.randint(1, TRACK_COUNT)
    player.playTrack(track)


def testE2E(duration_ms=500):
    """
    End-to-end test: randomise a lightning effect and a thunder track,
    start them simultaneously, and wait a few seconds.

    Lightning runs locally while audio plays asynchronously on DFPlayer.

    REPL usage:
        >>> testE2E()
    """
    np = _get_neopixels()
    player = _get_mp3_player()
    track = random.randint(1, TRACK_COUNT)
    print(f"🎬 E2E: Track {track}, duration {duration_ms}ms")
    player.playTrack(track)
    executeRandomLightning(np, duration_ms=duration_ms, batch_size=LED_BATCH_SIZE)
    time.sleep(4)
    return track


# ============================================================================
# MAIN EVENT LOOP
# ============================================================================

def main():
    """
    Main application loop.
    
    Behaviour:
        1. Initialise hardware
        2. Seed random number generator for variability
        3. Enter infinite loop:
           a. Generate random interval (MIN_INTERVAL to MAX_INTERVAL seconds)
           b. Wait for interval to expire (check for manual trigger every 100ms)
           c. Trigger lightning + thunder effect
           d. Cooldown period to prevent rapid re-triggering
        4. Handle errors gracefully (print and continue)
    
    Manual Trigger:
        If USE_MANUAL_TRIGGER is True, button press will immediately trigger
        effect regardless of interval timer.
    
    Loop runs indefinitely until power off or Ctrl+C (REPL only).
    """
    try:
        # Initialise all hardware
        neopixels, mp3_player, status_led, trigger_button = initialiseHardware()
        
        # Seed random number generator
        # Using time-based seed for variability between boots
        random.seed(time.ticks_ms())
        
        print("🌩️  Entering autonomous mode")
        print(f"   Interval: {MIN_INTERVAL}-{MAX_INTERVAL} seconds")
        print(f"   Cooldown: {COOLDOWN_PERIOD} seconds")
        if USE_MANUAL_TRIGGER:
            print(f"   Manual trigger: GPIO {TRIGGER_PIN}")
        print()
        print("Press Ctrl+C to stop (REPL only)")
        print("=" * 50)
        print()
        
        # Main event loop
        while True:
            # Generate random interval for next effect
            interval = random.randint(MIN_INTERVAL, MAX_INTERVAL)
            print(f"⏱️  Next effect in {interval} seconds...")
            
            # Wait for interval with manual trigger check
            # Break interval into 100ms chunks to check trigger button
            elapsed = 0
            triggered = False
            
            while elapsed < interval:
                # Check manual trigger button (if enabled)
                if USE_MANUAL_TRIGGER and trigger_button and trigger_button.value() == 1:
                    print("🔘 Manual trigger detected!")
                    triggered = True
                    break
                
                # Sleep for 100ms, then check again
                time.sleep(0.1)
                elapsed += 0.1
            
            # Trigger effect
            triggerEffect(neopixels, mp3_player, status_led)
            
            # Cooldown period to prevent rapid re-triggering
            # Especially important if manual trigger is used
            print(f"💤 Cooldown period ({COOLDOWN_PERIOD}s)...")
            time.sleep(COOLDOWN_PERIOD)
            print()
    
    except KeyboardInterrupt:
        # Graceful shutdown on Ctrl+C (REPL only)
        print()
        print("=" * 50)
        print("� Shutting down...")
        
        # Clean up hardware
        if 'neopixels' in locals():
            clearLights(neopixels, LED_BATCH_SIZE)
        
        if 'mp3_player' in locals():
            mp3_player.stop()
        
        if 'status_led' in locals():
            status_led.off()
        
        print("✅ Shutdown complete")
    
    except Exception as e:
        # Handle unexpected errors
        print()
        print("=" * 50)
        print("❌ FATAL ERROR:")
        print(f"   {e}")
        print()
        print("Hardware state:")
        print(f"   NeoPixels: {'initialised' if 'neopixels' in locals() else 'not initialised'}")
        print(f"   MP3 Player: {'initialised' if 'mp3_player' in locals() else 'not initialised'}")
        print()
        
        # Attempt cleanup
        try:
            if 'neopixels' in locals():
                clearLights(neopixels, LED_BATCH_SIZE)
            if 'status_led' in locals():
                status_led.off()
        except:
            pass  # Ignore cleanup errors
        
        print("System halted. Power cycle to restart.")


# ============================================================================
# ENTRY POINT
# ============================================================================

# Execute main function when module loads
# This runs automatically via boot.py
if __name__ == "__main__":
    main()
