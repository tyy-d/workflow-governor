"""Strict, deterministic JSON and portable identifiers."""

import json
import re
from datetime import datetime, timezone
from pathlib import PureWindowsPath

from .errors import ContractValidationError

SCHEMA_VERSION = 1
_RESERVED = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)),
             *(f"LPT{i}" for i in range(1, 10))}


def safe_id(value: str) -> str:
    if (not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}", value)
            or value.upper() in _RESERVED):
        raise ContractValidationError("Invalid portable identifier")
    return value


def logical_path(value: str) -> str:
    if not isinstance(value, str) or not value or PureWindowsPath(value).drive:
        raise ContractValidationError("Expected a nonempty relative logical path")
    parts = value.split("/")
    if any(p in ("", ".", "..") or p.endswith((".", " "))
           or p.split(".")[0].upper() in _RESERVED
           or any(ord(c) < 32 or c in '\\:*?"<>|' for c in p) for p in parts):
        raise ContractValidationError("Invalid portable relative path")
    return value


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def validate_timestamp(value: str) -> None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
            raise ValueError
    except (AttributeError, ValueError, TypeError) as exc:
        raise ContractValidationError("Expected UTC ISO-8601 timestamp") from exc


def json_text(value) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"
    except (TypeError, ValueError) as exc:
        raise ContractValidationError("Expected JSON-compatible finite values") from exc


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ContractValidationError("Duplicate JSON object key")
        result[key] = value
    return result


def parse_json(value: str):
    def reject_constant(value):
        raise ContractValidationError("Non-finite JSON number")
    return json.loads(value, object_pairs_hook=_unique_pairs, parse_constant=reject_constant)
