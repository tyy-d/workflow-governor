from __future__ import annotations

from pathlib import PurePosixPath


_FORBIDDEN_PARTS = {"ground_truth", "provenance"}


def normalize_source(source: str) -> str:
    return source.replace("\\", "/").lstrip("./")


def is_forbidden_runtime_source(source: str) -> bool:
    normalized = normalize_source(source)
    parts = {part.lower() for part in PurePosixPath(normalized).parts}
    if parts & _FORBIDDEN_PARTS:
        return True
    if "personas" in parts and normalized.lower().endswith("/evaluator.json"):
        return True
    return False


def ensure_runtime_source_allowed(source: str) -> None:
    if is_forbidden_runtime_source(source):
        raise ValueError(f"runtime access to hidden source is forbidden: {source}")

