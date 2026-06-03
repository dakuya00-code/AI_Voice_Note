#!/usr/bin/env python3
"""Copy server-side voice artifacts into the workspace mirror.

This script is intentionally generic: you point it at the server root that
contains voice-note artifacts (recordings, transcripts, logs), and it copies
supported files into /workspace/AI_Voice_Note/debug_exports.

Example:
  python scripts/sync_server_debug_artifacts.py \
    --source /workspace/server_data \
    --dest /workspace/AI_Voice_Note/debug_exports

Supported file extensions:
  .wav, .m4a, .json, .txt, .log

The copy preserves relative paths under the source root and writes an INDEX.md
summary into the destination.
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
class CopiedFile:
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
        if any(part in {".git", "build", "intermediates", ".gradle", "cache"} for part in p.parts):
            continue
        yield p


def copy_source(source: Path, dest: Path) -> list[CopiedFile]:
    source = source.resolve()
    dest = dest.resolve()
    if not source.exists():
        raise FileNotFoundError(f"source not found: {source}")
    if not source.is_dir():
        raise NotADirectoryError(f"source is not a directory: {source}")

    copied: list[CopiedFile] = []
    root_name = source.name or "server"
    for src_file in iter_files(source):
        rel = src_file.relative_to(source)
        out = dest / root_name / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, out)
        copied.append(CopiedFile(src_file, out, out.stat().st_size, sha256sum(out)))
    return copied


def write_index(dest: Path, copied: list[CopiedFile], source: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Server debug exports",
        "",
        f"Source: `{source}`",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "| Source | Size | SHA-256 | Mirrored Path |",
        "|---|---:|---|---|",
    ]
    for item in copied:
        lines.append(f"| `{item.source_path}` | {item.size} | `{item.sha256[:12]}…` | `{item.dest_path}` |")
    if not copied:
        lines.append("")
        lines.append("No supported artifacts were found.")
    (dest / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Copy server-side voice artifacts into the workspace")
    parser.add_argument("--source", required=True, help="Server-side artifact root")
    parser.add_argument("--dest", default="/workspace/AI_Voice_Note/debug_exports", help="Local workspace destination")
    parser.add_argument("--clear", action="store_true", help="Clear destination before copying")
    args = parser.parse_args()

    source = Path(args.source)
    dest = Path(args.dest)
    if args.clear and dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)

    copied = copy_source(source, dest)
    write_index(dest, copied, source)
    print(f"Copied {len(copied)} file(s) into {dest}")
    print(dest / "INDEX.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
