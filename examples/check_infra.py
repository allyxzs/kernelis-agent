"""Exemplo de uso programático do Kernelis."""

from kernelis import KernelisAgent, KernelisConfig
from kernelis.core.planner import ExecutionPlan


def main() -> None:
    config = KernelisConfig(provider="mock", policy="autonomous")
    agent = KernelisAgent(config=config)

    plan = ExecutionPlan.from_dict(
        {
            "objective": "Verificar Python e informações do host",
            "steps": [
                {
                    "id": "sys-info",
                    "description": "Inspecionar sistema",
                    "tool": "system",
                    "action": "info",
                    "params": {},
                    "verify": {"type": "json_valid", "expected": True},
                },
                {
                    "id": "python-bin",
                    "description": "Validar binário Python disponível",
                    "tool": "system",
                    "action": "which",
                    "params": {"binary": "python3"},
                    "verify": {"type": "exit_code", "expected": 0},
                },
            ],
        }
    )

    report = agent.execute_plan(plan)
    print(f"Objetivo: {report.objective} | Sucesso: {report.success}")
    for step in report.steps:
        msg = f"verified={step.verification.passed} ({step.verification.message})"
        print(f" - {step.step.id}: {msg}")


if __name__ == "__main__":
    main()
