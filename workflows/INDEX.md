# Workflows Index

Este diretório contém os SOPs (Standard Operating Procedures) em Markdown que definem como executar tarefas complexas.

## Como Usar

1. Cada workflow define: objetivo, inputs, ferramentas, passos e outputs
2. Use `_template.md` como base para criar novos workflows
3. Atualize workflows quando descobrir melhorias ou limitações

## Workflows Disponíveis

| Workflow | Descrição | Status |
|----------|-----------|--------|
| _template.md | Template para novos workflows | - |
| PIPS.md | Protocolo de Processamento Iterativo com Persistência de Estado | ✅ Ativo |

---

### PIPS - Processamento Iterativo

O workflow PIPS permite processar tarefas de longa duração que excedem limites de contexto,
mantendo estado persistente em arquivos externos. Útil para:

- Análise de múltiplos arquivos
- Processamento de grandes volumes de dados
- Síntese de informações distribuídas

**Comandos principais:**
- `/pips init <nome> <objetivo>` - Criar projeto
- `/pips resume <nome>` - Retomar processamento
- `/pips status <nome>` - Ver status

---

*Adicione novos workflows a esta tabela conforme forem criados*
