#!/usr/bin/env python3
"""
Tool: PIPS Consolidate
Descrição: Consolida insights raw em síntese estruturada

Uso:
    python tools/pips_consolidate.py --project <nome> [--mode append|replace]

Inputs:
    --project: Nome do projeto PIPS
    --mode: Modo de consolidação (append ou replace)

Outputs:
    - Arquivo insights_consolidated.md atualizado
    - Checkpoint registrado

Dependências:
    - pyyaml
"""

import argparse
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

# Adicionar src ao path para imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.context_engine.pips import PIPSEngine, list_projects
from src.context_engine.pips_models import OUTPUT_DIR, INSIGHTS_RAW_FILE


def extract_insights_from_raw(raw_content: str) -> list[dict]:
    """Extrai insights estruturados do conteúdo raw."""
    insights = []

    # Pattern para encontrar seções de ciclo
    cycle_pattern = r'## Ciclo (\d+) - (\d{4}-\d{2}-\d{2} \d{2}:\d{2})'
    cycles = re.split(cycle_pattern, raw_content)

    # cycles[0] é o header, depois vem [ciclo, data, conteúdo, ciclo, data, conteúdo, ...]
    i = 1
    while i < len(cycles) - 2:
        cycle_num = int(cycles[i])
        timestamp = cycles[i + 1]
        content = cycles[i + 2]

        # Extrair arquivo fonte se presente
        source_match = re.search(r'### Arquivo: (.+)', content)
        source = source_match.group(1).strip() if source_match else "desconhecido"

        # Extrair flags se presentes
        flags = []
        flag_matches = re.findall(r'\[([A-Z]+)\]', content)
        flags.extend(flag_matches)

        # Limpar conteúdo
        clean_content = re.sub(r'### Arquivo: .+\n', '', content)
        clean_content = re.sub(r'---\s*$', '', clean_content).strip()

        if clean_content:
            insights.append({
                'cycle': cycle_num,
                'timestamp': timestamp,
                'source': source,
                'content': clean_content,
                'flags': flags,
            })

        i += 3

    return insights


def identify_patterns(insights: list[dict]) -> dict:
    """Identifica padrões nos insights."""
    patterns = {
        'sources': Counter(),
        'flags': Counter(),
        'keywords': Counter(),
    }

    # Contar fontes
    for insight in insights:
        patterns['sources'][insight['source']] += 1
        for flag in insight['flags']:
            patterns['flags'][flag] += 1

    # Identificar palavras-chave frequentes (simplificado)
    all_text = ' '.join(i['content'] for i in insights)
    words = re.findall(r'\b[a-záàâãéèêíïóôõöúç]{5,}\b', all_text.lower())
    # Filtrar stopwords comuns em português
    stopwords = {
        'sobre', 'muito', 'também', 'quando', 'apenas', 'ainda',
        'porque', 'então', 'porém', 'sendo', 'dessa', 'desse',
        'desta', 'deste', 'mesmo', 'entre', 'depois', 'antes',
        'outros', 'outras', 'outra', 'outro', 'todos', 'todas',
    }
    filtered_words = [w for w in words if w not in stopwords]
    patterns['keywords'] = Counter(filtered_words).most_common(20)

    return patterns


def generate_synthesis(insights: list[dict], patterns: dict) -> str:
    """Gera síntese consolidada dos insights."""
    synthesis = []

    # Estatísticas gerais
    synthesis.append("## Resumo Estatístico\n")
    synthesis.append(f"- **Total de insights:** {len(insights)}")
    synthesis.append(f"- **Ciclos processados:** {max(i['cycle'] for i in insights) if insights else 0}")
    synthesis.append(f"- **Arquivos fonte:** {len(patterns['sources'])}")
    synthesis.append("")

    # Flags encontradas
    if patterns['flags']:
        synthesis.append("## Flags Identificadas\n")
        for flag, count in patterns['flags'].most_common():
            emoji = {
                'AMBIGUIDADE': '⚠️',
                'CONTRADICAO': '❌',
                'VALIDAR': '🔍',
            }.get(flag, '📌')
            synthesis.append(f"- {emoji} **{flag}:** {count} ocorrência(s)")
        synthesis.append("")

    # Palavras-chave
    if patterns['keywords']:
        synthesis.append("## Temas Frequentes\n")
        keywords_text = ", ".join(f"**{kw}** ({count})" for kw, count in patterns['keywords'][:10])
        synthesis.append(keywords_text)
        synthesis.append("")

    # Arquivos mais processados
    synthesis.append("## Fontes Processadas\n")
    for source, count in patterns['sources'].most_common(10):
        synthesis.append(f"- `{source}`: {count} insight(s)")
    synthesis.append("")

    # Insights por ciclo (resumido)
    synthesis.append("## Insights por Ciclo\n")
    insights_by_cycle = {}
    for insight in insights:
        cycle = insight['cycle']
        if cycle not in insights_by_cycle:
            insights_by_cycle[cycle] = []
        insights_by_cycle[cycle].append(insight)

    for cycle in sorted(insights_by_cycle.keys()):
        cycle_insights = insights_by_cycle[cycle]
        synthesis.append(f"### Ciclo {cycle}")
        synthesis.append(f"*{len(cycle_insights)} insight(s)*\n")

        # Mostrar resumo dos primeiros insights do ciclo
        for insight in cycle_insights[:3]:
            # Truncar conteúdo para resumo
            content_preview = insight['content'][:200]
            if len(insight['content']) > 200:
                content_preview += "..."
            synthesis.append(f"- {content_preview}")

        if len(cycle_insights) > 3:
            synthesis.append(f"- *... e mais {len(cycle_insights) - 3} insight(s)*")
        synthesis.append("")

    return "\n".join(synthesis)


def main():
    parser = argparse.ArgumentParser(
        description="Consolidar insights PIPS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
    # Consolidar insights (substitui consolidação anterior)
    python tools/pips_consolidate.py --project meu_projeto

    # Consolidar em modo append (adiciona à consolidação existente)
    python tools/pips_consolidate.py --project meu_projeto --mode append

    # Visualizar sem salvar
    python tools/pips_consolidate.py --project meu_projeto --dry-run
        """,
    )
    parser.add_argument(
        "--project",
        required=True,
        help="Nome do projeto PIPS",
    )
    parser.add_argument(
        "--mode",
        choices=["replace", "append"],
        default="replace",
        help="Modo de consolidação (padrão: replace)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Apenas mostrar síntese, sem salvar",
    )

    args = parser.parse_args()

    # Verificar projeto
    try:
        engine = PIPSEngine(args.project)
    except ValueError as e:
        print(f"❌ Nome de projeto inválido: {e}")
        sys.exit(1)

    if not engine.project_exists():
        print(f"❌ Projeto '{args.project}' não encontrado.")
        projects = list_projects()
        if projects:
            print(f"   Projetos disponíveis: {', '.join(projects)}")
        sys.exit(1)

    print("=" * 60)
    print(f"  Consolidação PIPS: {args.project}")
    print("=" * 60)
    print()

    # Carregar projeto
    try:
        engine.load_project()
    except Exception as e:
        print(f"❌ Erro ao carregar projeto: {e}")
        sys.exit(1)

    # Ler insights raw
    raw_path = engine.project_path / OUTPUT_DIR / INSIGHTS_RAW_FILE
    if not raw_path.exists():
        print("❌ Arquivo de insights raw não encontrado.")
        sys.exit(1)

    raw_content = raw_path.read_text(encoding='utf-8')

    # Extrair insights
    print("🔍 Extraindo insights do arquivo raw...")
    insights = extract_insights_from_raw(raw_content)
    print(f"   Encontrados: {len(insights)} insight(s)")

    if not insights:
        print("\n⚠️  Nenhum insight encontrado para consolidar.")
        print("   Execute o processamento primeiro com /pips resume")
        sys.exit(0)

    # Identificar padrões
    print("\n🔍 Identificando padrões...")
    patterns = identify_patterns(insights)
    print(f"   Fontes únicas: {len(patterns['sources'])}")
    print(f"   Flags encontradas: {sum(patterns['flags'].values())}")

    # Gerar síntese
    print("\n📝 Gerando síntese consolidada...")
    synthesis = generate_synthesis(insights, patterns)

    if args.dry_run:
        print("\n" + "-" * 60)
        print("PRÉVIA DA SÍNTESE (dry-run):")
        print("-" * 60)
        print(synthesis)
        print("-" * 60)
        print("\n💡 Use sem --dry-run para salvar a síntese.")
        sys.exit(0)

    # Salvar síntese
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    header = f"""# Síntese Consolidada

**Projeto:** {args.project}
**Última consolidação:** {timestamp}
**Modo:** {args.mode}

---

"""

    if args.mode == "append":
        # Ler consolidação existente e adicionar
        existing = engine._state.insights_consolidated or ""
        full_synthesis = existing + f"\n\n## Consolidação de {timestamp}\n\n" + synthesis
    else:
        full_synthesis = header + synthesis

    engine.update_consolidated(full_synthesis)

    # Criar checkpoint
    engine.create_checkpoint(
        "consolidate",
        f"Síntese consolidada ({args.mode}): {len(insights)} insights"
    )

    print("\n✅ Consolidação concluída!")
    print(f"   Arquivo atualizado: _output/insights_consolidated.md")
    print(f"   Insights processados: {len(insights)}")


if __name__ == "__main__":
    main()
