"""
DFPlayer Mini MP3 Player Module Interface

This module implements the serial protocol for communicating with DFPlayer Mini
MP3 player modules via UART. Handles command formatting, checksum calculation,
and timing requirements.

Hardware Requirements:
- DFPlayer Mini module (DFRobot compatible)
- UART connection (9600 baud)
- MicroSD card with MP3 files (0001.mp3, 0002.mp3, etc.)
- 5V power supply for module

Protocol Specification:
- Based on DFRobot DFPlayer Mini protocol
- Reference: https://github.com/DFRobot/DFRobotDFPlayerMini
- Command format: 7E FF 06 <CMD> 00 <DATA_H> <DATA_L> <CHKSUM_H> <CHKSUM_L> EF

Timing Requirements:
- 500ms initialisation delay after power-on
- 100ms between commands
- 9600 baud rate (faster rates unreliable)

MP3Player only formats and writes frames. It never sleeps, so it can run inside the asyncio
scheduler without stalling the LED strips: start-up waits are done by main.start(), and the
spacing between commands during the show is kept by the thunder channel in main.py. The UART is
created at start-up and passed in, so the frames can be checked under host Python with a fake.
"""

import time

# DFPlayer Mini command bytes (verified against DFRobot specification)
CMD_NEXT = 0x01          # Play next track
CMD_PREV = 0x02          # Play previous track
CMD_PLAY_TRACK = 0x03    # Play specific track number
CMD_VOL_UP = 0x04        # Increase volume
CMD_VOL_DOWN = 0x05      # Decrease volume
CMD_SET_VOLUME = 0x06    # Set volume to specific level (0-30)
CMD_SET_EQ = 0x07        # Set equaliser mode
CMD_PLAY_MODE = 0x08     # Set playback mode (repeat, etc.)
CMD_SET_SOURCE = 0x09    # Set playback source (SD, USB, etc.)
CMD_STANDBY = 0x0A       # Enter standby mode
CMD_NORMAL = 0x0B        # Exit standby mode
CMD_RESET = 0x0C         # Reset module
CMD_PLAY = 0x0D          # Resume playback
CMD_PAUSE = 0x0E         # Pause playback
CMD_PLAY_FOLDER = 0x0F   # Play track from specific folder
CMD_STOP = 0x16          # Stop playback
CMD_INIT = 0x3F          # Initialise module

# Protocol constants
START_BYTE = 0x7E        # Command start delimiter
END_BYTE = 0xEF          # Command end delimiter
VERSION = 0xFF           # Protocol version
LENGTH = 0x06            # Command length (always 6 bytes)
NO_FEEDBACK = 0x00       # Disable command acknowledgement (faster)

# Timing constants (in milliseconds)
INIT_DELAY_MS = 500      # Module startup time after power-on
CMD_DELAY_MS = 100       # Delay between commands (prevent buffer overflow)


class MP3Player:
    """
    Interface for DFPlayer Mini MP3 player module.

    Formats the 10-byte command frames (checksums included) and writes them to the UART it is
    given. It does not wait between commands; callers keep CMD_DELAY_MS between frames.

    Example usage:
        import machine
        from mp3_player import MP3Player

        uart = machine.UART(1, baudrate=9600, tx=machine.Pin(4), rx=machine.Pin(5))
        player = MP3Player(uart)
        player.setVolume(20)
        player.playTrack(1)
    """

    def __init__(self, uart):
        """
        Args:
            uart: An open 9600-baud UART (or anything with write(bytes)) wired to the
                  DFPlayer's RX pin. UART1 keeps UART0 free for USB serial debugging.
        """
        self.uart = uart

    def reset(self):
        """Reset the module to a known state. Send only after INIT_DELAY_MS from power-on."""
        self._sendCommand(CMD_RESET, 0x00, 0x00)

    def initialise(self):
        """Prepare the module for playback; some modules ignore play commands without it."""
        self._sendCommand(CMD_INIT, 0x00, 0x00)

    def playTrack(self, trackNumber):
        """
        Play specific track number from SD card.

        Args:
            trackNumber: Track number (1-255), playing 0001.mp3, 0002.mp3, ...

        File Naming Requirements:
            - Files must be named 0001.mp3, 0002.mp3, etc.
            - Files must be in root directory of SD card
            - SD card must be FAT32 formatted
            - The module numbers tracks by copy order, not by name (see known-issues.md)
        """
        # Track numbers 1-255 fit the low byte, so the high byte is always 0
        self._sendCommand(CMD_PLAY_TRACK, 0x00, trackNumber)

    def setVolume(self, level):
        """
        Set playback volume.

        Args:
            level: Volume level 0-30 (0=mute, 30=maximum), clamped to that range.
                   >25 may distort on some amplifiers.

        Note: Volume persists until changed or module reset
        """
        level = max(0, min(30, level))
        self._sendCommand(CMD_SET_VOLUME, 0x00, level)

    def pause(self):
        """Pause current playback; resume with play()."""
        self._sendCommand(CMD_PAUSE, 0x00, 0x00)

    def play(self):
        """Resume playback after pause(). To start a specific track, use playTrack()."""
        self._sendCommand(CMD_PLAY, 0x00, 0x00)

    def stop(self):
        """Stop playback completely; restart with playTrack(), not play()."""
        self._sendCommand(CMD_STOP, 0x00, 0x00)

    def _sendCommand(self, cmd, paramHigh, paramLow):
        """
        Format and send one 10-byte command frame.

        Frame: 7E FF 06 CMD 00 DATA_H DATA_L CHK_H CHK_L EF. The checksum is the two's
        complement of bytes 1-6, masked to 16 bits (docs/reference/dfplayer-protocol.md).

        Protocol Reference:
            https://github.com/DFRobot/DFRobotDFPlayerMini/blob/master/DFRobotDFPlayerMini.cpp
        """
        checksum = -(VERSION + LENGTH + cmd + NO_FEEDBACK + paramHigh + paramLow) & 0xFFFF
        frame = bytearray([
            START_BYTE,
            VERSION,
            LENGTH,
            cmd,
            NO_FEEDBACK,     # No acknowledgement: nothing is read back
            paramHigh,
            paramLow,
            checksum >> 8,
            checksum & 0xFF,
            END_BYTE,
        ])
        self.uart.write(frame)

        # Wokwi has no DFPlayer part, so the serial monitor stands in for it (blueprint 4.3)
        print("DFPlayer <", " ".join("%02X" % b for b in frame))


def startPlayer(uart):
    """
    Wake the module and return a ready MP3Player. Blocks for about 700 ms, so call it at
    start-up only, before the scheduler runs.

    The module ignores commands until it has booted (INIT_DELAY_MS), and back-to-back frames
    overflow its buffer (CMD_DELAY_MS); see docs/reference/known-issues.md.
    """
    player = MP3Player(uart)
    time.sleep_ms(INIT_DELAY_MS)
    player.reset()
    time.sleep_ms(CMD_DELAY_MS)
    player.initialise()
    time.sleep_ms(CMD_DELAY_MS)
    return player


def testMP3Player(txPin=4, rxPin=5):
    """
    Play track 1 at volume 20 for 3 seconds, then stop. REPL only:

        >>> from mp3_player import testMP3Player
        >>> testMP3Player(4, 5)

    Needs the DFPlayer wired to the given UART1 pins and 0001.mp3 on its MicroSD card.
    """
    import machine

    uart = machine.UART(1, baudrate=9600, tx=machine.Pin(txPin), rx=machine.Pin(rxPin))
    player = startPlayer(uart)
    player.setVolume(20)
    time.sleep_ms(CMD_DELAY_MS)
    player.playTrack(1)
    time.sleep(3)
    player.stop()


# Module-level test when run directly
if __name__ == "__main__":
    print("mp3_player.py - DFPlayer Mini Interface Module")
    print("Import this module and create an MP3Player instance")
    print("Example: testMP3Player(4, 5)")
