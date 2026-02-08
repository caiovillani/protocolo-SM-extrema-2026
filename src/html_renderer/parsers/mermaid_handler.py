"""
Mermaid Handler - Processador de diagramas Mermaid

Detecta blocos de código Mermaid no Markdown e os converte
para elementos HTML que serão renderizados pelo Mermaid.js.
"""

import re
from typing import Optional
from dataclasses import dataclass


@dataclass
class MermaidDiagram:
    """Representa um diagrama Mermaid extraído."""
    id: str
    content: str
    diagram_type: str
    caption: Optional[str] = None


class MermaidHandler:
    """
    Processa blocos de diagrama Mermaid no conteúdo Markdown.

    O handler detecta blocos ```mermaid e os converte para
    elementos HTML <div class="mermaid"> que serão renderizados
    pelo Mermaid.js no navegador.
    """

    # Padrão para blocos de código Mermaid
    MERMAID_PATTERN = re.compile(
        r'```mermaid\s*\n(.*?)```',
        re.DOTALL
    )

    # Tipos de diagrama suportados
    DIAGRAM_TYPES = {
        'flowchart': 'Fluxograma',
        'graph': 'Grafo',
        'sequenceDiagram': 'Diagrama de Sequência',
        'classDiagram': 'Diagrama de Classes',
        'stateDiagram': 'Diagrama de Estados',
        'erDiagram': 'Diagrama ER',
        'gantt': 'Gráfico de Gantt',
        'pie': 'Gráfico de Pizza',
        'journey': 'Jornada do Usuário',
        'gitGraph': 'Grafo Git',
        'mindmap': 'Mapa Mental',
        'timeline': 'Linha do Tempo',
        'quadrantChart': 'Gráfico de Quadrantes',
        'xychart': 'Gráfico XY',
        'block': 'Diagrama de Blocos'
    }

    def __init__(self, add_captions: bool = True):
        """
        Inicializa o handler.

        Args:
            add_captions: Se True, adiciona legendas automáticas aos diagramas.
        """
        self.add_captions = add_captions
        self._diagram_counter = 0

    def _detect_diagram_type(self, content: str) -> str:
        """
        Detecta o tipo de diagrama a partir do conteúdo.

        Args:
            content: Conteúdo do diagrama Mermaid.

        Returns:
            Nome do tipo de diagrama.
        """
        content_lower = content.strip().lower()

        for keyword, name in self.DIAGRAM_TYPES.items():
            if content_lower.startswith(keyword.lower()):
                return name

        return "Diagrama"

    def _generate_id(self, diagram_type: str) -> str:
        """
        Gera um ID único para o diagrama.

        Args:
            diagram_type: Tipo do diagrama.

        Returns:
            ID único no formato 'diagram-{tipo}-{numero}'.
        """
        self._diagram_counter += 1
        tipo_slug = diagram_type.lower().replace(' ', '-').replace('á', 'a')
        return f"diagram-{tipo_slug}-{self._diagram_counter}"

    def _extract_title_from_subgraph(self, content: str) -> Optional[str]:
        """
        Tenta extrair um título a partir do primeiro subgraph.

        Args:
            content: Conteúdo do diagrama Mermaid.

        Returns:
            Título extraído ou None.
        """
        # Procura por subgraph com título
        match = re.search(
            r'subgraph\s+\w+\s*\["([^"]+)"\]',
            content
        )
        if match:
            return match.group(1)

        # Procura por subgraph simples
        match = re.search(
            r'subgraph\s+(\w+)',
            content
        )
        if match:
            return match.group(1).replace('_', ' ').title()

        return None

    def _create_html(self, diagram: MermaidDiagram) -> str:
        """
        Cria o HTML para um diagrama Mermaid.

        Args:
            diagram: Objeto MermaidDiagram com os dados.

        Returns:
            String HTML do diagrama.
        """
        # Escapa caracteres HTML no conteúdo do diagrama
        content_escaped = (
            diagram.content
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
        )

        # Monta o HTML
        html_parts = [
            f'<figure class="diagram diagram--{diagram.diagram_type.lower().replace(" ", "-")}" ',
            f'role="img" aria-label="{diagram.diagram_type}">',
            f'<div class="diagram__wrapper">',
            f'<div class="mermaid" data-diagram-id="{diagram.id}">',
            diagram.content,  # Conteúdo original (não escapado) para Mermaid.js
            '</div>',
            '</div>',
        ]

        # Adiciona caption se configurado
        if self.add_captions and diagram.caption:
            html_parts.extend([
                f'<figcaption class="diagram__caption">',
                f'Figura: {diagram.caption}',
                '</figcaption>'
            ])

        html_parts.append('</figure>')

        # Adiciona fallback para noscript
        html_parts.extend([
            '<noscript>',
            '<div class="diagram__fallback">',
            '<p>Este diagrama requer JavaScript para visualização.</p>',
            '<p>Consulte a versão em PDF para visualização offline.</p>',
            '</div>',
            '</noscript>'
        ])

        return '\n'.join(html_parts)

    def process(self, content: str) -> str:
        """
        Processa o conteúdo Markdown, convertendo blocos Mermaid em HTML.

        Args:
            content: Conteúdo Markdown completo.

        Returns:
            Conteúdo com blocos Mermaid convertidos para HTML.
        """
        def replace_mermaid(match):
            mermaid_content = match.group(1).strip()

            # Detecta tipo de diagrama
            diagram_type = self._detect_diagram_type(mermaid_content)

            # Gera ID único
            diagram_id = self._generate_id(diagram_type)

            # Tenta extrair título
            caption = self._extract_title_from_subgraph(mermaid_content)
            if not caption:
                caption = diagram_type

            # Cria objeto de diagrama
            diagram = MermaidDiagram(
                id=diagram_id,
                content=mermaid_content,
                diagram_type=diagram_type,
                caption=caption
            )

            return self._create_html(diagram)

        # Substitui todos os blocos Mermaid
        return self.MERMAID_PATTERN.sub(replace_mermaid, content)

    def extract_diagrams(self, content: str) -> list[MermaidDiagram]:
        """
        Extrai todos os diagramas Mermaid do conteúdo.

        Args:
            content: Conteúdo Markdown.

        Returns:
            Lista de objetos MermaidDiagram.
        """
        diagrams = []

        for match in self.MERMAID_PATTERN.finditer(content):
            mermaid_content = match.group(1).strip()
            diagram_type = self._detect_diagram_type(mermaid_content)
            diagram_id = self._generate_id(diagram_type)
            caption = self._extract_title_from_subgraph(mermaid_content)

            diagrams.append(MermaidDiagram(
                id=diagram_id,
                content=mermaid_content,
                diagram_type=diagram_type,
                caption=caption or diagram_type
            ))

        return diagrams

    def reset(self) -> None:
        """Reseta o contador de diagramas."""
        self._diagram_counter = 0
