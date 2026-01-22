#!/usr/bin/env python3
"""
Tool: [Nome da Ferramenta]
Descrição: [O que esta ferramenta faz]

Uso:
    python tools/nome_ferramenta.py --arg1 valor1 --arg2 valor2

Inputs:
    --arg1: descrição do argumento
    --arg2: descrição do argumento

Outputs:
    - Arquivo salvo em .tmp/output.json
    - OU: dados enviados para Google Sheets/etc

Dependências:
    - requests
    - python-dotenv
"""

import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Diretórios padrão
PROJECT_ROOT = Path(__file__).parent.parent
TMP_DIR = PROJECT_ROOT / ".tmp"


def main():
    parser = argparse.ArgumentParser(description="[Descrição da ferramenta]")
    parser.add_argument("--exemplo", type=str, help="Argumento de exemplo")
    args = parser.parse_args()

    # Garante que .tmp existe
    TMP_DIR.mkdir(exist_ok=True)

    # Implementação aqui
    print(f"Ferramenta executada com: {args}")


if __name__ == "__main__":
    main()
