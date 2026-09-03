#!/usr/bin/env python3
"""
Extend every subtitle in a CapCut/JianYing draft so it lasts until the next
subtitle starts (no gaps between captions).

CapCut stores each project as JSON (draft_content.json, sometimes
draft_info.json on older versions) inside the draft folder. Subtitles live
on tracks with type "text". Each segment has a target_timerange with
"start" and "duration" in microseconds. Batch-extending is just:

    duration[i] = start[i+1] - start[i]

for every segment except the last one on the track.

Usage:
    python capcut_extend_subtitles.py /path/to/draft_folder
    python capcut_extend_subtitles.py /path/to/draft_folder --dry-run
    python capcut_extend_subtitles.py /path/to/draft_folder --track-index 0
    python capcut_extend_subtitles.py /path/to/draft_folder --tail-seconds 1.5

By default:
  - every "text" track found is processed
  - a segment is only ever lengthened, never shortened (overlaps are left
    untouched and reported, not silently trimmed)
  - the last segment on each track is left as-is unless --tail-seconds is
    given
  - a .bak copy of the original file is written before overwriting
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

DRAFT_FILENAMES = ("draft_content.json", "draft_info.json")

MICROSECONDS_PER_SECOND = 1_000_000


def find_draft_file(draft_path: Path) -> Path:
    if draft_path.is_file():
        return draft_path
    for name in DRAFT_FILENAMES:
        candidate = draft_path / name
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        f"No {DRAFT_FILENAMES} found in {draft_path}. "
        "Pass the draft folder (e.g. .../CapCut Drafts/<project name>) "
        "or the draft_content.json file directly."
    )


def find_text_tracks(data: dict):
    tracks = data.get("tracks", [])
    return [
        (index, track)
        for index, track in enumerate(tracks)
        if track.get("type") == "text"
    ]


def extend_track_segments(segments: list, tail_seconds: float, dry_run: bool):
    """Extend each segment's target_timerange.duration to the start of the
    next segment. Returns (extended_count, overlap_count, added_us)."""

    ordered = sorted(
        (s for s in segments if "target_timerange" in s),
        key=lambda s: s["target_timerange"]["start"],
    )

    extended = 0
    overlaps = 0
    added_us = 0

    for i, seg in enumerate(ordered):
        tr = seg["target_timerange"]
        start = tr["start"]
        duration = tr["duration"]
        current_end = start + duration

        if i + 1 < len(ordered):
            next_start = ordered[i + 1]["target_timerange"]["start"]
            if next_start > current_end:
                new_duration = next_start - start
                added_us += new_duration - duration
                if not dry_run:
                    tr["duration"] = new_duration
                extended += 1
            elif next_start < current_end:
                overlaps += 1
        else:
            if tail_seconds > 0:
                new_duration = duration + int(tail_seconds * MICROSECONDS_PER_SECOND)
                added_us += new_duration - duration
                if not dry_run:
                    tr["duration"] = new_duration
                extended += 1

    return extended, overlaps, added_us


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("draft_path", type=Path, help="CapCut draft folder or draft_content.json path")
    parser.add_argument("--track-index", type=int, default=None, help="Only process this text track index (see --list-tracks)")
    parser.add_argument("--tail-seconds", type=float, default=0.0, help="Extend the last subtitle on each track by this many seconds (default: leave it untouched)")
    parser.add_argument("--dry-run", action="store_true", help="Report what would change without writing anything")
    parser.add_argument("--list-tracks", action="store_true", help="List text tracks found and exit")
    parser.add_argument("--no-backup", action="store_true", help="Skip writing a .bak file before overwriting")
    args = parser.parse_args()

    try:
        draft_file = find_draft_file(args.draft_path)
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(draft_file.read_text(encoding="utf-8"))
    text_tracks = find_text_tracks(data)

    if not text_tracks:
        print("No text tracks found in this draft.", file=sys.stderr)
        sys.exit(1)

    if args.list_tracks:
        for index, track in text_tracks:
            print(f"track {index}: {len(track.get('segments', []))} subtitle segment(s)")
        return

    if args.track_index is not None:
        text_tracks = [(i, t) for i, t in text_tracks if i == args.track_index]
        if not text_tracks:
            print(f"error: no text track with index {args.track_index}", file=sys.stderr)
            sys.exit(1)

    total_extended = 0
    total_overlaps = 0
    total_added_us = 0

    for index, track in text_tracks:
        extended, overlaps, added_us = extend_track_segments(
            track.get("segments", []), args.tail_seconds, args.dry_run
        )
        total_extended += extended
        total_overlaps += overlaps
        total_added_us += added_us
        print(
            f"track {index}: extended {extended} segment(s), "
            f"{overlaps} already-overlapping segment(s) left untouched, "
            f"+{added_us / MICROSECONDS_PER_SECOND:.2f}s added"
        )

    print(
        f"\nTOTAL: {total_extended} extended, {total_overlaps} overlaps skipped, "
        f"+{total_added_us / MICROSECONDS_PER_SECOND:.2f}s added"
    )

    if args.dry_run:
        print("\nDry run: no file written.")
        return

    if total_extended == 0:
        print("\nNothing to write.")
        return

    if not args.no_backup:
        backup_path = draft_file.with_suffix(draft_file.suffix + ".bak")
        if not backup_path.exists():
            shutil.copy2(draft_file, backup_path)
            print(f"Backup written to {backup_path}")

    draft_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    print(f"Updated {draft_file}")
    print("Close and reopen the project in CapCut to see the change (do this while CapCut is not running on the project, to avoid it overwriting your edit).")


if __name__ == "__main__":
    main()
