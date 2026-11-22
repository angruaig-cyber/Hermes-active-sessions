from __future__ import annotations

import json
import os
import tempfile
import threading
from pathlib import Path
from typing import Any

_LOCK = threading.RLock()
_SCHEMA = 1


def _home() -> Path:
    return Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))


def _path() -> Path:
    return _home() / "busytime.json"


def _load() -> dict[str, Any]:
    try:
        data = json.loads(_path().read_text(encoding="utf-8"))
        return data if isinstance(data, dict) and isinstance(data.get("sessions", {}), dict) else {"schema": _SCHEMA, "sessions": {}}
    except (OSError, ValueError, TypeError):
        return {"schema": _SCHEMA, "sessions": {}}


def _save(data: dict[str, Any]) -> None:
    target = _path()
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix="busytime-", suffix=".json", dir=str(target.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(data, fh, indent=2, sort_keys=True)
            fh.write("\n")
        os.replace(name, target)
    finally:
        try:
            os.unlink(name)
        except FileNotFoundError:
            pass


def get(session_id: str) -> dict[str, Any]:
    with _LOCK:
        row = _load()["sessions"].get(session_id, {})
        return {
            "session_id": session_id,
            "completed_seconds": float(row.get("completed_seconds", 0.0)),
            "turns": int(row.get("turns", 0)),
        }


def add(session_id: str, seconds: float) -> dict[str, Any]:
    seconds = max(0.0, float(seconds))
    with _LOCK:
        data = _load()
        row = data["sessions"].setdefault(session_id, {})
        row["completed_seconds"] = float(row.get("completed_seconds", 0.0)) + seconds
        row["turns"] = int(row.get("turns", 0)) + 1
        data["schema"] = _SCHEMA
        _save(data)
        return get(session_id)


def format_seconds(seconds: float) -> str:
    total = max(0, int(seconds))
    hours, rem = divmod(total, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours}h {minutes:02d}m {secs:02d}s"
    if minutes:
        return f"{minutes}m {secs:02d}s"
    return f"{secs}s"
