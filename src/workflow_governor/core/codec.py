"""Additive serialization for existing shared dataclasses, without semantic changes."""

import types
from collections.abc import Mapping
from dataclasses import fields, is_dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Literal, get_args, get_origin, get_type_hints

from .errors import ContractValidationError
from .persistence_json import json_text, logical_path, safe_id, validate_timestamp


def decode(value, annotation):
    origin, args = get_origin(annotation), get_args(annotation)
    if annotation is Any:
        if value is None or type(value) in (str, bool, int, float):
            json_text(value)
            return value
        if type(value) is list:
            return [decode(v, Any) for v in value]
        if type(value) is dict and all(type(k) is str for k in value):
            return {k: decode(v, Any) for k, v in value.items()}
        raise ContractValidationError("Invalid JSON value")
    if origin is types.UnionType:
        for option in args:
            try:
                return decode(value, option)
            except ContractValidationError:
                pass
        raise ContractValidationError("Invalid optional value")
    if origin is Literal:
        if value not in args or type(value) is not type(args[0]):
            raise ContractValidationError("Invalid literal or schema version")
        return value
    if origin is tuple:
        if type(value) not in (list, tuple):
            raise ContractValidationError("Expected a sequence")
        return tuple(decode(v, args[0]) for v in value)
    if origin in (dict, Mapping):
        if type(value) is not dict or not all(type(k) is str for k in value):
            raise ContractValidationError("Expected an object with string keys")
        return {k: decode(v, args[1]) for k, v in value.items()}
    if isinstance(annotation, type) and issubclass(annotation, Enum):
        try:
            return annotation(value)
        except (ValueError, TypeError) as exc:
            raise ContractValidationError("Unknown runtime enum value") from exc
    if annotation is datetime:
        validate_timestamp(value)
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    if is_dataclass(annotation):
        return from_dict(annotation, value)
    if type(value) is not annotation:
        raise ContractValidationError("Wrong field type")
    return value


def primitive(value):
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        text = value.isoformat()
        validate_timestamp(text)
        return text
    if is_dataclass(value):
        return to_dict(value)
    if isinstance(value, tuple):
        return [primitive(v) for v in value]
    if isinstance(value, dict):
        if not all(type(k) is str for k in value):
            raise ContractValidationError("JSON keys must be strings")
        return {k: primitive(v) for k, v in value.items()}
    if isinstance(value, list):
        return [primitive(v) for v in value]
    return decode(value, Any)


def _validate_fields(value):
    for name, annotation in get_type_hints(type(value)).items():
        raw = primitive(getattr(value, name))
        decode(raw, annotation)
        if name in {"workflow_id", "task_id", "plan_id", "grant_id"}:
            safe_id(getattr(value, name))
        if name in {"source", "relative_path", "root"}:
            logical_path(getattr(value, name))
    for dep in getattr(value, "dependencies", ()):
        safe_id(dep)
    for source in getattr(value, "granted_sources", ()):
        logical_path(source)
    for path in getattr(value, "artifacts", ()):
        logical_path(path)
    if hasattr(value, "version") and value.version < 1:
        raise ContractValidationError("Versions start at one")
    if hasattr(value, "size") and value.size is not None and value.size < 0:
        raise ContractValidationError("Negative file size")
    if hasattr(value, "_validate"):
        value._validate()


def to_dict(value):
    _validate_fields(value)
    result = {f.name: primitive(getattr(value, f.name)) for f in fields(value)}
    result["schema_version"] = 1
    return result


def from_dict(cls, value):
    if type(value) is not dict or type(value.get("schema_version")) is not int or value["schema_version"] != 1:
        raise ContractValidationError("Unsupported or missing schema_version")
    names = {f.name for f in fields(cls)}
    # Read pre-human-integration TaskSpec records without rewriting their files.
    # The added field has the least-privileged meaning: no decision authority.
    if (cls.__module__ == "workflow_governor.core.models" and cls.__name__ == "TaskSpec"
            and set(value) == (names - {"requested_decision_authority_scope"}) | {"schema_version"}):
        value = dict(value, requested_decision_authority_scope="NO_DECISION")
    if set(value) != names | {"schema_version"}:
        raise ContractValidationError("Unknown or missing contract fields")
    hints = get_type_hints(cls)
    result = cls(**{k: decode(value[k], hints[k]) for k in names})
    _validate_fields(result)
    return result


class DurableModel:
    @property
    def schema_version(self):
        return 1

    def to_dict(self):
        return to_dict(self)

    @classmethod
    def from_dict(cls, value):
        return from_dict(cls, value)
