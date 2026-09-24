#!/usr/bin/env python3
"""PreToolUse hook: block Bash commands that would delete/overwrite
data/skillgrowth.db while the app container is running.

See CLAUDE.md's "Never delete data/skillgrowth.db while the container is
running" section for why: the app holds the SQLite file open via a
bind mount, and deleting/truncating it out from under a live container has
corrupted the running instance before ("no such table" errors mid-session).
"""

import json
import re
import subprocess
import sys

DB_PATH_RE = r"(?:\./)?data/skillgrowth\.db"

DESTRUCTIVE_PATTERNS = [
    re.compile(rf"\brm\b[^|;&]*{DB_PATH_RE}"),
    re.compile(rf"\btruncate\b[^|;&]*{DB_PATH_RE}"),
    re.compile(rf"\bmv\b[^|;&]*{DB_PATH_RE}"),
    re.compile(rf">>?\|?\s*{DB_PATH_RE}"),
    re.compile(r"\brm\b\s+(-\w*r\w*f\w*|-\w*f\w*r\w*)\s+(?:\./)?data(?:/|\s|$)"),
]


def repo_root() -> str | None:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def app_container_running(root: str) -> bool:
    try:
        result = subprocess.run(
            ["docker", "compose", "ps", "--status", "running", "--services"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
    return "app" in result.stdout.split()


def main() -> int:
    payload = json.load(sys.stdin)
    command = payload.get("tool_input", {}).get("command", "")

    if not any(pattern.search(command) for pattern in DESTRUCTIVE_PATTERNS):
        return 0

    root = repo_root()
    if root is None or not app_container_running(root):
        return 0

    print(
        "Blocked: this command would delete/overwrite data/skillgrowth.db "
        "while the app container is running, which has corrupted the "
        "running instance before. Stop the container first "
        "(`docker compose stop`), or don't touch the file while it's up. "
        "See CLAUDE.md.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
