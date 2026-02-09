# -*- coding: utf-8 -*-
"""Reorganize procurement documentation folders (Phases 0-2).

Usage:
    py -3.13 tools/reorganize_procurement.py count
    py -3.13 tools/reorganize_procurement.py phase0
    py -3.13 tools/reorganize_procurement.py phase1
    py -3.13 tools/reorganize_procurement.py phase2
    py -3.13 tools/reorganize_procurement.py all
"""

import sys
import hashlib
import shutil
from pathlib import Path
from collections import Counter

SRC = Path(r"c:\Users\caiov\OneDrive\Desktop\MEMÓRIA TÉCNICA AI\SAÚDE MENTAL\Licitacoes_Compras_e_Contratos")
OUT = Path(r"c:\Users\caiov\OneDrive\Desktop\Claude AI\Projetos\projeto-local-compras-e-licitacoes\Extrema-main\Extrema-main\output")

SKIP_FILES = {"desktop.ini", ".gitkeep", "settings.local.json"}


def md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def count_files():
    print("=== SOURCE FOLDER ===")
    src_files = [f for f in SRC.rglob("*") if f.is_file() and f.name not in SKIP_FILES
                 and ".claude" not in str(f) and ".mypy_cache" not in str(f)]
    print(f"Total files: {len(src_files)}")
    exts = Counter(f.suffix.lower() for f in src_files)
    for ext, count in exts.most_common():
        print(f"  {ext or '(no ext)'}: {count}")

    print("\n=== OUTPUT FOLDER ===")
    out_files = [f for f in OUT.rglob("*") if f.is_file() and f.name not in SKIP_FILES]
    print(f"Total files: {len(out_files)}")
    exts = Counter(f.suffix.lower() for f in out_files)
    for ext, count in exts.most_common():
        print(f"  {ext or '(no ext)'}: {count}")

    return len(src_files), len(out_files)


def move_file(src_path: Path, dest_dir: Path, label: str = ""):
    if src_path.exists():
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / src_path.name
        shutil.move(str(src_path), str(dest))
        print(f"  -> {label}/{src_path.name}")
        return True
    else:
        print(f"  [SKIP] Not found: {src_path.name}")
        return False


def phase0():
    print("=== PHASE 0: DEDUPLICATION ===")
    dup_dir = SRC / "_duplicados"
    dup_dir.mkdir(exist_ok=True)

    dup1 = SRC / "DicasEstudarOnline_NLLC-AspectosGeraisPontosAtencao_ECG (1).pdf"
    dup2 = SRC / "DicasEstudarOnline_NLLC-AspectosGeraisPontosAtencao_ECG (2).pdf"
    orig = SRC / "DicasEstudarOnline_NLLC-AspectosGeraisPontosAtencao_ECG.pdf"

    moved = 0
    if dup1.exists():
        shutil.move(str(dup1), str(dup_dir / dup1.name))
        print("[OK] Moved duplicate (1) to _duplicados/")
        moved += 1
    if dup2.exists():
        shutil.move(str(dup2), str(dup_dir / dup2.name))
        print("[OK] Moved duplicate (2) to _duplicados/")
        moved += 1

    # Verify hashes
    if orig.exists():
        orig_hash = md5(orig)
        print(f"Original hash: {orig_hash}")
        for name in ["DicasEstudarOnline_NLLC-AspectosGeraisPontosAtencao_ECG (1).pdf",
                      "DicasEstudarOnline_NLLC-AspectosGeraisPontosAtencao_ECG (2).pdf"]:
            p = dup_dir / name
            if p.exists():
                h = md5(p)
                status = "[OK] matches" if h == orig_hash else f"[WARN] MISMATCH: {h}"
                print(f"  {name}: {status}")

    print(f"\n[OK] Phase 0 complete - {moved} duplicates moved")


def phase1():
    print("=== PHASE 1: SOURCE FOLDER REORGANIZATION ===")
    before = len([f for f in SRC.iterdir() if f.is_file() and f.name not in SKIP_FILES])
    print(f"Files at root before: {before}")

    taxonomy = {
        "normativos": [
            "licitacoes_e_contratos_administrativos_L14133.pdf",
            "L12764.pdf",
            "Lei Entidades Beneficentes.pdf",
            "DELIBERA\u00c7\u00c3O_CIB_SUS_MG_1403_2013.pdf",
            "OSC_Leis, Decretos e Normas do Minist\u00e9rio da Sa\u00fade.pdf",
            "PORTARIA INTERMINISTERIAL SG_MGI_AGU N\u00ba 197, DE 11 DE AGOSTO DE 2025 - Transferegov.br.pdf",
            "DECRETO N\u00ba 47.132, DE 20 DE JANEIRO.txt",
        ],
        "mrosc": [
            "Manual_MROSC.pdf",
            "manual_MROSC_MG_AGE.pdf",
            "A aplicabilidade do MROSC nas parcerias da Sa\u00fade \u2013 Observat\u00f3rio da Sociedade Civil.pdf",
            "A aplicabilidade do MROSC nas parcerias da Sa\u00fade \u2013 Observat\u00f3rio da Sociedade Civil2.pdf",
            "Anexo I - Manual MROSC - Modelo de Proposta e Plano de Trabalho.docx",
            "Anexo IV - Manual MROSC - Modelo T\u00e9cnico de Monitoramento e Avalia\u00e7\u00e3o.docx",
        ],
        "capacitacao_nllc": [
            "DicasEstudarOnline_NLLC-AspectosGeraisPontosAtencao_ECG.pdf",
            "NLLC_Material de Apoio aos V\u00eddeos do M\u00f3dulo 1.pdf",
            "NLLC_Material de Apoio aos V\u00eddeos do M\u00f3dulo 2.pdf",
            "Cartilha - Transferencias Especiais 2025.pdf",
            "manual-de-boas-praticas-em-contratacoes-publicas.pdf",
            "Contrata\u00e7\u00e3o GOV.pdf",
            "4.1. Estudo T\u00e9cnico Preliminar (ETP)  Licita\u00e7\u00f5es e Contratos.pdf",
        ],
        "benchmarks": [
            "exemplo_apae_pouso_alegre.pdf",
            "exemplo_apae_2.pdf",
            "Estudo+Tecnico+Preliminar+000004+2025.pdf",
            "copy_of_ANEXO_IV_MODELO_DE_PLANO_DE_TRABALHO_ajustada_27.09.2023.pdf",
            "Plano_de_trabalho_Saude_para_manutencao_de_pagamento_e_educador_fisico_assinado.pdf",
        ],
        "projeto_crie": [
            "TR - CRIE.docx",
            "PLANO DE TRABALHO CRIE.docx",
            "CUSTO FUNCIONARIO com educador fisico 2.pdf",
            "RELAT\u00d3RIO_T\u00c9CNICO_CAPS_I e II.docx",
        ],
        "instrumentos_gerados": [
            "TERMO_DE_REFERENCIA_CRIE_SMS_Extrema.docx",
            "PLANO_DE_TRABALHO_CRIE_SMS_Extrema.docx",
            "06 - Minuta do Termo de Refer\u00eancia.docx",
            "07 - Termo de Justificativa T\u00e9cnica.docx",
            "09 - Minuta de Contratos.docx",
        ],
        "sinteses_ia": [
            "CONTEXTO_ESTRATEGICO_EXTREMA.md",
            "BANCO_CONHECIMENTO_TECNICO.md",
            "EXTRACAO_DADOS_CRIE.md",
            "MEMORIA_CALCULO_ORCAMENTO.md",
            "RASCUNHO_INSTRUMENTOS_JURIDICOS.md",
            "RELATORIO_NAO_CONFORMIDADES.md",
            "LISTA_EXIGENCIAS_COMPLEMENTACAO.md",
            "LOG_AUDITORIA_TAREFAS.md",
            "RELATORIO_ENTREGA_DOCUMENTOS_OFICIAIS.md",
            "RELATORIO_FINAL_ENTREGA.md",
            "planejamento-executivo-diretoria_contrato_compras_licitacoes-extrema.md",
        ],
    }

    total_moved = 0
    for folder, files in taxonomy.items():
        dest = SRC / folder
        dest.mkdir(exist_ok=True)
        print(f"\n--- {folder}/ ---")
        for fname in files:
            if move_file(SRC / fname, dest, folder):
                total_moved += 1

    # Show remaining root files
    remaining = [f for f in SRC.iterdir() if f.is_file() and f.name not in SKIP_FILES]
    print(f"\nFiles remaining at root: {len(remaining)}")
    for f in remaining:
        print(f"  {f.name}")

    # Total files check
    all_files = [f for f in SRC.rglob("*") if f.is_file() and f.name not in SKIP_FILES
                 and ".claude" not in str(f) and ".mypy_cache" not in str(f)]
    print(f"\nTotal files after reorg: {len(all_files)} (moved: {total_moved})")
    print("[OK] Phase 1 complete")


def phase2():
    print("=== PHASE 2: OUTPUT FOLDER REORGANIZATION ===")
    before = len([f for f in OUT.rglob("*") if f.is_file() and f.name not in SKIP_FILES])
    print(f"Files before: {before}")

    taxonomy = {
        "oficios": [
            "oficio-a-realocacao-bruna-forlim.html",
            "oficio-a-realocacao-bruna-forlim.md",
            "oficio-b-contratualizacao-crie-apae.docx",
            "oficio-b-contratualizacao-crie-apae.html",
            "oficio-b-contratualizacao-crie-apae.md",
            "oficio-b-contratualizacao-crie-apae.v4-pre-narrativa.md",
            "oficio-c-realocacao-centro-integrar.md",
        ],
        "memorandos": [
            "memorando-d-serdi-pipa-centro-integrar.html",
            "memorando-d-serdi-pipa-centro-integrar.md",
            "memorando-e-manutencao-telhado-caps.html",
            "memorando-e-manutencao-telhado-caps.md",
        ],
        "parceria-crie-apae": [
            "parceria-apae-saude-mrosc.md",
            "app-parceria-apae-saude-mrosc.html",
            "diagnostico-oficio-b-v4.md",
            "diagnostico-oficio-b-v4-resolved.md",
            "verificacao-triangulacao-oficio-b.md",
            "relatorio-revisao-oficio-b-v4.md",
            "manual-diagnostico-situacional-centro-integrar.md",
            "manual-diagnostico-situacional-centro-integrar.html",
            "manual-compras-saude-mental.html",
            "diagnostico-situacional-tea-di-extrema.html",
        ],
        "diagnostico-tea": [
            "diagnostico-e1-autismo-por-idade-extrema.docx",
            "diagnostico-e1-autismo-por-idade-extrema.html",
            "diagnostico-e1-autismo-por-idade-extrema.md",
            "diagnostico-e2-revisao-tecnica-psicossocial-tea-extrema.docx",
            "diagnostico-e2-revisao-tecnica-psicossocial-tea-extrema.html",
            "diagnostico-e2-revisao-tecnica-psicossocial-tea-extrema.md",
            "diagnostico-e3-portfolio-grafico-tea-extrema.html",
            "diagnostico-e3-portfolio-grafico-tea-extrema.pptx",
            "relatorio_tea_extrema.html",
            "saude_professor_3523105.html",
            "saude_professor_3550308.html",
        ],
        "reforma-telhado-caps": [
            "pesquisa-precos-reforma-telhado-caps.html",
            "pesquisa-precos-reforma-telhado-caps.md",
            "relatorio-executivo-reforma-telhado-caps.html",
            "relatorio-executivo-reforma-telhado-caps.md",
        ],
    }

    # Files to move into reviews/ (from root)
    review_files = [
        "critical-review-oficio-b-crie-apae.md",
        "critical-review-parceria-apae-mrosc.md",
        "critical-review-parceria-apae-mrosc.txt",
        "expert-evaluation-oficio-crie-apae.md",
        "revisao-critica-tarefas-ADE-2026-02-04.md",
    ]

    total_moved = 0

    # Move taxonomy files
    for folder, files in taxonomy.items():
        dest = OUT / folder
        dest.mkdir(exist_ok=True)
        print(f"\n--- {folder}/ ---")
        for fname in files:
            if move_file(OUT / fname, dest, folder):
                total_moved += 1

    # Move PNGs from e3-graficos/ to diagnostico-tea/graficos/
    graf_src = OUT / "e3-graficos"
    graf_dest = OUT / "diagnostico-tea" / "graficos"
    graf_dest.mkdir(parents=True, exist_ok=True)
    if graf_src.exists():
        print(f"\n--- diagnostico-tea/graficos/ ---")
        for f in graf_src.iterdir():
            if f.is_file() and f.name != ".gitkeep":
                shutil.move(str(f), str(graf_dest / f.name))
                print(f"  -> diagnostico-tea/graficos/{f.name}")
                total_moved += 1
        # Remove empty old folder (ignore OneDrive lock errors)
        remaining = list(graf_src.iterdir())
        if not remaining or all(f.name == ".gitkeep" for f in remaining):
            try:
                shutil.rmtree(str(graf_src))
                print("  [OK] Removed empty e3-graficos/")
            except PermissionError:
                print("  [INFO] e3-graficos/ empty but locked by OneDrive — remove manually")

    # Move review files
    reviews_dest = OUT / "reviews"
    reviews_dest.mkdir(exist_ok=True)
    print(f"\n--- reviews/ ---")
    for fname in review_files:
        if move_file(OUT / fname, reviews_dest, "reviews"):
            total_moved += 1

    # Move empty placeholder folders to _staging/
    staging = OUT / "_staging"
    staging.mkdir(exist_ok=True)
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
                old.rmdir()
            print(f"  -> _staging/{d}/")

    # Count after
    after = len([f for f in OUT.rglob("*") if f.is_file() and f.name not in SKIP_FILES])
    print(f"\nFiles after: {after}")

    # Show remaining root files
    remaining = [f for f in OUT.iterdir() if f.is_file() and f.name not in SKIP_FILES]
    if remaining:
        print(f"\n[INFO] Files remaining at output root ({len(remaining)}):")
        for f in remaining:
            print(f"  {f.name}")
    else:
        print("[OK] No orphan files at root")

    print(f"\n[OK] Phase 2 complete (moved: {total_moved})")


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "count"

    if action == "count":
        count_files()
    elif action == "phase0":
        phase0()
    elif action == "phase1":
        phase1()
    elif action == "phase2":
        phase2()
    elif action == "all":
        phase0()
        print()
        phase1()
        print()
        phase2()
    else:
        print("Usage: py -3.13 tools/reorganize_procurement.py count|phase0|phase1|phase2|all")
