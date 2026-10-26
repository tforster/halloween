"""
Checks on the firmware files themselves rather than their behaviour.
"""

from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src"


def test_ac9_firmware_source_is_ascii_so_mpremote_mount_loads_it_intact():
    # npm run simulate imports src/ over mpremote's mount, which corrupted main.py after its
    # multi-byte "→" characters (SyntaxError mid-file); ASCII-only source loads intact
    offenders = [
        f"{path.name}:{number}"
        for path in sorted(SRC.glob("*.py"))
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
        if not line.isascii()
    ]
    assert offenders == []
