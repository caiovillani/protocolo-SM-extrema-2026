# tests/test_html_renderer.py

"""Testes para o renderizador HTML de protocolos clínicos."""

import pytest
from pathlib import Path

from src.html_renderer.parsers.mermaid_handler import MermaidHandler, MermaidDiagram
from src.html_renderer.parsers.table_enhancer import TableEnhancer, RiskLevel, TableInfo


# =============================================================================
# Testes do MermaidHandler
# =============================================================================


class TestMermaidHandler:
    """Testes para o processador de diagramas Mermaid."""

    @pytest.fixture
    def handler(self):
        """Cria instância do handler para testes."""
        return MermaidHandler(add_captions=True)

    def test_detect_flowchart_type(self, handler):
        """Deve detectar diagrama tipo flowchart."""
        content = "flowchart TD\n    A --> B"
        diagram_type = handler._detect_diagram_type(content)
        assert diagram_type == "Fluxograma"

    def test_detect_graph_type(self, handler):
        """Deve detectar diagrama tipo graph."""
        content = "graph LR\n    A --> B"
        diagram_type = handler._detect_diagram_type(content)
        assert diagram_type == "Grafo"

    def test_detect_sequence_diagram_type(self, handler):
        """Deve detectar diagrama de sequência."""
        content = "sequenceDiagram\n    Alice->>Bob: Hello"
        diagram_type = handler._detect_diagram_type(content)
        assert diagram_type == "Diagrama de Sequência"

    def test_detect_unknown_type(self, handler):
        """Deve retornar 'Diagrama' para tipos desconhecidos."""
        content = "unknown\n    A --> B"
        diagram_type = handler._detect_diagram_type(content)
        assert diagram_type == "Diagrama"

    def test_generate_unique_ids(self, handler):
        """Deve gerar IDs únicos para cada diagrama."""
        id1 = handler._generate_id("Fluxograma")
        id2 = handler._generate_id("Fluxograma")
        id3 = handler._generate_id("Grafo")

        assert id1 != id2
        assert id2 != id3
        assert "fluxograma" in id1
        assert "grafo" in id3

    def test_reset_counter(self, handler):
        """Reset deve reiniciar contador de IDs."""
        handler._generate_id("Teste")
        handler._generate_id("Teste")
        handler.reset()
        id_after_reset = handler._generate_id("Teste")

        assert "1" in id_after_reset

    def test_extract_title_from_subgraph(self, handler):
        """Deve extrair título de subgraph."""
        content = '''flowchart TD
    subgraph ENTRADA["PORTAS DE ENTRADA"]
        A[Demanda]
    end'''
        title = handler._extract_title_from_subgraph(content)
        assert title == "PORTAS DE ENTRADA"

    def test_extract_title_simple_subgraph(self, handler):
        """Deve extrair título de subgraph simples."""
        content = '''flowchart TD
    subgraph meu_grupo
        A[Node]
    end'''
        title = handler._extract_title_from_subgraph(content)
        assert title == "Meu Grupo"

    def test_process_single_mermaid_block(self, handler):
        """Deve processar bloco Mermaid único."""
        content = '''# Título

```mermaid
flowchart TD
    A --> B
```

Texto após diagrama.'''

        result = handler.process(content)

        assert '```mermaid' not in result
        assert '<div class="mermaid"' in result
        assert 'A --> B' in result
        assert '<figure class="diagram' in result

    def test_process_multiple_mermaid_blocks(self, handler):
        """Deve processar múltiplos blocos Mermaid."""
        content = '''```mermaid
flowchart TD
    A --> B
```

Texto entre diagramas.

```mermaid
graph LR
    C --> D
```'''

        result = handler.process(content)

        assert result.count('<div class="mermaid"') == 2
        assert 'A --> B' in result
        assert 'C --> D' in result

    def test_extract_diagrams(self, handler):
        """Deve extrair lista de diagramas."""
        content = '''```mermaid
flowchart TD
    A --> B
```

```mermaid
sequenceDiagram
    Alice->>Bob: Hi
```'''

        diagrams = handler.extract_diagrams(content)

        assert len(diagrams) == 2
        assert diagrams[0].diagram_type == "Fluxograma"
        assert diagrams[1].diagram_type == "Diagrama de Sequência"

    def test_no_mermaid_blocks(self, handler):
        """Deve retornar conteúdo inalterado sem blocos Mermaid."""
        content = "# Título\n\nApenas texto sem diagramas."
        result = handler.process(content)

        assert result == content

    def test_noscript_fallback_added(self, handler):
        """Deve adicionar fallback noscript."""
        content = '''```mermaid
flowchart TD
    A --> B
```'''

        result = handler.process(content)

        assert '<noscript>' in result
        assert 'requer JavaScript' in result


class TestMermaidDiagram:
    """Testes para a dataclass MermaidDiagram."""

    def test_create_diagram(self):
        """Deve criar diagrama com todos os campos."""
        diagram = MermaidDiagram(
            id="diagram-1",
            content="flowchart TD\n    A --> B",
            diagram_type="Fluxograma",
            caption="Meu fluxo"
        )

        assert diagram.id == "diagram-1"
        assert diagram.diagram_type == "Fluxograma"
        assert diagram.caption == "Meu fluxo"

    def test_diagram_optional_caption(self):
        """Caption deve ser opcional."""
        diagram = MermaidDiagram(
            id="diagram-2",
            content="graph LR",
            diagram_type="Grafo"
        )

        assert diagram.caption is None


# =============================================================================
# Testes do TableEnhancer
# =============================================================================


class TestTableEnhancer:
    """Testes para o aprimorador de tabelas."""

    @pytest.fixture
    def enhancer(self):
        """Cria instância do enhancer para testes."""
        return TableEnhancer(add_wrapper=True, add_risk_labels=True)

    def test_detect_risk_level_color_names(self, enhancer):
        """Deve detectar níveis de risco por nome de cor."""
        assert enhancer._detect_risk_level("VERMELHO") == RiskLevel.VERMELHO
        assert enhancer._detect_risk_level("Laranja") == RiskLevel.LARANJA
        assert enhancer._detect_risk_level("amarelo") == RiskLevel.AMARELO
        assert enhancer._detect_risk_level("Verde") == RiskLevel.VERDE
        assert enhancer._detect_risk_level("Azul") == RiskLevel.AZUL

    def test_detect_risk_level_priority_codes(self, enhancer):
        """Deve detectar níveis por códigos de prioridade (P1, P2, etc)."""
        assert enhancer._detect_risk_level("P1 - Urgente") == RiskLevel.VERMELHO
        assert enhancer._detect_risk_level("P2") == RiskLevel.LARANJA
        assert enhancer._detect_risk_level("P3") == RiskLevel.AMARELO
        assert enhancer._detect_risk_level("P4") == RiskLevel.VERDE

    def test_detect_risk_level_keywords(self, enhancer):
        """Deve detectar níveis por palavras-chave."""
        assert enhancer._detect_risk_level("Urgência imediata") == RiskLevel.VERMELHO
        assert enhancer._detect_risk_level("Risco alto") == RiskLevel.LARANJA
        assert enhancer._detect_risk_level("Moderado") == RiskLevel.AMARELO
        assert enhancer._detect_risk_level("Baixo risco") == RiskLevel.VERDE
        assert enhancer._detect_risk_level("Eletivo") == RiskLevel.AZUL

    def test_detect_risk_level_not_found(self, enhancer):
        """Deve retornar None quando não detectar risco."""
        assert enhancer._detect_risk_level("Texto qualquer") is None
        assert enhancer._detect_risk_level("123") is None

    def test_clean_html(self, enhancer):
        """Deve limpar tags HTML e normalizar texto."""
        result = enhancer._clean_html("<strong>Texto</strong> com  espaços")
        assert result == "texto com espaços"

    def test_analyze_table_headers_risk_table(self, enhancer):
        """Deve detectar tabela de risco pelo cabeçalho."""
        thead = '''<tr>
            <th>Cor</th>
            <th>Descrição</th>
            <th>Prazo</th>
        </tr>'''

        info = enhancer._analyze_table_headers(thead)

        assert info.is_risk_table is True
        assert info.color_column_index == 0

    def test_analyze_table_headers_regular_table(self, enhancer):
        """Deve identificar tabela comum (sem risco)."""
        thead = '''<tr>
            <th>Nome</th>
            <th>Idade</th>
            <th>Cidade</th>
        </tr>'''

        info = enhancer._analyze_table_headers(thead)

        assert info.is_risk_table is False
        assert info.color_column_index is None

    def test_enhance_adds_wrapper(self, enhancer):
        """Deve adicionar wrapper responsivo às tabelas."""
        html = '<table><tr><td>Célula</td></tr></table>'
        result = enhancer.enhance(html)

        assert '<div class="table-wrapper">' in result

    def test_enhance_no_wrapper(self):
        """Deve respeitar configuração sem wrapper."""
        enhancer = TableEnhancer(add_wrapper=False)
        html = '<table><tr><td>Célula</td></tr></table>'
        result = enhancer.enhance(html)

        assert '<div class="table-wrapper">' not in result

    def test_enhance_risk_table_adds_data_attribute(self, enhancer):
        """Deve adicionar data-risco às linhas de tabela de risco."""
        html = '''<table>
            <thead><tr><th>Cor</th><th>Ação</th></tr></thead>
            <tbody>
                <tr><td>VERMELHO</td><td>Urgente</td></tr>
                <tr><td>VERDE</td><td>Eletivo</td></tr>
            </tbody>
        </table>'''

        result = enhancer.enhance(html)

        assert 'data-risco="vermelho"' in result
        assert 'data-risco="verde"' in result

    def test_enhance_regular_table_no_data_risco(self, enhancer):
        """Tabelas comuns não devem ter data-risco."""
        html = '''<table>
            <thead><tr><th>Nome</th><th>Valor</th></tr></thead>
            <tbody>
                <tr><td>Item 1</td><td>100</td></tr>
            </tbody>
        </table>'''

        result = enhancer.enhance(html)

        assert 'data-risco=' not in result

    def test_detect_risk_tables(self, enhancer):
        """Deve listar tabelas de risco encontradas."""
        html = '''
        <table>
            <thead><tr><th>Prioridade</th><th>Descrição</th></tr></thead>
            <tbody>
                <tr><td>P1</td><td>Crítico</td></tr>
                <tr><td>P2</td><td>Alto</td></tr>
                <tr><td>P3</td><td>Médio</td></tr>
            </tbody>
        </table>
        <table>
            <thead><tr><th>Nome</th></tr></thead>
            <tbody><tr><td>Item</td></tr></tbody>
        </table>
        '''

        risk_tables = enhancer.detect_risk_tables(html)

        assert len(risk_tables) == 1
        assert risk_tables[0]['index'] == 0

    def test_enhance_preserves_content(self, enhancer):
        """Deve preservar conteúdo original das células."""
        html = '''<table>
            <thead><tr><th>Classificação</th><th>Descrição Detalhada</th></tr></thead>
            <tbody>
                <tr><td>Moderado</td><td>Acompanhamento ambulatorial em 30 dias</td></tr>
            </tbody>
        </table>'''

        result = enhancer.enhance(html)

        assert 'Acompanhamento ambulatorial em 30 dias' in result


class TestRiskLevel:
    """Testes para o enum RiskLevel."""

    def test_all_risk_levels_exist(self):
        """Deve ter todos os níveis de risco esperados."""
        expected = ['vermelho', 'laranja', 'amarelo', 'verde', 'azul']

        for level_name in expected:
            assert hasattr(RiskLevel, level_name.upper())

    def test_risk_level_values(self):
        """Valores devem ser strings lowercase."""
        assert RiskLevel.VERMELHO.value == "vermelho"
        assert RiskLevel.LARANJA.value == "laranja"


class TestTableInfo:
    """Testes para a dataclass TableInfo."""

    def test_default_values(self):
        """Deve ter valores padrão corretos."""
        info = TableInfo()

        assert info.is_risk_table is False
        assert info.color_column_index is None
        assert info.priority_column_index is None

    def test_create_with_values(self):
        """Deve criar com valores personalizados."""
        info = TableInfo(
            is_risk_table=True,
            color_column_index=2,
            priority_column_index=0
        )

        assert info.is_risk_table is True
        assert info.color_column_index == 2
        assert info.priority_column_index == 0


# =============================================================================
# Testes de Integração
# =============================================================================


class TestIntegration:
    """Testes de integração entre componentes."""

    def test_full_pipeline_mermaid_and_tables(self):
        """Deve processar documento com Mermaid e tabelas de risco."""
        from src.html_renderer.parsers.mermaid_handler import MermaidHandler
        from src.html_renderer.parsers.table_enhancer import TableEnhancer

        content = '''# Protocolo de Classificação de Risco

```mermaid
flowchart TD
    A[Paciente] --> B{Triagem}
    B -->|Vermelho| C[Urgência]
    B -->|Verde| D[Ambulatório]
```

## Tabela de Prioridades

<table>
    <thead><tr><th>Cor</th><th>Prazo</th></tr></thead>
    <tbody>
        <tr><td>VERMELHO</td><td>Imediato</td></tr>
        <tr><td>VERDE</td><td>30 dias</td></tr>
    </tbody>
</table>
'''

        # Processa Mermaid
        mermaid_handler = MermaidHandler()
        content = mermaid_handler.process(content)

        # Processa tabelas
        table_enhancer = TableEnhancer()
        content = table_enhancer.enhance(content)

        # Verifica Mermaid processado
        assert '<div class="mermaid"' in content
        assert '```mermaid' not in content

        # Verifica tabelas processadas
        assert 'data-risco="vermelho"' in content
        assert 'data-risco="verde"' in content
        assert '<div class="table-wrapper">' in content

    def test_empty_content_handled_gracefully(self):
        """Deve lidar com conteúdo vazio."""
        mermaid_handler = MermaidHandler()
        table_enhancer = TableEnhancer()

        result = mermaid_handler.process("")
        result = table_enhancer.enhance(result)

        assert result == ""

    def test_content_without_special_elements(self):
        """Deve preservar conteúdo sem elementos especiais."""
        content = "# Título\n\nApenas texto markdown."

        mermaid_handler = MermaidHandler()
        table_enhancer = TableEnhancer()

        result = mermaid_handler.process(content)
        result = table_enhancer.enhance(result)

        assert result == content
