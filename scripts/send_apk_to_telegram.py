#!/usr/bin/env python3
"""Send the latest APK to Telegram using bot token + chat id from env or JSON.

Usage examples:
  TELEGRAM_BOT_TOKEN=... TELEGRAM_CHAT_ID=... \
    python scripts/send_apk_to_telegram.py app/build/outputs/apk/debug/app-debug.apk

  python scripts/send_apk_to_telegram.py \
    --cred-file /path/to/telegram.json \
    app/build/outputs/apk/debug/app-debug.apk

Credential file JSON keys accepted:
  - telegram_bot_token
  - telegram_chat_id
  - TELEGRAM_BOT_TOKEN
  - TELEGRAM_CHAT_ID
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path


def load_creds(cred_file: Path | None) -> tuple[str | None, str | None]:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if cred_file and cred_file.exists():
        data = json.loads(cred_file.read_text(encoding="utf-8"))
        token = token or data.get("telegram_bot_token") or data.get("TELEGRAM_BOT_TOKEN") or data.get("bot_token")
        chat_id = chat_id or data.get("telegram_chat_id") or data.get("TELEGRAM_CHAT_ID") or data.get("chat_id")

    return token, chat_id


def send_document(token: str, chat_id: str, apk: Path, caption: str | None = None) -> dict:
    boundary = "----HermesTelegramBoundarySendAPK"
    crlf = "\r\n"
    parts: list[bytes] = []

    def add_field(name: str, value: str) -> None:
        parts.append(
            f'--{boundary}{crlf}Content-Disposition: form-data; name="{name}"{crlf}{crlf}{value}{crlf}'.encode("utf-8")
        )

    def add_file(name: str, filename: str, content: bytes, content_type: str = "application/vnd.android.package-archive") -> None:
        parts.append(
            f'--{boundary}{crlf}Content-Disposition: form-data; name="{name}"; filename="{filename}"{crlf}Content-Type: {content_type}{crlf}{crlf}'.encode("utf-8")
        )
        parts.append(content)
        parts.append(crlf.encode("utf-8"))

    add_field("chat_id", chat_id)
    if caption:
        add_field("caption", caption)
    add_file("document", apk.name, apk.read_bytes())
    body = b"".join(parts) + f"--{boundary}--{crlf}".encode("utf-8")

    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendDocument",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Send APK to Telegram")
    parser.add_argument("apk", nargs="?", default="app/build/outputs/apk/debug/app-debug.apk", help="Path to APK file")
    parser.add_argument("--cred-file", type=Path, default=None, help="Optional JSON file containing Telegram creds")
    parser.add_argument("--caption", default="최신 AI Voice Note APK", help="Telegram caption")
    args = parser.parse_args()

    apk = Path(args.apk)
    if not apk.exists():
        print(f"APK not found: {apk}", file=sys.stderr)
        return 2

    token, chat_id = load_creds(args.cred_file)
    if not token or not chat_id:
        print("Missing TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID (env or cred file)", file=sys.stderr)
        return 3

    result = send_document(token, chat_id, apk, args.caption)
    print(json.dumps({
        "ok": result.get("ok"),
        "message_id": result.get("result", {}).get("message_id"),
        "chat_id": result.get("result", {}).get("chat", {}).get("id"),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
