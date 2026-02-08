# src/context_engine/pips.py

"""Motor principal do PIPS (Protocolo de Processamento Iterativo com Persistência de Estado).

Implementa o ciclo Work-Save-Validate-Reset-Resume para processamento de tarefas
de longa duração com persistência de estado em arquivos externos.
"""

import hashlib
import os
import re
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from .pips_models import (
    CHECKPOINTS_FILE,
    CONFIG_DIR,
    CONTEXT_FILE,
    ERRORS_FILE,
    INSIGHTS_CONSOLIDATED_FILE,
    INSIGHTS_RAW_FILE,
    OUTPUT_DIR,
    PIPS_ROOT,
    PIPSConfig,
    PIPSState,
    PIPSStatus,
    PROGRESS_FILE,
    QUEUE_FILE,
    SCHEMA_FILE,
    SOURCE_DIR,
    SOURCE_HASHES_FILE,
    STATE_DIR,
    TODOS_FILE,
    Checkpoint,
    Insight,
    QueueItem,
    TodoItem,
    TodoStatus,
)


class PIPSEngine:
    """Motor principal do PIPS para gerenciamento de estado persistente."""

    def __init__(self, project_name: str, pips_root: Optional[Path] = None):
        """Inicializa o motor PIPS.

        Args:
            project_name: Nome do projeto (letras minúsculas, números, underscore)
            pips_root: Raiz do diretório PIPS (padrão: .pips/)
        """
        self.project_name = self._validate_project_name(project_name)
        self.pips_root = pips_root or PIPS_ROOT
        self.project_path = self.pips_root / f"projeto_{self.project_name}"
        self._config: Optional[PIPSConfig] = None
        self._state: Optional[PIPSState] = None

    @staticmethod
    def _validate_project_name(name: str) -> str:
        """Valida e normaliza nome do projeto."""
        name = name.strip().lower()
        if not re.match(r'^[a-z][a-z0-9_]*$', name):
            raise ValueError(
                "Nome de projeto inválido. Use apenas letras minúsculas, "
                "números e underscore, começando com letra."
            )
        return name

    # =========================================================================
    # Lifecycle Methods
    # =========================================================================

    def project_exists(self) -> bool:
        """Verifica se o projeto já existe."""
        return self.project_path.exists()

    def init_project(
        self,
        objective: str,
        source_files: List[Path],
        output_schema: Optional[Dict[str, Any]] = None,
        trigger_reason: str = "solicitação do usuário",
        chunk_size: int = 10000,
    ) -> PIPSState:
        """Inicializa novo projeto PIPS com estrutura de diretórios.

        Args:
            objective: Descrição do objetivo do projeto
            source_files: Lista de arquivos fonte a processar
            output_schema: Schema esperado para output (opcional)
            trigger_reason: Motivo de ativação do PIPS
            chunk_size: Tamanho de chunk em tokens estimados

        Returns:
            PIPSState inicial do projeto

        Raises:
            FileExistsError: Se o projeto já existe
            ValueError: Se objetivo ou source_files inválidos
        """
        if self.project_exists():
            raise FileExistsError(
                f"Projeto '{self.project_name}' já existe. "
                f"Use /pips delete {self.project_name} primeiro."
            )

        if not objective or len(objective.strip()) < 10:
            raise ValueError("Objetivo deve ter pelo menos 10 caracteres.")

        # source_files pode ser vazio - usuário adicionará arquivos depois

        # Criar estrutura de diretórios
        self._create_directory_structure()

        # Criar configuração
        self._config = PIPSConfig(
            project_name=self.project_name,
            objective=objective.strip(),
            output_schema=output_schema or {},
            source_files=[Path(f) for f in source_files],
            created_at=datetime.now(),
            trigger_reason=trigger_reason,
            chunk_size=chunk_size,
        )

        # Criar fila de processamento
        queue = self._create_initial_queue(source_files, chunk_size)

        # Criar estado inicial
        self._state = PIPSState(
            project_name=self.project_name,
            status=PIPSStatus.NAO_INICIADO,
            current_cycle=0,
            todos=[],
            queue=queue,
            checkpoints=[],
            errors=[],
        )

        # Persistir arquivos
        self._save_config()
        self._save_state()

        # Calcular e armazenar hashes dos arquivos fonte para verificação de integridade
        hash_count = self.store_initial_hashes()

        # Registrar checkpoint inicial
        self.create_checkpoint(
            "init",
            f"Projeto inicializado com sucesso. {hash_count} arquivo(s) com hash registrado."
        )

        return self._state

    def load_project(self) -> Tuple[PIPSConfig, PIPSState]:
        """Carrega projeto existente do disco.

        Returns:
            Tupla (PIPSConfig, PIPSState)

        Raises:
            FileNotFoundError: Se o projeto não existe
        """
        if not self.project_exists():
            raise FileNotFoundError(
                f"Projeto '{self.project_name}' não encontrado. "
                "Use /pips list para ver projetos disponíveis."
            )

        self._load_config()
        self._load_state()

        return self._config, self._state

    def delete_project(self, confirm: bool = False) -> bool:
        """Remove projeto PIPS completamente.

        Args:
            confirm: Deve ser True para confirmar a operação destrutiva

        Returns:
            True se removido com sucesso

        Raises:
            ValueError: Se confirm=False (proteção contra deleção acidental)
        """
        if not confirm:
            raise ValueError(
                "Operação destrutiva requer confirmação. "
                "Use delete_project(confirm=True) para confirmar."
            )

        if not self.project_exists():
            return False

        shutil.rmtree(self.project_path)
        self._config = None
        self._state = None
        return True

    # =========================================================================
    # Cycle Methods (Work-Save-Validate-Reset-Resume)
    # =========================================================================

    def work(self, item_id: Optional[str] = None) -> Optional[QueueItem]:
        """Inicia processamento de um item da fila.

        Args:
            item_id: ID específico do item (opcional, senão pega próximo)

        Returns:
            QueueItem em processamento ou None se fila vazia
        """
        if self._state is None:
            self.load_project()

        if item_id:
            item = next((i for i in self._state.queue if i.id == item_id), None)
        else:
            item = self._state.get_next_item()

        if item is None:
            return None

        # Atualizar status
        item.status = TodoStatus.EM_PROGRESSO
        self._state.status = PIPSStatus.EM_PROGRESSO
        self._state.current_cycle += 1

        self._save_state()
        self.create_checkpoint("work", f"Iniciado processamento de {item.source_file}")

        return item

    def save(
        self,
        item_id: str,
        raw_output: str,
        insights: Optional[List[str]] = None,
    ) -> None:
        """Persiste resultados de processamento de um item.

        Args:
            item_id: ID do item processado
            raw_output: Output bruto do processamento
            insights: Lista de insights extraídos (opcional)
        """
        if self._state is None:
            raise RuntimeError("Estado não carregado. Use load_project() primeiro.")

        # Encontrar item
        item = next((i for i in self._state.queue if i.id == item_id), None)
        if item is None:
            raise ValueError(f"Item '{item_id}' não encontrado na fila.")

        # Validar status - item deve estar em progresso para ser salvo
        if item.status == TodoStatus.CONCLUIDO:
            raise ValueError(
                f"Item '{item_id}' já foi concluído. "
                "Não é possível salvar resultado novamente."
            )

        if item.status not in (TodoStatus.PENDENTE, TodoStatus.EM_PROGRESSO):
            raise ValueError(
                f"Item '{item_id}' está com status '{item.status.value}'. "
                "Apenas itens pendentes ou em progresso podem ser salvos."
            )

        # Atualizar item
        item.status = TodoStatus.CONCLUIDO
        item.processed_at = datetime.now()

        # Atualizar contadores
        self._state.tokens_processed += item.token_estimate
        self._state.last_updated = datetime.now()

        # Append raw output
        self.append_raw_insight(raw_output, item.source_file.name)

        # Registrar insights se fornecidos
        if insights:
            for insight_text in insights:
                insight = Insight(
                    id=str(uuid.uuid4())[:8],
                    cycle_number=self._state.current_cycle,
                    source_file=str(item.source_file),
                    content=insight_text,
                )
                self._append_insight_to_raw(insight)

        # Verificar se deve consolidar automaticamente
        if self._config and self._config.auto_consolidate:
            completed = sum(
                1 for i in self._state.queue if i.status == TodoStatus.CONCLUIDO
            )
            if completed % self._config.consolidate_interval == 0:
                self._auto_consolidate()

        self._save_state()
        self.create_checkpoint("save", f"Salvo resultado de {item.source_file}")

    def validate(self) -> Tuple[bool, List[str]]:
        """Valida estado atual contra regras de integridade.

        Returns:
            Tupla (is_valid, list_of_errors)
        """
        if self._state is None:
            self.load_project()

        errors = []

        # Verificar estrutura de diretórios
        required_dirs = [CONFIG_DIR, STATE_DIR, OUTPUT_DIR, SOURCE_DIR]
        for dir_name in required_dirs:
            dir_path = self.project_path / dir_name
            if not dir_path.exists():
                errors.append(f"Diretório ausente: {dir_name}")

        # Verificar arquivos de configuração
        if not (self.project_path / CONFIG_DIR / CONTEXT_FILE).exists():
            errors.append("Arquivo context.md ausente")

        # Verificar consistência de estado
        if self._state:
            # Verificar se há itens órfãos
            queue_ids = {item.id for item in self._state.queue}
            for checkpoint in self._state.checkpoints:
                if checkpoint.action == "work":
                    # Verificar se item referenciado existe
                    pass  # Simplificado

            # Verificar progresso
            if self._state.current_cycle < 0:
                errors.append("Ciclo atual inválido (negativo)")

        is_valid = len(errors) == 0

        self._state.status = PIPSStatus.VALIDANDO
        self._save_state()
        self.create_checkpoint(
            "validate",
            f"Validação {'bem-sucedida' if is_valid else 'com erros'}",
        )

        return is_valid, errors

    def reset(self) -> None:
        """Prepara para nova sessão (flush caches internos).

        Chamado antes de reset de contexto do LLM.
        """
        if self._state is None:
            return

        self._state.status = PIPSStatus.PAUSADO
        self._state.last_updated = datetime.now()
        self._save_state()
        self.create_checkpoint("reset", "Sessão pausada para reset de contexto")

        # Limpar caches internos
        self._config = None
        self._state = None

    def resume(self) -> PIPSState:
        """Retoma processamento do último checkpoint válido.

        Returns:
            PIPSState carregado
        """
        config, state = self.load_project()

        state.status = PIPSStatus.EM_PROGRESSO
        state.last_updated = datetime.now()

        self._save_state()
        self.create_checkpoint(
            "resume",
            f"Retomado do ciclo {state.current_cycle}. "
            f"Progresso: {state.get_progress_percentage():.1f}%",
        )

        return state

    # =========================================================================
    # Infinite Memory Protocol Methods
    # =========================================================================

    def snapshot(
        self,
        trigger: str = "manual",
        include_context_summary: bool = True,
    ) -> Dict[str, Any]:
        """Cria snapshot rápido do estado atual para persistência.

        Chamado automaticamente pelo PreCompact hook ou manualmente.

        Args:
            trigger: Motivo do snapshot ('pre_compact', 'manual', 'periodic')
            include_context_summary: Se True, inclui resumo de contexto

        Returns:
            Dict com metadados do snapshot para auditoria
        """
        # Garantir que config E state estejam carregados (evita race condition)
        if self._state is None or self._config is None:
            self.load_project()

        timestamp = datetime.now()

        # Salvar estado atual
        self._save_state()

        # Criar checkpoint de snapshot
        progress_pct = self._state.get_progress_percentage()
        checkpoint = self.create_checkpoint(
            action=f"snapshot_{trigger}",
            notes=f"Snapshot automático - {progress_pct:.1f}% concluído",
        )

        # Metadados para auditoria
        snapshot_meta = {
            'timestamp': timestamp.isoformat(),
            'trigger': trigger,
            'project_name': self.project_name,
            'cycle': self._state.current_cycle,
            'progress_pct': progress_pct,
            'pending_items': len(self._state.get_pending_items()),
            'checkpoint_id': checkpoint.timestamp.isoformat(),
        }

        # Opcional: salvar resumo de contexto para reconstrução
        if include_context_summary:
            snapshot_meta['context_summary'] = self._generate_context_summary()

        # Registrar ação automatizada
        self.log_automated_action('snapshot', trigger, snapshot_meta)

        return snapshot_meta

    def _generate_context_summary(self) -> str:
        """Gera resumo compacto do contexto atual para reconstrução."""
        if self._config is None or self._state is None:
            return ""

        pending = self._state.get_pending_items()
        next_item = pending[0] if pending else None

        summary = f"""## Contexto PIPS: {self.project_name}
Objetivo: {self._config.objective[:200]}...
Progresso: {self._state.get_progress_percentage():.1f}%
Ciclo: {self._state.current_cycle}
"""

        if next_item:
            summary += f"""
Próximo item:
- Arquivo: {next_item.source_file.name}
- Chunk: {next_item.chunk_index + 1}/{next_item.total_chunks}
"""

        # Adicionar últimos insights se disponíveis
        if self._state.insights_consolidated:
            summary += f"""
Última síntese:
{self._state.insights_consolidated[:500]}...
"""

        return summary

    def get_resumable_status(self) -> Optional[Dict[str, Any]]:
        """Verifica se projeto tem trabalho resumível.

        Returns:
            Dict com informações de retomada, ou None se não existir.
            Se o projeto existir mas estiver corrompido, retorna dict com
            'error' key indicando o problema.
        """
        if not self.project_exists():
            return None

        try:
            self.load_project()
        except Exception as e:
            # Projeto existe mas está corrompido - retornar status de erro
            # para visibilidade em vez de silenciosamente ignorar
            return {
                'project_name': self.project_name,
                'status': 'erro',
                'error': f"Falha ao carregar projeto: {str(e)[:100]}",
                'recoverable': True,  # Tentar recover_from_corruption()
            }

        # Verificar se está em estado resumível
        resumable_states = {
            PIPSStatus.EM_PROGRESSO,
            PIPSStatus.PAUSADO,
            PIPSStatus.NAO_INICIADO,
        }

        if self._state.status not in resumable_states:
            return None

        pending = self._state.get_pending_items()
        if not pending:
            return None

        # Carregar últimos checkpoints
        checkpoints_path = self.project_path / CONFIG_DIR / CHECKPOINTS_FILE
        last_checkpoints = []
        if checkpoints_path.exists():
            try:
                lines = checkpoints_path.read_text(encoding='utf-8').strip().split('\n')
                # Filtrar linhas vazias e headers
                checkpoint_lines = [
                    ln for ln in lines
                    if ln.strip() and not ln.startswith('#')
                ]
                last_checkpoints = checkpoint_lines[-5:] if len(checkpoint_lines) >= 5 else checkpoint_lines
            except Exception:
                pass

        return {
            'project_name': self.project_name,
            'status': self._state.status.value,
            'objective': self._config.objective[:200] if self._config else '',
            'progress_pct': self._state.get_progress_percentage(),
            'pending_count': len(pending),
            'total_count': len(self._state.queue),
            'current_cycle': self._state.current_cycle,
            'last_updated': self._state.last_updated.isoformat(),
            'next_item': {
                'file': str(pending[0].source_file.name),
                'chunk': f"{pending[0].chunk_index + 1}/{pending[0].total_chunks}",
                'tokens': pending[0].token_estimate,
            } if pending else None,
            'last_checkpoints': last_checkpoints,
        }

    def verify_source_integrity(self) -> Tuple[bool, List[str]]:
        """Verifica integridade dos arquivos fonte via hash MD5.

        Compara hashes atuais com hashes registrados. Se nenhum hash
        estiver armazenado, cria o arquivo de hashes para futuras verificações.

        Returns:
            Tupla (is_valid, list_of_issues)
        """
        issues = []

        if self._config is None:
            self.load_project()

        if not self._config or not self._config.source_files:
            return True, []

        # Carregar hashes armazenados
        stored_hashes = self._load_source_hashes()
        hashes_updated = False

        for source_file in self._config.source_files:
            file_key = str(source_file.name)

            if not source_file.exists():
                issues.append(f"AUSENTE: {file_key}")
                continue

            # Calcular hash atual
            try:
                current_hash = self._calculate_file_hash(source_file)
                if not current_hash:
                    issues.append(f"ILEGÍVEL: {file_key}")
                    continue

                # Comparar com hash armazenado
                if file_key in stored_hashes:
                    stored_hash = stored_hashes[file_key]
                    if current_hash != stored_hash:
                        issues.append(
                            f"MODIFICADO: {file_key} "
                            f"(esperado: {stored_hash[:8]}..., atual: {current_hash[:8]}...)"
                        )
                else:
                    # Arquivo novo - registrar hash
                    stored_hashes[file_key] = current_hash
                    hashes_updated = True

            except Exception as e:
                issues.append(f"ERRO ao verificar {file_key}: {e}")

        # Salvar hashes atualizados se houve novos arquivos
        if hashes_updated:
            self._save_source_hashes(stored_hashes)

        is_valid = len(issues) == 0

        if not is_valid:
            self.log_error(f"Verificação de integridade falhou: {len(issues)} problema(s)")

        return is_valid, issues

    def _load_source_hashes(self) -> Dict[str, str]:
        """Carrega hashes armazenados de arquivos fonte."""
        hashes_path = self.project_path / CONFIG_DIR / SOURCE_HASHES_FILE
        if not hashes_path.exists():
            return {}

        try:
            with open(hashes_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
                return data.get('hashes', {})
        except Exception:
            return {}

    def _save_source_hashes(self, hashes: Dict[str, str]) -> None:
        """Salva hashes de arquivos fonte para verificação futura."""
        hashes_path = self.project_path / CONFIG_DIR / SOURCE_HASHES_FILE

        data = {
            'version': 1,
            'created_at': datetime.now().isoformat(),
            'hashes': hashes,
        }

        try:
            with open(hashes_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
                f.flush()
                os.fsync(f.fileno())
        except Exception as e:
            self.log_error(f"Erro ao salvar hashes: {e}")

    def store_initial_hashes(self) -> int:
        """Calcula e armazena hashes de todos os arquivos fonte.

        Chamado na inicialização do projeto para estabelecer baseline.

        Returns:
            Número de arquivos com hash calculado
        """
        if self._config is None:
            self.load_project()

        if not self._config or not self._config.source_files:
            return 0

        hashes = {}
        for source_file in self._config.source_files:
            if source_file.exists():
                file_hash = self._calculate_file_hash(source_file)
                if file_hash:
                    hashes[str(source_file.name)] = file_hash

        if hashes:
            self._save_source_hashes(hashes)

        return len(hashes)

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calcula hash MD5 de arquivo para verificação de integridade."""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ''

    def _serialize_for_json(self, obj: Any) -> Any:
        """Serializa objetos para JSON de forma segura.

        Converte datetime e Path para strings.
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Path):
            return str(obj)
        if isinstance(obj, dict):
            return {k: self._serialize_for_json(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [self._serialize_for_json(item) for item in obj]
        return obj

    def log_automated_action(
        self,
        action_type: str,
        trigger: str,
        details: Dict[str, Any],
    ) -> None:
        """Registra ação automatizada no log de auditoria.

        Args:
            action_type: Tipo de ação ('snapshot', 'pre_compact', 'session_resume')
            trigger: O que disparou a ação ('hook', 'manual', 'scheduled')
            details: Detalhes adicionais
        """
        import json

        timestamp = datetime.now().isoformat()
        cycle = self._state.current_cycle if self._state else 0

        # Serializar details para evitar TypeError com datetime/Path
        safe_details = self._serialize_for_json(details)

        audit_path = self.project_path / CONFIG_DIR / 'audit.log'
        try:
            with open(audit_path, 'a', encoding='utf-8') as f:
                f.write(
                    f"[{timestamp}] {action_type.upper()} | {trigger} | "
                    f"cycle={cycle} | {json.dumps(safe_details, ensure_ascii=False)}\n"
                )
        except Exception:
            # Falha silenciosa - não deve interromper operação principal
            pass

    def snapshot_with_recovery(self, trigger: str) -> Dict[str, Any]:
        """Snapshot com recuperação automática em caso de falha.

        Args:
            trigger: Motivo do snapshot

        Returns:
            Dict com metadados do snapshot ou informações de erro
        """
        try:
            return self.snapshot(trigger)
        except PermissionError as e:
            self.log_error(f"Permissão negada ao salvar snapshot: {e}")
            return self._emergency_snapshot(trigger)
        except IOError as e:
            self.log_error(f"Erro de I/O ao salvar snapshot: {e}")
            # IOError também tenta snapshot de emergência para consistência
            return self._emergency_snapshot(trigger)
        except Exception as e:
            self.log_error(f"Erro inesperado no snapshot: {e}")
            return self._emergency_snapshot(trigger)

    def _emergency_snapshot(self, trigger: str) -> Dict[str, Any]:
        """Snapshot de emergência em localização alternativa."""
        import tempfile

        emergency_data = {
            'timestamp': datetime.now().isoformat(),
            'project': self.project_name,
            'cycle': self._state.current_cycle if self._state else 0,
            'queue_count': len(self._state.queue) if self._state else 0,
            'trigger': trigger,
            'emergency': True,
        }

        # Tentar salvar em diretório temporário
        try:
            emergency_path = Path(tempfile.gettempdir()) / f"pips_emergency_{self.project_name}.yaml"
            with open(emergency_path, 'w', encoding='utf-8') as f:
                yaml.dump(emergency_data, f, allow_unicode=True)
            emergency_data['emergency_path'] = str(emergency_path)
        except Exception:
            pass

        return emergency_data

    def recover_from_corruption(self) -> Tuple[bool, str]:
        """Tenta recuperar projeto de estado corrompido.

        Estratégias de recuperação (em ordem):
        1. Restaurar do backup (progress.yaml.bak)
        2. Reconstruir estado + fila do config + checkpoints
        3. Estado mínimo com fila reconstruída

        Returns:
            Tupla (success, message)
        """
        progress_path = self.project_path / STATE_DIR / PROGRESS_FILE
        backup_path = progress_path.with_suffix('.yaml.bak')

        # 1. Tentar restaurar do backup
        if backup_path.exists():
            try:
                shutil.copy(backup_path, progress_path)
                self.load_project()
                self.log_automated_action(
                    'recovery', 'backup_restore',
                    {'source': str(backup_path)}
                )
                return True, "Restaurado do backup progress.yaml.bak"
            except Exception:
                pass

        # Tentar carregar config para reconstruir fila
        try:
            self._load_config()
        except Exception:
            self._config = None

        # 2. Tentar reconstruir do checkpoints.log com fila reconstruída
        checkpoints_path = self.project_path / CONFIG_DIR / CHECKPOINTS_FILE
        if checkpoints_path.exists():
            try:
                # Detectar último ciclo conhecido
                content = checkpoints_path.read_text(encoding='utf-8')
                last_cycle = 0
                for line in content.split('\n'):
                    if 'ciclo' in line.lower():
                        match = re.search(r'ciclo\s+(\d+)', line.lower())
                        if match:
                            last_cycle = max(last_cycle, int(match.group(1)))

                # Reconstruir fila dos arquivos fonte se config disponível
                queue = []
                if self._config and self._config.source_files:
                    queue = self._create_initial_queue(
                        self._config.source_files,
                        self._config.chunk_size,
                    )

                self._state = PIPSState(
                    project_name=self.project_name,
                    status=PIPSStatus.PAUSADO,
                    current_cycle=last_cycle,
                    todos=[],
                    queue=queue,
                    checkpoints=[],
                    errors=["Estado reconstruído de checkpoints.log"],
                )
                self._save_state()
                self.log_automated_action(
                    'recovery', 'checkpoint_reconstruction',
                    {'last_cycle': last_cycle, 'queue_items': len(queue)}
                )
                return True, (
                    f"Reconstruído a partir do checkpoints.log (ciclo {last_cycle}, "
                    f"{len(queue)} itens na fila)"
                )
            except Exception:
                pass

        # 3. Último recurso - estado mínimo com fila reconstruída
        try:
            # Tentar reconstruir fila mesmo no último recurso
            queue = []
            if self._config and self._config.source_files:
                queue = self._create_initial_queue(
                    self._config.source_files,
                    self._config.chunk_size,
                )

            self._state = PIPSState(
                project_name=self.project_name,
                status=PIPSStatus.ERRO if not queue else PIPSStatus.PAUSADO,
                current_cycle=0,
                todos=[],
                queue=queue,
                checkpoints=[],
                errors=["Estado corrompido - reconstruído com fila inicial"],
            )
            self._save_state()
            self.log_automated_action(
                'recovery', 'minimal_state',
                {'reason': 'all_recovery_methods_failed', 'queue_items': len(queue)}
            )
            if queue:
                return True, f"Reconstruído com fila inicial ({len(queue)} itens)"
            return True, "Reinicializado com estado mínimo (config ausente - requer reconstrução manual)"
        except Exception as e:
            return False, f"Falha na recuperação: {e}"

    # =========================================================================
    # Queue Management
    # =========================================================================

    def get_next_item(self) -> Optional[QueueItem]:
        """Retorna próximo item da fila de processamento."""
        if self._state is None:
            self.load_project()
        return self._state.get_next_item()

    def update_queue(self, items: List[QueueItem]) -> None:
        """Atualiza fila de processamento."""
        if self._state is None:
            raise RuntimeError("Estado não carregado.")
        self._state.queue = items
        self._save_state()

    @staticmethod
    def estimate_tokens(file_path: Path, fallback_estimate: int = 1000) -> int:
        """Estima tokens para arquivo (chars / 4 aproximadamente).

        Args:
            file_path: Caminho do arquivo
            fallback_estimate: Estimativa conservadora se arquivo não puder ser lido

        Returns:
            Estimativa de tokens (nunca retorna 0 para arquivos existentes)
        """
        if not file_path.exists():
            return 0

        try:
            # Tentar ler o arquivo
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            estimated = len(content) // 4
            # Garantir mínimo de 1 token para arquivos não vazios
            return max(1, estimated) if content else fallback_estimate
        except PermissionError:
            # Arquivo existe mas não pode ser lido - usar fallback
            return fallback_estimate
        except MemoryError:
            # Arquivo muito grande - estimar pelo tamanho em bytes
            try:
                file_size = file_path.stat().st_size
                return file_size // 4  # Aproximação conservadora
            except Exception:
                return fallback_estimate * 10  # Arquivo grande
        except Exception:
            # Outros erros - usar fallback conservador
            return fallback_estimate

    # =========================================================================
    # Todo Management
    # =========================================================================

    def add_todo(self, description: str, priority: int = 1) -> TodoItem:
        """Adiciona item à lista de tarefas."""
        if self._state is None:
            raise RuntimeError("Estado não carregado.")

        todo = TodoItem(
            id=str(uuid.uuid4())[:8],
            description=description,
            status=TodoStatus.PENDENTE,
            priority=priority,
        )
        self._state.todos.append(todo)
        self._save_state()
        return todo

    def update_todo(self, todo_id: str, status: TodoStatus) -> None:
        """Atualiza status de tarefa."""
        if self._state is None:
            raise RuntimeError("Estado não carregado.")

        todo = next((t for t in self._state.todos if t.id == todo_id), None)
        if todo:
            todo.status = status
            if status == TodoStatus.CONCLUIDO:
                todo.completed_at = datetime.now()
            self._save_state()

    def get_pending_todos(self) -> List[TodoItem]:
        """Retorna tarefas pendentes."""
        if self._state is None:
            return []
        return [t for t in self._state.todos if t.status == TodoStatus.PENDENTE]

    # =========================================================================
    # Output Management
    # =========================================================================

    def append_raw_insight(self, content: str, source: str = "") -> None:
        """Adiciona insight ao arquivo raw."""
        if self._state is None:
            raise RuntimeError("Estado não carregado.")

        raw_file = self.project_path / OUTPUT_DIR / INSIGHTS_RAW_FILE

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = f"\n## Ciclo {self._state.current_cycle} - {timestamp}\n"
        if source:
            entry += f"### Arquivo: {source}\n"
        entry += f"\n{content}\n\n---\n"

        with open(raw_file, 'a', encoding='utf-8') as f:
            f.write(entry)

        self._state.insights_raw += entry

    def update_consolidated(self, synthesis: str) -> None:
        """Atualiza síntese consolidada."""
        if self._state is None:
            raise RuntimeError("Estado não carregado.")

        consolidated_file = self.project_path / OUTPUT_DIR / INSIGHTS_CONSOLIDATED_FILE

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        header = f"# Síntese Consolidada\n\nÚltima atualização: {timestamp}\n"
        header += f"Ciclo: {self._state.current_cycle}\n"
        header += f"Progresso: {self._state.get_progress_percentage():.1f}%\n\n---\n\n"

        content = header + synthesis

        with open(consolidated_file, 'w', encoding='utf-8') as f:
            f.write(content)

        self._state.insights_consolidated = synthesis
        self._save_state()

    def finalize_output(self, final_content: str, filename: str) -> Path:
        """Gera entrega final.

        Args:
            final_content: Conteúdo final
            filename: Nome do arquivo de saída

        Returns:
            Path do arquivo gerado
        """
        if self._state is None:
            raise RuntimeError("Estado não carregado.")

        final_dir = self.project_path / OUTPUT_DIR / "final"
        final_dir.mkdir(exist_ok=True)

        output_path = final_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_content)

        self._state.status = PIPSStatus.CONCLUIDO
        self._save_state()
        self.create_checkpoint("finalize", f"Entrega final gerada: {filename}")

        return output_path

    # =========================================================================
    # Error Handling
    # =========================================================================

    def log_error(self, error: str) -> None:
        """Registra erro no log."""
        if self._state is None:
            raise RuntimeError("Estado não carregado.")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_entry = f"[{timestamp}] {error}"

        self._state.errors.append(error_entry)

        errors_file = self.project_path / STATE_DIR / ERRORS_FILE
        with open(errors_file, 'a', encoding='utf-8') as f:
            f.write(error_entry + "\n")

        self._save_state()

    def get_errors(self) -> List[str]:
        """Retorna lista de erros."""
        if self._state is None:
            return []
        return self._state.errors

    # =========================================================================
    # Checkpoint Management
    # =========================================================================

    def create_checkpoint(self, action: str, notes: str) -> Checkpoint:
        """Cria checkpoint de validação."""
        if self._state is None:
            # Permitir checkpoint mesmo sem estado (para init)
            checkpoint = Checkpoint(
                timestamp=datetime.now(),
                cycle_number=0,
                action=action,
                validation_result=True,
                notes=notes,
            )
        else:
            pending = len(self._state.get_pending_items())
            completed = len(self._state.queue) - pending

            checkpoint = Checkpoint(
                timestamp=datetime.now(),
                cycle_number=self._state.current_cycle,
                action=action,
                validation_result=True,
                notes=notes,
                items_processed=completed,
                items_remaining=pending,
            )
            self._state.checkpoints.append(checkpoint)

        # Append ao log de checkpoints
        self._append_checkpoint_log(checkpoint)

        return checkpoint

    def get_last_checkpoint(self) -> Optional[Checkpoint]:
        """Retorna último checkpoint."""
        if self._state is None or not self._state.checkpoints:
            return None
        return self._state.checkpoints[-1]

    # =========================================================================
    # Private Methods
    # =========================================================================

    def _create_directory_structure(self) -> None:
        """Cria estrutura de diretórios do projeto."""
        dirs = [
            self.project_path / CONFIG_DIR,
            self.project_path / STATE_DIR,
            self.project_path / OUTPUT_DIR,
            self.project_path / OUTPUT_DIR / "final",
            self.project_path / SOURCE_DIR,
        ]
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Criar arquivos iniciais vazios
        (self.project_path / OUTPUT_DIR / INSIGHTS_RAW_FILE).write_text(
            "# Insights Brutos\n\n", encoding='utf-8'
        )
        (self.project_path / OUTPUT_DIR / INSIGHTS_CONSOLIDATED_FILE).write_text(
            "# Síntese Consolidada\n\n*Ainda não consolidado.*\n", encoding='utf-8'
        )
        (self.project_path / STATE_DIR / ERRORS_FILE).write_text("", encoding='utf-8')
        (self.project_path / CONFIG_DIR / CHECKPOINTS_FILE).write_text(
            "# Checkpoints Log\n\n", encoding='utf-8'
        )

    def _create_initial_queue(
        self, source_files: List[Path], chunk_size: int
    ) -> List[QueueItem]:
        """Cria fila inicial de processamento."""
        queue = []
        for file_path in source_files:
            path = Path(file_path)
            tokens = self.estimate_tokens(path)
            num_chunks = max(1, (tokens + chunk_size - 1) // chunk_size)

            for chunk_idx in range(num_chunks):
                queue.append(
                    QueueItem(
                        id=str(uuid.uuid4())[:8],
                        source_file=path,
                        chunk_index=chunk_idx,
                        total_chunks=num_chunks,
                        status=TodoStatus.PENDENTE,
                        token_estimate=min(chunk_size, tokens - chunk_idx * chunk_size),
                    )
                )

        return queue

    def _save_config(self) -> None:
        """Salva configuração em disco."""
        if self._config is None:
            return

        # Salvar context.md
        context_path = self.project_path / CONFIG_DIR / CONTEXT_FILE
        context_content = self._format_context_md()
        context_path.write_text(context_content, encoding='utf-8')

        # Salvar schema.yaml
        schema_path = self.project_path / CONFIG_DIR / SCHEMA_FILE
        with open(schema_path, 'w', encoding='utf-8') as f:
            yaml.dump(self._config.output_schema, f, allow_unicode=True)

    def _load_config(self) -> None:
        """Carrega configuração do disco."""
        context_path = self.project_path / CONFIG_DIR / CONTEXT_FILE
        schema_path = self.project_path / CONFIG_DIR / SCHEMA_FILE

        # Parse context.md
        context_content = context_path.read_text(encoding='utf-8')
        objective = self._extract_objective_from_context(context_content)

        # Extrair parâmetros de execução do context.md
        config_params = self._extract_config_params_from_context(context_content)

        # Load schema.yaml
        output_schema = {}
        if schema_path.exists():
            with open(schema_path, 'r', encoding='utf-8') as f:
                output_schema = yaml.safe_load(f) or {}

        # Carregar source_files do progress.yaml se existir
        source_files = []
        progress_path = self.project_path / STATE_DIR / PROGRESS_FILE
        if progress_path.exists():
            with open(progress_path, 'r', encoding='utf-8') as f:
                state_dict = yaml.safe_load(f) or {}
                source_files = [Path(p) for p in state_dict.get('source_files', [])]

        # Reconstruir config completa
        self._config = PIPSConfig(
            project_name=self.project_name,
            objective=objective,
            output_schema=output_schema,
            source_files=source_files,
            created_at=config_params.get('created_at', datetime.now()),
            trigger_reason=config_params.get('trigger_reason', 'carregado do disco'),
            chunk_size=config_params.get('chunk_size', 10000),
            auto_consolidate=config_params.get('auto_consolidate', True),
            consolidate_interval=config_params.get('consolidate_interval', 5),
        )

    def _save_state(self) -> None:
        """Salva estado em disco."""
        if self._state is None:
            return

        # Salvar progress.yaml
        progress_path = self.project_path / STATE_DIR / PROGRESS_FILE

        # Incluir source_files da config para persistência
        source_files = []
        if self._config and self._config.source_files:
            source_files = [str(f) for f in self._config.source_files]

        state_dict = {
            'project_name': self._state.project_name,
            'status': self._state.status.value,
            'current_cycle': self._state.current_cycle,
            'last_updated': self._state.last_updated.isoformat(),
            'tokens_processed': self._state.tokens_processed,
            'estimated_remaining': self._state.estimated_remaining,
            'source_files': source_files,
            'queue': [
                {
                    'id': item.id,
                    'source_file': str(item.source_file),
                    'chunk_index': item.chunk_index,
                    'total_chunks': item.total_chunks,
                    'status': item.status.value,
                    'token_estimate': item.token_estimate,
                }
                for item in self._state.queue
            ],
            'todos': [
                {
                    'id': todo.id,
                    'description': todo.description,
                    'status': todo.status.value,
                    'priority': todo.priority,
                }
                for todo in self._state.todos
            ],
            'errors': self._state.errors,
        }

        with open(progress_path, 'w', encoding='utf-8') as f:
            yaml.dump(state_dict, f, allow_unicode=True, default_flow_style=False)
            f.flush()                    # Force Python buffer to OS
            os.fsync(f.fileno())         # Force OS buffer to disk

        # Atualizar todos.md (formato legível)
        self._update_todos_md()

        # Atualizar queue.md (formato legível)
        self._update_queue_md()

    def _load_state(self) -> None:
        """Carrega estado do disco."""
        progress_path = self.project_path / STATE_DIR / PROGRESS_FILE

        if not progress_path.exists():
            raise FileNotFoundError(f"Arquivo de estado não encontrado: {progress_path}")

        with open(progress_path, 'r', encoding='utf-8') as f:
            state_dict = yaml.safe_load(f)

        # Reconstruir queue
        queue = [
            QueueItem(
                id=item['id'],
                source_file=Path(item['source_file']),
                chunk_index=item['chunk_index'],
                total_chunks=item['total_chunks'],
                status=TodoStatus(item['status']),
                token_estimate=item['token_estimate'],
            )
            for item in state_dict.get('queue', [])
        ]

        # Reconstruir todos
        todos = [
            TodoItem(
                id=todo['id'],
                description=todo['description'],
                status=TodoStatus(todo['status']),
                priority=todo.get('priority', 1),
            )
            for todo in state_dict.get('todos', [])
        ]

        self._state = PIPSState(
            project_name=state_dict['project_name'],
            status=PIPSStatus(state_dict['status']),
            current_cycle=state_dict['current_cycle'],
            todos=todos,
            queue=queue,
            checkpoints=[],  # Checkpoints são append-only no log
            errors=state_dict.get('errors', []),
            last_updated=datetime.fromisoformat(state_dict['last_updated']),
            tokens_processed=state_dict.get('tokens_processed', 0),
            estimated_remaining=state_dict.get('estimated_remaining', 0),
        )

    def _format_context_md(self) -> str:
        """Formata arquivo context.md."""
        if self._config is None:
            return ""

        content = f"""# CONTEXTO DA TAREFA

## Objetivo Principal

{self._config.objective}

## Critérios de Sucesso

- [ ] Todos os arquivos fonte processados
- [ ] Insights consolidados e validados
- [ ] Entrega final gerada conforme schema

## Parâmetros de Execução

- Granularidade: {self._config.chunk_size} tokens por chunk
- Consolidação automática: {'Sim' if self._config.auto_consolidate else 'Não'}
- Intervalo de consolidação: {self._config.consolidate_interval} itens

## Arquivos Fonte

{chr(10).join(f'- {f}' for f in self._config.source_files)}

## Restrições

- Manter consistência entre insights raw e consolidados
- Registrar todas as ambiguidades e contradições
- Validar checkpoint antes de cada reset

---

Data de criação: {self._config.created_at.strftime('%Y-%m-%d %H:%M')}
Motivo de ativação: {self._config.trigger_reason}
Checksum: {self._calculate_checksum()}
"""
        return content

    def _extract_objective_from_context(self, content: str) -> str:
        """Extrai objetivo do context.md."""
        # Simplificado: procura seção "Objetivo Principal"
        lines = content.split('\n')
        in_objective = False
        objective_lines = []

        for line in lines:
            if '## Objetivo Principal' in line:
                in_objective = True
                continue
            if in_objective:
                if line.startswith('## '):
                    break
                objective_lines.append(line)

        return '\n'.join(objective_lines).strip()

    def _extract_config_params_from_context(self, content: str) -> Dict[str, Any]:
        """Extrai parâmetros de configuração do context.md.

        Returns:
            Dicionário com: chunk_size, auto_consolidate, consolidate_interval,
            created_at, trigger_reason
        """
        params: Dict[str, Any] = {}

        # Extrair granularidade (chunk_size)
        match = re.search(r'Granularidade:\s*(\d+)\s*tokens', content)
        if match:
            params['chunk_size'] = int(match.group(1))

        # Extrair auto_consolidate
        match = re.search(r'Consolidação automática:\s*(Sim|Não)', content)
        if match:
            params['auto_consolidate'] = match.group(1) == 'Sim'

        # Extrair consolidate_interval
        match = re.search(r'Intervalo de consolidação:\s*(\d+)\s*itens', content)
        if match:
            params['consolidate_interval'] = int(match.group(1))

        # Extrair data de criação
        match = re.search(r'Data de criação:\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})', content)
        if match:
            try:
                params['created_at'] = datetime.strptime(match.group(1), '%Y-%m-%d %H:%M')
            except ValueError:
                pass

        # Extrair motivo de ativação
        match = re.search(r'Motivo de ativação:\s*(.+?)(?:\n|$)', content)
        if match:
            params['trigger_reason'] = match.group(1).strip()

        return params

    def _calculate_checksum(self) -> str:
        """Calcula checksum do contexto."""
        if self._config is None:
            return ""
        content = f"{self._config.objective}{self._config.project_name}"
        return hashlib.md5(content.encode()).hexdigest()[:8]

    def _update_todos_md(self) -> None:
        """Atualiza arquivo todos.md (formato legível)."""
        if self._state is None:
            return

        todos_path = self.project_path / STATE_DIR / TODOS_FILE
        content = f"""# ESTADO DE PROCESSAMENTO

Última atualização: {self._state.last_updated.strftime('%Y-%m-%d %H:%M')}
Ciclo atual: {self._state.current_cycle}
Progresso: {self._state.get_progress_percentage():.1f}%

## Tarefas

| # | Descrição | Status | Prioridade |
|---|-----------|--------|------------|
"""
        for i, todo in enumerate(self._state.todos, 1):
            status_icon = {
                TodoStatus.PENDENTE: "⏳",
                TodoStatus.EM_PROGRESSO: "🔄",
                TodoStatus.CONCLUIDO: "✅",
                TodoStatus.BLOQUEADO: "❌",
            }.get(todo.status, "?")
            content += f"| {i} | {todo.description} | {status_icon} {todo.status.value} | {todo.priority} |\n"

        todos_path.write_text(content, encoding='utf-8')

    def _update_queue_md(self) -> None:
        """Atualiza arquivo queue.md (formato legível)."""
        if self._state is None:
            return

        queue_path = self.project_path / STATE_DIR / QUEUE_FILE
        completed = sum(1 for item in self._state.queue if item.status == TodoStatus.CONCLUIDO)
        pending = sum(1 for item in self._state.queue if item.status == TodoStatus.PENDENTE)

        content = f"""# FILA DE PROCESSAMENTO

Total: {len(self._state.queue)} itens
Concluídos: {completed}
Pendentes: {pending}

## Itens

| # | Arquivo | Chunk | Status | Tokens |
|---|---------|-------|--------|--------|
"""
        for i, item in enumerate(self._state.queue, 1):
            status_icon = {
                TodoStatus.PENDENTE: "⏳",
                TodoStatus.EM_PROGRESSO: "🔄",
                TodoStatus.CONCLUIDO: "✅",
                TodoStatus.BLOQUEADO: "❌",
            }.get(item.status, "?")
            content += f"| {i} | {item.source_file.name} | {item.chunk_index + 1}/{item.total_chunks} | {status_icon} | {item.token_estimate} |\n"

        queue_path.write_text(content, encoding='utf-8')

    def _append_checkpoint_log(self, checkpoint: Checkpoint) -> None:
        """Append checkpoint ao log."""
        checkpoints_path = self.project_path / CONFIG_DIR / CHECKPOINTS_FILE

        entry = (
            f"[{checkpoint.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] "
            f"Ciclo {checkpoint.cycle_number} | {checkpoint.action.upper()} | "
            f"Processados: {checkpoint.items_processed} | "
            f"Restantes: {checkpoint.items_remaining} | "
            f"{checkpoint.notes}\n"
        )

        with open(checkpoints_path, 'a', encoding='utf-8') as f:
            f.write(entry)

    def _append_insight_to_raw(self, insight: Insight) -> None:
        """Append insight formatado ao arquivo raw."""
        raw_path = self.project_path / OUTPUT_DIR / INSIGHTS_RAW_FILE

        entry = f"""
### Insight [{insight.id}]
**Fonte:** {insight.source_file}
**Ciclo:** {insight.cycle_number}

{insight.content}

"""
        if insight.evidence:
            entry += f'> "{insight.evidence}"\n\n'

        if insight.flags:
            entry += f"**Flags:** {', '.join(insight.flags)}\n\n"

        entry += "---\n"

        with open(raw_path, 'a', encoding='utf-8') as f:
            f.write(entry)

    def _auto_consolidate(self) -> None:
        """Consolidação automática de insights.

        Cria uma síntese básica dos insights raw coletados até o momento.
        Em implementação completa, chamaria LLM para sintetizar.
        """
        if self._state is None:
            return

        raw_path = self.project_path / OUTPUT_DIR / INSIGHTS_RAW_FILE
        if not raw_path.exists():
            return

        try:
            raw_content = raw_path.read_text(encoding='utf-8')

            # Extrair apenas os insights (ignorar cabeçalhos e metadados)
            insights = []
            current_insight = []
            in_insight = False

            for line in raw_content.split('\n'):
                if line.startswith('## Ciclo'):
                    if current_insight:
                        insights.append('\n'.join(current_insight).strip())
                    current_insight = []
                    in_insight = True
                elif line.startswith('---') and in_insight:
                    if current_insight:
                        insights.append('\n'.join(current_insight).strip())
                    current_insight = []
                    in_insight = False
                elif in_insight and line.strip():
                    current_insight.append(line)

            if current_insight:
                insights.append('\n'.join(current_insight).strip())

            # Criar síntese básica
            if insights:
                completed = sum(
                    1 for i in self._state.queue if i.status == TodoStatus.CONCLUIDO
                )
                total = len(self._state.queue)

                synthesis = f"""## Resumo de Processamento

**Itens processados:** {completed}/{total}
**Ciclo atual:** {self._state.current_cycle}

## Insights Coletados

"""
                for i, insight in enumerate(insights[-10:], 1):  # Últimos 10
                    # Limitar tamanho de cada insight
                    truncated = insight[:500] + '...' if len(insight) > 500 else insight
                    synthesis += f"### Insight {i}\n{truncated}\n\n"

                if len(insights) > 10:
                    synthesis += f"*... e mais {len(insights) - 10} insight(s) anteriores*\n"

                self.update_consolidated(synthesis)
                self.create_checkpoint(
                    "consolidate",
                    f"Consolidação automática: {len(insights)} insights processados"
                )
        except Exception as e:
            self.log_error(f"Erro na consolidação automática: {e}")


# =============================================================================
# Helper Functions
# =============================================================================


def should_trigger_pips(
    file_count: int,
    total_tokens: int,
    is_synthesis: bool = False,
    user_explicit: bool = False,
) -> Tuple[bool, str]:
    """Determina se PIPS deve ser ativado.

    Critérios:
    - Multi-file processing (>3 arquivos)
    - Volume > 50,000 tokens estimados
    - Síntese de fontes distribuídas
    - Solicitação explícita do usuário

    Args:
        file_count: Número de arquivos a processar
        total_tokens: Tokens estimados total
        is_synthesis: Se é tarefa de síntese de múltiplas fontes
        user_explicit: Se usuário solicitou explicitamente

    Returns:
        Tupla (should_trigger, reason)
    """
    if user_explicit:
        return True, "solicitação explícita do usuário"

    if file_count > 3:
        return True, f"processamento de múltiplos arquivos ({file_count} arquivos)"

    if total_tokens > 50000:
        return True, f"volume de dados ({total_tokens:,} tokens estimados)"

    if is_synthesis:
        return True, "síntese de informações distribuídas"

    return False, ""


def list_projects(pips_root: Optional[Path] = None) -> List[str]:
    """Lista todos os projetos PIPS existentes.

    Returns:
        Lista de nomes de projetos
    """
    root = pips_root or PIPS_ROOT
    if not root.exists():
        return []

    projects = []
    for item in root.iterdir():
        if item.is_dir() and item.name.startswith("projeto_"):
            projects.append(item.name.replace("projeto_", ""))

    return sorted(projects)


def delete_project(
    project_name: str,
    pips_root: Optional[Path] = None,
    confirm: bool = False,
) -> bool:
    """Remove projeto PIPS.

    Args:
        project_name: Nome do projeto
        pips_root: Raiz do diretório PIPS (opcional)
        confirm: Deve ser True para confirmar operação

    Returns:
        True se removido com sucesso
    """
    engine = PIPSEngine(project_name, pips_root)
    return engine.delete_project(confirm=confirm)


def get_all_resumable_projects(pips_root: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Retorna todos os projetos com trabalho resumível.

    Usado pelo Protocolo de Memória Infinita para detectar projetos ativos
    no início de sessão ou antes de compactação de contexto.

    Args:
        pips_root: Raiz do diretório PIPS (opcional)

    Returns:
        Lista de dicts com status de cada projeto resumível, ordenada
        por última atualização (mais recente primeiro)
    """
    projects = list_projects(pips_root)
    resumable = []

    for project_name in projects:
        try:
            engine = PIPSEngine(project_name, pips_root)
            status = engine.get_resumable_status()
            if status:
                # Incluir tanto projetos resumíveis quanto corrompidos
                # para dar visibilidade ao usuário
                resumable.append(status)
        except Exception as e:
            # Falha crítica na instanciação - reportar como erro
            resumable.append({
                'project_name': project_name,
                'status': 'erro',
                'error': f"Projeto inacessível: {str(e)[:100]}",
                'recoverable': False,
            })

    # Ordenar por última atualização (mais recente primeiro)
    resumable.sort(key=lambda x: x.get('last_updated', ''), reverse=True)

    return resumable
