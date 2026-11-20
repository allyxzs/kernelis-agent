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
                    "verify": {"type": "file_exists", "target": "app.conf"},
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
