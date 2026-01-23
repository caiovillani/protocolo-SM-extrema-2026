# src/context_engine/context_models.py

"""Modelos de dados para o Motor de Contexto de Alta Qualidade Técnica.

Define dataclasses para representação estruturada de documentos, conceitos,
relacionamentos e índices cruzados.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


class ConceptType(Enum):
    """Tipos de conceito extraídos dos documentos."""
    DEFINICAO = "definicao"
    NORMA = "norma"
    PROCEDIMENTO = "procedimento"
    CONDICAO_CLINICA = "condicao_clinica"
    FLUXO = "fluxo"
    METRICA = "metrica"
    CONCEITO_CHAVE = "conceito_chave"
    RISCO = "risco"
    RECURSO = "recurso"


class RelationType(Enum):
    """Tipos de relacionamento entre conceitos."""
    REFERENCIA = "referencia"
    DEPENDE = "depende"
    IMPLEMENTA = "implementa"
    RELACIONADO = "relacionado"
    CONTRADIZ = "contradiz"
    COMPLEMENTA = "complementa"


@dataclass
class DocumentMetadata:
    """Metadados do documento processado."""
    file_path: Path
    file_type: str
    size_bytes: int
    lines_count: int
    tokens_estimate: int
    processed_at: datetime
    processing_time_ms: float
    hash_md5: str


@dataclass
class StructuredSection:
    """Seção estruturada do documento."""
    title: str
    level: int
    start_line: int
    end_line: int
    content: str
    subsections: List['StructuredSection'] = field(default_factory=list)


@dataclass
class Concept:
    """Conceito extraído do documento."""
    id: str
    text: str
    type: ConceptType
    source_file: Path
    section: str
    line_number: int
    context: str
    confidence: float
    keywords: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Relationship:
    """Relacionamento entre conceitos."""
    source_id: str
    target_id: str
    type: RelationType
    weight: float
    evidence: str
    line_number: int


@dataclass
class ContextIndex:
    """Índice cruzado de conceitos."""
    concepts_by_type: Dict[str, List[str]] = field(default_factory=dict)
    concepts_by_keyword: Dict[str, List[str]] = field(default_factory=dict)
    concepts_by_file: Dict[str, List[str]] = field(default_factory=dict)

    def _add_to_index(self, index_dict: Dict[str, List[str]], key: str, value: str) -> None:
        """Adiciona valor a lista em dicionário, criando lista se necessário."""
        if key not in index_dict:
            index_dict[key] = []
        index_dict[key].append(value)

    def add_concept(self, concept: Concept) -> None:
        """Adiciona conceito ao índice."""
        self._add_to_index(self.concepts_by_type, concept.type.value, concept.id)

        for keyword in concept.keywords:
            self._add_to_index(self.concepts_by_keyword, keyword.lower(), concept.id)

        self._add_to_index(self.concepts_by_file, str(concept.source_file), concept.id)

    def search_by_keyword(self, keyword: str) -> List[str]:
        """Busca conceitos por keyword."""
        return self.concepts_by_keyword.get(keyword.lower(), [])

    def search_by_type(self, concept_type: ConceptType) -> List[str]:
        """Busca conceitos por tipo."""
        return self.concepts_by_type.get(concept_type.value, [])


@dataclass
class ProcessingStats:
    """Estatísticas de processamento."""
    total_files: int = 0
    total_concepts: int = 0
    concepts_by_type: Dict[str, int] = field(default_factory=dict)
    total_relationships: int = 0
    processing_time_ms: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0


@dataclass
class StructuredDocument:
    """Documento completamente processado com contexto estruturado."""
    metadata: DocumentMetadata
    full_content: str
    sections: List[StructuredSection]
    concepts: List[Concept]
    relationships: List[Relationship]
    summary: str = ""

    def get_concepts_by_type(self, concept_type: ConceptType) -> List[Concept]:
        """Retorna conceitos filtrados por tipo."""
        return [c for c in self.concepts if c.type == concept_type]

    def get_top_concepts(self, limit: int = 10) -> List[Concept]:
        """Retorna conceitos com maior confiança."""
        sorted_concepts = sorted(self.concepts, key=lambda c: -c.confidence)
        return sorted_concepts[:limit]

    def to_dict(self) -> Dict[str, Any]:
        """Serializa para dicionário (para cache YAML)."""
        return {
            'metadata': {
                'file_path': str(self.metadata.file_path),
                'file_type': self.metadata.file_type,
                'size_bytes': self.metadata.size_bytes,
                'lines_count': self.metadata.lines_count,
                'tokens_estimate': self.metadata.tokens_estimate,
                'processed_at': self.metadata.processed_at.isoformat(),
                'processing_time_ms': self.metadata.processing_time_ms,
                'hash_md5': self.metadata.hash_md5,
            },
            'sections': [
                {
                    'title': s.title,
                    'level': s.level,
                    'start_line': s.start_line,
                    'end_line': s.end_line,
                }
                for s in self.sections
            ],
            'concepts': [
                {
                    'id': c.id,
                    'text': c.text,
                    'type': c.type.value,
                    'section': c.section,
                    'line_number': c.line_number,
                    'confidence': c.confidence,
                    'keywords': list(c.keywords),
                }
                for c in self.concepts
            ],
            'relationships': [
                {
                    'source_id': r.source_id,
                    'target_id': r.target_id,
                    'type': r.type.value,
                    'weight': r.weight,
                    'evidence': r.evidence,
                    'line_number': r.line_number,
                }
                for r in self.relationships
            ],
            'summary': self.summary,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], full_content: str) -> 'StructuredDocument':
        """Deserializa de dicionário.

        Raises:
            ValueError: Se dados estiverem em formato inválido.
        """
        try:
            meta = data['metadata']
            metadata = DocumentMetadata(
                file_path=Path(meta['file_path']),
                file_type=meta['file_type'],
                size_bytes=meta['size_bytes'],
                lines_count=meta['lines_count'],
                tokens_estimate=meta['tokens_estimate'],
                processed_at=datetime.fromisoformat(meta['processed_at']),
                processing_time_ms=meta['processing_time_ms'],
                hash_md5=meta['hash_md5'],
            )

            sections = [
                StructuredSection(
                    title=s['title'],
                    level=s['level'],
                    start_line=s['start_line'],
                    end_line=s['end_line'],
                    content="",
                )
                for s in data.get('sections', [])
            ]

            concepts = [
                Concept(
                    id=c['id'],
                    text=c['text'],
                    type=ConceptType(c['type']),
                    source_file=Path(meta['file_path']),
                    section=c['section'],
                    line_number=c['line_number'],
                    context="",
                    confidence=c['confidence'],
                    keywords=set(c.get('keywords', [])),
                )
                for c in data.get('concepts', [])
            ]

            relationships = [
                Relationship(
                    source_id=r['source_id'],
                    target_id=r['target_id'],
                    type=RelationType(r['type']),
                    weight=r['weight'],
                    evidence=r['evidence'],
                    line_number=r['line_number'],
                )
                for r in data.get('relationships', [])
            ]

            return cls(
                metadata=metadata,
                full_content=full_content,
                sections=sections,
                concepts=concepts,
                relationships=relationships,
                summary=data.get('summary', ''),
            )

        except (KeyError, TypeError, ValueError) as e:
            raise ValueError(f"Formato de dados inválido: {e}") from e
