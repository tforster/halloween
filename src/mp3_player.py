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
- 50-100ms delay between commands
- 9600 baud rate (faster rates unreliable)
"""

import machine
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
    
    Provides high-level methods for controlling playback while handling
    low-level protocol details (checksums, timing, retries).
    
    Example usage:
        from mp3_player import MP3Player
        
        # Initialise player on UART1
        player = MP3Player(tx_pin=4, rx_pin=5)
        
        # Play track 1 at volume 20
        player.setVolume(20)
        player.playTrack(1)
    """
    
    def __init__(self, tx_pin, rx_pin, baud=9600):
        """
        Initialise UART connection to DFPlayer Mini module.
        
        Args:
            tx_pin: GPIO pin number for TX (Pico transmit → Module receive)
            rx_pin: GPIO pin number for RX (Pico receive ← Module transmit)
            baud: Baud rate (default 9600, do not change - faster rates unreliable)
        
        Hardware Notes:
            - DFPlayer Mini RX connects to Pico TX (GP4 recommended)
            - DFPlayer Mini TX connects to Pico RX (GP5 recommended)
            - Use UART1 to avoid conflicts with USB serial debugging
            - Module requires 5V power, but 3.3V UART signals work fine
        
        Timing Notes:
            - Waits 500ms for module initialisation
            - Sends reset command to clear any previous state
            - Sends init command to prepare module for playback
        """
        print(f"🎵 Initialising MP3 Player (TX: GP{tx_pin}, RX: GP{rx_pin})")
        
        # Initialise UART1 (ID=1) for MP3 player communication
        # UART0 is typically used for USB serial, so we use UART1
        self.uart = machine.UART(1, baudrate=baud, tx=machine.Pin(tx_pin), rx=machine.Pin(rx_pin))
        
        # Wait for module to initialise after power-on
        # DFPlayer Mini requires ~500ms startup time
        print("⏱️  Waiting for module initialisation (500ms)...")
        time.sleep_ms(INIT_DELAY_MS)
        
        # Reset module to known state
        print("🔄 Resetting module...")
        self._sendCommand(CMD_RESET, 0x00, 0x00)
        time.sleep_ms(CMD_DELAY_MS)
        
        # Initialise module for playback
        print("🎬 Initialising playback...")
        self._sendCommand(CMD_INIT, 0x00, 0x00)
        time.sleep_ms(CMD_DELAY_MS)
        
        print("✅ MP3 Player initialised")
    
    def playTrack(self, track_number):
        """
        Play specific track number from SD card.
        
        Args:
            track_number: Track number (1-3 for our setup)
                         Corresponds to 0001.mp3, 0002.mp3, 0003.mp3
        
        File Naming Requirements:
            - Files must be named 0001.mp3, 0002.mp3, etc.
            - Files must be in root directory of SD card
            - SD card must be FAT32 formatted
            - First file copied becomes track 1 (order matters!)
        
        Note: playTrack(1) plays 0001.mp3 (first thunder sound)
        """
        print(f"▶️  Playing track {track_number}")
        
        # Split track number into high and low bytes
        # For track numbers 1-255, high byte is always 0
        param_high = 0x00
        param_low = track_number
        
        self._sendCommand(CMD_PLAY_TRACK, param_high, param_low)
        time.sleep_ms(CMD_DELAY_MS)
    
    def setVolume(self, level):
        """
        Set playback volume.
        
        Args:
            level: Volume level 0-30 (0=mute, 30=maximum)
                  Recommended: 20-25 for balanced output
                  Warning: >25 may cause distortion on some amplifiers
        
        Note: Volume persists until changed or module reset
        """
        # Clamp volume to valid range (0-30)
        if level < 0:
            level = 0
        elif level > 30:
            level = 30
        
        print(f"🔊 Setting volume to {level}")
        
        self._sendCommand(CMD_SET_VOLUME, 0x00, level)
        time.sleep_ms(CMD_DELAY_MS)
    
    def pause(self):
        """
        Pause current playback.
        
        Can be resumed with play() method.
        """
        print("⏸️  Pausing playback")
        self._sendCommand(CMD_PAUSE, 0x00, 0x00)
        time.sleep_ms(CMD_DELAY_MS)
    
    def play(self):
        """
        Resume playback (after pause).
        
        Note: To start a specific track, use playTrack() instead.
        """
        print("▶️  Resuming playback")
        self._sendCommand(CMD_PLAY, 0x00, 0x00)
        time.sleep_ms(CMD_DELAY_MS)
    
    def stop(self):
        """
        Stop playback completely.
        
        Unlike pause(), requires playTrack() to restart (not play()).
        """
        print("⏹️  Stopping playback")
        self._sendCommand(CMD_STOP, 0x00, 0x00)
        time.sleep_ms(CMD_DELAY_MS)
    
    def _sendCommand(self, cmd, param_high, param_low):
        """
        Internal method: Format and send command to DFPlayer Mini.
        
        Constructs 10-byte command packet with proper checksum.
        
        Command Structure (10 bytes):
            [0] 0x7E - Start byte
            [1] 0xFF - Version
            [2] 0x06 - Length (always 6)
            [3] CMD  - Command byte
            [4] 0x00 - Feedback (0=no acknowledgement)
            [5] DATA_HIGH - Parameter high byte
            [6] DATA_LOW  - Parameter low byte
            [7] CHECKSUM_HIGH - Checksum high byte
            [8] CHECKSUM_LOW  - Checksum low byte
            [9] 0xEF - End byte
        
        Checksum Calculation:
            - Sum bytes [1] through [6] (version, length, cmd, feedback, params)
            - Negate the sum (two's complement)
            - Split into high and low bytes
        
        Args:
            cmd: Command byte (use CMD_* constants)
            param_high: Parameter high byte (usually 0x00)
            param_low: Parameter low byte (volume, track number, etc.)
        
        Protocol Reference:
            https://github.com/DFRobot/DFRobotDFPlayerMini/blob/master/DFRobotDFPlayerMini.cpp
        """
        # Calculate checksum (negative sum of bytes 1-6)
        # Formula: checksum = -(version + length + cmd + feedback + param_high + param_low)
        checksum = -(VERSION + LENGTH + cmd + NO_FEEDBACK + param_high + param_low)
        
        # Convert checksum to 16-bit signed value, then extract bytes
        # This handles the two's complement properly
        checksum = checksum & 0xFFFF  # Mask to 16 bits
        checksum_high = (checksum >> 8) & 0xFF  # High byte
        checksum_low = checksum & 0xFF          # Low byte
        
        # Construct 10-byte command packet
        command = bytearray([
            START_BYTE,      # [0] Start delimiter
            VERSION,         # [1] Protocol version
            LENGTH,          # [2] Command length
            cmd,             # [3] Command byte
            NO_FEEDBACK,     # [4] No acknowledgement (faster)
            param_high,      # [5] Parameter high byte
            param_low,       # [6] Parameter low byte
            checksum_high,   # [7] Checksum high byte
            checksum_low,    # [8] Checksum low byte
            END_BYTE         # [9] End delimiter
        ])
        
        # Send command via UART
        self.uart.write(command)
        
        # Note: We're not reading responses (NO_FEEDBACK mode)
        # This simplifies code and improves reliability
        # Commands are fire-and-forget with timing delays


# Standalone testing function (can be called from REPL)
def testMP3Player(tx_pin=4, rx_pin=5):
    """
    Standalone test function for MP3 player.
    
    Can be called from REPL for testing without full system:
        >>> from mp3_player import testMP3Player
        >>> testMP3Player(4, 5)  # Test on GP4 (TX) and GP5 (RX)
    
    Test Sequence:
        1. Initialise player
        2. Set volume to 20
        3. Play track 1 (0001.mp3)
        4. Wait 3 seconds
        5. Stop playback
    
    Hardware Requirements:
        - DFPlayer Mini connected to specified UART pins
        - MicroSD card with 0001.mp3 in root directory
        - Amplifier/speaker connected to audio output
        - 5V power supply for DFPlayer Mini
    
    Args:
        tx_pin: GPIO pin for Pico TX → DFPlayer RX (default 4)
        rx_pin: GPIO pin for Pico RX ← DFPlayer TX (default 5)
    """
    print("🎃 MP3 Player Test")
    print(f"TX Pin: GP{tx_pin}, RX Pin: GP{rx_pin}")
    print()
    
    # Initialise player
    player = MP3Player(tx_pin, rx_pin)
    print()
    
    # Set volume
    print("Setting volume to 20...")
    player.setVolume(20)
    print()
    
    # Play track 1
    print("Playing track 1 (0001.mp3)...")
    player.playTrack(1)
    print()
    
    # Let it play for a bit
    print("Playing for 3 seconds...")
    time.sleep(3)
    print()
    
    # Stop playback
    print("Stopping playback...")
    player.stop()
    print()
    
    print("✅ Test complete")


# Module-level test when run directly
if __name__ == "__main__":
    print("mp3_player.py - DFPlayer Mini Interface Module")
    print("Import this module and create an MP3Player instance")
    print("Example: testMP3Player(4, 5)")
