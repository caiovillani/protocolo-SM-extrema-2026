# src/context_engine/pipeline.py

"""Processing pipeline for the Context Engineering Engine.

Each function represents a stage of the pipeline. The implementations are
simplified placeholders that can be expanded later.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from .formatter import (
    format_pips_status,
    format_pips_list,
    format_pips_init_success,
    format_pips_resume,
    format_contexto_document,
    format_contexto_directory,
    format_contexto_stats,
    format_template_output,
    format_auditoria_output,
    format_orientacao_output,
    format_comparar_output,
    format_conformidade_output,
    format_export_success,
    format_export_error,
    format_export_help,
    get_status_emoji,
    inject_citations_into_output,
)

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

def load_context(request_type: str, command_args: List[str] = None) -> Dict[str, Any]:
    """Load the resources required for the given request type.

    The function delegates to the ``resources`` module and context processor.
    It returns a dictionary with:
    - 'concepts': List of relevant Concept objects for citation
    - 'normativas': YAML normative resources
    - Additional context specific to the request type

    Args:
        request_type: Type of request (template, auditoria, etc.)
        command_args: Optional command arguments for targeted loading

    Returns:
        Context dictionary with concepts and resources
    """
    from . import resources

    context: Dict[str, Any] = {
        'concepts': [],  # For citation injection
        'documents': [],  # Loaded structured documents
    }

    # Load structured concepts for citation support
    try:
        context['concepts'] = _load_relevant_concepts(request_type, command_args)
    except Exception:
        # Graceful degradation if context loading fails
        context['concepts'] = []

    if request_type == "template":
        # Template commands may reference specific protocols
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
    elif request_type == "validar":
        # Validation commands need full protocol context
        context["validation_enabled"] = True
    elif request_type == "evidencia":
        # Evidence commands query the reference index
        context["evidence_enabled"] = True

    return context


def _load_relevant_concepts(
    request_type: str,
    command_args: List[str] = None
) -> List[Any]:
    """Load relevant concepts based on request type and arguments.

    This is the bridge between the context processor and the command pipeline.

    Args:
        request_type: Type of request
        command_args: Command arguments (e.g., protocol ID)

    Returns:
        List of Concept objects relevant to the request
    """
    from .context_cache import CachedContextProcessor

    concepts = []

    # Define protocol paths based on common patterns
    protocol_paths = {
        'CLI_01': 'entregas/Protocolos_Compartilhamento_Cuidado/Protocolos_Clinicos/',
        'CLI_02': 'entregas/Protocolos_Compartilhamento_Cuidado/Protocolos_Clinicos/CLI_02_TRANSTORNO_ESPECTRO_AUTISTA.md',
        'CLI_03': 'entregas/Protocolos_Compartilhamento_Cuidado/Protocolos_Clinicos/',
        'MACROFLUXO': 'entregas/Protocolos_Compartilhamento_Cuidado/Protocolos_Clinicos/MACROFLUXO_NARRATIVO_DI_TEA.md',
        'GUIA_NARRATIVO': 'entregas/Protocolos_Compartilhamento_Cuidado/Protocolos_Clinicos/GUIA_NARRATIVO_APS_DI_TEA.md',
    }

    if not command_args:
        return concepts

    # Check if any argument matches a known protocol
    for arg in command_args:
        arg_upper = arg.upper()
        for protocol_key, protocol_path in protocol_paths.items():
            if protocol_key in arg_upper:
                try:
                    full_path = Path.cwd() / protocol_path
                    if full_path.exists() and full_path.is_file():
                        processor = CachedContextProcessor()
                        doc = processor.process_file(full_path)
                        concepts.extend(doc.concepts)
                except Exception:
                    pass  # Graceful degradation

    return concepts

# ---------------------------------------------------------------------------
# Stage 4 – Core Processing
# ---------------------------------------------------------------------------

def process_request(command: Any, context: Dict[str, Any]) -> str:
    """Generate the final output based on the command and loaded context.

    This function assembles command outputs with citation injection for
    evidence traceability.

    Args:
        command: Parsed command object
        context: Loaded context with concepts for citation

    Returns:
        Formatted output string with citations
    """
    # Extract concepts for citation injection
    concepts = context.get('concepts', [])

    if command.name == "template":
        template_id = command.args[0] if command.args else "unknown"
        # Build template data from loaded concepts
        template_data = _build_template_data(template_id, concepts)
        output = format_template_output(template_id, template_data)
        # Inject citations from relevant concepts
        return inject_citations_into_output(output, concepts)

    elif command.name == "auditoria":
        registro = command.args[0] if command.args else "registro"
        output = format_auditoria_output(registro, None)
        return inject_citations_into_output(output, concepts)

    elif command.name == "orientacao":
        campo = command.args[0] if command.args else "campo"
        output = format_orientacao_output(campo, None)
        return inject_citations_into_output(output, concepts)

    elif command.name == "conformidade":
        questao = command.args[0] if command.args else "questao"
        output = format_conformidade_output(questao, None)
        return inject_citations_into_output(output, concepts)

    elif command.name == "comparar":
        tipo1 = command.args[0] if len(command.args) > 0 else "tipo1"
        tipo2 = command.args[1] if len(command.args) > 1 else "tipo2"
        output = format_comparar_output(tipo1, tipo2, None)
        return inject_citations_into_output(output, concepts)

    elif command.name == "export":
        return process_export_request(command, context)

    elif command.name == "pips":
        return process_pips_request(command, context)

    elif command.name == "contexto":
        return process_contexto_request(command, context)

    elif command.name == "validar":
        return process_validar_request(command, context)

    elif command.name == "evidencia":
        return process_evidencia_request(command, context)

    else:
        return f"Comando '{command.name}' processado (placeholder)."


def _build_template_data(template_id: str, concepts: List[Any]) -> Dict[str, Any]:
    """Build template data from loaded concepts.

    Args:
        template_id: ID of the template
        concepts: List of Concept objects

    Returns:
        Dictionary with template data
    """
    if not concepts:
        return None

    # Filter concepts relevant to the template
    relevant_concepts = [c for c in concepts if template_id.upper() in str(c.source_file).upper()]

    if not relevant_concepts:
        return None

    # Group concepts by type
    concepts_by_type: Dict[str, List[Any]] = {}
    for c in relevant_concepts:
        type_key = c.type.value
        if type_key not in concepts_by_type:
            concepts_by_type[type_key] = []
        concepts_by_type[type_key].append(c)

    return {
        'tipo': 'protocolo_clinico',
        'arquivo': str(relevant_concepts[0].source_file) if relevant_concepts else 'N/A',
        'secoes': list(set(c.section for c in relevant_concepts if c.section)),
        'conceitos_por_tipo': {k: len(v) for k, v in concepts_by_type.items()},
    }


# ---------------------------------------------------------------------------
# Validation Processing (Phase 5 placeholder)
# ---------------------------------------------------------------------------

def process_validar_request(command: Any, context: Dict[str, Any]) -> str:
    """Process /validar command for cross-document validation.

    Args:
        command: Parsed command object
        context: Loaded context dictionary

    Returns:
        Validation results string
    """
    from .commands import parse_validar_command
    from .validator import CrossDocumentValidator, format_validation_report
    from .formatter import format_header

    validar_cmd = parse_validar_command(command)
    if validar_cmd.error:
        return validar_cmd.error_message or (
            "Uso: /validar <protocolo1> [protocolo2]\n\n"
            "Exemplos:\n"
            "  /validar CLI_02                    # Validar protocolo único\n"
            "  /validar CLI_02 MACROFLUXO        # Comparar dois protocolos\n"
            "  /validar --all                    # Validar todos os protocolos"
        )

    # Initialize validator with rules and reference index
    rules_path = Path.cwd() / "src/context_engine/validation_rules.yaml"
    index_path = Path.cwd() / "referencias/REFERENCE_INDEX.yaml"

    validator = CrossDocumentValidator(
        rules_path=rules_path if rules_path.exists() else None,
        reference_index_path=index_path if index_path.exists() else None,
    )

    try:
        if validar_cmd.validate_all:
            # Validate all known protocols
            report = validator.detect_inconsistencies()
        elif validar_cmd.protocol_b:
            # Compare two protocols
            report = validator.compare_protocols(
                validar_cmd.protocol_a,
                validar_cmd.protocol_b
            )
        else:
            # Validate single protocol
            report = validator.validate_protocol(validar_cmd.protocol_a)

        # Save report to session state for export support
        context['last_validation_report'] = report
        formatted_output = format_validation_report(report)
        context['last_command_output'] = formatted_output

        return formatted_output

    except Exception as e:
        return f"Erro durante validação: {e}"


def process_evidencia_request(command: Any, context: Dict[str, Any]) -> str:
    """Process /evidencia command for querying reference sources.

    Args:
        command: Parsed command object
        context: Loaded context dictionary

    Returns:
        Evidence query results string
    """
    from .commands import parse_evidencia_command
    from .validator import CrossDocumentValidator
    from .formatter import format_header, format_separator, CONTENT_EMOJI

    evidencia_cmd = parse_evidencia_command(command)
    if evidencia_cmd.error:
        return evidencia_cmd.error_message or (
            "Uso: /evidencia <termo> [opções]\n\n"
            "Exemplos:\n"
            "  /evidencia TEA                    # Fontes sobre TEA\n"
            "  /evidencia CuidaSM --validation   # Dados de validação\n"
            "  /evidencia --grade ALTA           # Apenas evidência alta"
        )

    # Initialize validator with reference index
    index_path = Path.cwd() / "referencias/REFERENCE_INDEX.yaml"

    validator = CrossDocumentValidator(
        reference_index_path=index_path if index_path.exists() else None,
    )

    # Query reference index
    results = validator.get_evidence_for_term(evidencia_cmd.search_term)

    # Filter by evidence grade if specified
    if evidencia_cmd.evidence_grade_filter:
        results = [
            r for r in results
            if r.get('evidence_grade', '').lower() == evidencia_cmd.evidence_grade_filter
        ]

    # Format output
    output = format_header(f"EVIDÊNCIA: {evidencia_cmd.search_term}")
    output += "\n\n"

    if not results:
        output += f"Nenhuma fonte encontrada para '{evidencia_cmd.search_term}'.\n\n"
        output += "Tente:\n"
        output += "  • Usar termos diferentes (TEA, autismo, M-CHAT, CuidaSM)\n"
        output += "  • Verificar se REFERENCE_INDEX.yaml existe\n"
        return output

    output += f"📚 Fontes encontradas: {len(results)}\n\n"

    for result in results:
        # Evidence grade emoji
        grade = result.get('evidence_grade', 'nao_avaliada')
        grade_emoji = {
            'alta': '🟢',
            'moderada': '🟡',
            'baixa': '🟠',
            'normativa': '🔵',
        }.get(grade, '⚪')

        output += f"{grade_emoji} **{result.get('name', 'Sem nome')}**\n"
        output += f"   Tipo: {result.get('type', 'N/A')}\n"
        output += f"   Evidência: {grade.upper()}\n"

        # Show validation data if requested
        if evidencia_cmd.show_validation and 'validation' in result:
            validation = result['validation']
            output += "   📊 Validação:\n"
            if 'sensitivity' in validation:
                output += f"      Sensibilidade: {validation['sensitivity']}\n"
            if 'specificity' in validation:
                output += f"      Especificidade: {validation['specificity']}\n"
            if 'population' in validation:
                output += f"      População: {validation['population']}\n"

        # Show scoring if available
        if 'scoring' in result:
            output += "   📈 Pontuação:\n"
            for level, info in result['scoring'].items():
                if isinstance(info, dict):
                    output += f"      {level}: {info.get('range', info.get('description', 'N/A'))}\n"

        # Source files
        if 'source_files' in result:
            output += "   📄 Arquivos:\n"
            for sf in result['source_files'][:2]:
                path = sf.get('path', sf) if isinstance(sf, dict) else sf
                output += f"      • {path}\n"

        output += "\n"

    output += format_separator()
    output += "\n"
    output += "Opções: --validation (dados validação) | --grade <nivel> (filtrar)\n"

    return output

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
# Export Processing
# ---------------------------------------------------------------------------

def process_export_request(command: Any, context: Dict[str, Any]) -> str:
    """Process /export command.

    Args:
        command: Parsed export command
        context: Loaded context

    Returns:
        Export success message or error
    """
    from .commands import parse_export_command
    from .main import get_last_output
    from .exporter import CommandExporter, ExportFormat, ExportMetadata

    export_cmd = parse_export_command(command)
    if export_cmd.error:
        return export_cmd.error_message or format_export_help()

    # Get last command output from session state
    last_output, last_command = get_last_output()
    if not last_output:
        return (
            "Nenhum comando anterior para exportar.\n\n"
            "Execute um comando primeiro, depois use /export.\n\n"
            "Exemplo:\n"
            "  /pips status meu_projeto\n"
            "  /export md"
        )

    # Parse format
    try:
        export_format = ExportFormat.from_string(export_cmd.format)
    except ValueError as e:
        return format_export_error(str(e))

    # Create metadata
    metadata = ExportMetadata(
        command_name=last_command,
        timestamp=datetime.now().isoformat(),
    )

    # Determine output path
    if export_cmd.output_path:
        output_path = Path(export_cmd.output_path)
    else:
        # Auto-generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extension = export_format.value
        filename = f"{last_command}_{timestamp}.{extension}"
        output_path = Path("./exports") / filename

    # Export
    exporter = CommandExporter()
    result = exporter.export_to_file(
        last_output,
        export_format,
        output_path,
        metadata if export_cmd.include_metadata else None,
    )

    if result.success:
        return format_export_success(
            export_format.value,
            str(result.file_path),
            result.size_bytes,
        )
    else:
        return format_export_error(result.error_message or "Erro desconhecido")


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
    elif pips_cmd.subcommand == "memory":
        return _pips_memory()

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

        return format_pips_init_success(project_name, objective)

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

        # Use centralized formatter
        output = format_pips_status(project_name, config, state)

        # Add checkpoint info if available
        last_checkpoint = engine.get_last_checkpoint()
        if last_checkpoint:
            output += f"\n\n📍 Último checkpoint: {last_checkpoint.action} ({last_checkpoint.notes})"

        return output

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

        return format_pips_resume(project_name, state, next_item)

    except Exception as e:
        return f"Erro ao retomar projeto: {e}"


def _pips_list() -> str:
    """List all PIPS projects."""
    from .pips import PIPSEngine, list_projects

    projects_names = list_projects()

    if not projects_names:
        return (
            "Nenhum projeto PIPS encontrado.\n\n"
            "Para criar um novo projeto:\n"
            "  /pips init <nome> <objetivo>"
        )

    # Collect project data for formatter
    projects_data = []
    for project_name in projects_names:
        try:
            engine = PIPSEngine(project_name)
            config, state = engine.load_project()
            projects_data.append((project_name, config, state))
        except Exception:
            # Create minimal mock for error case
            projects_data.append((project_name, None, None))

    return format_pips_list(projects_data)


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


def _pips_memory() -> str:
    """Show Infinite Memory Protocol status.

    Displays all resumable projects and protocol status information.
    """
    from .pips import get_all_resumable_projects
    from .formatter import BOX_WIDTH, STATUS_EMOJI

    resumable = get_all_resumable_projects()

    # Header
    output = "\n"
    output += "═" * BOX_WIDTH + "\n"
    output += "  PROTOCOLO DE MEMÓRIA INFINITA\n"
    output += "═" * BOX_WIDTH + "\n\n"

    if not resumable:
        output += "✅ Nenhum projeto com trabalho pendente.\n\n"
        output += "O protocolo está ativo e irá:\n"
        output += "  • Salvar estado automaticamente antes de compactação (PreCompact)\n"
        output += "  • Alertar sobre projetos ativos ao iniciar sessão (SessionStart)\n"
        output += "  • Manter auditoria de todas as ações automáticas\n\n"
        output += "─" * BOX_WIDTH + "\n"
        output += "Para criar novo projeto: /pips init <nome> <objetivo>\n"
        return output

    output += f"📋 Projetos com trabalho resumível: {len(resumable)}\n\n"

    # Mapeamento de status para emoji
    status_map = {
        'nao_iniciado': '🔵',
        'em_progresso': '▶️',
        'pausado': '⏸️',
        'validando': '🔍',
        'concluido': '✅',
        'erro': '❌',
    }

    for proj in resumable:
        emoji = status_map.get(proj['status'], '❓')
        output += f"{emoji} {proj['project_name']}\n"

        if proj.get('objective'):
            obj_short = proj['objective'][:80] + "..." if len(proj['objective']) > 80 else proj['objective']
            output += f"   Objetivo: {obj_short}\n"

        output += f"   Progresso: {proj['pending_count']}/{proj['total_count']} pendentes "
        output += f"({proj['progress_pct']:.1f}% concluído)\n"
        output += f"   Ciclo: {proj['current_cycle']} | "
        output += f"Atualizado: {proj['last_updated'][:16]}\n"

        if proj.get('next_item'):
            next_item = proj['next_item']
            output += f"   Próximo: {next_item['file']} (chunk {next_item['chunk']}, ~{next_item['tokens']} tokens)\n"

        output += "\n"

    output += "─" * BOX_WIDTH + "\n"
    output += "Comandos disponíveis:\n"
    output += "  /pips resume <nome>  - Retomar processamento\n"
    output += "  /pips status <nome>  - Ver status detalhado\n"
    output += "  /pips validate <nome> - Validar integridade\n"

    return output


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
        return format_contexto_stats(stats)

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
            return format_contexto_document(doc)

        elif target_path.is_dir():
            # Process directory
            documents, index = processor.process_directory(
                target_path, force_reload=force_reload
            )
            return format_contexto_directory(documents, index, target_path)

        else:
            return f"Erro: Caminho inválido: {path_arg}"

    except (FileNotFoundError, PermissionError) as e:
        return f"Erro ao processar: {e}"
    except ValueError as e:
        return f"Erro de validação: {e}"
