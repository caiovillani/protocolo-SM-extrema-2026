"""
Table Enhancer - Aprimorador de tabelas HTML

Este módulo processa tabelas HTML geradas pelo parser Markdown
e adiciona classes CSS para estilização, especialmente para
tabelas de classificação de risco em protocolos clínicos.

Funcionalidades:
1. Detecta tabelas de classificação de risco
2. Adiciona atributos data-risco às linhas
3. Converte labels de cor em spans estilizados
4. Envolve tabelas em wrappers responsivos
"""

import re
from typing import Optional
from dataclasses import dataclass
from enum import Enum


class RiskLevel(Enum):
    """Níveis de risco padronizados."""
    VERMELHO = "vermelho"
    LARANJA = "laranja"
    AMARELO = "amarelo"
    VERDE = "verde"
    AZUL = "azul"


@dataclass
class TableInfo:
    """Informações sobre uma tabela detectada."""
    is_risk_table: bool = False
    color_column_index: Optional[int] = None
    priority_column_index: Optional[int] = None


class TableEnhancer:
    """
    Aprimorador de tabelas HTML.

    Detecta automaticamente tabelas de classificação de risco
    e adiciona classes CSS apropriadas para estilização.
    """

    # Palavras-chave que indicam coluna de cor/risco
    COLOR_KEYWORDS = {
        'cor', 'color', 'risco', 'risk', 'classificação',
        'prioridade', 'priority', 'nível', 'level'
    }

    # Mapeamento de texto para nível de risco
    RISK_MAPPINGS = {
        # Cores
        'vermelho': RiskLevel.VERMELHO,
        'vermelha': RiskLevel.VERMELHO,
        'red': RiskLevel.VERMELHO,

        'laranja': RiskLevel.LARANJA,
        'orange': RiskLevel.LARANJA,

        'amarelo': RiskLevel.AMARELO,
        'amarela': RiskLevel.AMARELO,
        'yellow': RiskLevel.AMARELO,

        'verde': RiskLevel.VERDE,
        'green': RiskLevel.VERDE,

        'azul': RiskLevel.AZUL,
        'blue': RiskLevel.AZUL,

        # Prioridades (P1, P2, etc.)
        'p1': RiskLevel.VERMELHO,
        'p2': RiskLevel.LARANJA,
        'p3': RiskLevel.AMARELO,
        'p4': RiskLevel.VERDE,

        # Níveis
        'urgência': RiskLevel.VERMELHO,
        'urgencia': RiskLevel.VERMELHO,
        'emergência': RiskLevel.VERMELHO,
        'emergencia': RiskLevel.VERMELHO,
        'imediato': RiskLevel.VERMELHO,
        'crítico': RiskLevel.VERMELHO,
        'critico': RiskLevel.VERMELHO,

        'alto': RiskLevel.LARANJA,
        'alta': RiskLevel.LARANJA,
        'high': RiskLevel.LARANJA,

        'moderado': RiskLevel.AMARELO,
        'moderada': RiskLevel.AMARELO,
        'médio': RiskLevel.AMARELO,
        'medio': RiskLevel.AMARELO,
        'medium': RiskLevel.AMARELO,

        'baixo': RiskLevel.VERDE,
        'baixa': RiskLevel.VERDE,
        'low': RiskLevel.VERDE,

        'eletivo': RiskLevel.AZUL,
        'programado': RiskLevel.AZUL,
        'programada': RiskLevel.AZUL,
    }

    # Padrões regex
    TABLE_PATTERN = re.compile(r'<table>(.*?)</table>', re.DOTALL | re.IGNORECASE)
    THEAD_PATTERN = re.compile(r'<thead>(.*?)</thead>', re.DOTALL | re.IGNORECASE)
    TBODY_PATTERN = re.compile(r'<tbody>(.*?)</tbody>', re.DOTALL | re.IGNORECASE)
    TR_PATTERN = re.compile(r'<tr>(.*?)</tr>', re.DOTALL | re.IGNORECASE)
    TH_PATTERN = re.compile(r'<th[^>]*>(.*?)</th>', re.DOTALL | re.IGNORECASE)
    TD_PATTERN = re.compile(r'<td[^>]*>(.*?)</td>', re.DOTALL | re.IGNORECASE)

    def __init__(self, add_wrapper: bool = True, add_risk_labels: bool = True):
        """
        Inicializa o enhancer.

        Args:
            add_wrapper: Se True, envolve tabelas em div.table-wrapper.
            add_risk_labels: Se True, converte texto de risco em spans estilizados.
        """
        self.add_wrapper = add_wrapper
        self.add_risk_labels = add_risk_labels

    def _clean_html(self, text: str) -> str:
        """
        Remove tags HTML e normaliza texto.

        Args:
            text: Texto com possíveis tags HTML.

        Returns:
            Texto limpo e normalizado.
        """
        # Remove tags HTML
        clean = re.sub(r'<[^>]+>', '', text)
        # Remove espaços extras
        clean = ' '.join(clean.split())
        return clean.strip().lower()

    def _detect_risk_level(self, text: str) -> Optional[RiskLevel]:
        """
        Detecta o nível de risco a partir do texto.

        Args:
            text: Texto a analisar.

        Returns:
            RiskLevel se detectado, None caso contrário.
        """
        clean_text = self._clean_html(text)

        # Verifica mapeamentos diretos
        for keyword, level in self.RISK_MAPPINGS.items():
            if keyword in clean_text:
                return level

        # Verifica padrões especiais (ex: "VERDE/AZUL")
        if 'verde' in clean_text and 'azul' in clean_text:
            return RiskLevel.VERDE

        return None

    def _analyze_table_headers(self, thead_content: str) -> TableInfo:
        """
        Analisa cabeçalhos da tabela para detectar colunas de risco.

        Args:
            thead_content: Conteúdo do <thead>.

        Returns:
            TableInfo com informações sobre a tabela.
        """
        info = TableInfo()

        # Extrai células do cabeçalho
        headers = self.TH_PATTERN.findall(thead_content)

        for i, header in enumerate(headers):
            header_clean = self._clean_html(header)

            # Verifica se é coluna de cor/risco
            if any(kw in header_clean for kw in self.COLOR_KEYWORDS):
                info.is_risk_table = True
                info.color_column_index = i
                break

        return info

    def _enhance_row(
        self,
        tr_content: str,
        table_info: TableInfo,
        is_header: bool = False
    ) -> str:
        """
        Aprimora uma linha da tabela.

        Args:
            tr_content: Conteúdo original do <tr>.
            table_info: Informações sobre a tabela.
            is_header: Se True, é linha de cabeçalho.

        Returns:
            Conteúdo aprimorado do <tr>.
        """
        if is_header or not table_info.is_risk_table:
            return f'<tr>{tr_content}</tr>'

        # Extrai células
        cells = self.TD_PATTERN.findall(tr_content)
        if not cells:
            return f'<tr>{tr_content}</tr>'

        # Detecta nível de risco
        risk_level = None

        # Verifica coluna específica de cor
        if table_info.color_column_index is not None:
            if table_info.color_column_index < len(cells):
                risk_level = self._detect_risk_level(
                    cells[table_info.color_column_index]
                )

        # Se não encontrou na coluna específica, procura em todas
        if risk_level is None:
            for cell in cells:
                risk_level = self._detect_risk_level(cell)
                if risk_level:
                    break

        if risk_level:
            # Adiciona atributo data-risco
            enhanced_content = tr_content

            # Melhora a célula de cor com label estilizado
            if self.add_risk_labels and table_info.color_column_index is not None:
                enhanced_content = self._enhance_risk_cell(
                    enhanced_content,
                    risk_level
                )

            return f'<tr data-risco="{risk_level.value}">{enhanced_content}</tr>'

        return f'<tr>{tr_content}</tr>'

    def _enhance_risk_cell(self, content: str, risk_level: RiskLevel) -> str:
        """
        Aprimora célula de risco com span estilizado.

        Args:
            content: Conteúdo da linha.
            risk_level: Nível de risco detectado.

        Returns:
            Conteúdo com célula aprimorada.
        """
        # Padrão para encontrar célula com nome da cor (ex: **VERMELHO**)
        patterns = [
            (r'\*\*(' + risk_level.value.upper() + r')\*\*', r'<span class="risco-label risco-label--' + risk_level.value + r'">\1</span>'),
            (r'\*\*(' + risk_level.value.capitalize() + r')\*\*', r'<span class="risco-label risco-label--' + risk_level.value + r'">\1</span>'),
        ]

        result = content
        for pattern, replacement in patterns:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

        return result

    def _enhance_table(self, table_match) -> str:
        """
        Aprimora uma tabela individual.

        Args:
            table_match: Match object do padrão de tabela.

        Returns:
            HTML da tabela aprimorada.
        """
        table_content = table_match.group(1)

        # Analisa cabeçalho
        thead_match = self.THEAD_PATTERN.search(table_content)
        table_info = TableInfo()

        if thead_match:
            table_info = self._analyze_table_headers(thead_match.group(1))

        # Processa body
        tbody_match = self.TBODY_PATTERN.search(table_content)

        if tbody_match:
            tbody_content = tbody_match.group(1)
            new_tbody_content = []

            # Processa cada linha
            for tr_match in self.TR_PATTERN.finditer(tbody_content):
                enhanced_row = self._enhance_row(
                    tr_match.group(1),
                    table_info
                )
                new_tbody_content.append(enhanced_row)

            # Substitui tbody
            new_tbody = '<tbody>' + ''.join(new_tbody_content) + '</tbody>'
            table_content = self.TBODY_PATTERN.sub(new_tbody, table_content)

        # Define classe da tabela
        table_class = "table--risco" if table_info.is_risk_table else ""

        # Monta tabela final
        table_html = f'<table class="{table_class}">{table_content}</table>'

        # Adiciona wrapper se configurado
        if self.add_wrapper:
            table_html = f'<div class="table-wrapper">{table_html}</div>'

        return table_html

    def enhance(self, html_content: str) -> str:
        """
        Aprimora todas as tabelas no conteúdo HTML.

        Args:
            html_content: Conteúdo HTML com tabelas.

        Returns:
            Conteúdo com tabelas aprimoradas.
        """
        return self.TABLE_PATTERN.sub(self._enhance_table, html_content)

    def detect_risk_tables(self, html_content: str) -> list[dict]:
        """
        Detecta e analisa tabelas de risco no conteúdo.

        Args:
            html_content: Conteúdo HTML.

        Returns:
            Lista de dicionários com informações sobre tabelas de risco.
        """
        risk_tables = []

        for i, match in enumerate(self.TABLE_PATTERN.finditer(html_content)):
            table_content = match.group(1)
            thead_match = self.THEAD_PATTERN.search(table_content)

            if thead_match:
                table_info = self._analyze_table_headers(thead_match.group(1))

                if table_info.is_risk_table:
                    # Conta linhas por nível de risco
                    risk_counts = {level: 0 for level in RiskLevel}
                    tbody_match = self.TBODY_PATTERN.search(table_content)

                    if tbody_match:
                        for tr_match in self.TR_PATTERN.finditer(tbody_match.group(1)):
                            for cell in self.TD_PATTERN.findall(tr_match.group(1)):
                                level = self._detect_risk_level(cell)
                                if level:
                                    risk_counts[level] += 1
                                    break

                    risk_tables.append({
                        'index': i,
                        'color_column': table_info.color_column_index,
                        'risk_counts': {
                            level.value: count
                            for level, count in risk_counts.items()
                            if count > 0
                        }
                    })

        return risk_tables
