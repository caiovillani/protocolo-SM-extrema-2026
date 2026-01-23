# tests/test_pips.py

"""Testes para o sistema PIPS (Protocolo de Processamento Iterativo com Persistência de Estado)."""

import pytest
import shutil
from pathlib import Path
from datetime import datetime

from src.context_engine.commands import parse_command, parse_pips_command, PIPS_SUBCOMMANDS
from src.context_engine.pips import PIPSEngine, should_trigger_pips, list_projects, delete_project
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
        """Testa deleção de projeto."""
        project_path = initialized_engine.project_path
        assert project_path.exists()

        success = initialized_engine.delete_project()

        assert success
        assert not project_path.exists()


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

        success = delete_project("para_deletar", temp_pips_root)

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
