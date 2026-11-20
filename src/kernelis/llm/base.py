"""Interface base para provedores de LLM do Kernelis."""

from __future__ import annotations

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Contrato mínimo para geração de planos e diagnósticos."""

    @abstractmethod
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        """Envia prompts ao modelo e retorna o texto gerado."""
