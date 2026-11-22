from __future__ import annotations

import json

from hermes_active_sessions.active_sessions import format_records


def test_active_session_format():
    text = format_records([{
        "session_id": "20260724_235551_10afa9",
        "title": "CC-chat-dev",
        "surface": "cli",
        "state": "idle",
        "model": "gpt-5.6-sol",
        "duration_seconds": 2,
        "busy_seconds": 0,
        "idle_seconds": 0,
        "background_tasks": 0,
        "background_processes": 0,
        "background_subagents": 0,
        "last_update_seconds": 0,
    }])
    assert 'Hermes Active Sessions' in text
    assert 'Busy: ∑ 0s' in text
    assert '"CC-chat-dev"' in text


def test_empty_active_session_format():
    assert format_records([]) == 'Hermes Active Sessions\n\nNo active sessions.'
