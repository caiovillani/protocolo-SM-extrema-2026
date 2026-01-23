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


# Subcomandos PIPS válidos
PIPS_SUBCOMMANDS = {
    "init",      # /pips init <nome> - Iniciar novo projeto
    "status",    # /pips status [nome] - Ver status do projeto
    "resume",    # /pips resume <nome> - Retomar processamento
    "list",      # /pips list - Listar todos os projetos
    "validate",  # /pips validate <nome> - Validar estado
    "finalize",  # /pips finalize <nome> - Finalizar e gerar output
    "delete",    # /pips delete <nome> - Remover projeto
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
    known = {"template", "auditoria", "orientacao", "conformidade", "comparar", "pips", "contexto"}
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
