"""Ferramenta de execução de comandos shell com guardrails e timeout."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

from kernelis.tools.base import BaseTool, ToolResult

DANGEROUS_PATTERNS = [
    r"rm\s+-rf\s+/(?:\s|$)",
    r"mkfs\.",
    r"dd\s+if=.*of=/dev/",
    r":\(\)\{\s*:\|:\&\s*\};:",
    r"shutdown\s+-h",
    r"reboot\b",
]


class ShellTool(BaseTool):
    """Executa comandos de sistema com timeout e bloqueio de comandos destrutivos."""

    name = "shell"
    description = "Executa comandos shell com captura de stdout, stderr, exit_code e guardrails."

    def __init__(self, workdir: Path | None = None, default_timeout: int = 60) -> None:
        self.workdir = (workdir or Path.cwd()).resolve()
        self.default_timeout = default_timeout

    @staticmethod
    def is_dangerous(command: str) -> bool:
        return any(re.search(pattern, command) for pattern in DANGEROUS_PATTERNS)

    def execute(self, action: str, params: dict[str, Any]) -> ToolResult:
        if action != "run":
            return ToolResult(
                success=False,
                error=f"Ação não suportada em shell: {action}",
                exit_code=2,
            )

        command = str(params.get("command", "")).strip()
        if not command:
            return ToolResult(
                success=False,
                error="Parâmetro 'command' é obrigatório.",
                exit_code=2,
            )

        if self.is_dangerous(command):
            return ToolResult(
                success=False,
                error=f"Comando bloqueado pela política de segurança: {command}",
                exit_code=126,
            )

        timeout = int(params.get("timeout", self.default_timeout))
        cwd = Path(params.get("cwd", self.workdir)).resolve()

        try:
            proc = subprocess.run(
                command,
                shell=True,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return ToolResult(
                success=proc.returncode == 0,
                output=proc.stdout.strip(),
                error=proc.stderr.strip(),
                exit_code=proc.returncode,
                metadata={"command": command, "cwd": str(cwd)},
            )
        except subprocess.TimeoutExpired as exc:
            out = (exc.stdout or "").strip() if isinstance(exc.stdout, str) else ""
            return ToolResult(
                success=False,
                output=out,
                error=f"Timeout após {timeout}s executando: {command}",
                exit_code=124,
                metadata={"command": command, "timeout": timeout},
            )
        except Exception as exc:
            return ToolResult(success=False, error=str(exc), exit_code=1)
