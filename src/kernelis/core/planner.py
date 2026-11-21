"""Planejador de tarefas técnicas do Kernelis."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Literal

from kernelis.core.verifier import VerificationSpec
from kernelis.llm.base import LLMProvider
from kernelis.prompts.system import SYSTEM_PROMPT

ErrorStrategy = Literal["stop", "continue"]


@dataclass
class PlanStep:
    id: str
    description: str
    tool: str
    action: str
    params: dict[str, Any] = field(default_factory=dict)
    verify: VerificationSpec = field(default_factory=VerificationSpec)
    on_error: ErrorStrategy = "stop"


@dataclass
class ExecutionPlan:
    objective: str
    steps: list[PlanStep] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ExecutionPlan":
        steps: list[PlanStep] = []
        for idx, raw in enumerate(data.get("steps", []), start=1):
            raw_verify = raw.get("verify") or {}
            verify = VerificationSpec(
                type=str(raw_verify.get("type", "exit_code")),
                expected=raw_verify.get("expected", 0),
                target=str(raw_verify.get("target", "")),
            )
            on_error = str(raw.get("on_error", "stop")).lower()
            if on_error not in ("stop", "continue"):
                on_error = "stop"
            steps.append(
                PlanStep(
                    id=str(raw.get("id", f"step-{idx}")),
                    description=str(raw.get("description", "")),
                    tool=str(raw["tool"]),
                    action=str(raw["action"]),
                    params=dict(raw.get("params") or {}),
                    verify=verify,
                    on_error=on_error,  # type: ignore[arg-type]
                )
            )
        return cls(objective=str(data.get("objective", "")), steps=steps)


class TaskPlanner:
    """Converte objetivos em planos estruturados com critérios de verificação."""

    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider

    @staticmethod
    def _extract_json(text: str) -> dict[str, Any]:
        cleaned = text.strip()
        fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
        if fence:
            cleaned = fence.group(1)
        return json.loads(cleaned)

    def plan(self, objective: str, available_tools: dict[str, str]) -> ExecutionPlan:
        tools_summary = "\n".join(
            f"- {name}: {desc}" for name, desc in available_tools.items()
        )
        prompt = (
            f"Objetivo técnico:\n{objective}\n\n"
            f"Ferramentas disponíveis:\n{tools_summary}\n\n"
            "Gere o plano em JSON válido com verificação para cada etapa."
        )
        raw_response = self.provider.complete(SYSTEM_PROMPT, prompt)
        data = self._extract_json(raw_response)
        return ExecutionPlan.from_dict(data)
