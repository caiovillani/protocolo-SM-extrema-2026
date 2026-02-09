# -*- coding: utf-8 -*-
"""Verify reorganization results."""
import sys
import io
from pathlib import Path
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

SRC = Path(r"c:\Users\caiov\OneDrive\Desktop\MEMÓRIA TÉCNICA AI\SAÚDE MENTAL\Licitacoes_Compras_e_Contratos")
OUT = Path(r"c:\Users\caiov\OneDrive\Desktop\Claude AI\Projetos\projeto-local-compras-e-licitacoes\Extrema-main\Extrema-main\output")

SKIP = {"desktop.ini", "settings.local.json", ".gitkeep"}

def verify(base: Path, label: str):
    all_f = [f for f in base.rglob("*") if f.is_file() and f.name not in SKIP
             and ".claude" not in str(f) and ".mypy_cache" not in str(f)]
    print(f"\n=== {label} ===")
    print(f"Total files: {len(all_f)}")

    dirs = Counter()
    for f in all_f:
        rel = f.parent.relative_to(base)
        top = str(rel).split("\\")[0] if str(rel) != "." else "(root)"
        dirs[top] += 1

    for d, c in sorted(dirs.items()):
        print(f"  {d}: {c}")

verify(SRC, "SOURCE FOLDER")
verify(OUT, "OUTPUT FOLDER")
