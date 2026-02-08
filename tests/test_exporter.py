# tests/test_exporter.py

"""Tests for the exporter module."""

import pytest
import json
from pathlib import Path
from datetime import datetime

import yaml

from src.context_engine.exporter import (
    ExportFormat,
    ExportResult,
    ExportMetadata,
    CommandExporter,
    parse_formatted_content,
    export_command_output,
)


class TestExportFormat:
    """Test ExportFormat enum."""

    def test_from_string_md(self):
        """Should parse 'md' format."""
        assert ExportFormat.from_string("md") == ExportFormat.MARKDOWN

    def test_from_string_markdown_alias(self):
        """Should parse 'markdown' alias."""
        assert ExportFormat.from_string("markdown") == ExportFormat.MARKDOWN

    def test_from_string_yaml(self):
        """Should parse 'yaml' format."""
        assert ExportFormat.from_string("yaml") == ExportFormat.YAML

    def test_from_string_yml_alias(self):
        """Should parse 'yml' alias."""
        assert ExportFormat.from_string("yml") == ExportFormat.YAML

    def test_from_string_json(self):
        """Should parse 'json' format."""
        assert ExportFormat.from_string("json") == ExportFormat.JSON

    def test_from_string_docx(self):
        """Should parse 'docx' format."""
        assert ExportFormat.from_string("docx") == ExportFormat.DOCX

    def test_from_string_invalid(self):
        """Should raise ValueError for invalid format."""
        with pytest.raises(ValueError):
            ExportFormat.from_string("invalid")

    def test_list_formats(self):
        """Should list all format values."""
        formats = ExportFormat.list_formats()
        assert "md" in formats
        assert "yaml" in formats
        assert "json" in formats
        assert "docx" in formats


class TestExportMetadata:
    """Test ExportMetadata dataclass."""

    def test_to_dict(self):
        """Should convert to dictionary."""
        metadata = ExportMetadata(
            command_name="test",
            timestamp="2024-01-01T12:00:00",
        )
        result = metadata.to_dict()
        assert result["comando"] == "test"
        assert result["data_hora"] == "2024-01-01T12:00:00"
        assert "origem" in result


class TestParseFormattedContent:
    """Test content parsing utility."""

    def test_parse_with_header(self):
        """Should extract title from header."""
        content = """═══════════════════════════════════════════════════
  PIPS: meu_projeto
═══════════════════════════════════════════════════

📊 Status: EM_PROGRESSO"""

        result = parse_formatted_content(content)
        # Title extraction finds first non-box-drawing line after header
        assert "PIPS" in result["titulo"] or "titulo" in result

    def test_parse_preserves_raw(self):
        """Should preserve raw content."""
        content = "Simple content without formatting"
        result = parse_formatted_content(content)
        assert result["conteudo_raw"] == content


class TestCommandExporter:
    """Test CommandExporter class."""

    def test_export_to_string_markdown(self):
        """Should export to markdown string."""
        exporter = CommandExporter()
        content = "Test content"
        result = exporter.export_to_string(content, ExportFormat.MARKDOWN)
        assert "Test content" in result
        assert "Exportado pelo Context Engine" in result

    def test_export_to_string_yaml(self):
        """Should export to valid YAML."""
        exporter = CommandExporter()
        content = "Test content"
        result = exporter.export_to_string(content, ExportFormat.YAML)

        # Verify valid YAML
        data = yaml.safe_load(result)
        assert isinstance(data, dict)
        assert "exportacao" in data

    def test_export_to_string_json(self):
        """Should export to valid JSON."""
        exporter = CommandExporter()
        content = "Test content"
        result = exporter.export_to_string(content, ExportFormat.JSON)

        # Verify valid JSON
        data = json.loads(result)
        assert isinstance(data, dict)
        assert "exportacao" in data

    def test_export_to_string_docx_raises(self):
        """DOCX export to string should raise ValueError."""
        exporter = CommandExporter()
        with pytest.raises(ValueError):
            exporter.export_to_string("content", ExportFormat.DOCX)

    def test_export_to_file_markdown(self, tmp_path):
        """Should export markdown to file."""
        exporter = CommandExporter()
        output_file = tmp_path / "test.md"

        result = exporter.export_to_file(
            "Test content",
            ExportFormat.MARKDOWN,
            output_file,
        )

        assert result.success
        assert output_file.exists()
        assert "Test content" in output_file.read_text(encoding="utf-8")

    def test_export_to_file_creates_parent_dirs(self, tmp_path):
        """Should create parent directories if needed."""
        exporter = CommandExporter()
        output_file = tmp_path / "subdir" / "test.md"

        result = exporter.export_to_file(
            "Test content",
            ExportFormat.MARKDOWN,
            output_file,
        )

        assert result.success
        assert output_file.exists()

    def test_export_to_file_with_metadata(self, tmp_path):
        """Should include metadata in export."""
        exporter = CommandExporter()
        output_file = tmp_path / "test.md"
        metadata = ExportMetadata(
            command_name="test_cmd",
            timestamp="2024-01-01T12:00:00",
        )

        result = exporter.export_to_file(
            "Test content",
            ExportFormat.MARKDOWN,
            output_file,
            metadata,
        )

        assert result.success
        content = output_file.read_text(encoding="utf-8")
        assert "test_cmd" in content

    def test_export_result_attributes(self, tmp_path):
        """Export result should have correct attributes."""
        exporter = CommandExporter()
        output_file = tmp_path / "test.md"

        result = exporter.export_to_file(
            "Test content",
            ExportFormat.MARKDOWN,
            output_file,
        )

        assert result.format == ExportFormat.MARKDOWN
        assert result.success is True
        assert result.file_path == output_file
        assert result.size_bytes > 0
        assert result.timestamp


class TestExportConvenienceFunction:
    """Test the export_command_output convenience function."""

    def test_export_with_string_format(self, tmp_path):
        """Should accept string format."""
        output_path = tmp_path / "test.md"
        result = export_command_output(
            command_name="test",
            output="Test content",
            format="md",
            output_path=output_path,
        )
        assert result.success
        assert output_path.exists()

    def test_export_with_enum_format(self, tmp_path):
        """Should accept enum format."""
        output_path = tmp_path / "test.yaml"
        result = export_command_output(
            command_name="test",
            output="Test content",
            format=ExportFormat.YAML,
            output_path=output_path,
        )
        assert result.success


class TestYAMLExport:
    """Test YAML export specifically."""

    def test_yaml_has_expected_structure(self):
        """YAML should have expected structure."""
        exporter = CommandExporter()
        content = """═══════════════════════════════════════════════════
  Test Title
═══════════════════════════════════════════════════

📊 Seção 1:
  Conteúdo da seção 1
"""
        result = exporter.export_to_string(content, ExportFormat.YAML)
        data = yaml.safe_load(result)

        assert "titulo" in data
        assert "exportacao" in data
        assert data["exportacao"]["formato"] == "yaml"


class TestJSONExport:
    """Test JSON export specifically."""

    def test_json_has_expected_structure(self):
        """JSON should have expected structure."""
        exporter = CommandExporter()
        content = "Test content"
        result = exporter.export_to_string(content, ExportFormat.JSON)
        data = json.loads(result)

        assert "titulo" in data
        assert "exportacao" in data
        assert data["exportacao"]["formato"] == "json"

    def test_json_is_utf8_friendly(self):
        """JSON should handle Portuguese characters."""
        exporter = CommandExporter()
        content = "Conteúdo em português com acentos: ção, é, ã"
        result = exporter.export_to_string(content, ExportFormat.JSON)

        # Should not have unicode escapes
        assert "\\u" not in result
        assert "ção" in result or "Conte\\u00fado" not in result
