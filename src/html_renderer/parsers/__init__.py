"""
Parsers especializados para o HTML Renderer.

- MermaidHandler: Processa blocos de diagrama Mermaid
- AsciiArtHandler: Converte formulários em ASCII art para HTML
- TableEnhancer: Adiciona classes de cor às tabelas de risco
"""

from .mermaid_handler import MermaidHandler
from .ascii_art_handler import AsciiArtHandler
from .table_enhancer import TableEnhancer

__all__ = ["MermaidHandler", "AsciiArtHandler", "TableEnhancer"]
