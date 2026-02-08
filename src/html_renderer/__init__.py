"""
HTML Renderer - Sistema de Protocolos RAPS Extrema/MG

Este módulo converte documentos Markdown de protocolos clínicos
para HTML com suporte a:
- Diagramas Mermaid
- Formulários ASCII Art
- Tabelas de classificação de risco
- Design institucional responsivo
- Impressão profissional
"""

from .renderer import ProtocolRenderer

__version__ = "1.0.0"
__all__ = ["ProtocolRenderer"]
