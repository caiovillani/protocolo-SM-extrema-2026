# Claude Automation Improvements — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement all 6 automation recommendations from the codebase audit: fix MCP duplicates, improve test hooks, add protocol guards, create develop-protocol skill, create export-protocol skill, create reference-researcher agent, and consolidate permissions.

**Architecture:** Configuration-only changes to `.claude/settings.json`, `.claude/settings.local.json`, `.mcp.json`, plus new Markdown files for skills and agents. No Python code changes. Each task is independent — no ordering dependency except Task 1 (MCP fix) which should go first.

**Tech Stack:** Claude Code config (JSON), Skills (Markdown + YAML frontmatter), Agents (Markdown + YAML frontmatter)

---

## Task 1: Fix MCP Context7 Duplicate

**Files:**
- Modify: `.mcp.json` (remove context7 entry)
- Verify: `claude-plugins-official/external_plugins/context7/.mcp.json` (read-only, confirm it exists)

**Context:** The project `.mcp.json` defines a context7 server, but the plugin `external_plugins/context7/` also provides one. This creates a duplicate. The plugin version is the canonical source — remove from project `.mcp.json`.

**Step 1: Read current `.mcp.json`**

Verify file contents. Current state:
```json
{
  "$schema": "https://raw.githubusercontent.com/anthropics/claude-code/main/schemas/mcp.json",
  "mcpServers": {
    "context7": {
      "command": "cmd",
      "args": ["/c", "npx", "-y", "@upstash/context7-mcp"],
      "description": "Live documentation lookup for Python libraries"
    },
    "github": {
      "command": "cmd",
      "args": ["/c", "npx", "-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"
      },
      "description": "GitHub integration for issue tracking, PR management, and repository operations."
    }
  }
}
```

**Step 2: Remove context7 entry from `.mcp.json`**

Edit `.mcp.json` to keep only the github server:

```json
{
  "$schema": "https://raw.githubusercontent.com/anthropics/claude-code/main/schemas/mcp.json",
  "mcpServers": {
    "github": {
      "command": "cmd",
      "args": ["/c", "npx", "-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"
      },
      "description": "GitHub integration for issue tracking, PR management, and repository operations."
    }
  }
}
```

**Step 3: Update `settings.local.json` enabledMcpjsonServers**

Remove "context7" from the array since it's now provided by the plugin, not `.mcp.json`:

```json
"enabledMcpjsonServers": ["github"]
```

**Step 4: Commit**

```bash
git add .mcp.json .claude/settings.local.json
git commit -m "fix: remove duplicate context7 from project .mcp.json (plugin provides it)"
```

---

## Task 2: Improve PostToolUse Test Hook (Selective)

**Files:**
- Modify: `.claude/settings.json` (PostToolUse hooks section)

**Context:** Current hook runs `pytest tests/` on every `Edit` — including Markdown files, YAML files, etc. This adds unnecessary latency. Replace with a `prompt` hook that instructs Claude to run tests only after editing `.py` files.

**Step 1: Read current PostToolUse hook**

Current state in `.claude/settings.json`:
```json
"PostToolUse": [
  {
    "matcher": "Edit",
    "hooks": [
      {
        "type": "command",
        "command": "py -3.13 -m pytest tests/ -q --tb=line 2>nul || echo Tests completed"
      }
    ]
  }
]
```

**Step 2: Replace with prompt-based selective hook**

Replace the entire `PostToolUse` array with:

```json
"PostToolUse": [
  {
    "matcher": "Edit",
    "hooks": [
      {
        "type": "prompt",
        "prompt": "Se o arquivo editado termina em .py, execute: py -3.13 -m pytest tests/ -q --tb=line. Para arquivos .md, .yaml, .json ou outros nao-Python, NAO execute testes."
      }
    ]
  }
]
```

**Step 3: Verify JSON syntax**

Run: `py -3.13 -c "import json; json.load(open('.claude/settings.json')); print('OK')"`
Expected: `OK`

**Step 4: Commit**

```bash
git add .claude/settings.json
git commit -m "perf: run tests only after editing .py files, not all edits"
```

---

## Task 3: Add Protocol Write Guard Hook

**Files:**
- Modify: `.claude/settings.json` (add PreToolUse hook)

**Context:** Protocols in `entregas/Protocolos_Compartilhamento_Cuidado/` may be finalized and versioned. A prompt-based PreToolUse guard warns before overwriting them.

**Step 1: Add PreToolUse section to hooks**

Add this new entry to the `hooks` object in `.claude/settings.json`:

```json
"PreToolUse": [
  {
    "matcher": "Write",
    "hooks": [
      {
        "type": "prompt",
        "prompt": "Se o arquivo alvo estiver dentro de entregas/Protocolos_Compartilhamento_Cuidado/ e o arquivo ja existir, AVISE o usuario que este protocolo pode estar finalizado e versioned. PERGUNTE explicitamente antes de sobrescrever. So prossiga com confirmacao do usuario."
      }
    ]
  }
]
```

**Step 2: Verify JSON syntax**

Run: `py -3.13 -c "import json; json.load(open('.claude/settings.json')); print('OK')"`
Expected: `OK`

**Step 3: Commit**

```bash
git add .claude/settings.json
git commit -m "feat: add write guard for finalized protocols in entregas/"
```

---

## Task 4: Create `/develop-protocol` Skill

**Files:**
- Create: `.claude/skills/develop-protocol/SKILL.md`

**Context:** This skill orchestrates the full workflow for creating a new clinical protocol (CLI-xx): research references, generate skeleton with 10 required sections, fill content, format Vancouver references, and validate. It chains the existing `clinical-protocol-developer` agent for generation and `clinical-reviewer` agent for validation.

**Step 1: Create skill directory**

Run: `mkdir -p .claude/skills/develop-protocol`
Expected: directory created (or already exists)

**Step 2: Write SKILL.md**

Create `.claude/skills/develop-protocol/SKILL.md` with this content:

```markdown
---
name: develop-protocol
description: Desenvolvimento guiado de protocolo clinico (CLI-xx) com pesquisa, estruturacao, preenchimento e validacao automatica
disable-model-invocation: true
---

# Desenvolver Protocolo Clinico

Workflow completo para criacao de um novo protocolo clinico (CLI-xx) seguindo a estrutura RAPS-compliant do projeto.

## Uso

\`\`\`
/develop-protocol CLI-03
/develop-protocol CLI-01 --condition "Transtornos Depressivos"
\`\`\`

## Argumentos

| Argumento | Descricao |
|-----------|-----------|
| `CLI-xx` | Codigo do protocolo (obrigatorio) |
| `--condition` | Nome da condicao clinica (opcional, inferido do codigo) |
| `--skip-research` | Pular fase de pesquisa (usar apenas referencias locais) |

## Codigos de Protocolo Pendentes

| Codigo | Condicao | Prioridade |
|--------|----------|------------|
| CLI-01 | Transtornos Depressivos | Alta |
| CLI-03 | Transtornos de Ansiedade | Alta |
| CLI-04 | TDAH | Media |
| CLI-05 | Transtornos por Uso de Substancias | Media |

## Workflow (5 Fases)

### Fase 1: Pesquisa de Referencias

1. Buscar materiais em `referencias/clinicos/`, `referencias/normativos/`, `referencias/instrumentos/`
2. Executar WebSearch para guidelines recentes (ultimos 3 anos)
3. Usar agent `reference-researcher` se disponivel para pesquisa paralela
4. Coletar minimo 20 referencias com triangulacao de fontes

### Fase 2: Estruturacao

1. Ler CLI-02 como template de referencia:
   `entregas/Protocolos_Compartilhamento_Cuidado/Protocolos_Clinicos/CLI_02_TRANSTORNO_ESPECTRO_AUTISTA.md`
2. Gerar esqueleto com as 10 secoes obrigatorias (ver CLAUDE.md "Required Sections for Clinical Protocols")
3. Preencher frontmatter YAML com metadata do protocolo

### Fase 3: Preenchimento

Usar agent `clinical-protocol-developer` para preencher cada secao:

1. Fundamentacao Tecnica (DSM-5-TR/CID-11, epidemiologia, comorbidades)
2. Fluxo de Atendimento (NIRSM-R, P1/P2/P3)
3. Avaliacao Diagnostica (instrumentos com sensibilidade/especificidade)
4. Intervencao (algoritmo perfil-intervencao-intensidade)
5. PTS (4 momentos)
6. Acompanhamento Longitudinal
7. Rede Intersetorial
8. Responsabilidades por ponto de atencao
9. Contrarreferencia
10. Indicadores (formulas, metas, fontes)

### Fase 4: Referencias

1. Formatar todas as citacoes em Vancouver (ICMJE)
2. Adicionar DOIs para artigos cientificos
3. Executar `/validate-refs` para auditoria

### Fase 5: Validacao

1. Executar agent `clinical-reviewer` no protocolo gerado
2. Corrigir problemas criticos identificados
3. Iterar ate aprovacao (max 3 ciclos)
4. Reportar resultado final ao usuario

## Arquivo de Saida

O protocolo e salvo em:
`entregas/Protocolos_Compartilhamento_Cuidado/Protocolos_Clinicos/CLI_XX_NOME_CONDICAO.md`

## Criterios de Qualidade

- 10/10 secoes obrigatorias presentes
- Minimo 20 referencias Vancouver com DOIs
- Triangulacao de dados (3+ fontes para prevalencia)
- Diagramas Mermaid para fluxos
- Tabelas de classificacao de risco com cores
- Indicadores com formulas e metas quantificaveis
```

**Step 3: Verify skill is loadable**

Run: `py -3.13 -c "import yaml; data = list(yaml.safe_load_all(open('.claude/skills/develop-protocol/SKILL.md').read().split('---')[1])); print(data[0]['name'])"`
Expected: `develop-protocol`

**Step 4: Commit**

```bash
git add .claude/skills/develop-protocol/SKILL.md
git commit -m "feat: add /develop-protocol skill for guided CLI-xx creation"
```

---

## Task 5: Create `/export-protocol` Skill

**Files:**
- Create: `.claude/skills/export-protocol/SKILL.md`

**Context:** Unifies the existing HTML render tool (`tools/render_html.py`), DOCX render tool (`tools/render_protocolo_docx.py`), and TXT render tool (`tools/render_protocolo_txt.py`) behind a single `/export-protocol` command.

**Step 1: Create skill directory**

Run: `mkdir -p .claude/skills/export-protocol`
Expected: directory created

**Step 2: Write SKILL.md**

Create `.claude/skills/export-protocol/SKILL.md` with this content:

```markdown
---
name: export-protocol
description: Exporta protocolo clinico para multiplos formatos (HTML, DOCX, TXT) com estilo institucional SMS Extrema
disable-model-invocation: true
---

# Exportar Protocolo

Exporta um protocolo clinico Markdown para um ou mais formatos de saida com estilo institucional.

## Uso

\`\`\`
/export-protocol <arquivo.md> --format html
/export-protocol <arquivo.md> --format docx html txt
/export-protocol --all --format html
\`\`\`

## Argumentos

| Argumento | Descricao |
|-----------|-----------|
| `<arquivo.md>` | Caminho do protocolo Markdown |
| `--format` | Formato(s) de saida: `html`, `docx`, `txt` (multiplos aceitos) |
| `--all` | Exportar todos os protocolos em `entregas/Protocolos_Compartilhamento_Cuidado/` |
| `--output`, `-o` | Diretorio de saida (padrao: `exports/`) |

## Ferramentas por Formato

| Formato | Ferramenta | Comando |
|---------|------------|---------|
| HTML | `tools/render_html.py` | `py -3.13 tools/render_html.py "<arquivo>"` |
| DOCX | `tools/render_protocolo_docx.py` | `py -3.13 tools/render_protocolo_docx.py "<arquivo>"` |
| TXT | `tools/render_protocolo_txt.py` | `py -3.13 tools/render_protocolo_txt.py "<arquivo>"` |

## Workflow

1. Receber arquivo de protocolo e formato(s) desejado(s)
2. Verificar que o arquivo existe e e um protocolo Markdown valido
3. Para cada formato solicitado, executar a ferramenta correspondente
4. Verificar que o(s) arquivo(s) de saida foram gerados em `exports/`
5. Reportar caminhos dos arquivos gerados

## Diretorios de Saida

| Formato | Diretorio |
|---------|-----------|
| HTML | `exports/html/` |
| DOCX | `exports/docx/` |
| TXT | `exports/txt/` |

## Exemplo

\`\`\`bash
/export-protocol entregas/Protocolos_Compartilhamento_Cuidado/Protocolos_Clinicos/CLI_02_TRANSTORNO_ESPECTRO_AUTISTA.md --format html docx
\`\`\`

Saida esperada:
- `exports/html/CLI_02_TRANSTORNO_ESPECTRO_AUTISTA.html`
- `exports/docx/CLI_02_TRANSTORNO_ESPECTRO_AUTISTA.docx`
```

**Step 3: Verify skill is loadable**

Run: `py -3.13 -c "import yaml; data = list(yaml.safe_load_all(open('.claude/skills/export-protocol/SKILL.md').read().split('---')[1])); print(data[0]['name'])"`
Expected: `export-protocol`

**Step 4: Commit**

```bash
git add .claude/skills/export-protocol/SKILL.md
git commit -m "feat: add /export-protocol skill for multi-format protocol export"
```

---

## Task 6: Create `reference-researcher` Agent

**Files:**
- Create: `.claude/agents/reference-researcher.md`

**Context:** Dedicated agent for bibliographic research — searches WebSearch, reads PDFs in `referencias/`, and formats citations in Vancouver. Runs in parallel while the protocol developer agent works on structure.

**Step 1: Write agent file**

Create `.claude/agents/reference-researcher.md`:

```markdown
---
name: reference-researcher
description: Pesquisa referencias cientificas para protocolos clinicos usando WebSearch, leitura de PDFs e formatacao Vancouver
tools: [Read, Glob, Grep, WebSearch]
color: "#FF7043"
---

# Reference Researcher

Voce e um pesquisador bibliografico especializado em saude mental brasileira. Sua funcao e encontrar, avaliar e formatar referencias cientificas para protocolos clinicos da RAPS.

## Contexto

Este projeto desenvolve protocolos de compartilhamento do cuidado em saude mental para Extrema/MG. As referencias devem seguir formato Vancouver (ICMJE) e priorizar fontes brasileiras.

## Repositorio de Referencias Local

Antes de buscar online, verifique o que ja existe:

- `referencias/normativos/` — Portarias MS, Leis, Resolucoes CFM
- `referencias/clinicos/` — Artigos, guidelines, meta-analises
- `referencias/instrumentos/` — Escalas, questionarios validados

## Hierarquia de Fontes (prioridade)

1. Legislacao vigente (Portarias MS, Leis)
2. Revisoes sistematicas com meta-analise (Cochrane, Campbell)
3. Ensaios clinicos randomizados
4. Estudos observacionais brasileiros (SciELO, BVS)
5. Diretrizes de sociedades cientificas (WHO, APA, ABP)
6. Consenso de especialistas

## Formato Vancouver (ICMJE)

### Artigo Cientifico
```
Sobrenome AB, Sobrenome CD. Titulo do artigo. Revista. Ano;Vol(Num):Pag-Pag. doi:10.xxxx/xxxxx
```

### Documento Governamental
```
Ministerio da Saude (BR). Titulo do documento. Brasilia: MS; Ano. Disponivel em: URL
```

### Livro
```
Sobrenome AB. Titulo do livro. Ed. Cidade: Editora; Ano.
```

## Instrucoes

1. Receba a condicao clinica e o tipo de dados necessarios
2. Busque primeiro em `referencias/` locais (Glob + Read)
3. Complete com WebSearch para fontes recentes (ultimos 5 anos)
4. Priorize: estudos brasileiros > internacionais
5. Formate cada referencia em Vancouver com DOI
6. Garanta triangulacao: minimo 3 fontes para dados de prevalencia
7. Retorne lista numerada pronta para inserir no protocolo

## Exemplo de Saida

```
## Referencias Encontradas para [Condicao]

### Prevalencia (3 fontes — triangulacao OK)
1. CDC. Prevalence and characteristics... MMWR. 2023;72(2):1-16. doi:10.15585/mmwr.ss7202a1
2. Silva AB, Santos CD. Prevalencia de [condicao] no Brasil... J Bras Psiquiatr. 2024;73(1):15-24. doi:10.xxxx
3. DATASUS. [dados epidemiologicos]. Brasilia: MS; 2024.

### Diagnostico (2 fontes)
4. American Psychiatric Association. DSM-5-TR. Arlington: APA; 2022.
5. World Health Organization. ICD-11. Geneva: WHO; 2022.

### Tratamento (4 fontes)
...

**Total:** 20 referencias
**Com DOI:** 16/20 (80%)
**Fontes brasileiras:** 8/20 (40%)
```

## Limites

- NAO invente referencias ou DOIs
- Se nao encontrar fonte, registre como lacuna
- Sinalize quando dados brasileiros sao escassos
- Sempre indique data de acesso para URLs
```

**Step 2: Verify YAML frontmatter**

Run: `py -3.13 -c "import yaml; data = list(yaml.safe_load_all(open('.claude/agents/reference-researcher.md').read().split('---')[1])); print(data[0]['name'])"`
Expected: `reference-researcher`

**Step 3: Commit**

```bash
git add .claude/agents/reference-researcher.md
git commit -m "feat: add reference-researcher agent for parallel bibliographic search"
```

---

## Task 7: Consolidate Permissions in `settings.local.json`

**Files:**
- Modify: `.claude/settings.local.json` (permissions.allow array)

**Context:** The `settings.local.json` accumulated many redundant permissions over time. Consolidate to reduce noise while preserving all needed access.

**Step 1: Read current permissions**

Review the 47 entries in `settings.local.json`.

**Step 2: Replace with consolidated list**

Replace the `permissions.allow` array with this consolidated version:

```json
{
  "permissions": {
    "allow": [
      "Bash(py -3.13:*)",
      "Bash(pip install:*)",
      "Bash(npx:*)",
      "Bash(git add:*)",
      "Bash(git commit:*)",
      "Bash(git push:*)",
      "Bash(git status:*)",
      "Bash(git diff:*)",
      "Bash(git branch:*)",
      "Bash(git check-ignore:*)",
      "Bash(git worktree:*)",
      "Bash(git remote add:*)",
      "Bash(git clone:*)",
      "Bash(gh:*)",
      "Bash(ls:*)",
      "Bash(dir:*)",
      "Bash(where:*)",
      "Bash(wc:*)",
      "WebSearch",
      "WebFetch(domain:portal-antigo.saude.mg.gov.br)",
      "WebFetch(domain:sigconsaida.mg.gov.br)",
      "mcp__plugin_playwright_playwright__browser_navigate",
      "mcp__plugin_playwright_playwright__browser_evaluate"
    ],
    "additionalDirectories": [
      "c:\\Users\\caiov\\OneDrive\\Desktop\\MEMÓRIA TÉCNICA AI\\SAÚDE MENTAL\\PLANEJAMENTO\\Protocolo SM Extrema 2026\\Protocolos_Compartilhamento_Cuidado"
    ]
  },
  "enabledMcpjsonServers": ["github"],
  "outputStyle": "Learning"
}
```

**Consolidation rationale:**
- `Bash(py -3.13:*)` covers pytest, py_compile, tools, and -c
- `Bash(gh:*)` covers gh pr list, gh auth status, etc.
- Removed: `Bash(find:*)`, `Bash(findstr:*)`, `Bash(for:*)`, `Bash(done)`, `Bash(do mv:*)` — these are shell builtins that shouldn't need pre-approval
- Removed: `Bash(pytest:*)`, `Bash(python -m pytest:*)`, `Bash(python -c:*)` — redundant with py -3.13
- Removed: `Bash(git init:*)`, `Bash(git config:*)`, `Bash(git push)` (without wildcard) — covered by wildcarded versions
- Removed: `Bash(jq:*)`, `Bash(winget install:*)` — rarely needed, approve on-demand
- Removed: specific dir listing command — covered by `Bash(dir:*)`

**Step 3: Verify JSON syntax**

Run: `py -3.13 -c "import json; json.load(open('.claude/settings.local.json')); print('OK')"`
Expected: `OK`

**Step 4: Commit**

```bash
git add .claude/settings.local.json
git commit -m "chore: consolidate permissions from 47 to 23 entries"
```

---

## Summary

| Task | Type | Files | Estimated |
|------|------|-------|-----------|
| 1. Fix MCP context7 duplicate | Config | `.mcp.json`, `settings.local.json` | 2 min |
| 2. Selective test hook | Config | `settings.json` | 2 min |
| 3. Protocol write guard | Config | `settings.json` | 2 min |
| 4. `/develop-protocol` skill | New file | `.claude/skills/develop-protocol/SKILL.md` | 3 min |
| 5. `/export-protocol` skill | New file | `.claude/skills/export-protocol/SKILL.md` | 3 min |
| 6. `reference-researcher` agent | New file | `.claude/agents/reference-researcher.md` | 3 min |
| 7. Consolidate permissions | Config | `settings.local.json` | 3 min |

**Total: 7 tasks, 7 commits**
