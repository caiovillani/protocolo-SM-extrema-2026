# Configuração Pandoc - Portal SMS Extrema/MG

## Contexto

O portal usa **Pandoc** para gerar páginas HTML a partir de arquivos Markdown. As páginas de conteúdo (pesquisas de preços, manuais, diagnósticos) atualmente usam CSS inline padrão do Pandoc, o que replica os problemas da homepage (sem cache, sem meta tags SEO, sem navegação).

**Solução:** Template Pandoc customizado com estilos unificados e meta tags completas.

---

## Arquivos do Sistema Pandoc

| Arquivo | Propósito |
|---------|-----------|
| `pandoc-template.html` | Template HTML5 customizado |
| `styles-document.css` | Estilos específicos para documentos |
| `styles.css` | Estilos globais (compartilhados com homepage) |

---

## Setup Básico

### 1. Estrutura de Diretórios

```
oficina.reflowmci.cloud/
├── index.html                    # Homepage (corrigida)
├── styles.css                    # CSS global (homepage + documentos)
├── styles-document.css           # CSS específico para documentos
├── manifest.json                 # PWA manifest
├── favicon.svg                   # Ícone
├── _templates/
│   └── pandoc-template.html      # Template Pandoc customizado
└── pesquisa-precos/
    ├── index.html                # Listagem (gerada ou manual)
    └── reforma-telhado-caps.html # Documento (gerado por Pandoc)
```

### 2. Comando Pandoc Básico

```bash
# Gerar HTML com template customizado
pandoc documento.md \
  -o documento.html \
  --template=_templates/pandoc-template.html \
  --standalone \
  --metadata title="Título do Documento" \
  --metadata description-meta="Descrição para SEO (máx 160 chars)" \
  --metadata category="pesquisa-precos" \
  --metadata url="pesquisa-precos/documento.html"
```

### 3. Configuração via YAML Frontmatter (Recomendado)

**Arquivo Markdown:** `reforma-telhado-caps.md`

```markdown
---
title: "Pesquisa de Preços — Reforma de Telhado do CAPS-I"
description-meta: "Pesquisa de preços para contratação de reforma de telhado do CAPS em Extrema/MG, conforme IN SEGES/ME 65/2021."
category: "pesquisa-precos"
url: "pesquisa-precos/reforma-telhado-caps.html"
date: "07 de fevereiro de 2026"
author: "Secretaria Municipal de Saúde - Extrema/MG"
---

# Pesquisa de Preços – Reforma de Telhado do CAPS

**Data da pesquisa:** 07 de fevereiro de 2026
...
```

**Comando simplificado:**

```bash
pandoc reforma-telhado-caps.md \
  -o reforma-telhado-caps.html \
  --template=_templates/pandoc-template.html \
  --standalone
```

---

## Metadados Suportados no Template

| Campo | Obrigatório | Uso |
|-------|-------------|-----|
| `title` | ✅ | Título da página (`<title>` + `<h1>`) |
| `description-meta` | 🟡 Recomendado | Meta description para SEO |
| `category` | 🟡 Recomendado | Categoria para breadcrumb (ex: `pesquisa-precos`) |
| `url` | 🟡 Recomendado | URL relativa para Open Graph |
| `date` | ⚪ Opcional | Data do documento |
| `author` | ⚪ Opcional | Autor(es) |
| `subtitle` | ⚪ Opcional | Subtítulo |
| `keywords` | ⚪ Opcional | Palavras-chave (array) |

**Exemplo completo:**

```yaml
---
title: "Manual Operacional de Acolhimento em Saúde Mental"
subtitle: "Protocolos e Fluxos para APS"
description-meta: "Manual operacional para profissionais de APS sobre acolhimento, classificação de risco e encaminhamento em saúde mental, conforme protocolos RAPS."
category: "manuais"
url: "manuais/acolhimento-saude-mental.html"
date: "10 de janeiro de 2026"
author: "Núcleo Interno de Regulação de Saúde Mental"
keywords:
  - acolhimento
  - saúde mental
  - APS
  - classificação de risco
---
```

---

## Automação com Makefile (Opcional)

Criar `Makefile` na raiz do projeto:

```makefile
# Configuração
TEMPLATE = _templates/pandoc-template.html
PANDOC_OPTS = --standalone --template=$(TEMPLATE)

# Fontes e destinos
MD_FILES := $(wildcard **/*.md)
HTML_FILES := $(MD_FILES:.md=.html)

# Regra padrão
all: $(HTML_FILES)

# Regra genérica: .md → .html
%.html: %.md $(TEMPLATE)
	pandoc $< -o $@ $(PANDOC_OPTS)

# Limpar HTMLs gerados
clean:
	rm -f $(HTML_FILES)

# Rebuild completo
rebuild: clean all

.PHONY: all clean rebuild
```

**Uso:**

```bash
# Gerar todos os HTMLs
make

# Regenerar tudo
make rebuild

# Limpar
make clean
```

---

## Script Batch para Windows (Alternativa)

**Arquivo:** `build-docs.bat`

```batch
@echo off
setlocal enabledelayedexpansion

set TEMPLATE=_templates\pandoc-template.html

echo Gerando documentos HTML com Pandoc...

for /r %%f in (*.md) do (
    echo Processando: %%f
    pandoc "%%f" -o "%%~dpnf.html" --standalone --template=%TEMPLATE%
)

echo.
echo Concluido!
pause
```

**Uso:** Duplo clique em `build-docs.bat`

---

## Configuração Permanente (Defaults File)

Criar `~/.pandoc/defaults/sms-extrema.yaml`:

```yaml
# Defaults para documentos SMS Extrema/MG
standalone: true
template: _templates/pandoc-template.html
metadata:
  author: "Secretaria Municipal de Saúde - Extrema/MG"
  lang: pt-BR
```

**Uso:**

```bash
pandoc documento.md -o documento.html -d sms-extrema
```

---

## Checklist de Validação

Após gerar documentos HTML com o template, validar:

### Estrutura HTML
- [ ] `<link rel="stylesheet" href="/styles.css?v=1.0.0">` presente
- [ ] `<link rel="stylesheet" href="/styles-document.css?v=1.0.0">` presente
- [ ] Meta description presente
- [ ] Open Graph tags presentes
- [ ] Breadcrumb com link "← Portal SMS"

### Acessibilidade
- [ ] Navegação por teclado funciona (Tab + Enter)
- [ ] Breadcrumb tem `aria-label`
- [ ] Links têm `aria-label` quando necessário
- [ ] Contraste de cores adequado (WebAIM)

### SEO
- [ ] `<title>` descritivo e único
- [ ] Meta description entre 120-160 caracteres
- [ ] URL relativa em `og:url`

### Performance
- [ ] CSS externo (não inline)
- [ ] Favicon carrega sem 404
- [ ] Sem erros no console

---

## Migração de Documentos Existentes

### Passo 1: Identificar HTMLs Gerados por Pandoc

```bash
# Procurar por meta generator="pandoc"
grep -r 'meta name="generator" content="pandoc"' . --include="*.html"
```

### Passo 2: Backup

```bash
mkdir backup-html-$(date +%Y%m%d)
find . -name "*.html" -exec cp {} backup-html-$(date +%Y%m%d)/ \;
```

### Passo 3: Regenerar com Template

**Se você tem os arquivos .md originais:**

```bash
for file in **/*.md; do
  pandoc "$file" -o "${file%.md}.html" \
    --template=_templates/pandoc-template.html \
    --standalone
done
```

**Se NÃO tem os .md (apenas HTML):**

Opção A: Converter HTML → Markdown → HTML
```bash
# Converter HTML → Markdown
pandoc old.html -o doc.md

# Adicionar frontmatter YAML manualmente ao doc.md
# Regenerar com template
pandoc doc.md -o new.html --template=_templates/pandoc-template.html --standalone
```

Opção B: Editar HTML manualmente (não recomendado)
- Substituir `<head>` pelo do template
- Adicionar breadcrumb antes do `<header>`
- Adicionar footer após `<main>`
- Linkar CSS externos

---

## Troubleshooting

### Problema: Template não encontrado

**Erro:**
```
pandoc: _templates/pandoc-template.html: openFile: does not exist
```

**Solução:**
```bash
# Verificar caminho
ls -la _templates/pandoc-template.html

# Usar caminho absoluto se necessário
pandoc doc.md -o doc.html --template=/path/absoluto/_templates/pandoc-template.html
```

### Problema: CSS não carrega

**Sintomas:** Documento sem estilos

**Soluções:**
1. Verificar se `styles.css` e `styles-document.css` estão no root
2. Verificar caminhos no template (devem ser `/styles.css`, não `styles.css`)
3. Limpar cache do navegador (Ctrl+Shift+R)

### Problema: Breadcrumb quebrado

**Sintomas:** Link "← Portal SMS" vai para lugar errado

**Solução:** Verificar metadado `category` no YAML:
```yaml
category: "pesquisa-precos"  # ✅ Correto
category: pesquisa-precos/   # ❌ Barra final quebra link
```

---

## Exemplos de Uso

### Exemplo 1: Pesquisa de Preços

```bash
pandoc reforma-telhado-caps.md \
  -o reforma-telhado-caps.html \
  --template=_templates/pandoc-template.html \
  --standalone \
  --metadata category="pesquisa-precos"
```

### Exemplo 2: Manual Operacional

```bash
pandoc manual-acolhimento.md \
  -o manual-acolhimento.html \
  --template=_templates/pandoc-template.html \
  --standalone \
  --metadata category="manuais" \
  --metadata description-meta="Manual de acolhimento em saúde mental para APS"
```

### Exemplo 3: Diagnóstico Epidemiológico

```bash
pandoc diagnostico-sm-2025.md \
  -o diagnostico-sm-2025.html \
  --template=_templates/pandoc-template.html \
  --standalone \
  --metadata category="diagnosticos" \
  --metadata url="diagnosticos/diagnostico-sm-2025.html"
```

---

## Próximos Passos

1. ✅ Upload do template para `_templates/pandoc-template.html`
2. ✅ Upload de `styles-document.css` para raiz
3. 🔄 Regenerar documentos existentes com novo template
4. 🔄 Configurar build automatizado (Makefile ou script)
5. 🔄 Documentar processo no README do repositório

---

**Versão:** 1.0.0
**Data:** 2026-02-15
**Compatibilidade:** Pandoc 2.x+
**Mantido por:** SMS Extrema/MG
