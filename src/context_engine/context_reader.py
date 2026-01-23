# src/context_engine/context_reader.py

"""Leitores de arquivos heterogêneos para o Motor de Contexto.

Suporta leitura integral de: MD, TXT, YAML, PY, PDF
Cada reader retorna conteúdo completo sem truncamento.
"""

import hashlib
import re
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

import yaml

from .context_models import DocumentMetadata, StructuredSection


class FileReader(ABC):
    """Classe base abstrata para leitores de arquivo."""

    @property
    @abstractmethod
    def supported_extensions(self) -> List[str]:
        """Extensões suportadas (ex: ['.md', '.markdown'])."""
        pass

    def can_read(self, file_path: Path) -> bool:
        """Verifica se pode ler o arquivo."""
        return file_path.suffix.lower() in self.supported_extensions

    @abstractmethod
    def read(self, file_path: Path) -> Tuple[str, List[StructuredSection]]:
        """Lê arquivo e retorna conteúdo + estrutura.

        Returns:
            Tupla (conteúdo_completo, lista_de_seções)
        """
        pass

    def create_metadata(
        self,
        file_path: Path,
        content: str,
        processing_time_ms: float,
    ) -> DocumentMetadata:
        """Cria metadados do documento."""
        file_stat = file_path.stat()
        content_hash = hashlib.md5(content.encode('utf-8', errors='ignore')).hexdigest()

        return DocumentMetadata(
            file_path=file_path,
            file_type=file_path.suffix.lstrip('.').lower(),
            size_bytes=file_stat.st_size,
            lines_count=content.count('\n') + 1,
            tokens_estimate=len(content) // 4,
            processed_at=datetime.now(),
            processing_time_ms=processing_time_ms,
            hash_md5=content_hash,
        )


class MarkdownReader(FileReader):
    """Leitor de arquivos Markdown."""

    @property
    def supported_extensions(self) -> List[str]:
        return ['.md', '.markdown']

    def read(self, file_path: Path) -> Tuple[str, List[StructuredSection]]:
        """Lê arquivo MD extraindo estrutura de headers."""
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        sections = self._extract_sections(content)
        return content, sections

    def _extract_sections(self, content: str) -> List[StructuredSection]:
        """Extrai estrutura hierárquica de headers."""
        sections = []
        lines = content.split('\n')
        current_section: Optional[StructuredSection] = None
        section_start = 0

        for i, line in enumerate(lines):
            if line.startswith('#'):
                # Finalizar seção anterior
                if current_section:
                    current_section.end_line = i
                    current_section.content = '\n'.join(lines[section_start:i])

                # Extrair nível e título
                level = len(line) - len(line.lstrip('#'))
                title = line.lstrip('#').strip()

                current_section = StructuredSection(
                    title=title,
                    level=level,
                    start_line=i + 1,
                    end_line=len(lines),
                    content="",
                )
                sections.append(current_section)
                section_start = i

        # Finalizar última seção
        if current_section:
            current_section.end_line = len(lines)
            current_section.content = '\n'.join(lines[section_start:])

        return sections


class TextReader(FileReader):
    """Leitor de arquivos de texto puro."""

    @property
    def supported_extensions(self) -> List[str]:
        return ['.txt', '.text']

    def read(self, file_path: Path) -> Tuple[str, List[StructuredSection]]:
        """Lê arquivo TXT com estrutura genérica de parágrafos."""
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        sections = self._extract_paragraphs(content)
        return content, sections

    def _extract_paragraphs(self, content: str) -> List[StructuredSection]:
        """Extrai parágrafos como seções."""
        sections = []
        paragraphs = content.split('\n\n')
        line_num = 1

        for i, para in enumerate(paragraphs):
            if para.strip():
                para_lines = para.count('\n') + 1
                title = para.split('\n')[0][:50] + ('...' if len(para.split('\n')[0]) > 50 else '')

                sections.append(StructuredSection(
                    title=title,
                    level=1,
                    start_line=line_num,
                    end_line=line_num + para_lines - 1,
                    content=para,
                ))
                line_num += para_lines + 1  # +1 for blank line
            else:
                line_num += 1

        return sections


class YAMLReader(FileReader):
    """Leitor de arquivos YAML."""

    @property
    def supported_extensions(self) -> List[str]:
        return ['.yaml', '.yml']

    def read(self, file_path: Path) -> Tuple[str, List[StructuredSection]]:
        """Lê arquivo YAML extraindo chaves principais como seções."""
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        sections = self._extract_yaml_structure(content)
        return content, sections

    def _extract_yaml_structure(self, content: str) -> List[StructuredSection]:
        """Extrai chaves de primeiro nível como seções."""
        sections = []

        try:
            data = yaml.safe_load(content)
            if isinstance(data, dict):
                for i, (key, value) in enumerate(data.items()):
                    sections.append(StructuredSection(
                        title=str(key),
                        level=1,
                        start_line=i + 1,
                        end_line=i + 1,
                        content=yaml.dump({key: value}, allow_unicode=True),
                    ))
        except yaml.YAMLError:
            # Fallback: tratar como texto
            sections.append(StructuredSection(
                title="YAML (parse error)",
                level=1,
                start_line=1,
                end_line=content.count('\n') + 1,
                content=content,
            ))

        return sections


class PythonReader(FileReader):
    """Leitor de arquivos Python."""

    @property
    def supported_extensions(self) -> List[str]:
        return ['.py']

    def read(self, file_path: Path) -> Tuple[str, List[StructuredSection]]:
        """Lê arquivo PY extraindo classes, funções e imports."""
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        sections = self._extract_python_structure(content)
        return content, sections

    def _extract_python_structure(self, content: str) -> List[StructuredSection]:
        """Extrai estrutura de código Python."""
        sections = []
        lines = content.split('\n')

        # Padrões para detecção
        class_pattern = re.compile(r'^class\s+(\w+)')
        func_pattern = re.compile(r'^def\s+(\w+)')
        import_pattern = re.compile(r'^(?:import|from)\s+')

        current_block: Optional[StructuredSection] = None
        block_start = 0
        imports_section = None

        for i, line in enumerate(lines):
            stripped = line.lstrip()

            # Imports (agrupar todos)
            if import_pattern.match(stripped) and not imports_section:
                imports_section = StructuredSection(
                    title="imports",
                    level=1,
                    start_line=i + 1,
                    end_line=i + 1,
                    content=line,
                )
                sections.insert(0, imports_section)
            elif imports_section and import_pattern.match(stripped):
                imports_section.end_line = i + 1
                imports_section.content += '\n' + line

            # Classes
            class_match = class_pattern.match(stripped)
            if class_match and not line.startswith(' '):
                if current_block:
                    current_block.end_line = i
                    current_block.content = '\n'.join(lines[block_start:i])

                current_block = StructuredSection(
                    title=f"class {class_match.group(1)}",
                    level=1,
                    start_line=i + 1,
                    end_line=len(lines),
                    content="",
                )
                sections.append(current_block)
                block_start = i

            # Funções de nível superior
            func_match = func_pattern.match(stripped)
            if func_match and not line.startswith(' '):
                if current_block:
                    current_block.end_line = i
                    current_block.content = '\n'.join(lines[block_start:i])

                current_block = StructuredSection(
                    title=f"def {func_match.group(1)}",
                    level=2,
                    start_line=i + 1,
                    end_line=len(lines),
                    content="",
                )
                sections.append(current_block)
                block_start = i

        # Finalizar último bloco
        if current_block:
            current_block.end_line = len(lines)
            current_block.content = '\n'.join(lines[block_start:])

        return sections


class PDFReader(FileReader):
    """Leitor de arquivos PDF usando pypdf."""

    def __init__(self):
        """Inicializa reader verificando disponibilidade do pypdf."""
        self._pypdf_available = False
        try:
            from pypdf import PdfReader as PyPdfReader
            self._pypdf_available = True
            self._PdfReader = PyPdfReader
        except ImportError:
            pass

    @property
    def supported_extensions(self) -> List[str]:
        return ['.pdf']

    def can_read(self, file_path: Path) -> bool:
        """Verifica se pode ler PDF (requer pypdf instalado)."""
        return (
            file_path.suffix.lower() in self.supported_extensions
            and self._pypdf_available
        )

    def read(self, file_path: Path) -> Tuple[str, List[StructuredSection]]:
        """Lê PDF extraindo texto de todas as páginas."""
        if not self._pypdf_available:
            raise ImportError(
                "pypdf não está instalado. Execute: pip install pypdf"
            )

        reader = self._PdfReader(file_path)
        text_parts = []
        sections = []

        for page_num, page in enumerate(reader.pages, 1):
            page_text = page.extract_text() or ""
            text_parts.append(f"--- Página {page_num} ---\n{page_text}")

            sections.append(StructuredSection(
                title=f"Página {page_num}",
                level=1,
                start_line=sum(t.count('\n') for t in text_parts[:-1]) + 1,
                end_line=sum(t.count('\n') for t in text_parts) + 1,
                content=page_text,
            ))

        full_content = '\n\n'.join(text_parts)
        return full_content, sections


class ReaderFactory:
    """Factory para seleção automática de reader."""

    def __init__(self):
        """Inicializa factory com readers disponíveis."""
        self.readers: List[FileReader] = [
            MarkdownReader(),
            TextReader(),
            YAMLReader(),
            PythonReader(),
            PDFReader(),
        ]

    def get_reader(self, file_path: Path) -> Optional[FileReader]:
        """Retorna reader apropriado para o arquivo."""
        for reader in self.readers:
            if reader.can_read(file_path):
                return reader
        return None

    def get_supported_extensions(self) -> List[str]:
        """Retorna todas as extensões suportadas."""
        extensions = []
        for reader in self.readers:
            extensions.extend(reader.supported_extensions)
        return extensions


# Instância global do factory
_reader_factory = ReaderFactory()


def read_file(file_path: Path) -> Tuple[str, List[StructuredSection], DocumentMetadata]:
    """Função conveniente para ler qualquer arquivo suportado.

    Args:
        file_path: Caminho do arquivo

    Returns:
        Tupla (conteúdo, seções, metadados)

    Raises:
        FileNotFoundError: Arquivo não encontrado
        ValueError: Tipo de arquivo não suportado
    """
    import time

    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    reader = _reader_factory.get_reader(file_path)
    if reader is None:
        supported = ', '.join(_reader_factory.get_supported_extensions())
        raise ValueError(
            f"Tipo de arquivo não suportado: {file_path.suffix}. "
            f"Tipos suportados: {supported}"
        )

    start_time = time.perf_counter()
    content, sections = reader.read(file_path)
    elapsed_ms = (time.perf_counter() - start_time) * 1000

    metadata = reader.create_metadata(file_path, content, elapsed_ms)

    return content, sections, metadata
