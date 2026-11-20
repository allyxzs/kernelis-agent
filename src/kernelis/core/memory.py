"""Registro em memória da sessão de execução do Kernelis."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class ExecutionEvent:
    timestamp: str
    step_id: str
    tool: str
    action: str
    success: bool
    verified: bool
    summary: str
    details: dict[str, Any] = field(default_factory=dict)


class ExecutionMemory:
    """Mantém o histórico auditável de execuções e verificações."""

    def __init__(self) -> None:
        self._events: list[ExecutionEvent] = []

    def record(
        self,
        step_id: str,
        tool: str,
        action: str,
        success: bool,
        verified: bool,
        summary: str,
        details: dict[str, Any] | None = None,
    ) -> ExecutionEvent:
        event = ExecutionEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            step_id=step_id,
            tool=tool,
            action=action,
            success=success,
            verified=verified,
            summary=summary,
            details=details or {},
        )
        self._events.append(event)
        return event

    @property
    def events(self) -> list[ExecutionEvent]:
        return list(self._events)
