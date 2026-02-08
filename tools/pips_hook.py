#!/usr/bin/env python3
# tools/pips_hook.py
"""CLI tool for PIPS hooks integration.

Called by Claude Code hooks to execute PIPS operations automatically.
Guarantees execution of Python methods (unlike prompt-type hooks).

Usage:
    python tools/pips_hook.py snapshot         # PreCompact hook
    python tools/pips_hook.py status           # SessionStart hook
    python tools/pips_hook.py session_end      # SessionEnd hook (future)
"""

import sys
from pathlib import Path

# Fix Windows console encoding for Unicode output
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from context_engine.pips import (
    PIPSEngine,
    get_all_resumable_projects,
    list_projects,
)
from context_engine.pips_models import PIPSStatus


def snapshot_all_projects() -> None:
    """Snapshot all active PIPS projects before context compaction.

    Called by PreCompact hook to persist state.
    """
    projects = list_projects()
    if not projects:
        print("[MEMORIA INFINITA] Nenhum projeto PIPS ativo.")
        return

    saved_count = 0
    for project_name in projects:
        try:
            engine = PIPSEngine(project_name)
            if not engine.project_exists():
                continue

            engine.load_project()

            # Only snapshot non-completed projects
            if engine._state and engine._state.status != PIPSStatus.CONCLUIDO:
                result = engine.snapshot_with_recovery('pre_compact')
                if 'error' not in result:
                    progress = result.get('progress_pct', 0)
                    cycle = result.get('cycle', 0)
                    print(f"[MEMORIA INFINITA] Estado salvo: {project_name} - {progress:.1f}% - ciclo {cycle}")
                    saved_count += 1
                else:
                    print(f"[MEMORIA INFINITA] AVISO: Falha ao salvar {project_name}: {result.get('error')}")
        except Exception as e:
            print(f"[MEMORIA INFINITA] ERRO: {project_name}: {e}")

    if saved_count == 0:
        print("[MEMORIA INFINITA] Nenhum projeto ativo para salvar.")
    else:
        print(f"[MEMORIA INFINITA] {saved_count} projeto(s) salvo(s) com sucesso.")


def show_resumable_status() -> None:
    """Show status of all resumable PIPS projects.

    Called by SessionStart hook to inform user of pending work.
    """
    resumable = get_all_resumable_projects()

    if not resumable:
        print("Nenhum projeto PIPS ativo.")
        return

    # Status indicator mapping (ASCII-safe for Windows compatibility)
    status_emoji = {
        'nao_iniciado': '[.]',
        'em_progresso': '[>]',
        'pausado': '[||]',
        'validando': '[?]',
        'concluido': '[OK]',
        'erro': '[X]',
    }

    print()
    print("=" * 56)
    print("  PROJETOS PIPS ATIVOS - PROTOCOLO MEMORIA INFINITA")
    print("=" * 56)
    print()

    for proj in resumable:
        emoji = status_emoji.get(proj['status'], '❓')
        print(f"{emoji} {proj['project_name']}")

        if proj.get('objective'):
            obj_short = proj['objective'][:80] + "..." if len(proj['objective']) > 80 else proj['objective']
            print(f"   Objetivo: {obj_short}")

        print(f"   Progresso: {proj['pending_count']}/{proj['total_count']} pendentes ({proj['progress_pct']:.1f}% concluído)")
        print(f"   Ciclo: {proj['current_cycle']} | Atualizado: {proj['last_updated'][:16]}")

        if proj.get('next_item'):
            next_item = proj['next_item']
            print(f"   Próximo: {next_item['file']} (chunk {next_item['chunk']})")

        print()

    print("-" * 54)
    print("Comandos disponíveis:")
    print("  /pips resume <nome>  - Retomar processamento")
    print("  /pips status <nome>  - Ver status detalhado")
    print("  /pips memory         - Status do protocolo")
    print()


def session_end_snapshot() -> None:
    """Snapshot all projects at session end.

    Called by SessionEnd hook (if configured).
    """
    projects = list_projects()
    if not projects:
        return

    for project_name in projects:
        try:
            engine = PIPSEngine(project_name)
            if engine.project_exists():
                engine.load_project()
                if engine._state and engine._state.status not in {PIPSStatus.CONCLUIDO, PIPSStatus.ERRO}:
                    engine.snapshot_with_recovery('session_end')
        except Exception:
            pass  # Silent on session end


def main():
    """Main entry point for hook CLI."""
    if len(sys.argv) < 2:
        print("Uso: python tools/pips_hook.py <comando>")
        print("Comandos: snapshot, status, session_end")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "snapshot":
        snapshot_all_projects()
    elif command == "status":
        show_resumable_status()
    elif command == "session_end":
        session_end_snapshot()
    else:
        print(f"Comando desconhecido: {command}")
        print("Comandos válidos: snapshot, status, session_end")
        sys.exit(1)


if __name__ == "__main__":
    main()
