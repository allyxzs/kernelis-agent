"""Interface de linha de comando (CLI) do Kernelis."""

from __future__ import annotations

import json
from pathlib import Path

import typer
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from kernelis import __version__
from kernelis.config import KernelisConfig
from kernelis.core.agent import ExecutionReport, KernelisAgent
from kernelis.core.planner import ExecutionPlan, PlanStep

app = typer.Typer(
    name="kernelis",
    help="Kernelis — Agente de Sistemas, Infraestrutura, Ferramentas e Execução Técnica.",
    no_args_is_help=True,
)
console = Console()


def _render_report(report: ExecutionReport, json_out: Path | None = None) -> None:
    table = Table(title=f"Relatório Kernelis — {report.objective}")
    table.add_column("Etapa", style="cyan")
    table.add_column("Ferramenta", style="magenta")
    table.add_column("Tentativas", justify="right")
    table.add_column("Execução")
    table.add_column("Verificação")

    for item in report.steps:
        if item.result.success:
            exec_status = "[green]OK[/green]"
        else:
            exec_status = f"[red]FALHA ({item.result.exit_code})[/red]"

        ver_status = (
            f"[green]PASS[/green] ({item.verification.message})"
            if item.verification.passed
            else f"[red]FAIL[/red] ({item.verification.message})"
        )
        table.add_row(
            f"{item.step.id}: {item.step.description}",
            f"{item.step.tool}.{item.step.action}",
            str(item.attempts),
            exec_status,
            ver_status,
        )

    console.print(table)
    if report.success:
        panel = Panel(
            "[bold green]TAREFA CONCLUÍDA E VERIFICADA[/bold green]",
            border_style="green",
        )
    else:
        panel = Panel(
            "[bold red]TAREFA FALHOU NA EXECUÇÃO OU VERIFICAÇÃO[/bold red]",
            border_style="red",
        )
    console.print(panel)

    if json_out is not None:
        json_out.parent.mkdir(parents=True, exist_ok=True)
        json_out.write_text(
            json.dumps(report.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        console.print(f"[dim]Relatório JSON salvo em: {json_out}[/dim]")


def _confirm_step(step: PlanStep) -> bool:
    prompt = f"Executar [{step.id}] {step.tool}.{step.action} ({step.description})?"
    return typer.confirm(prompt)


@app.command()
def version() -> None:
    """Exibe a versão atual do Kernelis."""
    console.print(f"Kernelis v{__version__}")


@app.command()
def doctor() -> None:
    """Executa diagnóstico rápido do ambiente local."""
    config = KernelisConfig.from_env()
    agent = KernelisAgent(config=config)
    info = agent.registry.get("system").execute("info", {})
    disk = agent.registry.get("system").execute("disk", {"path": "."})
    console.print(Panel(info.output, title="Sistema", border_style="cyan"))
    console.print(Panel(disk.output, title="Disco", border_style="cyan"))


@app.command()
def run(
    objective: str = typer.Argument(
        ...,
        help="Objetivo técnico a ser planejado, executado e verificado.",
    ),
    auto: bool = typer.Option(False, "--auto", help="Executa sem confirmação manual."),
    mock: bool = typer.Option(False, "--mock", help="Usa provedor mock local para dry-run."),
    json_out: Path | None = typer.Option(
        None,
        "--json-out",
        help="Salva o relatório estruturado em JSON.",
    ),
) -> None:
    """Planeja, executa e verifica uma tarefa técnica usando o agente."""
    config = KernelisConfig.from_env()
    if auto:
        config.policy = "autonomous"
    if mock:
        config.provider = "mock"

    agent = KernelisAgent(config=config)
    callback = _confirm_step if config.policy == "confirm" else None
    report = agent.run(objective, confirm_callback=callback)
    _render_report(report, json_out=json_out)
    if not report.success:
        raise typer.Exit(code=1)


@app.command()
def playbook(
    file: Path = typer.Argument(
        ...,
        exists=True,
        readable=True,
        help="Arquivo YAML com etapas e verificações.",
    ),
    auto: bool = typer.Option(False, "--auto", help="Executa sem confirmação manual."),
    json_out: Path | None = typer.Option(
        None,
        "--json-out",
        help="Salva o relatório estruturado em JSON.",
    ),
) -> None:
    """Executa e verifica um playbook técnico declarativo em YAML."""
    config = KernelisConfig.from_env()
    if auto:
        config.policy = "autonomous"

    data = yaml.safe_load(file.read_text(encoding="utf-8"))
    plan = ExecutionPlan.from_dict(data)
    agent = KernelisAgent(config=config)
    callback = _confirm_step if config.policy == "confirm" else None
    report = agent.execute_plan(plan, confirm_callback=callback)
    _render_report(report, json_out=json_out)
    if not report.success:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
