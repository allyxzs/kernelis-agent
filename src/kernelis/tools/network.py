"""Ferramenta de diagnósticos de rede e saúde de serviços."""

from __future__ import annotations

import socket
from typing import Any

import httpx

from kernelis.tools.base import BaseTool, ToolResult


class NetworkTool(BaseTool):
    """Verifica conectividade TCP, resolução DNS e healthchecks HTTP."""

    name = "network"
    description = "Checagens de infraestrutura de rede: port_check, dns_lookup, http_check."

    def execute(self, action: str, params: dict[str, Any]) -> ToolResult:
        try:
            if action == "port_check":
                host = str(params.get("host", "127.0.0.1"))
                port = int(params.get("port", 80))
                timeout = float(params.get("timeout", 3.0))
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(timeout)
                    code = sock.connect_ex((host, port))
                is_open = code == 0
                return ToolResult(
                    success=is_open,
                    output=f"{host}:{port} -> {'OPEN' if is_open else 'CLOSED'}",
                    exit_code=0 if is_open else 1,
                    metadata={"host": host, "port": port, "open": is_open},
                )

            if action == "dns_lookup":
                host = str(params.get("host", "")).strip()
                if not host:
                    return ToolResult(
                        success=False,
                        error="Parâmetro 'host' é obrigatório.",
                        exit_code=2,
                    )
                ip = socket.gethostbyname(host)
                return ToolResult(success=True, output=ip, metadata={"host": host, "ip": ip})

            if action == "http_check":
                url = str(params.get("url", "")).strip()
                if not url:
                    return ToolResult(
                        success=False,
                        error="Parâmetro 'url' é obrigatório.",
                        exit_code=2,
                    )
                timeout = float(params.get("timeout", 5.0))
                resp = httpx.get(url, timeout=timeout, follow_redirects=True)
                ok = 200 <= resp.status_code < 400
                return ToolResult(
                    success=ok,
                    output=f"HTTP {resp.status_code}",
                    exit_code=0 if ok else 1,
                    metadata={"url": url, "status_code": resp.status_code},
                )

            return ToolResult(
                success=False,
                error=f"Ação não suportada em network: {action}",
                exit_code=2,
            )
        except Exception as exc:
            return ToolResult(success=False, error=str(exc), exit_code=1)
