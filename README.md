# Kernelis

**Kernelis** é um agente autônomo voltado para **Sistemas, Infraestrutura, Ferramentas e Execução Técnica**. Ele planeja tarefas operacionais, executa ações por meio de ferramentas modulares e **verifica objetivamente o funcionamento** de cada etapa antes de declarar sucesso.

## Novidades da v0.2.0

- Conformidade **PEP 639** no `pyproject.toml` e linting rigoroso com `ruff` (CI verde em Python 3.10, 3.11 e 3.12).
- Novo verificador **`file_contains`** para validar conteúdo de arquivos diretamente.
- Suporte a **`on_error: continue | stop`** em etapas de planos e playbooks YAML.
- Exportação de relatórios estruturados via **`--json-out`** na CLI (`run` e `playbook`).

## Principais Recursos

- **Ciclo Plan -> Execute -> Verify**: toda etapa técnica possui critério verificável (`exit_code`, `stdout_contains`, `stdout_regex`, `file_exists`, `file_contains`, `json_valid`, `port_open`, `http_status`).
- **Ferramentas Nativas**: `shell`, `filesystem`, `system` e `network`.
- **Políticas de Execução**: `safe`, `confirm` e `autonomous`.
- **Playbooks Declarativos**: execute pipelines técnicos reprodutíveis via YAML.
- **Agnóstico de LLM**: compatível com **Ollama** (local), APIs **OpenAI-compatible** e modo `mock`.

## Instalação

```bash
git clone https://github.com/allyxzs/kernelis-agent.git
cd kernelis-agent
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

pip install -e ".[dev]"
cp .env.example .env
```

## Uso Rápido

```bash
# Diagnóstico do ambiente
kernelis doctor

# Executar playbook com verificação e exportar relatório JSON
kernelis playbook examples/tasks.yaml --auto --json-out .kernelis/report.json

# Executar tarefa via agente (dry-run local com mock)
kernelis run "Inspecionar ambiente local" --mock --auto
```

## Testes e Lint

```bash
ruff check src tests
pytest -v --cov=kernelis
```

## Licença

Distribuído sob a licença MIT. Veja [LICENSE](LICENSE).
