"""
Halloween Lightning & Thunder Effect - Main Application

One Raspberry Pi Pico 2 drives several lightning rigs. Each rig owns a WS2812B strip and strikes
on its own random timer; one DFPlayer Mini plays thunder for all of them, and the latest strike
wins: a new strike replaces thunder that is already playing. See
docs/explanation/2026-blueprint.md.

Hardware Configuration:
- GPIO 16: Rig A NeoPixel data (via 74AHCT125 level shifter)
- GPIO 17: Rig B NeoPixel data (adjacent pin, also PIO-capable)
- GPIO 4:  UART1 TX -> DFPlayer Mini RX
- GPIO 5:  UART1 RX (reserved; no feedback is read)
- GPIO 15: Optional manual trigger (pull-down, active high)
- GPIO 25: Onboard LED, heartbeat while the scheduler runs

Concurrency:
asyncio, one task per rig. Lightning patterns await the clock between frames, so overlapping
strikes on different strips interleave frame by frame. Hardware (strips, UART, pins) is created
only in start(); everything above it takes fakes under host pytest.
"""

import asyncio

from lights import executeRandomLightning
from mp3_player import CMD_DELAY_MS

# ============================================================================
# CONFIGURATION CONSTANTS
# ============================================================================

# One entry per rig. Add or remove entries to change the number of rigs; no code changes.
# Pins are GPIO numbers; intervalS is the (min, max) wait in seconds after a strike ends.
RIGS = [
    {"name": "A", "pin": 16, "pixels": 300, "intervalS": (60, 120)},
    {"name": "B", "pin": 17, "pixels": 300, "intervalS": (60, 120)},
]

# MP3 Player Configuration
MP3_TX_PIN = 4           # UART1 TX (Pico -> DFPlayer Mini RX)
MP3_RX_PIN = 5           # UART1 RX, reserved: commands are sent without feedback
MP3_VOLUME = 25          # Volume level 0-30; one speaker for the display, retune on site
TRACK_COUNT = 3          # Thunder tracks on the SD card (0001.mp3 ... 0003.mp3)

# Test mode: every rig waits TEST_INTERVAL_S instead of its own intervalS, for bench testing
TEST_MODE = False
TEST_INTERVAL_S = (1, 3)

# Optional Manual Trigger
TRIGGER_PIN = 15         # Button to 3.3 V; internal pull-down holds it low when open
USE_MANUAL_TRIGGER = False
TRIGGER_POLL_MS = 50     # Poll period; also debounces, as contact bounce settles within it

# How often a rig whose timer fired mid-strike checks whether the strike has ended
FRAME_POLL_MS = 10

# Set by devops/simulate.sh. Wokwi's Pico 2 hangs inside machine.UART(1, ...) and has no
# DFPlayer part, so a simulated run sends frames nowhere; MP3Player still prints each one
SIMULATED = False

# Status LED (onboard Pico LED)
STATUS_LED_PIN = 25


# ============================================================================
# RIGS, THUNDER AND THE STORM
# ============================================================================


class Rig:
    """One strip and its strike interval. isBusy is set while a strike is animating."""

    def __init__(self, name, strip, intervalS):
        self.name = name
        self.strip = strip
        self.minMs = intervalS[0] * 1000
        self.maxMs = intervalS[1] * 1000
        self.isBusy = False
        self.manualStrike = None


def buildRigs(rigConfigs, makeStrip, testMode=False):
    """
    Create a Rig per configuration entry. makeStrip(pin, pixels) opens the strip: a NeoPixel on
    the Pico, a fake under pytest. testMode swaps every interval for TEST_INTERVAL_S.
    """
    return [
        Rig(
            config["name"],
            makeStrip(config["pin"], config["pixels"]),
            TEST_INTERVAL_S if testMode else config["intervalS"],
        )
        for config in rigConfigs
    ]


class Thunder:
    """
    The one shared audio path: every strike asks it for a random thunder track.

    Latest strike wins. A play command goes out at once, cutting off any thunder still playing,
    unless the previous command left the DFPlayer less than CMD_DELAY_MS ago (back-to-back
    frames overflow its buffer). Then the track waits out the gap, and a strike during that wait
    replaces it, so at most one command is ever pending and nothing queues.
    """

    def __init__(self, player, clock, rng, trackCount):
        self.player = player
        self.clock = clock
        self.rng = rng
        self.trackCount = trackCount
        self.lastSentAt = None
        self.pendingTrack = None
        self.sender = None

    def strike(self):
        track = self.rng.randint(1, self.trackCount)
        if self.pendingTrack is not None:
            self.pendingTrack = track
            return
        wait = 0 if self.lastSentAt is None else CMD_DELAY_MS - self.clock.since(self.lastSentAt)
        if wait <= 0:
            self._send(track)
        else:
            self.pendingTrack = track
            # Held here because CPython (the host tests) keeps only a weak reference to tasks
            self.sender = asyncio.create_task(self._sendAfter(wait))

    async def _sendAfter(self, wait):
        await self.clock.sleep(wait)
        self._send(self.pendingTrack)
        self.pendingTrack = None

    def _send(self, track):
        self.player.playTrack(track)
        self.lastSentAt = self.clock.now()


class Storm:
    """Runs every rig on its own timer and routes each strike through one strike path."""

    def __init__(self, rigs, thunder, clock, rng):
        self.rigs = rigs
        self.thunder = thunder
        self.clock = clock
        self.rng = rng

    async def run(self):
        await asyncio.gather(*[self._runRig(rig) for rig in self.rigs])

    async def _runRig(self, rig):
        while True:
            await self.clock.sleep(self.rng.randint(rig.minMs, rig.maxMs))
            if rig.isBusy:
                # A manual strike is running on this rig. Striking now would garble it, so wait
                # for it to end and start a fresh interval from there, as after any strike
                while rig.isBusy:
                    await self.clock.sleep(FRAME_POLL_MS)
                continue
            await self.strike(rig)

    async def watchTrigger(self, button):
        """
        Fire one strike on a random idle rig for each press. Fires on the press edge, so a held
        button strikes once; a press while every rig is striking is ignored, because two
        patterns on one strip would garble it. Rig timers are not reset.
        """
        wasPressed = False
        while True:
            isPressed = button.value() == 1
            if isPressed and not wasPressed:
                idle = [rig for rig in self.rigs if not rig.isBusy]
                if idle:
                    rig = idle[self.rng.randint(0, len(idle) - 1)]
                    # Mark it busy now, before the task runs, so a second press can't pick it
                    rig.isBusy = True
                    # MicroPython's scheduler holds running tasks, but CPython (the host tests) keeps
                    # only a weak reference, so the rig holds it until the strike ends
                    rig.manualStrike = asyncio.create_task(self.strike(rig))
            wasPressed = isPressed
            await self.clock.sleep(TRIGGER_POLL_MS)

    async def strike(self, rig):
        rig.isBusy = True
        try:
            print("Rig", rig.name, "strikes")
            self.thunder.strike()
            await executeRandomLightning(rig.strip, self.clock, self.rng)
        finally:
            rig.isBusy = False


async def heartbeat(led, clock):
    """Blink the onboard LED at 1 Hz. If it stops blinking, the scheduler has stalled or died."""
    while True:
        led.toggle()
        await clock.sleep(500)


async def showtime(storm, led, trigger, clock):
    tasks = [storm.run(), heartbeat(led, clock)]
    if trigger:
        tasks.append(storm.watchTrigger(trigger))
    await asyncio.gather(*tasks)


# ============================================================================
# START-UP: the only place hardware is created
# ============================================================================


class NoUart:
    """Stands in for the DFPlayer UART in Wokwi (see SIMULATED): accepts frames and drops them."""

    def write(self, frame):
        return len(frame)


def start():
    """Open the hardware, wake the DFPlayer and run the storm until power-off or Ctrl-C."""
    import machine
    import neopixel
    import os
    import random
    import time

    from clock import PicoClock
    from mp3_player import startPlayer

    led = machine.Pin(STATUS_LED_PIN, machine.Pin.OUT)
    led.on()  # Solid while starting; blinking once the storm runs

    def makeStrip(pin, pixels):
        strip = neopixel.NeoPixel(machine.Pin(pin, machine.Pin.OUT), pixels)
        strip.fill((0, 0, 0))  # Strips power up showing random colours
        strip.write()
        return strip

    rigs = buildRigs(RIGS, makeStrip, TEST_MODE)

    if SIMULATED:
        uart = NoUart()
    else:
        # UART1 keeps UART0 free for USB serial debugging; 9600 baud is the only reliable rate
        uart = machine.UART(1, baudrate=9600, tx=machine.Pin(MP3_TX_PIN), rx=machine.Pin(MP3_RX_PIN))
    player = startPlayer(uart)
    player.setVolume(MP3_VOLUME)
    time.sleep_ms(CMD_DELAY_MS)

    # ticks_ms() is nearly the same on every boot; os.urandom draws on the RP2350's hardware
    # entropy, so each power-up gets a different storm (docs/reference/known-issues.md)
    random.seed(int.from_bytes(os.urandom(4), "little"))

    trigger = None
    if USE_MANUAL_TRIGGER:
        trigger = machine.Pin(TRIGGER_PIN, machine.Pin.IN, machine.Pin.PULL_DOWN)

    clock = PicoClock()
    storm = Storm(rigs, Thunder(player, clock, random, TRACK_COUNT), clock, random)

    print("Storm running:", len(rigs), "rigs", "(test mode)" if TEST_MODE else "")
    try:
        asyncio.run(showtime(storm, led, trigger, clock))
    finally:
        # Ctrl-C in the REPL or a fatal error: leave the display dark and quiet
        for rig in rigs:
            rig.strip.fill((0, 0, 0))
            rig.strip.write()
        time.sleep_ms(CMD_DELAY_MS)  # A play may have gone out just before the interrupt
        player.stop()
        led.off()


# boot.py runs this file on power-up (AUTO_START); host tests import it without starting
if __name__ == "__main__":
    start()
