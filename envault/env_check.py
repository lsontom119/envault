"""Environment variable health checks for envault."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envault.vault import load_vault


class EnvCheckError(Exception):
    """Raised when an environment check operation fails."""


@dataclass
class CheckResult:
    key: str
    passed: bool
    message: str


@dataclass
class CheckReport:
    results: List[CheckResult] = field(default_factory=list)

    @property
    def passed(self) -> List[CheckResult]:
        return [r for r in self.results if r.passed]

    @property
    def failed(self) -> List[CheckResult]:
        return [r for r in self.results if not r.passed]

    @property
    def ok(self) -> bool:
        return len(self.failed) == 0


def check_required(vault_data: Dict[str, str], required_keys: List[str]) -> List[CheckResult]:
    """Check that all required keys are present and non-empty."""
    results = []
    for key in required_keys:
        if key not in vault_data or vault_data[key].strip() == "":
            results.append(CheckResult(key=key, passed=False, message=f"Required key '{key}' is missing or empty"))
        else:
            results.append(CheckResult(key=key, passed=True, message=f"'{key}' is present"))
    return results


def check_pattern(vault_data: Dict[str, str], key: str, pattern: str) -> CheckResult:
    """Check that a key's value matches the given regex pattern."""
    value = vault_data.get(key)
    if value is None:
        return CheckResult(key=key, passed=False, message=f"Key '{key}' not found in vault")
    if re.fullmatch(pattern, value):
        return CheckResult(key=key, passed=True, message=f"'{key}' matches pattern")
    return CheckResult(key=key, passed=False, message=f"'{key}' value does not match pattern '{pattern}'")


def run_checks(
    password: str,
    required_keys: Optional[List[str]] = None,
    patterns: Optional[Dict[str, str]] = None,
    vault_dir: Optional[str] = None,
) -> CheckReport:
    """Load vault and run all configured checks, returning a CheckReport."""
    kwargs = {"vault_dir": vault_dir} if vault_dir else {}
    try:
        vault_data = load_vault(password, **kwargs)
    except Exception as exc:
        raise EnvCheckError(f"Failed to load vault: {exc}") from exc

    report = CheckReport()

    if required_keys:
        report.results.extend(check_required(vault_data, required_keys))

    if patterns:
        for key, pattern in patterns.items():
            report.results.append(check_pattern(vault_data, key, pattern))

    return report
