"""
Real clock for the asyncio scheduler on the Pico.

The scheduler, thunder channel and lightning patterns never call time or asyncio timers
directly: they take a clock with now(), since(ticks) and sleep(ms). main.start() and the REPL
helpers in lights.py pass this one; the host tests pass a virtual clock instead, so minutes of
storm run in milliseconds.
"""

import asyncio
import time


class PicoClock:
    def now(self):
        return time.ticks_ms()

    def since(self, ticks):
        # ticks_ms wraps (about every 12 days on rp2), so differences go through ticks_diff
        return time.ticks_diff(time.ticks_ms(), ticks)

    async def sleep(self, ms):
        await asyncio.sleep_ms(ms)
