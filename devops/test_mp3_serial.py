#!/usr/bin/env python3
"""
Test serial communication with DFPlayer Mini MP3 module.

This script helps debug and test the DFPlayer Mini protocol
without deploying code to the Pico.

Usage:
    python devops/test_mp3_serial.py /dev/ttyUSB0
    python devops/test_mp3_serial.py COM3  # Windows
"""

import argparse
import time
from typing import Optional

try:
    import serial
except ImportError:
    print("Error: pyserial not installed")
    print("Install with: pip install pyserial")
    exit(1)


class DFPlayerTester:
    """Test interface for DFPlayer Mini MP3 module."""
    
    def __init__(self, port: str, baudrate: int = 9600):
        """
        Initialise serial connection to DFPlayer Mini.
        
        Args:
            port: Serial port (e.g., /dev/ttyUSB0 or COM3)
            baudrate: Baud rate (default: 9600)
        """
        self.ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(0.5)  # DFPlayer needs startup time
        print(f"Connected to {port} at {baudrate} baud")
    
    def _send_command(self, cmd: int, param_high: int = 0, param_low: int = 0) -> None:
        """
        Send command to DFPlayer Mini.
        
        Command format (10 bytes):
        [0] 0x7E - Start byte
        [1] 0xFF - Version
        [2] 0x06 - Length
        [3] CMD  - Command byte
        [4] 0x00 - Feedback (disabled)
        [5] PARAM_HIGH
        [6] PARAM_LOW
        [7] CHECKSUM_HIGH
        [8] CHECKSUM_LOW
        [9] 0xEF - End byte
        """
        # Calculate checksum
        checksum = -(0xFF + 0x06 + cmd + 0x00 + param_high + param_low)
        checksum_high = (checksum >> 8) & 0xFF
        checksum_low = checksum & 0xFF
        
        # Build command
        command = bytes([
            0x7E, 0xFF, 0x06, cmd, 0x00,
            param_high, param_low,
            checksum_high, checksum_low,
            0xEF
        ])
        
        self.ser.write(command)
        print(f"Sent: {' '.join(f'{b:02X}' for b in command)}")
        time.sleep(0.1)  # Give module time to process
    
    def play_track(self, track: int) -> None:
        """Play specific track number (1-based)."""
        print(f"\nPlaying track {track}...")
        self._send_command(0x03, 0x00, track)
    
    def set_volume(self, volume: int) -> None:
        """Set volume (0-30)."""
        volume = max(0, min(30, volume))
        print(f"\nSetting volume to {volume}...")
        self._send_command(0x06, 0x00, volume)
    
    def pause(self) -> None:
        """Pause playback."""
        print("\nPausing...")
        self._send_command(0x0E)
    
    def resume(self) -> None:
        """Resume playback."""
        print("\nResuming...")
        self._send_command(0x0D)
    
    def stop(self) -> None:
        """Stop playback."""
        print("\nStopping...")
        self._send_command(0x16)
    
    def reset(self) -> None:
        """Reset module."""
        print("\nResetting module...")
        self._send_command(0x0C)
        time.sleep(1)  # Reset takes time
    
    def close(self) -> None:
        """Close serial connection."""
        self.ser.close()


def interactive_test(port: str) -> None:
    """Run interactive test session."""
    tester = DFPlayerTester(port)
    
    print("\nDFPlayer Mini Test Interface")
    print("Commands:")
    print("  p <track>  - Play track number")
    print("  v <volume> - Set volume (0-30)")
    print("  pause      - Pause playback")
    print("  resume     - Resume playback")
    print("  stop       - Stop playback")
    print("  reset      - Reset module")
    print("  quit       - Exit")
    
    try:
        # Set initial volume
        tester.set_volume(20)
        
        while True:
            try:
                cmd = input("\n> ").strip().lower()
                
                if cmd == 'quit':
                    break
                elif cmd.startswith('p '):
                    track = int(cmd.split()[1])
                    tester.play_track(track)
                elif cmd.startswith('v '):
                    volume = int(cmd.split()[1])
                    tester.set_volume(volume)
                elif cmd == 'pause':
                    tester.pause()
                elif cmd == 'resume':
                    tester.resume()
                elif cmd == 'stop':
                    tester.stop()
                elif cmd == 'reset':
                    tester.reset()
                else:
                    print("Unknown command")
            except (ValueError, IndexError):
                print("Invalid command format")
            except KeyboardInterrupt:
                break
    
    finally:
        tester.close()
        print("\nDisconnected")


def main():
    parser = argparse.ArgumentParser(
        description="Test DFPlayer Mini serial communication"
    )
    parser.add_argument(
        'port',
        help='Serial port (e.g., /dev/ttyUSB0 or COM3)'
    )
    parser.add_argument(
        '--baudrate',
        type=int,
        default=9600,
        help='Baud rate (default: 9600)'
    )
    
    args = parser.parse_args()
    
    try:
        interactive_test(args.port)
    except serial.SerialException as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
