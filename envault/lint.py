"""Lint and validate environment variable names and values in the vault.

Provides checks for common issues such as:
- Invalid variable name characters
- Empty values
- Suspicious patterns (e.g. placeholder text, very long values)
- Duplicate keys (case-insensitive conflicts)
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List

from envault.vault import load_vault

# Valid POSIX env var name: letters, digits, underscores; must not start with digit
_VALID_NAME_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')

# Patterns that suggest a value is still a placeholder
_PLACEHOLDER_PATTERNS = [
    re.compile(r'<[^>]+>'),          # <YOUR_VALUE>
    re.compile(r'\$\{[^}]+\}'),      # ${PLACEHOLDER}
    re.compile(r'CHANGEME', re.I),
    re.compile(r'TODO', re.I),
    re.compile(r'FIXME', re.I),
    re.compile(r'^your[-_]', re.I),
]

_MAX_VALUE_LENGTH = 4096


class LintError(Exception):
    """Raised when linting cannot be performed (e.g. vault not found)."""


@dataclass
class LintIssue:
    """A single linting issue found for a variable."""

    key: str
    severity: str   # 'error' | 'warning'
    message: str

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.key}: {self.message}"


@dataclass
class LintResult:
    """Aggregated result of a lint run."""

    issues: List[LintIssue] = field(default_factory=list)

    @property
    def errors(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == 'error']

    @property
    def warnings(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == 'warning']

    @property
    def passed(self) -> bool:
        """True only when there are no errors (warnings are acceptable)."""
        return len(self.errors) == 0


def _check_name(key: str) -> List[LintIssue]:
    """Validate the variable name."""
    issues: List[LintIssue] = []
    if not _VALID_NAME_RE.match(key):
        issues.append(LintIssue(
            key=key,
            severity='error',
            message=(
                "Invalid variable name. Names must start with a letter or "
                "underscore and contain only letters, digits, and underscores."
            ),
        ))
    return issues


def _check_value(key: str, value: str) -> List[LintIssue]:
    """Validate the variable value."""
    issues: List[LintIssue] = []

    if value == '':
        issues.append(LintIssue(
            key=key,
            severity='warning',
            message='Value is empty.',
        ))
        return issues  # no further checks make sense on empty string

    for pattern in _PLACEHOLDER_PATTERNS:
        if pattern.search(value):
            issues.append(LintIssue(
                key=key,
                severity='warning',
                message=f'Value looks like a placeholder (matched pattern: {pattern.pattern!r}).',
            ))
            break  # one placeholder warning per key is enough

    if len(value) > _MAX_VALUE_LENGTH:
        issues.append(LintIssue(
            key=key,
            severity='warning',
            message=f'Value is very long ({len(value)} characters > {_MAX_VALUE_LENGTH}).',
        ))

    return issues


def _check_case_conflicts(variables: Dict[str, str]) -> List[LintIssue]:
    """Detect keys that differ only in case (can cause cross-platform issues)."""
    issues: List[LintIssue] = []
    seen: Dict[str, str] = {}  # lower -> original
    for key in variables:
        lower = key.lower()
        if lower in seen:
            issues.append(LintIssue(
                key=key,
                severity='warning',
                message=(
                    f'Case-insensitive conflict with existing key "{seen[lower]}". '
                    'This may cause problems on case-insensitive systems.'
                ),
            ))
        else:
            seen[lower] = key
    return issues


def lint_vault(password: str, vault_dir: str | None = None) -> LintResult:
    """Load the vault and run all lint checks.

    Args:
        password: Vault decryption password.
        vault_dir: Optional override for the vault directory (used in tests).

    Returns:
        A :class:`LintResult` containing all discovered issues.

    Raises:
        LintError: If the vault cannot be loaded.
    """
    try:
        variables = load_vault(password, vault_dir=vault_dir)
    except Exception as exc:  # noqa: BLE001
        raise LintError(f'Could not load vault: {exc}') from exc

    result = LintResult()

    for key, value in variables.items():
        result.issues.extend(_check_name(key))
        result.issues.extend(_check_value(key, value))

    result.issues.extend(_check_case_conflicts(variables))

    return result
