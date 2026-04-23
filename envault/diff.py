"""Diff utility for comparing vault contents across environments or revisions."""

from dataclasses import dataclass
from typing import Dict, List, Optional


class DiffError(Exception):
    pass


@dataclass
class DiffEntry:
    key: str
    status: str  # 'added', 'removed', 'changed', 'unchanged'
    old_value: Optional[str] = None
    new_value: Optional[str] = None


def diff_vaults(
    old: Dict[str, str],
    new: Dict[str, str],
    show_unchanged: bool = False,
) -> List[DiffEntry]:
    """Compare two vault dicts and return a list of DiffEntry results."""
    entries: List[DiffEntry] = []
    all_keys = set(old) | set(new)

    for key in sorted(all_keys):
        if key in old and key not in new:
            entries.append(DiffEntry(key=key, status="removed", old_value=old[key]))
        elif key not in old and key in new:
            entries.append(DiffEntry(key=key, status="added", new_value=new[key]))
        elif old[key] != new[key]:
            entries.append(
                DiffEntry(key=key, status="changed", old_value=old[key], new_value=new[key])
            )
        elif show_unchanged:
            entries.append(
                DiffEntry(key=key, status="unchanged", old_value=old[key], new_value=new[key])
            )

    return entries


def format_diff(entries: List[DiffEntry], mask_values: bool = True) -> str:
    """Format diff entries into a human-readable string."""
    if not entries:
        return "No differences found."

    lines = []
    symbols = {"added": "+", "removed": "-", "changed": "~", "unchanged": " "}

    for entry in entries:
        symbol = symbols[entry.status]
        if entry.status == "added":
            val = "***" if mask_values else entry.new_value
            lines.append(f"{symbol} {entry.key}={val}")
        elif entry.status == "removed":
            val = "***" if mask_values else entry.old_value
            lines.append(f"{symbol} {entry.key}={val}")
        elif entry.status == "changed":
            old = "***" if mask_values else entry.old_value
            new = "***" if mask_values else entry.new_value
            lines.append(f"{symbol} {entry.key}: {old} -> {new}")
        else:
            val = "***" if mask_values else entry.old_value
            lines.append(f"{symbol} {entry.key}={val}")

    return "\n".join(lines)
