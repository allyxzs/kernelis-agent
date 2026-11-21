"""Implementações de provedores LLM (OpenAI-compatible, Ollama e Mock)."""

from __future__ import annotations

import json

import httpx

from kernelis.config import KernelisConfig
from kernelis.llm.base import LLMProvider


class OpenAICompatibleProvider(LLMProvider):
    """Cliente leve compatível com OpenAI API e Ollama (/v1/chat/completions)."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        timeout: float = 60.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "temperature": 0.1,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        response = httpx.post(url, headers=headers, json=payload, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return str(data["choices"][0]["message"]["content"])


class MockLLMProvider(LLMProvider):
    """Provedor determinístico para testes locais e dry-run sem chamadas externas."""

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        plan = {
            "objective": user_prompt,
            "steps": [
                {
                    "id": "step-1",
                    "description": "Inspecionar informações básicas do sistema",
                    "tool": "system",
                    "action": "info",
                    "params": {},
                    "verify": {"type": "exit_code", "expected": 0},
                }
            ],
        }
        return json.dumps(plan, ensure_ascii=False)


def build_provider(config: KernelisConfig) -> LLMProvider:
    if config.provider == "mock":
        return MockLLMProvider()
    return OpenAICompatibleProvider(
        base_url=config.base_url,
        api_key=config.api_key,
        model=config.model,
        timeout=float(config.command_timeout),
    )
