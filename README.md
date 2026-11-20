# Kernelis

**Kernelis** é um agente autônomo voltado para **Sistemas, Infraestrutura, Ferramentas e Execução Técnica**. Ele planeja tarefas operacionais, executa ações por meio de ferramentas modulares e **verifica objetivamente o funcionamento** de cada etapa antes de declarar sucesso.

## Principais Recursos

- **Ciclo Plan -> Execute -> Verify**: toda etapa técnica possui um critério verificável (`exit_code`, `stdout_contains`, `stdout_regex`, `file_exists`, `json_valid`, `port_open`, `http_status`).
- **Ferramentas Nativas**:
  - `shell`: execução com timeout, diretório isolado e bloqueio contra comandos destrutivos.
  - `filesystem`: leitura, escrita, listagem, existência e checksum `sha256`.
  - `system`: diagnóstico de SO, CPU, disco, variáveis de ambiente e binários (`which`).
  - `network`: checagem de portas TCP, resolução DNS e healthchecks HTTP.
- **Políticas de Execução**: `safe`, `confirm` e `autonomous`.
- **Playbooks Declarativos**: execute pipelines técnicos reprodutíveis via YAML.
- **Agnóstico de LLM**: compatível com **Ollama** (local), APIs compatíveis com **OpenAI** e modo `mock` para testes offline.

## Estrutura do Projeto

```text
kernelis/
├── .github/workflows/ci.yml
├── docs/ARCHITECTURE.md
├── examples/
│   ├── check_infra.py
│   └── tasks.yaml
├── src/kernelis/
│   ├── cli.py
│   ├── config.py
│   ├── core/
│   │   ├── agent.py
│   │   ├── memory.py
│   │   ├── planner.py
│   │   └── verifier.py
│   ├── llm/
│   │   ├── base.py
│   │   └── providers.py
│   ├── prompts/
│   │   └── system.py
│   └── tools/
│       ├── base.py
│       ├── filesystem.py
│       ├── network.py
│       ├── shell.py
│       └── system.py
├── tests/
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── pyproject.toml
```

## Instalação

```bash
git clone https://github.com/SEU-USUARIO/kernelis.git
cd kernelis
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

pip install -e ".[dev]"
cp .env.example .env
```

## Uso Rápido

### 1. Diagnóstico do ambiente
```bash
kernelis doctor
```

### 2. Executar um playbook técnico com verificação
```bash
kernelis playbook examples/tasks.yaml --auto
```

### 3. Executar uma tarefa via agente (LLM)
```bash
kernelis run "Verifique espaço em disco e valide se o binário git está disponível"
```

Para testar sem LLM externo (dry-run local):
```bash
kernelis run "Inspecionar ambiente local" --mock --auto
```

## Testes

```bash
pytest -v
```

## Docker

```bash
docker compose build
docker compose run --rm kernelis doctor
```

## Publicando no GitHub

```bash
git init
git add .
git commit -m "feat: initial release of Kernelis agent"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/kernelis.git
git push -u origin main
```

## Licença

Distribuído sob a licença MIT. Veja [LICENSE](LICENSE) para mais detalhes.
