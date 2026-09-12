from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path, PurePosixPath
from typing import Iterable

from workflow_governor.core.config import confined
from workflow_governor.core.errors import ContractValidationError, WorkspaceAccessError
from workflow_governor.core.models import EvidenceContent
from workflow_governor.core.security import is_forbidden_runtime_source
from workflow_governor.execution.runner import HumanHandoff


class PersonaContextError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class PersonaSession:
    session_id: str
    persona_id: str
    actor_source: str
    case_id: str | None = None
    memory_source: str | None = None
    grants: tuple[EvidenceContent, ...] = ()
    conversation_history: tuple[str, ...] = ()
    authorized_context: tuple[str, ...] = ()

    def with_grants(self, additions: Iterable[EvidenceContent]) -> "PersonaSession":
        existing = {item.ref.source: item for item in self.grants}
        for item in additions:
            _validate_grant_source(item.ref.source, self.persona_id)
            existing[item.ref.source] = item
        return replace(self, grants=tuple(existing.values()))

    def with_message(self, message: str) -> "PersonaSession":
        if not message.strip():
            raise PersonaContextError("conversation messages must be non-empty")
        return replace(self, conversation_history=self.conversation_history + (message,))


class PersonaContextAssembler:
    def __init__(self, repository_root: Path, prompt_source: str = "simulator/prompts/persona_system_prompt.md") -> None:
        self._root = repository_root.resolve()
        self._prompt_source = prompt_source

    def render(self, session: PersonaSession, handoff: HumanHandoff) -> str:
        self._validate_session(session)
        allowed_handoff_sources = {ref.source for ref in handoff.evidence_refs}
        grant_sources = {item.ref.source for item in session.grants}
        if not allowed_handoff_sources.issubset(grant_sources):
            missing = sorted(allowed_handoff_sources - grant_sources)
            raise PersonaContextError(f"handoff evidence was not explicitly granted: {missing}")

        actor = self._read(session.actor_source)
        memory = self._read(session.memory_source) if session.memory_source else ""
        prompt = self._read(self._prompt_source)
        grants = "\n\n".join(
            f"<UNTRUSTED_BUSINESS_EVIDENCE source={item.ref.source!r}>\n{item.content}\n</UNTRUSTED_BUSINESS_EVIDENCE>"
            for item in session.grants
        )
        task = (
            f"handoff_id: {handoff.handoff_id}\n"
            f"workflow_id: {handoff.workflow_id}\n"
            f"task_id: {handoff.task_id}\n"
            f"objective: {handoff.objective}\n"
            f"requested_decision_authority_scope: {handoff.requested_decision_authority_scope.value}\n"
            f"authority_requirement: {handoff.authority_requirement or 'none'}\n"
            f"completion_criteria: {list(handoff.completion_criteria)!r}\n"
            f"unresolved_questions: {list(handoff.unresolved_questions)!r}"
        )
        replacements = {
            "{{ACTOR_PROFILE}}": actor,
            "{{AUTHORIZED_CONTEXT}}": "\n".join(session.authorized_context),
            "{{CASE_MEMORY}}": memory,
            "{{GRANTED_FILES}}": grants,
            "{{CONVERSATION_HISTORY}}": "\n".join(session.conversation_history),
            "{{CURRENT_TASK_CONTEXT}}": task,
        }
        for marker, value in replacements.items():
            prompt = prompt.replace(marker, value)
        return prompt

    def _validate_session(self, session: PersonaSession) -> None:
        expected_actor = f"personas/{session.persona_id}/actor.md"
        if _normalize(session.actor_source) != expected_actor:
            raise PersonaContextError("actor source does not match the selected persona")
        if session.memory_source:
            if not session.case_id:
                raise PersonaContextError("case memory requires a case_id")
            expected_memory = f"cases/{session.case_id}/persona_memory/{session.persona_id}.md"
            if _normalize(session.memory_source) != expected_memory:
                raise PersonaContextError("case memory does not match the selected persona and case")
        for item in session.grants:
            _validate_grant_source(item.ref.source, session.persona_id)

    def _read(self, source: str) -> str:
        normalized = _normalize(source)
        try:
            candidate = confined(self._root, normalized)
        except (ContractValidationError, WorkspaceAccessError) as exc:
            raise PersonaContextError(f"unsafe authorized source: {source}") from exc
        if not candidate.is_file():
            raise PersonaContextError(f"authorized source does not exist: {source}")
        return candidate.read_text(encoding="utf-8")


def _normalize(source: str) -> str:
    path = PurePosixPath(source.replace("\\", "/"))
    if path.is_absolute() or ".." in path.parts:
        raise PersonaContextError(f"unsafe source path: {source}")
    return path.as_posix()


def _validate_grant_source(source: str, persona_id: str) -> None:
    normalized = _normalize(source)
    lowered = normalized.lower()
    parts = PurePosixPath(lowered).parts
    if is_forbidden_runtime_source(normalized):
        raise PersonaContextError(f"forbidden persona grant: {source}")
    if lowered.startswith("personas/") or "/persona_memory/" in lowered:
        raise PersonaContextError("actor and memory files must enter through their dedicated selected fields")
    if lowered.startswith("runtime/operators/") or "routing" in parts:
        raise PersonaContextError(f"hidden operator or routing state is forbidden: {source}")
