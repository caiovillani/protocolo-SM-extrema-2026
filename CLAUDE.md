# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Sistema de Protocolos de Compartilhamento do Cuidado em Saude Mental para Extrema/MG. Hybrid project combining clinical documentation (aligned with Brazilian RAPS regulations) and a Python Context Engine for protocol processing.

## Development Commands

```bash
# Run tests
py -3.13 -m pytest tests/ -v

# Run single test file
py -3.13 -m pytest tests/test_commands.py -v

# Run REPL interface
python src/context_engine/main.py

# Syntax check
py -3.13 -m py_compile src/context_engine/*.py
```

## Architecture

### Context Engine (`src/context_engine/`)
Multi-stage pipeline for processing protocol-related commands:
- **main.py** - REPL entry point with session state management
- **commands.py** - Command parsing (`/template`, `/auditoria`, `/orientacao`, `/conformidade`, `/comparar`, `/pips`, `/contexto`, `/export`)
- **pipeline.py** - 5-stage processing: parse → classify → validate input → load context → process → validate output
- **formatter.py** - Centralized formatting (box-drawing, emoji mappings, command formatters)
- **exporter.py** - Export engine (MD, YAML, JSON, DOCX formats)
- **resources.py** - YAML resource loader with caching (normativas, taxonomias, templates)
- **pips.py** - PIPS engine for iterative processing with state persistence
- **pips_models.py** - Dataclasses for PIPS state management
- **context_cache.py** - High-quality context extraction with caching

### WAT Framework
- **Workflows** (`/workflows/`) - Standard Operating Procedures in Markdown
- **Tools** (`/tools/`) - Deterministic Python CLI scripts
- Both use `_template.*` files and `INDEX.md` registries for extensibility

### Resource System
YAML files loaded from configurable root (via `RESOURCE_ROOT` env var). Three types: normativas, taxonomias, templates. In-memory caching enabled by default.

### PIPS - Protocolo de Processamento Iterativo com Persistência de Estado

Sistema para processamento de tarefas de longa duração com persistência de estado em arquivos externos.

**Quando usar:**
- Processamento de múltiplos arquivos (>3)
- Volume de dados >50.000 tokens
- Síntese de informações distribuídas

**Comandos PIPS:**
```bash
# Via REPL
/pips init <nome> <objetivo>    # Criar projeto
/pips status [nome]             # Ver status
/pips resume <nome>             # Retomar processamento
/pips list                      # Listar projetos
/pips validate <nome>           # Validar integridade
/pips finalize <nome>           # Gerar entrega final
/pips delete <nome>             # Remover projeto
/pips memory                    # Status do Protocolo de Memória Infinita

# Via CLI Tools
python tools/pips_init.py --name <nome> --objective <texto> --sources <dir>
python tools/pips_validate.py --project <nome> --fix
python tools/pips_consolidate.py --project <nome>
python tools/pips_export.py --project <nome> --format md
```

**Estrutura de diretórios:**
```
.pips/projeto_<nome>/
├── _config/    # Objetivo e configuração imutáveis
├── _state/     # Estado de processamento
├── _output/    # Insights e entregas
└── _source/    # Arquivos fonte
```

**Ciclo:** Work → Save → Validate → Reset → Resume

### Protocolo de Memória Infinita (Infinite Memory Protocol)

Sistema automatizado para persistir estado do PIPS antes de compactação de contexto e restaurar contexto ao iniciar nova sessão. Garante que nenhum trabalho seja perdido durante tarefas de longa duração.

**Componentes do Protocolo:**

| Componente | Arquivo | Função |
|------------|---------|--------|
| `context.md` | `_config/context.md` | Objetivo imutável (Estrela do Norte) |
| `progress.yaml` | `_state/progress.yaml` | GPS de progresso (estado, fila, ciclo) |
| `insights_raw.md` | `_output/insights_raw.md` | Memória de longo prazo |
| `source_hashes.yaml` | `_config/source_hashes.yaml` | MD5 hashes para verificação de integridade |
| `audit.log` | `_config/audit.log` | Log de ações automáticas |

**Hooks Automáticos (command type):**

Configurados em `.claude/settings.json` - executam CLI tool real:
```json
{
  "hooks": {
    "PreCompact": [{"type": "command", "command": "py -3.13 tools/pips_hook.py snapshot"}],
    "SessionStart": [{"type": "command", "command": "py -3.13 tools/pips_hook.py status"}],
    "Stop": [{"type": "command", "command": "py -3.13 tools/pips_hook.py session_end"}]
  }
}
```

**CLI Tool (`tools/pips_hook.py`):**
```bash
py -3.13 tools/pips_hook.py snapshot      # Salva estado de projetos ativos
py -3.13 tools/pips_hook.py status        # Lista projetos resumíveis
py -3.13 tools/pips_hook.py session_end   # Snapshot final ao encerrar
```

**Métodos do Motor PIPS:**
```python
engine.snapshot(trigger)              # Snapshot rápido para persistência
engine.snapshot_with_recovery(...)    # Snapshot com fallback para emergência
engine._emergency_snapshot(trigger)   # Salva em temp se falhar local
engine.get_resumable_status()         # Retorna status ou {error: ...} se corrompido
engine.verify_source_integrity()      # Compara hashes MD5 atual vs armazenado
engine.store_initial_hashes()         # Armazena hashes no init (automático)
engine.recover_from_corruption()      # Tenta backup → checkpoints → mínimo
engine.log_automated_action(...)      # Registra em audit.log (serializa datetime/Path)
```

**Funções Auxiliares:**
```python
get_all_resumable_projects()  # Lista projetos, incluindo corrompidos com status='erro'
```

**Salvaguardas Científicas:**
- `source_hashes.yaml`: MD5 de cada arquivo fonte armazenado no init
- `verify_source_integrity()`: Detecta modificações ou arquivos ausentes
- `audit.log`: Registro cronológico de todas as ações automáticas

**Estratégia de Recuperação (Graceful Degradation):**
1. **Backup**: Restaura de `progress.yaml.bak` se existir
2. **Checkpoints**: Reconstrói estado de `checkpoints.log` + fila dos source_files
3. **Mínimo**: Cria estado básico com fila reconstruída dos arquivos fonte

**Uso:**
```bash
/pips memory                    # Ver status do protocolo
/pips validate <nome>           # Verifica integridade dos arquivos fonte
```

**Padrões Importantes:**
- Hooks devem ser `command` type (executam shell), não `prompt` type (apenas instruções)
- `get_resumable_status()` retorna `{status: 'erro', error: ..., recoverable: True}` em vez de None para projetos corrompidos (visibilidade > silêncio)
- `_serialize_for_json()` converte datetime/Path antes de serializar para audit.log
- `snapshot()` verifica AMBOS `_config` e `_state` antes de prosseguir (evita race condition)

### Export System

Sistema para exportar saídas de comandos em múltiplos formatos.

**Formatos suportados:**
- **md** - Markdown com frontmatter YAML
- **yaml** - YAML estruturado
- **json** - JSON estruturado
- **docx** - Documento Word (requer `python-docx`)

**Comandos de exportação:**
```bash
# Via REPL (exporta o último comando executado)
/export md                      # Exportar como Markdown
/export docx relatorio.docx     # Exportar como Word
/export yaml --no-metadata      # Exportar sem metadados

# Via CLI Tool
python tools/export_command.py --command template --args CLI_02 --format docx
python tools/export_command.py --file output.txt --format yaml --output dados.yaml
python tools/export_command.py --command pips --args status projeto --format json --stdout
```

**Arquitetura:**
- `formatter.py` - Formatação centralizada (constantes, utilitários, formatadores por comando)
- `exporter.py` - Engine de exportação com suporte a 4 formatos
- `tools/export_command.py` - CLI tool para exportação standalone

**Constantes centralizadas:**
```python
BOX_WIDTH = 51
STATUS_EMOJI = {"concluido": "✅", "erro": "❌", "em_progresso": "▶️", ...}
```

## Clinical Documentation Structure

### Protocol Hierarchy (`entregas/Protocolos_Compartilhamento_Cuidado/`)

| Type | Code | Purpose | Example |
|------|------|---------|---------|
| **PCC** | PCC-01 to PCC-06 | Macro care flow protocols | `01_PROTOCOLO_INTERSETORIAL_APS_NIRSM_AES.md` |
| **CLI** | CLI-01 to CLI-05 | Condition-specific clinical protocols | `CLI_02_TRANSTORNO_ESPECTRO_AUTISTA.md` |
| **GN** | GN-01+ | Narrative guides for APS teams | `GUIA_NARRATIVO_APS_DI_TEA.md` |
| **POP** | POP-01 to POP-07 | Standard Operating Procedures | `POP_05_ELABORACAO_PTS.md` |
| **REG** | REG-01 to REG-02 | Regulation protocols (NIRSM-R) | `05_PROTOCOLO_REGULACAO_NIRSM_R.md` |

### DI/TEA Documentation Suite

Three interconnected documents for Intellectual Disability and Autism Spectrum Disorder:

1. **CLI-02** (`Protocolos_Clinicos/CLI_02_TRANSTORNO_ESPECTRO_AUTISTA.md`) — **v2.7**
   - Clinical reference: DSM-5-TR criteria, M-CHAT-R/F protocol, intervention approaches
   - **~1,925 lines, 21 sections + visual annexes, 34 Vancouver references**
   - Key sections: 3.1 Fundamentação (10 subseções), 7.3 NIRSM-R, 9.2.4 Algoritmo intervenção, 11.3.1 Transição adulto, 12.4-12.6 Rede expandida
   - **v2.6-v2.7 additions:** Anexo F (Mermaid flowcharts by age), Anexo G (M-CHAT pocket card)

2. **PCC-06 MACROFLUXO** (`Protocolos_Clinicos/MACROFLUXO_NARRATIVO_DI_TEA.md`)
   - 10-phase patient navigation cascade: Surveillance → Diagnosis → Intervention → Discharge
   - P1/P2/P3 prioritization system (30/90/180 days)
   - ~1050 lines

3. **GN-01 GUIA NARRATIVO** (`Protocolos_Clinicos/GUIA_NARRATIVO_APS_DI_TEA.md`)
   - Step-by-step guide for e-ESF, e-Multi, ACS teams
   - 4 Macro Etapas → 12 Micro Etapas (Planifica SUS methodology)
   - RACI matrix, quality indicators, checklists
   - ~1100 lines

### Key Clinical Concepts

| Concept | Description |
|---------|-------------|
| **MACC** | Modelo de Atenção às Condições Crônicas - 5-level stratification pyramid |
| **CuidaSM** | 31-item scale for mental health risk stratification (0-11 points) |
| **M-CHAT-R/F** | Modified Checklist for Autism in Toddlers (16-30 months) |
| **IRDI** | Indicadores de Risco para o Desenvolvimento Infantil (0-18 months) |
| **P1/P2/P3** | Priority system: P1=30d (urgent), P2=90d (high), P3=180d (regular) |
| **NIRSM-R** | Núcleo Interno de Regulação de Saúde Mental - gatekeeper |
| **PTS** | Projeto Terapêutico Singular - individualized care plan |

### PTS (Projeto Terapêutico Singular) — Reflexões Técnicas

O PTS é uma **tecnologia de gestão do cuidado** — não apenas um formulário. Representa a operacionalização da **clínica ampliada** e do **modelo biopsicossocial** no contexto da RAPS brasileira.

**Os 4 Momentos Estruturais:**

| Momento | Foco | Insight Técnico |
|---------|------|-----------------|
| **1. Diagnóstico Integral** | Avaliação biopsicossocial, vulnerabilidades e potencialidades | Vai além do CID-10 — mapeia determinantes sociais, barreiras de acesso e rede de apoio |
| **2. Definição de Metas** | Objetivos SMART em 30/90/>90 dias | A **negociação** com usuário é elemento constitutivo, não opcional |
| **3. Divisão de Responsabilidades** | Matriz clara de quem faz o quê | Inclui **compromissos do próprio usuário e família** — co-responsabilização |
| **4. Reavaliação** | Monitoramento e ajustes | Processo **cíclico** — não é documento estático |

**Insights Críticos:**

- **PTS Preliminar (Inovação TEA/DI):** Elaborado ANTES da confirmação diagnóstica. Alinhado com MS Brasil 2025 e janela de neuroplasticidade (0-3 anos). Ruptura com lógica "primeiro diagnóstico, depois intervenção"
- **Estratificação de Risco como Motor:** PTS se articula com classificação 🔴🟠🟡🟢🔵. Reclassificação em cada reavaliação é evidência de efetividade
- **Intersetorialidade Estrutural:** Campos obrigatórios para Educação (PSE, AEE, PEI), Assistência Social (CRAS/CREAS), Terceiro setor
- **Gestor de Caso:** Profissional de referência como coordenador — evita fragmentação do cuidado

**Indicadores de Qualidade:**

| Indicador | Meta | Significado |
|-----------|------|-------------|
| Usuários CAPS com PTS | 100% | Cobertura universal |
| PTS com participação do usuário | ≥80% | Protagonismo real |
| PTS revisados no prazo | ≥90% | Processo vivo |
| Metas SMART alcançadas | ≥70% | Efetividade clínica |

**Diferenciação do Plano de Cuidado Genérico:**
1. **Singularização** — cada PTS é único
2. **Co-construção** — usuário é sujeito, não objeto
3. **Temporalidade** — metas com prazos definidos
4. **Responsabilização mútua** — todos têm papéis claros
5. **Dinamicidade** — reavaliação programada

**Bases Normativas:** PNH, PNSM, MACC, Linha de Cuidado TEA (MS Brasil 2025)

**Documentos de Referência:**
- `POPs/POP_05_ELABORACAO_PTS.md` — Procedimento operacional (4 etapas)
- `_Instrumentos/F-02_Modelo_PTS_Compartilhado.md` — Formulário completo (5 momentos)

### Document Templates

- **Protocol template:** `_Templates/TEMPLATE_PROTOCOLO_PCC.md`
- **Master index:** `00_INDICE_MASTER_PROTOCOLOS.md`

## Clinical Protocol Development Patterns

### Versioning Strategy (CLI-02 as reference)
| Version | Focus |
|---------|-------|
| x.0 | Initial structure |
| x.1 | Technical corrections (data triangulation) |
| x.2 | Reference formatting (Vancouver/ICMJE) |
| x.3 | Operational flows (contrarreferência, falso-negativos) |
| x.4 | Conceptual expansion (fundamentação técnica) |
| x.5 | Full operationalization (responsabilidades, algoritmos) |

### Required Sections for Clinical Protocols (CLI-xx)
1. **Fundamentação Técnica** — DSM-5-TR/CID-11 criteria, neurobiological bases, comorbidities
2. **Fluxo de Atendimento** — Including NIRSM-R role, P1/P2/P3 prioritization
3. **Avaliação Diagnóstica** — Instruments with psychometric properties (sens, spec, VPP)
4. **Intervenção** — Algorithm: profile → intervention → intensity → frequency
5. **PTS** — 4 moments: diagnostic, goals, responsibilities, reassessment
6. **Acompanhamento Longitudinal** — APS monitoring protocol, transition criteria
7. **Rede Intersetorial** — Education, CRAS/CREAS, 3rd sector, telecare, caregiver support
8. **Responsabilidades** — By professional (eSF, eMulti) and by point of care (NIRSM-R)
9. **Contrarreferência** — Criteria with responsible party for each criterion
10. **Indicadores** — Formulas, targets, data sources

### Data Triangulation Sources (TEA)
- CDC MMWR (prevalence)
- Losapio 2023 (M-CHAT Brazilian validation)
- Santos 2024 (ADOS-2, CARS-2 meta-analysis)
- ENAP 2020 (IFBrM classification)
- MS 2025 (Linha de Cuidado TEA)

### Reference Format
All clinical protocols use **Vancouver (ICMJE)** format with DOIs for scientific literature.

## PIPS Test Coverage

**Test file:** `tests/test_pips.py` (85 tests)

| Test Class | Focus | Count |
|------------|-------|-------|
| `TestPIPSCommands` | Command parsing | 5 |
| `TestPIPSTrigger` | Activation criteria | 5 |
| `TestPIPSEngine` | Core engine operations | 6 |
| `TestPIPSCycle` | Work-Save-Validate cycle | 7 |
| `TestPIPSOutput` | Output generation | 3 |
| `TestConfigPersistence` | Config persistence | 5 |
| `TestSnapshot` | Snapshot methods | 5 |
| `TestGetResumableStatus` | Status with corruption detection | 4 |
| `TestVerifySourceIntegrity` | Hash verification | 4 |
| `TestLogAutomatedAction` | JSON serialization | 4 |
| `TestRecoverFromCorruption` | Recovery strategies | 4 |
| `TestGetAllResumableProjects` | Multi-project listing | 4 |
| `TestSourceHashOperations` | Hash storage/loading | 4 |

**Fixtures principais:**
- `temp_pips_root`: Diretório temporário para testes
- `sample_source_files`: 3 arquivos de ~600 tokens cada
- `initialized_engine`: Engine com projeto já inicializado

## Key Conventions

- **Python 3.13** required
- **All user-facing text in Portuguese (Brazilian)** - error messages, commands, documentation
- Reference materials in `/referencias/` organized by type (normativos, clinicos, instrumentos)
- Deliverables tracked in README.md with completion status
- Clinical protocols follow Planifica SUS macro/micro etapa methodology
- Mermaid diagrams used for flowcharts in clinical documents

## Implementation Lessons (PIPS/Memory Protocol)

### Hook Configuration
- **Use `command` type, not `prompt` type** - prompt hooks only send instructions to Claude, they don't execute code
- CLI tools called by hooks must handle Windows console encoding (`TextIOWrapper` with utf-8)
- Avoid emojis in CLI output on Windows - use ASCII indicators like `[.]`, `[>]`, `[||]`

### Error Handling Patterns
- **Visibility over silence**: Return error dicts instead of None for corrupted states
- Example: `{status: 'erro', error: '...', recoverable: True}` allows user action
- Always provide graceful degradation (try best → progressively simpler fallbacks)

### JSON Serialization
- datetime and Path objects fail with `json.dumps()` - use recursive serializer
- Pattern: `_serialize_for_json()` that handles nested dicts/lists

### State Management
- Always check BOTH `_config` AND `_state` before operations (avoid race conditions)
- `load_project()` loads both atomically - prefer single call over separate loads
- Recovery should rebuild queues from source_files when possible (not empty queues)

### Integrity Verification
- Store hashes at project init (`store_initial_hashes()` in `init_project()`)
- Compare stored vs current hashes for modification detection
- Report both MODIFIED and MISSING files distinctly
