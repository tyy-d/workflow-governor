"""Metadata first and explicitly selected content second; never follow links."""

import hashlib
import os
import stat
from datetime import datetime, timezone
from pathlib import Path

from workflow_governor.core.config import RuntimeConfig, confined
from workflow_governor.core.errors import ContractValidationError, WorkspaceAccessError
from workflow_governor.core.models import EvidenceRef, FileRecord, WorkspaceMap
from workflow_governor.core.persistence_json import logical_path, utc_now
from workflow_governor.core.substrate import Diagnostic, RetrievedEvidence, WorkspaceGrant

_MEDIA = {".txt": "text/plain", ".md": "text/markdown", ".markdown": "text/markdown",
          ".json": "application/json", ".csv": "text/csv"}
_FORBIDDEN = {"ground_truth", "provenance", "evaluation", ".git"}


def allowed(path):
    logical_path(path)
    parts = path.casefold().split("/")
    if set(parts) & _FORBIDDEN or parts[-1] == "evaluator.json":
        raise WorkspaceAccessError("Source is excluded from runtime access")


def _fingerprint(info):
    # On Windows Python 3.12, stat() and fstat() can expose different ctime
    # semantics (birth time versus change time). Identity, size and mtime agree.
    base = (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns)
    return base + ((info.st_ctime_ns,) if os.name == "posix" else ())


def read_bounded(root, relative, budget):
    """Return bytes, stat, stable-read flag. Never claim a partial hash is a file hash."""
    path = confined(root, relative)
    before = path.stat()
    if not stat.S_ISREG(before.st_mode):
        raise WorkspaceAccessError("Evidence must be a regular file")
    if before.st_size > budget:
        return None, before, True
    with path.open("rb") as handle:
        opened = os.fstat(handle.fileno())
        if not stat.S_ISREG(opened.st_mode):
            raise WorkspaceAccessError("Evidence must be a regular file")
        data = handle.read(min(before.st_size, budget))
        after = os.fstat(handle.fileno())
    current = confined(root, relative).stat()
    stable = (_fingerprint(before) == _fingerprint(opened) == _fingerprint(after)
              == _fingerprint(current) and len(data) == before.st_size)
    return data, after, stable


class WorkspaceScout:
    def __init__(self, config: RuntimeConfig, grants=()):
        self.config = config
        self._grants = {}
        for grant in grants:
            self._authorize(grant)

    def _authorize(self, grant):
        grant.to_dict()
        allowed(grant.root)
        root = confined(self.config.repository_root, grant.root)
        if not root.is_dir():
            raise WorkspaceAccessError("Authorized workspace root is not a directory")
        previous = self._grants.get(grant.grant_id)
        if previous is not None and previous != grant:
            raise WorkspaceAccessError("Grant identity cannot be rebound")
        self._grants[grant.grant_id] = grant
        return root

    def _files(self, root, diagnostics, relative=""):
        directory = root if not relative else confined(root, relative)
        try:
            with os.scandir(directory) as entries:
                entries = sorted(entries, key=lambda entry: entry.name)
        except OSError:
            diagnostics.append(Diagnostic("directory_unreadable", "Directory could not be enumerated", relative or None))
            return
        for entry in entries:
            path = f"{relative}/{entry.name}" if relative else entry.name
            try:
                allowed(path)
                confined(root, path)
                if entry.is_dir(follow_symlinks=False):
                    yield from self._files(root, diagnostics, path)
                elif entry.is_file(follow_symlinks=False):
                    yield path
                else:
                    diagnostics.append(Diagnostic("not_regular", "Non-regular entry skipped", path))
            except (WorkspaceAccessError, ContractValidationError):
                # Unsafe names must not themselves break diagnostic serialization.
                diagnostics.append(Diagnostic("excluded_path", "Unsafe or excluded entry skipped"))
            except OSError:
                yield path  # Record inaccessible individual files instead of dropping them.

    def discover(self, grant, limits):
        limits.to_dict()
        root = self._authorize(grant)
        files, warnings = [], []
        remaining = limits.max_total_bytes
        for relative in self._files(root, warnings):
            if len(files) >= limits.max_files:
                warnings.append(Diagnostic("file_limit", "File count limit reached"))
                break
            ext = Path(relative).suffix.lower()
            media = _MEDIA.get(ext, "application/octet-stream")
            size = modified = digest = None
            preview, state, issues = "", "unreadable", []
            try:
                data, info, stable = read_bounded(root, relative, min(remaining, limits.max_bytes_per_file))
                size = info.st_size
                modified = datetime.fromtimestamp(info.st_mtime, timezone.utc).isoformat()
                if data is None:
                    state = "limited"
                    issues.append(Diagnostic("byte_limit", "File was not read because it exceeds the byte budget", relative))
                else:
                    remaining -= len(data)
                    if not stable:
                        state = "changed"
                        issues.append(Diagnostic("changed_during_read", "File changed while being read", relative))
                    else:
                        digest = hashlib.sha256(data).hexdigest()
                        state = "unsupported"
                        if ext in _MEDIA:
                            try:
                                preview = data.decode("utf-8-sig")[:limits.max_preview_chars]
                                state = "extracted"
                            except UnicodeDecodeError:
                                state = "invalid_utf8"
                                issues.append(Diagnostic("invalid_utf8", "Text is not valid UTF-8", relative))
            except (OSError, WorkspaceAccessError):
                issues.append(Diagnostic("file_unreadable", "File could not be read safely", relative))
            files.append(FileRecord(relative, Path(relative).name, media, size,
                                    {"extension": ext, "modified_at": modified, "sha256": digest,
                                     "extraction_status": state, "preview": preview,
                                     "diagnostics": [d.to_dict() for d in issues]}, state == "extracted"))
        return WorkspaceMap(grant.root, tuple(sorted(files, key=lambda f: f.relative_path)),
                            {"grant": grant.to_dict(), "discovered_at": utc_now(),
                             "bytes_scanned": limits.max_total_bytes - remaining,
                             "diagnostics": [d.to_dict() for d in warnings]},
                            tuple(d.message for d in warnings))

    def retrieve(self, workspace_map, relative_paths, limits):
        limits.to_dict()
        workspace_map.to_dict()
        if isinstance(relative_paths, (str, bytes)) or relative_paths is None:
            raise ContractValidationError("Retrieval requires an explicit sequence of paths")
        grant = WorkspaceGrant.from_dict(workspace_map.metadata.get("grant"))
        if self._grants.get(grant.grant_id) != grant or workspace_map.root != grant.root:
            raise WorkspaceAccessError("A persisted map is not an authorization grant")
        root = confined(self.config.repository_root, grant.root)
        records = {f.relative_path: f for f in workspace_map.files}
        paths = list(dict.fromkeys(relative_paths))
        # Validate the whole request before reading any content.
        for relative in paths:
            allowed(relative)
            confined(root, relative)
            if relative not in records:
                raise WorkspaceAccessError("Requested source is not in the discovered map")
        remaining_chars, remaining_bytes = limits.max_total_chars, limits.max_total_bytes
        result = []
        for relative in paths:
            record = records[relative]
            old_hash = record.metadata.get("sha256")
            digest, content, truncated, issues = None, "", False, []
            state = "unreadable"
            try:
                data, _, stable = read_bounded(root, relative, min(remaining_bytes, limits.max_bytes_per_file))
                if data is None:
                    state, truncated = "limited", True
                    issues.append(Diagnostic("byte_limit", "Retrieval byte limit reached", relative))
                else:
                    remaining_bytes -= len(data)
                    if not stable:
                        state = "changed"
                        issues.append(Diagnostic("changed_during_read", "Unstable content withheld", relative))
                    else:
                        digest = hashlib.sha256(data).hexdigest()
                        state = "unverified" if old_hash is None else "unchanged" if digest == old_hash else "changed"
                        if state == "changed":
                            issues.append(Diagnostic("changed_since_discovery", "Evidence hash differs from discovery", relative))
                        if Path(relative).suffix.lower() not in _MEDIA:
                            issues.append(Diagnostic("unsupported_format", "Metadata-only format", relative))
                            if state != "changed":
                                state = "unsupported"
                        else:
                            try:
                                text = data.decode("utf-8-sig")
                                content = text[:min(remaining_chars, limits.max_chars_per_file)]
                                truncated = len(content) < len(text)
                                remaining_chars -= len(content)
                            except UnicodeDecodeError:
                                issues.append(Diagnostic("invalid_utf8", "Text is not valid UTF-8", relative))
                                if state != "changed":
                                    state = "invalid_utf8"
            except FileNotFoundError:
                state = "missing"
                issues.append(Diagnostic("file_missing", "Source no longer exists", relative))
            except (OSError, WorkspaceAccessError):
                issues.append(Diagnostic("file_unreadable", "Source cannot be read safely", relative))
            ref = EvidenceRef(f"{grant.root}/{relative}", artifact_id=f"sha256:{digest}" if digest else None,
                              label=grant.grant_id)
            result.append(RetrievedEvidence(ref, old_hash, digest, state, content, truncated, utc_now(), tuple(issues)))
        return tuple(result)
