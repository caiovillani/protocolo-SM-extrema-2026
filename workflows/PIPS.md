# Workflow: PIPS - Protocolo de Processamento Iterativo com Persistência de Estado

## Objetivo

Processar tarefas de longa duração que excedem limites de tokens de uma sessão,
mantendo estado persistente em arquivos externos e permitindo retomada após interrupções.

O PIPS implementa o ciclo **Work-Save-Validate-Reset-Resume** para garantir que nenhum
progresso seja perdido durante processamentos extensos.

## Quando Usar PIPS

Ative o PIPS quando **qualquer** das condições abaixo for verdadeira:

- [ ] Processando mais de 3 arquivos fonte
- [ ] Volume estimado maior que 50.000 tokens
- [ ] Sintetizando informações de múltiplas fontes distribuídas
- [ ] Usuário solicita explicitamente processamento iterativo
- [ ] Tarefa requer múltiplas passagens de refinamento

## Inputs Necessários

- [ ] **Objetivo claro:** Descrição do que deve ser produzido ao final (mín. 10 caracteres)
- [ ] **Arquivos fonte:** Lista de arquivos ou diretório a processar
- [ ] **Schema de output:** Formato esperado da entrega (opcional)

## Ferramentas Utilizadas

| Ferramenta | Descrição |
|------------|-----------|
| `tools/pips_init.py` | Inicialização do projeto PIPS |
| `tools/pips_validate.py` | Validação de estado e integridade |
| `tools/pips_consolidate.py` | Consolidação de insights raw em síntese |
| `tools/pips_export.py` | Exportação de entregas finais |

## Comandos REPL

| Comando | Descrição |
|---------|-----------|
| `/pips init <nome> <objetivo>` | Criar novo projeto |
| `/pips status [nome]` | Ver status do projeto |
| `/pips resume <nome>` | Retomar processamento |
| `/pips list` | Listar projetos existentes |
| `/pips validate <nome>` | Validar integridade |
| `/pips finalize <nome>` | Gerar entrega final |
| `/pips delete <nome>` | Remover projeto |

## Ciclo de Processamento

```
┌─────────────────────────────────────────────────────────────────┐
│                    CICLO PIPS v2.0                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────┐    ┌─────────┐    ┌──────────┐    ┌─────────┐     │
│  │  LOAD   │───▶│  WORK   │───▶│   SAVE   │───▶│VALIDATE │     │
│  │ Estado  │    │Processar│    │  Estado  │    │Qualidade│     │
│  └────┬────┘    └─────────┘    └──────────┘    └────┬────┘     │
│       │                                             │          │
│       │              ┌──────────┐                   │          │
│       │              │  RESET   │◀──────────────────┘          │
│       │              │ Contexto │                              │
│       │              └────┬─────┘                              │
│       │                   │                                    │
│       └───────────────────┴────────────────────────────────────┘
│                      RESUME                                    │
│                                                                │
└─────────────────────────────────────────────────────────────────┘
```

### 1. LOAD - Carregar Estado

Ao iniciar ou retomar processamento:
1. Ler `_config/context.md` → relembrar objetivo
2. Ler `_state/progress.yaml` → identificar ponto de parada
3. Ler `_output/insights_consolidated.md` → absorver progresso acumulado

**Comando:** `/pips resume <nome>`

### 2. WORK - Processar Item

Para cada item da fila:
1. Carregar próximo item pendente
2. Processar conteúdo conforme objetivo
3. Extrair insights e informações relevantes
4. Marcar flags de ambiguidade/contradição se necessário

**Saída:** Insights estruturados para o item

### 3. SAVE - Persistir Progresso

Após processar cada item:
1. Append insights em `_output/insights_raw.md`
2. Atualizar status do item em `_state/progress.yaml`
3. Atualizar contadores e timestamps
4. **CRÍTICO:** Confirmar escrita antes de continuar

**Comando interno:** `engine.save(item_id, resultado, insights)`

### 4. VALIDATE - Verificar Integridade

A cada N ciclos (configurável):
1. Verificar consistência entre arquivos de estado
2. Avaliar métricas de qualidade
3. Registrar checkpoint em `_config/checkpoints.log`
4. Se degradação detectada: sinalizar para revisão

**Comando:** `/pips validate <nome>`
**Ferramenta:** `python tools/pips_validate.py --project <nome>`

### 5. RESET - Preparar para Nova Sessão

Antes de reset de contexto do LLM:
1. Garantir que todos os arquivos estão salvos
2. Marcar projeto como "pausado"
3. Limpar caches internos

**Importante:** NÃO tentar manter informações na memória de curto prazo

### 6. RESUME - Retomar Processamento

Após qualquer interrupção:
1. Ler arquivos de estado do disco
2. Restaurar contexto operacional
3. Continuar do ponto de parada
4. **NUNCA** assumir conhecimento de ciclos anteriores não registrado

**Comando:** `/pips resume <nome>`

## Estrutura de Diretórios

```
.pips/
└── projeto_<nome>/
    ├── _config/
    │   ├── context.md          # Objetivo imutável
    │   ├── schema.yaml         # Formato esperado
    │   └── checkpoints.log     # Registro de validações
    ├── _state/
    │   ├── todos.md            # Tarefas (human-readable)
    │   ├── queue.md            # Fila (human-readable)
    │   ├── progress.yaml       # Estado (machine-readable)
    │   └── errors.log          # Erros encontrados
    ├── _output/
    │   ├── insights_raw.md     # Achados brutos (append-only)
    │   ├── insights_consolidated.md  # Síntese progressiva
    │   └── final/              # Entregas finais
    └── _source/
        └── [arquivos fonte]
```

## Estados do Projeto

| Estado | Emoji | Descrição |
|--------|-------|-----------|
| `nao_iniciado` | ⏸️ | Projeto criado mas não iniciado |
| `em_progresso` | ▶️ | Processamento ativo |
| `pausado` | ⏸️ | Pausado pelo usuário ou reset |
| `validando` | 🔍 | Em validação de checkpoint |
| `concluido` | ✅ | Processamento finalizado |
| `erro` | ❌ | Erro crítico detectado |

## Flags de Insight

| Flag | Descrição | Ação |
|------|-----------|------|
| `[AMBIGUIDADE]` | Interpretação ambígua | Marcar para revisão |
| `[CONTRADIÇÃO]` | Conflito entre fontes | Manter ambas versões |
| `[VALIDAR]` | Requer validação humana | Escalar para revisão |

## Outputs Esperados

- [ ] **insights_raw.md:** Achados brutos de cada ciclo (append-only)
- [ ] **insights_consolidated.md:** Síntese progressiva dos insights
- [ ] **final/:** Entregas finais exportadas

## Casos Especiais / Edge Cases

### Interrupção Inesperada

1. Executar `/pips status <nome>` para ver estado
2. Executar `python tools/pips_validate.py --project <nome> --fix`
3. Retomar com `/pips resume <nome>`

### Erro de Validação

1. Verificar `_state/errors.log`
2. Corrigir inconsistências manualmente ou com `--fix`
3. Criar novo checkpoint com `tools/pips_validate.py`

### Mudança de Objetivo

1. PIPS não permite alterar `context.md` após início
2. Criar novo projeto se objetivo mudar significativamente
3. Migrar insights relevantes manualmente

### Projeto Muito Grande

1. Dividir em sub-projetos por tema/categoria
2. Processar sequencialmente
3. Consolidar ao final

## Métricas de Qualidade

| Métrica | Descrição | Alvo |
|---------|-----------|------|
| Cobertura | % de arquivos processados | 100% |
| Densidade | Insights por arquivo | > 1 |
| Consistência | Flags resolvidas vs. pendentes | > 80% resolvidas |
| Checkpoints | Validações bem-sucedidas | 100% |

## Notas de Aprendizado

<!-- Atualize esta seção conforme descobrir limitações ou comportamentos inesperados -->

- **Chunk size ótimo:** ~10.000 tokens por item
- **Consolidação:** Recomendado a cada 5 itens processados
- **Checkpoint:** Obrigatório após cada ciclo completo
- **Reset:** Sempre salvar antes de qualquer operação que possa limpar contexto

---

*Última atualização: Janeiro 2026*
*Versão: 2.0*
