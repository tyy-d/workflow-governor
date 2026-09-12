"""Portable discovery/inspection CLI. No planner, executor, or evaluation calls."""

import argparse
from pathlib import Path

from .artifacts import ArtifactStore, WorkflowStateLoader
from .core.config import RuntimeConfig
from .core.errors import WorkflowGovernorError
from .core.persistence_json import json_text
from .core.substrate import DiscoveryLimits, RetrievalLimits, WorkspaceGrant
from .workspace import WorkspaceScout


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--runtime", type=Path)
    sub = parser.add_subparsers(dest="command", required=True)
    discover = sub.add_parser("discover")
    discover.add_argument("--workflow-id", required=True)
    discover.add_argument("--objective", required=True)
    discover.add_argument("--grant-id", required=True)
    discover.add_argument("--grant-root", required=True)
    discover.add_argument("--path", action="append", default=[], help="Explicit path relative to the grant root; may be repeated")
    discover.add_argument("--max-files", type=int, default=1000)
    discover.add_argument("--max-total-bytes", type=int, default=10_000_000)
    inspect = sub.add_parser("inspect")
    inspect.add_argument("workflow_id")
    inspect.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)
    try:
        config = RuntimeConfig(args.repository, args.runtime)
        store = ArtifactStore(config)
        if args.command == "discover":
            grant = WorkspaceGrant(args.grant_id, args.grant_root)
            scout = WorkspaceScout(config)
            workspace_map = scout.discover(grant, DiscoveryLimits(max_files=args.max_files, max_total_bytes=args.max_total_bytes))
            selected = scout.retrieve(workspace_map, args.path, RetrievalLimits())
            store.create_workflow(args.workflow_id, args.objective, (grant,))
            store.save_workspace_map(args.workflow_id, workspace_map)
            store.save_evidence(args.workflow_id, selected)
            print(json_text({"workflow_id": args.workflow_id, "files_discovered": len(workspace_map.files),
                             "bytes_scanned": workspace_map.metadata["bytes_scanned"], "evidence_retrieved": len(selected),
                             "warnings": list(workspace_map.warnings)}), end="")
        else:
            snapshot = WorkflowStateLoader(store).load(args.workflow_id, strict=args.strict)
            print(json_text({"workflow_id": snapshot.manifest.workflow_id,
                             "current_plan_revision": snapshot.manifest.current_plan_revision,
                             "files": len(snapshot.workspace_map.files) if snapshot.workspace_map else 0,
                             "evidence": len(snapshot.evidence), "tasks": sorted(snapshot.tasks),
                             "statuses": snapshot.statuses, "results": sorted(snapshot.results),
                             "final_artifacts": sorted(snapshot.final_artifacts),
                             "diagnostics": [d.to_dict() for d in snapshot.diagnostics]}), end="")
        return 0
    except WorkflowGovernorError as exc:
        print(json_text({"error": str(exc), "diagnostics": [d.to_dict() for d in getattr(exc, "diagnostics", ())]}), end="")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
