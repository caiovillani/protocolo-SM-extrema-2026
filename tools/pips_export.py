#!/usr/bin/env python3
"""
Tool: PIPS Export
Descrição: Exporta entregas finais do projeto PIPS

Uso:
    python tools/pips_export.py --project <nome> --format <md|yaml|json>

Inputs:
    --project: Nome do projeto PIPS
    --format: Formato de saída (md, yaml, json)
    --output: Caminho de saída customizado (opcional)

Outputs:
    - Arquivo final em _output/final/ ou caminho customizado

Dependências:
    - pyyaml
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import yaml

# Adicionar src ao path para imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.context_engine.pips import PIPSEngine, list_projects
from src.context_engine.pips_models import OUTPUT_DIR, INSIGHTS_CONSOLIDATED_FILE, INSIGHTS_RAW_FILE


def export_markdown(engine: PIPSEngine, include_raw: bool = False) -> str:
    """Exporta como Markdown formatado."""
    config, state = engine.load_project()

    content = f"""# Relatório Final: {config.project_name}

## Metadados

| Campo | Valor |
|-------|-------|
| **Projeto** | {config.project_name} |
| **Status** | {state.status.value} |
| **Data de criação** | {config.created_at.strftime('%Y-%m-%d %H:%M')} |
| **Última atualização** | {state.last_updated.strftime('%Y-%m-%d %H:%M')} |
| **Ciclos executados** | {state.current_cycle} |
| **Progresso** | {state.get_progress_percentage():.1f}% |

## Objetivo

{config.objective}

## Síntese Consolidada

{state.insights_consolidated or '*Nenhuma síntese consolidada disponível.*'}

## Estatísticas de Processamento

- **Total de itens na fila:** {len(state.queue)}
- **Itens concluídos:** {sum(1 for i in state.queue if i.status.value == 'concluido')}
- **Itens pendentes:** {len(state.get_pending_items())}
- **Tokens processados:** {state.tokens_processed:,}
- **Erros registrados:** {len(state.errors)}

"""

    if state.errors:
        content += "## Erros Registrados\n\n"
        for error in state.errors[-10:]:  # Últimos 10 erros
            content += f"- {error}\n"
        if len(state.errors) > 10:
            content += f"\n*... e mais {len(state.errors) - 10} erro(s)*\n"
        content += "\n"

    if include_raw:
        raw_path = engine.project_path / OUTPUT_DIR / INSIGHTS_RAW_FILE
        if raw_path.exists():
            raw_content = raw_path.read_text(encoding='utf-8')
            content += "## Insights Brutos (Raw)\n\n"
            content += raw_content

    content += f"""
---

*Gerado pelo PIPS (Protocolo de Processamento Iterativo com Persistência de Estado)*
*Data de exportação: {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""

    return content


def export_yaml(engine: PIPSEngine) -> dict:
    """Exporta como YAML estruturado."""
    config, state = engine.load_project()

    data = {
        'metadata': {
            'project_name': config.project_name,
            'status': state.status.value,
            'created_at': config.created_at.isoformat(),
            'last_updated': state.last_updated.isoformat(),
            'cycles_executed': state.current_cycle,
            'progress_percentage': round(state.get_progress_percentage(), 1),
        },
        'objective': config.objective,
        'synthesis': state.insights_consolidated,
        'statistics': {
            'total_items': len(state.queue),
            'completed_items': sum(1 for i in state.queue if i.status.value == 'concluido'),
            'pending_items': len(state.get_pending_items()),
            'tokens_processed': state.tokens_processed,
            'errors_count': len(state.errors),
        },
        'queue_summary': [
            {
                'id': item.id,
                'source_file': str(item.source_file),
                'status': item.status.value,
                'chunk': f"{item.chunk_index + 1}/{item.total_chunks}",
            }
            for item in state.queue
        ],
        'errors': state.errors[-20:] if state.errors else [],
        'export_info': {
            'format': 'yaml',
            'exported_at': datetime.now().isoformat(),
            'tool': 'pips_export.py',
        },
    }

    return data


def export_json(engine: PIPSEngine) -> dict:
    """Exporta como JSON."""
    # Reutiliza a estrutura do YAML
    return export_yaml(engine)


def main():
    parser = argparse.ArgumentParser(
        description="Exportar projeto PIPS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
    # Exportar como Markdown
    python tools/pips_export.py --project meu_projeto --format md

    # Exportar como YAML para arquivo específico
    python tools/pips_export.py --project meu_projeto --format yaml --output ./relatorio.yaml

    # Exportar como JSON incluindo insights raw
    python tools/pips_export.py --project meu_projeto --format json --include-raw
        """,
    )
    parser.add_argument(
        "--project",
        required=True,
        help="Nome do projeto PIPS",
    )
    parser.add_argument(
        "--format",
        choices=["md", "yaml", "json"],
        default="md",
        help="Formato de saída (padrão: md)",
    )
    parser.add_argument(
        "--output",
        help="Caminho de saída customizado",
    )
    parser.add_argument(
        "--include-raw",
        action="store_true",
        help="Incluir insights raw na exportação (apenas para md)",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Imprimir no stdout ao invés de salvar em arquivo",
    )

    args = parser.parse_args()

    # Verificar projeto
    try:
        engine = PIPSEngine(args.project)
    except ValueError as e:
        print(f"❌ Nome de projeto inválido: {e}", file=sys.stderr)
        sys.exit(1)

    if not engine.project_exists():
        print(f"❌ Projeto '{args.project}' não encontrado.", file=sys.stderr)
        projects = list_projects()
        if projects:
            print(f"   Projetos disponíveis: {', '.join(projects)}", file=sys.stderr)
        sys.exit(1)

    # Gerar conteúdo
    try:
        if args.format == "md":
            content = export_markdown(engine, include_raw=args.include_raw)
            extension = "md"
        elif args.format == "yaml":
            data = export_yaml(engine)
            content = yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)
            extension = "yaml"
        elif args.format == "json":
            data = export_json(engine)
            content = json.dumps(data, ensure_ascii=False, indent=2)
            extension = "json"
    except Exception as e:
        print(f"❌ Erro ao gerar exportação: {e}", file=sys.stderr)
        sys.exit(1)

    # Output
    if args.stdout:
        print(content)
        sys.exit(0)

    # Determinar caminho de saída
    if args.output:
        output_path = Path(args.output)
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{args.project}_export_{timestamp}.{extension}"
        output_path = engine.project_path / OUTPUT_DIR / "final" / filename

    # Criar diretório se necessário
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Salvar arquivo
    output_path.write_text(content, encoding='utf-8')

    print("=" * 60)
    print(f"  Exportação PIPS: {args.project}")
    print("=" * 60)
    print()
    print(f"✅ Exportação concluída!")
    print(f"   Formato: {args.format.upper()}")
    print(f"   Arquivo: {output_path}")
    print(f"   Tamanho: {len(content):,} caracteres")

    # Registrar checkpoint
    try:
        engine.load_project()
        engine.create_checkpoint(
            "export",
            f"Exportado como {args.format.upper()} para {output_path.name}"
        )
    except Exception:
        pass  # Ignorar erros de checkpoint


if __name__ == "__main__":
    main()
