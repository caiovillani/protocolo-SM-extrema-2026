"""
Renderer Principal - Pipeline de conversão Markdown → HTML

Este módulo implementa o pipeline de renderização:
1. Parse Markdown
2. Extrai frontmatter (metadados YAML)
3. Processa blocos Mermaid
4. Converte ASCII Art para HTML
5. Aprimora tabelas com cores de risco
6. Gera TOC (Table of Contents)
7. Renderiza template Jinja2
"""

import re
import shutil
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

# Imports opcionais (podem não estar instalados)
try:
    import markdown
    from markdown.extensions.toc import TocExtension
    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

try:
    from jinja2 import Environment, FileSystemLoader
    HAS_JINJA2 = True
except ImportError:
    HAS_JINJA2 = False

from .parsers.mermaid_handler import MermaidHandler
from .parsers.ascii_art_handler import AsciiArtHandler
from .parsers.table_enhancer import TableEnhancer


@dataclass
class ProtocolMetadata:
    """Metadados extraídos do frontmatter YAML."""
    title: str = ""
    version: str = "1.0"
    date: str = ""
    status: str = "Documento Normativo"
    description: str = ""
    code: str = ""
    type: str = ""
    logo: str = ""
    signatures: list = field(default_factory=list)


@dataclass
class RenderConfig:
    """Configurações de renderização."""
    include_toc: bool = True
    include_mermaid: bool = True
    convert_ascii_forms: bool = True
    enhance_tables: bool = True
    copy_assets: bool = True
    minify_output: bool = False


class ProtocolRenderer:
    """
    Renderizador de protocolos Markdown para HTML.

    Uso:
        renderer = ProtocolRenderer()
        renderer.render(
            source_path=Path("protocolo.md"),
            output_path=Path("protocolo.html")
        )
    """

    def __init__(
        self,
        template_dir: Optional[Path] = None,
        config: Optional[RenderConfig] = None
    ):
        """
        Inicializa o renderer.

        Args:
            template_dir: Diretório com templates Jinja2.
                         Default: templates/ no mesmo diretório.
            config: Configurações de renderização.
        """
        self.base_dir = Path(__file__).parent
        self.template_dir = template_dir or self.base_dir / "templates"
        self.assets_dir = self.base_dir / "assets"
        self.config = config or RenderConfig()

        # Handlers especializados
        self.mermaid_handler = MermaidHandler()
        self.ascii_handler = AsciiArtHandler()
        self.table_enhancer = TableEnhancer()

        # Jinja2 Environment
        if HAS_JINJA2:
            self.jinja_env = Environment(
                loader=FileSystemLoader(str(self.template_dir)),
                autoescape=True
            )
        else:
            self.jinja_env = None

        # Markdown parser
        if HAS_MARKDOWN:
            self.md = markdown.Markdown(
                extensions=[
                    'tables',
                    'fenced_code',
                    'codehilite',
                    'attr_list',
                    'def_list',
                    TocExtension(
                        title='',
                        toc_depth=3,
                        slugify=self._slugify
                    )
                ],
                extension_configs={
                    'codehilite': {
                        'css_class': 'highlight',
                        'guess_lang': False
                    }
                }
            )
        else:
            self.md = None

    def _slugify(self, value: str, separator: str = "-") -> str:
        """
        Converte texto para slug (ID de âncora).

        Args:
            value: Texto a converter.
            separator: Separador de palavras.

        Returns:
            String slug (lowercase, sem acentos, sem espaços).
        """
        import unicodedata

        # Normaliza Unicode (remove acentos)
        value = unicodedata.normalize('NFKD', value)
        value = value.encode('ascii', 'ignore').decode('ascii')

        # Remove caracteres não-alfanuméricos
        value = re.sub(r'[^\w\s-]', '', value.lower())

        # Substitui espaços por separador
        value = re.sub(r'[-\s]+', separator, value).strip(separator)

        return value

    def extract_frontmatter(self, content: str) -> tuple[ProtocolMetadata, str]:
        """
        Extrai metadados YAML do início do documento.

        Args:
            content: Conteúdo Markdown completo.

        Returns:
            Tupla (metadata, body) onde body é o conteúdo sem frontmatter.
        """
        metadata = ProtocolMetadata()

        # Padrão para frontmatter YAML (entre ---)
        pattern = r'^---\s*\n(.*?)\n---\s*\n'
        match = re.match(pattern, content, re.DOTALL)

        if match and HAS_YAML:
            try:
                yaml_content = match.group(1)
                data = yaml.safe_load(yaml_content) or {}

                metadata.title = data.get('title', '')
                metadata.version = data.get('version', '1.0')
                metadata.date = data.get('date', '')
                metadata.status = data.get('status', 'Documento Normativo')
                metadata.description = data.get('description', '')
                metadata.code = data.get('code', '')
                metadata.type = data.get('type', '')
                metadata.logo = data.get('logo', '')
                metadata.signatures = data.get('signatures', [])

                body = content[match.end():]
            except yaml.YAMLError:
                body = content
        else:
            body = content

        # Se não tem frontmatter, tenta extrair título do H1
        if not metadata.title:
            h1_match = re.search(r'^#\s+(.+)$', body, re.MULTILINE)
            if h1_match:
                metadata.title = h1_match.group(1).strip()

        # Extrai versão/data do cabeçalho se não estiver no frontmatter
        if not metadata.version or not metadata.date:
            header_match = re.search(
                r'\*\*Versão:\*\*\s*(\S+)\s*\|\s*\*\*Data:\*\*\s*(.+?)$',
                body,
                re.MULTILINE
            )
            if header_match:
                if not metadata.version:
                    metadata.version = header_match.group(1)
                if not metadata.date:
                    metadata.date = header_match.group(2).strip()

        return metadata, body

    def process_content(self, content: str) -> str:
        """
        Processa o conteúdo Markdown com handlers especializados.

        Args:
            content: Conteúdo Markdown.

        Returns:
            Conteúdo HTML processado.
        """
        # 1. Processa blocos Mermaid (antes do Markdown parser)
        if self.config.include_mermaid:
            content = self.mermaid_handler.process(content)

        # 2. Converte ASCII Art para marcação especial (antes do Markdown parser)
        if self.config.convert_ascii_forms:
            content = self.ascii_handler.mark_ascii_blocks(content)

        # 3. Converte Markdown para HTML
        if self.md:
            self.md.reset()
            html_content = self.md.convert(content)
            toc_html = self.md.toc
        else:
            # Fallback básico se markdown não está instalado
            html_content = f"<pre>{content}</pre>"
            toc_html = ""

        # 4. Converte marcações ASCII para HTML semântico
        if self.config.convert_ascii_forms:
            html_content = self.ascii_handler.convert_to_html(html_content)

        # 5. Aprimora tabelas com cores de risco
        if self.config.enhance_tables:
            html_content = self.table_enhancer.enhance(html_content)

        return html_content, toc_html

    def render(
        self,
        source_path: Path,
        output_path: Path,
        metadata_override: Optional[dict] = None
    ) -> Path:
        """
        Renderiza um arquivo Markdown para HTML.

        Args:
            source_path: Caminho do arquivo .md de origem.
            output_path: Caminho do arquivo .html de saída.
            metadata_override: Metadados para sobrescrever os extraídos.

        Returns:
            Caminho do arquivo HTML gerado.
        """
        # Verifica dependências
        if not HAS_MARKDOWN:
            raise ImportError(
                "O pacote 'markdown' é necessário. "
                "Instale com: pip install markdown"
            )

        if not HAS_JINJA2:
            raise ImportError(
                "O pacote 'jinja2' é necessário. "
                "Instale com: pip install jinja2"
            )

        # Lê arquivo fonte
        content = source_path.read_text(encoding='utf-8')

        # Extrai metadados
        metadata, body = self.extract_frontmatter(content)

        # Aplica overrides
        if metadata_override:
            for key, value in metadata_override.items():
                if hasattr(metadata, key):
                    setattr(metadata, key, value)

        # Processa conteúdo
        html_content, toc_html = self.process_content(body)

        # Prepara dados para template
        template_data = {
            'title': metadata.title,
            'content': html_content,
            'toc': toc_html if self.config.include_toc else None,
            'metadata': {
                'version': metadata.version,
                'date': metadata.date,
                'status': metadata.status,
                'description': metadata.description,
                'logo': metadata.logo,
                'signatures': metadata.signatures
            },
            'breadcrumbs': None  # TODO: implementar breadcrumbs
        }

        # Renderiza template
        template = self.jinja_env.get_template('base.html')
        output_html = template.render(**template_data)

        # Cria diretório de saída se necessário
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Escreve arquivo HTML
        output_path.write_text(output_html, encoding='utf-8')

        # Copia assets se configurado
        if self.config.copy_assets:
            self._copy_assets(output_path.parent)

        return output_path

    def _copy_assets(self, output_dir: Path) -> None:
        """
        Copia arquivos de assets (CSS, imagens) para o diretório de saída.

        Args:
            output_dir: Diretório de saída.
        """
        assets_output = output_dir / "assets"

        # Usa dirs_exist_ok para sobrescrever sem remover primeiro
        # (evita problemas de permissão no Windows/OneDrive)
        shutil.copytree(
            self.assets_dir,
            assets_output,
            dirs_exist_ok=True
        )

    def render_batch(
        self,
        source_dir: Path,
        output_dir: Path,
        pattern: str = "*.md"
    ) -> list[Path]:
        """
        Renderiza múltiplos arquivos Markdown.

        Args:
            source_dir: Diretório com arquivos .md.
            output_dir: Diretório de saída para .html.
            pattern: Padrão glob para filtrar arquivos.

        Returns:
            Lista de caminhos dos arquivos HTML gerados.
        """
        output_files = []

        for source_file in source_dir.glob(pattern):
            output_file = output_dir / source_file.with_suffix('.html').name
            self.render(source_file, output_file)
            output_files.append(output_file)

        return output_files


def main():
    """Função principal para uso via CLI."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Renderiza protocolos Markdown para HTML"
    )
    parser.add_argument(
        "source",
        type=Path,
        help="Arquivo Markdown de origem"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Arquivo HTML de saída (default: mesmo nome com .html)"
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

    args = parser.parse_args()

    # Configura renderer
    config = RenderConfig(
        include_toc=not args.no_toc,
        include_mermaid=not args.no_mermaid
    )

    renderer = ProtocolRenderer(config=config)

    # Define output path
    output_path = args.output or args.source.with_suffix('.html')

    # Renderiza
    result = renderer.render(args.source, output_path)
    print(f"✓ Gerado: {result}")


if __name__ == "__main__":
    main()
