#!/usr/bin/env python3
"""Mirror voice-note debug artifacts into the workspace.

Use this when you have already pulled artifacts from the phone or server into
one or more local source folders, and you want a normalized copy inside
/workspace/AI_Voice_Note/debug_exports for easy inspection.

Typical usage:
  python scripts/mirror_debug_artifacts.py --source /tmp/voice_artifacts
  python scripts/mirror_debug_artifacts.py \
    --source /path/to/device_pull_1 \
    --source /path/to/server_dump \
    --dest /workspace/AI_Voice_Note/debug_exports

The script copies only voice/artifact files:
  - *.wav
  - *.m4a
  - *.json
  - *.txt
  - *.log

It preserves relative paths under each source and generates an INDEX.md
summarizing the mirrored files.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

ALLOWED_EXTS = {".wav", ".m4a", ".json", ".txt", ".log"}


@dataclass(frozen=True)
class MirroredFile:
    source_root: Path
    source_path: Path
    dest_path: Path
    size: int
    sha256: str


def sha256sum(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def iter_files(source: Path) -> Iterable[Path]:
    for p in source.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in ALLOWED_EXTS:
            continue
        # Skip Android/Gradle build outputs and VCS metadata if sources come from repo trees.
        if any(part in {".git", "build", "intermediates", ".gradle", "cache"} for part in p.parts):
            continue
        yield p


def mirror_one_source(source: Path, dest: Path) -> list[MirroredFile]:
    source = source.resolve()
    dest = dest.resolve()
    if not source.exists():
        raise FileNotFoundError(f"source not found: {source}")
    if not source.is_dir():
        raise NotADirectoryError(f"source is not a directory: {source}")

    mirrored: list[MirroredFile] = []
    source_name = source.name or "source"
    for src_file in iter_files(source):
        rel = src_file.relative_to(source)
        out = dest / source_name / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, out)
        mirrored.append(
            MirroredFile(
                source_root=source,
                source_path=src_file,
                dest_path=out,
                size=out.stat().st_size,
                sha256=sha256sum(out),
            )
        )
    return mirrored


def write_index(dest: Path, mirrored: list[MirroredFile]) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Voice Note debug exports",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "| Source | Size | SHA-256 | Mirrored Path |",
        "|---|---:|---|---|",
    ]
    for item in mirrored:
        lines.append(
            f"| `{item.source_path}` | {item.size} | `{item.sha256[:12]}…` | `{item.dest_path}` |"
        )
    if not mirrored:
        lines.append("")
        lines.append("No supported artifacts were found in the provided source folders.")
    (dest / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Mirror voice-note debug artifacts into the workspace")
    parser.add_argument(
        "--source",
        action="append",
        required=True,
        help="Source directory to mirror (repeatable)",
    )
    parser.add_argument(
        "--dest",
        default="/workspace/AI_Voice_Note/debug_exports",
        help="Destination workspace directory",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Delete destination directory contents before mirroring",
    )
    args = parser.parse_args()

    dest = Path(args.dest)
    if args.clear and dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)

    mirrored: list[MirroredFile] = []
    for src in args.source:
        mirrored.extend(mirror_one_source(Path(src), dest))

    write_index(dest, mirrored)
    print(f"Mirrored {len(mirrored)} file(s) into {dest}")
    print(dest / "INDEX.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
