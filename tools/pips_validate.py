#!/usr/bin/env python3
"""
Tool: PIPS Validate
Descrição: Valida estado e integridade do projeto PIPS

Uso:
    python tools/pips_validate.py --project <nome> [--fix]

Inputs:
    --project: Nome do projeto PIPS
    --fix: Tenta corrigir inconsistências automaticamente

Outputs:
    - Relatório de validação em stdout
    - Arquivo de log atualizado

Dependências:
    - pyyaml
"""

import argparse
import sys
from pathlib import Path

# Adicionar src ao path para imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.context_engine.pips import PIPSEngine, list_projects
from src.context_engine.pips_models import (
    CONFIG_DIR,
    STATE_DIR,
    OUTPUT_DIR,
    SOURCE_DIR,
    CONTEXT_FILE,
    SCHEMA_FILE,
    PROGRESS_FILE,
    CHECKPOINTS_FILE,
    INSIGHTS_RAW_FILE,
    INSIGHTS_CONSOLIDATED_FILE,
)


def validate_directory_structure(project_path: Path) -> list[str]:
    """Valida estrutura de diretórios."""
    errors = []
    required_dirs = [CONFIG_DIR, STATE_DIR, OUTPUT_DIR, SOURCE_DIR]

    for dir_name in required_dirs:
        dir_path = project_path / dir_name
        if not dir_path.exists():
            errors.append(f"Diretório ausente: {dir_name}/")
        elif not dir_path.is_dir():
            errors.append(f"'{dir_name}' existe mas não é um diretório")

    return errors


def validate_config_files(project_path: Path) -> list[str]:
    """Valida arquivos de configuração."""
    errors = []
    config_dir = project_path / CONFIG_DIR

    required_files = [CONTEXT_FILE, SCHEMA_FILE, CHECKPOINTS_FILE]
    for filename in required_files:
        file_path = config_dir / filename
        if not file_path.exists():
            errors.append(f"Arquivo de configuração ausente: _config/{filename}")
        elif file_path.stat().st_size == 0 and filename != CHECKPOINTS_FILE:
            errors.append(f"Arquivo de configuração vazio: _config/{filename}")

    # Validar conteúdo de context.md
    context_path = config_dir / CONTEXT_FILE
    if context_path.exists():
        content = context_path.read_text(encoding='utf-8')
        if "## Objetivo Principal" not in content:
            errors.append("context.md não contém seção 'Objetivo Principal'")
        if len(content) < 100:
            errors.append("context.md muito curto (esperado > 100 caracteres)")

    return errors


def validate_state_files(project_path: Path) -> list[str]:
    """Valida arquivos de estado."""
    errors = []
    state_dir = project_path / STATE_DIR

    # Verificar progress.yaml
    progress_path = state_dir / PROGRESS_FILE
    if not progress_path.exists():
        errors.append("Arquivo de estado ausente: _state/progress.yaml")
    else:
        import yaml
        try:
            with open(progress_path, 'r', encoding='utf-8') as f:
                state_data = yaml.safe_load(f)

            # Validar campos obrigatórios
            required_fields = ['project_name', 'status', 'current_cycle', 'queue']
            for field in required_fields:
                if field not in state_data:
                    errors.append(f"Campo ausente em progress.yaml: {field}")

            # Validar status
            valid_statuses = ['nao_iniciado', 'em_progresso', 'pausado', 'validando', 'concluido', 'erro']
            if state_data.get('status') not in valid_statuses:
                errors.append(f"Status inválido: {state_data.get('status')}")

            # Validar ciclo
            if state_data.get('current_cycle', -1) < 0:
                errors.append("current_cycle negativo")

        except yaml.YAMLError as e:
            errors.append(f"Erro ao parsear progress.yaml: {e}")

    return errors


def validate_output_files(project_path: Path) -> list[str]:
    """Valida arquivos de output."""
    errors = []
    output_dir = project_path / OUTPUT_DIR

    # Verificar insights_raw.md
    raw_path = output_dir / INSIGHTS_RAW_FILE
    if not raw_path.exists():
        errors.append("Arquivo ausente: _output/insights_raw.md")

    # Verificar insights_consolidated.md
    consolidated_path = output_dir / INSIGHTS_CONSOLIDATED_FILE
    if not consolidated_path.exists():
        errors.append("Arquivo ausente: _output/insights_consolidated.md")

    # Verificar pasta final
    final_dir = output_dir / "final"
    if not final_dir.exists():
        errors.append("Diretório ausente: _output/final/")

    return errors


def validate_state_consistency(engine: PIPSEngine) -> list[str]:
    """Valida consistência entre arquivos de estado."""
    errors = []

    try:
        config, state = engine.load_project()

        # Verificar se todos os itens da fila têm IDs únicos
        queue_ids = [item.id for item in state.queue]
        if len(queue_ids) != len(set(queue_ids)):
            errors.append("Existem IDs duplicados na fila de processamento")

        # Verificar progresso
        completed = sum(1 for item in state.queue if item.status.value == 'concluido')
        total = len(state.queue)
        if total > 0:
            progress = (completed / total) * 100
            # Se está concluído mas progresso < 100%
            if state.status.value == 'concluido' and progress < 100:
                errors.append(
                    f"Status 'concluido' mas progresso é {progress:.1f}%"
                )

    except Exception as e:
        errors.append(f"Erro ao validar consistência: {e}")

    return errors


def fix_common_issues(project_path: Path) -> list[str]:
    """Tenta corrigir problemas comuns."""
    fixed = []

    # Criar diretórios ausentes
    for dir_name in [CONFIG_DIR, STATE_DIR, OUTPUT_DIR, SOURCE_DIR]:
        dir_path = project_path / dir_name
        if not dir_path.exists():
            dir_path.mkdir(parents=True)
            fixed.append(f"Criado diretório: {dir_name}/")

    # Criar pasta final se ausente
    final_dir = project_path / OUTPUT_DIR / "final"
    if not final_dir.exists():
        final_dir.mkdir()
        fixed.append("Criado diretório: _output/final/")

    # Criar arquivos de output vazios se ausentes
    output_dir = project_path / OUTPUT_DIR
    raw_path = output_dir / INSIGHTS_RAW_FILE
    if not raw_path.exists():
        raw_path.write_text("# Insights Brutos\n\n", encoding='utf-8')
        fixed.append(f"Criado arquivo: {INSIGHTS_RAW_FILE}")

    consolidated_path = output_dir / INSIGHTS_CONSOLIDATED_FILE
    if not consolidated_path.exists():
        consolidated_path.write_text(
            "# Síntese Consolidada\n\n*Ainda não consolidado.*\n",
            encoding='utf-8'
        )
        fixed.append(f"Criado arquivo: {INSIGHTS_CONSOLIDATED_FILE}")

    return fixed


def main():
    parser = argparse.ArgumentParser(
        description="Validar projeto PIPS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
    # Validar projeto
    python tools/pips_validate.py --project meu_projeto

    # Validar e corrigir
    python tools/pips_validate.py --project meu_projeto --fix

    # Listar projetos disponíveis
    python tools/pips_validate.py --list
        """,
    )
    parser.add_argument(
        "--project",
        help="Nome do projeto PIPS para validar",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Tentar corrigir problemas automaticamente",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Listar todos os projetos disponíveis",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Mostrar detalhes adicionais",
    )

    args = parser.parse_args()

    # Listar projetos
    if args.list:
        projects = list_projects()
        if not projects:
            print("Nenhum projeto PIPS encontrado.")
        else:
            print("Projetos PIPS disponíveis:")
            for p in projects:
                print(f"  • {p}")
        sys.exit(0)

    if not args.project:
        print("Erro: --project é obrigatório (ou use --list)")
        sys.exit(1)

    # Validar projeto
    try:
        engine = PIPSEngine(args.project)
    except ValueError as e:
        print(f"❌ Nome de projeto inválido: {e}")
        sys.exit(1)

    if not engine.project_exists():
        print(f"❌ Projeto '{args.project}' não encontrado.")
        projects = list_projects()
        if projects:
            print(f"   Projetos disponíveis: {', '.join(projects)}")
        sys.exit(1)

    print("=" * 60)
    print(f"  Validação PIPS: {args.project}")
    print("=" * 60)
    print()

    all_errors = []
    project_path = engine.project_path

    # 1. Validar estrutura de diretórios
    print("🔍 Verificando estrutura de diretórios...")
    errors = validate_directory_structure(project_path)
    all_errors.extend(errors)
    if errors:
        for e in errors:
            print(f"   ❌ {e}")
    else:
        print("   ✅ Estrutura de diretórios OK")

    # 2. Validar arquivos de configuração
    print("\n🔍 Verificando arquivos de configuração...")
    errors = validate_config_files(project_path)
    all_errors.extend(errors)
    if errors:
        for e in errors:
            print(f"   ❌ {e}")
    else:
        print("   ✅ Arquivos de configuração OK")

    # 3. Validar arquivos de estado
    print("\n🔍 Verificando arquivos de estado...")
    errors = validate_state_files(project_path)
    all_errors.extend(errors)
    if errors:
        for e in errors:
            print(f"   ❌ {e}")
    else:
        print("   ✅ Arquivos de estado OK")

    # 4. Validar arquivos de output
    print("\n🔍 Verificando arquivos de output...")
    errors = validate_output_files(project_path)
    all_errors.extend(errors)
    if errors:
        for e in errors:
            print(f"   ❌ {e}")
    else:
        print("   ✅ Arquivos de output OK")

    # 5. Validar consistência
    print("\n🔍 Verificando consistência de estado...")
    errors = validate_state_consistency(engine)
    all_errors.extend(errors)
    if errors:
        for e in errors:
            print(f"   ❌ {e}")
    else:
        print("   ✅ Consistência de estado OK")

    # Resumo
    print()
    print("-" * 60)

    if not all_errors:
        print("✅ Validação concluída: NENHUM ERRO ENCONTRADO")
        sys.exit(0)

    print(f"❌ Validação concluída: {len(all_errors)} erro(s) encontrado(s)")

    # Tentar corrigir se solicitado
    if args.fix:
        print()
        print("🔧 Tentando corrigir problemas...")
        fixed = fix_common_issues(project_path)
        if fixed:
            for f in fixed:
                print(f"   ✅ {f}")
            print()
            print("⚠️  Alguns problemas foram corrigidos.")
            print("   Execute a validação novamente para verificar.")
        else:
            print("   ℹ️  Nenhum problema pôde ser corrigido automaticamente.")
            print("   Correção manual pode ser necessária.")

    sys.exit(1)


if __name__ == "__main__":
    main()
