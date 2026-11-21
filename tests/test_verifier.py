from pathlib import Path

from kernelis.core.verifier import VerificationSpec, Verifier
from kernelis.tools.base import ToolResult


def test_verifier_exit_code() -> None:
    verifier = Verifier()
    spec = VerificationSpec(type="exit_code", expected=0)
    res = verifier.verify(spec, ToolResult(success=True, exit_code=0))
    assert res.passed


def test_verifier_stdout_contains() -> None:
    verifier = Verifier()
    spec = VerificationSpec(type="stdout_contains", expected="ready")
    res = verifier.verify(spec, ToolResult(success=True, output="service ready"))
    assert res.passed


def test_verifier_file_exists_and_contains(tmp_path: Path) -> None:
    flag = tmp_path / "ok.flag"
    flag.write_text("status=healthy", encoding="utf-8")
    verifier = Verifier(base_dir=tmp_path)

    exists_spec = VerificationSpec(type="file_exists", target="ok.flag")
    assert verifier.verify(exists_spec, ToolResult(success=True)).passed

    contains_spec = VerificationSpec(
        type="file_contains",
        target="ok.flag",
        expected="healthy",
    )
    assert verifier.verify(contains_spec, ToolResult(success=True)).passed


def test_verifier_json_valid() -> None:
    verifier = Verifier()
    spec = VerificationSpec(type="json_valid")
    res = verifier.verify(spec, ToolResult(success=True, output='{"ok": true}'))
    assert res.passed
