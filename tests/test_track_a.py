"""Structural Track A tests; no evaluator or hidden fixture access."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from workflow_governor.artifacts import ArtifactStore, WorkflowStateLoader
from workflow_governor.core.config import RuntimeConfig
from workflow_governor.core.errors import ContractValidationError, PersistenceError, WorkspaceAccessError
from workflow_governor.core.models import (
    EvidenceContent, EvidenceRef, ExecutionStatus, ExecutorType, PlanStatus,
    TaskContext, TaskResult, TaskSpec, WorkflowPlan, WorkspaceMap,
)
from workflow_governor.core.persistence_json import json_text, logical_path, parse_json, safe_id
from workflow_governor.core.substrate import DiscoveryLimits, RetrievalLimits, WorkspaceGrant
from workflow_governor.workspace import WorkspaceScout


class TrackATest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.workspace = self.root / "workspace"
        self.workspace.mkdir()
        for name, content in {"a.txt": "中文 hello", "b.md": "# Evidence\nbody", "c.json": '{"value": 2}',
                              "d.csv": "id,value\na,3\n"}.items():
            (self.workspace / name).write_text(content, encoding="utf-8")
        (self.workspace / "e.pdf").write_bytes(b"%PDF-example")
        self.config = RuntimeConfig(self.root)
        self.grant = WorkspaceGrant("selected", "workspace")
        self.scout = WorkspaceScout(self.config)
        self.map = self.scout.discover(self.grant, DiscoveryLimits())
        self.store = ArtifactStore(self.config)
        self.store.create_workflow("run", "Inspect selected evidence", (self.grant,))
        self.task = TaskSpec("read", "Read evidence", "Inspect explicitly selected evidence", ExecutorType.DETERMINISTIC)
        self.plan = WorkflowPlan("plan", 1, "Inspect", (self.task,))

    def complete_state(self):
        evidence = self.scout.retrieve(self.map, ["a.txt"], RetrievalLimits())[0]
        self.store.save_workspace_map("run", self.map)
        self.store.save_evidence("run", (evidence,))
        self.store.save_task("run", self.task)
        self.store.save_context("run", TaskContext("read", evidence=(evidence.as_content(),), granted_sources=(evidence.reference.source,)))
        self.store.save_result("run", TaskResult("read", ExecutionStatus.COMPLETED, ExecutorType.DETERMINISTIC, evidence_refs=(evidence.reference,)))
        self.store.save_task_status("run", "read", ExecutionStatus.COMPLETED)
        self.store.save_plan("run", self.plan, status=PlanStatus.APPROVED)
        self.store.save_finding("run", "observation", {"summary": "Evidence inspected"}, text="Evidence inspected")
        self.store.append_correction("run", {"author": "operator", "reason": "Source clarified"})
        self.store.save_final_state("run", {"status": "completed"})
        self.store.save_final_artifact("run", "summary.txt", "可检查的结果")

    def make_link(self, target, link, directory=False):
        try:
            link.symlink_to(target, target_is_directory=directory)
        except OSError as exc:
            self.skipTest(f"Symlink creation unavailable on this host: {exc.errno}")

    def test_contract_roundtrips_and_deterministic_json(self):
        records = [self.grant, self.map, self.task, self.plan,
                   self.scout.retrieve(self.map, ["a.txt"], RetrievalLimits())[0],
                   TaskContext("read"), TaskResult("read", ExecutionStatus.FAILED, ExecutorType.HUMAN, error="Unavailable")]
        for record in records:
            with self.subTest(record=type(record).__name__):
                raw = record.to_dict()
                self.assertEqual(raw["schema_version"], 1)
                restored = type(record).from_dict(parse_json(json_text(raw)))
                self.assertEqual(restored, record)
                self.assertEqual(json_text(raw), json_text(restored.to_dict()))

    def test_unknown_schema_fields_enums_and_json_rejected(self):
        for version in (0, 2, True, "1"):
            raw = self.task.to_dict() | {"schema_version": version}
            with self.assertRaises(ContractValidationError):
                TaskSpec.from_dict(raw)
        with self.assertRaises(ContractValidationError):
            TaskSpec.from_dict(self.task.to_dict() | {"executor_type": "EVALUATOR"})
        with self.assertRaises(ContractValidationError):
            TaskSpec.from_dict(self.task.to_dict() | {"unknown": 1})
        with self.assertRaises(ContractValidationError):
            json_text({"x": float("nan")})
        with self.assertRaises(ContractValidationError):
            parse_json('{"a":1,"a":2}')

    def test_safe_identifiers_and_paths(self):
        for value in ("../escape", "/tmp/x", "C:/x", "a\\b", "x:stream", "a/../b", "a//b", "a/./b", "CON", "x.", ""):
            with self.subTest(path=value), self.assertRaises(ContractValidationError):
                logical_path(value)
        for value in ("../x", "a/b", "a.b", "NUL", ""):
            with self.assertRaises(ContractValidationError):
                safe_id(value)
        self.assertEqual(logical_path("文档/notes.md"), "文档/notes.md")

    def test_limits_validate_types_and_values(self):
        for kwargs in ({"max_files": -1}, {"max_files": True}, {"max_files": "2"}):
            with self.assertRaises(ContractValidationError):
                DiscoveryLimits(**kwargs)

    def test_discovery_metadata_and_no_full_content(self):
        found = self.scout.discover(self.grant, DiscoveryLimits(max_preview_chars=3))
        self.assertEqual([f.relative_path for f in found.files], sorted(f.relative_path for f in found.files))
        self.assertEqual([f.media_type for f in found.files], ["text/plain", "text/markdown", "application/json", "text/csv", "application/octet-stream"])
        for record in found.files:
            self.assertLessEqual(len(record.metadata["preview"]), 3)
            self.assertEqual(record.metadata["sha256"], hashlib.sha256((self.workspace / record.relative_path).read_bytes()).hexdigest())
        self.assertFalse(found.files[-1].extractable)
        self.assertEqual(found.files[-1].metadata["preview"], "")

    def test_byte_count_and_file_budgets(self):
        found = self.scout.discover(self.grant, DiscoveryLimits(max_files=2, max_total_bytes=15, max_bytes_per_file=12))
        self.assertEqual(len(found.files), 2)
        self.assertLessEqual(found.metadata["bytes_scanned"], 15)
        self.assertTrue(found.warnings)
        limited = self.scout.discover(self.grant, DiscoveryLimits(max_bytes_per_file=0))
        self.assertTrue(all(f.metadata["sha256"] is None for f in limited.files))
        self.assertEqual(len(self.scout.discover(self.grant, DiscoveryLimits(max_files=0)).files), 0)

    def test_explicit_authority_required_after_reload(self):
        ungranted = WorkspaceScout(self.config)
        with self.assertRaises(WorkspaceAccessError):
            ungranted.retrieve(self.map, ["a.txt"], RetrievalLimits())
        authorized = WorkspaceScout(self.config, (self.grant,))
        self.assertEqual(authorized.retrieve(WorkspaceMap.from_dict(self.map.to_dict()), ["a.txt"], RetrievalLimits())[0].status, "unchanged")
        with self.assertRaises(WorkspaceAccessError):
            authorized.discover(WorkspaceGrant("selected", "runtime"), DiscoveryLimits())

    def test_forbidden_roots_and_entries(self):
        for name in ("ground_truth", "provenance", "evaluation"):
            (self.workspace / name).mkdir()
            (self.workspace / name / "secret.txt").write_text("hidden", encoding="utf-8")
            with self.assertRaises(WorkspaceAccessError):
                self.scout.discover(WorkspaceGrant(name, f"workspace/{name}"), DiscoveryLimits())
        (self.workspace / "evaluator.json").write_text("{}")
        found = self.scout.discover(self.grant, DiscoveryLimits())
        self.assertEqual(len(found.files), 5)

    def test_retrieval_requires_selected_known_paths(self):
        self.assertEqual(self.scout.retrieve(self.map, [], RetrievalLimits()), ())
        for paths in (None, "a.txt"):
            with self.assertRaises(ContractValidationError):
                self.scout.retrieve(self.map, paths, RetrievalLimits())
        for path in ("../secret", "/etc/passwd", "C:/secret", "missing.txt"):
            with self.assertRaises((WorkspaceAccessError, ContractValidationError)):
                self.scout.retrieve(self.map, [path], RetrievalLimits())

    def test_retrieval_hash_content_and_character_budgets(self):
        result = self.scout.retrieve(self.map, ["a.txt", "b.md", "a.txt"], RetrievalLimits(max_chars_per_file=4, max_total_chars=6))
        self.assertEqual(len(result), 2)
        self.assertEqual(sum(len(r.content) for r in result), 6)
        self.assertTrue(all(r.truncated for r in result))
        self.assertTrue(all(r.status == "unchanged" and r.sha256 == r.discovered_sha256 for r in result))
        self.assertTrue(result[0].reference.artifact_id.startswith("sha256:"))
        self.assertTrue(result[0].as_content().untrusted_document)

    def test_changed_missing_and_unsupported_sources(self):
        (self.workspace / "a.txt").write_text("changed", encoding="utf-8")
        (self.workspace / "b.md").unlink()
        result = self.scout.retrieve(self.map, ["a.txt", "b.md", "e.pdf"], RetrievalLimits())
        self.assertEqual([r.status for r in result], ["changed", "missing", "unsupported"])
        self.assertNotEqual(result[0].sha256, result[0].discovered_sha256)
        self.assertIsNone(result[1].sha256)

    def test_invalid_utf8_and_unverified_hash(self):
        (self.workspace / "bad.txt").write_bytes(b"\xff\xfe")
        found = self.scout.discover(self.grant, DiscoveryLimits())
        self.assertEqual(next(f for f in found.files if f.relative_path == "bad.txt").metadata["extraction_status"], "invalid_utf8")
        self.assertEqual(self.scout.retrieve(found, ["bad.txt"], RetrievalLimits())[0].status, "invalid_utf8")
        limited = self.scout.discover(self.grant, DiscoveryLimits(max_total_bytes=0))
        self.assertEqual(self.scout.retrieve(limited, ["a.txt"], RetrievalLimits())[0].status, "unverified")

    def test_unreadable_discovery_and_retrieval(self):
        from workflow_governor.workspace.scout import read_bounded
        def read(root, relative, budget):
            if relative == "a.txt":
                raise PermissionError("test-local permission failure")
            return read_bounded(root, relative, budget)
        with patch("workflow_governor.workspace.scout.read_bounded", side_effect=read):
            found = self.scout.discover(self.grant, DiscoveryLimits())
            self.assertEqual(found.files[0].metadata["extraction_status"], "unreadable")
            result = self.scout.retrieve(self.map, ["a.txt", "b.md"], RetrievalLimits())
            self.assertEqual([r.status for r in result], ["unreadable", "unchanged"])

    def test_symlink_escape_and_cycle(self):
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "secret.txt").write_text("secret")
        self.make_link(outside, self.workspace / "escape", True)
        self.make_link(self.workspace, self.workspace / "cycle", True)
        found = self.scout.discover(self.grant, DiscoveryLimits())
        self.assertEqual(len(found.files), 5)
        with self.assertRaises(WorkspaceAccessError):
            self.scout.retrieve(found, ["escape/secret.txt"], RetrievalLimits())

    def test_symlink_swapped_after_discovery(self):
        outside = self.root / "secret.txt"
        outside.write_text("secret")
        (self.workspace / "a.txt").unlink()
        self.make_link(outside, self.workspace / "a.txt")
        with self.assertRaises(WorkspaceAccessError):
            self.scout.retrieve(self.map, ["a.txt"], RetrievalLimits())

    def test_complete_snapshot_roundtrip(self):
        self.complete_state()
        snapshot = WorkflowStateLoader(ArtifactStore(self.config)).load("run", strict=True)
        self.assertEqual(snapshot.tasks["read"], self.task)
        self.assertEqual(snapshot.current_plan.status, PlanStatus.APPROVED)
        self.assertEqual(snapshot.results["read"].status, ExecutionStatus.COMPLETED)
        self.assertEqual(snapshot.statuses["read"], "COMPLETED")
        self.assertEqual(snapshot.final_artifacts["summary.txt"].decode(), "可检查的结果")
        self.assertEqual(len(snapshot.corrections), 1)
        self.assertEqual(snapshot.evidence, self.store.load_evidence("run"))

    def test_fresh_process_reload(self):
        self.complete_state()
        code = "from pathlib import Path; from workflow_governor.artifacts import ArtifactStore,WorkflowStateLoader; from workflow_governor.core.config import RuntimeConfig; import sys; s=WorkflowStateLoader(ArtifactStore(RuntimeConfig(Path(sys.argv[1])))).load('run',strict=True); assert s.results['read'].status == 'COMPLETED'; print('fresh-process-ok')"
        env = dict(os.environ, PYTHONPATH=str(REPO / "src"))
        result = subprocess.run([sys.executable, "-u", "-c", code, str(self.root)], env=env, text=True, capture_output=True, check=True)
        self.assertIn("fresh-process-ok", result.stdout)

    def test_plan_revisions_and_projection(self):
        first = self.store.save_plan("run", self.plan, text="First\n")
        original = self.store.path("run", "plans/plan_0001.json").read_bytes()
        second = self.store.save_plan("run", replace(self.plan, version=2), text="Second\n")
        self.assertEqual((first, second), (1, 2))
        self.assertEqual(self.store.path("run", "plans/plan_0001.json").read_bytes(), original)
        self.assertEqual(self.store.load_manifest("run").current_plan_revision, 2)
        self.assertEqual(self.store.path("run", "plan.md").read_text(), "Second\n")

    def test_atomic_failure_preserves_old_file(self):
        self.store.save_task("run", self.task)
        path = self.store.path("run", "tasks/read/task.json")
        old = path.read_bytes()
        with patch("workflow_governor.artifacts.store.os.replace", side_effect=OSError("interrupted")):
            with self.assertRaises(PersistenceError):
                self.store.save_task("run", replace(self.task, objective="Updated"))
        self.assertEqual(path.read_bytes(), old)
        self.assertEqual(list(path.parent.glob("*.tmp")), [])

    def test_plan_interruption_reports_uncommitted_revision(self):
        self.store.save_task("run", self.task)
        self.store.save_plan("run", self.plan)
        from workflow_governor.artifacts.store import atomic_write
        def write(path, data):
            if path.name == "manifest.json":
                raise OSError("interrupted before commit")
            return atomic_write(path, data)
        with patch("workflow_governor.artifacts.store.atomic_write", side_effect=write):
            with self.assertRaises(PersistenceError):
                self.store.save_plan("run", replace(self.plan, version=2))
        snapshot = WorkflowStateLoader(self.store).load("run")
        self.assertEqual(snapshot.current_plan.revision, 1)
        self.assertIn("uncommitted_plan", [d.code for d in snapshot.diagnostics])
        self.assertEqual(self.store.save_plan("run", replace(self.plan, version=3)), 3)

    def test_append_only_corrections_and_torn_entry(self):
        self.store.append_correction("run", {"reason": "one"})
        path = self.store.path("run", "corrections.jsonl")
        before = path.read_bytes()
        with path.open("ab") as handle:
            handle.write(b'{"torn":')
        self.store.append_correction("run", {"reason": "two"})
        self.assertTrue(path.read_bytes().startswith(before))
        records, diagnostics = self.store.load_corrections("run")
        self.assertEqual(len(records), 2)
        self.assertEqual(len(diagnostics), 1)
        with self.assertRaises(PersistenceError):
            self.store.load_corrections("run", strict=True)

    def test_local_corruption_preserves_completed_results(self):
        self.complete_state()
        other = replace(self.task, task_id="other")
        self.store.save_task("run", other)
        self.store.path("run", "tasks/other/result.json").write_text("bad json")
        self.store.path("run", "findings/observation.json").write_text("bad json")
        snapshot = WorkflowStateLoader(self.store).load("run")
        self.assertEqual(snapshot.results["read"].status, ExecutionStatus.COMPLETED)
        self.assertNotIn("other", snapshot.results)
        self.assertGreaterEqual(len(snapshot.diagnostics), 2)
        with self.assertRaises(PersistenceError):
            WorkflowStateLoader(self.store).load("run", strict=True)

    def test_fatal_manifest_and_structure(self):
        path = self.store.path("run", "manifest.json")
        good = path.read_bytes()
        path.write_text("{broken")
        with self.assertRaises(PersistenceError) as error:
            WorkflowStateLoader(self.store).load("run")
        self.assertEqual(error.exception.diagnostics[0].severity, "fatal")
        path.write_bytes(good)
        self.store.path("run", "tasks").rmdir()
        with self.assertRaises(PersistenceError):
            WorkflowStateLoader(self.store).load("run")

    def test_manifest_identity_mismatch(self):
        path = self.store.path("run", "manifest.json")
        raw = json.loads(path.read_text())
        raw["workflow_id"] = "another"
        path.write_text(json.dumps(raw))
        with self.assertRaises(PersistenceError):
            self.store.load_manifest("run")

    def test_interrupted_failed_cancelled_are_not_scheduled(self):
        for status in ("PENDING", "IN_PROGRESS", "FAILED", "CANCELLED"):
            self.store.save_task("run", self.task)
            self.store.save_task_status("run", "read", status)
            self.store.save_final_state("run", {"status": status})
            snapshot = WorkflowStateLoader(self.store).load("run", strict=True)
            self.assertEqual(snapshot.statuses["read"], status)
            self.assertEqual(snapshot.results, {})
            self.assertFalse(hasattr(snapshot, "ready_tasks"))

    def test_status_conflict_reported_not_repaired(self):
        self.complete_state()
        self.store.save_task_status("run", "read", "IN_PROGRESS")
        snapshot = WorkflowStateLoader(self.store).load("run")
        self.assertIn("status_conflict", [d.code for d in snapshot.diagnostics])
        self.assertEqual(snapshot.statuses["read"], "IN_PROGRESS")

    def test_missing_completed_result_has_explicit_diagnostic(self):
        self.store.save_task("run", self.task)
        self.store.save_task_status("run", "read", "COMPLETED")
        snapshot = WorkflowStateLoader(self.store).load("run")
        self.assertIn("missing_completed_result", [d.code for d in snapshot.diagnostics])
        self.assertEqual(snapshot.results, {})

    def test_bad_plan_filename_does_not_discard_good_plan(self):
        self.store.save_task("run", self.task)
        self.store.save_plan("run", self.plan)
        self.store.path("run", "plans/plan_bad.json").write_text("invalid")
        snapshot = WorkflowStateLoader(self.store).load("run")
        self.assertEqual(snapshot.current_plan.plan, self.plan)
        self.assertIn("invalid_plan_filename", [d.code for d in snapshot.diagnostics])

    def test_unindexed_final_file_reports_interrupted_save(self):
        self.store.path("run", "final/artifacts/orphan.txt").write_text("uncommitted")
        snapshot = WorkflowStateLoader(self.store).load("run")
        self.assertIn("unindexed_final_artifact", [d.code for d in snapshot.diagnostics])
        self.assertEqual(snapshot.final_artifacts, {})

    def test_cli_discovery_and_new_process_inspection(self):
        env = dict(os.environ, PYTHONPATH=str(REPO / "src"))
        command = [sys.executable, "-u", "-m", "workflow_governor.track_a", "--repository", str(self.root)]
        discovered = subprocess.run(command + ["discover", "--workflow-id", "cli", "--objective", "Inspect", "--grant-id", "visible", "--grant-root", "workspace", "--path", "a.txt"], env=env, text=True, capture_output=True, check=True)
        self.assertEqual(json.loads(discovered.stdout)["evidence_retrieved"], 1)
        inspected = subprocess.run(command + ["inspect", "cli", "--strict"], env=env, text=True, capture_output=True, check=True)
        self.assertEqual(json.loads(inspected.stdout)["diagnostics"], [])
        self.assertEqual(json.loads(inspected.stdout)["evidence"], 1)

    def test_final_artifact_integrity(self):
        self.store.save_final_artifact("run", "nested/result.bin", b"\x00\x01")
        self.assertEqual(self.store.load_final_artifact("run", "nested/result.bin"), b"\x00\x01")
        self.store.path("run", "final/artifacts/nested/result.bin").write_bytes(b"bad")
        with self.assertRaises(PersistenceError):
            self.store.load_final_artifact("run", "nested/result.bin")
        self.assertTrue(WorkflowStateLoader(self.store).load("run").diagnostics)

    def test_workflow_isolation_and_escape(self):
        with self.assertRaises(PersistenceError):
            self.store.create_workflow("run", "Do not overwrite", ())
        for identifier in ("../escape", "C:/escape", "a/b"):
            with self.assertRaises(ContractValidationError):
                self.store.create_workflow(identifier, "bad", ())
        for path in ("../escape", "C:/escape", "nested/../../escape"):
            with self.assertRaises(ContractValidationError):
                self.store.save_final_artifact("run", path, "bad")
        self.store.create_workflow("other", "Other", ())
        self.store.save_task("run", self.task)
        with self.assertRaises(PersistenceError):
            self.store.load_task("other", "read")

    def test_artifact_symlink_confinement(self):
        outside = self.root / "outside"
        outside.mkdir()
        self.make_link(outside, self.store.path("run", "final/artifacts/link"), True)
        with self.assertRaises(PersistenceError):
            self.store.save_final_artifact("run", "link/escape.txt", "bad")
        self.assertEqual(list(outside.iterdir()), [])

    def test_portable_runtime_and_no_absolute_paths_in_artifacts(self):
        self.complete_state()
        root = self.store.workflow_root("run")
        for path in root.rglob("*"):
            if path.is_file():
                self.assertNotIn(str(self.root), path.read_text(encoding="utf-8"))
        config = RuntimeConfig(self.root, Path("custom/runtime"))
        self.assertEqual(config.workflows_root, self.root / "custom/runtime/workflows")

    def test_case001_structural_smoke(self):
        grant = WorkspaceGrant("case001", "cases/CASE_001_VENDOR_ACTIVATION/workspace")
        scout = WorkspaceScout(RuntimeConfig(REPO))
        found = scout.discover(grant, DiscoveryLimits())
        self.assertTrue(found.files)
        self.assertTrue(all(not any(part in f.relative_path for part in ("ground_truth", "evaluator", "provenance")) for f in found.files))
        selected = [f.relative_path for f in found.files if f.extractable][:2]
        retrieved = scout.retrieve(found, selected, RetrievalLimits())
        self.assertTrue(all(r.status == "unchanged" for r in retrieved))
        self.store.create_workflow("case001", "Structural discovery/persistence smoke test", (grant,))
        self.store.save_workspace_map("case001", found)
        loaded = WorkflowStateLoader(self.store).load("case001", strict=True)
        self.assertEqual(loaded.workspace_map, found)
        self.assertEqual(scout.retrieve(loaded.workspace_map, selected, RetrievalLimits())[0].sha256, retrieved[0].sha256)
        for relative in ("../ground_truth/secret.json", "../../personas/P001/evaluator.json", "../../../company/northstar/provenance/source.txt"):
            with self.assertRaises((WorkspaceAccessError, ContractValidationError)):
                scout.retrieve(found, [relative], RetrievalLimits())


if __name__ == "__main__":
    unittest.main(verbosity=2)
