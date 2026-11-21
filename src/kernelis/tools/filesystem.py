"""Ferramenta de manipulação e auditoria de arquivos."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from kernelis.tools.base import BaseTool, ToolResult


class FilesystemTool(BaseTool):
    """Lê, escreve, lista e calcula checksums de arquivos no workspace."""

    name = "filesystem"
    description = "Operações seguras em sistema de arquivos: read, write, exists, list, sha256."

    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = (base_dir or Path.cwd()).resolve()

    def _resolve_path(self, raw_path: str) -> Path:
        path = Path(raw_path)
        if not path.is_absolute():
            path = self.base_dir / path
        return path.resolve()

    def execute(self, action: str, params: dict[str, Any]) -> ToolResult:
        raw_path = str(params.get("path", "")).strip()
        if not raw_path:
            return ToolResult(
                success=False,
                error="Parâmetro 'path' é obrigatório.",
                exit_code=2,
            )

        target = self._resolve_path(raw_path)

        try:
            if action == "read":
                content = target.read_text(encoding="utf-8")
                return ToolResult(success=True, output=content, metadata={"path": str(target)})

            if action == "write":
                content = str(params.get("content", ""))
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
                return ToolResult(
                    success=True,
                    output=f"Arquivo gravado com sucesso: {target}",
                    metadata={"path": str(target), "bytes": len(content.encode("utf-8"))},
                )

            if action == "exists":
                exists = target.exists()
                return ToolResult(
                    success=exists,
                    output="exists" if exists else "not_found",
                    exit_code=0 if exists else 1,
                    metadata={"path": str(target), "exists": exists},
                )

            if action == "list":
                if not target.is_dir():
                    return ToolResult(
                        success=False,
                        error=f"Não é um diretório: {target}",
                        exit_code=1,
                    )
                entries = sorted(p.name for p in target.iterdir())
                return ToolResult(
                    success=True,
                    output="\n".join(entries),
                    metadata={"path": str(target), "count": len(entries)},
                )

            if action == "sha256":
                digest = hashlib.sha256(target.read_bytes()).hexdigest()
                return ToolResult(
                    success=True,
                    output=digest,
                    metadata={"path": str(target), "sha256": digest},
                )

            return ToolResult(
                success=False,
                error=f"Ação não suportada em filesystem: {action}",
                exit_code=2,
            )
        except Exception as exc:
            return ToolResult(success=False, error=str(exc), exit_code=1)
