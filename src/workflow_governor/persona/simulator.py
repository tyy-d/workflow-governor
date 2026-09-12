from __future__ import annotations

from typing import Protocol

from workflow_governor.execution.runner import HumanHandoff
from workflow_governor.human.contracts import HumanTaskResponse, ResponseValidationResult
from workflow_governor.human.validation import HumanResponseValidator
from workflow_governor.persona.session import PersonaContextAssembler, PersonaSession


class PersonaBackend(Protocol):
    def respond(self, prompt: str, handoff: HumanHandoff, session: PersonaSession) -> HumanTaskResponse: ...


class PersonaSimulator:
    def __init__(
        self,
        assembler: PersonaContextAssembler,
        backend: PersonaBackend,
        validator: HumanResponseValidator,
    ) -> None:
        self._assembler = assembler
        self._backend = backend
        self._validator = validator

    def interact(self, handoff: HumanHandoff, session: PersonaSession) -> ResponseValidationResult:
        prompt = self._assembler.render(session, handoff)
        response = self._backend.respond(prompt, handoff, session)
        return self._validator.validate(handoff, response, session_id=session.session_id)
