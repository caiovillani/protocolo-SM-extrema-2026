# src/context_engine/commands.py

"""Command parsing utilities for the Context Engineering Engine.

Supported shortcuts:
- /template [type]
- /auditoria [registro]
- /orientacao [campo]
- /conformidade [questao]
- /comparar [tipo1] [tipo2]
- /pips <subcomando> [argumentos] - Protocolo de Processamento Iterativo
- /contexto <caminho> [opções] - Motor de Contexto de Alta Qualidade
- /export <formato> [caminho] - Exportar saída do comando anterior
- /validar <protocolo1> [protocolo2] - Validação cruzada de protocolos
- /evidencia <termo> [opções] - Consultar fontes de evidência
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Command:
    """Comando base parseado do input do usuário."""
    raw: str
    name: str
    args: List[str]
    error: bool = False
    error_message: Optional[str] = None


@dataclass
class PIPSCommand(Command):
    """Comando PIPS com subcomando e nome do projeto."""
    subcommand: str = ""
    project_name: str = ""


@dataclass
class ExportCommand(Command):
    """Comando de exportação com formato e caminho de saída.

    Examples:
        /export md
        /export docx relatorio.docx
        /export yaml --no-metadata
    """
    format: str = "md"
    output_path: Optional[str] = None
    include_metadata: bool = True


@dataclass
class ValidarCommand(Command):
    """Comando de validação cruzada de protocolos.

    Examples:
        /validar CLI_02
        /validar CLI_02 MACROFLUXO
        /validar --all
        /validar CLI_02 --severity critical
    """
    protocol_a: str = ""
    protocol_b: Optional[str] = None
    validate_all: bool = False
    severity_filter: Optional[str] = None  # "critical", "warning", "info"
    conflict_type_filter: Optional[str] = None  # "numeric", "timeline", etc.


@dataclass
class EvidenciaCommand(Command):
    """Comando de consulta de evidências.

    Examples:
        /evidencia TEA
        /evidencia CuidaSM --validation
        /evidencia --grade ALTA
    """
    search_term: str = ""
    show_validation: bool = False
    evidence_grade_filter: Optional[str] = None  # "alta", "moderada", "baixa", "normativa"
    format_citations: bool = False


# Formatos de exportação válidos
EXPORT_FORMATS = {"md", "markdown", "yaml", "yml", "json", "docx", "doc", "word"}


# Subcomandos PIPS válidos
PIPS_SUBCOMMANDS = {
    "init",      # /pips init <nome> - Iniciar novo projeto
    "status",    # /pips status [nome] - Ver status do projeto
    "resume",    # /pips resume <nome> - Retomar processamento
    "list",      # /pips list - Listar todos os projetos
    "validate",  # /pips validate <nome> - Validar estado
    "finalize",  # /pips finalize <nome> - Finalizar e gerar output
    "delete",    # /pips delete <nome> - Remover projeto
    "memory",    # /pips memory - Status do Protocolo de Memória Infinita
}


def parse_command(user_input: str) -> Command:
    """Parse a raw user input string into a Command object.

    Returns a Command with `error=True` if the input does not start with a recognized
    shortcut.
    """
    user_input = user_input.strip()
    if not user_input.startswith('/'):
        return Command(
            raw=user_input,
            name="",
            args=[],
            error=True,
            error_message="Comando não reconhecido. Use um dos atalhos iniciados por '/'",
        )

    parts = user_input.split()
    name = parts[0][1:]  # remove leading '/'
    args = parts[1:]
    # Simple validation for known commands
    known = {"template", "auditoria", "orientacao", "conformidade", "comparar", "pips", "contexto", "export", "validar", "evidencia"}
    if name not in known:
        return Command(
            raw=user_input,
            name=name,
            args=args,
            error=True,
            error_message=f"Comando '/{name}' não suportado.",
        )
    return Command(raw=user_input, name=name, args=args)


def parse_pips_command(command: Command) -> PIPSCommand:
    """Parse PIPS-specific arguments from a Command.

    Args:
        command: Comando base já parseado

    Returns:
        PIPSCommand com subcomando e nome do projeto extraídos
    """
    if command.name != "pips":
        return PIPSCommand(
            raw=command.raw,
            name=command.name,
            args=command.args,
            error=True,
            error_message="Comando não é um comando PIPS.",
        )

    if not command.args:
        subcommands_list = ", ".join(sorted(PIPS_SUBCOMMANDS))
        return PIPSCommand(
            raw=command.raw,
            name=command.name,
            args=command.args,
            error=True,
            error_message=(
                "Uso: /pips <subcomando> [argumentos]\n"
                f"Subcomandos disponíveis: {subcommands_list}"
            ),
        )

    subcommand = command.args[0].lower()
    if subcommand not in PIPS_SUBCOMMANDS:
        subcommands_list = ", ".join(sorted(PIPS_SUBCOMMANDS))
        return PIPSCommand(
            raw=command.raw,
            name=command.name,
            args=command.args,
            error=True,
            error_message=(
                f"Subcomando PIPS desconhecido: '{subcommand}'\n"
                f"Subcomandos válidos: {subcommands_list}"
            ),
        )

    # Extrair nome do projeto (se aplicável)
    project_name = ""
    if len(command.args) > 1:
        project_name = command.args[1]

    # Validar se subcomando requer nome do projeto
    requires_project = {"init", "status", "resume", "validate", "finalize", "delete"}
    if subcommand in requires_project and not project_name and subcommand != "status":
        return PIPSCommand(
            raw=command.raw,
            name=command.name,
            args=command.args,
            subcommand=subcommand,
            error=True,
            error_message=f"Subcomando '/{command.name} {subcommand}' requer nome do projeto.",
        )

    return PIPSCommand(
        raw=command.raw,
        name=command.name,
        args=command.args,
        subcommand=subcommand,
        project_name=project_name,
    )


def parse_export_command(command: Command) -> ExportCommand:
    """Parse export command arguments.

    Syntax: /export <formato> [caminho] [--no-metadata]

    Args:
        command: Comando base já parseado

    Returns:
        ExportCommand com formato e opções extraídos
    """
    if command.name != "export":
        return ExportCommand(
            raw=command.raw,
            name=command.name,
            args=command.args,
            error=True,
            error_message="Comando não é um comando /export.",
        )

    if not command.args:
        formats_list = "md, yaml, json, docx"
        return ExportCommand(
            raw=command.raw,
            name=command.name,
            args=command.args,
            error=True,
            error_message=(
                "Uso: /export <formato> [caminho] [--no-metadata]\n"
                f"Formatos disponíveis: {formats_list}\n\n"
                "Exemplos:\n"
                "  /export md\n"
                "  /export docx relatorio.docx\n"
                "  /export yaml ./outputs/dados.yaml"
            ),
        )

    format_arg = command.args[0].lower()

    # Validate format
    if format_arg not in EXPORT_FORMATS:
        formats_list = "md, yaml, json, docx"
        return ExportCommand(
            raw=command.raw,
            name=command.name,
            args=command.args,
            error=True,
            error_message=(
                f"Formato de exportação inválido: '{format_arg}'\n"
                f"Formatos válidos: {formats_list}"
            ),
        )

    # Normalize format aliases
    format_aliases = {
        "markdown": "md",
        "yml": "yaml",
        "word": "docx",
        "doc": "docx",
    }
    format_normalized = format_aliases.get(format_arg, format_arg)

    # Parse optional path (second arg, if not a flag)
    output_path = None
    if len(command.args) > 1 and not command.args[1].startswith("--"):
        output_path = command.args[1]

    # Parse flags
    include_metadata = "--no-metadata" not in command.args

    return ExportCommand(
        raw=command.raw,
        name=command.name,
        args=command.args,
        format=format_normalized,
        output_path=output_path,
        include_metadata=include_metadata,
    )


# Protocolos conhecidos para validação
KNOWN_PROTOCOLS = {
    "CLI_01", "CLI_02", "CLI_03", "CLI_04", "CLI_05",
    "MACROFLUXO", "GUIA_NARRATIVO",
    "PCC_01", "PCC_02", "PCC_03", "PCC_04", "PCC_05", "PCC_06",
}

# Graus de evidência válidos (sync with context_models.EvidenceGrade)
EVIDENCE_GRADES = {"alta", "moderada", "baixa", "muito_baixa", "normativa", "nao_avaliada"}


def parse_validar_command(command: Command) -> ValidarCommand:
    """Parse validation command arguments.

    Syntax: /validar <protocolo1> [protocolo2] [--all] [--severity <level>]

    Args:
        command: Comando base já parseado

    Returns:
        ValidarCommand com protocolos e opções extraídos
    """
    if command.name != "validar":
        return ValidarCommand(
            raw=command.raw,
            name=command.name,
            args=command.args,
            error=True,
            error_message="Comando não é um comando /validar.",
        )

    # Check for --all flag
    validate_all = "--all" in command.args

    if not command.args and not validate_all:
        protocols_list = ", ".join(sorted(KNOWN_PROTOCOLS)[:5]) + "..."
        return ValidarCommand(
            raw=command.raw,
            name=command.name,
            args=command.args,
            error=True,
            error_message=(
                "Uso: /validar <protocolo1> [protocolo2] [opções]\n\n"
                f"Protocolos disponíveis: {protocols_list}\n\n"
                "Opções:\n"
                "  --all              Validar todos os protocolos\n"
                "  --severity <nivel> Filtrar por severidade (critical, warning, info)\n\n"
                "Exemplos:\n"
                "  /validar CLI_02\n"
                "  /validar CLI_02 MACROFLUXO\n"
                "  /validar --all"
            ),
        )

    # Extract protocols (non-flag arguments)
    protocols = [arg for arg in command.args if not arg.startswith("--")]
    protocol_a = protocols[0] if protocols else ""
    protocol_b = protocols[1] if len(protocols) > 1 else None

    # Extract severity filter
    severity_filter = None
    if "--severity" in command.args:
        idx = command.args.index("--severity")
        if idx + 1 < len(command.args):
            severity_filter = command.args[idx + 1].lower()

    # Extract conflict type filter
    conflict_type_filter = None
    if "--type" in command.args:
        idx = command.args.index("--type")
        if idx + 1 < len(command.args):
            conflict_type_filter = command.args[idx + 1].lower()

    return ValidarCommand(
        raw=command.raw,
        name=command.name,
        args=command.args,
        protocol_a=protocol_a,
        protocol_b=protocol_b,
        validate_all=validate_all,
        severity_filter=severity_filter,
        conflict_type_filter=conflict_type_filter,
    )


def parse_evidencia_command(command: Command) -> EvidenciaCommand:
    """Parse evidence query command arguments.

    Syntax: /evidencia <termo> [--validation] [--grade <nivel>] [--cite]

    Args:
        command: Comando base já parseado

    Returns:
        EvidenciaCommand com termo e opções extraídos
    """
    if command.name != "evidencia":
        return EvidenciaCommand(
            raw=command.raw,
            name=command.name,
            args=command.args,
            error=True,
            error_message="Comando não é um comando /evidencia.",
        )

    if not command.args:
        return EvidenciaCommand(
            raw=command.raw,
            name=command.name,
            args=command.args,
            error=True,
            error_message=(
                "Uso: /evidencia <termo> [opções]\n\n"
                "Opções:\n"
                "  --validation   Mostrar dados de validação (sensibilidade, especificidade)\n"
                "  --grade <nivel> Filtrar por grau de evidência (alta, moderada, baixa, normativa)\n"
                "  --cite         Formatar como citação Vancouver\n\n"
                "Exemplos:\n"
                "  /evidencia TEA\n"
                "  /evidencia CuidaSM --validation\n"
                "  /evidencia M-CHAT --grade alta"
            ),
        )

    # Extract search term (first non-flag argument)
    search_term = ""
    for arg in command.args:
        if not arg.startswith("--"):
            search_term = arg
            break

    # Extract flags
    show_validation = "--validation" in command.args
    format_citations = "--cite" in command.args

    # Extract grade filter
    evidence_grade_filter = None
    if "--grade" in command.args:
        idx = command.args.index("--grade")
        if idx + 1 < len(command.args):
            grade = command.args[idx + 1].lower()
            if grade in EVIDENCE_GRADES:
                evidence_grade_filter = grade

    return EvidenciaCommand(
        raw=command.raw,
        name=command.name,
        args=command.args,
        search_term=search_term,
        show_validation=show_validation,
        evidence_grade_filter=evidence_grade_filter,
        format_citations=format_citations,
    )
