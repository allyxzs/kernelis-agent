"""Configuração centralizada do Kernelis."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

ExecutionPolicy = Literal["safe", "confirm", "autonomous"]
ProviderType = Literal["openai", "ollama", "mock"]


@dataclass
class KernelisConfig:
    """Parâmetros de execução, modelo e segurança do agente Kernelis."""

    provider: ProviderType = "ollama"
    model: str = "qwen2.5-coder:14b"
    base_url: str = "http://localhost:11434/v1"
    api_key: str = "ollama"
    policy: ExecutionPolicy = "confirm"
    command_timeout: int = 60
    max_retries: int = 2
    workdir: Path = field(default_factory=lambda: Path.cwd())
    log_level: str = "INFO"

    @classmethod
    def from_env(cls, env_file: str | Path | None = None) -> "KernelisConfig":
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()

        provider = os.getenv("KERNELIS_PROVIDER", "ollama").lower()
        if provider not in ("openai", "ollama", "mock"):
            provider = "ollama"

        policy = os.getenv("KERNELIS_POLICY", "confirm").lower()
        if policy not in ("safe", "confirm", "autonomous"):
            policy = "confirm"

        return cls(
            provider=provider,  # type: ignore[arg-type]
            model=os.getenv("KERNELIS_MODEL", "qwen2.5-coder:14b"),
            base_url=os.getenv("KERNELIS_BASE_URL", "http://localhost:11434/v1"),
            api_key=os.getenv("KERNELIS_API_KEY", "ollama"),
            policy=policy,  # type: ignore[arg-type]
            command_timeout=int(os.getenv("KERNELIS_COMMAND_TIMEOUT", "60")),
            max_retries=int(os.getenv("KERNELIS_MAX_RETRIES", "2")),
            workdir=Path(os.getenv("KERNELIS_WORKDIR", ".")).resolve(),
            log_level=os.getenv("KERNELIS_LOG_LEVEL", "INFO").upper(),
        )
