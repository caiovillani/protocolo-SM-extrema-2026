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
- **main.py** - REPL entry point
- **commands.py** - Command parsing (`/template`, `/auditoria`, `/orientacao`, `/conformidade`, `/comparar`, `/pips`)
- **pipeline.py** - 5-stage processing: parse → classify → validate input → load context → process → validate output
- **resources.py** - YAML resource loader with caching (normativas, taxonomias, templates)
- **pips.py** - PIPS engine for iterative processing with state persistence
- **pips_models.py** - Dataclasses for PIPS state management

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

## Key Conventions

- **Python 3.13** required
- **All user-facing text in Portuguese (Brazilian)** - error messages, commands, documentation
- Reference materials in `/referencias/` organized by type (normativos, clinicos, instrumentos)
- Deliverables tracked in README.md with completion status
