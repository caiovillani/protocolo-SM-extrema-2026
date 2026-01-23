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
- **commands.py** - Command parsing (`/template`, `/auditoria`, `/orientacao`, `/conformidade`, `/comparar`)
- **pipeline.py** - 5-stage processing: parse → classify → validate input → load context → process → validate output
- **resources.py** - YAML resource loader with caching (normativas, taxonomias, templates)

### WAT Framework
- **Workflows** (`/workflows/`) - Standard Operating Procedures in Markdown
- **Tools** (`/tools/`) - Deterministic Python CLI scripts
- Both use `_template.*` files and `INDEX.md` registries for extensibility

### Resource System
YAML files loaded from configurable root (via `RESOURCE_ROOT` env var). Three types: normativas, taxonomias, templates. In-memory caching enabled by default.

## Key Conventions

- **Python 3.13** required
- **All user-facing text in Portuguese (Brazilian)** - error messages, commands, documentation
- Reference materials in `/referencias/` organized by type (normativos, clinicos, instrumentos)
- Deliverables tracked in README.md with completion status
