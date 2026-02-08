# src/context_engine/validator.py

"""Cross-document validation engine for clinical protocols.

This module implements the core validation logic for detecting conflicts
and inconsistencies between clinical protocols. It supports the /validar
command and evidence-backed protocol development.

Key Classes:
    RulesEngine: Executes validation rules from YAML configuration
    CrossDocumentValidator: Main validation engine
    ClaimExtractor: Extracts validatable claims from documents
    ConflictDetector: Detects conflicts between claims

Example:
    validator = CrossDocumentValidator()
    report = validator.compare_protocols("CLI_02", "MACROFLUXO")
    print(report.format_summary())
"""

import re
import uuid
from collections import defaultdict
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

import yaml

from .context_models import ConceptType, EvidenceGrade
from .validation_models import (
    ClaimConflict,
    ConflictSeverity,
    ConflictType,
    ValidatableClaim,
    ValidationReport,
    ValidationRule,
    ValidationStatus,
)


# =============================================================================
# Comparison Functions
# =============================================================================

def compare_numeric_values(
    value_a: Any,
    value_b: Any,
    tolerance: float = 5.0
) -> Tuple[bool, str]:
    """Compare numeric values with tolerance.

    Args:
        value_a: First value (can be dict with 'days' key or direct number)
        value_b: Second value
        tolerance: Maximum allowed difference

    Returns:
        Tuple of (is_conflict, explanation)
    """
    # Extract numeric values from various formats
    num_a = _extract_number(value_a)
    num_b = _extract_number(value_b)

    if num_a is None or num_b is None:
        return False, ""

    diff = abs(num_a - num_b)
    if diff > tolerance:
        return True, f"Diferença de {diff} excede tolerância de {tolerance}"
    return False, ""


def compare_score_ranges(
    range_a: Any,
    range_b: Any,
    tolerance: int = 1
) -> Tuple[bool, str]:
    """Compare scoring ranges for instruments.

    Args:
        range_a: First range (dict with 'range' key or [low, high] list)
        range_b: Second range
        tolerance: Maximum allowed boundary difference

    Returns:
        Tuple of (is_conflict, explanation)
    """
    r_a = _extract_range(range_a)
    r_b = _extract_range(range_b)

    if r_a is None or r_b is None:
        return False, ""

    # Compare boundaries
    low_diff = abs(r_a[0] - r_b[0])
    high_diff = abs(r_a[1] - r_b[1])

    if low_diff > tolerance or high_diff > tolerance:
        return True, f"Faixas inconsistentes: {r_a} vs {r_b}"
    return False, ""


def compare_responsibility_sets(
    roles_a: Any,
    roles_b: Any
) -> Tuple[bool, str]:
    """Compare responsibility assignments between documents.

    Args:
        roles_a: First responsibility claim
        roles_b: Second responsibility claim

    Returns:
        Tuple of (is_conflict, explanation)
    """
    text_a = _extract_text(roles_a)
    text_b = _extract_text(roles_b)

    if not text_a or not text_b:
        return False, ""

    # Normalize and tokenize responsibilities
    tokens_a = _tokenize_responsibilities(text_a)
    tokens_b = _tokenize_responsibilities(text_b)

    # Check for contradictions (same role, different responsibilities)
    role_a = _extract_role(roles_a)
    role_b = _extract_role(roles_b)

    if role_a and role_b and role_a.lower() == role_b.lower():
        # Same role - check if responsibilities are very different
        similarity = SequenceMatcher(None, tokens_a, tokens_b).ratio()
        if similarity < 0.5:
            return True, f"Atribuições do {role_a} divergem significativamente"

    return False, ""


def compare_flow_sequences(
    flow_a: Any,
    flow_b: Any
) -> Tuple[bool, str]:
    """Compare care flow sequences between documents.

    Args:
        flow_a: First flow description
        flow_b: Second flow description

    Returns:
        Tuple of (is_conflict, explanation)
    """
    text_a = _extract_text(flow_a)
    text_b = _extract_text(flow_b)

    if not text_a or not text_b:
        return False, ""

    # Extract flow nodes (APS, NIRSM, CAPS, etc.)
    nodes_a = _extract_flow_nodes(text_a)
    nodes_b = _extract_flow_nodes(text_b)

    # Check for missing or extra steps
    missing_in_b = nodes_a - nodes_b
    missing_in_a = nodes_b - nodes_a

    if missing_in_b or missing_in_a:
        explanation_parts = []
        if missing_in_b:
            explanation_parts.append(f"Ausentes no segundo: {missing_in_b}")
        if missing_in_a:
            explanation_parts.append(f"Ausentes no primeiro: {missing_in_a}")
        return True, "; ".join(explanation_parts)

    return False, ""


def compare_terminology_definitions(
    def_a: Any,
    def_b: Any
) -> Tuple[bool, str]:
    """Compare terminology definitions for drift.

    Args:
        def_a: First definition
        def_b: Second definition

    Returns:
        Tuple of (is_conflict, explanation)
    """
    text_a = _extract_text(def_a)
    text_b = _extract_text(def_b)

    if not text_a or not text_b:
        return False, ""

    # Calculate semantic similarity (simplified)
    similarity = SequenceMatcher(None, text_a.lower(), text_b.lower()).ratio()

    if similarity < 0.6:
        return True, f"Definições divergem (similaridade: {similarity:.0%})"

    return False, ""


def compare_criteria_lists(
    criteria_a: Any,
    criteria_b: Any
) -> Tuple[bool, str]:
    """Compare diagnostic criteria lists.

    Args:
        criteria_a: First criteria set
        criteria_b: Second criteria set

    Returns:
        Tuple of (is_conflict, explanation)
    """
    text_a = _extract_text(criteria_a)
    text_b = _extract_text(criteria_b)

    if not text_a or not text_b:
        return False, ""

    # Extract numbered or bulleted criteria
    items_a = _extract_list_items(text_a)
    items_b = _extract_list_items(text_b)

    if len(items_a) != len(items_b):
        return True, f"Número de critérios difere: {len(items_a)} vs {len(items_b)}"

    return False, ""


def compare_with_normative(
    value: Any,
    normative_value: Any,
    tolerance: float = 0
) -> Tuple[bool, str]:
    """Compare value against normative reference.

    Args:
        value: Value to check
        normative_value: Expected normative value
        tolerance: Allowed deviation

    Returns:
        Tuple of (is_conflict, explanation)
    """
    num_val = _extract_number(value)
    num_norm = _extract_number(normative_value)

    if num_val is None or num_norm is None:
        return False, ""

    diff = abs(num_val - num_norm)
    if diff > tolerance:
        return True, f"Valor {num_val} difere da normativa {num_norm}"

    return False, ""


def compare_categorical_values(
    cat_a: Any,
    cat_b: Any,
    valid_categories: Set[str] = None
) -> Tuple[bool, str]:
    """Compare categorical assignments.

    Args:
        cat_a: First categorical value
        cat_b: Second categorical value
        valid_categories: Optional set of valid categories

    Returns:
        Tuple of (is_conflict, explanation)
    """
    text_a = _extract_text(cat_a).lower().strip()
    text_b = _extract_text(cat_b).lower().strip()

    if not text_a or not text_b:
        return False, ""

    # Direct comparison
    if text_a != text_b:
        return True, f"Categorias divergem: '{text_a}' vs '{text_b}'"

    return False, ""


def compare_reference_dates(
    date_a: Any,
    date_b: Any,
    max_age_years: int = 5
) -> Tuple[bool, str]:
    """Compare reference dates for currency.

    Args:
        date_a: First date/year
        date_b: Second date/year
        max_age_years: Maximum acceptable age

    Returns:
        Tuple of (is_conflict, explanation)
    """
    year_a = _extract_year(date_a)
    year_b = _extract_year(date_b)

    if year_a is None and year_b is None:
        return False, ""

    current_year = datetime.now().year

    # Check if either reference is outdated
    if year_a and (current_year - year_a) > max_age_years:
        return True, f"Referência de {year_a} pode estar desatualizada"
    if year_b and (current_year - year_b) > max_age_years:
        return True, f"Referência de {year_b} pode estar desatualizada"

    # Check if references are from different eras
    if year_a and year_b and abs(year_a - year_b) > max_age_years:
        return True, f"Referências de épocas diferentes: {year_a} vs {year_b}"

    return False, ""


# =============================================================================
# Helper Functions for Comparison
# =============================================================================

def _extract_number(value: Any) -> Optional[float]:
    """Extract a number from various value formats."""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, dict):
        for key in ['days', 'value', 'count', 'score']:
            if key in value:
                return float(value[key])
    if isinstance(value, str):
        match = re.search(r'(\d+(?:[.,]\d+)?)', value)
        if match:
            return float(match.group(1).replace(',', '.'))
    return None


def _extract_range(value: Any) -> Optional[Tuple[int, int]]:
    """Extract a numeric range from various formats."""
    if isinstance(value, (list, tuple)) and len(value) >= 2:
        return (int(value[0]), int(value[1]))
    if isinstance(value, dict):
        if 'range' in value:
            r = value['range']
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                return (int(r[0]), int(r[1]))
    if isinstance(value, str):
        match = re.search(r'(\d+)\s*[-–]\s*(\d+)', value)
        if match:
            return (int(match.group(1)), int(match.group(2)))
    return None


def _extract_text(value: Any) -> str:
    """Extract text from various value formats."""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        for key in ['text', 'responsibility', 'description', 'claim_text']:
            if key in value:
                return str(value[key])
    return str(value) if value else ""


def _extract_role(value: Any) -> Optional[str]:
    """Extract role name from responsibility value."""
    if isinstance(value, dict) and 'role' in value:
        return value['role']
    return None


def _tokenize_responsibilities(text: str) -> List[str]:
    """Tokenize responsibility text into comparable tokens."""
    # Remove common words and punctuation
    stopwords = {'deve', 'responsável', 'por', 'para', 'a', 'o', 'de', 'do', 'da'}
    words = re.findall(r'\b\w+\b', text.lower())
    return [w for w in words if w not in stopwords and len(w) > 2]


def _extract_flow_nodes(text: str) -> Set[str]:
    """Extract flow nodes from text."""
    nodes = set()
    patterns = ['APS', 'UBS', 'NIRSM', 'NIRSM-R', 'CAPS', 'CAPSi', 'NASF', 'eMulti']
    for pattern in patterns:
        if re.search(rf'\b{pattern}\b', text, re.IGNORECASE):
            nodes.add(pattern.upper())
    return nodes


def _extract_list_items(text: str) -> List[str]:
    """Extract numbered or bulleted list items."""
    items = []
    # Match numbered items (1., 2., etc.) or bullets (-, *, •)
    pattern = r'(?:(?:\d+[.)]\s*)|(?:[-*•]\s*))(.+?)(?=(?:\d+[.)]\s*)|(?:[-*•]\s*)|$)'
    for match in re.finditer(pattern, text, re.MULTILINE):
        items.append(match.group(1).strip())
    return items


def _extract_year(value: Any) -> Optional[int]:
    """Extract year from various formats."""
    if isinstance(value, int) and 1900 <= value <= 2100:
        return value
    text = str(value) if value else ""
    match = re.search(r'\b(19|20)\d{2}\b', text)
    if match:
        return int(match.group())
    return None


# =============================================================================
# Rules Engine
# =============================================================================

class RulesEngine:
    """Executes validation rules from YAML configuration.

    This class bridges the gap between YAML rule definitions and
    Python comparison functions.
    """

    def __init__(self, rules: List[ValidationRule] = None, rules_data: Dict[str, Any] = None):
        """Initialize the rules engine.

        Args:
            rules: List of ValidationRule objects
            rules_data: Raw YAML data for additional configuration
        """
        self.rules = rules or []
        self.rules_data = rules_data or {}
        self._comparison_functions = self._register_comparison_functions()

    def _register_comparison_functions(self) -> Dict[str, Callable]:
        """Register all comparison functions by name."""
        return {
            'compare_numeric_values': compare_numeric_values,
            'compare_score_ranges': compare_score_ranges,
            'compare_scoring_ranges': compare_score_ranges,  # Alias
            'compare_responsibility_sets': compare_responsibility_sets,
            'compare_flow_sequences': compare_flow_sequences,
            'compare_terminology_definitions': compare_terminology_definitions,
            'compare_terminology_contexts': compare_terminology_definitions,  # Alias
            'compare_terminology_usage': compare_terminology_definitions,  # Alias
            'compare_criteria_lists': compare_criteria_lists,
            'compare_diagnostic_criteria': compare_criteria_lists,  # Alias
            'compare_with_normative': compare_with_normative,
            'compare_categorical_values': compare_categorical_values,
            'compare_reference_dates': compare_reference_dates,
            'check_reference_currency': compare_reference_dates,  # Alias
            'compare_age_ranges': compare_score_ranges,  # Reuse range comparison
            'compare_referral_destinations': compare_flow_sequences,  # Reuse flow
        }

    def get_comparison_function(self, name: str) -> Optional[Callable]:
        """Get a comparison function by name.

        Args:
            name: Function name as specified in YAML

        Returns:
            Comparison function or None if not found
        """
        return self._comparison_functions.get(name)

    def get_rules_for_type(self, conflict_type: ConflictType) -> List[ValidationRule]:
        """Get all rules matching a conflict type.

        Args:
            conflict_type: Type of conflict to filter by

        Returns:
            List of matching rules
        """
        return [r for r in self.rules if r.conflict_type == conflict_type and r.enabled]

    def get_rule_tolerance(self, rule: ValidationRule) -> float:
        """Get tolerance value for a rule.

        Args:
            rule: Validation rule

        Returns:
            Tolerance value (from rule or default)
        """
        # Check rule metadata for tolerance
        if hasattr(rule, 'tolerance') and rule.tolerance is not None:
            return rule.tolerance

        # Default tolerances by conflict type
        defaults = {
            ConflictType.TIMELINE_INCONSISTENCY: 5.0,
            ConflictType.INSTRUMENT_SCORING: 1.0,
            ConflictType.NUMERIC_MISMATCH: 0.0,
        }
        return defaults.get(rule.conflict_type, 0.0)

    def execute_rule(
        self,
        rule: ValidationRule,
        claim_a: ValidatableClaim,
        claim_b: ValidatableClaim
    ) -> Optional[ClaimConflict]:
        """Execute a single rule against two claims.

        Args:
            rule: Validation rule to execute
            claim_a: First claim
            claim_b: Second claim

        Returns:
            ClaimConflict if conflict detected, None otherwise
        """
        if not rule.enabled:
            return None

        # Get comparison function
        compare_fn = self.get_comparison_function(rule.comparison_function)
        if not compare_fn:
            return None

        # Get tolerance for this rule
        tolerance = self.get_rule_tolerance(rule)

        # Execute comparison
        try:
            is_conflict, explanation = compare_fn(
                claim_a.normalized_value,
                claim_b.normalized_value,
                tolerance=tolerance
            )

            if is_conflict:
                return ClaimConflict(
                    id=f"rule_{rule.id}_{uuid.uuid4().hex[:8]}",
                    claim_a=claim_a,
                    claim_b=claim_b,
                    conflict_type=rule.conflict_type,
                    severity=rule.severity,
                    explanation=f"[{rule.name}] {explanation}",
                    suggested_resolution=self._generate_resolution(rule, claim_a, claim_b),
                )
        except TypeError:
            # Function doesn't accept tolerance parameter - try without it
            try:
                is_conflict, explanation = compare_fn(
                    claim_a.normalized_value,
                    claim_b.normalized_value
                )
                if is_conflict:
                    return ClaimConflict(
                        id=f"rule_{rule.id}_{uuid.uuid4().hex[:8]}",
                        claim_a=claim_a,
                        claim_b=claim_b,
                        conflict_type=rule.conflict_type,
                        severity=rule.severity,
                        explanation=f"[{rule.name}] {explanation}",
                        suggested_resolution=self._generate_resolution(rule, claim_a, claim_b),
                    )
            except Exception:
                pass

        return None

    def _generate_resolution(
        self,
        rule: ValidationRule,
        claim_a: ValidatableClaim,
        claim_b: ValidatableClaim
    ) -> str:
        """Generate a suggested resolution for a conflict."""
        if rule.conflict_type == ConflictType.TIMELINE_INCONSISTENCY:
            # Use expected value from rule metadata if available
            expected = getattr(rule, 'expected_value', None)
            if expected:
                return f"Alinhar com valor normativo: {expected} dias"
            return "Verificar normativa MS para prazo correto"

        if rule.conflict_type == ConflictType.INSTRUMENT_SCORING:
            return "Verificar validação oficial do instrumento"

        if rule.conflict_type == ConflictType.RESPONSIBILITY_CONFLICT:
            return "Alinhar atribuições com matriz RACI do protocolo"

        if rule.conflict_type == ConflictType.FLOW_INCONSISTENCY:
            return "Verificar macrofluxo oficial da RAPS"

        return "Revisar e alinhar entre documentos"


# =============================================================================
# Claim Extractor
# =============================================================================

class ClaimExtractor:
    """Extracts validatable claims from protocol documents.

    This class converts raw text and concepts into structured claims
    that can be compared across documents.
    """

    # Regex patterns for extracting numeric values
    NUMERIC_PATTERNS = {
        # Matches various formats:
        # - | **P1 – Urgente** | Até 30 dias |
        # - **P1 – URGENTE** (até 30 dias ...)
        # - P1[P1 URGENTE<br/>até 30 dias]
        # - P1: até 30 dias
        # - Prioridade 1: 30 dias
        'timeline_days': re.compile(
            r'(?:\*{0,2}P([123])[\s\u2013\u2014–—-]+\w+\*{0,2}[^|]*\|[^|]*[Aa]t[eé]\s*(\d+)\s*dias?'
            r'|\*{0,2}P([123])[\s\u2013\u2014–—-]+\w+\*{0,2}\s*\([^)]*?[Aa]t[eé]\s*(\d+)\s*dias?'
            r'|P([123])\[P[123]\s+\w+<br/?>[Aa]t[eé]\s*(\d+)\s*dias?'
            r'|(?:P([123])|Prioridade\s+([123]))[:\s]+(?:at[eé]\s+)?(\d+)\s*dias?)',
            re.IGNORECASE
        ),
        'score_range': re.compile(
            r'(?:baixo|moderado|alto)\s+risco[:\s]+(\d+)\s*[-–]\s*(\d+)',
            re.IGNORECASE
        ),
        'age_months': re.compile(
            r'(\d+)\s*[-–]\s*(\d+)\s*meses?',
            re.IGNORECASE
        ),
        'percentage': re.compile(
            r'(\d+(?:[.,]\d+)?)\s*%',
            re.IGNORECASE
        ),
        'frequency': re.compile(
            r'(?:a cada|cada)\s+(\d+)\s+(?:dias|semanas|meses)',
            re.IGNORECASE
        ),
    }

    # Regex patterns for extracting categorical values
    CATEGORICAL_PATTERNS = {
        'priority': re.compile(
            r'\b(P[123]|Prioridade\s+[123]|prioridade\s+(?:alta|moderada|regular))\b',
            re.IGNORECASE
        ),
        'responsibility': re.compile(
            r'(ACS|enfermeiro|médico|NIRSM-?R|eMulti|eSF)[:\s]+(?:deve|responsável)',
            re.IGNORECASE
        ),
        'instrument': re.compile(
            r'\b(M-CHAT[-\w]*|CuidaSM|IRDI|ADOS|CARS)\b',
            re.IGNORECASE
        ),
        'risk_level': re.compile(
            r'(?:risco|classificação)[:\s]+(baixo|moderado|alto|muito\s+alto)',
            re.IGNORECASE
        ),
    }

    # Regex patterns for flow extraction
    FLOW_PATTERNS = {
        'transition': re.compile(
            r'(APS|NIRSM|CAPS|UBS|CAPSi)\s*(?:→|->|para)\s*(APS|NIRSM|CAPS|UBS|CAPSi)',
            re.IGNORECASE
        ),
        'step_sequence': re.compile(
            r'(?:etapa|fase|passo)\s+(\d+)[:\s]+(.+?)(?=etapa|fase|passo|\n|$)',
            re.IGNORECASE
        ),
    }

    # Regex patterns for terminology extraction
    TERMINOLOGY_PATTERNS = {
        'definition': re.compile(
            r'(?:define-se|entende-se por|considera-se)\s+([^:]+)[:\s]+(.+?)(?=\.|;|$)',
            re.IGNORECASE
        ),
    }

    def __init__(self, context_processor=None):
        """Initialize the claim extractor.

        Args:
            context_processor: Optional CachedContextProcessor for integration
        """
        self._claim_counter = 0
        self._section_cache: Dict[str, List[Tuple[int, str]]] = {}
        self.context_processor = context_processor

    def _generate_claim_id(self, source_file: Path, claim_type: str) -> str:
        """Generate a unique claim ID."""
        self._claim_counter += 1
        file_prefix = source_file.stem[:10].lower().replace(' ', '_')
        return f"{file_prefix}_{claim_type}_{self._claim_counter}"

    def _extract_section_headers(self, text: str) -> List[Tuple[int, str]]:
        """Extract section headers with their line numbers.

        Args:
            text: Full document text

        Returns:
            List of (line_number, section_title) tuples
        """
        headers = []
        for i, line in enumerate(text.split('\n'), 1):
            match = re.match(r'^(#{1,4})\s+(.+)$', line)
            if match:
                headers.append((i, match.group(2).strip()))
        return headers

    def _get_section_for_line(self, text: str, line_number: int, source_file: Path) -> str:
        """Get the section header for a given line number.

        Args:
            text: Full document text
            line_number: Line number to find section for
            source_file: Source file path (for caching)

        Returns:
            Section title or empty string
        """
        cache_key = str(source_file)
        if cache_key not in self._section_cache:
            self._section_cache[cache_key] = self._extract_section_headers(text)

        headers = self._section_cache[cache_key]
        current_section = ""

        for header_line, title in headers:
            if header_line <= line_number:
                current_section = title
            else:
                break

        return current_section

    def extract_claims_from_text(
        self,
        text: str,
        source_file: Path,
        base_line_number: int = 1
    ) -> List[ValidatableClaim]:
        """Extract validatable claims from raw text.

        Args:
            text: Raw text content
            source_file: Path to the source file
            base_line_number: Starting line number offset

        Returns:
            List of extracted claims
        """
        claims = []
        lines = text.split('\n')

        for i, line in enumerate(lines):
            line_number = base_line_number + i
            section = self._get_section_for_line(text, line_number, source_file)

            # Extract timeline claims
            for match in self.NUMERIC_PATTERNS['timeline_days'].finditer(line):
                claim = self._create_timeline_claim(
                    match, line, source_file, line_number
                )
                claim = ValidatableClaim(
                    id=claim.id,
                    claim_text=claim.claim_text,
                    normalized_value=claim.normalized_value,
                    source_file=claim.source_file,
                    line_number=claim.line_number,
                    section=section,  # Now populated
                    concept_type=claim.concept_type,
                    confidence=claim.confidence,
                    keywords=claim.keywords,
                )
                claims.append(claim)

            # Extract score range claims
            for match in self.NUMERIC_PATTERNS['score_range'].finditer(line):
                claim = self._create_score_claim(
                    match, line, source_file, line_number
                )
                claim = ValidatableClaim(
                    id=claim.id,
                    claim_text=claim.claim_text,
                    normalized_value=claim.normalized_value,
                    source_file=claim.source_file,
                    line_number=claim.line_number,
                    section=section,
                    concept_type=claim.concept_type,
                    confidence=claim.confidence,
                    keywords=claim.keywords,
                )
                claims.append(claim)

            # Extract priority claims
            for match in self.CATEGORICAL_PATTERNS['priority'].finditer(line):
                claim = self._create_priority_claim(
                    match, line, source_file, line_number
                )
                claim = ValidatableClaim(
                    id=claim.id,
                    claim_text=claim.claim_text,
                    normalized_value=claim.normalized_value,
                    source_file=claim.source_file,
                    line_number=claim.line_number,
                    section=section,
                    concept_type=claim.concept_type,
                    confidence=claim.confidence,
                    keywords=claim.keywords,
                )
                claims.append(claim)

            # Extract responsibility claims
            for match in self.CATEGORICAL_PATTERNS['responsibility'].finditer(line):
                claim = self._create_responsibility_claim(
                    match, line, source_file, line_number
                )
                claim = ValidatableClaim(
                    id=claim.id,
                    claim_text=claim.claim_text,
                    normalized_value=claim.normalized_value,
                    source_file=claim.source_file,
                    line_number=claim.line_number,
                    section=section,
                    concept_type=claim.concept_type,
                    confidence=claim.confidence,
                    keywords=claim.keywords,
                )
                claims.append(claim)

            # Extract risk level claims
            for match in self.CATEGORICAL_PATTERNS['risk_level'].finditer(line):
                claims.append(self._create_risk_level_claim(
                    match, line, source_file, line_number, section
                ))

            # Extract flow transition claims
            for match in self.FLOW_PATTERNS['transition'].finditer(line):
                claims.append(self._create_flow_claim(
                    match, line, source_file, line_number, section
                ))

        return claims

    def _create_timeline_claim(
        self,
        match: re.Match,
        line: str,
        source_file: Path,
        line_number: int
    ) -> ValidatableClaim:
        """Create a timeline claim from a regex match.

        The pattern has multiple alternatives:
        - Groups 1,2: Table format (| **P1 – Urgente** | Até 30 dias |)
        - Groups 3,4,5: Simple format (P1: até 30 dias)
        """
        # Extract days and priority from whichever pattern matched
        if match.group(1) and match.group(2):
            # Table format matched
            priority_num = match.group(1)
            days = int(match.group(2))
        else:
            # Simple format matched
            priority_num = match.group(3) or match.group(4) or "?"
            days = int(match.group(5)) if match.group(5) else 0

        priority = f"P{priority_num}" if priority_num and priority_num.isdigit() else priority_num

        return ValidatableClaim(
            id=self._generate_claim_id(source_file, f"timeline_{priority}"),
            claim_text=line.strip(),
            normalized_value={'priority': priority, 'days': days},
            source_file=source_file,
            line_number=line_number,
            section="",
            concept_type=ConceptType.METRICA,
            confidence=0.8,
            keywords={'timeline', 'prazo', priority.lower(), 'dias'},
        )

    def _create_score_claim(
        self,
        match: re.Match,
        line: str,
        source_file: Path,
        line_number: int
    ) -> ValidatableClaim:
        """Create a scoring claim from a regex match."""
        low = int(match.group(1))
        high = int(match.group(2))

        # Determine risk level and instrument
        risk_level = "?"
        if "baixo" in line.lower():
            risk_level = "baixo"
        elif "moderado" in line.lower() or "médio" in line.lower():
            risk_level = "moderado"
        elif "alto" in line.lower():
            risk_level = "alto"

        instrument = "unknown"
        for inst in ['M-CHAT', 'CuidaSM', 'IRDI']:
            if inst.lower() in line.lower():
                instrument = inst
                break

        return ValidatableClaim(
            id=self._generate_claim_id(source_file, f"score_{instrument}_{risk_level}"),
            claim_text=line.strip(),
            normalized_value={
                'instrument': instrument,
                'risk_level': risk_level,
                'range': [low, high]
            },
            source_file=source_file,
            line_number=line_number,
            section="",
            concept_type=ConceptType.METRICA,
            confidence=0.85,
            keywords={'scoring', instrument.lower(), risk_level, 'pontuação'},
        )

    def _create_priority_claim(
        self,
        match: re.Match,
        line: str,
        source_file: Path,
        line_number: int
    ) -> ValidatableClaim:
        """Create a priority claim from a regex match."""
        priority_text = match.group(1)

        return ValidatableClaim(
            id=self._generate_claim_id(source_file, "priority"),
            claim_text=line.strip(),
            normalized_value={'priority': priority_text.upper()},
            source_file=source_file,
            line_number=line_number,
            section="",
            concept_type=ConceptType.FLUXO,
            confidence=0.75,
            keywords={'prioridade', priority_text.lower()},
        )

    def _create_responsibility_claim(
        self,
        match: re.Match,
        line: str,
        source_file: Path,
        line_number: int
    ) -> ValidatableClaim:
        """Create a responsibility claim from a regex match."""
        role = match.group(1)

        return ValidatableClaim(
            id=self._generate_claim_id(source_file, f"responsibility_{role}"),
            claim_text=line.strip(),
            normalized_value={'role': role, 'responsibility': line.strip()},
            source_file=source_file,
            line_number=line_number,
            section="",
            concept_type=ConceptType.PROCEDIMENTO,
            confidence=0.7,
            keywords={'responsabilidade', role.lower(), 'atribuição'},
        )

    def _create_risk_level_claim(
        self,
        match: re.Match,
        line: str,
        source_file: Path,
        line_number: int,
        section: str
    ) -> ValidatableClaim:
        """Create a risk level claim from a regex match."""
        risk_level = match.group(1).lower()

        return ValidatableClaim(
            id=self._generate_claim_id(source_file, f"risk_{risk_level}"),
            claim_text=line.strip(),
            normalized_value={'risk_level': risk_level},
            source_file=source_file,
            line_number=line_number,
            section=section,
            concept_type=ConceptType.RISCO,
            confidence=0.75,
            keywords={'risco', risk_level, 'classificação'},
        )

    def _create_flow_claim(
        self,
        match: re.Match,
        line: str,
        source_file: Path,
        line_number: int,
        section: str
    ) -> ValidatableClaim:
        """Create a flow transition claim from a regex match."""
        source_node = match.group(1).upper()
        target_node = match.group(2).upper()

        return ValidatableClaim(
            id=self._generate_claim_id(source_file, f"flow_{source_node}_{target_node}"),
            claim_text=line.strip(),
            normalized_value={
                'source': source_node,
                'target': target_node,
                'flow': f"{source_node} → {target_node}"
            },
            source_file=source_file,
            line_number=line_number,
            section=section,
            concept_type=ConceptType.FLUXO,
            confidence=0.85,
            keywords={'fluxo', source_node.lower(), target_node.lower(), 'encaminhamento'},
        )


# =============================================================================
# Conflict Detector
# =============================================================================

class ConflictDetector:
    """Detects conflicts between claims from different documents.

    This class uses the RulesEngine to execute validation rules
    and detect conflicts.
    """

    def __init__(self, rules_engine: RulesEngine = None, rules: List[ValidationRule] = None):
        """Initialize the conflict detector.

        Args:
            rules_engine: RulesEngine instance for rule execution
            rules: Optional list of validation rules (creates internal engine)
        """
        if rules_engine:
            self.rules_engine = rules_engine
        elif rules:
            self.rules_engine = RulesEngine(rules)
        else:
            self.rules_engine = RulesEngine([])

        self._conflict_counter = 0

    def _generate_conflict_id(self) -> str:
        """Generate a unique conflict ID."""
        self._conflict_counter += 1
        return f"conflict_{self._conflict_counter}_{uuid.uuid4().hex[:8]}"

    def detect_conflicts(
        self,
        claims_a: List[ValidatableClaim],
        claims_b: List[ValidatableClaim]
    ) -> List[ClaimConflict]:
        """Detect conflicts between two sets of claims.

        Uses O(n) indexing for efficient comparison.

        Args:
            claims_a: Claims from first document
            claims_b: Claims from second document

        Returns:
            List of detected conflicts
        """
        conflicts = []

        # Build indexes for O(n) lookup
        index_a = self._build_claim_index(claims_a)
        index_b = self._build_claim_index(claims_b)

        # Compare claims by type
        for claim_type, type_claims_a in index_a.items():
            if claim_type in index_b:
                type_claims_b = index_b[claim_type]
                conflicts.extend(
                    self._compare_typed_claims(type_claims_a, type_claims_b, claim_type)
                )

        return conflicts

    def _build_claim_index(
        self,
        claims: List[ValidatableClaim]
    ) -> Dict[str, List[ValidatableClaim]]:
        """Build an index of claims by type for efficient lookup."""
        index: Dict[str, List[ValidatableClaim]] = defaultdict(list)

        for claim in claims:
            # Determine grouping key based on normalized value
            key = self._get_claim_type_key(claim)
            index[key].append(claim)

        return index

    def _get_claim_type_key(self, claim: ValidatableClaim) -> str:
        """Get the type key for indexing a claim."""
        if isinstance(claim.normalized_value, dict):
            if 'priority' in claim.normalized_value and 'days' in claim.normalized_value:
                return f"timeline_{claim.normalized_value['priority']}"
            if 'instrument' in claim.normalized_value:
                return f"score_{claim.normalized_value['instrument']}_{claim.normalized_value.get('risk_level', '')}"
            if 'role' in claim.normalized_value:
                return f"responsibility_{claim.normalized_value['role']}"
            if 'source' in claim.normalized_value and 'target' in claim.normalized_value:
                return f"flow_{claim.normalized_value['source']}_{claim.normalized_value['target']}"
            if 'risk_level' in claim.normalized_value:
                return f"risk_{claim.normalized_value['risk_level']}"

        return claim.concept_type.value

    def _compare_typed_claims(
        self,
        claims_a: List[ValidatableClaim],
        claims_b: List[ValidatableClaim],
        claim_type: str
    ) -> List[ClaimConflict]:
        """Compare claims of the same type."""
        conflicts = []

        # Determine which rules apply to this claim type
        conflict_type = self._infer_conflict_type(claim_type)
        applicable_rules = self.rules_engine.get_rules_for_type(conflict_type)

        for claim_a in claims_a:
            for claim_b in claims_b:
                # Skip if claims are from the same file
                if claim_a.source_file == claim_b.source_file:
                    continue

                # Check if claims are related
                if not claim_a.matches_keywords(claim_b):
                    continue

                # Try rules-based detection first
                if applicable_rules:
                    for rule in applicable_rules:
                        conflict = self.rules_engine.execute_rule(rule, claim_a, claim_b)
                        if conflict:
                            conflicts.append(conflict)
                            break  # One conflict per claim pair
                else:
                    # Fallback to built-in comparison
                    conflict = self._compare_claims_builtin(claim_a, claim_b)
                    if conflict:
                        conflicts.append(conflict)

        return conflicts

    def _infer_conflict_type(self, claim_type_key: str) -> ConflictType:
        """Infer the conflict type from claim type key."""
        if claim_type_key.startswith('timeline_'):
            return ConflictType.TIMELINE_INCONSISTENCY
        if claim_type_key.startswith('score_'):
            return ConflictType.INSTRUMENT_SCORING
        if claim_type_key.startswith('responsibility_'):
            return ConflictType.RESPONSIBILITY_CONFLICT
        if claim_type_key.startswith('flow_'):
            return ConflictType.FLOW_INCONSISTENCY
        if claim_type_key.startswith('risk_'):
            return ConflictType.CATEGORICAL_CONFLICT
        return ConflictType.NUMERIC_MISMATCH

    def _compare_claims_builtin(
        self,
        claim_a: ValidatableClaim,
        claim_b: ValidatableClaim
    ) -> Optional[ClaimConflict]:
        """Built-in comparison for when no rules apply."""
        val_a = claim_a.normalized_value
        val_b = claim_b.normalized_value

        if not isinstance(val_a, dict) or not isinstance(val_b, dict):
            return None

        # Timeline comparison
        if 'days' in val_a and 'days' in val_b:
            if val_a.get('priority') == val_b.get('priority'):
                is_conflict, explanation = compare_numeric_values(val_a, val_b, tolerance=5.0)
                if is_conflict:
                    return self._create_timeline_conflict(claim_a, claim_b, explanation)

        # Score range comparison
        if 'range' in val_a and 'range' in val_b:
            if val_a.get('instrument') == val_b.get('instrument'):
                if val_a.get('risk_level') == val_b.get('risk_level'):
                    is_conflict, explanation = compare_score_ranges(val_a, val_b)
                    if is_conflict:
                        return self._create_scoring_conflict(claim_a, claim_b, explanation)

        return None

    def _create_timeline_conflict(
        self,
        claim_a: ValidatableClaim,
        claim_b: ValidatableClaim,
        explanation: str
    ) -> ClaimConflict:
        """Create a timeline inconsistency conflict."""
        priority = claim_a.normalized_value.get('priority', 'P?')
        days_a = claim_a.normalized_value['days']
        days_b = claim_b.normalized_value['days']

        return ClaimConflict(
            id=self._generate_conflict_id(),
            claim_a=claim_a,
            claim_b=claim_b,
            conflict_type=ConflictType.TIMELINE_INCONSISTENCY,
            severity=ConflictSeverity.CRITICAL if priority == 'P1' else ConflictSeverity.WARNING,
            explanation=f"Timeline {priority}: {days_a} dias vs {days_b} dias. {explanation}",
            suggested_resolution=f"Alinhar com normativa MS: {priority} = {30 if priority == 'P1' else 90 if priority == 'P2' else 180} dias",
        )

    def _create_scoring_conflict(
        self,
        claim_a: ValidatableClaim,
        claim_b: ValidatableClaim,
        explanation: str
    ) -> ClaimConflict:
        """Create a scoring inconsistency conflict."""
        instrument = claim_a.normalized_value.get('instrument', 'Unknown')
        risk_level = claim_a.normalized_value.get('risk_level', '?')

        return ClaimConflict(
            id=self._generate_conflict_id(),
            claim_a=claim_a,
            claim_b=claim_b,
            conflict_type=ConflictType.INSTRUMENT_SCORING,
            severity=ConflictSeverity.CRITICAL,
            explanation=f"Pontuação {instrument} ({risk_level}): {explanation}",
            suggested_resolution=f"Verificar validação oficial do instrumento {instrument}",
        )


# =============================================================================
# Cross-Document Validator
# =============================================================================

class CrossDocumentValidator:
    """Main validation engine for cross-document protocol validation.

    This class orchestrates the extraction, comparison, and reporting of
    conflicts between clinical protocols.

    Example:
        validator = CrossDocumentValidator()
        report = validator.compare_protocols(
            Path("CLI_02.md"),
            Path("MACROFLUXO.md")
        )
        print(report.format_summary())
    """

    # Default protocol paths
    PROTOCOL_PATHS = {
        'CLI_02': 'entregas/Protocolos_Compartilhamento_Cuidado/Protocolos_Clinicos/CLI_02_TRANSTORNO_ESPECTRO_AUTISTA.md',
        'MACROFLUXO': 'entregas/Protocolos_Compartilhamento_Cuidado/Protocolos_Clinicos/MACROFLUXO_NARRATIVO_DI_TEA.md',
        'GUIA_NARRATIVO': 'entregas/Protocolos_Compartilhamento_Cuidado/Protocolos_Clinicos/GUIA_NARRATIVO_APS_DI_TEA.md',
    }

    def __init__(
        self,
        rules_path: Optional[Path] = None,
        reference_index_path: Optional[Path] = None
    ):
        """Initialize the validator.

        Args:
            rules_path: Path to validation_rules.yaml
            reference_index_path: Path to REFERENCE_INDEX.yaml
        """
        self.extractor = ClaimExtractor()

        # Load rules if provided
        self.rules = []
        self.rules_data = {}
        if rules_path and rules_path.exists():
            self.rules, self.rules_data = self._load_rules(rules_path)

        # Create rules engine
        self.rules_engine = RulesEngine(self.rules, self.rules_data)

        # Create detector with rules engine
        self.detector = ConflictDetector(rules_engine=self.rules_engine)

        # Load reference index if provided
        self.reference_index = {}
        if reference_index_path and reference_index_path.exists():
            self.reference_index = self._load_reference_index(reference_index_path)

    def _load_rules(self, rules_path: Path) -> Tuple[List[ValidationRule], Dict[str, Any]]:
        """Load validation rules from YAML file."""
        try:
            with open(rules_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            rules = []
            rule_groups = [
                'timeline_rules', 'instrument_rules', 'responsibility_rules',
                'flow_rules', 'terminology_rules', 'normative_rules'
            ]

            for rule_group in rule_groups:
                if rule_group in data:
                    for rule_data in data[rule_group]:
                        rule = ValidationRule(
                            id=rule_data['id'],
                            name=rule_data['name'],
                            description=rule_data.get('description', ''),
                            conflict_type=ConflictType(rule_data['conflict_type']),
                            severity=ConflictSeverity(rule_data['severity']),
                            patterns=rule_data.get('patterns', []),
                            comparison_function=rule_data.get('comparison_function', ''),
                            enabled=rule_data.get('enabled', True),
                        )
                        # Store additional metadata
                        if 'tolerance' in rule_data:
                            rule.tolerance = rule_data['tolerance']
                        if 'expected_value' in rule_data:
                            rule.expected_value = rule_data['expected_value']
                        rules.append(rule)

            return rules, data

        except Exception:
            return [], {}

    def _load_reference_index(self, index_path: Path) -> Dict[str, Any]:
        """Load reference index from YAML file."""
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception:
            return {}

    def _resolve_protocol_path(self, protocol_name: str) -> Optional[Path]:
        """Resolve a protocol name to a file path."""
        # Check if it's a known protocol name
        if protocol_name.upper() in self.PROTOCOL_PATHS:
            path = Path.cwd() / self.PROTOCOL_PATHS[protocol_name.upper()]
            if path.exists():
                return path

        # Check if it's a direct path
        direct_path = Path(protocol_name)
        if direct_path.exists():
            return direct_path

        # Check in protocol directories
        for base_path in self.PROTOCOL_PATHS.values():
            parent = Path.cwd() / Path(base_path).parent
            if parent.exists():
                for f in parent.glob(f"*{protocol_name}*"):
                    if f.is_file():
                        return f

        return None

    def validate_protocol(self, protocol_name: str) -> ValidationReport:
        """Validate a single protocol against reference standards."""
        report = ValidationReport(
            id=f"validation_{uuid.uuid4().hex[:8]}",
            protocols_validated=[protocol_name],
            validation_started=datetime.now(),
            status=ValidationStatus.IN_PROGRESS,
        )

        protocol_path = self._resolve_protocol_path(protocol_name)
        if not protocol_path:
            report.status = ValidationStatus.FAILED
            report.summary['error'] = f"Protocolo não encontrado: {protocol_name}"
            return report

        try:
            content = protocol_path.read_text(encoding='utf-8')
            claims = self.extractor.extract_claims_from_text(content, protocol_path)
            report.claims_analyzed = len(claims)
        except Exception as e:
            report.status = ValidationStatus.FAILED
            report.summary['error'] = f"Erro ao ler protocolo: {e}"
            return report

        report.status = ValidationStatus.COMPLETED
        report.validation_completed = datetime.now()
        return report

    def compare_protocols(
        self,
        protocol_a: str,
        protocol_b: str
    ) -> ValidationReport:
        """Compare two protocols for conflicts."""
        report = ValidationReport(
            id=f"comparison_{uuid.uuid4().hex[:8]}",
            protocols_validated=[protocol_a, protocol_b],
            validation_started=datetime.now(),
            status=ValidationStatus.IN_PROGRESS,
        )

        path_a = self._resolve_protocol_path(protocol_a)
        path_b = self._resolve_protocol_path(protocol_b)

        if not path_a:
            report.status = ValidationStatus.FAILED
            report.summary['error'] = f"Protocolo não encontrado: {protocol_a}"
            return report

        if not path_b:
            report.status = ValidationStatus.FAILED
            report.summary['error'] = f"Protocolo não encontrado: {protocol_b}"
            return report

        try:
            content_a = path_a.read_text(encoding='utf-8')
            content_b = path_b.read_text(encoding='utf-8')

            claims_a = self.extractor.extract_claims_from_text(content_a, path_a)
            claims_b = self.extractor.extract_claims_from_text(content_b, path_b)

            report.claims_analyzed = len(claims_a) + len(claims_b)
        except Exception as e:
            report.status = ValidationStatus.FAILED
            report.summary['error'] = f"Erro ao ler protocolos: {e}"
            return report

        conflicts = self.detector.detect_conflicts(claims_a, claims_b)
        report.conflicts = conflicts

        report.summary = {
            'claims_in_a': len(claims_a),
            'claims_in_b': len(claims_b),
            'conflicts_found': len(conflicts),
        }

        report.status = ValidationStatus.COMPLETED
        report.validation_completed = datetime.now()
        return report

    def detect_inconsistencies(
        self,
        protocol_names: List[str] = None
    ) -> ValidationReport:
        """Detect all inconsistencies across multiple protocols."""
        if protocol_names is None:
            protocol_names = list(self.PROTOCOL_PATHS.keys())

        report = ValidationReport(
            id=f"full_validation_{uuid.uuid4().hex[:8]}",
            protocols_validated=protocol_names,
            validation_started=datetime.now(),
            status=ValidationStatus.IN_PROGRESS,
        )

        all_claims: Dict[str, List[ValidatableClaim]] = {}
        for name in protocol_names:
            path = self._resolve_protocol_path(name)
            if path:
                try:
                    content = path.read_text(encoding='utf-8')
                    claims = self.extractor.extract_claims_from_text(content, path)
                    all_claims[name] = claims
                    report.claims_analyzed += len(claims)
                except Exception:
                    pass

        protocol_list = list(all_claims.keys())
        for i in range(len(protocol_list)):
            for j in range(i + 1, len(protocol_list)):
                name_a = protocol_list[i]
                name_b = protocol_list[j]
                conflicts = self.detector.detect_conflicts(
                    all_claims[name_a],
                    all_claims[name_b]
                )
                report.conflicts.extend(conflicts)

        report.status = ValidationStatus.COMPLETED
        report.validation_completed = datetime.now()
        return report

    def get_evidence_for_term(self, term: str) -> List[Dict[str, Any]]:
        """Query reference index for evidence about a term."""
        results = []
        term_lower = term.lower()

        for section in ['instruments', 'guidelines', 'clinical_references', 'project_protocols']:
            for item in self.reference_index.get(section, []):
                if term_lower in item.get('name', '').lower():
                    results.append(item)
                elif term_lower in str(item.get('keywords', [])).lower():
                    results.append(item)
                elif term_lower in item.get('id', '').lower():
                    results.append(item)

        return results


# =============================================================================
# Report Formatting (moved to formatter.py in next step)
# =============================================================================

def format_validation_report(report: ValidationReport) -> str:
    """Format a validation report for display.

    Args:
        report: ValidationReport to format

    Returns:
        Formatted string for display
    """
    from .formatter import format_header, format_separator, BOX_WIDTH

    protocols_str = " vs ".join(report.protocols_validated)
    output = format_header(f"VALIDAÇÃO: {protocols_str}")
    output += "\n\n"

    output += report.format_summary()
    output += "\n"
    output += format_separator()
    output += "\n\n"

    if report.conflicts:
        output += "CONFLITOS DETECTADOS:\n\n"

        critical = report.get_conflicts_by_severity(ConflictSeverity.CRITICAL)
        if critical:
            output += "🔴 CRÍTICOS:\n"
            for conflict in critical:
                output += conflict.format_report_entry()
                output += "\n"

        warnings = report.get_conflicts_by_severity(ConflictSeverity.WARNING)
        if warnings:
            output += "🟡 ALERTAS:\n"
            for conflict in warnings:
                output += conflict.format_report_entry()
                output += "\n"

        info = report.get_conflicts_by_severity(ConflictSeverity.INFO)
        if info:
            output += "🔵 INFORMATIVOS:\n"
            for conflict in info:
                output += conflict.format_report_entry()
                output += "\n"
    else:
        output += "✅ Nenhum conflito detectado entre os protocolos.\n"

    return output
