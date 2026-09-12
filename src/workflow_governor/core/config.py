"""Runtime locations are local configuration, never serialized authority."""

import os
import stat
from dataclasses import dataclass
from pathlib import Path

from .errors import ConfigurationError, WorkspaceAccessError
from .persistence_json import logical_path


def confined(root: Path, relative: str) -> Path:
    """Reject links/reparse points, including Windows junctions, in every component.

    Filesystem trees must not be concurrently renamed by a hostile local process.
    This is an application access boundary, not an OS sandbox.
    """
    logical_path(relative)
    root = Path(root)
    # Include the root itself: replacing a configured root with a link is unsafe.
    for ancestor in (root, *root.parents):
        try:
            info = ancestor.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise WorkspaceAccessError("Linked root is not allowed")
    current = root
    for part in relative.split("/"):
        current = current / part
        try:
            info = current.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise WorkspaceAccessError("Linked or reparse path is not allowed")
    if not current.resolve().is_relative_to(root.resolve()):
        raise WorkspaceAccessError("Path escapes authorized root")
    return current


@dataclass(frozen=True)
class RuntimeConfig:
    repository_root: Path
    runtime_root: Path | None = None

    def __post_init__(self):
        repo = Path(self.repository_root).absolute()
        runtime = Path(self.runtime_root or os.environ.get("WORKFLOW_GOVERNOR_RUNTIME", "runtime"))
        if not runtime.is_absolute():
            runtime = repo / runtime
        if not repo.is_dir():
            raise ConfigurationError("Repository root must be an existing directory")
        object.__setattr__(self, "repository_root", repo)
        object.__setattr__(self, "runtime_root", runtime.absolute())

    @classmethod
    def from_environment(cls):
        return cls(Path(os.environ.get("WORKFLOW_GOVERNOR_REPOSITORY", Path.cwd())))

    @property
    def workflows_root(self) -> Path:
        return confined(self.runtime_root, "workflows")
