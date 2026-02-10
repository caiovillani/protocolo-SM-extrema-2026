#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Renderizador de protocolo clinico Markdown para TXT plano.

Gera versao texto plano com:
- Headings com separadores visuais (====, ----)
- Tabelas preservadas em formato pipe alinhado
- Fluxogramas ASCII preservados integralmente
- Blockquotes com prefixo >
- Word wrap em 100 caracteres para paragrafos
- Encoding UTF-8 com BOM (compatibilidade Windows/Notepad)

Uso:
    py -3.13 tools/render_protocolo_txt.py -i protocolo.md -o protocolo.txt
"""

from __future__ import annotations

import argparse
import sys
import textwrap
from pathlib import Path

# Import do parser compartilhado
sys.path.insert(0, str(Path(__file__).parent))
from md_protocol_parser import (
    parse_protocol, count_blocks_by_type, spans_to_plain,
    Block, Heading, Paragraph, Table, CodeBlock, ListBlock, HorizontalRule,
    Span, SpanType
)


# ===========================================================================
# CONSTANTES
# ===========================================================================

LINE_WIDTH = 100
SEP_H1 = "="
SEP_H2 = "-"
SEP_HR = "-"


# ===========================================================================
# TXT BUILDER
# ===========================================================================

class TXTProtocolBuilder:
    """Constroi documento TXT plano a partir de blocos parseados."""

    def __init__(self, metadata: dict):
        self.meta = metadata
        self.lines: list[str] = []

    def _write(self, text: str = ""):
        """Adiciona linha ao buffer."""
        self.lines.append(text)

    def _write_separator(self, char: str, width: int = LINE_WIDTH):
        """Linha separadora."""
        self._write(char * width)

    def _write_centered(self, text: str, width: int = LINE_WIDTH):
        """Texto centralizado."""
        padding = max(0, (width - len(text)) // 2)
        self._write(" " * padding + text)

    # --- Cabecalho ---

    def add_header(self):
        """Cabecalho do documento."""
        self._write_separator(SEP_H1)
        title = self.meta.get("title",
                              "PROTOCOLO DE FLUXOS DE ATENCAO EM SAUDE MENTAL")
        self._write_centered(title.upper())
        self._write_centered(
            f"Municipio de Extrema - MG | {self.meta.get('year', '2026')}")
        self._write_separator(SEP_H1)
        self._write()
        self._write_centered(
            "Secretaria Municipal de Saude - Coordenacao de Saude Mental")
        self._write()
        self._write_separator(SEP_HR)
        self._write()

    # --- Renderizadores por tipo de bloco ---

    def render_blocks(self, blocks: list[Block]):
        """Renderiza lista de blocos sequencialmente."""
        for block in blocks:
            if isinstance(block, Heading):
                self._render_heading(block)
            elif isinstance(block, Paragraph):
                if block.style == "blockquote":
                    self._render_blockquote(block)
                else:
                    self._render_paragraph(block)
            elif isinstance(block, Table):
                self._render_table(block)
            elif isinstance(block, CodeBlock):
                self._render_code_block(block)
            elif isinstance(block, ListBlock):
                self._render_list(block)
            elif isinstance(block, HorizontalRule):
                self._write_separator(SEP_HR)
                self._write()

    def _render_heading(self, h: Heading):
        """Heading com separadores visuais."""
        text = self._spans_to_text(h.spans)

        self._write()
        if h.level == 1:
            self._write_separator(SEP_H1)
            self._write(text.upper())
            self._write_separator(SEP_H1)
        elif h.level == 2:
            self._write(text.upper())
            self._write_separator(SEP_H2)
        elif h.level == 3:
            self._write(f"### {text}")
        else:
            self._write(f"#### {text}")
        self._write()

    def _render_paragraph(self, para: Paragraph):
        """Paragrafo com word wrap."""
        text = self._spans_to_text(para.spans)
        wrapped = textwrap.fill(text, width=LINE_WIDTH)
        self._write(wrapped)
        self._write()

    def _render_blockquote(self, para: Paragraph):
        """Blockquote com prefixo >."""
        text = self._spans_to_text(para.spans)
        wrapped = textwrap.fill(text, width=LINE_WIDTH - 2)
        for line in wrapped.split('\n'):
            self._write(f"> {line}")
        self._write()

    def _render_table(self, tbl: Table):
        """Tabela em formato pipe alinhado."""
        # Coletar todo o conteudo como texto
        all_rows: list[list[str]] = []

        if tbl.has_header and tbl.headers:
            header_texts = [self._spans_to_text(spans) for spans in tbl.headers]
            all_rows.append(header_texts)

        for row in tbl.rows:
            row_texts = [self._spans_to_text(spans) for spans in row]
            all_rows.append(row_texts)

        if not all_rows:
            return

        # Calcular largura de colunas
        num_cols = max(len(row) for row in all_rows)
        col_widths = [0] * num_cols
        for row in all_rows:
            for j, cell in enumerate(row):
                if j < num_cols:
                    col_widths[j] = max(col_widths[j], len(cell))

        # Renderizar
        for i, row in enumerate(all_rows):
            cells = []
            for j in range(num_cols):
                text = row[j] if j < len(row) else ""
                cells.append(text.ljust(col_widths[j]))
            self._write("| " + " | ".join(cells) + " |")

            # Separador apos header
            if i == 0 and tbl.has_header and tbl.headers:
                sep_cells = [SEP_HR * col_widths[j] for j in range(num_cols)]
                self._write("| " + " | ".join(sep_cells) + " |")

        self._write()

    def _render_code_block(self, cb: CodeBlock):
        """Bloco ASCII preservado exatamente."""
        for line in cb.lines:
            self._write(line)
        self._write()

    def _render_list(self, lb: ListBlock):
        """Lista com prefixos."""
        for idx, item_spans in enumerate(lb.items, start=lb.start):
            text = self._spans_to_text(item_spans)
            if lb.ordered:
                prefix = f"{idx}. "
            else:
                prefix = "- "

            # Primeira linha com prefixo, seguintes indentadas
            wrapped = textwrap.fill(text, width=LINE_WIDTH - len(prefix),
                                    initial_indent=prefix,
                                    subsequent_indent=" " * len(prefix))
            self._write(wrapped)
        self._write()

    # --- Helpers ---

    def _spans_to_text(self, spans: list[Span]) -> str:
        """Converte Spans para texto plano. Bold vira MAIUSCULO."""
        parts = []
        for s in spans:
            if s.type == SpanType.BOLD:
                parts.append(s.text.upper())
            elif s.type == SpanType.LINK:
                parts.append(s.text)
            else:
                parts.append(s.text)
        return "".join(parts)

    # --- Salvar ---

    def save(self, output_path: str):
        """Salva documento TXT com UTF-8 BOM."""
        content = '\n'.join(self.lines)
        with open(output_path, 'w', encoding='utf-8-sig') as f:
            f.write(content)


# ===========================================================================
# CLI
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Renderiza protocolo clinico Markdown para TXT plano."
    )
    parser.add_argument("-i", "--input", required=True, type=Path,
                        help="Arquivo Markdown de entrada")
    parser.add_argument("-o", "--output", required=True, type=Path,
                        help="Arquivo TXT de saida")
    parser.add_argument("--title",
                        default="PROTOCOLO DE FLUXOS DE ATENCAO EM SAUDE MENTAL",
                        help="Titulo do documento")
    parser.add_argument("--year", default="2026",
                        help="Ano de elaboracao")

    args = parser.parse_args()

    # Validacao
    if not args.input.exists():
        print(f"[ERRO] Arquivo nao encontrado: {args.input}", file=sys.stderr)
        sys.exit(1)

    # Ler e parsear
    print(f"[.] Lendo {args.input.name}...")
    md_content = args.input.read_text(encoding='utf-8')

    print(f"[.] Parseando Markdown...")
    blocks = parse_protocol(md_content)
    counts = count_blocks_by_type(blocks)
    print(f"    {len(blocks)} blocos: {', '.join(f'{k}={v}' for k, v in sorted(counts.items()))}")

    # Construir TXT
    print(f"[.] Construindo TXT...")
    metadata = {
        "title": args.title,
        "year": args.year,
    }

    builder = TXTProtocolBuilder(metadata)
    builder.add_header()
    builder.render_blocks(blocks)

    # Salvar
    builder.save(str(args.output))

    size_kb = args.output.stat().st_size / 1024
    print(f"[OK] Documento gerado: {args.output}")
    print(f"     Tamanho: {size_kb:.1f} KB")
    print(f"     Codificacao: UTF-8 com BOM (compativel Windows/Notepad)")


if __name__ == "__main__":
    main()
