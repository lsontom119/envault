"""Track change history for vault variables."""

import json
import os
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional

HISTORY_FILENAME = ".envault_history.json"
MAX_HISTORY_ENTRIES = 500


class HistoryError(Exception):
    pass


@dataclass
class HistoryEntry:
    timestamp: float
    action: str        # 'set' | 'delete' | 'rotate' | 'import'
    key: Optional[str]
    vault_path: str

    def formatted_time(self) -> str:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.timestamp))


def _get_history_path(vault_path: str) -> Path:
    vault_dir = Path(vault_path).parent
    return vault_dir / HISTORY_FILENAME


def record_change(vault_path: str, action: str, key: Optional[str] = None) -> None:
    """Append a change entry to the history log."""
    history_path = _get_history_path(vault_path)
    entries = _load_raw(history_path)
    entries.append({
        "timestamp": time.time(),
        "action": action,
        "key": key,
        "vault_path": vault_path,
    })
    if len(entries) > MAX_HISTORY_ENTRIES:
        entries = entries[-MAX_HISTORY_ENTRIES:]
    history_path.write_text(json.dumps(entries, indent=2))


def get_history(vault_path: str, limit: int = 50) -> List[HistoryEntry]:
    """Return recent history entries, newest first."""
    history_path = _get_history_path(vault_path)
    raw = _load_raw(history_path)
    entries = [
        HistoryEntry(
            timestamp=r["timestamp"],
            action=r["action"],
            key=r.get("key"),
            vault_path=r["vault_path"],
        )
        for r in raw
    ]
    return list(reversed(entries))[:limit]


def clear_history(vault_path: str) -> None:
    """Delete the history log."""
    history_path = _get_history_path(vault_path)
    if history_path.exists():
        history_path.unlink()


def _load_raw(history_path: Path) -> list:
    if not history_path.exists():
        return []
    try:
        return json.loads(history_path.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        raise HistoryError(f"Failed to read history: {exc}") from exc
