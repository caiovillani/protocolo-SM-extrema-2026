#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parser Markdown compartilhado para protocolos clínicos.

Converte Markdown em lista de blocos tipados (dataclasses) consumíveis
por builders de diferentes formatos (DOCX, TXT, HTML).

Uso:
    from md_protocol_parser import parse_protocol, Heading, Table, CodeBlock, ...

    blocks = parse_protocol(md_content)
    for block in blocks:
        match block:
            case Heading(level=2):  ...
            case Table():           ...
            case CodeBlock():       ...
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Union


# ---------------------------------------------------------------------------
# Dataclasses — Representação intermediária
# ---------------------------------------------------------------------------

class SpanType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    EMOJI = "emoji"
    LINK = "link"


@dataclass
class Span:
    """Fragmento de texto inline com formatação."""
    type: SpanType
    text: str
    url: str | None = None  # Apenas para LINK


@dataclass
class Heading:
    level: int           # 1-4
    spans: list[Span]    # Conteúdo com formatação inline
    raw_text: str = ""   # Texto sem marcação (para TOC, etc.)


@dataclass
class Paragraph:
    spans: list[Span]
    style: str = "normal"  # "normal" | "blockquote"


@dataclass
class Table:
    headers: list[list[Span]]   # Cada header é lista de Spans
    rows: list[list[list[Span]]]  # rows[i][j] = lista de Spans
    has_header: bool = True


@dataclass
class CodeBlock:
    lines: list[str]  # Preserva exatamente como no source
    language: str = ""  # hint de linguagem (se houver)


@dataclass
class ListBlock:
    items: list[list[Span]]  # Cada item é lista de Spans
    ordered: bool = False
    start: int = 1


@dataclass
class HorizontalRule:
    pass


# Tipo-união para blocos
Block = Union[Heading, Paragraph, Table, CodeBlock, ListBlock, HorizontalRule]


# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

RE_HEADING = re.compile(r'^(#{1,4})\s+(.+)$')
RE_TABLE_ROW = re.compile(r'^\|(.+)\|$')
RE_TABLE_SEP = re.compile(r'^\|[\s:|-]+\|$')
RE_CODE_FENCE = re.compile(r'^```(.*)$')
RE_BLOCKQUOTE = re.compile(r'^>\s?(.*)$')
RE_HR = re.compile(r'^(-{3,}|\*{3,}|_{3,})\s*$')
RE_OL_ITEM = re.compile(r'^(\d+)\.\s+(.+)$')
RE_UL_ITEM = re.compile(r'^[-*+]\s+(.+)$')
RE_HTML_COMMENT = re.compile(r'<!--.*?-->', re.DOTALL)

# Inline patterns
RE_BOLD = re.compile(r'\*\*(.+?)\*\*')
RE_ITALIC = re.compile(r'(?<!\*)\*([^*]+?)\*(?!\*)')
RE_LINK = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
EMOJI_PATTERN = re.compile(r'[\U0001F534\U0001F7E0\U0001F7E1\U0001F7E2\U0001F535\u26AA\u26AB'
                           r'\U0001F7E3\U0001F7E4\u2B55\u2705\u274C\u25B6\u23F8'
                           r'\U0001F50D\U0001F4C4\U0001F4C1\U0001F4CA\U0001F4A1\U0001F517]')


# ---------------------------------------------------------------------------
# Inline parser
# ---------------------------------------------------------------------------

def parse_inline(text: str) -> list[Span]:
    """Parseia formatação inline em lista de Spans."""
    if not text or not text.strip():
        return [Span(SpanType.TEXT, text)]

    spans: list[Span] = []
    # Coletar todos os matches com posição
    matches: list[tuple[int, int, Span]] = []

    for m in RE_BOLD.finditer(text):
        matches.append((m.start(), m.end(), Span(SpanType.BOLD, m.group(1))))

    for m in RE_ITALIC.finditer(text):
        # Evitar conflito com bold (** contém *)
        overlap = False
        for existing in matches:
            if m.start() >= existing[0] and m.end() <= existing[1]:
                overlap = True
                break
        if not overlap:
            matches.append((m.start(), m.end(), Span(SpanType.ITALIC, m.group(1))))

    for m in RE_LINK.finditer(text):
        overlap = False
        for existing in matches:
            if m.start() >= existing[0] and m.end() <= existing[1]:
                overlap = True
                break
        if not overlap:
            matches.append((m.start(), m.end(),
                            Span(SpanType.LINK, m.group(1), url=m.group(2))))

    for m in EMOJI_PATTERN.finditer(text):
        overlap = False
        for existing in matches:
            if m.start() >= existing[0] and m.end() <= existing[1]:
                overlap = True
                break
        if not overlap:
            matches.append((m.start(), m.end(), Span(SpanType.EMOJI, m.group(0))))

    if not matches:
        return [Span(SpanType.TEXT, text)]

    # Ordenar por posição
    matches.sort(key=lambda x: x[0])

    pos = 0
    for start, end, span in matches:
        if start > pos:
            plain = text[pos:start]
            if plain:
                spans.append(Span(SpanType.TEXT, plain))
        spans.append(span)
        pos = end

    if pos < len(text):
        remaining = text[pos:]
        if remaining:
            spans.append(Span(SpanType.TEXT, remaining))

    return spans if spans else [Span(SpanType.TEXT, text)]


def spans_to_plain(spans: list[Span]) -> str:
    """Converte lista de Spans para texto plano."""
    return "".join(s.text for s in spans)


# ---------------------------------------------------------------------------
# Parser principal — State machine
# ---------------------------------------------------------------------------

class _ParserState(Enum):
    NORMAL = "normal"
    IN_TABLE = "in_table"
    IN_CODE_BLOCK = "in_code_block"
    IN_BLOCKQUOTE = "in_blockquote"


def parse_protocol(md_content: str) -> list[Block]:
    """
    Parseia conteúdo Markdown de protocolo clínico em lista de blocos tipados.

    Args:
        md_content: String com o conteúdo Markdown completo.

    Returns:
        Lista de Block (Heading, Paragraph, Table, CodeBlock, ListBlock, HorizontalRule).
    """
    # Remover comentários HTML
    md_content = RE_HTML_COMMENT.sub('', md_content)

    lines = md_content.split('\n')
    blocks: list[Block] = []
    state = _ParserState.NORMAL

    # Buffers para blocos multiline
    table_lines: list[str] = []
    code_lines: list[str] = []
    code_lang: str = ""
    blockquote_lines: list[str] = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # === STATE: IN_CODE_BLOCK ===
        if state == _ParserState.IN_CODE_BLOCK:
            if RE_CODE_FENCE.match(line.strip()):
                # Fecha code block
                blocks.append(CodeBlock(lines=code_lines, language=code_lang))
                code_lines = []
                code_lang = ""
                state = _ParserState.NORMAL
            else:
                code_lines.append(line)
            i += 1
            continue

        # === STATE: IN_TABLE ===
        if state == _ParserState.IN_TABLE:
            if RE_TABLE_ROW.match(line.strip()):
                table_lines.append(line)
                i += 1
                continue
            else:
                # Finaliza tabela
                blocks.append(_build_table(table_lines))
                table_lines = []
                state = _ParserState.NORMAL
                # Não incrementa i — processa a linha atual no NORMAL

        # === STATE: IN_BLOCKQUOTE ===
        if state == _ParserState.IN_BLOCKQUOTE:
            bq_match = RE_BLOCKQUOTE.match(line)
            if bq_match:
                blockquote_lines.append(bq_match.group(1))
                i += 1
                continue
            else:
                # Finaliza blockquote
                bq_text = ' '.join(blockquote_lines)
                blocks.append(Paragraph(
                    spans=parse_inline(bq_text.strip()),
                    style="blockquote"
                ))
                blockquote_lines = []
                state = _ParserState.NORMAL
                # Não incrementa i

        # === STATE: NORMAL ===
        stripped = line.strip()

        # Linha vazia
        if not stripped:
            i += 1
            continue

        # Code fence (```)
        fence_match = RE_CODE_FENCE.match(stripped)
        if fence_match:
            state = _ParserState.IN_CODE_BLOCK
            code_lang = fence_match.group(1).strip()
            code_lines = []
            i += 1
            continue

        # Heading (#)
        heading_match = RE_HEADING.match(stripped)
        if heading_match:
            level = len(heading_match.group(1))
            text = heading_match.group(2).strip()
            blocks.append(Heading(
                level=level,
                spans=parse_inline(text),
                raw_text=_strip_inline_markers(text)
            ))
            i += 1
            continue

        # Horizontal rule (---, ***, ___)
        if RE_HR.match(stripped):
            blocks.append(HorizontalRule())
            i += 1
            continue

        # Blockquote (>)
        bq_match = RE_BLOCKQUOTE.match(line)
        if bq_match:
            state = _ParserState.IN_BLOCKQUOTE
            blockquote_lines = [bq_match.group(1)]
            i += 1
            continue

        # Table row (|...|)
        if RE_TABLE_ROW.match(stripped):
            state = _ParserState.IN_TABLE
            table_lines = [line]
            i += 1
            continue

        # Ordered list (1. ...)
        ol_match = RE_OL_ITEM.match(stripped)
        if ol_match:
            items: list[list[Span]] = []
            start_num = int(ol_match.group(1))
            while i < len(lines):
                ol_m = RE_OL_ITEM.match(lines[i].strip())
                if ol_m:
                    items.append(parse_inline(ol_m.group(2)))
                    i += 1
                else:
                    break
            blocks.append(ListBlock(items=items, ordered=True, start=start_num))
            continue

        # Unordered list (- ...)
        ul_match = RE_UL_ITEM.match(stripped)
        if ul_match:
            items = []
            while i < len(lines):
                ul_m = RE_UL_ITEM.match(lines[i].strip())
                if ul_m:
                    items.append(parse_inline(ul_m.group(1)))
                    i += 1
                else:
                    break
            blocks.append(ListBlock(items=items, ordered=False))
            continue

        # Paragraph (default)
        # Acumula linhas contíguas não-vazias que não são outros blocos
        para_lines = [stripped]
        i += 1
        while i < len(lines):
            next_line = lines[i].strip()
            if not next_line:
                break
            if (RE_HEADING.match(next_line) or RE_HR.match(next_line) or
                    RE_CODE_FENCE.match(next_line) or RE_TABLE_ROW.match(next_line) or
                    RE_BLOCKQUOTE.match(next_line) or RE_OL_ITEM.match(next_line) or
                    RE_UL_ITEM.match(next_line)):
                break
            para_lines.append(next_line)
            i += 1

        para_text = ' '.join(para_lines)
        blocks.append(Paragraph(spans=parse_inline(para_text)))
        continue

    # Finalizar buffers pendentes
    if state == _ParserState.IN_CODE_BLOCK and code_lines:
        blocks.append(CodeBlock(lines=code_lines, language=code_lang))
    if state == _ParserState.IN_TABLE and table_lines:
        blocks.append(_build_table(table_lines))
    if state == _ParserState.IN_BLOCKQUOTE and blockquote_lines:
        bq_text = ' '.join(blockquote_lines)
        blocks.append(Paragraph(
            spans=parse_inline(bq_text.strip()),
            style="blockquote"
        ))

    return blocks


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_table(raw_lines: list[str]) -> Table:
    """Constrói Table a partir de linhas pipe-delimitadas."""
    rows_raw: list[list[str]] = []
    separator_idx: int | None = None

    for idx, line in enumerate(raw_lines):
        stripped = line.strip()
        if RE_TABLE_SEP.match(stripped):
            separator_idx = idx
            continue
        # Split por | removendo primeiro/último vazios
        cells = [c.strip() for c in stripped.split('|')]
        # Remove strings vazias do split de |...|
        if cells and cells[0] == '':
            cells = cells[1:]
        if cells and cells[-1] == '':
            cells = cells[:-1]
        rows_raw.append(cells)

    has_header = separator_idx is not None and separator_idx <= 1

    if has_header and len(rows_raw) >= 1:
        headers = [parse_inline(cell) for cell in rows_raw[0]]
        data_rows = [[parse_inline(cell) for cell in row] for row in rows_raw[1:]]
        return Table(headers=headers, rows=data_rows, has_header=True)
    else:
        # Sem header — todas as linhas são rows
        headers = []
        data_rows = [[parse_inline(cell) for cell in row] for row in rows_raw]
        return Table(headers=headers, rows=data_rows, has_header=False)


def _strip_inline_markers(text: str) -> str:
    """Remove marcadores inline (**bold**, *italic*, [link](url)) para texto plano."""
    text = RE_BOLD.sub(r'\1', text)
    text = RE_ITALIC.sub(r'\1', text)
    text = RE_LINK.sub(r'\1', text)
    return text.strip()


# ---------------------------------------------------------------------------
# Utilitários para builders
# ---------------------------------------------------------------------------

def count_blocks_by_type(blocks: list[Block]) -> dict[str, int]:
    """Conta blocos por tipo (para diagnóstico)."""
    counts: dict[str, int] = {}
    for b in blocks:
        name = type(b).__name__
        counts[name] = counts.get(name, 0) + 1
    return counts


if __name__ == "__main__":
    import sys
    from pathlib import Path

    if len(sys.argv) < 2:
        print("Uso: python md_protocol_parser.py <arquivo.md>")
        print("Modo diagnóstico: parseia e exibe estatísticas dos blocos.")
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"[ERRO] Arquivo nao encontrado: {path}", file=sys.stderr)
        sys.exit(1)

    content = path.read_text(encoding='utf-8')
    blocks = parse_protocol(content)

    counts = count_blocks_by_type(blocks)
    total = len(blocks)

    print(f"[OK] Parseados {total} blocos de {path.name}")
    print()
    for btype, count in sorted(counts.items(), key=lambda x: -x[1]):
        pct = count / total * 100
        print(f"  {btype:20s}  {count:4d}  ({pct:5.1f}%)")
