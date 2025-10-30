#!/usr/bin/env python3
"""
SRT Timestamp Prepender & Transcript Generator
Adds absolute timestamps to SRT subtitle files based on recording start time,
and generates a clean text transcript without SRT numbering or timestamp lines.
This file is included just for easy access when needed.

Usage:
    python srt_timestamp.py path/to/file.srt --timestamp "14:23:23"
"""

import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path

def parse_srt_timestamp(timestamp_str):
    """Parse SRT timestamp format (HH:MM:SS,mmm) to timedelta."""
    time_part, ms_part = timestamp_str.split(',')
    h, m, s = map(int, time_part.split(':'))
    ms = int(ms_part)
    return timedelta(hours=h, minutes=m, seconds=s, milliseconds=ms)

def parse_base_timestamp(timestamp_str):
    """Parse base timestamp (HH:MM:SS) to datetime object."""
    try:
        return datetime.strptime(timestamp_str, "%H:%M:%S")
    except ValueError:
        raise ValueError(f"Invalid timestamp format. Expected HH:MM:SS, got: {timestamp_str}")

def format_minute_timestamp(dt):
    """Format datetime as [HH:MM]."""
    return f"[{dt.strftime('%H:%M')}]"

def process_srt_file(input_path, base_timestamp):
    """Process SRT file, add timestamps, and produce cleaned transcript."""
    input_path = Path(input_path)
    output_srt_path = input_path.parent / f"{input_path.stem}_ondertiteling{input_path.suffix}"
    output_txt_path = input_path.parent / f"{input_path.stem}_tekstbestand_met_timestamp.txt"

    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split into subtitle blocks (separated by double newlines)
    blocks = content.strip().split('\n\n')

    last_minute_added = None
    processed_blocks = []
    transcript_lines = []

    for block in blocks:
        lines = block.split('\n')
        if len(lines) < 3:
            continue  # Skip malformed entries

        subtitle_num = lines[0]
        timestamp_line = lines[1]
        subtitle_text = lines[2:]

        # Extract start timestamp (before -->)
        match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->', timestamp_line)
        if not match:
            continue  # Skip invalid timestamp lines

        start_timestamp_str = match.group(1)
        subtitle_offset = parse_srt_timestamp(start_timestamp_str)
        absolute_time = base_timestamp + subtitle_offset
        current_minute = absolute_time.strftime('%H:%M')

        # Check if we need to prepend timestamp to this block
        new_minute_started = current_minute != last_minute_added
        if new_minute_started:
            minute_tag = format_minute_timestamp(absolute_time)
            subtitle_text[0] = f"{minute_tag} {subtitle_text[0]}"
            last_minute_added = current_minute

        # Reconstruct processed SRT block
        new_block = '\n'.join([subtitle_num, timestamp_line] + subtitle_text)
        processed_blocks.append(new_block)

        # Generate plain transcript lines
        if new_minute_started:
            transcript_lines.append(format_minute_timestamp(absolute_time))  # separate line for timestamp
        for line in subtitle_text:
            # Strip possible minute tag from text for cleaner output
            cleaned_line = re.sub(r'^\[\d{2}:\d{2}\]\s*', '', line)
            transcript_lines.append(cleaned_line)

    # Write timestamped SRT output
    output_content = '\n\n'.join(processed_blocks)
    if not output_content.endswith('\n'):
        output_content += '\n'

    with open(output_srt_path, 'w', encoding='utf-8') as f:
        f.write(output_content)

    # Write clean TXT transcript
    with open(output_txt_path, 'w', encoding='utf-8') as f:
        for line in transcript_lines:
            f.write(line.strip() + '\n')

    return output_srt_path, output_txt_path

def main():
    parser = argparse.ArgumentParser(
        description='Add absolute timestamps to SRT files and create a clean transcript.'
    )
    parser.add_argument('srt_file', help='Path to the SRT file')
    parser.add_argument(
        '--timestamp',
        required=True,
        help='Recording start time in HH:MM:SS format (e.g., "14:23:23")'
    )

    args = parser.parse_args()

    # Parse base timestamp
    try:
        base_time = parse_base_timestamp(args.timestamp)
    except ValueError as e:
        print(f"Error: {e}")
        return 1

    # Verify file exists
    if not Path(args.srt_file).exists():
        print(f"Error: File not found: {args.srt_file}")
        return 1

    # Process file
    try:
        srt_path, txt_path = process_srt_file(args.srt_file, base_time)
        print("✓ Successfully processed SRT file")
        print(f"✓ Timestamped SRT saved to: {srt_path}")
        print(f"✓ Clean transcript saved to: {txt_path}")
        return 0
    except Exception as e:
        print(f"Error processing file: {e}")
        return 1

if __name__ == '__main__':
    exit(main())
