"""Explicit, bounded workspace access."""

from .scout import WorkspaceScout
from workflow_governor.core.substrate import DiscoveryLimits, RetrievalLimits, WorkspaceGrant

__all__ = ["WorkspaceScout", "WorkspaceGrant", "DiscoveryLimits", "RetrievalLimits"]
