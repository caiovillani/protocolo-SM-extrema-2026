"""
PDF Processing Utilities - Shared functions for Phase 1 preprocessing

Funções compartilhadas para detecção OCR, extração de tabelas, formatação markdown
e validação técnica de PDFs processados.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import pdfplumber
except ImportError:
    pdfplumber = None


@dataclass
class MarkdownTable:
    """Tabela extraída convertida para markdown."""
    page: int
    idx: int
    markdown: str
    rows: int = 0
    cols: int = 0


@dataclass
class ValidationResult:
    """Resultado de validação técnica."""
    success: bool
    issues: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ProcessingResult:
    """Resultado de processamento de 1 PDF."""
    pdf_path: Path
    output_path: Optional[Path]
    markdown: str
    metadata: Dict[str, Any]
    validation: Optional[ValidationResult]
    status: str  # "success" or "failed"


def detect_ocr_needed(pdf_path: Path) -> Tuple[bool, float]:
    """Detecta se PDF precisa OCR via text extraction ratio.

    Args:
        pdf_path: Caminho do PDF

    Returns:
        Tuple de (needs_ocr, text_ratio) onde text_ratio ∈ [0, 1]
        - text_ratio < 0.25: Scanned PDF (needs OCR)
        - text_ratio >= 0.25: Text-based PDF

    Raises:
        Exception se pdfplumber não disponível
    """
    if pdfplumber is None:
        raise Exception("pdfplumber not installed")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Sample first 5 pages (or all if fewer)
            sample_pages = min(5, len(pdf.pages))

            total_chars = 0
            for i in range(sample_pages):
                page = pdf.pages[i]
                text = page.extract_text() or ""
                total_chars += len(text)

            # Calculate average chars per page
            avg_chars_per_page = total_chars / sample_pages if sample_pages > 0 else 0

            # Normalize: 2000 chars/page is reasonable for text-based PDF
            text_ratio = min(1.0, avg_chars_per_page / 2000)

            # Threshold: <500 chars/page (~25% de 2000) = scanned
            needs_ocr = text_ratio < 0.25

            return needs_ocr, text_ratio

    except Exception as e:
        # If detection fails, assume text-based (safer default)
        print(f"Warning: OCR detection failed for {pdf_path}: {e}")
        return False, 0.5


def extract_tables_pdfplumber(pdf_path: Path) -> List[MarkdownTable]:
    """Extrai tabelas usando pdfplumber e converte para markdown.

    Args:
        pdf_path: Caminho do PDF

    Returns:
        Lista de MarkdownTable com tabelas convertidas
    """
    if pdfplumber is None:
        return []

    tables = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_tables = page.extract_tables()

                if not page_tables:
                    continue

                for table_idx, table_data in enumerate(page_tables, 1):
                    if not table_data or len(table_data) == 0:
                        continue

                    # Convert to markdown
                    md_table = convert_to_markdown_table(table_data)

                    tables.append(MarkdownTable(
                        page=page_num,
                        idx=table_idx,
                        markdown=md_table,
                        rows=len(table_data),
                        cols=len(table_data[0]) if table_data else 0
                    ))

    except Exception as e:
        print(f"Warning: Table extraction failed for {pdf_path}: {e}")
        return []

    return tables


def convert_to_markdown_table(table_data: List[List[Any]]) -> str:
    """Converte matriz de dados para tabela markdown.

    Args:
        table_data: Lista de listas (linhas × colunas)

    Returns:
        String com tabela em formato markdown
    """
    if not table_data or len(table_data) == 0:
        return ""

    # Limpar células None e normalizar
    cleaned_data = []
    for row in table_data:
        cleaned_row = [str(cell or "").strip() for cell in row]
        cleaned_data.append(cleaned_row)

    # Primeira linha como header
    if len(cleaned_data) == 0:
        return ""

    header = cleaned_data[0]
    body = cleaned_data[1:] if len(cleaned_data) > 1 else []

    # Calcular largura de colunas
    col_widths = [len(h) for h in header]
    for row in body:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(cell))

    # Gerar linhas markdown
    lines = []

    # Header
    header_line = "| " + " | ".join(h.ljust(w) for h, w in zip(header, col_widths)) + " |"
    lines.append(header_line)

    # Separator
    separator = "|" + "|".join("-" * (w + 2) for w in col_widths) + "|"
    lines.append(separator)

    # Body
    for row in body:
        # Pad row if needed
        padded_row = row + [""] * (len(header) - len(row))
        row_line = "| " + " | ".join(cell.ljust(w) for cell, w in zip(padded_row, col_widths)) + " |"
        lines.append(row_line)

    return "\n".join(lines)


def format_preliminary_markdown(
    pages_text: List[str],
    tables: List[MarkdownTable],
    metadata: Dict[str, Any]
) -> str:
    """Gera markdown preliminar com metadados básicos e page anchors.

    Args:
        pages_text: Lista de textos por página
        tables: Lista de tabelas extraídas
        metadata: Dicionário de metadados

    Returns:
        String com markdown completo
    """
    lines = [
        "---",
        "# PRELIMINARY EXTRACTION - Phase 1",
        f"source_file: {metadata.get('source_file', 'unknown')}",
        f"taxonomy: {metadata.get('taxonomy', 'unknown')}",
        f"pages_total: {metadata.get('pages_total', 0)}",
        f"ocr_applied: {metadata.get('ocr_applied', False)}",
        f"text_extraction_quality: {metadata.get('text_extraction_quality', 0):.2f}",
        f"tables_detected: {metadata.get('tables_detected', 0)}",
        f"file_hash: {metadata.get('file_hash', 'unknown')}",
        f"processed_at: {metadata.get('processed_at', '')}",
        "---",
        "",
        "# Conteúdo Extraído",
        ""
    ]

    # Text with page anchors
    for page_num, page_text in enumerate(pages_text, 1):
        lines.append(f"<!-- page {page_num} -->")
        lines.append("")
        if page_text.strip():
            lines.append(page_text)
        else:
            lines.append("*(página vazia ou sem texto extraível)*")
        lines.append("")

    # Tables section
    if tables:
        lines.append("---")
        lines.append("")
        lines.append("## Tabelas Extraídas")
        lines.append("")

        for table in tables:
            lines.append(f"### Página {table.page}, Tabela {table.idx}")
            lines.append("")
            lines.append(table.markdown)
            lines.append("")

    return "\n".join(lines)


def validate_preliminary_extraction(
    pdf_path: Path,
    markdown: str,
    metadata: Dict[str, Any]
) -> ValidationResult:
    """Validação técnica da extração Phase 1.

    Args:
        pdf_path: Caminho do PDF original
        markdown: Markdown gerado
        metadata: Metadados do processamento

    Returns:
        ValidationResult com issues e warnings
    """
    issues = []
    warnings = []

    # Check 1: OCR quality
    if metadata.get('ocr_applied', False):
        text_quality = metadata.get('text_extraction_quality', 0)
        if text_quality < 0.5:
            issues.append({
                "type": "low_ocr_quality",
                "severity": "high",
                "message": f"OCR quality {text_quality:.2f} abaixo do limite 0.5"
            })

    # Check 2: Page anchor completeness
    page_anchors = markdown.count("<!-- page")
    pages_total = metadata.get('pages_total', 0)

    if pages_total > 0 and page_anchors < pages_total * 0.9:
        warnings.append({
            "type": "missing_pages",
            "severity": "medium",
            "message": f"{page_anchors} âncoras vs {pages_total} páginas esperadas"
        })

    # Check 3: Table count sanity
    tables_detected = metadata.get('tables_detected', 0)
    tables_in_md = markdown.count("### Página")  # Table headers

    if abs(tables_in_md - tables_detected) > 2:
        warnings.append({
            "type": "table_mismatch",
            "severity": "low",
            "message": f"{tables_in_md} tabelas em MD vs {tables_detected} detectadas"
        })

    # Check 4: File size vs content size ratio
    try:
        file_size_mb = pdf_path.stat().st_size / (1024 * 1024)
        content_kb = len(markdown.encode('utf-8')) / 1024
        ratio = content_kb / (file_size_mb * 1024) if file_size_mb > 0 else 0

        if ratio < 0.05:  # Menos de 5% do esperado
            warnings.append({
                "type": "low_extraction_ratio",
                "severity": "medium",
                "message": f"Razão extração/tamanho: {ratio:.2%} (esperado >5%)"
            })
    except Exception:
        pass

    # Check 5: Completely empty extraction
    content_lines = [line for line in markdown.split('\n') if line.strip() and not line.startswith('#') and not line.startswith('---')]
    if len(content_lines) < 10:
        issues.append({
            "type": "empty_extraction",
            "severity": "high",
            "message": f"Extração quase vazia: apenas {len(content_lines)} linhas de conteúdo"
        })

    return ValidationResult(
        success=len(issues) == 0,
        issues=issues,
        warnings=warnings
    )


def extract_taxonomy_from_path(pdf_path: Path) -> str:
    """Extrai taxonomia do caminho do arquivo.

    Args:
        pdf_path: Caminho do PDF

    Returns:
        String com taxonomia (e.g., "normativos", "clinicos/manuais")
    """
    parts = pdf_path.parts

    # Find "referencias" in path
    if "referencias" in parts:
        idx = parts.index("referencias")
        # Get everything after referencias/ and before filename
        taxonomy_parts = parts[idx+1:-1]

        if len(taxonomy_parts) == 0:
            return "unknown"
        elif len(taxonomy_parts) == 1:
            return taxonomy_parts[0]
        else:
            # Join with / for nested taxonomies (e.g., clinicos/manuais)
            return "/".join(taxonomy_parts)

    # Fallback: parent directory name
    return pdf_path.parent.name if pdf_path.parent.name else "unknown"


def infer_doc_type(filename: str) -> str:
    """Infere tipo de documento pelo nome do arquivo.

    Args:
        filename: Nome do arquivo PDF

    Returns:
        String com tipo inferido
    """
    filename_lower = filename.lower()

    # Patterns for common document types
    if any(kw in filename_lower for kw in ["portaria", "resolucao", "lei", "decreto"]):
        return "normativo"
    elif any(kw in filename_lower for kw in ["manual", "guia", "orientacao", "instrucao"]):
        return "manual"
    elif any(kw in filename_lower for kw in ["workshop", "oficina", "capacitacao"]):
        return "material_formacao"
    elif any(kw in filename_lower for kw in ["caso", "estudo_caso"]):
        return "caso_clinico"
    elif any(kw in filename_lower for kw in ["escala", "instrumento", "questionario", "ficha"]):
        return "instrumento"
    elif any(kw in filename_lower for kw in ["apresentacao", "slides"]):
        return "apresentacao"
    elif any(kw in filename_lower for kw in ["artigo", "paper"]):
        return "artigo"
    elif any(kw in filename_lower for kw in ["tutorial", "tutoria", "tutor"]):
        return "guia_tutoria"
    elif any(kw in filename_lower for kw in ["gerenciamento", "gestao"]):
        return "guia_gerenciamento"
    elif any(kw in filename_lower for kw in ["desenvolvimento", "desenv"]):
        return "guia_desenvolvimento"
    else:
        return "documento_geral"
