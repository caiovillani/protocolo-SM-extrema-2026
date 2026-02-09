# -*- coding: utf-8 -*-
"""Complete Phase 2: move reviews and staging folders."""
import sys
import io
import shutil
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

OUT = Path(r"c:\Users\caiov\OneDrive\Desktop\Claude AI\Projetos\projeto-local-compras-e-licitacoes\Extrema-main\Extrema-main\output")

# Move review files from root to reviews/
reviews_dest = OUT / "reviews"
reviews_dest.mkdir(exist_ok=True)
review_files = [
    "critical-review-oficio-b-crie-apae.md",
    "critical-review-parceria-apae-mrosc.md",
    "critical-review-parceria-apae-mrosc.txt",
    "expert-evaluation-oficio-crie-apae.md",
    "revisao-critica-tarefas-ADE-2026-02-04.md",
]

print("--- reviews/ ---")
for fname in review_files:
    p = OUT / fname
    if p.exists():
        shutil.move(str(p), str(reviews_dest / fname))
        print(f"  -> reviews/{fname}")
    else:
        print(f"  [SKIP] {fname}")

# Move empty placeholder folders to _staging/
staging = OUT / "_staging"
staging.mkdir(exist_ok=True)
print("\n--- _staging/ ---")
for d in ["etp", "pareceres", "tr"]:
    old = OUT / d
    if old.exists():
        new = staging / d
        new.mkdir(exist_ok=True)
        gk = old / ".gitkeep"
        if gk.exists():
            shutil.move(str(gk), str(new / ".gitkeep"))
        remaining = list(old.iterdir())
        if not remaining:
            try:
                old.rmdir()
            except PermissionError:
                print(f"  [INFO] {d}/ locked — remove manually")
        print(f"  -> _staging/{d}/")
    else:
        print(f"  [SKIP] {d}/ not found")

# Try to remove empty e3-graficos
e3 = OUT / "e3-graficos"
if e3.exists():
    remaining = [f for f in e3.iterdir() if f.name != ".gitkeep"]
    if not remaining:
        try:
            shutil.rmtree(str(e3))
            print("\n[OK] Removed empty e3-graficos/")
        except PermissionError:
            print("\n[INFO] e3-graficos/ still locked")

print("\n[DONE]")
