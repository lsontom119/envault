"""Export vault contents to shell-compatible formats."""

from typing import Dict


def to_export_script(data: Dict[str, str]) -> str:
    """Return a shell export script string for the given env vars."""
    lines = ["#!/bin/sh"]
    for key, value in sorted(data.items()):
        escaped = value.replace('"', '\\"')
        lines.append(f'export {key}="{escaped}"')
    return "\n".join(lines) + "\n"


def to_dotenv(data: Dict[str, str]) -> str:
    """Return a .env file string for the given env vars."""
    lines = []
    for key, value in sorted(data.items()):
        escaped = value.replace('"', '\\"')
        lines.append(f'{key}="{escaped}"')
    return "\n".join(lines) + "\n"


def to_dict(data: Dict[str, str]) -> Dict[str, str]:
    """Return a plain dict copy of the vault data."""
    return dict(data)
