# src/context_engine/pips_models.py

"""Estruturas de dados para o sistema PIPS (Protocolo de Processamento Iterativo com Persistência de Estado).

Define as dataclasses utilizadas para representar configuração, estado, tarefas,
filas de processamento e checkpoints do sistema PIPS.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class PIPSStatus(Enum):
    """Status do projeto PIPS."""
    NAO_INICIADO = "nao_iniciado"
    EM_PROGRESSO = "em_progresso"
    PAUSADO = "pausado"
    VALIDANDO = "validando"
    CONCLUIDO = "concluido"
    ERRO = "erro"


class TodoStatus(Enum):
    """Status de um item de tarefa."""
    PENDENTE = "pendente"
    EM_PROGRESSO = "em_progresso"
    CONCLUIDO = "concluido"
    BLOQUEADO = "bloqueado"


@dataclass
class PIPSConfig:
    """Configuração imutável do projeto PIPS.

    Armazenada em _config/context.md e _config/schema.yaml.
    Não deve ser alterada após a criação do projeto.
    """
    project_name: str
    objective: str
    output_schema: Dict[str, Any]
    source_files: List[Path]
    created_at: datetime
    trigger_reason: str
    chunk_size: int = 10000  # tokens estimados por chunk
    auto_consolidate: bool = True
    consolidate_interval: int = 5  # consolidar a cada N itens


@dataclass
class TodoItem:
    """Item individual na lista de tarefas.

    Representa uma tarefa de alto nível no processamento.
    """
    id: str
    description: str
    status: TodoStatus
    priority: int = 1  # 1 = mais alta
    dependencies: List[str] = field(default_factory=list)
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class QueueItem:
    """Item na fila de processamento.

    Representa um chunk específico de um arquivo fonte a ser processado.
    """
    id: str
    source_file: Path
    chunk_index: int
    total_chunks: int
    status: TodoStatus
    token_estimate: int
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None


@dataclass
class Checkpoint:
    """Registro de checkpoint de validação.

    Armazenado em _config/checkpoints.log para rastreamento do ciclo.
    """
    timestamp: datetime
    cycle_number: int
    action: str  # work, save, validate, reset, resume
    validation_result: bool
    notes: str
    items_processed: int = 0
    items_remaining: int = 0


@dataclass
class Insight:
    """Insight individual extraído durante processamento.

    Armazenado em _output/insights_raw.md.

    Para garantir confiabilidade científica, cada insight deve ser
    rastreável à sua fonte original via source_hash e source_section.
    """
    id: str
    cycle_number: int
    source_file: str
    content: str
    evidence: Optional[str] = None
    flags: List[str] = field(default_factory=list)  # AMBIGUIDADE, CONTRADICAO, VALIDAR
    timestamp: datetime = field(default_factory=datetime.now)
    # Campos de rastreabilidade científica (Protocolo de Memória Infinita)
    source_hash: Optional[str] = None    # MD5 do arquivo fonte no momento da extração
    source_page: Optional[int] = None    # Página (para PDFs)
    source_section: Optional[str] = None # Seção/capítulo do documento


@dataclass
class PIPSState:
    """Estado mutável do projeto PIPS.

    Representa o estado atual do processamento, atualizado a cada ciclo.
    Armazenado em _state/progress.yaml.
    """
    project_name: str
    status: PIPSStatus
    current_cycle: int
    todos: List[TodoItem]
    queue: List[QueueItem]
    checkpoints: List[Checkpoint]
    errors: List[str]

    # Conteúdo acumulado
    insights_raw: str = ""
    insights_consolidated: str = ""

    # Metadados de sessão
    last_updated: datetime = field(default_factory=datetime.now)
    tokens_processed: int = 0
    estimated_remaining: int = 0

    def get_progress_percentage(self) -> float:
        """Calcula percentual de progresso baseado na fila."""
        if not self.queue:
            return 0.0
        completed = sum(1 for item in self.queue if item.status == TodoStatus.CONCLUIDO)
        return (completed / len(self.queue)) * 100

    def get_pending_items(self) -> List[QueueItem]:
        """Retorna itens pendentes na fila."""
        return [item for item in self.queue if item.status == TodoStatus.PENDENTE]

    def get_next_item(self) -> Optional[QueueItem]:
        """Retorna próximo item a processar."""
        pending = self.get_pending_items()
        return pending[0] if pending else None


# Constantes para estrutura de diretórios
PIPS_ROOT = Path(".pips")
CONFIG_DIR = "_config"
STATE_DIR = "_state"
OUTPUT_DIR = "_output"
SOURCE_DIR = "_source"

# Nomes de arquivos padrão
CONTEXT_FILE = "context.md"
SCHEMA_FILE = "schema.yaml"
SOURCE_HASHES_FILE = "source_hashes.yaml"  # Hashes MD5 para verificação de integridade
CHECKPOINTS_FILE = "checkpoints.log"
TODOS_FILE = "todos.md"
QUEUE_FILE = "queue.md"
PROGRESS_FILE = "progress.yaml"
ERRORS_FILE = "errors.log"
INSIGHTS_RAW_FILE = "insights_raw.md"
INSIGHTS_CONSOLIDATED_FILE = "insights_consolidated.md"
