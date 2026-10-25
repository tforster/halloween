#!/usr/bin/env python3
"""
Audio preparation script for DFPlayer Mini MP3 module.

This script:
1. Scans audio/ directory for MP3/WAV files
2. Converts WAV files to MP3 if needed
3. Renames files to DFPlayer naming convention (0001.mp3, 0002.mp3, etc.)
4. Creates audio/prepared/ directory ready for SD card

Usage:
    python devops/prepare_audio.py
    python devops/prepare_audio.py --dry-run  # Preview changes without modifying files
"""

import argparse
import os
import shutil
from pathlib import Path

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    print("Warning: pydub not installed. WAV conversion will be skipped.")
    print("Install with: pip install pydub")


def prepare_audio_files(source_dir: Path, output_dir: Path, dry_run: bool = False) -> None:
    """
    Prepare audio files for DFPlayer Mini module.
    
    Args:
        source_dir: Directory containing source audio files
        output_dir: Directory where prepared files will be placed
        dry_run: If True, show what would be done without modifying files
    """
    # Find all audio files
    audio_files = []
    for ext in ['*.mp3', '*.MP3', '*.wav', '*.WAV']:
        audio_files.extend(source_dir.glob(ext))
    
    if not audio_files:
        print(f"No audio files found in {source_dir}")
        return
    
    # Sort files alphabetically for consistent numbering
    audio_files.sort()
    
    print(f"\nFound {len(audio_files)} audio file(s):")
    for i, file in enumerate(audio_files, 1):
        print(f"  {i}. {file.name}")
    
    if dry_run:
        print("\n[DRY RUN] Would create the following files:")
    else:
        print(f"\nPreparing files for SD card in {output_dir}...")
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process each file
    for i, source_file in enumerate(audio_files, 1):
        target_name = f"{i:04d}.mp3"
        target_path = output_dir / target_name
        
        if source_file.suffix.lower() == '.mp3':
            # Copy MP3 files directly
            if dry_run:
                print(f"  {target_name} <- {source_file.name} (copy)")
            else:
                shutil.copy2(source_file, target_path)
                print(f"  ✓ {target_name} (copied from {source_file.name})")
        
        elif source_file.suffix.lower() == '.wav':
            # Convert WAV to MP3
            if not PYDUB_AVAILABLE:
                print(f"  ✗ {target_name} (skipped - pydub not installed)")
                continue
            
            if dry_run:
                print(f"  {target_name} <- {source_file.name} (convert WAV→MP3)")
            else:
                try:
                    audio = AudioSegment.from_wav(str(source_file))
                    audio.export(str(target_path), format='mp3', bitrate='192k')
                    print(f"  ✓ {target_name} (converted from {source_file.name})")
                except Exception as e:
                    print(f"  ✗ {target_name} (conversion failed: {e})")
    
    if not dry_run:
        print(f"\n✓ Complete! Copy {output_dir}/*.mp3 to your SD card root directory.")
        print("  IMPORTANT: Copy files in numerical order (0001, 0002, etc.)")


def main():
    parser = argparse.ArgumentParser(
        description="Prepare audio files for DFPlayer Mini MP3 module"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    parser.add_argument(
        '--source',
        type=Path,
        default=Path('audio'),
        help='Source directory containing audio files (default: audio/)'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('audio/prepared'),
        help='Output directory for prepared files (default: audio/prepared/)'
    )
    
    args = parser.parse_args()
    
    if not args.source.exists():
        print(f"Error: Source directory not found: {args.source}")
        return 1
    
    prepare_audio_files(args.source, args.output, args.dry_run)
    return 0


if __name__ == '__main__':
    exit(main())
