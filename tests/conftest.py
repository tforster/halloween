"""
Shared pytest set-up for the firmware tests.

The firmware in src/ is MicroPython, but below start-up it imports nothing from the hardware
(`machine`, `neopixel`), so CPython can import it directly once src/ is on the path.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
