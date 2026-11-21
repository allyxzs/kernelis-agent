"""Motor de verificação técnica pós-execução do Kernelis."""

from __future__ import annotations

import json
import re
import socket
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

from kernelis.tools.base import ToolResult


@dataclass
class VerificationSpec:
    """Especificação de como verificar se uma etapa técnica funcionou."""

    type: str = "exit_code"
    expected: Any = 0
    target: str = ""


@dataclass
class VerificationResult:
    """Resultado objetivo da checagem de funcionamento."""

    passed: bool
    check_type: str
    message: str


class Verifier:
    """Valida resultados de execução técnica contra critérios verificáveis."""

    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = (base_dir or Path.cwd()).resolve()

    def _resolve_target(self, raw_path: str) -> Path:
        target_path = Path(raw_path)
        if not target_path.is_absolute():
            target_path = self.base_dir / target_path
        return target_path

    def verify(self, spec: VerificationSpec, result: ToolResult) -> VerificationResult:
        check = spec.type

        if check == "exit_code":
            expected_code = int(spec.expected)
            passed = result.exit_code == expected_code
            return VerificationResult(
                passed=passed,
                check_type=check,
                message=f"exit_code={result.exit_code} (esperado={expected_code})",
            )

        if check == "stdout_contains":
            needle = str(spec.expected)
            passed = needle in result.output
            return VerificationResult(
                passed=passed,
                check_type=check,
                message=f"stdout {'contém' if passed else 'não contém'} '{needle}'",
            )

        if check == "stdout_regex":
            pattern = str(spec.expected)
            passed = re.search(pattern, result.output) is not None
            return VerificationResult(
                passed=passed,
                check_type=check,
                message=f"regex '{pattern}' {'correspondeu' if passed else 'não correspondeu'}",
            )

        if check == "file_exists":
            target_path = self._resolve_target(spec.target or str(spec.expected))
            passed = target_path.exists()
            return VerificationResult(
                passed=passed,
                check_type=check,
                message=f"arquivo '{target_path}' {'encontrado' if passed else 'ausente'}",
            )

        if check == "file_contains":
            target_path = self._resolve_target(spec.target)
            if not target_path.exists():
                return VerificationResult(
                    passed=False,
                    check_type=check,
                    message=f"arquivo '{target_path}' ausente",
                )
            needle = str(spec.expected)
            content = target_path.read_text(encoding="utf-8")
            passed = needle in content
            return VerificationResult(
                passed=passed,
                check_type=check,
                message=f"arquivo {'contém' if passed else 'não contém'} '{needle}'",
            )

        if check == "json_valid":
            try:
                json.loads(result.output)
                return VerificationResult(
                    passed=True,
                    check_type=check,
                    message="saída JSON válida",
                )
            except json.JSONDecodeError as exc:
                return VerificationResult(
                    passed=False,
                    check_type=check,
                    message=f"JSON inválido: {exc}",
                )

        if check == "port_open":
            host, _, port_str = (spec.target or "127.0.0.1:80").partition(":")
            port = int(port_str or spec.expected)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(3.0)
                passed = sock.connect_ex((host, port)) == 0
            return VerificationResult(
                passed=passed,
                check_type=check,
                message=f"porta {host}:{port} {'aberta' if passed else 'fechada'}",
            )

        if check == "http_status":
            url = spec.target
            expected_status = int(spec.expected)
            try:
                resp = httpx.get(url, timeout=5.0, follow_redirects=True)
                passed = resp.status_code == expected_status
                return VerificationResult(
                    passed=passed,
                    check_type=check,
                    message=f"HTTP {resp.status_code} em {url} (esperado={expected_status})",
                )
            except Exception as exc:
                return VerificationResult(
                    passed=False,
                    check_type=check,
                    message=f"erro HTTP: {exc}",
                )

        return VerificationResult(
            passed=False,
            check_type=check,
            message=f"Tipo de verificação desconhecido: {check}",
        )
