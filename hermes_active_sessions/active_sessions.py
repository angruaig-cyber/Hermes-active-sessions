from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from . import store


def _home() -> Path:
    return Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))


def _entries() -> list[dict[str, Any]]:
    path = _home() / "runtime" / "active_sessions.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        rows = data.get("entries", data) if isinstance(data, (dict, list)) else []
        return [row for row in rows if isinstance(row, dict)]
    except (OSError, ValueError, TypeError):
        return []


def _age(value: Any) -> int:
    try:
        return max(0, int(time.time() - float(value)))
    except (TypeError, ValueError):
        return 0


def _duration(seconds: float) -> str:
    return store.format_seconds(seconds)


def _record(row: dict[str, Any]) -> dict[str, Any]:
    session_id = str(row.get("session_id") or "unknown")
    meta = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
    started = row.get("started_at")
    updated = row.get("updated_at") or started
    busy = store.get(session_id)
    state = str(meta.get("state") or "idle")
    if state not in {"idle", "working", "busy", "queued", "waiting"}:
        state = "idle"
    return {
        "session_id": session_id,
        "title": str(meta.get("title") or ""),
        "surface": str(row.get("surface") or meta.get("surface") or "unknown"),
        "state": state,
        "model": str(meta.get("model") or "unknown"),
        "duration_seconds": _age(started),
        "busy_seconds": float(busy.get("completed_seconds", 0.0)),
        "idle_seconds": _age(updated) if state == "idle" else 0,
        "background_tasks": int(meta.get("background_tasks", 0) or 0),
        "background_processes": int(meta.get("background_processes", 0) or 0),
        "background_subagents": int(meta.get("background_subagents", 0) or 0),
        "last_update_seconds": _age(updated),
    }


def active_records() -> list[dict[str, Any]]:
    return sorted((_record(row) for row in _entries()), key=lambda row: row["session_id"])


def format_records(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "Hermes Active Sessions\n\nNo active sessions."
    lines = ["Hermes Active Sessions", ""]
    for index, row in enumerate(rows, 1):
        title = f'  "{row["title"]}"' if row["title"] else ""
        lines.extend([
            f'{index}. {row["session_id"]}{title}',
            f'   Surface: {row["surface"]} | State: {row["state"]}',
            f'   Model: {row["model"]} | Duration: {_duration(row["duration_seconds"])} | Busy: ∑ {_duration(row["busy_seconds"])}',
            f'   Idle: {_duration(row["idle_seconds"])} | BG tasks: {row["background_tasks"]} | BG procs: {row["background_processes"]} | BG subagents: {row["background_subagents"]}',
            f'   Last update: {_duration(row["last_update_seconds"])} ago',
        ])
    return "\n".join(lines)
