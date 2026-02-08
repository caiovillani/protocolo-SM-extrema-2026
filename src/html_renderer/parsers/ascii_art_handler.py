"""
ASCII Art Handler - Conversor de formulários em box-drawing para HTML

Este módulo detecta e converte blocos de ASCII art (usando caracteres
de box-drawing como ┌─┬─┐ │ ├─┼─┤ └─┴─┘) para elementos HTML semânticos.

Tipos de conversão:
1. Formulários com checkboxes [ ] → HTML forms
2. Tabelas simples → Mantidas como <pre> estilizado
3. Fluxogramas ASCII → Mantidos como <pre> estilizado
"""

import re
from typing import Optional
from dataclasses import dataclass, field
from enum import Enum


class AsciiBlockType(Enum):
    """Tipos de blocos ASCII detectados."""
    FORM = "form"           # Formulário com campos/checkboxes
    TABLE = "table"         # Tabela estruturada
    FLOWCHART = "flowchart" # Fluxograma
    UNKNOWN = "unknown"     # Tipo não identificado


@dataclass
class AsciiBlock:
    """Representa um bloco de ASCII art detectado."""
    content: str
    block_type: AsciiBlockType
    title: Optional[str] = None
    sections: list = field(default_factory=list)
    checkboxes: list = field(default_factory=list)


class AsciiArtHandler:
    """
    Handler para conversão de ASCII art em HTML.

    Detecta blocos com caracteres de box-drawing e os converte
    para elementos HTML semânticos com classes CSS apropriadas.
    """

    # Caracteres de box-drawing
    BOX_CHARS = set('┌┬┐├┼┤└┴┘─│╔╦╗╠╬╣╚╩╝═║┏┳┓┣╋┫┗┻┛━┃')

    # Padrão para detectar blocos de código com box-drawing
    CODE_BLOCK_PATTERN = re.compile(
        r'```\s*\n(.*?)```',
        re.DOTALL
    )

    # Padrão para checkbox
    CHECKBOX_PATTERN = re.compile(r'\[\s*\]|\[x\]|\[X\]')

    # Padrão para linhas de cabeçalho (primeira linha após borda superior)
    HEADER_PATTERN = re.compile(r'│\s*([^│]+?)\s*│')

    # Caracteres de fluxograma
    FLOWCHART_CHARS = {'▼', '▲', '◄', '►', '→', '←', '↓', '↑'}

    def __init__(self, convert_to_semantic: bool = True):
        """
        Inicializa o handler.

        Args:
            convert_to_semantic: Se True, converte para HTML semântico.
                                Se False, mantém como <pre> estilizado.
        """
        self.convert_to_semantic = convert_to_semantic
        self._block_counter = 0

    def _has_box_drawing(self, text: str) -> bool:
        """
        Verifica se o texto contém caracteres de box-drawing.

        Args:
            text: Texto a verificar.

        Returns:
            True se contém caracteres de box-drawing.
        """
        return bool(self.BOX_CHARS.intersection(text))

    def _has_flowchart_chars(self, text: str) -> bool:
        """
        Verifica se o texto contém caracteres de fluxograma.

        Args:
            text: Texto a verificar.

        Returns:
            True se contém caracteres de fluxograma.
        """
        return bool(self.FLOWCHART_CHARS.intersection(text))

    def _detect_block_type(self, content: str) -> AsciiBlockType:
        """
        Detecta o tipo de bloco ASCII.

        Args:
            content: Conteúdo do bloco.

        Returns:
            Tipo do bloco.
        """
        # Verifica se tem checkboxes → Formulário
        if self.CHECKBOX_PATTERN.search(content):
            return AsciiBlockType.FORM

        # Verifica se tem caracteres de fluxograma
        if self._has_flowchart_chars(content):
            return AsciiBlockType.FLOWCHART

        # Verifica se parece uma tabela (linhas separadoras horizontais)
        lines = content.strip().split('\n')
        separator_count = sum(
            1 for line in lines
            if '├' in line or '┼' in line or '┤' in line
        )

        if separator_count > 1:
            return AsciiBlockType.TABLE

        # Verifica se é formulário (tem campos com ___ ou linhas em branco para preencher)
        if '___' in content or re.search(r':\s*$', content, re.MULTILINE):
            return AsciiBlockType.FORM

        return AsciiBlockType.UNKNOWN

    def _extract_title(self, content: str) -> Optional[str]:
        """
        Extrai o título do bloco ASCII (primeira linha após borda superior).

        Args:
            content: Conteúdo do bloco.

        Returns:
            Título extraído ou None.
        """
        lines = content.strip().split('\n')

        for i, line in enumerate(lines):
            # Pula linhas de borda
            if line.strip().startswith('┌') or line.strip().startswith('╔'):
                continue

            # Procura título na próxima linha válida
            match = self.HEADER_PATTERN.search(line)
            if match:
                title = match.group(1).strip()
                # Ignora linhas que parecem dados de formulário
                if title and not '___' in title and not ':' in title:
                    return title

            break

        return None

    def _extract_sections(self, content: str) -> list[dict]:
        """
        Extrai seções de um formulário ASCII.

        Args:
            content: Conteúdo do formulário.

        Returns:
            Lista de dicionários com seções.
        """
        sections = []
        current_section = {'title': '', 'fields': []}
        lines = content.strip().split('\n')

        for line in lines:
            # Detecta início de nova seção (linha com apenas texto maiúsculo)
            if '│' in line:
                inner = self.HEADER_PATTERN.search(line)
                if inner:
                    text = inner.group(1).strip()

                    # Se é título de seção (maiúsculo, sem dados)
                    if (text.isupper() or
                        (text and not '___' in text and not ':' in text[-1:])):

                        # Salva seção anterior se existir
                        if current_section['fields']:
                            sections.append(current_section)

                        current_section = {'title': text, 'fields': []}

                    # Se é campo de formulário
                    elif ':' in text or '___' in text:
                        current_section['fields'].append(text)

        # Adiciona última seção
        if current_section['fields'] or current_section['title']:
            sections.append(current_section)

        return sections

    def _extract_checkboxes(self, content: str) -> list[dict]:
        """
        Extrai checkboxes do conteúdo.

        Args:
            content: Conteúdo do formulário.

        Returns:
            Lista de dicionários com checkboxes.
        """
        checkboxes = []

        for line in content.split('\n'):
            # Procura por [ ] ou [x]
            matches = list(self.CHECKBOX_PATTERN.finditer(line))

            for match in matches:
                # Pega o texto após o checkbox
                start = match.end()
                end = line.find('[', start) if '[' in line[start:] else len(line)
                end = min(end, line.find('│', start) if '│' in line[start:] else len(line))

                label = line[start:end].strip()
                checked = 'x' in match.group().lower()

                if label:
                    checkboxes.append({
                        'label': label,
                        'checked': checked
                    })

        return checkboxes

    def mark_ascii_blocks(self, content: str) -> str:
        """
        Marca blocos ASCII para processamento posterior.

        Esta função é chamada ANTES do parser Markdown para
        proteger os blocos ASCII de serem alterados.

        Args:
            content: Conteúdo Markdown.

        Returns:
            Conteúdo com blocos marcados.
        """
        def replace_block(match):
            block_content = match.group(1)

            if self._has_box_drawing(block_content):
                self._block_counter += 1
                block_type = self._detect_block_type(block_content)

                # Marca o bloco com identificador especial
                return (
                    f'<!-- ASCII_BLOCK_START:{self._block_counter}:{block_type.value} -->\n'
                    f'```\n{block_content}```\n'
                    f'<!-- ASCII_BLOCK_END:{self._block_counter} -->'
                )

            return match.group(0)

        return self.CODE_BLOCK_PATTERN.sub(replace_block, content)

    def convert_to_html(self, html_content: str) -> str:
        """
        Converte blocos ASCII marcados para HTML semântico.

        Esta função é chamada DEPOIS do parser Markdown.

        Args:
            html_content: Conteúdo HTML.

        Returns:
            HTML com blocos ASCII convertidos.
        """
        # Padrão para encontrar blocos marcados no HTML
        pattern = re.compile(
            r'<!-- ASCII_BLOCK_START:(\d+):(\w+) -->\s*'
            r'<pre><code>(.*?)</code></pre>\s*'
            r'<!-- ASCII_BLOCK_END:\1 -->',
            re.DOTALL
        )

        def replace_marked(match):
            block_id = match.group(1)
            block_type = match.group(2)
            content = match.group(3)

            # Decodifica entidades HTML
            content = (
                content
                .replace('&lt;', '<')
                .replace('&gt;', '>')
                .replace('&amp;', '&')
            )

            return self._render_block(content, block_type, block_id)

        return pattern.sub(replace_marked, html_content)

    def _render_block(self, content: str, block_type: str, block_id: str) -> str:
        """
        Renderiza um bloco ASCII para HTML.

        Args:
            content: Conteúdo do bloco.
            block_type: Tipo do bloco.
            block_id: ID único do bloco.

        Returns:
            HTML do bloco.
        """
        if not self.convert_to_semantic:
            return self._render_as_pre(content, block_type)

        if block_type == 'form':
            return self._render_form(content, block_id)
        elif block_type == 'flowchart':
            return self._render_flowchart(content, block_id)
        else:
            return self._render_as_pre(content, block_type)

    def _render_as_pre(self, content: str, block_type: str) -> str:
        """
        Renderiza como elemento <pre> estilizado.

        Args:
            content: Conteúdo do bloco.
            block_type: Tipo do bloco.

        Returns:
            HTML do bloco.
        """
        css_class = f"form-ascii form-ascii--raw form-ascii--{block_type}"
        return f'<div class="{css_class}"><pre>{content}</pre></div>'

    def _render_form(self, content: str, block_id: str) -> str:
        """
        Renderiza formulário ASCII como HTML semântico.

        Args:
            content: Conteúdo do formulário.
            block_id: ID único.

        Returns:
            HTML do formulário.
        """
        title = self._extract_title(content)
        sections = self._extract_sections(content)
        checkboxes = self._extract_checkboxes(content)

        html_parts = [
            f'<div class="form-ascii" role="form" aria-label="{title or "Formulário"}" id="form-{block_id}">'
        ]

        # Header
        if title:
            html_parts.append(f'<div class="form-ascii__header">{title}</div>')

        # Se tem checkboxes, renderiza como lista
        if checkboxes:
            html_parts.append('<div class="form-ascii__section">')
            for i, cb in enumerate(checkboxes):
                checked = 'checked' if cb['checked'] else ''
                html_parts.append(f'''
                    <div class="form-ascii__checkbox">
                        <input type="checkbox" id="cb-{block_id}-{i}" {checked} disabled>
                        <label for="cb-{block_id}-{i}">{cb['label']}</label>
                    </div>
                ''')
            html_parts.append('</div>')

        # Se tem seções estruturadas
        elif sections:
            for section in sections:
                html_parts.append('<div class="form-ascii__section">')
                if section['title']:
                    html_parts.append(
                        f'<div class="form-ascii__section-title">{section["title"]}</div>'
                    )
                for field in section['fields']:
                    html_parts.append(f'<div class="form-ascii__field">{field}</div>')
                html_parts.append('</div>')

        # Fallback: renderiza como pre
        else:
            html_parts.append(f'<pre class="form-ascii__body">{content}</pre>')

        html_parts.append('</div>')

        return '\n'.join(html_parts)

    def _render_flowchart(self, content: str, block_id: str) -> str:
        """
        Renderiza fluxograma ASCII.

        Args:
            content: Conteúdo do fluxograma.
            block_id: ID único.

        Returns:
            HTML do fluxograma.
        """
        return f'''
        <figure class="diagram diagram--ascii-flowchart" id="flowchart-{block_id}">
            <div class="diagram__wrapper">
                <pre class="flowchart-ascii">{content}</pre>
            </div>
            <figcaption class="diagram__caption">Fluxograma</figcaption>
        </figure>
        '''

    def reset(self) -> None:
        """Reseta o contador de blocos."""
        self._block_counter = 0
