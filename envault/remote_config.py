"""Locate and manage the per-project remote configuration file."""

import os
from pathlib import Path

REMOTE_CONFIG_FILENAME = ".envault-remote.json"


def get_remote_config_path(project_dir: str = None) -> str:
    """Return the path to the remote config file for the given (or current) directory."""
    base = Path(project_dir) if project_dir else Path.cwd()
    return str(base / REMOTE_CONFIG_FILENAME)


def remote_config_exists(project_dir: str = None) -> bool:
    return os.path.isfile(get_remote_config_path(project_dir))
