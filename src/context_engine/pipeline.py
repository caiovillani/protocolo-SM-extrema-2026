# src/context_engine/pipeline.py

"""Processing pipeline for the Context Engineering Engine.

Each function represents a stage of the pipeline. The implementations are
simplified placeholders that can be expanded later.
"""

from pathlib import Path
from typing import Any, Dict, List

# ---------------------------------------------------------------------------
# Stage 1 – Classification
# ---------------------------------------------------------------------------

def classify_request(command: Any) -> str:
    """Determine the request type based on the parsed command.

    Returns a string identifier such as ``"template"``, ``"auditoria"`` etc.
    """
    # For now we simply use the command name as the request type.
    return command.name

# ---------------------------------------------------------------------------
# Stage 2 – Input Validation
# ---------------------------------------------------------------------------

def validate_input(command: Any) -> List[str]:
    """Validate raw input data.

    For commands that include free‑text (e.g., ``/auditoria``) we could check for
    personally identifiable information. Here we return an empty list to signal
    no errors.
    """
    # Placeholder – real implementation would scan ``command.args`` for PII.
    return []

# ---------------------------------------------------------------------------
# Stage 3 – Load Context / Resources
# ---------------------------------------------------------------------------

def load_context(request_type: str) -> Dict[str, Any]:
    """Load the resources required for the given request type.

    The function delegates to the ``resources`` module. It returns a dictionary
    with the loaded data, e.g. ``{"template": {...}}``.
    """
    from . import resources

    context: Dict[str, Any] = {}
    if request_type == "template":
        # Expect the first argument to be the template id.
        # The caller will pass the full command object later, but we can load a
        # generic template list here if needed.
        # For now we load nothing and let the processing stage handle it.
        pass
    elif request_type == "auditoria":
        # Load normative resources that are used during audits.
        try:
            context["normativas"] = resources.get_normativa("normativa_cfm")
        except Exception:
            context["normativas"] = {}
    elif request_type == "pips":
        # PIPS loads its own context from project state files
        context["pips_enabled"] = True
    # Additional request types can be added similarly.
    return context

# ---------------------------------------------------------------------------
# Stage 4 – Core Processing
# ---------------------------------------------------------------------------

def process_request(command: Any, context: Dict[str, Any]) -> str:
    """Generate the final output based on the command and loaded context.

    This is a very high‑level placeholder. Real logic would assemble a template,
    fill fields, run audits, etc.
    """
    if command.name == "template":
        template_id = command.args[0] if command.args else "unknown"
        # In a full implementation we would fetch the template YAML and render it.
        return f"[Template {template_id}] – conteúdo gerado aqui."
    elif command.name == "auditoria":
        return "[Auditoria] – análise de conformidade gerada aqui."
    elif command.name == "pips":
        return process_pips_request(command, context)
    elif command.name == "contexto":
        return process_contexto_request(command, context)
    else:
        return f"Comando '{command.name}' processado (placeholder)."

# ---------------------------------------------------------------------------
# Stage 5 – Output Validation
# ---------------------------------------------------------------------------

def validate_output(output: str) -> List[str]:
    """Validate the generated output before returning it to the user.

    Checks could include length limits, prohibited terms, etc. Here we simply
    return an empty list to indicate no problems.
    """
    return []


# ---------------------------------------------------------------------------
# PIPS Processing
# ---------------------------------------------------------------------------

def process_pips_request(command: Any, context: Dict[str, Any]) -> str:
    """Process PIPS-specific commands.

    Args:
        command: Comando parseado (deve ser /pips)
        context: Contexto carregado (com pips_enabled=True)

    Returns:
        String com resultado do processamento
    """
    from .commands import parse_pips_command

    pips_cmd = parse_pips_command(command)
    if pips_cmd.error:
        return pips_cmd.error_message or "Erro desconhecido no comando PIPS."

    if pips_cmd.subcommand == "init":
        return _pips_init(pips_cmd)
    elif pips_cmd.subcommand == "status":
        return _pips_status(pips_cmd)
    elif pips_cmd.subcommand == "resume":
        return _pips_resume(pips_cmd)
    elif pips_cmd.subcommand == "list":
        return _pips_list()
    elif pips_cmd.subcommand == "validate":
        return _pips_validate(pips_cmd)
    elif pips_cmd.subcommand == "finalize":
        return _pips_finalize(pips_cmd)
    elif pips_cmd.subcommand == "delete":
        return _pips_delete(pips_cmd)

    return f"Subcomando PIPS não implementado: {pips_cmd.subcommand}"


def _pips_init(cmd: Any) -> str:
    """Initialize new PIPS project."""
    from .pips import PIPSEngine

    project_name = cmd.project_name

    # Extrair objetivo dos argumentos adicionais
    # Formato: /pips init <nome> [objetivo...]
    objective = " ".join(cmd.args[2:]) if len(cmd.args) > 2 else ""

    if not objective:
        return (
            f"Uso: /pips init {project_name} <objetivo>\n"
            "Exemplo: /pips init meu_projeto Analisar transcricoes de reunioes\n\n"
            "Após criar o projeto, adicione arquivos fonte ao diretório:\n"
            f"  .pips/projeto_{project_name}/_source/"
        )

    try:
        engine = PIPSEngine(project_name)

        if engine.project_exists():
            return (
                f"Projeto '{project_name}' já existe.\n"
                f"Use /pips delete {project_name} para remover ou "
                f"/pips status {project_name} para ver detalhes."
            )

        # Verificar se há arquivos no diretório _source/
        source_dir = engine.project_path / "_source"
        source_dir.mkdir(parents=True, exist_ok=True)

        # Coletar arquivos .md e .txt existentes no _source/
        source_files = list(source_dir.glob("*.md")) + list(source_dir.glob("*.txt"))

        # Se não há arquivos, criar projeto vazio (usuário adicionará depois)
        if not source_files:
            # Usar lista vazia - projeto será inicializado sem fila
            source_files = []

        state = engine.init_project(
            objective=objective,
            source_files=source_files,
            trigger_reason="criado via /pips init",
        )

        return (
            f"Projeto PIPS '{project_name}' criado com sucesso!\n\n"
            f"Objetivo: {objective}\n\n"
            "Próximos passos:\n"
            f"1. Adicione arquivos fonte em: .pips/projeto_{project_name}/_source/\n"
            f"2. Execute /pips resume {project_name} para iniciar processamento\n"
            f"3. Use /pips status {project_name} para acompanhar progresso"
        )

    except ValueError as e:
        return f"Erro ao criar projeto: {e}"
    except Exception as e:
        return f"Erro inesperado ao criar projeto: {e}"


def _pips_status(cmd: Any) -> str:
    """Show PIPS project status."""
    from .pips import PIPSEngine, list_projects

    project_name = cmd.project_name

    # Se nenhum projeto especificado, mostrar lista
    if not project_name:
        return _pips_list()

    try:
        engine = PIPSEngine(project_name)

        if not engine.project_exists():
            projects = list_projects()
            if projects:
                return (
                    f"Projeto '{project_name}' não encontrado.\n"
                    f"Projetos disponíveis: {', '.join(projects)}"
                )
            return (
                f"Projeto '{project_name}' não encontrado.\n"
                "Nenhum projeto PIPS existe. Use /pips init <nome> <objetivo> para criar."
            )

        config, state = engine.load_project()

        progress = state.get_progress_percentage()
        pending = len(state.get_pending_items())
        total = len(state.queue)
        completed = total - pending

        status_emoji = {
            "nao_iniciado": "⏸️",
            "em_progresso": "▶️",
            "pausado": "⏸️",
            "validando": "🔍",
            "concluido": "✅",
            "erro": "❌",
        }.get(state.status.value, "❓")

        output = f"""
═══════════════════════════════════════════════════
  PIPS: {project_name}
═══════════════════════════════════════════════════

{status_emoji} Status: {state.status.value.upper()}
📊 Progresso: {progress:.1f}% ({completed}/{total} itens)
🔄 Ciclo atual: {state.current_cycle}

📝 Objetivo:
{config.objective[:200]}{'...' if len(config.objective) > 200 else ''}

📁 Arquivos na fila: {total}
✅ Processados: {completed}
⏳ Pendentes: {pending}

🕐 Última atualização: {state.last_updated.strftime('%Y-%m-%d %H:%M')}
"""

        if state.errors:
            output += f"\n⚠️ Erros registrados: {len(state.errors)}\n"

        last_checkpoint = engine.get_last_checkpoint()
        if last_checkpoint:
            output += f"\n📍 Último checkpoint: {last_checkpoint.action} ({last_checkpoint.notes})\n"

        return output.strip()

    except Exception as e:
        return f"Erro ao carregar status: {e}"


def _pips_resume(cmd: Any) -> str:
    """Resume PIPS project processing."""
    from .pips import PIPSEngine

    project_name = cmd.project_name

    try:
        engine = PIPSEngine(project_name)

        if not engine.project_exists():
            return (
                f"Projeto '{project_name}' não encontrado.\n"
                "Use /pips list para ver projetos disponíveis."
            )

        state = engine.resume()

        next_item = state.get_next_item()
        if next_item is None:
            return (
                f"Projeto '{project_name}' retomado, mas não há itens pendentes.\n"
                f"Use /pips finalize {project_name} para gerar entrega final."
            )

        progress = state.get_progress_percentage()

        return f"""
Projeto '{project_name}' retomado com sucesso!

📊 Progresso: {progress:.1f}%
🔄 Ciclo: {state.current_cycle}

Próximo item a processar:
  📄 Arquivo: {next_item.source_file.name}
  📦 Chunk: {next_item.chunk_index + 1}/{next_item.total_chunks}
  📏 Tokens estimados: {next_item.token_estimate:,}

Para processar o próximo item, carregue o arquivo e use:
  engine.work() → processe → engine.save(item_id, resultado)
"""

    except Exception as e:
        return f"Erro ao retomar projeto: {e}"


def _pips_list() -> str:
    """List all PIPS projects."""
    from .pips import PIPSEngine, list_projects

    projects = list_projects()

    if not projects:
        return (
            "Nenhum projeto PIPS encontrado.\n\n"
            "Para criar um novo projeto:\n"
            "  /pips init <nome> <objetivo>"
        )

    output = "═══════════════════════════════════════════════════\n"
    output += "  PROJETOS PIPS\n"
    output += "═══════════════════════════════════════════════════\n\n"

    for project_name in projects:
        try:
            engine = PIPSEngine(project_name)
            _, state = engine.load_project()
            progress = state.get_progress_percentage()
            status = state.status.value

            status_emoji = {
                "nao_iniciado": "⏸️",
                "em_progresso": "▶️",
                "pausado": "⏸️",
                "validando": "🔍",
                "concluido": "✅",
                "erro": "❌",
            }.get(status, "❓")

            output += f"  {status_emoji} {project_name}\n"
            output += f"     Status: {status} | Progresso: {progress:.1f}%\n\n"
        except Exception:
            output += f"  ❓ {project_name} (erro ao carregar)\n\n"

    output += "───────────────────────────────────────────────────\n"
    output += "Comandos: /pips status <nome> | /pips resume <nome>\n"

    return output


def _pips_validate(cmd: Any) -> str:
    """Validate PIPS project state."""
    from .pips import PIPSEngine

    project_name = cmd.project_name

    try:
        engine = PIPSEngine(project_name)

        if not engine.project_exists():
            return f"Projeto '{project_name}' não encontrado."

        engine.load_project()
        is_valid, errors = engine.validate()

        if is_valid:
            return (
                f"✅ Projeto '{project_name}' validado com sucesso!\n\n"
                "Todos os arquivos de estado estão íntegros."
            )

        output = f"❌ Projeto '{project_name}' possui erros de validação:\n\n"
        for error in errors:
            output += f"  • {error}\n"

        output += "\nPara tentar corrigir automaticamente:\n"
        output += f"  python tools/pips_validate.py --project {project_name} --fix"

        return output

    except Exception as e:
        return f"Erro durante validação: {e}"


def _pips_finalize(cmd: Any) -> str:
    """Finalize PIPS project and generate output."""
    from .pips import PIPSEngine

    project_name = cmd.project_name

    try:
        engine = PIPSEngine(project_name)

        if not engine.project_exists():
            return f"Projeto '{project_name}' não encontrado."

        config, state = engine.load_project()

        # Verificar se há itens pendentes
        pending = state.get_pending_items()
        if pending:
            return (
                f"⚠️ Projeto '{project_name}' ainda possui {len(pending)} itens pendentes.\n"
                f"Use /pips resume {project_name} para continuar processamento."
            )

        # Gerar output final
        final_content = f"""# Entrega Final: {project_name}

Data: {state.last_updated.strftime('%Y-%m-%d %H:%M')}
Ciclos executados: {state.current_cycle}

## Objetivo
{config.objective}

## Síntese Consolidada
{state.insights_consolidated or '*Nenhuma síntese consolidada disponível.*'}

---
*Gerado pelo PIPS (Protocolo de Processamento Iterativo com Persistência de Estado)*
"""

        output_path = engine.finalize_output(final_content, f"{project_name}_final.md")

        return (
            f"✅ Projeto '{project_name}' finalizado!\n\n"
            f"📄 Entrega final gerada em:\n"
            f"   {output_path}\n\n"
            "O projeto foi marcado como CONCLUÍDO."
        )

    except Exception as e:
        return f"Erro ao finalizar projeto: {e}"


def _pips_delete(cmd: Any) -> str:
    """Delete PIPS project."""
    from .pips import PIPSEngine

    project_name = cmd.project_name

    try:
        engine = PIPSEngine(project_name)

        if not engine.project_exists():
            return f"Projeto '{project_name}' não encontrado."

        # Deleção confirmada via comando explícito do usuário
        success = engine.delete_project(confirm=True)

        if success:
            return (
                f"✅ Projeto '{project_name}' removido com sucesso.\n\n"
                "Todos os arquivos de estado e outputs foram deletados."
            )

        return f"❌ Falha ao remover projeto '{project_name}'."

    except Exception as e:
        return f"Erro ao remover projeto: {e}"


# ---------------------------------------------------------------------------
# Contexto Processing
# ---------------------------------------------------------------------------

def process_contexto_request(command: Any, context: Dict[str, Any]) -> str:
    """Process /contexto command for high-quality context extraction.

    Args:
        command: Parsed command object
        context: Loaded context dictionary

    Returns:
        Formatted string with processing results
    """
    from pathlib import Path
    from .context_cache import CachedContextProcessor

    if not command.args:
        return (
            "Uso: /contexto <caminho> [opções]\n\n"
            "Opções:\n"
            "  --no-cache    Ignorar cache e reprocessar\n"
            "  --stats       Mostrar estatísticas do cache\n\n"
            "Exemplos:\n"
            "  /contexto referencias/\n"
            "  /contexto documento.md\n"
            "  /contexto .pips/_source/ --no-cache"
        )

    path_arg = command.args[0]
    force_reload = "--no-cache" in command.args
    show_stats = "--stats" in command.args

    # Handle stats request
    if show_stats:
        processor = CachedContextProcessor()
        stats = processor.get_cache_stats()
        return (
            "═══════════════════════════════════════════════════\n"
            "  ESTATÍSTICAS DO CACHE DE CONTEXTO\n"
            "═══════════════════════════════════════════════════\n\n"
            f"📊 Hits: {stats.get('hits', 0)}\n"
            f"📊 Misses: {stats.get('misses', 0)}\n"
            f"📊 Taxa de acerto: {stats.get('hit_rate', 0):.1%}\n"
            f"📁 Entradas em cache: {stats.get('entries', 0)}\n"
            f"💾 Tamanho total: {stats.get('size_mb', 0):.2f} MB"
        )

    target_path = Path(path_arg)

    # Resolve relative paths
    if not target_path.is_absolute():
        target_path = Path.cwd() / target_path

    if not target_path.exists():
        return f"Erro: Caminho não encontrado: {path_arg}"

    try:
        processor = CachedContextProcessor()

        if target_path.is_file():
            # Process single file
            doc = processor.process_file(target_path, force_reload=force_reload)
            return _format_document_result(doc)

        elif target_path.is_dir():
            # Process directory
            documents, index = processor.process_directory(
                target_path, force_reload=force_reload
            )
            return _format_directory_result(documents, index, target_path)

        else:
            return f"Erro: Caminho inválido: {path_arg}"

    except (FileNotFoundError, PermissionError) as e:
        return f"Erro ao processar: {e}"
    except ValueError as e:
        return f"Erro de validação: {e}"


def _format_document_result(doc: Any) -> str:
    """Format single document processing result."""
    output = (
        "═══════════════════════════════════════════════════\n"
        f"  CONTEXTO: {doc.metadata.file_path.name}\n"
        "═══════════════════════════════════════════════════\n\n"
    )

    output += f"📄 Tipo: {doc.metadata.file_type}\n"
    output += f"📏 Linhas: {doc.metadata.lines_count}\n"
    output += f"🔢 Tokens estimados: {doc.metadata.tokens_estimate:,}\n"
    output += f"⏱️ Tempo de processamento: {doc.metadata.processing_time_ms:.1f}ms\n\n"

    if doc.sections:
        output += "📑 Seções:\n"
        for section in doc.sections[:10]:
            indent = "  " * section.level
            output += f"  {indent}• {section.title}\n"
        if len(doc.sections) > 10:
            output += f"  ... e mais {len(doc.sections) - 10} seções\n"
        output += "\n"

    if doc.concepts:
        output += f"💡 Conceitos extraídos: {len(doc.concepts)}\n"
        top_concepts = doc.get_top_concepts(5)
        for concept in top_concepts:
            output += f"  • [{concept.type.value}] {concept.text[:50]}...\n"
        output += "\n"

    if doc.relationships:
        output += f"🔗 Relacionamentos: {len(doc.relationships)}\n"

    if doc.summary:
        output += f"\n📝 Resumo:\n{doc.summary[:500]}{'...' if len(doc.summary) > 500 else ''}\n"

    return output


def _format_directory_result(documents: List[Any], index: Any, directory: Path) -> str:
    """Format directory processing result."""
    output = (
        "═══════════════════════════════════════════════════\n"
        f"  CONTEXTO: {directory.name}/\n"
        "═══════════════════════════════════════════════════\n\n"
    )

    output += f"📁 Arquivos processados: {len(documents)}\n"

    total_concepts = sum(len(d.concepts) for d in documents)
    total_relationships = sum(len(d.relationships) for d in documents)
    total_tokens = sum(d.metadata.tokens_estimate for d in documents)

    output += f"💡 Total de conceitos: {total_concepts}\n"
    output += f"🔗 Total de relacionamentos: {total_relationships}\n"
    output += f"🔢 Tokens estimados: {total_tokens:,}\n\n"

    # Concepts by type summary
    if index.concepts_by_type:
        output += "📊 Conceitos por tipo:\n"
        for concept_type, concept_ids in sorted(index.concepts_by_type.items()):
            output += f"  • {concept_type}: {len(concept_ids)}\n"
        output += "\n"

    # Top keywords
    if index.concepts_by_keyword:
        sorted_keywords = sorted(
            index.concepts_by_keyword.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:10]
        output += "🏷️ Palavras-chave frequentes:\n"
        for keyword, concept_ids in sorted_keywords:
            output += f"  • {keyword}: {len(concept_ids)} ocorrências\n"

    return output
