from pathlib import Path

from kernelis.tools.filesystem import FilesystemTool
from kernelis.tools.shell import ShellTool
from kernelis.tools.system import SystemTool


def test_shell_blocks_dangerous_commands(tmp_path: Path) -> None:
    tool = ShellTool(workdir=tmp_path)
    result = tool.execute("run", {"command": "rm -rf /"})
    assert not result.success
    assert result.exit_code == 126


def test_shell_runs_echo(tmp_path: Path) -> None:
    tool = ShellTool(workdir=tmp_path)
    result = tool.execute("run", {"command": "echo kernelis"})
    assert result.success
    assert result.output == "kernelis"


def test_filesystem_write_read_sha256(tmp_path: Path) -> None:
    tool = FilesystemTool(base_dir=tmp_path)
    write_res = tool.execute("write", {"path": "status.txt", "content": "online"})
    assert write_res.success

    read_res = tool.execute("read", {"path": "status.txt"})
    assert read_res.success
    assert read_res.output == "online"

    hash_res = tool.execute("sha256", {"path": "status.txt"})
    assert hash_res.success
    assert len(hash_res.output) == 64


def test_system_info_returns_json() -> None:
    tool = SystemTool()
    result = tool.execute("info", {})
    assert result.success
    assert '"python"' in result.output
