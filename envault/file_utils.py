"""Utility helpers for reading and writing .env-style files."""

from pathlib import Path
from typing import Dict


def parse_dotenv(text: str) -> Dict[str, str]:
    """Parse a .env-formatted string into a dict.

    Skips blank lines and comments. Strips optional surrounding quotes.
    """
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        result[key] = value
    return result


def read_dotenv_file(path: Path) -> Dict[str, str]:
    """Read and parse a .env file from disk."""
    return parse_dotenv(path.read_text(encoding="utf-8"))


def write_dotenv_file(path: Path, data: Dict[str, str]) -> None:
    """Write a dict of key/value pairs as a .env file."""
    lines = []
    for key, value in sorted(data.items()):
        escaped = value.replace('"', '\\"')
        lines.append(f'{key}="{escaped}"')
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def merge_dotenv(base: Dict[str, str], override: Dict[str, str]) -> Dict[str, str]:
    """Merge two env dicts; override values take precedence."""
    merged = dict(base)
    merged.update(override)
    return merged
