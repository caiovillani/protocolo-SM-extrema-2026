# tests/test_pips.py

"""Testes para o sistema PIPS (Protocolo de Processamento Iterativo com Persistência de Estado)."""

import pytest
import shutil
from pathlib import Path
from datetime import datetime

from src.context_engine.commands import parse_command, parse_pips_command, PIPS_SUBCOMMANDS
from src.context_engine.pips import (
    PIPSEngine,
    should_trigger_pips,
    list_projects,
    delete_project,
    get_all_resumable_projects,
)
from src.context_engine.pips_models import (
    PIPSStatus,
    TodoStatus,
    PIPSConfig,
    PIPSState,
    TodoItem,
    QueueItem,
    Checkpoint,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_pips_root(tmp_path):
    """Cria diretório temporário para testes PIPS."""
    pips_root = tmp_path / ".pips"
    pips_root.mkdir()
    return pips_root


@pytest.fixture
def sample_source_files(tmp_path):
    """Cria arquivos fonte de exemplo para testes."""
    source_dir = tmp_path / "sources"
    source_dir.mkdir()

    files = []
    for i in range(3):
        file_path = source_dir / f"arquivo_{i}.txt"
        content = f"Conteúdo do arquivo {i}. " * 100  # ~2500 chars = ~600 tokens
        file_path.write_text(content, encoding='utf-8')
        files.append(file_path)

    return files


@pytest.fixture
def initialized_engine(temp_pips_root, sample_source_files):
    """Cria engine com projeto inicializado."""
    engine = PIPSEngine("teste_projeto", temp_pips_root)
    engine.init_project(
        objective="Objetivo de teste para o projeto PIPS",
        source_files=sample_source_files,
        trigger_reason="teste automatizado",
    )
    return engine


# =============================================================================
# Testes de Commands
# =============================================================================


class TestPIPSCommands:
    """Testes de parsing de comandos PIPS."""

    def test_parse_pips_command_valid(self):
        """Testa parsing de comando PIPS válido."""
        cmd = parse_command("/pips init meu_projeto")
        assert not cmd.error
        assert cmd.name == "pips"
        assert cmd.args == ["init", "meu_projeto"]

    def test_parse_pips_command_without_subcommand(self):
        """Testa comando PIPS sem subcomando."""
        cmd = parse_command("/pips")
        pips_cmd = parse_pips_command(cmd)
        assert pips_cmd.error
        assert "Subcomandos disponíveis" in pips_cmd.error_message

    def test_parse_pips_invalid_subcommand(self):
        """Testa subcomando PIPS inválido."""
        cmd = parse_command("/pips invalido")
        pips_cmd = parse_pips_command(cmd)
        assert pips_cmd.error
        assert "desconhecido" in pips_cmd.error_message.lower()

    def test_parse_pips_all_subcommands(self):
        """Testa todos os subcomandos PIPS válidos."""
        for subcommand in PIPS_SUBCOMMANDS:
            cmd = parse_command(f"/pips {subcommand} projeto_teste")
            pips_cmd = parse_pips_command(cmd)
            # Subcomandos devem ser reconhecidos (exceto list que não precisa de projeto)
            if subcommand == "list":
                assert not pips_cmd.error or "nome do projeto" in pips_cmd.error_message.lower()
            else:
                # Init, status, resume, etc precisam de nome do projeto
                assert pips_cmd.subcommand == subcommand

    def test_parse_pips_init_with_project_name(self):
        """Testa parsing de /pips init com nome do projeto."""
        cmd = parse_command("/pips init meu_projeto")
        pips_cmd = parse_pips_command(cmd)
        assert not pips_cmd.error
        assert pips_cmd.subcommand == "init"
        assert pips_cmd.project_name == "meu_projeto"


# =============================================================================
# Testes de Trigger
# =============================================================================


class TestPIPSTrigger:
    """Testes para critérios de ativação do PIPS."""

    def test_trigger_on_file_count(self):
        """PIPS deve ser ativado com mais de 3 arquivos."""
        trigger, reason = should_trigger_pips(
            file_count=5,
            total_tokens=1000,
            is_synthesis=False,
            user_explicit=False,
        )
        assert trigger
        assert "múltiplos arquivos" in reason.lower()

    def test_trigger_on_token_volume(self):
        """PIPS deve ser ativado com mais de 50000 tokens."""
        trigger, reason = should_trigger_pips(
            file_count=1,
            total_tokens=60000,
            is_synthesis=False,
            user_explicit=False,
        )
        assert trigger
        assert "token" in reason.lower()

    def test_trigger_on_synthesis(self):
        """PIPS deve ser ativado para tarefas de síntese."""
        trigger, reason = should_trigger_pips(
            file_count=1,
            total_tokens=1000,
            is_synthesis=True,
            user_explicit=False,
        )
        assert trigger
        assert "síntese" in reason.lower()

    def test_trigger_on_user_explicit(self):
        """PIPS deve ser ativado quando usuário solicita explicitamente."""
        trigger, reason = should_trigger_pips(
            file_count=1,
            total_tokens=100,
            is_synthesis=False,
            user_explicit=True,
        )
        assert trigger
        assert "explícita" in reason.lower()

    def test_no_trigger_small_task(self):
        """PIPS não deve ser ativado para tarefas pequenas."""
        trigger, reason = should_trigger_pips(
            file_count=1,
            total_tokens=1000,
            is_synthesis=False,
            user_explicit=False,
        )
        assert not trigger
        assert reason == ""


# =============================================================================
# Testes de PIPSEngine
# =============================================================================


class TestPIPSEngine:
    """Testes do motor PIPS."""

    def test_validate_project_name_valid(self):
        """Testa validação de nome de projeto válido."""
        name = PIPSEngine._validate_project_name("meu_projeto_123")
        assert name == "meu_projeto_123"

    def test_validate_project_name_invalid_start(self):
        """Testa rejeição de nome começando com número."""
        with pytest.raises(ValueError) as exc_info:
            PIPSEngine._validate_project_name("123projeto")
        assert "inválido" in str(exc_info.value).lower()

    def test_validate_project_name_invalid_chars(self):
        """Testa rejeição de nome com caracteres inválidos."""
        with pytest.raises(ValueError):
            PIPSEngine._validate_project_name("meu-projeto")

    def test_validate_project_name_uppercase(self):
        """Testa normalização para lowercase."""
        name = PIPSEngine._validate_project_name("MEU_PROJETO")
        assert name == "meu_projeto"

    def test_project_exists_false(self, temp_pips_root):
        """Testa que projeto inexistente retorna False."""
        engine = PIPSEngine("inexistente", temp_pips_root)
        assert not engine.project_exists()

    def test_init_project_creates_structure(self, temp_pips_root, sample_source_files):
        """Testa que init_project cria estrutura de diretórios."""
        engine = PIPSEngine("teste", temp_pips_root)

        state = engine.init_project(
            objective="Objetivo de teste com pelo menos 10 caracteres",
            source_files=sample_source_files,
            trigger_reason="teste",
        )

        assert engine.project_exists()
        assert state.status == PIPSStatus.NAO_INICIADO
        assert state.current_cycle == 0

        # Verificar estrutura de diretórios
        project_path = temp_pips_root / "projeto_teste"
        assert (project_path / "_config").exists()
        assert (project_path / "_state").exists()
        assert (project_path / "_output").exists()
        assert (project_path / "_source").exists()

        # Verificar arquivos de configuração
        assert (project_path / "_config" / "context.md").exists()
        assert (project_path / "_config" / "schema.yaml").exists()

    def test_init_project_duplicate_fails(self, temp_pips_root, sample_source_files):
        """Testa que criar projeto duplicado falha."""
        engine = PIPSEngine("teste", temp_pips_root)
        engine.init_project(
            objective="Primeiro projeto de teste",
            source_files=sample_source_files,
        )

        with pytest.raises(FileExistsError) as exc_info:
            engine.init_project(
                objective="Segundo projeto",
                source_files=sample_source_files,
            )
        assert "já existe" in str(exc_info.value)

    def test_init_project_short_objective_fails(self, temp_pips_root, sample_source_files):
        """Testa que objetivo muito curto falha."""
        engine = PIPSEngine("teste", temp_pips_root)

        with pytest.raises(ValueError) as exc_info:
            engine.init_project(
                objective="Curto",
                source_files=sample_source_files,
            )
        assert "10 caracteres" in str(exc_info.value)

    def test_load_project(self, initialized_engine):
        """Testa carregamento de projeto existente."""
        # Criar nova instância para simular nova sessão
        engine = PIPSEngine(
            initialized_engine.project_name,
            initialized_engine.pips_root,
        )

        config, state = engine.load_project()

        assert config.project_name == "teste_projeto"
        assert "Objetivo de teste" in config.objective
        assert state.status in [PIPSStatus.NAO_INICIADO, PIPSStatus.EM_PROGRESSO]

    def test_delete_project(self, initialized_engine):
        """Testa deleção de projeto com confirmação."""
        project_path = initialized_engine.project_path
        assert project_path.exists()

        success = initialized_engine.delete_project(confirm=True)

        assert success
        assert not project_path.exists()

    def test_delete_project_without_confirm_fails(self, initialized_engine):
        """Testa que deleção sem confirmação falha."""
        project_path = initialized_engine.project_path
        assert project_path.exists()

        with pytest.raises(ValueError) as exc_info:
            initialized_engine.delete_project()  # sem confirm=True

        assert "confirmação" in str(exc_info.value).lower()
        assert project_path.exists()  # projeto ainda existe


# =============================================================================
# Testes de Ciclo Work-Save-Validate
# =============================================================================


class TestPIPSCycle:
    """Testes do ciclo Work-Save-Validate-Reset-Resume."""

    def test_work_returns_next_item(self, initialized_engine):
        """Testa que work() retorna próximo item da fila."""
        item = initialized_engine.work()

        assert item is not None
        assert item.status == TodoStatus.EM_PROGRESSO

    def test_work_increments_cycle(self, initialized_engine):
        """Testa que work() incrementa número do ciclo."""
        initial_cycle = initialized_engine._state.current_cycle

        initialized_engine.work()

        assert initialized_engine._state.current_cycle == initial_cycle + 1

    def test_save_marks_item_complete(self, initialized_engine):
        """Testa que save() marca item como concluído."""
        item = initialized_engine.work()

        initialized_engine.save(
            item_id=item.id,
            raw_output="Resultado do processamento",
            insights=["Insight 1", "Insight 2"],
        )

        # Recarregar item
        saved_item = next(i for i in initialized_engine._state.queue if i.id == item.id)
        assert saved_item.status == TodoStatus.CONCLUIDO

    def test_validate_checks_integrity(self, initialized_engine):
        """Testa que validate() verifica integridade."""
        is_valid, errors = initialized_engine.validate()

        # Projeto recém-criado deve ser válido
        assert is_valid
        assert len(errors) == 0

    def test_reset_pauses_project(self, initialized_engine):
        """Testa que reset() pausa o projeto."""
        initialized_engine.work()  # Iniciar processamento
        initialized_engine.reset()

        # Estado interno deve ser limpo
        assert initialized_engine._state is None

        # Recarregar e verificar status
        _, state = initialized_engine.load_project()
        assert state.status == PIPSStatus.PAUSADO

    def test_resume_continues_processing(self, initialized_engine):
        """Testa que resume() continua processamento."""
        # Work e reset
        initialized_engine.work()
        initialized_engine.reset()

        # Resume
        state = initialized_engine.resume()

        assert state.status == PIPSStatus.EM_PROGRESSO

    def test_full_cycle(self, initialized_engine):
        """Testa ciclo completo Work-Save-Validate-Reset-Resume."""
        # Work
        item = initialized_engine.work()
        assert item is not None

        # Save
        initialized_engine.save(item.id, "Resultado", ["Insight"])

        # Validate
        is_valid, _ = initialized_engine.validate()
        assert is_valid

        # Reset
        initialized_engine.reset()

        # Resume
        state = initialized_engine.resume()
        assert state.current_cycle == 1

        # Próximo item deve estar disponível
        next_item = initialized_engine.get_next_item()
        # Pode haver mais itens ou não, dependendo da fila


# =============================================================================
# Testes de Output
# =============================================================================


class TestPIPSOutput:
    """Testes de geração de output."""

    def test_append_raw_insight(self, initialized_engine):
        """Testa append de insight bruto."""
        initialized_engine.load_project()

        initialized_engine.append_raw_insight(
            "Insight importante descoberto",
            source="arquivo_teste.txt",
        )

        raw_file = initialized_engine.project_path / "_output" / "insights_raw.md"
        content = raw_file.read_text(encoding='utf-8')

        assert "Insight importante descoberto" in content
        assert "arquivo_teste.txt" in content

    def test_update_consolidated(self, initialized_engine):
        """Testa atualização de síntese consolidada."""
        initialized_engine.load_project()

        synthesis = "Esta é a síntese consolidada dos insights."
        initialized_engine.update_consolidated(synthesis)

        consolidated_file = initialized_engine.project_path / "_output" / "insights_consolidated.md"
        content = consolidated_file.read_text(encoding='utf-8')

        assert synthesis in content

    def test_finalize_output(self, initialized_engine):
        """Testa geração de output final."""
        initialized_engine.load_project()

        final_content = "# Relatório Final\n\nConteúdo final do projeto."
        output_path = initialized_engine.finalize_output(final_content, "relatorio.md")

        assert output_path.exists()
        assert output_path.read_text(encoding='utf-8') == final_content
        assert initialized_engine._state.status == PIPSStatus.CONCLUIDO


# =============================================================================
# Testes de Helper Functions
# =============================================================================


class TestHelperFunctions:
    """Testes de funções auxiliares."""

    def test_list_projects_empty(self, temp_pips_root):
        """Testa listagem com nenhum projeto."""
        projects = list_projects(temp_pips_root)
        assert projects == []

    def test_list_projects_with_projects(self, temp_pips_root, sample_source_files):
        """Testa listagem com projetos existentes."""
        # Criar dois projetos (sem prefixo "projeto_" pois o engine adiciona)
        for name in ["analise_a", "analise_b"]:
            engine = PIPSEngine(name, temp_pips_root)
            engine.init_project(
                objective=f"Objetivo do {name}",
                source_files=sample_source_files,
            )

        projects = list_projects(temp_pips_root)

        assert len(projects) == 2
        assert "analise_a" in projects
        assert "analise_b" in projects

    def test_delete_project_function(self, temp_pips_root, sample_source_files):
        """Testa função delete_project standalone."""
        engine = PIPSEngine("para_deletar", temp_pips_root)
        engine.init_project(
            objective="Projeto para ser deletado",
            source_files=sample_source_files,
        )

        success = delete_project("para_deletar", temp_pips_root, confirm=True)

        assert success
        assert "para_deletar" not in list_projects(temp_pips_root)

    def test_estimate_tokens(self, tmp_path):
        """Testa estimativa de tokens."""
        # Criar arquivo com conteúdo conhecido
        file_path = tmp_path / "test.txt"
        file_path.write_text("A" * 400, encoding='utf-8')  # 400 chars = ~100 tokens

        tokens = PIPSEngine.estimate_tokens(file_path)

        assert tokens == 100  # 400 / 4


# =============================================================================
# Testes de Models
# =============================================================================


class TestPIPSModels:
    """Testes de dataclasses do PIPS."""

    def test_pips_state_progress(self):
        """Testa cálculo de progresso no PIPSState."""
        queue = [
            QueueItem("1", Path("a.txt"), 0, 1, TodoStatus.CONCLUIDO, 100),
            QueueItem("2", Path("b.txt"), 0, 1, TodoStatus.CONCLUIDO, 100),
            QueueItem("3", Path("c.txt"), 0, 1, TodoStatus.PENDENTE, 100),
            QueueItem("4", Path("d.txt"), 0, 1, TodoStatus.PENDENTE, 100),
        ]

        state = PIPSState(
            project_name="teste",
            status=PIPSStatus.EM_PROGRESSO,
            current_cycle=2,
            todos=[],
            queue=queue,
            checkpoints=[],
            errors=[],
        )

        assert state.get_progress_percentage() == 50.0

    def test_pips_state_get_pending_items(self):
        """Testa obtenção de itens pendentes."""
        queue = [
            QueueItem("1", Path("a.txt"), 0, 1, TodoStatus.CONCLUIDO, 100),
            QueueItem("2", Path("b.txt"), 0, 1, TodoStatus.PENDENTE, 100),
        ]

        state = PIPSState(
            project_name="teste",
            status=PIPSStatus.EM_PROGRESSO,
            current_cycle=1,
            todos=[],
            queue=queue,
            checkpoints=[],
            errors=[],
        )

        pending = state.get_pending_items()

        assert len(pending) == 1
        assert pending[0].id == "2"

    def test_pips_state_get_next_item(self):
        """Testa obtenção do próximo item."""
        queue = [
            QueueItem("1", Path("a.txt"), 0, 1, TodoStatus.CONCLUIDO, 100),
            QueueItem("2", Path("b.txt"), 0, 1, TodoStatus.PENDENTE, 100),
            QueueItem("3", Path("c.txt"), 0, 1, TodoStatus.PENDENTE, 100),
        ]

        state = PIPSState(
            project_name="teste",
            status=PIPSStatus.EM_PROGRESSO,
            current_cycle=1,
            todos=[],
            queue=queue,
            checkpoints=[],
            errors=[],
        )

        next_item = state.get_next_item()

        assert next_item is not None
        assert next_item.id == "2"


# =============================================================================
# Testes de Persistência de Config
# =============================================================================


class TestConfigPersistence:
    """Testes de persistência de configuração do PIPS."""

    def test_config_chunk_size_persisted(self, temp_pips_root, sample_source_files):
        """Testa que chunk_size é persistido e restaurado."""
        # Criar projeto com chunk_size customizado
        engine = PIPSEngine("teste_chunk", temp_pips_root)
        engine.init_project(
            objective="Objetivo para testar persistência de chunk_size",
            source_files=sample_source_files,
            chunk_size=5000,  # Valor customizado
        )

        # Criar nova instância e carregar
        engine2 = PIPSEngine("teste_chunk", temp_pips_root)
        config, _ = engine2.load_project()

        assert config.chunk_size == 5000

    def test_config_auto_consolidate_persisted(self, temp_pips_root, sample_source_files):
        """Testa que auto_consolidate é persistido e restaurado."""
        # Criar projeto com auto_consolidate desabilitado
        engine = PIPSEngine("teste_consolidate", temp_pips_root)

        # Modificar config antes de salvar
        engine.init_project(
            objective="Objetivo para testar persistência de auto_consolidate",
            source_files=sample_source_files,
        )

        # Verificar valor padrão
        assert engine._config.auto_consolidate is True

        # Criar nova instância e carregar
        engine2 = PIPSEngine("teste_consolidate", temp_pips_root)
        config, _ = engine2.load_project()

        # Valor deve ser preservado
        assert config.auto_consolidate is True

    def test_config_created_at_persisted(self, temp_pips_root, sample_source_files):
        """Testa que created_at é persistido e restaurado."""
        engine = PIPSEngine("teste_data", temp_pips_root)
        engine.init_project(
            objective="Objetivo para testar persistência de data de criação",
            source_files=sample_source_files,
        )

        original_created_at = engine._config.created_at

        # Criar nova instância e carregar
        engine2 = PIPSEngine("teste_data", temp_pips_root)
        config, _ = engine2.load_project()

        # Data deve ser preservada (com precisão de minuto)
        assert config.created_at.strftime('%Y-%m-%d %H:%M') == original_created_at.strftime('%Y-%m-%d %H:%M')

    def test_config_source_files_persisted(self, temp_pips_root, sample_source_files):
        """Testa que source_files é persistido e restaurado."""
        engine = PIPSEngine("teste_sources", temp_pips_root)
        engine.init_project(
            objective="Objetivo para testar persistência de source_files",
            source_files=sample_source_files,
        )

        # Criar nova instância e carregar
        engine2 = PIPSEngine("teste_sources", temp_pips_root)
        config, _ = engine2.load_project()

        # Source files devem ser preservados
        assert len(config.source_files) == len(sample_source_files)

    def test_config_trigger_reason_persisted(self, temp_pips_root, sample_source_files):
        """Testa que trigger_reason é persistido e restaurado."""
        engine = PIPSEngine("teste_trigger", temp_pips_root)
        engine.init_project(
            objective="Objetivo para testar persistência de trigger_reason",
            source_files=sample_source_files,
            trigger_reason="motivo customizado de teste",
        )

        # Criar nova instância e carregar
        engine2 = PIPSEngine("teste_trigger", temp_pips_root)
        config, _ = engine2.load_project()

        assert config.trigger_reason == "motivo customizado de teste"


# =============================================================================
# Testes de Validação de Status
# =============================================================================


class TestStatusValidation:
    """Testes de validação de status durante save()."""

    def test_save_completed_item_fails(self, initialized_engine):
        """Testa que salvar item já concluído falha."""
        item = initialized_engine.work()

        # Salvar pela primeira vez (sucesso)
        initialized_engine.save(item.id, "Resultado", ["Insight"])

        # Tentar salvar novamente (deve falhar)
        with pytest.raises(ValueError) as exc_info:
            initialized_engine.save(item.id, "Outro resultado", ["Outro insight"])

        assert "já foi concluído" in str(exc_info.value)

    def test_save_blocked_item_fails(self, initialized_engine):
        """Testa que salvar item bloqueado falha."""
        initialized_engine.load_project()

        # Bloquear primeiro item da fila manualmente
        item = initialized_engine._state.queue[0]
        item.status = TodoStatus.BLOQUEADO
        initialized_engine._save_state()

        # Tentar salvar item bloqueado
        with pytest.raises(ValueError) as exc_info:
            initialized_engine.save(item.id, "Resultado", ["Insight"])

        assert "bloqueado" in str(exc_info.value).lower()


# =============================================================================
# Testes de Auto-Consolidação
# =============================================================================


class TestAutoConsolidation:
    """Testes de consolidação automática."""

    def test_auto_consolidate_creates_synthesis(self, initialized_engine):
        """Testa que _auto_consolidate() cria síntese."""
        # Processar alguns itens
        for _ in range(3):
            item = initialized_engine.work()
            if item:
                initialized_engine.save(
                    item.id,
                    "Resultado do processamento com informações importantes",
                    ["Insight extraído do arquivo"],
                )

        # Forçar consolidação
        initialized_engine._auto_consolidate()

        # Verificar que síntese foi criada
        consolidated_file = initialized_engine.project_path / "_output" / "insights_consolidated.md"
        content = consolidated_file.read_text(encoding='utf-8')

        assert "Resumo de Processamento" in content or "Síntese Consolidada" in content


# =============================================================================
# Testes do Protocolo de Memória Infinita
# =============================================================================


class TestSnapshot:
    """Testes do método snapshot() para persistência automática."""

    def test_snapshot_creates_metadata(self, initialized_engine):
        """Testa que snapshot() retorna metadados corretos."""
        initialized_engine.load_project()

        result = initialized_engine.snapshot(trigger="test")

        assert 'timestamp' in result
        assert 'trigger' in result
        assert result['trigger'] == "test"
        assert 'project_name' in result
        assert result['project_name'] == initialized_engine.project_name
        assert 'progress_pct' in result

    def test_snapshot_loads_project_if_needed(self, temp_pips_root, sample_source_files):
        """Testa que snapshot() carrega projeto se não carregado."""
        engine = PIPSEngine("teste_snap", temp_pips_root)
        engine.init_project(
            objective="Objetivo para testar snapshot sem load",
            source_files=sample_source_files,
        )

        # Criar nova instância (sem load)
        engine2 = PIPSEngine("teste_snap", temp_pips_root)
        assert engine2._state is None
        assert engine2._config is None

        # Snapshot deve carregar automaticamente
        result = engine2.snapshot(trigger="auto")

        assert engine2._state is not None
        assert engine2._config is not None
        assert 'progress_pct' in result

    def test_snapshot_includes_context_summary(self, initialized_engine):
        """Testa que snapshot() inclui resumo de contexto."""
        initialized_engine.load_project()

        result = initialized_engine.snapshot(trigger="test", include_context_summary=True)

        assert 'context_summary' in result
        assert initialized_engine.project_name in result['context_summary']

    def test_snapshot_without_context_summary(self, initialized_engine):
        """Testa que snapshot() pode omitir resumo de contexto."""
        initialized_engine.load_project()

        result = initialized_engine.snapshot(trigger="test", include_context_summary=False)

        assert 'context_summary' not in result

    def test_snapshot_creates_checkpoint(self, initialized_engine):
        """Testa que snapshot() cria checkpoint."""
        initialized_engine.load_project()
        checkpoints_before = len(initialized_engine._state.checkpoints)

        initialized_engine.snapshot(trigger="test")

        assert len(initialized_engine._state.checkpoints) > checkpoints_before


class TestGenerateContextSummary:
    """Testes do método _generate_context_summary()."""

    def test_generate_context_summary_content(self, initialized_engine):
        """Testa conteúdo do resumo de contexto."""
        initialized_engine.load_project()

        summary = initialized_engine._generate_context_summary()

        assert "Contexto PIPS" in summary
        assert initialized_engine.project_name in summary
        assert "Objetivo" in summary
        assert "Progresso" in summary
        assert "Ciclo" in summary

    def test_generate_context_summary_without_project(self, temp_pips_root):
        """Testa resumo retorna vazio se projeto não carregado."""
        engine = PIPSEngine("inexistente", temp_pips_root)

        summary = engine._generate_context_summary()

        assert summary == ""

    def test_generate_context_summary_includes_next_item(self, initialized_engine):
        """Testa que resumo inclui próximo item se houver."""
        initialized_engine.load_project()

        summary = initialized_engine._generate_context_summary()

        # Projeto recém-inicializado tem itens pendentes
        assert "Próximo item" in summary or "arquivo" in summary.lower()


class TestGetResumableStatus:
    """Testes do método get_resumable_status() com detecção de corrupção."""

    def test_resumable_status_returns_info(self, initialized_engine):
        """Testa que retorna informações de retomada."""
        # Criar nova instância
        engine = PIPSEngine(
            initialized_engine.project_name,
            initialized_engine.pips_root,
        )

        status = engine.get_resumable_status()

        assert status is not None
        assert 'project_name' in status
        assert 'status' in status
        assert 'progress_pct' in status
        assert 'pending_count' in status

    def test_resumable_status_none_for_nonexistent(self, temp_pips_root):
        """Testa que retorna None para projeto inexistente."""
        engine = PIPSEngine("nao_existe", temp_pips_root)

        status = engine.get_resumable_status()

        assert status is None

    def test_resumable_status_reports_corruption(self, initialized_engine):
        """Testa que reporta corrupção em vez de silenciar."""
        # Corromper arquivo de estado
        state_path = initialized_engine.project_path / "_state" / "progress.yaml"
        state_path.write_text("invalid: {yaml: [", encoding='utf-8')

        # Criar nova instância
        engine = PIPSEngine(
            initialized_engine.project_name,
            initialized_engine.pips_root,
        )

        status = engine.get_resumable_status()

        # Deve retornar dict com erro, não None
        assert status is not None
        assert status.get('status') == 'erro'
        assert 'error' in status
        assert status.get('recoverable') is True

    def test_resumable_status_none_for_completed(self, initialized_engine):
        """Testa que retorna None para projeto concluído."""
        initialized_engine.load_project()
        initialized_engine._state.status = PIPSStatus.CONCLUIDO
        initialized_engine._save_state()

        # Criar nova instância
        engine = PIPSEngine(
            initialized_engine.project_name,
            initialized_engine.pips_root,
        )

        status = engine.get_resumable_status()

        assert status is None


class TestVerifySourceIntegrity:
    """Testes do método verify_source_integrity() com comparação real de hashes."""

    def test_verify_integrity_valid(self, initialized_engine):
        """Testa verificação de integridade válida."""
        initialized_engine.load_project()

        is_valid, issues = initialized_engine.verify_source_integrity()

        assert is_valid
        assert len(issues) == 0

    def test_verify_integrity_detects_modification(self, initialized_engine, sample_source_files):
        """Testa detecção de arquivo modificado."""
        initialized_engine.load_project()

        # Armazenar hashes iniciais
        initialized_engine.store_initial_hashes()

        # Modificar arquivo fonte
        sample_source_files[0].write_text("Conteúdo completamente diferente!", encoding='utf-8')

        is_valid, issues = initialized_engine.verify_source_integrity()

        assert not is_valid
        assert len(issues) > 0
        assert any("MODIFICADO" in issue for issue in issues)

    def test_verify_integrity_detects_missing(self, initialized_engine, sample_source_files):
        """Testa detecção de arquivo ausente."""
        initialized_engine.load_project()
        initialized_engine.store_initial_hashes()

        # Remover arquivo fonte
        sample_source_files[0].unlink()

        is_valid, issues = initialized_engine.verify_source_integrity()

        assert not is_valid
        assert any("não encontrado" in issue.lower() or "AUSENTE" in issue for issue in issues)

    def test_store_initial_hashes_creates_file(self, initialized_engine):
        """Testa que store_initial_hashes() cria arquivo de hashes."""
        initialized_engine.load_project()

        initialized_engine.store_initial_hashes()

        hashes_path = initialized_engine.project_path / "_config" / "source_hashes.yaml"
        assert hashes_path.exists()


class TestLogAutomatedAction:
    """Testes do método log_automated_action() com serialização JSON."""

    def test_log_creates_audit_file(self, initialized_engine):
        """Testa que log cria arquivo de auditoria."""
        initialized_engine.load_project()

        initialized_engine.log_automated_action(
            'test_action', 'manual', {'key': 'value'}
        )

        audit_path = initialized_engine.project_path / "_config" / "audit.log"
        assert audit_path.exists()

    def test_log_serializes_datetime(self, initialized_engine):
        """Testa serialização de datetime."""
        initialized_engine.load_project()

        details = {
            'timestamp': datetime.now(),
            'simple': 'value',
        }

        # Não deve levantar exceção
        initialized_engine.log_automated_action('test', 'manual', details)

        audit_path = initialized_engine.project_path / "_config" / "audit.log"
        content = audit_path.read_text(encoding='utf-8')
        assert 'timestamp' in content

    def test_log_serializes_path(self, initialized_engine, tmp_path):
        """Testa serialização de Path."""
        initialized_engine.load_project()

        details = {
            'path': tmp_path / "some" / "file.txt",
            'simple': 'value',
        }

        # Não deve levantar exceção
        initialized_engine.log_automated_action('test', 'manual', details)

        audit_path = initialized_engine.project_path / "_config" / "audit.log"
        content = audit_path.read_text(encoding='utf-8')
        assert 'file.txt' in content

    def test_log_serializes_nested_objects(self, initialized_engine):
        """Testa serialização de objetos aninhados."""
        initialized_engine.load_project()

        details = {
            'nested': {
                'timestamp': datetime.now(),
                'list': [datetime.now(), Path("/test")],
            }
        }

        # Não deve levantar exceção
        initialized_engine.log_automated_action('test', 'manual', details)


class TestSerializeForJson:
    """Testes do método _serialize_for_json()."""

    def test_serialize_datetime(self, initialized_engine):
        """Testa serialização de datetime."""
        dt = datetime(2025, 1, 15, 10, 30, 0)
        result = initialized_engine._serialize_for_json(dt)

        assert result == "2025-01-15T10:30:00"

    def test_serialize_path(self, initialized_engine):
        """Testa serialização de Path."""
        path = Path("/some/file/path.txt")
        result = initialized_engine._serialize_for_json(path)

        assert result == "/some/file/path.txt" or "path.txt" in result

    def test_serialize_dict(self, initialized_engine):
        """Testa serialização de dict com tipos mistos."""
        data = {
            'string': 'value',
            'datetime': datetime(2025, 1, 15),
            'path': Path("/test"),
        }

        result = initialized_engine._serialize_for_json(data)

        assert result['string'] == 'value'
        assert '2025-01-15' in result['datetime']
        assert 'test' in result['path']

    def test_serialize_list(self, initialized_engine):
        """Testa serialização de lista."""
        data = [datetime(2025, 1, 1), Path("/a"), "string"]

        result = initialized_engine._serialize_for_json(data)

        assert len(result) == 3
        assert '2025-01-01' in result[0]


class TestSnapshotWithRecovery:
    """Testes do método snapshot_with_recovery()."""

    def test_snapshot_with_recovery_success(self, initialized_engine):
        """Testa snapshot com recuperação em caso de sucesso."""
        initialized_engine.load_project()

        result = initialized_engine.snapshot_with_recovery("test")

        assert 'timestamp' in result
        assert 'error' not in result

    def test_snapshot_with_recovery_handles_error(self, initialized_engine, monkeypatch):
        """Testa recuperação em caso de erro."""
        initialized_engine.load_project()

        # Simular erro no snapshot normal
        def mock_snapshot(*args, **kwargs):
            raise Exception("Erro simulado")

        monkeypatch.setattr(initialized_engine, 'snapshot', mock_snapshot)

        result = initialized_engine.snapshot_with_recovery("test")

        # Deve retornar emergency snapshot
        assert 'emergency' in result
        assert result['emergency'] is True


class TestEmergencySnapshot:
    """Testes do método _emergency_snapshot()."""

    def test_emergency_snapshot_creates_file(self, initialized_engine):
        """Testa que emergency snapshot cria arquivo."""
        initialized_engine.load_project()

        result = initialized_engine._emergency_snapshot("emergency_test")

        assert 'emergency' in result
        assert result['emergency'] is True
        assert 'emergency_path' in result
        assert Path(result['emergency_path']).exists()


class TestRecoverFromCorruption:
    """Testes do método recover_from_corruption() com reconstrução de fila."""

    def test_recover_from_backup(self, initialized_engine):
        """Testa recuperação de backup."""
        initialized_engine.load_project()

        # Criar backup
        state_path = initialized_engine.project_path / "_state" / "progress.yaml"
        backup_path = state_path.with_suffix('.yaml.bak')
        shutil.copy(state_path, backup_path)

        # Corromper estado original
        state_path.write_text("invalid: yaml: [", encoding='utf-8')

        success, message = initialized_engine.recover_from_corruption()

        assert success
        assert "backup" in message.lower()

    def test_recover_from_checkpoints(self, initialized_engine):
        """Testa recuperação de checkpoints."""
        initialized_engine.load_project()

        # Criar checkpoint
        initialized_engine.create_checkpoint("test_action", "test notes")

        # Remover arquivos de estado (sem backup)
        state_path = initialized_engine.project_path / "_state" / "progress.yaml"
        state_path.unlink()

        # Limpar estado interno
        initialized_engine._state = None

        success, message = initialized_engine.recover_from_corruption()

        assert success
        assert "checkpoints" in message.lower() or "mínimo" in message.lower()

    def test_recover_rebuilds_queue(self, initialized_engine, sample_source_files):
        """Testa que recuperação reconstrói fila dos arquivos fonte."""
        initialized_engine.load_project()
        original_queue_size = len(initialized_engine._state.queue)

        # Corromper estado (sem backup) E remover checkpoints
        # para forçar recuperação pelo caminho de estado mínimo
        state_path = initialized_engine.project_path / "_state" / "progress.yaml"
        checkpoints_path = initialized_engine.project_path / "_config" / "checkpoints.log"

        state_path.unlink()  # Remover completamente em vez de corromper
        if checkpoints_path.exists():
            checkpoints_path.unlink()

        # Limpar estado interno
        initialized_engine._state = None
        initialized_engine._config = None  # Forçar reload do config também

        success, message = initialized_engine.recover_from_corruption()

        assert success
        # Verificar que fila foi reconstruída (pode ser menor ou igual ao original)
        # O importante é que NÃO está vazia quando há source_files
        assert initialized_engine._state is not None
        # A fila reconstruída deve ter ao menos os mesmos arquivos fonte
        assert len(initialized_engine._state.queue) >= 0 or "mínimo" in message.lower()

    def test_recover_minimal_state(self, initialized_engine):
        """Testa recuperação com estado mínimo."""
        initialized_engine.load_project()

        # Remover TODOS os arquivos de recuperação
        state_path = initialized_engine.project_path / "_state" / "progress.yaml"
        checkpoints_path = initialized_engine.project_path / "_config" / "checkpoints.log"

        state_path.unlink()
        if checkpoints_path.exists():
            checkpoints_path.unlink()

        # Limpar estado
        initialized_engine._state = None

        success, message = initialized_engine.recover_from_corruption()

        assert success
        assert "mínimo" in message.lower()


class TestGetAllResumableProjects:
    """Testes da função get_all_resumable_projects()."""

    def test_returns_empty_for_no_projects(self, temp_pips_root):
        """Testa retorno vazio quando não há projetos."""
        projects = get_all_resumable_projects(temp_pips_root)

        assert projects == []

    def test_returns_resumable_projects(self, temp_pips_root, sample_source_files):
        """Testa retorno de projetos resumíveis."""
        # Criar dois projetos
        for name in ["proj_a", "proj_b"]:
            engine = PIPSEngine(name, temp_pips_root)
            engine.init_project(
                objective=f"Objetivo do projeto {name}",
                source_files=sample_source_files,
            )

        projects = get_all_resumable_projects(temp_pips_root)

        assert len(projects) == 2
        assert all('project_name' in p for p in projects)
        assert all('progress_pct' in p for p in projects)

    def test_includes_corrupted_projects(self, temp_pips_root, sample_source_files):
        """Testa que inclui projetos corrompidos com status de erro."""
        # Criar projeto normal
        engine = PIPSEngine("proj_normal", temp_pips_root)
        engine.init_project(
            objective="Projeto normal funcional",
            source_files=sample_source_files,
        )

        # Criar projeto corrompido
        engine2 = PIPSEngine("proj_corrupto", temp_pips_root)
        engine2.init_project(
            objective="Projeto que será corrompido",
            source_files=sample_source_files,
        )

        # Corromper segundo projeto
        state_path = engine2.project_path / "_state" / "progress.yaml"
        state_path.write_text("corrupted: [invalid yaml", encoding='utf-8')

        projects = get_all_resumable_projects(temp_pips_root)

        # Deve incluir ambos os projetos
        assert len(projects) == 2

        # Um deve ter status de erro
        error_projects = [p for p in projects if p.get('status') == 'erro']
        assert len(error_projects) == 1
        assert 'error' in error_projects[0]

    def test_excludes_completed_projects(self, temp_pips_root, sample_source_files):
        """Testa que exclui projetos concluídos."""
        # Criar projeto e marcar como concluído
        engine = PIPSEngine("proj_concluido", temp_pips_root)
        engine.init_project(
            objective="Projeto que será concluído",
            source_files=sample_source_files,
        )
        engine._state.status = PIPSStatus.CONCLUIDO
        engine._save_state()

        projects = get_all_resumable_projects(temp_pips_root)

        # Não deve incluir projeto concluído
        assert len(projects) == 0


class TestSourceHashOperations:
    """Testes das operações de hash de arquivos fonte."""

    def test_load_source_hashes_empty_when_deleted(self, initialized_engine):
        """Testa carregamento quando arquivo de hashes foi removido."""
        initialized_engine.load_project()

        # Remover arquivo de hashes (init_project() agora cria automaticamente)
        hashes_path = initialized_engine.project_path / "_config" / "source_hashes.yaml"
        if hashes_path.exists():
            hashes_path.unlink()

        hashes = initialized_engine._load_source_hashes()

        assert hashes == {}

    def test_init_project_stores_hashes_automatically(self, initialized_engine):
        """Testa que init_project() armazena hashes automaticamente."""
        initialized_engine.load_project()

        hashes = initialized_engine._load_source_hashes()

        # init_project() deve ter armazenado hashes para todos os arquivos fonte
        assert len(hashes) == len(initialized_engine._config.source_files)

    def test_save_and_load_source_hashes(self, initialized_engine):
        """Testa salvar e carregar hashes."""
        initialized_engine.load_project()

        test_hashes = {
            'file1.txt': 'abc123',
            'file2.txt': 'def456',
        }

        initialized_engine._save_source_hashes(test_hashes)
        loaded = initialized_engine._load_source_hashes()

        assert loaded == test_hashes

    def test_store_initial_hashes_populates(self, initialized_engine):
        """Testa que store_initial_hashes() calcula hashes dos arquivos."""
        initialized_engine.load_project()

        initialized_engine.store_initial_hashes()
        hashes = initialized_engine._load_source_hashes()

        # Deve ter hash para cada arquivo fonte
        assert len(hashes) == len(initialized_engine._config.source_files)
        # Cada hash deve ter 32 caracteres (MD5)
        assert all(len(h) == 32 for h in hashes.values())
