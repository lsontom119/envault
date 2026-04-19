"""Audit log for vault operations."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


AUDIT_LOG_FILENAME = ".envault_audit.json"


def _get_audit_log_path(vault_dir: Optional[str] = None) -> Path:
    base = Path(vault_dir) if vault_dir else Path.home()
    return base / AUDIT_LOG_FILENAME


def record_event(action: str, key: Optional[str] = None, vault_dir: Optional[str] = None) -> None:
    """Append an audit event to the log file."""
    log_path = _get_audit_log_path(vault_dir)
    events = []
    if log_path.exists():
        try:
            with open(log_path, "r") as f:
                events = json.load(f)
        except (json.JSONDecodeError, OSError):
            events = []

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
    }
    if key is not None:
        event["key"] = key

    events.append(event)

    with open(log_path, "w") as f:
        json.dump(events, f, indent=2)


def get_events(vault_dir: Optional[str] = None) -> list:
    """Return all recorded audit events."""
    log_path = _get_audit_log_path(vault_dir)
    if not log_path.exists():
        return []
    with open(log_path, "r") as f:
        return json.load(f)


def clear_events(vault_dir: Optional[str] = None) -> None:
    """Clear the audit log."""
    log_path = _get_audit_log_path(vault_dir)
    if log_path.exists():
        os.remove(log_path)
