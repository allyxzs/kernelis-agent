from pathlib import Path

from kernelis.core.verifier import VerificationSpec, Verifier
from kernelis.tools.base import ToolResult


def test_verifier_exit_code() -> None:
    verifier = Verifier()
    res = verifier.verify(VerificationSpec(type="exit_code", expected=0), ToolResult(success=True, exit_code=0))
    assert res.passed


def test_verifier_stdout_contains() -> None:
    verifier = Verifier()
    res = verifier.verify(
        VerificationSpec(type="stdout_contains", expected="ready"),
        ToolResult(success=True, output="service ready"),
    )
    assert res.passed


def test_verifier_file_exists(tmp_path: Path) -> None:
    f = tmp_path / "ok.flag"
    f.write_text("1", encoding="utf-8")
    verifier = Verifier(base_dir=tmp_path)
    res = verifier.verify(VerificationSpec(type="file_exists", target="ok.flag"), ToolResult(success=True))
    assert res.passed


def test_verifier_json_valid() -> None:
    verifier = Verifier()
    res = verifier.verify(VerificationSpec(type="json_valid"), ToolResult(success=True, output='{"ok": true}'))
    assert res.passed
