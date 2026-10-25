# Prepare Thunder Audio <!-- omit in toc -->

Turn thunder recordings into files the DFPlayer Mini plays in a predictable order, and put them on its MicroSD card.

## Table of Contents <!-- omit in toc -->

- [1. Prerequisites](#1-prerequisites)
- [2. Steps](#2-steps)
- [3. Verification](#3-verification)

## 1. Prerequisites

- A [development environment](./set-up-development-environment.md), including ffmpeg
- Thunder recordings (MP3 or WAV) in `audio/`, which is gitignored
- A MicroSD card of 32 GB or less

## 2. Steps

1. Preview the renaming without changing anything:

   ```bash
   npm run audio:prep:dry
   ```

2. Prepare the files. The script converts WAV to MP3, sorts the sources alphabetically and writes `0001.mp3`, `0002.mp3`, … to `audio/prepared/`:

   ```bash
   npm run audio:prep
   ```

3. Format the MicroSD card as FAT32.
4. Copy the files from `audio/prepared/` to the card's root directory **one at a time, in numerical order**.
5. Set `TRACK_COUNT` in `src/main.py` to the number of files.

> [!IMPORTANT]
>
> The DFPlayer numbers tracks by the order files were written to the card, not by their names. Copying `0002.mp3` before `0001.mp3` makes it track 1. Formatting the card first and copying in order keeps names and track numbers in step.

## 3. Verification

Put the card in the DFPlayer and play track 1 from the REPL (see [Test and Debug](./test-and-debug.md#1-mp3-player)). It should be the sound you expect as `0001.mp3`.

[← Back to How-To Guides](./README.md)
