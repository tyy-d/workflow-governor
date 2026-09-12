from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from workflow_governor.core.models import ExecutorType, WorkflowPlan
from workflow_governor.core.security import is_forbidden_runtime_source


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    code: str
    message: str
    task_id: str | None = None


@dataclass(frozen=True, slots=True)
class ValidationResult:
    issues: tuple[ValidationIssue, ...] = ()

    @property
    def valid(self) -> bool:
        return not self.issues

    def require_valid(self) -> None:
        if not self.valid:
            details = "; ".join(issue.message for issue in self.issues)
            raise ValueError(f"invalid workflow plan: {details}")


class PlanValidator:
    def __init__(
        self,
        *,
        allowed_evidence_sources: Iterable[str] | None = None,
        supported_operations: Iterable[str] | None = None,
    ) -> None:
        self._allowed_sources = (
            frozenset(allowed_evidence_sources)
            if allowed_evidence_sources is not None
            else None
        )
        self._supported_operations = (
            frozenset(supported_operations)
            if supported_operations is not None
            else None
        )

    def validate(self, plan: WorkflowPlan) -> ValidationResult:
        issues: list[ValidationIssue] = []
        if not plan.plan_id.strip():
            issues.append(ValidationIssue("EMPTY_PLAN_ID", "plan_id must not be empty"))
        if plan.version < 1:
            issues.append(ValidationIssue("INVALID_VERSION", "plan version must be positive"))
        if not plan.objective.strip():
            issues.append(ValidationIssue("EMPTY_OBJECTIVE", "plan objective must not be empty"))
        if not plan.tasks:
            issues.append(ValidationIssue("EMPTY_PLAN", "plan must contain at least one task"))

        task_ids = [task.task_id for task in plan.tasks]
        known_ids = set(task_ids)
        if len(known_ids) != len(task_ids):
            issues.append(ValidationIssue("DUPLICATE_TASK_ID", "task IDs must be unique"))

        graph: dict[str, tuple[str, ...]] = {}
        for task in plan.tasks:
            if not task.task_id.strip():
                issues.append(ValidationIssue("EMPTY_TASK_ID", "task_id must not be empty"))
            if not task.objective.strip() or not task.description.strip():
                issues.append(
                    ValidationIssue(
                        "EMPTY_TASK_DESCRIPTION",
                        "task objective and description must not be empty",
                        task.task_id,
                    )
                )
            if not isinstance(task.executor_type, ExecutorType):
                issues.append(
                    ValidationIssue(
                        "INVALID_EXECUTOR", "unsupported executor type", task.task_id
                    )
                )
            if not task.completion_criteria:
                issues.append(
                    ValidationIssue(
                        "MISSING_COMPLETION_CRITERIA",
                        "task must define completion criteria",
                        task.task_id,
                    )
                )
            for dependency in task.dependencies:
                if dependency not in known_ids:
                    issues.append(
                        ValidationIssue(
                            "UNKNOWN_DEPENDENCY",
                            f"unknown dependency {dependency}",
                            task.task_id,
                        )
                    )
                if dependency == task.task_id:
                    issues.append(
                        ValidationIssue(
                            "SELF_DEPENDENCY", "task cannot depend on itself", task.task_id
                        )
                    )
            graph[task.task_id] = task.dependencies

            refs = task.evidence_requirements + task.policy_requirements
            for ref in refs:
                if is_forbidden_runtime_source(ref.source):
                    issues.append(
                        ValidationIssue(
                            "FORBIDDEN_SOURCE",
                            f"runtime source is forbidden: {ref.source}",
                            task.task_id,
                        )
                    )
                elif self._allowed_sources is not None and ref.source not in self._allowed_sources:
                    issues.append(
                        ValidationIssue(
                            "UNGRANTED_SOURCE",
                            f"source was not granted: {ref.source}",
                            task.task_id,
                        )
                    )
            if (
                task.executor_type is ExecutorType.DETERMINISTIC
                and not task.operation
            ):
                issues.append(
                    ValidationIssue(
                        "MISSING_OPERATION",
                        "deterministic task must name an operation",
                        task.task_id,
                    )
                )
            if (
                task.operation
                and self._supported_operations is not None
                and task.operation not in self._supported_operations
            ):
                issues.append(
                    ValidationIssue(
                        "UNSUPPORTED_OPERATION",
                        f"unsupported operation: {task.operation}",
                        task.task_id,
                    )
                )

        issues.extend(self._find_cycles(graph))
        return ValidationResult(tuple(issues))

    @staticmethod
    def _find_cycles(graph: dict[str, tuple[str, ...]]) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(task_id: str) -> None:
            if task_id in visited:
                return
            if task_id in visiting:
                issues.append(
                    ValidationIssue("DEPENDENCY_CYCLE", f"dependency cycle at {task_id}", task_id)
                )
                return
            visiting.add(task_id)
            for dependency in graph.get(task_id, ()):
                if dependency in graph:
                    visit(dependency)
            visiting.remove(task_id)
            visited.add(task_id)

        for task_id in graph:
            visit(task_id)
        return issues

