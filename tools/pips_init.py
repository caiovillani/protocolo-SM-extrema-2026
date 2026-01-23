#!/usr/bin/env python3
"""
Tool: PIPS Init
Descrição: Inicializa um novo projeto PIPS com estrutura completa

Uso:
    python tools/pips_init.py --name <nome> --objective <objetivo.md> --sources <dir>

Inputs:
    --name: Nome do projeto (sem espaços, letras minúsculas)
    --objective: Arquivo Markdown com objetivo do projeto OU texto direto
    --sources: Diretório ou lista de arquivos fonte

Outputs:
    - Estrutura de diretórios em .pips/projeto_<nome>/
    - Arquivo de configuração inicializado
    - Fila de processamento criada

Dependências:
    - pyyaml
"""

import argparse
import sys
from pathlib import Path

# Adicionar src ao path para imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.context_engine.pips import PIPSEngine, should_trigger_pips


def get_source_files(sources_arg: list) -> list[Path]:
    """Obtém lista de arquivos fonte a partir dos argumentos."""
    files = []

    for source in sources_arg:
        path = Path(source)

        if path.is_file():
            files.append(path)
        elif path.is_dir():
            # Adicionar todos os arquivos do diretório (não recursivo)
            for item in path.iterdir():
                if item.is_file() and not item.name.startswith('.'):
                    files.append(item)
        else:
            print(f"Aviso: '{source}' não encontrado, ignorando.")

    return files


def get_objective(objective_arg: str) -> str:
    """Obtém objetivo do arquivo ou texto direto."""
    path = Path(objective_arg)

    if path.exists() and path.is_file():
        return path.read_text(encoding='utf-8').strip()

    return objective_arg


def estimate_project_complexity(files: list[Path]) -> dict:
    """Estima complexidade do projeto."""
    total_tokens = sum(PIPSEngine.estimate_tokens(f) for f in files)

    return {
        'file_count': len(files),
        'total_tokens': total_tokens,
        'estimated_chunks': max(1, total_tokens // 10000),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Inicializar projeto PIPS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
    # Criar projeto com objetivo em texto
    python tools/pips_init.py --name meu_projeto --objective "Analisar transcricoes de reunioes" --sources ./dados/

    # Criar projeto com objetivo em arquivo
    python tools/pips_init.py --name analise --objective objetivo.md --sources arquivo1.txt arquivo2.txt
        """,
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Nome do projeto (letras minúsculas, números, underscore)",
    )
    parser.add_argument(
        "--objective",
        required=True,
        help="Objetivo do projeto (texto ou caminho para arquivo .md)",
    )
    parser.add_argument(
        "--sources",
        required=True,
        nargs="+",
        help="Diretório ou arquivos fonte para processamento",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=10000,
        help="Tamanho de chunk em tokens (padrão: 10000)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Apenas mostrar o que seria criado, sem executar",
    )

    args = parser.parse_args()

    # Obter arquivos fonte
    source_files = get_source_files(args.sources)
    if not source_files:
        print("Erro: Nenhum arquivo fonte encontrado nos caminhos especificados.")
        sys.exit(1)

    # Obter objetivo
    objective = get_objective(args.objective)
    if len(objective) < 10:
        print("Erro: Objetivo muito curto (mínimo 10 caracteres).")
        sys.exit(1)

    # Estimar complexidade
    complexity = estimate_project_complexity(source_files)

    # Verificar se PIPS é recomendado
    should_use, trigger_reason = should_trigger_pips(
        file_count=complexity['file_count'],
        total_tokens=complexity['total_tokens'],
    )

    print("=" * 60)
    print("  PIPS - Inicialização de Projeto")
    print("=" * 60)
    print()
    print(f"Nome do projeto: {args.name}")
    print(f"Objetivo: {objective[:100]}{'...' if len(objective) > 100 else ''}")
    print()
    print("📊 Análise de Complexidade:")
    print(f"   Arquivos: {complexity['file_count']}")
    print(f"   Tokens estimados: {complexity['total_tokens']:,}")
    print(f"   Chunks estimados: {complexity['estimated_chunks']}")
    print()

    if should_use:
        print(f"✅ PIPS recomendado: {trigger_reason}")
    else:
        print("ℹ️  PIPS pode não ser necessário para esta tarefa (poucas fontes/tokens)")
        print("   Continuando mesmo assim...")
    print()

    if args.dry_run:
        print("🔍 Modo dry-run: nenhuma alteração será feita.")
        print()
        print("Arquivos fonte detectados:")
        for f in source_files[:10]:
            print(f"   • {f}")
        if len(source_files) > 10:
            print(f"   ... e mais {len(source_files) - 10} arquivos")
        sys.exit(0)

    # Criar projeto
    try:
        engine = PIPSEngine(args.name)

        if engine.project_exists():
            print(f"❌ Erro: Projeto '{args.name}' já existe.")
            print(f"   Use: python tools/pips_init.py --name outro_nome ...")
            print(f"   Ou delete: /pips delete {args.name}")
            sys.exit(1)

        state = engine.init_project(
            objective=objective,
            source_files=source_files,
            trigger_reason=trigger_reason or "criado via CLI",
            chunk_size=args.chunk_size,
        )

        print("✅ Projeto criado com sucesso!")
        print()
        print(f"📁 Localização: {engine.project_path}")
        print(f"📊 Itens na fila: {len(state.queue)}")
        print()
        print("Próximos passos:")
        print(f"   1. Revise os arquivos em: {engine.project_path}/_config/")
        print(f"   2. Inicie processamento com: /pips resume {args.name}")
        print(f"   3. Acompanhe progresso com: /pips status {args.name}")

    except ValueError as e:
        print(f"❌ Erro de validação: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
