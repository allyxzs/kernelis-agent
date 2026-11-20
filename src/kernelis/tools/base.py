"""Abstrações base para ferramentas do Kernelis."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolResult:
    """Resultado padronizado de qualquer execução de ferramenta."""

    success: bool
    output: str = ""
    error: str = ""
    exit_code: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseTool(ABC):
    """Interface base que toda ferramenta do Kernelis deve implementar."""

    name: str = ""
    description: str = ""

    @abstractmethod
    def execute(self, action: str, params: dict[str, Any]) -> ToolResult:
        """Executa uma ação específica da ferramenta."""


class ToolRegistry:
    """Registro central de ferramentas disponíveis para o agente."""

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        if not tool.name:
            raise ValueError("A ferramenta precisa definir o atributo 'name'.")
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool:
        if name not in self._tools:
            available = ", ".join(sorted(self._tools))
            raise KeyError(f"Ferramenta '{name}' não registrada. Disponíveis: {available}")
        return self._tools[name]

    def list_tools(self) -> dict[str, str]:
        return {name: tool.description for name, tool in sorted(self._tools.items())}
