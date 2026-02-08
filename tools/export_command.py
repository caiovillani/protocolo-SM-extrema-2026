#!/usr/bin/env python3
"""
Tool: Command Export
Descrição: Exporta saídas de comandos em múltiplos formatos

Uso:
    # Execute comando e exporte resultado
    python tools/export_command.py --command template --args CLI_02 --format docx

    # Exporte arquivo texto existente
    python tools/export_command.py --file output.txt --format yaml

Inputs:
    --command: Nome do comando a executar (template, auditoria, pips, etc.)
    --args: Argumentos para o comando (separados por espaço)
    --format: Formato de saída (md, yaml, json, docx)
    --output: Caminho de saída customizado (opcional)
    --file: Arquivo de texto para exportar (alternativa a --command)
    --stdout: Imprimir no stdout ao invés de salvar em arquivo

Outputs:
    - Arquivo exportado no formato especificado

Dependências:
    - pyyaml
    - python-docx (para formato DOCX)
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# Adicionar src ao path para imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.context_engine.main import handle_user_input
from src.context_engine.exporter import (
    CommandExporter,
    ExportFormat,
    ExportMetadata,
)


def generate_output_path(command_name: str, format_str: str) -> Path:
    """Generate automatic output path for export.

    Args:
        command_name: Name of the command being exported
        format_str: Export format string

    Returns:
        Path for the output file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{command_name}_{timestamp}.{format_str}"
    return Path("./exports") / filename


def main():
    parser = argparse.ArgumentParser(
        description="Exportar saídas de comandos do Context Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
    # Executar /template e exportar como DOCX
    python tools/export_command.py --command template --args CLI_02 --format docx

    # Executar /pips status e exportar como YAML
    python tools/export_command.py --command pips --args status meu_projeto --format yaml

    # Exportar arquivo texto como Markdown
    python tools/export_command.py --file resultado.txt --format md --output relatorio.md

    # Imprimir exportação no console
    python tools/export_command.py --command template --args CLI_02 --format json --stdout
        """,
    )

    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--command",
        help="Nome do comando a executar (template, auditoria, pips, contexto, etc.)",
    )
    input_group.add_argument(
        "--file",
        help="Arquivo de texto para exportar (alternativa a --command)",
    )

    # Command arguments
    parser.add_argument(
        "--args",
        nargs="*",
        default=[],
        help="Argumentos para o comando (se usar --command)",
    )

    # Export options
    parser.add_argument(
        "--format",
        choices=["md", "yaml", "json", "docx"],
        default="md",
        help="Formato de saída (padrão: md)",
    )
    parser.add_argument(
        "--output",
        help="Caminho de saída customizado",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Imprimir no stdout ao invés de salvar em arquivo",
    )
    parser.add_argument(
        "--no-metadata",
        action="store_true",
        help="Excluir metadados da exportação",
    )

    args = parser.parse_args()

    # Get content
    command_name = "file"
    if args.command:
        # Execute command
        command_name = args.command
        command_args = " ".join(args.args) if args.args else ""
        command_input = f"/{args.command} {command_args}".strip()

        print(f"Executando: {command_input}", file=sys.stderr)
        content = handle_user_input(command_input)

        # Check for errors
        if content.startswith("Comando '") and "não suportado" in content:
            print(f"Erro: {content}", file=sys.stderr)
            sys.exit(1)
        if content.startswith("Erro"):
            print(f"Erro: {content}", file=sys.stderr)
            sys.exit(1)

    else:
        # Read file
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Erro: Arquivo não encontrado: {args.file}", file=sys.stderr)
            sys.exit(1)

        try:
            content = file_path.read_text(encoding="utf-8")
            command_name = file_path.stem  # Use filename without extension
        except Exception as e:
            print(f"Erro ao ler arquivo: {e}", file=sys.stderr)
            sys.exit(1)

    # Parse format
    try:
        export_format = ExportFormat.from_string(args.format)
    except ValueError as e:
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(1)

    # Create metadata
    metadata = None
    if not args.no_metadata:
        metadata = ExportMetadata(
            command_name=command_name,
            timestamp=datetime.now().isoformat(),
        )

    # Export
    exporter = CommandExporter()

    # Handle stdout output
    if args.stdout:
        if export_format == ExportFormat.DOCX:
            print(
                "Erro: Formato DOCX não pode ser impresso no stdout.",
                file=sys.stderr,
            )
            sys.exit(1)

        try:
            exported = exporter.export_to_string(content, export_format, metadata)
            # Use UTF-8 encoding for stdout on Windows
            sys.stdout.reconfigure(encoding='utf-8')
            print(exported)
            sys.exit(0)
        except Exception as e:
            print(f"Erro ao exportar: {e}", file=sys.stderr)
            sys.exit(1)

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = generate_output_path(command_name, export_format.value)

    # Export to file
    result = exporter.export_to_file(content, export_format, output_path, metadata)

    if result.success:
        # Reconfigure stdout for UTF-8 on Windows
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
            pass  # Python < 3.7

        print("=" * 60)
        print(f"  Exportacao Concluida")
        print("=" * 60)
        print()
        print(f"[OK] Arquivo: {result.file_path}")
        print(f"     Formato: {result.format.value.upper()}")
        print(f"     Tamanho: {result.size_bytes:,} bytes")
        print(f"     Comando: /{command_name}")
    else:
        print(f"[ERRO] Erro ao exportar: {result.error_message}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
