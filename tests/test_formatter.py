# tests/test_formatter.py

"""Tests for the formatter module."""

import pytest
from datetime import datetime
from unittest.mock import Mock

from src.context_engine.formatter import (
    format_header,
    format_separator,
    format_section,
    get_status_emoji,
    truncate_text,
    format_number,
    format_percentage,
    format_template_output,
    format_auditoria_output,
    format_export_success,
    format_export_help,
    STATUS_EMOJI,
    BOX_WIDTH,
    HEADER_CHAR,
    SEPARATOR_CHAR,
)


class TestConstants:
    """Test formatting constants."""

    def test_box_width_is_51(self):
        """Box width should be 51 characters."""
        assert BOX_WIDTH == 51

    def test_header_char_is_double_line(self):
        """Header character should be double line."""
        assert HEADER_CHAR == "═"

    def test_separator_char_is_single_line(self):
        """Separator character should be single line."""
        assert SEPARATOR_CHAR == "─"

    def test_status_emoji_has_all_statuses(self):
        """Status emoji dict should have all required statuses."""
        required = [
            "nao_iniciado",
            "em_progresso",
            "pausado",
            "validando",
            "concluido",
            "erro",
        ]
        for status in required:
            assert status in STATUS_EMOJI


class TestBoxDrawing:
    """Test box-drawing utility functions."""

    def test_format_header_default_width(self):
        """Header should use default width."""
        result = format_header("TEST")
        lines = result.split("\n")
        assert len(lines) == 3
        assert lines[0] == "═" * 51
        assert "TEST" in lines[1]
        assert lines[2] == "═" * 51

    def test_format_header_custom_width(self):
        """Header should respect custom width."""
        result = format_header("TEST", width=30)
        lines = result.split("\n")
        assert lines[0] == "═" * 30
        assert lines[2] == "═" * 30

    def test_format_separator_default(self):
        """Separator should use default character and width."""
        result = format_separator()
        assert result == "─" * 51

    def test_format_separator_custom_char(self):
        """Separator should use custom character."""
        result = format_separator(char="=", width=20)
        assert result == "=" * 20


class TestStatusEmoji:
    """Test status emoji mapping."""

    def test_get_status_emoji_concluido(self):
        """Concluido status should return checkmark."""
        assert get_status_emoji("concluido") == "✅"

    def test_get_status_emoji_erro(self):
        """Erro status should return X."""
        assert get_status_emoji("erro") == "❌"

    def test_get_status_emoji_em_progresso(self):
        """Em progresso status should return play button."""
        assert get_status_emoji("em_progresso") == "▶️"

    def test_get_status_emoji_unknown(self):
        """Unknown status should return question mark."""
        assert get_status_emoji("desconhecido") == "❓"


class TestTextUtilities:
    """Test text utility functions."""

    def test_truncate_text_within_limit(self):
        """Text within limit should not be truncated."""
        text = "short text"
        result = truncate_text(text, 50)
        assert result == text

    def test_truncate_text_over_limit(self):
        """Text over limit should be truncated with suffix."""
        text = "this is a very long text that should be truncated"
        result = truncate_text(text, 20)
        assert len(result) == 23  # 20 chars + "..."
        assert result.endswith("...")

    def test_truncate_text_custom_suffix(self):
        """Truncation should use custom suffix."""
        text = "this is a long text"
        result = truncate_text(text, 10, suffix="[...]")
        assert result.endswith("[...]")

    def test_format_number_with_separator(self):
        """Numbers should be formatted with thousand separators."""
        assert format_number(1000) == "1,000"
        assert format_number(1000000) == "1,000,000"

    def test_format_percentage(self):
        """Percentages should be formatted correctly."""
        assert format_percentage(45.678) == "45.7%"
        assert format_percentage(100.0) == "100.0%"


class TestCommandFormatters:
    """Test command-specific formatters."""

    def test_format_template_output_basic(self):
        """Template output should have header and content."""
        result = format_template_output("CLI_02", None)
        assert "TEMPLATE: CLI_02" in result
        assert "═" * 51 in result

    def test_format_template_output_with_data(self):
        """Template output should include data when provided."""
        data = {"tipo": "TEA", "arquivo": "test.md"}
        result = format_template_output("CLI_02", data)
        assert "CLI_02" in result
        assert "TEA" in result

    def test_format_auditoria_output_basic(self):
        """Auditoria output should have header."""
        result = format_auditoria_output("registro_teste", None)
        assert "AUDITORIA: registro_teste" in result

    def test_format_export_success(self):
        """Export success should show format, path, and size."""
        result = format_export_success("md", "/path/to/file.md", 1234)
        assert "Exportado com sucesso" in result
        assert "MD" in result
        assert "/path/to/file.md" in result
        assert "1,234" in result

    def test_format_export_help(self):
        """Export help should list all formats."""
        result = format_export_help()
        assert "md" in result
        assert "yaml" in result
        assert "json" in result
        assert "docx" in result


class TestSection:
    """Test section formatting."""

    def test_format_section_basic(self):
        """Section should format title and content."""
        result = format_section("Title", "Content")
        assert "Title:" in result
        assert "Content" in result

    def test_format_section_with_emoji(self):
        """Section should include emoji when provided."""
        result = format_section("Title", "Content", emoji="📊")
        assert "📊" in result
        assert "Title:" in result
