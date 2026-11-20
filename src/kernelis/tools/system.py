"""Ferramenta de inspeção de sistema operacional, recursos e binários."""

from __future__ import annotations

import json
import os
import platform
import shutil
from typing import Any

from kernelis.tools.base import BaseTool, ToolResult


class SystemTool(BaseTool):
    """Inspeciona ambiente, disco, CPU, variáveis e disponibilidade de ferramentas."""

    name = "system"
    description = "Diagnóstico de sistema: info, disk, which, env."

    def execute(self, action: str, params: dict[str, Any]) -> ToolResult:
        try:
            if action == "info":
                data = {
                    "os": platform.system(),
                    "release": platform.release(),
                    "machine": platform.machine(),
                    "python": platform.python_version(),
                    "cpu_count": os.cpu_count(),
                    "hostname": platform.node(),
                }
                return ToolResult(success=True, output=json.dumps(data, indent=2), metadata=data)

            if action == "disk":
                path = str(params.get("path", "."))
                usage = shutil.disk_usage(path)
                data = {
                    "path": path,
                    "total_gb": round(usage.total / (1024**3), 2),
                    "used_gb": round(usage.used / (1024**3), 2),
                    "free_gb": round(usage.free / (1024**3), 2),
                }
                return ToolResult(success=True, output=json.dumps(data, indent=2), metadata=data)

            if action == "which":
                binary = str(params.get("binary", "")).strip()
                if not binary:
                    return ToolResult(success=False, error="Parâmetro 'binary' é obrigatório.", exit_code=2)
                resolved = shutil.which(binary)
                return ToolResult(
                    success=resolved is not None,
                    output=resolved or "",
                    error="" if resolved else f"Binário não encontrado: {binary}",
                    exit_code=0 if resolved else 1,
                    metadata={"binary": binary, "path": resolved},
                )

            if action == "env":
                key = str(params.get("key", "")).strip()
                if not key:
                    return ToolResult(success=False, error="Parâmetro 'key' é obrigatório.", exit_code=2)
                val = os.getenv(key)
                return ToolResult(
                    success=val is not None,
                    output=val or "",
                    exit_code=0 if val is not None else 1,
                    metadata={"key": key, "present": val is not None},
                )

            return ToolResult(success=False, error=f"Ação não suportada em system: {action}", exit_code=2)
        except Exception as exc:  # noqa: BLE001
            return ToolResult(success=False, error=str(exc), exit_code=1)
