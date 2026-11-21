from pathlib import Path

from kernelis import KernelisAgent, KernelisConfig
from kernelis.core.planner import ExecutionPlan


def test_agent_executes_and_verifies_plan(tmp_path: Path) -> None:
    config = KernelisConfig(provider="mock", policy="autonomous", workdir=tmp_path)
    agent = KernelisAgent(config=config)

    plan = ExecutionPlan.from_dict(
        {
            "objective": "Criar e validar arquivo de configuração",
            "steps": [
                {
                    "id": "s1",
                    "description": "Criar arquivo",
                    "tool": "filesystem",
                    "action": "write",
                    "params": {"path": "app.conf", "content": "mode=prod"},
                    "verify": {
                        "type": "file_contains",
                        "target": "app.conf",
                        "expected": "mode=prod",
                    },
                },
                {
                    "id": "s2",
                    "description": "Validar conteúdo",
                    "tool": "filesystem",
                    "action": "read",
                    "params": {"path": "app.conf"},
                    "verify": {"type": "stdout_contains", "expected": "mode=prod"},
                },
            ],
        }
    )

    report = agent.execute_plan(plan)
    assert report.success
    assert len(report.steps) == 2
    assert len(agent.memory.events) == 2
    assert report.to_dict()["success"] is True


def test_agent_safe_policy_blocks_shell(tmp_path: Path) -> None:
    config = KernelisConfig(provider="mock", policy="safe", workdir=tmp_path)
    agent = KernelisAgent(config=config)

    plan = ExecutionPlan.from_dict(
        {
            "objective": "Tentar shell em modo safe",
            "steps": [
                {
                    "id": "s1",
                    "description": "Rodar comando",
                    "tool": "shell",
                    "action": "run",
                    "params": {"command": "echo oi"},
                    "verify": {"type": "exit_code", "expected": 0},
                }
            ],
        }
    )

    report = agent.execute_plan(plan)
    assert not report.success
    assert report.steps[0].result.exit_code == 126


def test_agent_on_error_continue(tmp_path: Path) -> None:
    config = KernelisConfig(
        provider="mock",
        policy="autonomous",
        max_retries=0,
        workdir=tmp_path,
    )
    agent = KernelisAgent(config=config)

    plan = ExecutionPlan.from_dict(
        {
            "objective": "Continuar após falha não crítica",
            "steps": [
                {
                    "id": "s1",
                    "description": "Ler arquivo inexistente",
                    "tool": "filesystem",
                    "action": "read",
                    "params": {"path": "missing.txt"},
                    "on_error": "continue",
                    "verify": {"type": "exit_code", "expected": 0},
                },
                {
                    "id": "s2",
                    "description": "Inspecionar sistema",
                    "tool": "system",
                    "action": "info",
                    "params": {},
                    "verify": {"type": "json_valid", "expected": True},
                },
            ],
        }
    )

    report = agent.execute_plan(plan)
    assert not report.success
    assert len(report.steps) == 2
    assert report.steps[1].verification.passed
