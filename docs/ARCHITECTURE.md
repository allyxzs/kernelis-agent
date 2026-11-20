# Arquitetura do Kernelis

O **Kernelis** opera sobre um ciclo determinístico de quatro estágios:

```
Objetivo -> [TaskPlanner] -> [Tool Execution] -> [Verifier] -> [ExecutionReport]
                                  ^                  |
                                  |___ (retry) ______|
```

## Componentes

- **`core/planner.py`**: traduz objetivos em linguagem natural (ou playbooks YAML) em etapas atômicas (`PlanStep`), cada uma acoplada a um critério explícito de verificação (`VerificationSpec`).
- **`tools/`**: camada de execução modular (`shell`, `filesystem`, `system`, `network`). Novas ferramentas podem ser registradas via `ToolRegistry`.
- **`core/verifier.py`**: garante que nenhuma tarefa seja marcada como concluída sem evidência técnica (`exit_code`, `stdout_contains`, `stdout_regex`, `file_exists`, `json_valid`, `port_open`, `http_status`).
- **`core/memory.py`**: registra cada tentativa, código de saída e resultado da verificação para auditoria.
- **`llm/`**: abstração compatível com endpoints OpenAI/Ollama e provedor `mock` para testes offline.

## Políticas de Segurança (`KERNELIS_POLICY`)

| Política | Comportamento |
| :--- | :--- |
| `safe` | Bloqueia execução de comandos `shell`; permite apenas inspeção e operações controladas. |
| `confirm` | Solicita aprovação interativa do operador antes de cada etapa. |
| `autonomous` | Executa o plano continuamente com guardrails de bloqueio contra comandos destrutivos. |
