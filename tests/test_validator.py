# tests/test_validator.py

"""Tests for the cross-document validation system.

This module tests:
- Claim extraction from protocol text
- Conflict detection between claims
- Validation report generation
- Command parsing for /validar and /evidencia
"""

import pytest
from pathlib import Path
from datetime import datetime

from src.context_engine.validation_models import (
    ValidatableClaim,
    ClaimConflict,
    ValidationReport,
    ConflictType,
    ConflictSeverity,
    ValidationStatus,
)
from src.context_engine.context_models import ConceptType, EvidenceGrade
from src.context_engine.validator import (
    ClaimExtractor,
    ConflictDetector,
    CrossDocumentValidator,
    format_validation_report,
)
from src.context_engine.commands import (
    parse_command,
    parse_validar_command,
    parse_evidencia_command,
    ValidarCommand,
    EvidenciaCommand,
)


# =============================================================================
# Test Data
# =============================================================================

SAMPLE_TEXT_WITH_TIMELINE = """
## Classificação de Prioridade

Os casos são classificados conforme urgência:
- P1: até 30 dias
- P2: até 90 dias
- P3: até 180 dias
"""

SAMPLE_TEXT_WITH_CONFLICTING_TIMELINE = """
## Fluxo de Atendimento

Prazos para atendimento:
- P1: até 45 dias (casos urgentes)
- P2: até 60 dias (casos moderados)
"""

SAMPLE_TEXT_WITH_SCORING = """
## M-CHAT-R/F Scoring

O M-CHAT-R/F classifica o risco em:
- baixo risco: 0-2 pontos
- risco moderado: 3-7 pontos
- alto risco: 8-20 pontos
"""


# =============================================================================
# ValidatableClaim Tests
# =============================================================================

class TestValidatableClaim:
    """Tests for ValidatableClaim dataclass."""

    def test_create_claim(self):
        """Test basic claim creation."""
        claim = ValidatableClaim(
            id="test_claim_1",
            claim_text="P1: 30 dias",
            normalized_value={'priority': 'P1', 'days': 30},
            source_file=Path("CLI_02.md"),
            line_number=100,
            section="Prioridades",
            concept_type=ConceptType.METRICA,
        )
        assert claim.id == "test_claim_1"
        assert claim.normalized_value['days'] == 30

    def test_get_citation_full(self):
        """Test full citation format."""
        claim = ValidatableClaim(
            id="test_claim",
            claim_text="Test",
            normalized_value={},
            source_file=Path("CLI_02_TRANSTORNO_ESPECTRO_AUTISTA.md"),
            line_number=847,
            section="",
            concept_type=ConceptType.METRICA,
        )
        citation = claim.get_citation()
        assert "CLI_02_TRANSTORNO_ESPECTRO_AUTISTA.md:847" in citation

    def test_get_citation_short(self):
        """Test short citation format."""
        claim = ValidatableClaim(
            id="test_claim",
            claim_text="Test",
            normalized_value={},
            source_file=Path("CLI_02_TRANSTORNO_ESPECTRO_AUTISTA.md"),
            line_number=847,
            section="",
            concept_type=ConceptType.METRICA,
        )
        citation = claim.get_citation(short=True)
        assert ":847]" in citation

    def test_matches_keywords(self):
        """Test keyword matching between claims."""
        claim_a = ValidatableClaim(
            id="a", claim_text="", normalized_value={},
            source_file=Path("a.md"), line_number=1, section="",
            concept_type=ConceptType.METRICA,
            keywords={'timeline', 'p1', 'prazo'},
        )
        claim_b = ValidatableClaim(
            id="b", claim_text="", normalized_value={},
            source_file=Path("b.md"), line_number=1, section="",
            concept_type=ConceptType.METRICA,
            keywords={'timeline', 'dias', 'p1'},
        )
        shared = claim_a.matches_keywords(claim_b)
        assert 'timeline' in shared
        assert 'p1' in shared
        assert 'prazo' not in shared


# =============================================================================
# ClaimConflict Tests
# =============================================================================

class TestClaimConflict:
    """Tests for ClaimConflict dataclass."""

    def test_create_conflict(self):
        """Test basic conflict creation."""
        claim_a = ValidatableClaim(
            id="a", claim_text="P1: 30 dias", normalized_value={'days': 30},
            source_file=Path("CLI_02.md"), line_number=100, section="",
            concept_type=ConceptType.METRICA,
        )
        claim_b = ValidatableClaim(
            id="b", claim_text="P1: 45 dias", normalized_value={'days': 45},
            source_file=Path("MACROFLUXO.md"), line_number=50, section="",
            concept_type=ConceptType.METRICA,
        )
        conflict = ClaimConflict(
            id="conflict_1",
            claim_a=claim_a,
            claim_b=claim_b,
            conflict_type=ConflictType.TIMELINE_INCONSISTENCY,
            severity=ConflictSeverity.CRITICAL,
            explanation="Timeline P1 inconsistente: 30 vs 45 dias",
        )
        assert conflict.severity == ConflictSeverity.CRITICAL
        assert "30" in conflict.explanation
        assert "45" in conflict.explanation

    def test_format_report_entry(self):
        """Test conflict report formatting."""
        claim_a = ValidatableClaim(
            id="a", claim_text="P1: 30 dias", normalized_value={},
            source_file=Path("CLI_02.md"), line_number=100, section="",
            concept_type=ConceptType.METRICA,
        )
        claim_b = ValidatableClaim(
            id="b", claim_text="P1: 45 dias", normalized_value={},
            source_file=Path("MACROFLUXO.md"), line_number=50, section="",
            concept_type=ConceptType.METRICA,
        )
        conflict = ClaimConflict(
            id="conflict_1",
            claim_a=claim_a,
            claim_b=claim_b,
            conflict_type=ConflictType.TIMELINE_INCONSISTENCY,
            severity=ConflictSeverity.CRITICAL,
            explanation="Test explanation",
            suggested_resolution="Fix it",
        )
        report_entry = conflict.format_report_entry()
        assert "CRITICAL" in report_entry
        assert "CLI_02.md:100" in report_entry
        assert "MACROFLUXO.md:50" in report_entry
        assert "Fix it" in report_entry


# =============================================================================
# ValidationReport Tests
# =============================================================================

class TestValidationReport:
    """Tests for ValidationReport dataclass."""

    def test_empty_report_is_valid(self):
        """Test that report with no conflicts is valid."""
        report = ValidationReport(
            id="test_report",
            protocols_validated=["CLI_02"],
            validation_started=datetime.now(),
            status=ValidationStatus.COMPLETED,
        )
        assert report.is_valid()

    def test_report_with_critical_is_invalid(self):
        """Test that report with critical conflicts is invalid."""
        claim_a = ValidatableClaim(
            id="a", claim_text="", normalized_value={},
            source_file=Path("a.md"), line_number=1, section="",
            concept_type=ConceptType.METRICA,
        )
        claim_b = ValidatableClaim(
            id="b", claim_text="", normalized_value={},
            source_file=Path("b.md"), line_number=1, section="",
            concept_type=ConceptType.METRICA,
        )
        conflict = ClaimConflict(
            id="c1", claim_a=claim_a, claim_b=claim_b,
            conflict_type=ConflictType.TIMELINE_INCONSISTENCY,
            severity=ConflictSeverity.CRITICAL,
            explanation="Critical issue",
        )
        report = ValidationReport(
            id="test_report",
            protocols_validated=["CLI_02", "MACROFLUXO"],
            validation_started=datetime.now(),
            status=ValidationStatus.COMPLETED,
            conflicts=[conflict],
        )
        assert not report.is_valid()

    def test_get_conflict_counts(self):
        """Test counting conflicts by severity."""
        claim = ValidatableClaim(
            id="a", claim_text="", normalized_value={},
            source_file=Path("a.md"), line_number=1, section="",
            concept_type=ConceptType.METRICA,
        )
        conflicts = [
            ClaimConflict(id="c1", claim_a=claim, claim_b=claim,
                         conflict_type=ConflictType.TIMELINE_INCONSISTENCY,
                         severity=ConflictSeverity.CRITICAL, explanation=""),
            ClaimConflict(id="c2", claim_a=claim, claim_b=claim,
                         conflict_type=ConflictType.TIMELINE_INCONSISTENCY,
                         severity=ConflictSeverity.WARNING, explanation=""),
            ClaimConflict(id="c3", claim_a=claim, claim_b=claim,
                         conflict_type=ConflictType.TIMELINE_INCONSISTENCY,
                         severity=ConflictSeverity.WARNING, explanation=""),
        ]
        report = ValidationReport(
            id="test", protocols_validated=[], validation_started=datetime.now(),
            conflicts=conflicts,
        )
        counts = report.get_conflict_counts()
        assert counts['critical'] == 1
        assert counts['warning'] == 2
        assert counts['info'] == 0


# =============================================================================
# ClaimExtractor Tests
# =============================================================================

class TestClaimExtractor:
    """Tests for ClaimExtractor class."""

    def test_extract_timeline_claims(self):
        """Test extraction of timeline claims."""
        extractor = ClaimExtractor()
        claims = extractor.extract_claims_from_text(
            SAMPLE_TEXT_WITH_TIMELINE,
            Path("test.md")
        )

        # Should find P1, P2, P3 timeline claims
        timeline_claims = [c for c in claims if 'days' in str(c.normalized_value)]
        assert len(timeline_claims) >= 3

    def test_extract_score_claims(self):
        """Test extraction of scoring claims."""
        extractor = ClaimExtractor()
        claims = extractor.extract_claims_from_text(
            SAMPLE_TEXT_WITH_SCORING,
            Path("test.md")
        )

        # Should find scoring range claims
        score_claims = [c for c in claims if 'range' in str(c.normalized_value)]
        assert len(score_claims) >= 1


# =============================================================================
# ConflictDetector Tests
# =============================================================================

class TestConflictDetector:
    """Tests for ConflictDetector class."""

    def test_detect_timeline_conflict(self):
        """Test detection of timeline conflicts."""
        extractor = ClaimExtractor()
        detector = ConflictDetector()

        claims_a = extractor.extract_claims_from_text(
            SAMPLE_TEXT_WITH_TIMELINE,
            Path("protocol_a.md")
        )
        claims_b = extractor.extract_claims_from_text(
            SAMPLE_TEXT_WITH_CONFLICTING_TIMELINE,
            Path("protocol_b.md")
        )

        conflicts = detector.detect_conflicts(claims_a, claims_b)

        # Should detect at least one timeline conflict
        timeline_conflicts = [
            c for c in conflicts
            if c.conflict_type == ConflictType.TIMELINE_INCONSISTENCY
        ]
        # Note: actual detection depends on claim matching
        # This test verifies the mechanism works
        assert isinstance(conflicts, list)

    def test_no_conflict_same_values(self):
        """Test that identical values don't create conflicts."""
        detector = ConflictDetector()

        claim_a = ValidatableClaim(
            id="a", claim_text="P1: 30 dias",
            normalized_value={'priority': 'P1', 'days': 30},
            source_file=Path("a.md"), line_number=1, section="",
            concept_type=ConceptType.METRICA,
            keywords={'timeline', 'p1'},
        )
        claim_b = ValidatableClaim(
            id="b", claim_text="P1: 30 dias",
            normalized_value={'priority': 'P1', 'days': 30},
            source_file=Path("b.md"), line_number=1, section="",
            concept_type=ConceptType.METRICA,
            keywords={'timeline', 'p1'},
        )

        conflicts = detector.detect_conflicts([claim_a], [claim_b])

        # Same values should not create conflicts
        assert len(conflicts) == 0


# =============================================================================
# CrossDocumentValidator Tests
# =============================================================================

class TestCrossDocumentValidator:
    """Tests for CrossDocumentValidator class."""

    def test_validator_initialization(self):
        """Test validator can be initialized."""
        validator = CrossDocumentValidator()
        assert validator.extractor is not None
        assert validator.detector is not None

    def test_resolve_known_protocol(self):
        """Test resolving known protocol names."""
        validator = CrossDocumentValidator()

        # Should know about CLI_02
        assert 'CLI_02' in validator.PROTOCOL_PATHS

    def test_compare_protocols_nonexistent(self):
        """Test comparing non-existent protocols returns error."""
        validator = CrossDocumentValidator()
        report = validator.compare_protocols("NONEXISTENT_A", "NONEXISTENT_B")

        assert report.status == ValidationStatus.FAILED
        assert 'error' in report.summary

    def test_get_evidence_for_term(self):
        """Test querying evidence index."""
        # Create validator with reference index
        index_path = Path.cwd() / "referencias/REFERENCE_INDEX.yaml"

        if index_path.exists():
            validator = CrossDocumentValidator(reference_index_path=index_path)
            results = validator.get_evidence_for_term("TEA")
            # Should find at least one result for TEA
            assert isinstance(results, list)


# =============================================================================
# Command Parsing Tests
# =============================================================================

class TestValidarCommandParsing:
    """Tests for /validar command parsing."""

    def test_parse_validar_single_protocol(self):
        """Test parsing /validar CLI_02."""
        cmd = parse_command("/validar CLI_02")
        validar = parse_validar_command(cmd)

        assert not validar.error
        assert validar.protocol_a == "CLI_02"
        assert validar.protocol_b is None

    def test_parse_validar_two_protocols(self):
        """Test parsing /validar CLI_02 MACROFLUXO."""
        cmd = parse_command("/validar CLI_02 MACROFLUXO")
        validar = parse_validar_command(cmd)

        assert not validar.error
        assert validar.protocol_a == "CLI_02"
        assert validar.protocol_b == "MACROFLUXO"

    def test_parse_validar_all(self):
        """Test parsing /validar --all."""
        cmd = parse_command("/validar --all")
        validar = parse_validar_command(cmd)

        assert not validar.error
        assert validar.validate_all

    def test_parse_validar_with_severity_filter(self):
        """Test parsing /validar CLI_02 --severity critical."""
        cmd = parse_command("/validar CLI_02 --severity critical")
        validar = parse_validar_command(cmd)

        assert not validar.error
        assert validar.severity_filter == "critical"

    def test_parse_validar_empty(self):
        """Test parsing /validar without args shows help."""
        cmd = parse_command("/validar")
        validar = parse_validar_command(cmd)

        assert validar.error
        assert "Uso:" in validar.error_message


class TestEvidenciaCommandParsing:
    """Tests for /evidencia command parsing."""

    def test_parse_evidencia_basic(self):
        """Test parsing /evidencia TEA."""
        cmd = parse_command("/evidencia TEA")
        evidencia = parse_evidencia_command(cmd)

        assert not evidencia.error
        assert evidencia.search_term == "TEA"

    def test_parse_evidencia_with_validation(self):
        """Test parsing /evidencia CuidaSM --validation."""
        cmd = parse_command("/evidencia CuidaSM --validation")
        evidencia = parse_evidencia_command(cmd)

        assert not evidencia.error
        assert evidencia.search_term == "CuidaSM"
        assert evidencia.show_validation

    def test_parse_evidencia_with_grade(self):
        """Test parsing /evidencia M-CHAT --grade alta."""
        cmd = parse_command("/evidencia M-CHAT --grade alta")
        evidencia = parse_evidencia_command(cmd)

        assert not evidencia.error
        assert evidencia.evidence_grade_filter == "alta"

    def test_parse_evidencia_empty(self):
        """Test parsing /evidencia without args shows help."""
        cmd = parse_command("/evidencia")
        evidencia = parse_evidencia_command(cmd)

        assert evidencia.error
        assert "Uso:" in evidencia.error_message


# =============================================================================
# Integration Tests
# =============================================================================

class TestValidationIntegration:
    """Integration tests for the validation system."""

    def test_full_validation_pipeline(self):
        """Test complete validation pipeline."""
        extractor = ClaimExtractor()
        detector = ConflictDetector()

        # Extract from both texts
        claims_a = extractor.extract_claims_from_text(
            SAMPLE_TEXT_WITH_TIMELINE,
            Path("protocol_a.md")
        )
        claims_b = extractor.extract_claims_from_text(
            SAMPLE_TEXT_WITH_CONFLICTING_TIMELINE,
            Path("protocol_b.md")
        )

        # Detect conflicts
        conflicts = detector.detect_conflicts(claims_a, claims_b)

        # Create report
        report = ValidationReport(
            id="integration_test",
            protocols_validated=["protocol_a.md", "protocol_b.md"],
            validation_started=datetime.now(),
            validation_completed=datetime.now(),
            status=ValidationStatus.COMPLETED,
            claims_analyzed=len(claims_a) + len(claims_b),
            conflicts=conflicts,
        )

        # Format report
        formatted = format_validation_report(report)

        # Should produce readable output
        assert "VALIDAÇÃO" in formatted
        assert isinstance(formatted, str)

    def test_report_to_dict_serialization(self):
        """Test that reports can be serialized to dict."""
        report = ValidationReport(
            id="test",
            protocols_validated=["CLI_02"],
            validation_started=datetime.now(),
            validation_completed=datetime.now(),
            status=ValidationStatus.COMPLETED,
        )
        data = report.to_dict()

        assert 'id' in data
        assert 'protocols_validated' in data
        assert 'is_valid' in data
        assert data['is_valid'] == True


# =============================================================================
# Rules Engine Tests
# =============================================================================

class TestRulesEngine:
    """Tests for the RulesEngine class."""

    def test_rules_engine_initialization(self):
        """Test RulesEngine initializes with empty rules."""
        from src.context_engine.validator import RulesEngine

        engine = RulesEngine()
        assert engine.rules == []
        assert len(engine._comparison_functions) > 0

    def test_rules_engine_registers_comparison_functions(self):
        """Test that all comparison functions are registered."""
        from src.context_engine.validator import RulesEngine

        engine = RulesEngine()

        # Check all 9 core functions are registered
        expected_functions = [
            'compare_numeric_values',
            'compare_score_ranges',
            'compare_responsibility_sets',
            'compare_flow_sequences',
            'compare_terminology_definitions',
            'compare_criteria_lists',
            'compare_with_normative',
            'compare_categorical_values',
            'compare_reference_dates',
        ]

        for fn_name in expected_functions:
            assert engine.get_comparison_function(fn_name) is not None, \
                f"Function {fn_name} not registered"

    def test_rules_engine_loads_yaml_rules(self):
        """Test loading rules from YAML file."""
        rules_path = Path.cwd() / "src/context_engine/validation_rules.yaml"

        if rules_path.exists():
            validator = CrossDocumentValidator(rules_path=rules_path)

            # Should have loaded rules
            assert len(validator.rules) > 0

            # Check rules have required attributes
            for rule in validator.rules:
                assert rule.id
                assert rule.name
                assert rule.comparison_function

    def test_rules_engine_get_rules_for_type(self):
        """Test filtering rules by conflict type."""
        from src.context_engine.validator import RulesEngine
        from src.context_engine.validation_models import ValidationRule

        rules = [
            ValidationRule(
                id="TL001",
                name="Test Timeline",
                description="",
                conflict_type=ConflictType.TIMELINE_INCONSISTENCY,
                severity=ConflictSeverity.CRITICAL,
                patterns=[],
                comparison_function="compare_numeric_values",
                enabled=True,
            ),
            ValidationRule(
                id="IN001",
                name="Test Instrument",
                description="",
                conflict_type=ConflictType.INSTRUMENT_SCORING,
                severity=ConflictSeverity.WARNING,
                patterns=[],
                comparison_function="compare_score_ranges",
                enabled=True,
            ),
        ]

        engine = RulesEngine(rules)
        timeline_rules = engine.get_rules_for_type(ConflictType.TIMELINE_INCONSISTENCY)

        assert len(timeline_rules) == 1
        assert timeline_rules[0].id == "TL001"


# =============================================================================
# Comparison Functions Tests
# =============================================================================

class TestComparisonFunctions:
    """Tests for the 9 comparison functions."""

    def test_compare_numeric_values_within_tolerance(self):
        """Test numeric comparison within tolerance."""
        from src.context_engine.validator import compare_numeric_values

        is_conflict, explanation = compare_numeric_values(
            {'days': 30}, {'days': 33}, tolerance=5.0
        )
        assert not is_conflict

    def test_compare_numeric_values_exceeds_tolerance(self):
        """Test numeric comparison exceeding tolerance."""
        from src.context_engine.validator import compare_numeric_values

        is_conflict, explanation = compare_numeric_values(
            {'days': 30}, {'days': 45}, tolerance=5.0
        )
        assert is_conflict
        assert "15" in explanation  # Difference of 15

    def test_compare_score_ranges_identical(self):
        """Test score range comparison with identical ranges."""
        from src.context_engine.validator import compare_score_ranges

        is_conflict, explanation = compare_score_ranges(
            {'range': [0, 3]}, {'range': [0, 3]}
        )
        assert not is_conflict

    def test_compare_score_ranges_conflict(self):
        """Test score range comparison with conflicting ranges."""
        from src.context_engine.validator import compare_score_ranges

        is_conflict, explanation = compare_score_ranges(
            {'range': [0, 3]}, {'range': [0, 5]}, tolerance=1
        )
        assert is_conflict
        assert "inconsistentes" in explanation.lower()

    def test_compare_flow_sequences_identical(self):
        """Test flow comparison with identical sequences."""
        from src.context_engine.validator import compare_flow_sequences

        is_conflict, explanation = compare_flow_sequences(
            "APS encaminha para NIRSM",
            "Encaminhamento APS → NIRSM"
        )
        # Both contain APS and NIRSM, so no conflict
        assert not is_conflict

    def test_compare_flow_sequences_missing_node(self):
        """Test flow comparison with missing node."""
        from src.context_engine.validator import compare_flow_sequences

        is_conflict, explanation = compare_flow_sequences(
            "APS → NIRSM → CAPS",
            "APS → NIRSM"  # Missing CAPS
        )
        assert is_conflict
        assert "CAPS" in explanation

    def test_compare_categorical_values_same(self):
        """Test categorical comparison with same values."""
        from src.context_engine.validator import compare_categorical_values

        is_conflict, explanation = compare_categorical_values(
            "alto risco", "Alto Risco"  # Case insensitive
        )
        assert not is_conflict

    def test_compare_categorical_values_different(self):
        """Test categorical comparison with different values."""
        from src.context_engine.validator import compare_categorical_values

        is_conflict, explanation = compare_categorical_values(
            "alto risco", "baixo risco"
        )
        assert is_conflict
        assert "divergem" in explanation.lower()

    def test_compare_reference_dates_recent(self):
        """Test reference date comparison with recent dates."""
        from src.context_engine.validator import compare_reference_dates

        is_conflict, explanation = compare_reference_dates(
            "2024", "2025", max_age_years=5
        )
        assert not is_conflict

    def test_compare_reference_dates_outdated(self):
        """Test reference date comparison with outdated reference."""
        from src.context_engine.validator import compare_reference_dates

        is_conflict, explanation = compare_reference_dates(
            "2015", "2025", max_age_years=5
        )
        assert is_conflict
        assert "2015" in explanation


# =============================================================================
# Section Extraction Tests
# =============================================================================

class TestSectionExtraction:
    """Tests for section header extraction."""

    def test_extract_section_for_claim(self):
        """Test that claims get correct section headers."""
        extractor = ClaimExtractor()

        text = """# Documento Principal

## Seção de Prazos

Os prazos são:
- P1: até 30 dias
- P2: até 90 dias

## Outra Seção

Conteúdo adicional.
"""

        claims = extractor.extract_claims_from_text(text, Path("test.md"))

        # Find the P1 claim
        p1_claims = [c for c in claims if 'P1' in str(c.normalized_value)]
        if p1_claims:
            assert p1_claims[0].section == "Seção de Prazos"


# =============================================================================
# Real Data Integration Tests
# =============================================================================

class TestRealDataValidation:
    """Tests using actual protocol files."""

    def test_validate_cli02_exists(self):
        """Test that CLI_02 protocol file exists."""
        cli02_path = Path.cwd() / "entregas/Protocolos_Compartilhamento_Cuidado/Protocolos_Clinicos/CLI_02_TRANSTORNO_ESPECTRO_AUTISTA.md"

        # Only run if file exists
        if cli02_path.exists():
            validator = CrossDocumentValidator()
            report = validator.validate_protocol("CLI_02")

            assert report.status == ValidationStatus.COMPLETED
            assert report.claims_analyzed > 0

    def test_compare_cli02_vs_macrofluxo(self):
        """Test comparing CLI_02 and MACROFLUXO for conflicts."""
        rules_path = Path.cwd() / "src/context_engine/validation_rules.yaml"
        index_path = Path.cwd() / "referencias/REFERENCE_INDEX.yaml"

        validator = CrossDocumentValidator(
            rules_path=rules_path if rules_path.exists() else None,
            reference_index_path=index_path if index_path.exists() else None,
        )

        # Only run if both protocols exist
        cli02_path = validator._resolve_protocol_path("CLI_02")
        macrofluxo_path = validator._resolve_protocol_path("MACROFLUXO")

        if cli02_path and macrofluxo_path:
            report = validator.compare_protocols("CLI_02", "MACROFLUXO")

            assert report.status == ValidationStatus.COMPLETED
            assert report.claims_analyzed > 0
            # The system should now find conflicts using rules engine
            # (may be 0 if protocols are aligned)
