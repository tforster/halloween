# DFPlayer Mini Protocol <!-- omit in toc -->

The serial frames `src/mp3_player.py` sends to the DFPlayer Mini, and the timing it needs. The upstream specification is the [DFRobot DFPlayer Mini library](https://github.com/DFRobot/DFRobotDFPlayerMini).

## Table of Contents <!-- omit in toc -->

- [1. Serial Settings](#1-serial-settings)
- [2. Frame Format](#2-frame-format)
- [3. Commands](#3-commands)
- [4. Known-Good Frames](#4-known-good-frames)
- [5. Timing](#5-timing)

## 1. Serial Settings

- 9600 baud, 8N1, on UART1; pins are in [Hardware](./hardware.md#2-pin-assignments). Faster rates are unreliable.
- Commands are sent without feedback (byte 4 is `0x00`), so the module sends no acknowledgement and nothing is read back.

## 2. Frame Format

Every command is 10 bytes:

| Byte | Value           | Meaning             |
| :--- | :-------------- | :------------------ |
| 0    | `0x7E`          | Start               |
| 1    | `0xFF`          | Version             |
| 2    | `0x06`          | Length, always 6    |
| 3    | `CMD`           | Command             |
| 4    | `0x00`          | Feedback off        |
| 5    | `DATA_HIGH`     | Parameter high byte |
| 6    | `DATA_LOW`      | Parameter low byte  |
| 7    | `CHECKSUM_HIGH` | Checksum high byte  |
| 8    | `CHECKSUM_LOW`  | Checksum low byte   |
| 9    | `0xEF`          | End                 |

The checksum is the two's complement of the sum of bytes 1 to 6, masked to 16 bits: `(-(0xFF + 0x06 + CMD + 0x00 + DATA_HIGH + DATA_LOW)) & 0xFFFF`.

## 3. Commands

| Command    | Byte   | Parameter                                                       | `MP3Player` method        |
| :--------- | :----- | :-------------------------------------------------------------- | :------------------------ |
| Play track | `0x03` | Track number, 1–255 (`playTrack` always sends a zero high byte) | `playTrack(n)`            |
| Set volume | `0x06` | Level, 0–30                                                     | `setVolume(level)`        |
| Reset      | `0x0C` | None                                                            | Called by the constructor |
| Resume     | `0x0D` | None                                                            | `play()`                  |
| Pause      | `0x0E` | None                                                            | `pause()`                 |
| Stop       | `0x16` | None                                                            | `stop()`                  |
| Initialise | `0x3F` | None                                                            | Called by the constructor |

## 4. Known-Good Frames

Worked from the formula above; use these as reference values in tests.

| Command       | Frame                           |
| :------------ | :------------------------------ |
| Play track 1  | `7E FF 06 03 00 00 01 FE F7 EF` |
| Set volume 25 | `7E FF 06 06 00 00 19 FE DC EF` |
| Pause         | `7E FF 06 0E 00 00 00 FE ED EF` |
| Resume        | `7E FF 06 0D 00 00 00 FE EE EF` |
| Stop          | `7E FF 06 16 00 00 00 FE E5 EF` |

## 5. Timing

| Delay            | Value                    | Why                                              |
| :--------------- | :----------------------- | :----------------------------------------------- |
| Start-up         | 500 ms (`INIT_DELAY_MS`) | The module ignores commands until it has booted  |
| Between commands | 100 ms (`CMD_DELAY_MS`)  | Back-to-back frames overflow the module's buffer |

[← Back to Reference](./README.md)
