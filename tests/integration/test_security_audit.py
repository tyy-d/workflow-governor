from __future__ import annotations

import ast
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "workflow_governor"


def test_production_source_has_no_case_knowledge_or_developer_machine_paths() -> None:
    text = "\n".join(path.read_text(encoding="utf-8") for path in SOURCE.rglob("*.py"))
    for forbidden in (
        "CASE_001",
        "NVID-10482",
        "Harbor Finch",
        "MCS-884201",
        "47cdd71",
        "C:\\Users\\",
        "/home/",
    ):
        assert forbidden not in text
    assert not re.search(r"[A-Za-z]:[/\\](?:Users|Documents|workspace)[/\\]", text)


def test_production_defines_no_mock_fake_or_scripted_implementations() -> None:
    prohibited = re.compile(r"^(?:Mock|Fake|Scripted).*(?:Planner|Model|Human|Artifact|Sink|Store)")
    for path in SOURCE.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                assert not prohibited.match(node.name), f"test substitute in production: {path}:{node.lineno}"
