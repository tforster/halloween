"""
Seam 1: the storm scheduler under host Python with fake hardware.

Rigs are built from configuration with fake strips that record each write, the thunder channel
wraps a real MP3Player on a fake UART, and a virtual clock stands in for asyncio's timers so
minutes of storm run in milliseconds. The random source is seeded, so every run is the same.
"""

import asyncio
import heapq
import itertools
import random

import pytest

import main
from mp3_player import MP3Player

PLAY_TRACK = 0x03
GAP_MS = 1000  # Writes closer than this belong to one strike; patterns hold <= 150 ms, rigs wait >= 5 s


class FakeClock:
    """Virtual milliseconds. Sleepers wake in deadline order only when the test advances time."""

    def __init__(self):
        self.nowMs = 0
        self.sleepers = []
        self.order = itertools.count()

    def now(self):
        return self.nowMs

    def since(self, ticks):
        return self.nowMs - ticks

    async def sleep(self, ms):
        wake = asyncio.get_running_loop().create_future()
        heapq.heappush(self.sleepers, (self.nowMs + ms, next(self.order), wake))
        await wake

    async def advance(self, ms):
        target = self.nowMs + ms
        while True:
            await settle()
            if not self.sleepers or self.sleepers[0][0] > target:
                break
            self.nowMs, _, wake = heapq.heappop(self.sleepers)
            wake.set_result(None)
        self.nowMs = target


async def settle():
    """Let every runnable task run until it blocks on the clock again."""
    for _ in range(20):
        await asyncio.sleep(0)


class FakeStrip:
    """Records (time, lit) for every write(); lit means any pixel is not black."""

    def __init__(self, clock, pixels):
        self.clock = clock
        self.pixels = [(0, 0, 0)] * pixels
        self.writes = []

    def __len__(self):
        return len(self.pixels)

    def __setitem__(self, index, colour):
        self.pixels[index] = colour

    def write(self):
        self.writes.append((self.clock.now(), any(any(p) for p in self.pixels)))

    def strikes(self):
        """(start, end) of each strike: runs of writes no more than GAP_MS apart."""
        runs = []
        for at, _ in self.writes:
            if runs and at - runs[-1][1] <= GAP_MS:
                runs[-1][1] = at
            else:
                runs.append([at, at])
        return [tuple(run) for run in runs]


class FakeUart:
    def __init__(self, clock):
        self.clock = clock
        self.frames = []

    def write(self, data):
        self.frames.append((self.clock.now(), bytes(data)))

    def plays(self):
        """(time, track) for every play-track frame."""
        return [(at, frame[6]) for at, frame in self.frames if frame[3] == PLAY_TRACK]


def rigConfig(name, intervalS=(60, 120), pixels=300):
    return {"name": name, "pin": 16, "pixels": pixels, "intervalS": intervalS}


def makeStorm(configs, seed=2026, testMode=False, trackCount=3):
    clock = FakeClock()
    rng = random.Random(seed)
    strips = []

    def makeStrip(pin, pixels):
        strip = FakeStrip(clock, pixels)
        strips.append(strip)
        return strip

    uart = FakeUart(clock)
    rigs = main.buildRigs(configs, makeStrip, testMode)
    thunder = main.Thunder(MP3Player(uart), clock, rng, trackCount)
    return main.Storm(rigs, thunder, clock, rng), clock, strips, uart


def runFor(storm, clock, ms, *coroutines):
    async def scenario():
        tasks = [asyncio.create_task(storm.run())]
        tasks += [asyncio.create_task(c) for c in coroutines]
        await clock.advance(ms)
        for task in tasks:
            task.cancel()

    asyncio.run(scenario())


def waitsBetween(strikes):
    """The wait before each strike: from start-up, then from the previous strike's end."""
    return [strikes[0][0]] + [nxt[0] - prev[1] for prev, nxt in zip(strikes, strikes[1:])]


def test_ac1_each_rig_strikes_at_a_random_interval_within_its_own_range():
    ranges = [(60, 120), (20, 30)]
    storm, clock, strips, _ = makeStorm([rigConfig("A", ranges[0]), rigConfig("B", ranges[1])])

    runFor(storm, clock, 30 * 60_000)

    for (minS, maxS), strip in zip(ranges, strips):
        waits = waitsBetween(strip.strikes())
        assert len(waits) >= 10
        # A strike's last write is followed by one 1 ms frame yield before the rig waits again
        assert all(minS * 1000 <= wait <= maxS * 1000 + 1 for wait in waits), waits
        assert len(set(waits)) > 1, "intervals should vary"


def test_ac2_both_strips_keep_receiving_frames_while_strikes_overlap():
    # Short intervals so strikes on the two rigs overlap often
    storm, clock, strips, _ = makeStorm([rigConfig("A", (1, 2)), rigConfig("B", (1, 2))])

    runFor(storm, clock, 60_000)

    [strikesA, strikesB] = [strip.strikes() for strip in strips]
    overlaps = [
        (max(a[0], b[0]), min(a[1], b[1]))
        for a in strikesA
        for b in strikesB
        if a[0] < b[1] and b[0] < a[1]
    ]
    assert len(overlaps) >= 3, "scenario should produce overlapping strikes"
    for start, end in overlaps:
        for strip in strips:
            times = [at for at, _ in strip.writes if start <= at <= end]
            # The longest hold in any pattern is 150 ms; a stalled strip would go dark for a
            # whole strike on the other rig (at least 400 ms)
            assert all(b - a <= 200 for a, b in zip(times, times[1:])), (start, end)


def test_ac3_each_strike_sends_one_play_track_command_within_the_track_count():
    storm, clock, [strip], uart = makeStorm([rigConfig("A")], trackCount=5)

    runFor(storm, clock, 60 * 60_000)

    strikes = strip.strikes()
    plays = uart.plays()
    assert len(strikes) >= 20
    assert [at for at, _ in plays] == [start for start, _ in strikes]
    assert {track for _, track in plays} <= {1, 2, 3, 4, 5}
    assert len({track for _, track in plays}) > 1, "tracks should vary"


class ScriptedTracks:
    """A random source whose randint returns the given tracks in order."""

    def __init__(self, *tracks):
        self.tracks = list(tracks)

    def randint(self, low, high):
        return self.tracks.pop(0)


def test_ac4_strike_while_thunder_plays_sends_a_new_play_command_immediately():
    storm, clock, strips, uart = makeStorm([rigConfig("A", (1, 2)), rigConfig("B", (1, 2))])

    runFor(storm, clock, 60_000)

    starts = sorted(start for strip in strips for start, _ in strip.strikes())
    playTimes = [at for at, _ in uart.plays()]
    # Thunder tracks run for seconds, so with strikes 1-2 s apart nearly every strike lands while
    # thunder is playing. Each still gets a play command at once: the only allowed delay is the
    # DFPlayer's minimum spacing after the previous command.
    for start in starts:
        assert any(start <= at <= start + main.CMD_DELAY_MS for at in playTimes), start
    assert len(playTimes) <= len(starts), "no command is queued beyond one per strike"
    assert all(b - a >= main.CMD_DELAY_MS for a, b in zip(playTimes, playTimes[1:]))


def test_ac4_strikes_inside_the_command_gap_send_only_the_latest_track():
    clock = FakeClock()
    uart = FakeUart(clock)
    thunder = main.Thunder(MP3Player(uart), clock, ScriptedTracks(1, 2, 3), 3)

    async def scenario():
        thunder.strike()  # t=0: sent at once
        await clock.advance(30)
        thunder.strike()  # t=30: inside the 100 ms gap, waits
        await clock.advance(30)
        thunder.strike()  # t=60: replaces the waiting track
        await clock.advance(500)

    asyncio.run(scenario())

    assert uart.plays() == [(0, 1), (100, 3)]


@pytest.mark.parametrize("rigCount", [1, 3])
def test_ac5_rig_count_follows_configuration(rigCount):
    configs = [rigConfig(name) for name in "ABC"[:rigCount]]
    storm, clock, strips, uart = makeStorm(configs)

    runFor(storm, clock, 10 * 60_000)

    assert len(strips) == rigCount
    assert all(len(strip.strikes()) >= 4 for strip in strips)
    assert len(uart.plays()) == sum(len(strip.strikes()) for strip in strips)


def test_ac8_test_mode_shortens_intervals_without_editing_the_interval_constants():
    storm, clock, [strip], _ = makeStorm([rigConfig("A", (60, 120))], testMode=True)

    runFor(storm, clock, 5 * 60_000)

    minS, maxS = main.TEST_INTERVAL_S
    assert maxS < 60
    waits = waitsBetween(strip.strikes())
    assert len(waits) >= 20
    assert all(minS * 1000 <= wait <= maxS * 1000 + 1 for wait in waits), waits
    assert main.RIGS[0]["intervalS"] == (60, 120), "configured intervals stay as written"


class FakeButton:
    """Manual trigger input: value() is 1 while pressed (the pin is pulled down when open)."""

    def __init__(self):
        self.pressed = 0

    def value(self):
        return self.pressed


async def press(clock, button, atMs, holdMs=300):
    await clock.sleep(atMs)
    button.pressed = 1
    await clock.sleep(holdMs)
    button.pressed = 0


def test_ac7_a_press_fires_one_strike_on_a_rig():
    storm, clock, strips, uart = makeStorm([rigConfig("A"), rigConfig("B")])
    button = FakeButton()

    # Rigs wait at least 60 s, so any strike in the first 5 s comes from the button
    runFor(storm, clock, 5_000, storm.watchTrigger(button), press(clock, button, 1_000))

    strikes = [start for strip in strips for start, _ in strip.strikes()]
    assert len(strikes) == 1, "one press held for 300 ms fires once"
    assert 1_000 <= strikes[0] <= 1_000 + main.TRIGGER_POLL_MS
    assert len(uart.plays()) == 1


def test_ac7_a_press_while_every_rig_is_striking_is_ignored():
    storm, clock, [strip], uart = makeStorm([rigConfig("A")])
    button = FakeButton()

    # The first press starts a strike (at least 400 ms); the second lands while it is running
    runFor(
        storm,
        clock,
        5_000,
        storm.watchTrigger(button),
        press(clock, button, 1_000, holdMs=100),
        press(clock, button, 1_200, holdMs=100),
    )

    assert len(strip.strikes()) == 1
    assert len(uart.plays()) == 1


def test_ac7_a_rig_timer_firing_during_a_manual_strike_waits_a_fresh_interval_after_it():
    storm, clock, [strip], uart = makeStorm([rigConfig("A", (1, 1))])
    button = FakeButton()

    # The press strikes at ~900 ms; the rig's own 1 s timer fires mid-strike. It must neither
    # start a second pattern on the strip nor strike sooner than 1 s after the manual strike ends
    runFor(storm, clock, 3_000, storm.watchTrigger(button), press(clock, button, 900, holdMs=50))

    strikes = strip.strikes()
    assert len(strikes) == 2
    assert len(uart.plays()) == 2
    assert strikes[1][0] - strikes[0][1] >= 1_000
