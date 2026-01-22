# tests/test_commands.py

import pytest
from src.context_engine.commands import parse_command, Command


def test_parse_valid_template():
    cmd = parse_command("/template PC-PSQ")
    assert not cmd.error
    assert cmd.name == "template"
    assert cmd.args == ["PC-PSQ"]


def test_parse_invalid():
    cmd = parse_command("hello")
    assert cmd.error
    assert "Comando não reconhecido" in cmd.error_message
