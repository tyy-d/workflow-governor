from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_track_c_does_not_import_runtime_or_planning_mutators() -> None:
    sources = "\n".join(
        path.read_text(encoding="utf-8")
        for package in ("human", "persona", "operator_model")
        for path in (ROOT / "src" / "workflow_governor" / package).rglob("*.py")
    )
    for forbidden in ("RunState", "TaskExecutionState", "PlanLifecycle", "MinimalTaskRunner"):
        assert forbidden not in sources
