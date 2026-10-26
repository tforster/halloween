"""
Checks on the firmware files themselves rather than their behaviour.
"""

from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src"


def test_ac9_firmware_source_is_ascii_so_mpremote_mount_loads_it_intact():
    # A SyntaxError mid-file under npm run simulate was first blamed on main.py's multi-byte "→"
    # characters; HALL-6 traced it to Wokwi's RP2350 emulation (ADR-012). ASCII-only source still
    # rules out encoding whenever a mounted import fails
    offenders = [
        f"{path.name}:{number}"
        for path in sorted(SRC.glob("*.py"))
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
        if not line.isascii()
    ]
    assert offenders == []
