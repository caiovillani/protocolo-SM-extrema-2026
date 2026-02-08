# src/context_engine/formatter.py

"""Centralized formatting utilities for the Context Engine.

This module provides consistent formatting for all command outputs, including:
- Box-drawing utilities (headers, separators)
- Status emoji mappings
- Command-specific formatters

All user-facing text is in Portuguese (Brazilian).
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Constants (Single Source of Truth)
# ---------------------------------------------------------------------------

BOX_WIDTH = 51
HEADER_CHAR = "═"
SEPARATOR_CHAR = "─"

# Status emoji mapping (eliminates duplication from pipeline.py)
STATUS_EMOJI: Dict[str, str] = {
    "nao_iniciado": "⏸️",
    "em_progresso": "▶️",
    "pausado": "⏸️",
    "validando": "🔍",
    "concluido": "✅",
    "erro": "❌",
}

# Command-specific emoji
COMMAND_EMOJI: Dict[str, str] = {
    "template": "📋",
    "auditoria": "🔍",
    "orientacao": "💡",
    "conformidade": "✅",
    "comparar": "⚖️",
    "pips": "🔄",
    "contexto": "📄",
    "export": "📤",
}

# Content type emoji
CONTENT_EMOJI: Dict[str, str] = {
    "arquivo": "📄",
    "diretorio": "📁",
    "metricas": "📊",
    "conceitos": "💡",
    "relacionamentos": "🔗",
    "keywords": "🏷️",
    "tokens": "🔢",
    "tempo": "⏱️",
    "linhas": "📏",
    "secoes": "📑",
    "resumo": "📝",
    "progresso": "📊",
    "ciclo": "🔄",
    "objetivo": "📝",
    "checkpoint": "📍",
    "erros": "⚠️",
    "pendentes": "⏳",
    "concluidos": "✅",
}


# ---------------------------------------------------------------------------
# Box-Drawing Utilities
# ---------------------------------------------------------------------------

def format_header(title: str, width: int = BOX_WIDTH) -> str:
    """Create a box-drawing header with centered title.

    Args:
        title: The title text to display
        width: Width of the box (default: 51 characters)

    Returns:
        Formatted header string with box-drawing characters

    Example:
        >>> format_header("PIPS: meu_projeto")
        '═══════════════════════════════════════════════════
          PIPS: meu_projeto
        ═══════════════════════════════════════════════════'
    """
    line = HEADER_CHAR * width
    return f"{line}\n  {title}\n{line}"


def format_separator(char: str = SEPARATOR_CHAR, width: int = BOX_WIDTH) -> str:
    """Create a horizontal separator line.

    Args:
        char: Character to use for the line (default: ─)
        width: Width of the separator (default: 51 characters)

    Returns:
        Separator string
    """
    return char * width


def format_section(
    title: str,
    content: str,
    emoji: str = "",
    indent: int = 0
) -> str:
    """Format a labeled section with optional emoji.

    Args:
        title: Section title
        content: Section content
        emoji: Optional emoji prefix
        indent: Number of spaces to indent

    Returns:
        Formatted section string
    """
    prefix = " " * indent
    emoji_prefix = f"{emoji} " if emoji else ""
    return f"{prefix}{emoji_prefix}{title}:\n{prefix}{content}"


def get_status_emoji(status: str) -> str:
    """Get emoji for a given status value.

    Args:
        status: Status string (e.g., "concluido", "em_progresso")

    Returns:
        Corresponding emoji or ❓ if unknown
    """
    return STATUS_EMOJI.get(status, "❓")


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to specified length with suffix.

    Args:
        text: Text to truncate
        max_length: Maximum length before truncation
        suffix: Suffix to append when truncated (default: "...")

    Returns:
        Truncated text with suffix, or original if within limit
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + suffix


def format_number(value: int) -> str:
    """Format number with thousands separator.

    Args:
        value: Number to format

    Returns:
        Formatted string with comma separators
    """
    return f"{value:,}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format percentage value.

    Args:
        value: Percentage value (0-100)
        decimals: Number of decimal places

    Returns:
        Formatted percentage string
    """
    return f"{value:.{decimals}f}%"


# ---------------------------------------------------------------------------
# PIPS Formatters
# ---------------------------------------------------------------------------

def format_pips_status(
    project_name: str,
    config: Any,
    state: Any
) -> str:
    """Format PIPS project status output.

    Args:
        project_name: Name of the PIPS project
        config: Project configuration object
        state: Project state object

    Returns:
        Formatted status string with box-drawing and emoji
    """
    progress = state.get_progress_percentage()
    pending = len(state.get_pending_items())
    total = len(state.queue)
    completed = total - pending

    status_emoji = get_status_emoji(state.status.value)

    output = f"""
{format_header(f"PIPS: {project_name}")}

{status_emoji} Status: {state.status.value.upper()}
{CONTENT_EMOJI['progresso']} Progresso: {format_percentage(progress)} ({completed}/{total} itens)
{CONTENT_EMOJI['ciclo']} Ciclo atual: {state.current_cycle}

{CONTENT_EMOJI['objetivo']} Objetivo:
{truncate_text(config.objective, 200)}

{CONTENT_EMOJI['diretorio']} Arquivos na fila: {total}
{CONTENT_EMOJI['concluidos']} Processados: {completed}
{CONTENT_EMOJI['pendentes']} Pendentes: {pending}

🕐 Última atualização: {state.last_updated.strftime('%Y-%m-%d %H:%M')}
"""

    if state.errors:
        output += f"\n{CONTENT_EMOJI['erros']} Erros registrados: {len(state.errors)}\n"

    return output.strip()


def format_pips_list(projects: List[Tuple[str, Any, Any]]) -> str:
    """Format list of PIPS projects.

    Args:
        projects: List of (project_name, config, state) tuples

    Returns:
        Formatted project list string
    """
    if not projects:
        return (
            "Nenhum projeto PIPS encontrado.\n\n"
            "Para criar um novo projeto:\n"
            "  /pips init <nome> <objetivo>"
        )

    output = f"{format_header('PROJETOS PIPS')}\n\n"

    for project_name, config, state in projects:
        try:
            progress = state.get_progress_percentage()
            status = state.status.value
            status_emoji = get_status_emoji(status)

            output += f"  {status_emoji} {project_name}\n"
            output += f"     Status: {status} | Progresso: {format_percentage(progress)}\n\n"
        except Exception:
            output += f"  ❓ {project_name} (erro ao carregar)\n\n"

    output += f"{format_separator()}\n"
    output += "Comandos: /pips status <nome> | /pips resume <nome>\n"

    return output


def format_pips_init_success(
    project_name: str,
    objective: str
) -> str:
    """Format PIPS project initialization success message.

    Args:
        project_name: Name of the created project
        objective: Project objective

    Returns:
        Formatted success message
    """
    return (
        f"Projeto PIPS '{project_name}' criado com sucesso!\n\n"
        f"Objetivo: {objective}\n\n"
        "Próximos passos:\n"
        f"1. Adicione arquivos fonte em: .pips/projeto_{project_name}/_source/\n"
        f"2. Execute /pips resume {project_name} para iniciar processamento\n"
        f"3. Use /pips status {project_name} para acompanhar progresso"
    )


def format_pips_resume(
    project_name: str,
    state: Any,
    next_item: Any
) -> str:
    """Format PIPS project resume message.

    Args:
        project_name: Name of the project
        state: Project state object
        next_item: Next queue item to process

    Returns:
        Formatted resume message
    """
    progress = state.get_progress_percentage()

    return f"""
Projeto '{project_name}' retomado com sucesso!

{CONTENT_EMOJI['progresso']} Progresso: {format_percentage(progress)}
{CONTENT_EMOJI['ciclo']} Ciclo: {state.current_cycle}

Próximo item a processar:
  {CONTENT_EMOJI['arquivo']} Arquivo: {next_item.source_file.name}
  📦 Chunk: {next_item.chunk_index + 1}/{next_item.total_chunks}
  {CONTENT_EMOJI['linhas']} Tokens estimados: {format_number(next_item.token_estimate)}

Para processar o próximo item, carregue o arquivo e use:
  engine.work() → processe → engine.save(item_id, resultado)
"""


# ---------------------------------------------------------------------------
# Contexto Formatters
# ---------------------------------------------------------------------------

def format_contexto_document(doc: Any) -> str:
    """Format single document context result.

    Args:
        doc: Processed document object

    Returns:
        Formatted document result string
    """
    output = f"{format_header(f'CONTEXTO: {doc.metadata.file_path.name}')}\n\n"

    output += f"{CONTENT_EMOJI['arquivo']} Tipo: {doc.metadata.file_type}\n"
    output += f"{CONTENT_EMOJI['linhas']} Linhas: {doc.metadata.lines_count}\n"
    output += f"{CONTENT_EMOJI['tokens']} Tokens estimados: {format_number(doc.metadata.tokens_estimate)}\n"
    output += f"{CONTENT_EMOJI['tempo']} Tempo de processamento: {doc.metadata.processing_time_ms:.1f}ms\n\n"

    if doc.sections:
        output += f"{CONTENT_EMOJI['secoes']} Seções:\n"
        for section in doc.sections[:10]:
            indent = "  " * section.level
            output += f"  {indent}• {section.title}\n"
        if len(doc.sections) > 10:
            output += f"  ... e mais {len(doc.sections) - 10} seções\n"
        output += "\n"

    if doc.concepts:
        output += f"{CONTENT_EMOJI['conceitos']} Conceitos extraídos: {len(doc.concepts)}\n"
        top_concepts = doc.get_top_concepts(5)
        for concept in top_concepts:
            output += f"  • [{concept.type.value}] {truncate_text(concept.text, 50)}\n"
        output += "\n"

    if doc.relationships:
        output += f"{CONTENT_EMOJI['relacionamentos']} Relacionamentos: {len(doc.relationships)}\n"

    if doc.summary:
        output += f"\n{CONTENT_EMOJI['resumo']} Resumo:\n{truncate_text(doc.summary, 500)}\n"

    return output


def format_contexto_directory(
    documents: List[Any],
    index: Any,
    directory: Path
) -> str:
    """Format directory context processing result.

    Args:
        documents: List of processed documents
        index: Directory index object
        directory: Path to the processed directory

    Returns:
        Formatted directory result string
    """
    output = f"{format_header(f'CONTEXTO: {directory.name}/')}\n\n"

    output += f"{CONTENT_EMOJI['diretorio']} Arquivos processados: {len(documents)}\n"

    total_concepts = sum(len(d.concepts) for d in documents)
    total_relationships = sum(len(d.relationships) for d in documents)
    total_tokens = sum(d.metadata.tokens_estimate for d in documents)

    output += f"{CONTENT_EMOJI['conceitos']} Total de conceitos: {total_concepts}\n"
    output += f"{CONTENT_EMOJI['relacionamentos']} Total de relacionamentos: {total_relationships}\n"
    output += f"{CONTENT_EMOJI['tokens']} Tokens estimados: {format_number(total_tokens)}\n\n"

    # Concepts by type summary
    if index.concepts_by_type:
        output += f"{CONTENT_EMOJI['metricas']} Conceitos por tipo:\n"
        for concept_type, concept_ids in sorted(index.concepts_by_type.items()):
            output += f"  • {concept_type}: {len(concept_ids)}\n"
        output += "\n"

    # Top keywords
    if index.concepts_by_keyword:
        sorted_keywords = sorted(
            index.concepts_by_keyword.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:10]
        output += f"{CONTENT_EMOJI['keywords']} Palavras-chave frequentes:\n"
        for keyword, concept_ids in sorted_keywords:
            output += f"  • {keyword}: {len(concept_ids)} ocorrências\n"

    return output


def format_contexto_stats(stats: Dict[str, Any]) -> str:
    """Format context cache statistics.

    Args:
        stats: Cache statistics dictionary

    Returns:
        Formatted statistics string
    """
    return (
        f"{format_header('ESTATÍSTICAS DO CACHE DE CONTEXTO')}\n\n"
        f"{CONTENT_EMOJI['metricas']} Hits: {stats.get('hits', 0)}\n"
        f"{CONTENT_EMOJI['metricas']} Misses: {stats.get('misses', 0)}\n"
        f"{CONTENT_EMOJI['metricas']} Taxa de acerto: {stats.get('hit_rate', 0):.1%}\n"
        f"{CONTENT_EMOJI['diretorio']} Entradas em cache: {stats.get('entries', 0)}\n"
        f"💾 Tamanho total: {stats.get('size_mb', 0):.2f} MB"
    )


# ---------------------------------------------------------------------------
# Template & Placeholder Formatters
# ---------------------------------------------------------------------------

def format_template_output(
    template_id: str,
    data: Optional[Dict[str, Any]] = None
) -> str:
    """Format template command output.

    Args:
        template_id: ID of the template
        data: Template data dictionary

    Returns:
        Formatted template output
    """
    output = f"{format_header(f'TEMPLATE: {template_id}')}\n\n"

    if data:
        output += f"{COMMAND_EMOJI['template']} Tipo: {data.get('tipo', 'N/A')}\n"
        output += f"{CONTENT_EMOJI['arquivo']} Arquivo: {data.get('arquivo', 'N/A')}\n\n"

        if 'secoes' in data:
            output += f"{CONTENT_EMOJI['secoes']} Seções:\n"
            for secao in data['secoes']:
                output += f"  • {secao}\n"
            output += "\n"

        if 'conteudo' in data:
            output += f"{CONTENT_EMOJI['resumo']} Conteúdo:\n{data['conteudo']}\n"
    else:
        output += f"{COMMAND_EMOJI['template']} Template '{template_id}' carregado.\n"
        output += "(Implemente a lógica de renderização de template)"

    return output


def format_auditoria_output(
    registro: str,
    conformidade: Optional[Dict[str, Any]] = None
) -> str:
    """Format auditoria command output.

    Args:
        registro: Registry or document being audited
        conformidade: Conformance results dictionary

    Returns:
        Formatted auditoria output
    """
    output = f"{format_header(f'AUDITORIA: {registro}')}\n\n"

    if conformidade:
        status = conformidade.get('status', 'pendente')
        status_emoji = get_status_emoji(status)

        output += f"{status_emoji} Status: {status.upper()}\n"
        output += f"{CONTENT_EMOJI['metricas']} Score: {conformidade.get('score', 'N/A')}\n\n"

        if 'itens' in conformidade:
            output += f"{COMMAND_EMOJI['auditoria']} Itens verificados:\n"
            for item in conformidade['itens']:
                item_emoji = "✅" if item.get('conforme') else "❌"
                output += f"  {item_emoji} {item.get('descricao', 'Item')}\n"
            output += "\n"

        if 'observacoes' in conformidade:
            output += f"{CONTENT_EMOJI['resumo']} Observações:\n{conformidade['observacoes']}\n"
    else:
        output += f"{COMMAND_EMOJI['auditoria']} Análise de conformidade para '{registro}'.\n"
        output += "(Implemente a lógica de auditoria)"

    return output


def format_orientacao_output(
    campo: str,
    orientacoes: Optional[List[str]] = None
) -> str:
    """Format orientacao command output.

    Args:
        campo: Field or topic for guidance
        orientacoes: List of guidance items

    Returns:
        Formatted orientacao output
    """
    output = f"{format_header(f'ORIENTAÇÃO: {campo}')}\n\n"

    if orientacoes:
        output += f"{COMMAND_EMOJI['orientacao']} Orientações:\n"
        for i, orientacao in enumerate(orientacoes, 1):
            output += f"  {i}. {orientacao}\n"
    else:
        output += f"{COMMAND_EMOJI['orientacao']} Orientações para '{campo}'.\n"
        output += "(Implemente a lógica de orientação)"

    return output


def format_comparar_output(
    tipo1: str,
    tipo2: str,
    diff: Optional[Dict[str, Any]] = None
) -> str:
    """Format comparar command output.

    Args:
        tipo1: First item type/name
        tipo2: Second item type/name
        diff: Comparison results dictionary

    Returns:
        Formatted comparison output
    """
    output = f"{format_header(f'COMPARAÇÃO: {tipo1} vs {tipo2}')}\n\n"

    if diff:
        output += f"{COMMAND_EMOJI['comparar']} Resultado:\n\n"

        if 'iguais' in diff:
            output += "✅ Itens iguais:\n"
            for item in diff['iguais']:
                output += f"  • {item}\n"
            output += "\n"

        if 'diferentes' in diff:
            output += "⚠️ Itens diferentes:\n"
            for item in diff['diferentes']:
                output += f"  • {item.get('campo', 'Campo')}: "
                output += f"{item.get('valor1', '?')} → {item.get('valor2', '?')}\n"
            output += "\n"

        if 'exclusivos' in diff:
            output += "📌 Itens exclusivos:\n"
            for item in diff['exclusivos']:
                output += f"  • [{item.get('origem', '?')}] {item.get('descricao', 'Item')}\n"
    else:
        output += f"{COMMAND_EMOJI['comparar']} Comparação entre '{tipo1}' e '{tipo2}'.\n"
        output += "(Implemente a lógica de comparação)"

    return output


def format_conformidade_output(
    questao: str,
    resultado: Optional[Dict[str, Any]] = None
) -> str:
    """Format conformidade command output.

    Args:
        questao: Compliance question or topic
        resultado: Compliance results dictionary

    Returns:
        Formatted conformidade output
    """
    output = f"{format_header(f'CONFORMIDADE: {questao}')}\n\n"

    if resultado:
        conforme = resultado.get('conforme', False)
        status_emoji = "✅" if conforme else "❌"

        output += f"{status_emoji} Resultado: {'CONFORME' if conforme else 'NÃO CONFORME'}\n\n"

        if 'normas' in resultado:
            output += f"{CONTENT_EMOJI['arquivo']} Normas aplicáveis:\n"
            for norma in resultado['normas']:
                output += f"  • {norma}\n"
            output += "\n"

        if 'justificativa' in resultado:
            output += f"{CONTENT_EMOJI['resumo']} Justificativa:\n{resultado['justificativa']}\n"
    else:
        output += f"{COMMAND_EMOJI['conformidade']} Verificação de conformidade para '{questao}'.\n"
        output += "(Implemente a lógica de conformidade)"

    return output


# ---------------------------------------------------------------------------
# Citation Formatters (Evidence Traceability)
# ---------------------------------------------------------------------------

def format_citation(
    source_file: str,
    line_number: int,
    short: bool = False
) -> str:
    """Format a source citation for evidence traceability.

    Args:
        source_file: Path to the source file
        line_number: Line number in the source file
        short: If True, use abbreviated format

    Returns:
        Formatted citation string (Vancouver-inspired format)

    Example:
        >>> format_citation("CLI_02_TRANSTORNO_ESPECTRO_AUTISTA.md", 847)
        '(Fonte: CLI_02_TRANSTORNO_ESPECTRO_AUTISTA.md:847)'
        >>> format_citation("CLI_02_TRANSTORNO_ESPECTRO_AUTISTA.md", 847, short=True)
        '[CLI_02:847]'
    """
    from pathlib import Path

    filename = Path(source_file).name
    if short:
        # Abbreviated format: [CLI_02:847]
        short_name = filename.replace('.md', '').replace('.pdf', '')[:15]
        return f"[{short_name}:{line_number}]"
    else:
        # Full format: (Fonte: filename.md:847)
        return f"(Fonte: {filename}:{line_number})"


def format_citations_block(
    concepts: List[Any],
    title: str = "Fontes"
) -> str:
    """Format a block of citations from concepts.

    Args:
        concepts: List of Concept objects with source_file and line_number
        title: Title for the citations block

    Returns:
        Formatted citations block string

    Example output:
        📚 Fontes:
          • CLI_02_TRANSTORNO_ESPECTRO_AUTISTA.md:847
          • MACROFLUXO_NARRATIVO_DI_TEA.md:234
    """
    if not concepts:
        return ""

    # Deduplicate citations by (source_file, line_number)
    seen = set()
    unique_citations = []
    for c in concepts:
        key = (str(c.source_file), c.line_number)
        if key not in seen:
            seen.add(key)
            unique_citations.append(c)

    output = f"\n📚 {title}:\n"
    for c in unique_citations[:10]:  # Limit to 10 citations
        from pathlib import Path
        filename = Path(c.source_file).name
        output += f"  • {filename}:{c.line_number}\n"

    if len(unique_citations) > 10:
        output += f"  ... e mais {len(unique_citations) - 10} fontes\n"

    return output


def format_concept_with_citation(
    concept: Any,
    include_context: bool = False
) -> str:
    """Format a single concept with its citation.

    Args:
        concept: Concept object
        include_context: If True, include the concept's context

    Returns:
        Formatted concept string with citation

    Example:
        [norma] M-CHAT-R/F: sensibilidade 0.882 (Fonte: triagem_precoce_autismo.md:123)
    """
    from pathlib import Path

    filename = Path(concept.source_file).name
    citation = f"(Fonte: {filename}:{concept.line_number})"

    text = truncate_text(concept.text, 80)
    output = f"[{concept.type.value}] {text} {citation}"

    if include_context and concept.context:
        context_short = truncate_text(concept.context.strip(), 150)
        output += f"\n    Contexto: \"{context_short}\""

    return output


def inject_citations_into_output(
    output: str,
    concepts: List[Any],
    inject_inline: bool = False
) -> str:
    """Inject citation references into command output.

    Args:
        output: Original command output string
        concepts: List of Concept objects used in generating the output
        inject_inline: If True, add inline citations (experimental)

    Returns:
        Output string with citations block appended

    This is the main integration point for evidence traceability.
    """
    if not concepts:
        return output

    citations_block = format_citations_block(concepts, "Fontes utilizadas")
    return output + citations_block


# ---------------------------------------------------------------------------
# Export Formatter
# ---------------------------------------------------------------------------

def format_export_success(
    format_name: str,
    file_path: str,
    size_bytes: int
) -> str:
    """Format export success message.

    Args:
        format_name: Name of the export format (md, yaml, json, docx)
        file_path: Path to the exported file
        size_bytes: Size of the exported file in bytes

    Returns:
        Formatted success message
    """
    return (
        f"✅ Exportado com sucesso!\n"
        f"   Formato: {format_name.upper()}\n"
        f"   Arquivo: {file_path}\n"
        f"   Tamanho: {format_number(size_bytes)} bytes"
    )


def format_export_error(error_message: str) -> str:
    """Format export error message.

    Args:
        error_message: Error description

    Returns:
        Formatted error message
    """
    return f"❌ Erro ao exportar: {error_message}"


def format_export_help() -> str:
    """Format export command help text.

    Returns:
        Help text for /export command
    """
    return (
        "Uso: /export <formato> [caminho]\n\n"
        "Formatos disponíveis:\n"
        "  md    - Markdown\n"
        "  yaml  - YAML estruturado\n"
        "  json  - JSON estruturado\n"
        "  docx  - Documento Word\n\n"
        "Exemplos:\n"
        "  /export md\n"
        "  /export docx relatorio.docx\n"
        "  /export yaml ./outputs/dados.yaml"
    )
