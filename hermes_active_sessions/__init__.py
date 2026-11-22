from __future__ import annotations

import argparse
import json
from typing import Any

from .active_sessions import active_records, format_records


def _command(raw_args: str = "", **kwargs: Any) -> str:
    rows = active_records()
    if raw_args.strip().lower() == "json":
        return json.dumps(rows, sort_keys=True)
    return format_records(rows)


def _setup(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--json", action="store_true", help="Print JSON")


def _cli(args: argparse.Namespace) -> int:
    print(_command("json" if args.json else ""))
    return 0


def register(ctx) -> None:
    ctx.register_command("sessions-active", _command, description="List active Hermes sessions", args_hint="[json]")
    ctx.register_cli_command("sessions-active", "List active Hermes sessions", _setup, _cli)
