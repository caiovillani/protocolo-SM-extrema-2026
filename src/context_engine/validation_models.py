# src/context_engine/validation_models.py

"""Data models for cross-document validation system.

This module defines the core data structures for detecting conflicts and
inconsistencies between clinical protocols. It supports the /validar command
and evidence-backed protocol development.

Key Classes:
    ValidatableClaim: A claim extracted from a document with source attribution
    ClaimConflict: A detected conflict between two claims
    ValidationReport: Summary of validation results
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .context_models import ConceptType, EvidenceGrade


class ConflictType(Enum):
    """Types of conflicts between protocol claims."""
    NUMERIC_MISMATCH = "numeric_mismatch"      # Different numeric values (e.g., P1=30 vs P1=45)
    CATEGORICAL_CONFLICT = "categorical_conflict"  # Different categorical assignments
    FLOW_INCONSISTENCY = "flow_inconsistency"   # Contradictory process flows
    RESPONSIBILITY_CONFLICT = "responsibility_conflict"  # Different role assignments
    TERMINOLOGY_DRIFT = "terminology_drift"      # Same term, different meanings
    TIMELINE_INCONSISTENCY = "timeline_inconsistency"  # Time-based conflicts
    INSTRUMENT_SCORING = "instrument_scoring"    # Scoring/cutoff discrepancies
    MISSING_REQUIREMENT = "missing_requirement"  # Required element absent
    OUTDATED_REFERENCE = "outdated_reference"    # Reference to superseded content


class ConflictSeverity(Enum):
    """Severity levels for detected conflicts."""
    CRITICAL = "critical"   # Must fix before release (safety, regulatory)
    WARNING = "warning"     # Should fix (consistency, quality)
    INFO = "info"           # May fix (style, optimization)


class ValidationStatus(Enum):
    """Status of a validation run."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ValidatableClaim:
    """A claim extracted from a document with full source attribution.

    This is the atomic unit for cross-document validation. Each claim can
    be traced back to its source file and line number.

    Attributes:
        id: Unique identifier for the claim
        claim_text: The actual text of the claim
        normalized_value: Extracted/normalized value (for comparison)
        source_file: Path to the source document
        line_number: Line number in the source
        section: Section where the claim appears
        concept_type: Type of concept (from ConceptType)
        evidence_grade: Quality of evidence supporting the claim
        confidence: Extraction confidence (0.0-1.0)
        keywords: Associated keywords for matching
        metadata: Additional claim-specific data

    Example:
        ValidatableClaim(
            id="cli02_p1_timeline",
            claim_text="P1: Prioridade 1 - Atendimento em até 30 dias",
            normalized_value={"priority": "P1", "days": 30},
            source_file=Path("CLI_02_TEA.md"),
            line_number=847,
            ...
        )
    """
    id: str
    claim_text: str
    normalized_value: Any  # Can be int, float, str, dict depending on claim type
    source_file: Path
    line_number: int
    section: str
    concept_type: ConceptType
    evidence_grade: EvidenceGrade = EvidenceGrade.NAO_AVALIADA
    confidence: float = 0.5
    keywords: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_citation(self, short: bool = False) -> str:
        """Generate a citation string for this claim.

        Args:
            short: If True, use abbreviated format

        Returns:
            Citation string (e.g., "CLI_02_TEA.md:847")
        """
        filename = self.source_file.name
        if short:
            short_name = filename.replace('.md', '').replace('.pdf', '')[:15]
            return f"[{short_name}:{self.line_number}]"
        return f"{filename}:{self.line_number}"

    def matches_keywords(self, other: 'ValidatableClaim') -> Set[str]:
        """Find keywords in common with another claim.

        Args:
            other: Another ValidatableClaim to compare

        Returns:
            Set of shared keywords
        """
        return self.keywords.intersection(other.keywords)


@dataclass
class ClaimConflict:
    """A detected conflict between two claims from different documents.

    This represents an inconsistency that needs human review or resolution.

    Attributes:
        id: Unique identifier for the conflict
        claim_a: First claim involved in the conflict
        claim_b: Second claim involved in the conflict
        conflict_type: Type of conflict detected
        severity: How critical is this conflict
        explanation: Human-readable explanation of the conflict
        suggested_resolution: Optional suggestion for fixing
        detected_at: Timestamp of detection
        metadata: Additional conflict-specific data
    """
    id: str
    claim_a: ValidatableClaim
    claim_b: ValidatableClaim
    conflict_type: ConflictType
    severity: ConflictSeverity
    explanation: str
    suggested_resolution: Optional[str] = None
    detected_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def format_report_entry(self) -> str:
        """Format this conflict for inclusion in a validation report.

        Returns:
            Formatted string for the conflict
        """
        severity_emoji = {
            ConflictSeverity.CRITICAL: "🔴",
            ConflictSeverity.WARNING: "🟡",
            ConflictSeverity.INFO: "🔵",
        }

        emoji = severity_emoji.get(self.severity, "❓")
        output = f"{emoji} [{self.severity.value.upper()}] {self.conflict_type.value}\n"
        output += f"  ├─ {self.claim_a.get_citation()} → \"{self.claim_a.claim_text[:50]}...\"\n"
        output += f"  ├─ {self.claim_b.get_citation()} → \"{self.claim_b.claim_text[:50]}...\"\n"
        output += f"  └─ {self.explanation}\n"

        if self.suggested_resolution:
            output += f"     💡 Sugestão: {self.suggested_resolution}\n"

        return output


@dataclass
class ValidationRule:
    """A rule for detecting specific types of conflicts.

    Validation rules define patterns to match and comparison logic.

    Attributes:
        id: Unique rule identifier
        name: Human-readable rule name
        description: What this rule checks for
        conflict_type: Type of conflict this rule detects
        severity: Default severity for conflicts from this rule
        patterns: Regex patterns for matching claims
        comparison_function: Name of comparison function to use
        enabled: Whether this rule is active
    """
    id: str
    name: str
    description: str
    conflict_type: ConflictType
    severity: ConflictSeverity
    patterns: List[str]
    comparison_function: str
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationReport:
    """Summary of a validation run with all detected conflicts.

    This is the main output of the /validar command.

    Attributes:
        id: Unique report identifier
        protocols_validated: List of protocol names/paths validated
        validation_started: When validation started
        validation_completed: When validation finished
        status: Current status of the validation
        conflicts: List of detected conflicts
        claims_analyzed: Total number of claims analyzed
        rules_applied: List of rule IDs that were applied
        summary: High-level summary statistics
    """
    id: str
    protocols_validated: List[str]
    validation_started: datetime
    validation_completed: Optional[datetime] = None
    status: ValidationStatus = ValidationStatus.PENDING
    conflicts: List[ClaimConflict] = field(default_factory=list)
    claims_analyzed: int = 0
    rules_applied: List[str] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)

    def get_conflicts_by_severity(self, severity: ConflictSeverity) -> List[ClaimConflict]:
        """Get conflicts filtered by severity.

        Args:
            severity: Severity level to filter by

        Returns:
            List of conflicts with the specified severity
        """
        return [c for c in self.conflicts if c.severity == severity]

    def get_conflict_counts(self) -> Dict[str, int]:
        """Get counts of conflicts by severity.

        Returns:
            Dictionary with severity -> count mapping
        """
        counts = {
            "critical": 0,
            "warning": 0,
            "info": 0,
        }
        for conflict in self.conflicts:
            counts[conflict.severity.value] += 1
        return counts

    def is_valid(self) -> bool:
        """Check if the validated protocols are considered valid.

        A protocol suite is valid if there are no critical conflicts.

        Returns:
            True if no critical conflicts exist
        """
        return len(self.get_conflicts_by_severity(ConflictSeverity.CRITICAL)) == 0

    def format_summary(self) -> str:
        """Format a summary of the validation report.

        Returns:
            Formatted summary string
        """
        counts = self.get_conflict_counts()
        total = len(self.conflicts)

        status_emoji = "✅" if self.is_valid() else "❌"
        output = f"{status_emoji} Validação {'aprovada' if self.is_valid() else 'reprovada'}\n\n"
        output += f"Protocolos analisados: {len(self.protocols_validated)}\n"
        output += f"Claims analisadas: {self.claims_analyzed}\n"
        output += f"Regras aplicadas: {len(self.rules_applied)}\n\n"
        output += f"Conflitos encontrados: {total}\n"
        output += f"  🔴 Críticos: {counts['critical']}\n"
        output += f"  🟡 Alertas: {counts['warning']}\n"
        output += f"  🔵 Informativos: {counts['info']}\n"

        return output

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the report to a dictionary.

        Returns:
            Dictionary representation for export
        """
        return {
            'id': self.id,
            'protocols_validated': self.protocols_validated,
            'validation_started': self.validation_started.isoformat(),
            'validation_completed': self.validation_completed.isoformat() if self.validation_completed else None,
            'status': self.status.value,
            'claims_analyzed': self.claims_analyzed,
            'rules_applied': self.rules_applied,
            'conflict_counts': self.get_conflict_counts(),
            'is_valid': self.is_valid(),
            'conflicts': [
                {
                    'id': c.id,
                    'type': c.conflict_type.value,
                    'severity': c.severity.value,
                    'explanation': c.explanation,
                    'claim_a_citation': c.claim_a.get_citation(),
                    'claim_b_citation': c.claim_b.get_citation(),
                }
                for c in self.conflicts
            ],
        }
