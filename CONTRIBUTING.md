# Guia de Contribuição - Protocolo SM Extrema 2026

Este documento descreve como configurar o ambiente de desenvolvimento e contribuir para o projeto.

---

## Pré-requisitos

### Obrigatórios

| Software | Versão | Verificação |
|----------|--------|-------------|
| Python | 3.13+ | `py -3.13 --version` |
| Git | 2.x+ | `git --version` |
| pip | 23+ | `py -3.13 -m pip --version` |

### Opcionais (para funcionalidades avançadas)

| Software | Uso | Instalação |
|----------|-----|------------|
| Node.js 20+ | MCP servers (Claude Code) | [nodejs.org](https://nodejs.org) |
| Visual Studio Code | IDE recomendado | [code.visualstudio.com](https://code.visualstudio.com) |

---

## Setup do Ambiente

### 1. Clonar o Repositório

```bash
git clone <repository-url>
cd "Protocolo SM Extrema 2026"
```

### 2. Criar Ambiente Virtual

```bash
# Windows
py -3.13 -m venv .venv
.venv\Scripts\activate

# Linux/macOS
python3.13 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar Dependências

```bash
# Dependências principais
pip install -r requirements.txt

# Para desenvolvimento (inclui ferramentas de teste)
pip install -r requirements-dev.txt
```

### 4. Verificar Instalação

```bash
# Executar testes
py -3.13 -m pytest tests/ -v

# Verificar sintaxe
py -3.13 -m py_compile src/context_engine/*.py

# Iniciar REPL (opcional)
py -3.13 src/context_engine/main.py
```

---

## Estrutura do Projeto

```
Protocolo SM Extrema 2026/
├── src/context_engine/       # Motor de contexto (Python)
│   ├── main.py               # REPL entry point
│   ├── commands.py           # Parsing de comandos
│   ├── pipeline.py           # Pipeline de 5 estágios
│   ├── pips.py               # Processamento iterativo
│   ├── exporter.py           # Exportação (MD/YAML/JSON/DOCX)
│   ├── formatter.py          # Formatação centralizada
│   └── validator.py          # Validação de protocolos
│
├── src/html_renderer/        # Renderizador HTML
│   ├── renderer.py           # Pipeline principal
│   ├── parsers/              # Handlers (Mermaid, ASCII, tabelas)
│   ├── templates/            # Jinja2 templates
│   └── assets/styles/        # CSS (design tokens, componentes)
│
├── entregas/                 # Documentação clínica final
│   └── Protocolos_.../       # Protocolos organizados por tipo
│       ├── Protocolos_Clinicos/    # CLI-01 a CLI-05
│       ├── Protocolos_Fluxo/       # PCC-01 a PCC-06
│       ├── POPs/                   # POP-01 a POP-07
│       └── Guias_Narrativos/       # GN-01+
│
├── referencias/              # Material de referência
│   ├── normativos/           # Legislação, RAPS
│   ├── clinicos/             # Referências clínicas
│   └── instrumentos/         # Escalas (M-CHAT, CuidaSM, etc.)
│
├── tools/                    # Scripts CLI
│   ├── render_html.py        # Renderização de protocolos
│   ├── export_command.py     # Exportação standalone
│   └── pips_*.py             # Ferramentas PIPS
│
├── tests/                    # Testes automatizados
├── .claude/                  # Configurações Claude Code
└── workflows/                # Workflows WAT
```

---

## Comandos de Desenvolvimento

### Testes

```bash
# Rodar todos os testes
py -3.13 -m pytest tests/ -v

# Com cobertura de código
py -3.13 -m pytest tests/ -v --cov=src/context_engine --cov-report=term-missing

# Arquivo específico
py -3.13 -m pytest tests/test_commands.py -v

# Teste único
py -3.13 -m pytest tests/test_commands.py::test_parse_template -v
```

### Linting e Verificação

```bash
# Verificar sintaxe de todos os módulos
py -3.13 -m py_compile src/context_engine/*.py

# Verificar tipos (se mypy instalado)
py -3.13 -m mypy src/context_engine/
```

### REPL do Context Engine

```bash
# Iniciar REPL interativo
py -3.13 src/context_engine/main.py

# Comandos disponíveis no REPL:
# /template <CLI_XX>     - Gerar template de protocolo
# /auditoria <arquivo>   - Auditar protocolo
# /conformidade          - Verificar conformidade RAPS
# /pips status <nome>    - Status de projeto PIPS
# /export <formato>      - Exportar última saída
```

### Renderização HTML

```bash
# Renderizar protocolo único
py -3.13 tools/render_html.py entregas/.../CLI_02_*.md

# Renderizar todos os protocolos
py -3.13 tools/render_html.py --all

# Especificar diretório de saída
py -3.13 tools/render_html.py --output exports/html/ CLI_02_*.md
```

---

## Workflow de Contribuição

### 1. Criar Branch

```bash
git checkout -b feature/nome-da-feature
# ou
git checkout -b fix/descricao-do-bug
```

### 2. Fazer Alterações

- Siga os padrões de código descritos abaixo
- Adicione testes para novas funcionalidades
- Atualize documentação se necessário

### 3. Testar

```bash
py -3.13 -m pytest tests/ -v
```

### 4. Commit

```bash
git add <arquivos>
git commit -m "feat: descrição concisa da mudança"
```

**Convenção de commits:**
- `feat:` - Nova funcionalidade
- `fix:` - Correção de bug
- `docs:` - Apenas documentação
- `test:` - Apenas testes
- `refactor:` - Refatoração sem mudança de comportamento
- `style:` - Formatação, sem mudança de código
- `chore:` - Manutenção, build, CI/CD

### 5. Pull Request

```bash
git push origin feature/nome-da-feature
```

Crie PR via GitHub com:
- Descrição clara das mudanças
- Referência a issues relacionadas
- Checklist de verificação

---

## Padrões de Código

### Python

- **Python 3.13+** obrigatório
- **Docstrings** em português para funções públicas
- **Type hints** para parâmetros e retornos
- **Nomes** em português quando apropriado (variáveis internas)
- **Mensagens de erro** em português (usuários brasileiros)

```python
def processar_protocolo(caminho: Path, formato: str = "md") -> dict:
    """
    Processa um protocolo clínico e retorna estrutura validada.

    Args:
        caminho: Caminho para o arquivo Markdown
        formato: Formato de saída (md, yaml, json, docx)

    Returns:
        Dicionário com metadados e conteúdo processado

    Raises:
        ValueError: Se o formato não for suportado
    """
    ...
```

### Documentação Clínica (Markdown)

- **Formato Vancouver** para referências bibliográficas
- **Mermaid** para fluxogramas
- **Tabelas** com cabeçalhos descritivos
- **10 seções obrigatórias** para protocolos CLI (ver CLAUDE.md)

```markdown
## 8. Referências

1. Autor AA, Autor BB. Título do artigo. Revista. 2024;Vol(Num):Páginas. doi:10.xxxx/xxxxx
2. Organização. Título do documento. Cidade: Editora; Ano. p. XX-YY.
```

---

## Como Adicionar Novos Protocolos

### 1. Criar Arquivo

```bash
# Copiar template
cp entregas/.../Protocolos_Clinicos/_Templates/TEMPLATE_PROTOCOLO_CLI.md \
   entregas/.../Protocolos_Clinicos/CLI_XX_NOME.md
```

### 2. Estrutura Obrigatória (CLI)

Todo protocolo clínico deve conter:

| # | Seção | Descrição |
|---|-------|-----------|
| 1 | Fundamentação Técnica | Critérios DSM-5/CID-11, bases neurobiológicas |
| 2 | Fluxo de Atendimento | Incluindo NIRSM-R e P1/P2/P3 |
| 3 | Avaliação Diagnóstica | Instrumentos com propriedades psicométricas |
| 4 | Intervenção | Algoritmo: perfil → intervenção → intensidade |
| 5 | PTS | 4 momentos: diagnóstico, metas, responsáveis, reavaliação |
| 6 | Acompanhamento Longitudinal | Monitoramento APS, critérios de transição |
| 7 | Rede Intersetorial | Educação, CRAS/CREAS, 3º setor |
| 8 | Responsabilidades | Por profissional e ponto de atenção |
| 9 | Contrarreferência | Critérios com responsável |
| 10 | Indicadores | Fórmulas, metas, fontes de dados |

### 3. Validar

```bash
# Via REPL
py -3.13 src/context_engine/main.py
> /auditoria entregas/.../CLI_XX_NOME.md

# Ou via skill (Claude Code)
/validate-protocol CLI_XX_NOME.md
```

### 4. Atualizar Índice

Adicionar entrada em `entregas/.../00_INDICE_MASTER_PROTOCOLOS.md`.

---

## Resolução de Problemas

### Erro: UnicodeEncodeError no Windows

```python
# Adicionar no início do script
import sys, os
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
```

### Erro: ModuleNotFoundError

```bash
# Verificar se está no ambiente virtual
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS

# Reinstalar dependências
pip install -r requirements.txt
```

### Erro: PermissionError com OneDrive

Arquivos sincronizados com OneDrive podem estar bloqueados. Aguarde a sincronização ou use `dirs_exist_ok=True` em `shutil.copytree()`.

---

## Recursos Adicionais

- [CLAUDE.md](./CLAUDE.md) - Instruções para Claude Code
- [README.md](./README.md) - Visão geral do projeto
- [Índice Master](./entregas/Protocolos_Compartilhamento_Cuidado/00_INDICE_MASTER_PROTOCOLOS.md) - Lista de protocolos

---

*Última atualização: 24 Janeiro 2026*
