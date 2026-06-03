#!/usr/bin/env python3
"""Pull debug artifacts from an Android device into the workspace mirror.

This script expects the app to export artifacts into its app-specific external
files directory, usually:
  /sdcard/Android/data/<package>/files/debug_exports

Usage:
  python scripts/pull_debug_artifacts_adb.py \
    --package com.hermes.aivoiceassistant \
    --dest /workspace/AI_Voice_Note/debug_exports \
    --clear

It will:
  1) verify adb is available
  2) check the device export directory
  3) adb pull the folder into a local workspace mirror
  4) print the final local path
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, text=True, capture_output=True, check=check)


def main() -> int:
    parser = argparse.ArgumentParser(description="Pull debug artifacts from an Android device")
    parser.add_argument("--package", required=True, help="Android package name")
    parser.add_argument("--dest", default="/workspace/AI_Voice_Note/debug_exports", help="Local workspace destination")
    parser.add_argument("--clear", action="store_true", help="Clear destination before pulling")
    parser.add_argument("--device-dir", default=None, help="Override device export dir")
    args = parser.parse_args()

    if shutil.which("adb") is None:
        print("adb not found in PATH", file=sys.stderr)
        return 2

    device_dir = args.device_dir or f"/sdcard/Android/data/{args.package}/files/debug_exports"
    dest = Path(args.dest).resolve()
    if args.clear and dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)

    # Make sure adb sees a device.
    devices = run(["adb", "devices"]).stdout.strip().splitlines()
    if len(devices) <= 1:
        print("No adb device detected", file=sys.stderr)
        return 3

    # Verify directory exists on device.
    exists_cmd = ["adb", "shell", "sh", "-c", f'test -d "{device_dir}" && echo YES || echo NO']
    exists = run(exists_cmd).stdout.strip().splitlines()[-1]
    if exists != "YES":
        print(f"Device debug export directory not found: {device_dir}", file=sys.stderr)
        return 4

    target = dest / args.package
    if target.exists():
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)

    pull = run(["adb", "pull", device_dir, str(target)])
    if pull.returncode != 0:
        print(pull.stdout)
        print(pull.stderr, file=sys.stderr)
        return pull.returncode

    index = target / "INDEX.md"
    print(f"Pulled debug artifacts into: {target}")
    if index.exists():
        print(f"Index: {index}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
