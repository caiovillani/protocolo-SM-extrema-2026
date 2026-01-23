# src/context_engine/context_processor.py

"""Processador de contexto para extração de conceitos e relacionamentos.

Implementa heurísticas pragmáticas para:
- Extração de conceitos-chave
- Identificação de relacionamentos
- Geração de resumos hierárquicos
- Construção de índice cruzado
"""

import hashlib
import re
import time
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .context_models import (
    Concept,
    ConceptType,
    ContextIndex,
    DocumentMetadata,
    ProcessingStats,
    Relationship,
    RelationType,
    StructuredDocument,
    StructuredSection,
)
from .context_reader import read_file


class ConceptExtractor:
    """Extrator de conceitos usando heurísticas pragmáticas."""

    # Padrões regex para detecção por tipo
    PATTERNS: Dict[ConceptType, List[str]] = {
        ConceptType.DEFINICAO: [
            r'^\*\*(.+?)\*\*[:\s]',
            r'^(.+?)\s*[:-]\s*(?:é|são|consiste|significa|define-se)',
            r'(?:entende-se por|compreende-se como)\s+(.+?)\s',
        ],
        ConceptType.NORMA: [
            r'(?:Lei|Portaria|Resolução|Decreto|RDC)\s+n[ºo°]?\s*[\d./-]+',
            r'(?:Art\.|Artigo)\s+\d+',
            r'\b(?:RAPS|SUS|CFM|CRM|CID-10|CID-11|DSM-5|DSM-V)\b',
            r'Portaria\s+(?:GM/)?MS\s+n[ºo°]?\s*[\d]+',
        ],
        ConceptType.PROCEDIMENTO: [
            r'(?:Protocolo|POP|Procedimento)\s+[\w-]+',
            r'(?:realizar|executar|proceder|aplicar|encaminhar)\s+[\w\s]{5,30}',
            r'^\d+\.\s+[A-Z][^.]+',
        ],
        ConceptType.CONDICAO_CLINICA: [
            r'(?:transtorno|síndrome|doença|condição|quadro)\s+[\w\s]{3,30}',
            r'\b(?:depressão|ansiedade|psicose|esquizofrenia|TEA|TDAH|autismo|bipolar)\b',
            r'CID[- ]?(?:10|11)[:\s]*[A-Z]\d{2}',
            r'\b[A-Z]\d{2}(?:\.\d)?\b',
        ],
        ConceptType.FLUXO: [
            r'(?:fluxo|fluxograma|encaminhamento)\s+[\w\s]{3,30}',
            r'(?:de|da|do)\s+\w+\s+(?:para|→|->)\s+\w+',
            r'APS\s*[→\->]\s*(?:NIRSM|CAPS)',
            r'referência\s+e?\s*contrarreferência',
        ],
        ConceptType.RISCO: [
            r'(?:risco|alerta|atenção|cuidado)\s+(?:de|em|para|com)',
            r'(?:contraindicação|restrição|limitação)',
            r'sinais?\s+de\s+(?:alerta|gravidade)',
            r'(?:emergência|urgência)\s+(?:psiquiátrica|clínica)',
        ],
        ConceptType.METRICA: [
            r'(?:indicador|índice|taxa|percentual)\s+[\w\s]{3,30}',
            r'\d+%',
            r'escala\s+[\w\s]{3,20}',
        ],
        ConceptType.RECURSO: [
            r'(?:CAPS|UBS|NASF|NIRSM|CEO|UPA|SAMU)\b',
            r'(?:equipe|serviço|unidade|centro)\s+[\w\s]{3,30}',
        ],
    }

    # Keywords para boost de confiança
    KEYWORDS: Dict[ConceptType, Set[str]] = {
        ConceptType.NORMA: {'lei', 'portaria', 'resolução', 'normativa', 'diretriz', 'regulamento'},
        ConceptType.PROCEDIMENTO: {'protocolo', 'pop', 'procedimento', 'passo', 'etapa', 'conduta'},
        ConceptType.CONDICAO_CLINICA: {'transtorno', 'síndrome', 'diagnóstico', 'cid', 'quadro', 'sintoma'},
        ConceptType.FLUXO: {'fluxo', 'encaminhamento', 'referência', 'contrarreferência', 'matriciamento'},
        ConceptType.RISCO: {'risco', 'alerta', 'atenção', 'contraindicação', 'emergência', 'crise'},
        ConceptType.METRICA: {'indicador', 'meta', 'índice', 'escala', 'score'},
        ConceptType.RECURSO: {'caps', 'ubs', 'nirsm', 'nasf', 'equipe', 'serviço'},
    }

    def __init__(self, min_confidence: float = 0.4):
        """Inicializa extrator.

        Args:
            min_confidence: Confiança mínima para aceitar conceito (0.0-1.0)
        """
        self.min_confidence = min_confidence

    def extract(
        self,
        content: str,
        metadata: DocumentMetadata,
        sections: List[StructuredSection],
    ) -> List[Concept]:
        """Extrai conceitos do documento.

        Args:
            content: Conteúdo textual completo
            metadata: Metadados do documento
            sections: Seções estruturadas

        Returns:
            Lista de conceitos extraídos
        """
        concepts = []
        lines = content.split('\n')
        section_map = self._build_section_map(sections, len(lines))

        for line_num, line in enumerate(lines, 1):
            if not line.strip():
                continue

            current_section = section_map.get(line_num, "")

            # Aplicar padrões por tipo
            for concept_type, patterns in self.PATTERNS.items():
                for pattern in patterns:
                    try:
                        matches = list(re.finditer(pattern, line, re.IGNORECASE))
                        for match in matches:
                            text = match.group(0).strip()
                            if len(text) < 3 or len(text) > 200:
                                continue

                            concept = self._create_concept(
                                text=text,
                                concept_type=concept_type,
                                line_num=line_num,
                                section=current_section,
                                context=self._get_context(lines, line_num),
                                metadata=metadata,
                            )

                            if concept.confidence >= self.min_confidence:
                                concepts.append(concept)
                    except re.error:
                        continue

            # Conceitos-chave por headers
            if line.startswith('#'):
                header_text = line.lstrip('#').strip()
                if len(header_text) >= 3:
                    concept = self._create_concept(
                        text=header_text,
                        concept_type=ConceptType.CONCEITO_CHAVE,
                        line_num=line_num,
                        section=current_section,
                        context=self._get_context(lines, line_num),
                        metadata=metadata,
                    )
                    concept.confidence = min(1.0, concept.confidence + 0.2)
                    concepts.append(concept)

        # Deduplicar e ordenar por confiança
        concepts = self._deduplicate(concepts)
        concepts.sort(key=lambda c: -c.confidence)

        return concepts

    def _build_section_map(
        self,
        sections: List[StructuredSection],
        total_lines: int,
    ) -> Dict[int, str]:
        """Mapeia linhas para seções."""
        section_map: Dict[int, str] = {}

        for section in sections:
            for line_num in range(section.start_line, min(section.end_line + 1, total_lines + 1)):
                section_map[line_num] = section.title

        return section_map

    def _create_concept(
        self,
        text: str,
        concept_type: ConceptType,
        line_num: int,
        section: str,
        context: str,
        metadata: DocumentMetadata,
    ) -> Concept:
        """Cria conceito com cálculo de confiança."""
        # Gerar ID único
        concept_id = hashlib.md5(
            f"{text}:{metadata.file_path}:{line_num}".encode()
        ).hexdigest()[:12]

        # Extrair keywords
        keywords = self._extract_keywords(text)

        # Calcular confiança
        confidence = self._calculate_confidence(text, concept_type, keywords)

        return Concept(
            id=concept_id,
            text=text,
            type=concept_type,
            source_file=metadata.file_path,
            section=section,
            line_number=line_num,
            context=context,
            confidence=confidence,
            keywords=keywords,
        )

    def _extract_keywords(self, text: str) -> Set[str]:
        """Extrai keywords do texto."""
        # Palavras significativas (>3 chars, sem stopwords)
        stopwords = {
            'para', 'como', 'com', 'sem', 'que', 'por', 'uma', 'uns',
            'das', 'dos', 'nas', 'nos', 'aos', 'pela', 'pelo', 'entre',
        }

        words = re.findall(r'\b[a-záàâãéèêíïóôõöúç]{4,}\b', text.lower())
        keywords = {w for w in words if w not in stopwords}

        # Adicionar siglas
        siglas = re.findall(r'\b[A-Z]{2,6}\b', text)
        keywords.update(s.lower() for s in siglas)

        return keywords

    def _calculate_confidence(
        self,
        text: str,
        concept_type: ConceptType,
        keywords: Set[str],
    ) -> float:
        """Calcula confiança baseada em múltiplos fatores."""
        confidence = 0.5

        # Boost por formatação
        if '**' in text:
            confidence += 0.15
        if text.startswith('#'):
            confidence += 0.15

        # Boost por keywords do tipo
        type_keywords = self.KEYWORDS.get(concept_type, set())
        matching_keywords = keywords & type_keywords
        confidence += min(0.2, len(matching_keywords) * 0.07)

        # Boost por tamanho adequado
        if 10 <= len(text) <= 100:
            confidence += 0.1

        # Penalidade por texto muito genérico
        if len(keywords) < 2:
            confidence -= 0.1

        return max(0.0, min(1.0, confidence))

    def _get_context(self, lines: List[str], line_num: int, radius: int = 2) -> str:
        """Extrai contexto ao redor da linha."""
        start = max(0, line_num - radius - 1)
        end = min(len(lines), line_num + radius)
        return '\n'.join(lines[start:end])

    def _deduplicate(self, concepts: List[Concept]) -> List[Concept]:
        """Remove conceitos duplicados, mantendo o de maior confiança."""
        seen: Dict[str, Concept] = {}

        for concept in concepts:
            # Normalizar texto para comparação
            key = concept.text.lower().strip()

            if key not in seen or concept.confidence > seen[key].confidence:
                seen[key] = concept

        return list(seen.values())


class RelationshipMapper:
    """Mapeia relacionamentos entre conceitos."""

    RELATIONSHIP_PATTERNS: Dict[RelationType, List[str]] = {
        RelationType.REFERENCIA: [
            r'(?:conforme|segundo|de acordo com|ver|vide|cf\.)\s+(.+?)(?:\.|,|$)',
            r'(?:previsto|estabelecido)\s+(?:na|no|pela|pelo)\s+(.+?)(?:\.|,|$)',
        ],
        RelationType.DEPENDE: [
            r'(?:requer|necessita|exige|depende)\s+(.+?)(?:\.|,|$)',
            r'(?:após|antes de|mediante)\s+(.+?)(?:\.|,|$)',
        ],
        RelationType.IMPLEMENTA: [
            r'implementa\s+(.+?)(?:\.|,|$)',
            r'(?:baseado|fundamentado)\s+(?:em|na|no)\s+(.+?)(?:\.|,|$)',
        ],
        RelationType.COMPLEMENTA: [
            r'(?:complementa|adiciona|inclui)\s+(.+?)(?:\.|,|$)',
            r'(?:além de|também)\s+(.+?)(?:\.|,|$)',
        ],
    }

    def map_relationships(
        self,
        concepts: List[Concept],
        content: str,
    ) -> List[Relationship]:
        """Mapeia relacionamentos entre conceitos.

        Args:
            concepts: Lista de conceitos extraídos
            content: Conteúdo do documento

        Returns:
            Lista de relacionamentos identificados
        """
        relationships = []

        # Relacionamentos explícitos (por padrões)
        relationships.extend(self._extract_explicit(concepts, content))

        # Relacionamentos implícitos (por co-ocorrência)
        relationships.extend(self._extract_implicit(concepts))

        return relationships

    def _extract_explicit(
        self,
        concepts: List[Concept],
        content: str,
    ) -> List[Relationship]:
        """Extrai relacionamentos explícitos por padrões."""
        relationships = []
        concept_texts = {c.text.lower(): c for c in concepts}

        for rel_type, patterns in self.RELATIONSHIP_PATTERNS.items():
            for pattern in patterns:
                try:
                    for match in re.finditer(pattern, content, re.IGNORECASE):
                        target_text = match.group(1).strip().lower()

                        # Encontrar conceito alvo
                        for text, target_concept in concept_texts.items():
                            if text in target_text or target_text in text:
                                # Encontrar conceito fonte (contexto anterior)
                                context_start = max(0, match.start() - 200)
                                context = content[context_start:match.start()]

                                for source_text, source_concept in concept_texts.items():
                                    if source_text in context.lower():
                                        relationships.append(Relationship(
                                            source_id=source_concept.id,
                                            target_id=target_concept.id,
                                            type=rel_type,
                                            weight=0.7,
                                            evidence=match.group(0)[:100],
                                            line_number=content[:match.start()].count('\n') + 1,
                                        ))
                                        break
                except re.error:
                    continue

        return relationships

    def _extract_implicit(self, concepts: List[Concept]) -> List[Relationship]:
        """Extrai relacionamentos implícitos por co-ocorrência."""
        relationships = []

        for i, concept_a in enumerate(concepts):
            for concept_b in concepts[i + 1:]:
                # Mesma seção = potencialmente relacionado
                if concept_a.section == concept_b.section:
                    weight = 0.3

                    # Boost por proximidade de linhas
                    line_distance = abs(concept_a.line_number - concept_b.line_number)
                    if line_distance <= 3:
                        weight += 0.25
                    elif line_distance <= 7:
                        weight += 0.15

                    # Boost por keywords comuns
                    common_keywords = concept_a.keywords & concept_b.keywords
                    if common_keywords:
                        weight += min(0.2, len(common_keywords) * 0.08)

                    if weight >= 0.45:
                        relationships.append(Relationship(
                            source_id=concept_a.id,
                            target_id=concept_b.id,
                            type=RelationType.RELACIONADO,
                            weight=weight,
                            evidence=f"Co-ocorrência na seção: {concept_a.section}",
                            line_number=min(concept_a.line_number, concept_b.line_number),
                        ))

        return relationships


class SummaryGenerator:
    """Gerador de resumos hierárquicos."""

    def generate(
        self,
        sections: List[StructuredSection],
        concepts: List[Concept],
        max_length: int = 500,
    ) -> str:
        """Gera resumo hierárquico do documento.

        Args:
            sections: Seções do documento
            concepts: Conceitos extraídos
            max_length: Tamanho máximo do resumo

        Returns:
            Resumo em texto
        """
        parts = []

        # Estrutura principal (headers nível 1-2)
        main_sections = [s for s in sections if s.level <= 2]
        if main_sections:
            titles = [s.title for s in main_sections[:5]]
            parts.append(f"Estrutura: {', '.join(titles)}")

        # Top conceitos por tipo
        concepts_by_type: Dict[str, List[Concept]] = {}
        for c in concepts:
            ctype = c.type.value
            if ctype not in concepts_by_type:
                concepts_by_type[ctype] = []
            concepts_by_type[ctype].append(c)

        for ctype, type_concepts in concepts_by_type.items():
            top = sorted(type_concepts, key=lambda x: -x.confidence)[:3]
            if top:
                texts = [c.text[:40] for c in top]
                parts.append(f"{ctype.capitalize()}: {', '.join(texts)}")

        # Juntar partes
        summary = '. '.join(parts)
        if len(summary) > max_length:
            summary = summary[:max_length - 3] + '...'

        return summary


class ContextProcessor:
    """Processador principal de contexto."""

    def __init__(
        self,
        min_confidence: float = 0.4,
    ):
        """Inicializa processador.

        Args:
            min_confidence: Confiança mínima para conceitos
        """
        self.concept_extractor = ConceptExtractor(min_confidence)
        self.relationship_mapper = RelationshipMapper()
        self.summary_generator = SummaryGenerator()
        self.stats = ProcessingStats()

    def process_file(self, file_path: Path) -> StructuredDocument:
        """Processa arquivo único gerando documento estruturado.

        Args:
            file_path: Caminho do arquivo

        Returns:
            StructuredDocument com contexto completo
        """
        start_time = time.perf_counter()

        # Ler arquivo
        content, sections, metadata = read_file(file_path)

        # Extrair conceitos
        concepts = self.concept_extractor.extract(content, metadata, sections)

        # Mapear relacionamentos
        relationships = self.relationship_mapper.map_relationships(concepts, content)

        # Gerar resumo
        summary = self.summary_generator.generate(sections, concepts)

        # Atualizar estatísticas
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        self._update_stats(concepts, relationships, elapsed_ms)

        return StructuredDocument(
            metadata=metadata,
            full_content=content,
            sections=sections,
            concepts=concepts,
            relationships=relationships,
            summary=summary,
        )

    def process_directory(
        self,
        directory: Path,
        patterns: Optional[List[str]] = None,
    ) -> Tuple[List[StructuredDocument], ContextIndex]:
        """Processa diretório inteiro.

        Args:
            directory: Diretório a processar
            patterns: Padrões glob para filtrar arquivos (ex: ['*.md', '*.pdf'])

        Returns:
            Tupla (lista de documentos, índice cruzado)
        """
        if patterns is None:
            patterns = ['*.md', '*.txt', '*.yaml', '*.yml', '*.py', '*.pdf']

        documents = []
        index = ContextIndex()

        for pattern in patterns:
            for file_path in directory.rglob(pattern):
                if not file_path.is_file():
                    continue

                try:
                    doc = self.process_file(file_path)
                    documents.append(doc)

                    # Adicionar ao índice
                    for concept in doc.concepts:
                        index.add_concept(concept)

                except (FileNotFoundError, PermissionError, ValueError) as e:
                    print(f"Erro ao processar {file_path}: {e}")
                    continue

        return documents, index

    def _update_stats(
        self,
        concepts: List[Concept],
        relationships: List[Relationship],
        processing_time_ms: float,
    ) -> None:
        """Atualiza estatísticas de processamento."""
        self.stats.total_files += 1
        self.stats.total_concepts += len(concepts)
        self.stats.total_relationships += len(relationships)
        self.stats.processing_time_ms += processing_time_ms

        for concept in concepts:
            ctype = concept.type.value
            self.stats.concepts_by_type[ctype] = (
                self.stats.concepts_by_type.get(ctype, 0) + 1
            )

    def get_stats(self) -> ProcessingStats:
        """Retorna estatísticas de processamento."""
        return self.stats

    def reset_stats(self) -> None:
        """Reseta estatísticas."""
        self.stats = ProcessingStats()
