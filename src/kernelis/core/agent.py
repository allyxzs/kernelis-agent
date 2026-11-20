"""Núcleo do agente Kernelis: ciclo Plan -> Execute -> Verify -> Report."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from kernelis.config import KernelisConfig
from kernelis.core.memory import ExecutionMemory
from kernelis.core.planner import ExecutionPlan, PlanStep, TaskPlanner
from kernelis.core.verifier import VerificationResult, Verifier
from kernelis.llm.base import LLMProvider
from kernelis.llm.providers import build_provider
from kernelis.tools import (
    FilesystemTool,
    NetworkTool,
    ShellTool,
    SystemTool,
    ToolRegistry,
    ToolResult,
)


@dataclass
class StepExecution:
    step: PlanStep
    result: ToolResult
    verification: VerificationResult
    attempts: int


@dataclass
class ExecutionReport:
    objective: str
    success: bool
    steps: list[StepExecution] = field(default_factory=list)


ConfirmCallback = Callable[[PlanStep], bool]


class KernelisAgent:
    """Agente de sistemas, infraestrutura, ferramentas e execução técnica verificada."""

    def __init__(
        self,
        config: KernelisConfig | None = None,
        provider: LLMProvider | None = None,
        registry: ToolRegistry | None = None,
    ) -> None:
        self.config = config or KernelisConfig.from_env()
        self.provider = provider or build_provider(self.config)
        self.registry = registry or self._default_registry()
        self.planner = TaskPlanner(self.provider)
        self.verifier = Verifier(base_dir=self.config.workdir)
        self.memory = ExecutionMemory()

    def _default_registry(self) -> ToolRegistry:
        registry = ToolRegistry()
        registry.register(ShellTool(workdir=self.config.workdir, default_timeout=self.config.command_timeout))
        registry.register(FilesystemTool(base_dir=self.config.workdir))
        registry.register(SystemTool())
        registry.register(NetworkTool())
        return registry

    def execute_plan(
        self,
        plan: ExecutionPlan,
        confirm_callback: ConfirmCallback | None = None,
    ) -> ExecutionReport:
        executions: list[StepExecution] = []
        all_ok = True

        for step in plan.steps:
            if self.config.policy == "safe" and step.tool == "shell":
                result = ToolResult(
                    success=False,
                    error="Execução shell bloqueada no modo 'safe'.",
                    exit_code=126,
                )
                verification = VerificationResult(
                    passed=False,
                    check_type=step.verify.type,
                    message="bloqueado pela política safe",
                )
                executions.append(StepExecution(step=step, result=result, verification=verification, attempts=0))
                all_ok = False
                break

            if self.config.policy == "confirm" and confirm_callback is not None:
                if not confirm_callback(step):
                    result = ToolResult(success=False, error="Etapa recusada pelo operador.", exit_code=130)
                    verification = VerificationResult(
                        passed=False,
                        check_type=step.verify.type,
                        message="cancelado pelo operador",
                    )
                    executions.append(StepExecution(step=step, result=result, verification=verification, attempts=0))
                    all_ok = False
                    break

            tool = self.registry.get(step.tool)
            attempts = 0
            result = ToolResult(success=False, error="Não executado", exit_code=1)
            verification = VerificationResult(passed=False, check_type=step.verify.type, message="não verificado")

            max_attempts = max(1, self.config.max_retries + 1)
            while attempts < max_attempts:
                attempts += 1
                result = tool.execute(step.action, step.params)
                verification = self.verifier.verify(step.verify, result)
                if result.success and verification.passed:
                    break

            self.memory.record(
                step_id=step.id,
                tool=step.tool,
                action=step.action,
                success=result.success,
                verified=verification.passed,
                summary=verification.message,
                details={"attempts": attempts, "exit_code": result.exit_code},
            )
            executions.append(StepExecution(step=step, result=result, verification=verification, attempts=attempts))

            if not (result.success and verification.passed):
                all_ok = False
                break

        return ExecutionReport(objective=plan.objective, success=all_ok, steps=executions)

    def run(
        self,
        objective: str,
        confirm_callback: ConfirmCallback | None = None,
    ) -> ExecutionReport:
        plan = self.planner.plan(objective, self.registry.list_tools())
        return self.execute_plan(plan, confirm_callback=confirm_callback)
