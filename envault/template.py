"""Template rendering: substitute vault variables into template strings/files."""

import re
from typing import Dict, Optional


class TemplateError(Exception):
    """Raised when template rendering fails."""


_PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")


def render_string(template: str, variables: Dict[str, str], strict: bool = True) -> str:
    """Replace {{VAR_NAME}} placeholders in *template* with values from *variables*.

    Args:
        template: The template string containing ``{{ VAR }}`` placeholders.
        variables: Mapping of variable names to their values.
        strict: If True, raise :class:`TemplateError` for unknown placeholders.
                If False, leave them unchanged.

    Returns:
        The rendered string.
    """
    missing = []

    def _replace(match: re.Match) -> str:
        key = match.group(1)
        if key in variables:
            return variables[key]
        if strict:
            missing.append(key)
            return match.group(0)
        return match.group(0)

    result = _PLACEHOLDER_RE.sub(_replace, template)

    if missing:
        raise TemplateError(
            f"Template references undefined variable(s): {', '.join(sorted(missing))}"
        )

    return result


def render_file(src_path: str, variables: Dict[str, str], strict: bool = True) -> str:
    """Read a template file and render it with *variables*.

    Args:
        src_path: Path to the template file.
        variables: Mapping of variable names to their values.
        strict: Forwarded to :func:`render_string`.

    Returns:
        The rendered content as a string.
    """
    try:
        with open(src_path, "r", encoding="utf-8") as fh:
            content = fh.read()
    except OSError as exc:
        raise TemplateError(f"Cannot read template file '{src_path}': {exc}") from exc

    return render_string(content, variables, strict=strict)


def list_placeholders(template: str) -> list:
    """Return a sorted list of unique placeholder names found in *template*."""
    return sorted(set(_PLACEHOLDER_RE.findall(template)))
