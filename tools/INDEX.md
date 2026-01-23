# Tools Index

Este diretório contém scripts Python para execução determinística de tarefas.

## Como Usar

1. Cada ferramenta é um script independente com inputs/outputs bem definidos
2. Use `_template.py` como base para criar novas ferramentas
3. Credenciais e API keys ficam em `.env` (nunca comite este arquivo)

## Dependências Comuns

```bash
pip install python-dotenv requests
```

## Ferramentas Disponíveis

| Ferramenta | Descrição | Inputs | Outputs |
|------------|-----------|--------|---------|
| _template.py | Template para novas ferramentas | - | - |
| pips_init.py | Inicializar projeto PIPS | --name, --objective, --sources | .pips/projeto_<nome>/ |
| pips_validate.py | Validar integridade de projeto PIPS | --project [--fix] | Relatório de validação |
| pips_consolidate.py | Consolidar insights em síntese | --project [--mode] | insights_consolidated.md |
| pips_export.py | Exportar entregas finais | --project, --format | Arquivo final |

---

### Ferramentas PIPS

As ferramentas PIPS suportam o workflow de processamento iterativo com persistência de estado.

**Exemplos de uso:**

```bash
# Inicializar projeto
python tools/pips_init.py --name meu_projeto --objective "Analisar transcricoes" --sources ./dados/

# Validar projeto
python tools/pips_validate.py --project meu_projeto --fix

# Consolidar insights
python tools/pips_consolidate.py --project meu_projeto

# Exportar como Markdown
python tools/pips_export.py --project meu_projeto --format md
```

---

*Adicione novas ferramentas a esta tabela conforme forem criadas*
