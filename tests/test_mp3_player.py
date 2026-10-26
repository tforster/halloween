"""
Seam 2: DFPlayer frames through MP3Player's public interface with a fake UART.

Expected frames are the known-good literals in docs/reference/dfplayer-protocol.md, not values
recomputed with the checksum formula.
"""

from mp3_player import MP3Player


class FakeUart:
    def __init__(self):
        self.frames = []

    def write(self, data):
        self.frames.append(bytes(data))


def sendOne(action):
    uart = FakeUart()
    action(MP3Player(uart))
    assert len(uart.frames) == 1
    return uart.frames[0].hex(" ").upper()


def test_ac6_play_track_1_frame_matches_known_good_frame():
    assert sendOne(lambda player: player.playTrack(1)) == "7E FF 06 03 00 00 01 FE F7 EF"


def test_ac6_set_volume_25_frame_matches_known_good_frame():
    assert sendOne(lambda player: player.setVolume(25)) == "7E FF 06 06 00 00 19 FE DC EF"


def test_ac6_stop_frame_matches_known_good_frame():
    assert sendOne(lambda player: player.stop()) == "7E FF 06 16 00 00 00 FE E5 EF"
