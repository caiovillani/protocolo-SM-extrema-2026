# src/context_engine/commands.py

"""Command parsing utilities for the Context Engineering Engine.

Supported shortcuts:
- /template [type]
- /auditoria [registro]
- /orientacao [campo]
- /conformidade [questao]
- /comparar [tipo1] [tipo2]
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Command:
    raw: str
    name: str
    args: List[str]
    error: bool = False
    error_message: Optional[str] = None


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
    known = {"template", "auditoria", "orientacao", "conformidade", "comparar"}
    if name not in known:
        return Command(
            raw=user_input,
            name=name,
            args=args,
            error=True,
            error_message=f"Comando '/{name}' não suportado.",
        )
    return Command(raw=user_input, name=name, args=args)
