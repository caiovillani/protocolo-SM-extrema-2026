#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script CLI para renderização de protocolos Markdown para HTML.

Uso:
    python tools/render_html.py <arquivo.md>
    python tools/render_html.py <arquivo.md> -o <saida.html>
    python tools/render_html.py --all
    python tools/render_html.py --test

Exemplos:
    # Renderizar um protocolo específico
    python tools/render_html.py entregas/Protocolos_Compartilhamento_Cuidado/02_PROTOCOLO_DEMANDA_ESPONTANEA_APS_NIRSM_AES.md

    # Renderizar todos os protocolos
    python tools/render_html.py --all

    # Testar a renderização sem salvar
    python tools/render_html.py --test
"""

import sys
import os
import argparse
from pathlib import Path

# Configura encoding UTF-8 para Windows
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Adiciona o diretório src ao path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from html_renderer import ProtocolRenderer
from html_renderer.renderer import RenderConfig


# Diretórios padrão
PROTOCOLS_DIR = PROJECT_ROOT / "entregas" / "Protocolos_Compartilhamento_Cuidado"
FINALIZED_DIR = PROJECT_ROOT / "entregas" / "protocolos_finalizados"
OUTPUT_DIR = PROJECT_ROOT / "exports" / "html"


def render_single(
    source: Path,
    output: Path = None,
    config: RenderConfig = None
) -> Path:
    """
    Renderiza um único arquivo Markdown.

    Args:
        source: Caminho do arquivo .md.
        output: Caminho do arquivo .html (opcional).
        config: Configurações de renderização.

    Returns:
        Caminho do arquivo HTML gerado.
    """
    if not source.exists():
        print(f"[ERRO] Arquivo nao encontrado: {source}")
        sys.exit(1)

    renderer = ProtocolRenderer(config=config)

    # Define output path se não especificado
    if output is None:
        output = OUTPUT_DIR / source.with_suffix('.html').name

    result = renderer.render(source, output)
    print(f"[OK] Gerado: {result}")

    return result


def render_all(config: RenderConfig = None) -> list[Path]:
    """
    Renderiza todos os protocolos encontrados.

    Args:
        config: Configurações de renderização.

    Returns:
        Lista de caminhos dos arquivos gerados.
    """
    results = []

    # Protocolos no diretório principal
    if PROTOCOLS_DIR.exists():
        for md_file in PROTOCOLS_DIR.glob("*.md"):
            # Ignora arquivos de template e índice
            if md_file.name.startswith("_") or "INDICE" in md_file.name:
                continue
            try:
                result = render_single(md_file, config=config)
                results.append(result)
            except Exception as e:
                print(f"[AVISO] Erro ao processar {md_file.name}: {e}")

    # Protocolos clínicos
    clinicos_dir = PROTOCOLS_DIR / "Protocolos_Clinicos"
    if clinicos_dir.exists():
        for md_file in clinicos_dir.glob("*.md"):
            if md_file.name.startswith("_"):
                continue
            try:
                result = render_single(md_file, config=config)
                results.append(result)
            except Exception as e:
                print(f"[AVISO] Erro ao processar {md_file.name}: {e}")

    # Protocolos finalizados
    if FINALIZED_DIR.exists():
        for md_file in FINALIZED_DIR.glob("*.md"):
            try:
                result = render_single(md_file, config=config)
                results.append(result)
            except Exception as e:
                print(f"[AVISO] Erro ao processar {md_file.name}: {e}")

    print(f"\n[INFO] Total: {len(results)} arquivos renderizados")
    return results


def test_rendering() -> bool:
    """
    Testa a renderização sem salvar arquivos.

    Returns:
        True se todos os testes passaram.
    """
    print("[TEST] Testando componentes do renderer...")

    # Testa imports
    try:
        from html_renderer.parsers.mermaid_handler import MermaidHandler
        from html_renderer.parsers.ascii_art_handler import AsciiArtHandler
        from html_renderer.parsers.table_enhancer import TableEnhancer
        print("  [v] Imports OK")
    except ImportError as e:
        print(f"  [x] Erro de import: {e}")
        return False

    # Testa MermaidHandler
    try:
        handler = MermaidHandler()
        test_content = '''
```mermaid
flowchart TD
    A[Início] --> B[Fim]
```
'''
        result = handler.process(test_content)
        assert 'class="mermaid"' in result
        print("  [v] MermaidHandler OK")
    except Exception as e:
        print(f"  [x] MermaidHandler erro: {e}")
        return False

    # Testa TableEnhancer
    try:
        enhancer = TableEnhancer()
        test_html = '''
<table>
<thead><tr><th>COR</th><th>Descrição</th></tr></thead>
<tbody><tr><td>**VERMELHO**</td><td>Urgência</td></tr></tbody>
</table>
'''
        result = enhancer.enhance(test_html)
        assert 'data-risco="vermelho"' in result
        print("  [v] TableEnhancer OK")
    except Exception as e:
        print(f"  [x] TableEnhancer erro: {e}")
        return False

    # Testa AsciiArtHandler
    try:
        handler = AsciiArtHandler()
        test_content = '''
```
┌─────────────────────┐
│   FORMULÁRIO        │
├─────────────────────┤
│ [ ] Campo 1         │
│ [ ] Campo 2         │
└─────────────────────┘
```
'''
        result = handler.mark_ascii_blocks(test_content)
        assert 'ASCII_BLOCK_START' in result
        print("  [v] AsciiArtHandler OK")
    except Exception as e:
        print(f"  [x] AsciiArtHandler erro: {e}")
        return False

    # Verifica dependências
    print("\n[DEPS] Verificando dependências...")

    try:
        import markdown
        print(f"  [v] markdown {markdown.__version__}")
    except ImportError:
        print("  [x] markdown não instalado (pip install markdown)")
        return False

    try:
        import jinja2
        print(f"  [v] jinja2 {jinja2.__version__}")
    except ImportError:
        print("  [x] jinja2 não instalado (pip install jinja2)")
        return False

    try:
        import yaml
        print(f"  [v] pyyaml instalado")
    except ImportError:
        print("  ⚠ pyyaml não instalado (opcional, pip install pyyaml)")

    print("\n[OK] Todos os testes passaram!")
    return True


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Renderiza protocolos Markdown para HTML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python tools/render_html.py arquivo.md           # Renderiza um arquivo
  python tools/render_html.py arquivo.md -o out.html  # Especifica saída
  python tools/render_html.py --all                # Renderiza todos
  python tools/render_html.py --test               # Executa testes
        """
    )

    parser.add_argument(
        "source",
        type=Path,
        nargs="?",
        help="Arquivo Markdown de origem"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Arquivo HTML de saída"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Renderizar todos os protocolos"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Executar testes de renderização"
    )
    parser.add_argument(
        "--no-toc",
        action="store_true",
        help="Não incluir sumário (TOC)"
    )
    parser.add_argument(
        "--no-mermaid",
        action="store_true",
        help="Não processar diagramas Mermaid"
    )
    parser.add_argument(
        "--no-assets",
        action="store_true",
        help="Não copiar arquivos de assets"
    )

    args = parser.parse_args()

    # Cria diretório de saída
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Configurações
    config = RenderConfig(
        include_toc=not args.no_toc,
        include_mermaid=not args.no_mermaid,
        copy_assets=not args.no_assets
    )

    # Executa ação
    if args.test:
        success = test_rendering()
        sys.exit(0 if success else 1)

    elif args.all:
        render_all(config=config)

    elif args.source:
        render_single(args.source, args.output, config=config)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
