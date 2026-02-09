param(
    [string]$Action = "count"
)

$src = "c:\Users\caiov\OneDrive\Desktop\MEMÓRIA TÉCNICA AI\SAÚDE MENTAL\Licitacoes_Compras_e_Contratos"
$out = "c:\Users\caiov\OneDrive\Desktop\Claude AI\Projetos\projeto-local-compras-e-licitacoes\Extrema-main\Extrema-main\output"

function Count-Files {
    Write-Host "=== SOURCE FOLDER ==="
    $srcFiles = Get-ChildItem $src -File | Where-Object { $_.Name -ne 'desktop.ini' }
    Write-Host "Total files: $($srcFiles.Count)"
    $srcFiles | Group-Object Extension | Sort-Object Count -Descending | Format-Table Name, Count -AutoSize

    Write-Host "`n=== OUTPUT FOLDER ==="
    $outFiles = Get-ChildItem $out -File -Recurse | Where-Object { $_.Name -ne '.gitkeep' }
    Write-Host "Total files: $($outFiles.Count)"
    $outFiles | Group-Object Extension | Sort-Object Count -Descending | Format-Table Name, Count -AutoSize
}

function Phase0-Dedup {
    Write-Host "=== PHASE 0: DEDUPLICATION ==="

    # Create _duplicados
    $dupDir = Join-Path $src "_duplicados"
    if (-not (Test-Path $dupDir)) { New-Item -ItemType Directory -Path $dupDir | Out-Null }

    # Move duplicates
    $dup1 = Join-Path $src "DicasEstudarOnline_NLLC-AspectosGeraisPontosAtencao_ECG (1).pdf"
    $dup2 = Join-Path $src "DicasEstudarOnline_NLLC-AspectosGeraisPontosAtencao_ECG (2).pdf"

    if (Test-Path $dup1) {
        Move-Item $dup1 $dupDir -Force
        Write-Host "[OK] Moved duplicate (1) to _duplicados/"
    }
    if (Test-Path $dup2) {
        Move-Item $dup2 $dupDir -Force
        Write-Host "[OK] Moved duplicate (2) to _duplicados/"
    }

    # Verify MD5 match
    $orig = Join-Path $src "DicasEstudarOnline_NLLC-AspectosGeraisPontosAtencao_ECG.pdf"
    if (Test-Path $orig) {
        $origHash = (Get-FileHash $orig -Algorithm MD5).Hash
        Write-Host "Original hash: $origHash"

        $moved1 = Join-Path $dupDir "DicasEstudarOnline_NLLC-AspectosGeraisPontosAtencao_ECG (1).pdf"
        $moved2 = Join-Path $dupDir "DicasEstudarOnline_NLLC-AspectosGeraisPontosAtencao_ECG (2).pdf"
        if (Test-Path $moved1) {
            $h1 = (Get-FileHash $moved1 -Algorithm MD5).Hash
            if ($h1 -eq $origHash) { Write-Host "[OK] Duplicate (1) hash matches" }
            else { Write-Host "[WARN] Duplicate (1) hash MISMATCH: $h1" }
        }
        if (Test-Path $moved2) {
            $h2 = (Get-FileHash $moved2 -Algorithm MD5).Hash
            if ($h2 -eq $origHash) { Write-Host "[OK] Duplicate (2) hash matches" }
            else { Write-Host "[WARN] Duplicate (2) hash MISMATCH: $h2" }
        }
    }

    Write-Host "`n[OK] Phase 0 complete"
}

function Phase1-ReorgSource {
    Write-Host "=== PHASE 1: SOURCE FOLDER REORGANIZATION ==="

    # Count before
    $before = (Get-ChildItem $src -File | Where-Object { $_.Name -ne 'desktop.ini' }).Count
    Write-Host "Files before: $before"

    # Create directories
    $dirs = @("normativos", "mrosc", "capacitacao_nllc", "benchmarks", "projeto_crie", "instrumentos_gerados", "sinteses_ia")
    foreach ($d in $dirs) {
        $path = Join-Path $src $d
        if (-not (Test-Path $path)) { New-Item -ItemType Directory -Path $path | Out-Null }
        Write-Host "[OK] Created $d/"
    }

    # --- normativos/ ---
    $normativos = @(
        "licitacoes_e_contratos_administrativos_L14133.pdf",
        "L12764.pdf",
        "Lei Entidades Beneficentes.pdf",
        "DELIBERAÇÃO_CIB_SUS_MG_1403_2013.pdf",
        "OSC_Leis, Decretos e Normas do Ministério da Saúde.pdf",
        "PORTARIA INTERMINISTERIAL SG_MGI_AGU Nº 197, DE 11 DE AGOSTO DE 2025 - Transferegov.br.pdf",
        "DECRETO Nº 47.132, DE 20 DE JANEIRO.txt"
    )
    foreach ($f in $normativos) {
        $p = Join-Path $src $f
        if (Test-Path $p) { Move-Item $p (Join-Path $src "normativos") -Force; Write-Host "  -> normativos/$f" }
        else { Write-Host "  [SKIP] Not found: $f" }
    }

    # --- mrosc/ ---
    $mrosc = @(
        "Manual_MROSC.pdf",
        "manual_MROSC_MG_AGE.pdf",
        "A aplicabilidade do MROSC nas parcerias da Saúde – Observatório da Sociedade Civil.pdf",
        "A aplicabilidade do MROSC nas parcerias da Saúde – Observatório da Sociedade Civil2.pdf",
        "Anexo I - Manual MROSC - Modelo de Proposta e Plano de Trabalho.docx",
        "Anexo IV - Manual MROSC - Modelo Técnico de Monitoramento e Avaliação.docx"
    )
    foreach ($f in $mrosc) {
        $p = Join-Path $src $f
        if (Test-Path $p) { Move-Item $p (Join-Path $src "mrosc") -Force; Write-Host "  -> mrosc/$f" }
        else { Write-Host "  [SKIP] Not found: $f" }
    }

    # --- capacitacao_nllc/ ---
    $cap = @(
        "DicasEstudarOnline_NLLC-AspectosGeraisPontosAtencao_ECG.pdf",
        "NLLC_Material de Apoio aos Vídeos do Módulo 1.pdf",
        "NLLC_Material de Apoio aos Vídeos do Módulo 2.pdf",
        "Cartilha - Transferencias Especiais 2025.pdf",
        "manual-de-boas-praticas-em-contratacoes-publicas.pdf",
        "Contratação GOV.pdf",
        "4.1. Estudo Técnico Preliminar (ETP)  Licitações e Contratos.pdf"
    )
    foreach ($f in $cap) {
        $p = Join-Path $src $f
        if (Test-Path $p) { Move-Item $p (Join-Path $src "capacitacao_nllc") -Force; Write-Host "  -> capacitacao_nllc/$f" }
        else { Write-Host "  [SKIP] Not found: $f" }
    }

    # --- benchmarks/ ---
    $bench = @(
        "exemplo_apae_pouso_alegre.pdf",
        "exemplo_apae_2.pdf",
        "Estudo+Tecnico+Preliminar+000004+2025.pdf",
        "copy_of_ANEXO_IV_MODELO_DE_PLANO_DE_TRABALHO_ajustada_27.09.2023.pdf",
        "Plano_de_trabalho_Saude_para_manutencao_de_pagamento_e_educador_fisico_assinado.pdf"
    )
    foreach ($f in $bench) {
        $p = Join-Path $src $f
        if (Test-Path $p) { Move-Item $p (Join-Path $src "benchmarks") -Force; Write-Host "  -> benchmarks/$f" }
        else { Write-Host "  [SKIP] Not found: $f" }
    }

    # --- projeto_crie/ ---
    $crie = @(
        "TR - CRIE.docx",
        "PLANO DE TRABALHO CRIE.docx",
        "CUSTO FUNCIONARIO com educador fisico 2.pdf",
        "RELATÓRIO_TÉCNICO_CAPS_I e II.docx"
    )
    foreach ($f in $crie) {
        $p = Join-Path $src $f
        if (Test-Path $p) { Move-Item $p (Join-Path $src "projeto_crie") -Force; Write-Host "  -> projeto_crie/$f" }
        else { Write-Host "  [SKIP] Not found: $f" }
    }

    # --- instrumentos_gerados/ ---
    $instr = @(
        "TERMO_DE_REFERENCIA_CRIE_SMS_Extrema.docx",
        "PLANO_DE_TRABALHO_CRIE_SMS_Extrema.docx",
        "06 - Minuta do Termo de Referência.docx",
        "07 - Termo de Justificativa Técnica.docx",
        "09 - Minuta de Contratos.docx"
    )
    foreach ($f in $instr) {
        $p = Join-Path $src $f
        if (Test-Path $p) { Move-Item $p (Join-Path $src "instrumentos_gerados") -Force; Write-Host "  -> instrumentos_gerados/$f" }
        else { Write-Host "  [SKIP] Not found: $f" }
    }

    # --- sinteses_ia/ ---
    $sinteses = @(
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
        "planejamento-executivo-diretoria_contrato_compras_licitacoes-extrema.md"
    )
    foreach ($f in $sinteses) {
        $p = Join-Path $src $f
        if (Test-Path $p) { Move-Item $p (Join-Path $src "sinteses_ia") -Force; Write-Host "  -> sinteses_ia/$f" }
        else { Write-Host "  [SKIP] Not found: $f" }
    }

    # Count after (files remaining at root that should stay)
    $rootFiles = Get-ChildItem $src -File | Where-Object { $_.Name -ne 'desktop.ini' }
    Write-Host "`nFiles remaining at root: $($rootFiles.Count)"
    $rootFiles | ForEach-Object { Write-Host "  $($_.Name)" }

    $allFiles = (Get-ChildItem $src -File -Recurse | Where-Object { $_.Name -ne 'desktop.ini' }).Count
    Write-Host "`nTotal files after reorg: $allFiles"
    Write-Host "[OK] Phase 1 complete"
}

function Phase2-ReorgOutput {
    Write-Host "=== PHASE 2: OUTPUT FOLDER REORGANIZATION ==="

    # Count before
    $before = (Get-ChildItem $out -File -Recurse | Where-Object { $_.Name -ne '.gitkeep' }).Count
    Write-Host "Files before: $before"

    # Create directories
    $dirs = @("oficios", "memorandos", "parceria-crie-apae", "diagnostico-tea", "diagnostico-tea\graficos", "reforma-telhado-caps", "_staging")
    foreach ($d in $dirs) {
        $path = Join-Path $out $d
        if (-not (Test-Path $path)) { New-Item -ItemType Directory -Path $path | Out-Null }
    }

    # --- oficios/ ---
    $oficios = @(
        "oficio-a-realocacao-bruna-forlim.html",
        "oficio-a-realocacao-bruna-forlim.md",
        "oficio-b-contratualizacao-crie-apae.docx",
        "oficio-b-contratualizacao-crie-apae.html",
        "oficio-b-contratualizacao-crie-apae.md",
        "oficio-b-contratualizacao-crie-apae.v4-pre-narrativa.md",
        "oficio-c-realocacao-centro-integrar.md"
    )
    foreach ($f in $oficios) {
        $p = Join-Path $out $f
        if (Test-Path $p) { Move-Item $p (Join-Path $out "oficios") -Force; Write-Host "  -> oficios/$f" }
    }

    # --- memorandos/ ---
    $memos = @(
        "memorando-d-serdi-pipa-centro-integrar.html",
        "memorando-d-serdi-pipa-centro-integrar.md",
        "memorando-e-manutencao-telhado-caps.html",
        "memorando-e-manutencao-telhado-caps.md"
    )
    foreach ($f in $memos) {
        $p = Join-Path $out $f
        if (Test-Path $p) { Move-Item $p (Join-Path $out "memorandos") -Force; Write-Host "  -> memorandos/$f" }
    }

    # --- parceria-crie-apae/ ---
    $parceria = @(
        "parceria-apae-saude-mrosc.md",
        "app-parceria-apae-saude-mrosc.html",
        "diagnostico-oficio-b-v4.md",
        "diagnostico-oficio-b-v4-resolved.md",
        "verificacao-triangulacao-oficio-b.md",
        "relatorio-revisao-oficio-b-v4.md",
        "manual-diagnostico-situacional-centro-integrar.md",
        "manual-diagnostico-situacional-centro-integrar.html",
        "manual-compras-saude-mental.html",
        "diagnostico-situacional-tea-di-extrema.html"
    )
    foreach ($f in $parceria) {
        $p = Join-Path $out $f
        if (Test-Path $p) { Move-Item $p (Join-Path $out "parceria-crie-apae") -Force; Write-Host "  -> parceria-crie-apae/$f" }
    }

    # --- diagnostico-tea/ ---
    $diag = @(
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
        "saude_professor_3550308.html"
    )
    foreach ($f in $diag) {
        $p = Join-Path $out $f
        if (Test-Path $p) { Move-Item $p (Join-Path $out "diagnostico-tea") -Force; Write-Host "  -> diagnostico-tea/$f" }
    }

    # Move PNGs from e3-graficos to diagnostico-tea/graficos
    $grafsrc = Join-Path $out "e3-graficos"
    if (Test-Path $grafsrc) {
        Get-ChildItem $grafsrc -File | ForEach-Object {
            Move-Item $_.FullName (Join-Path $out "diagnostico-tea\graficos") -Force
            Write-Host "  -> diagnostico-tea/graficos/$($_.Name)"
        }
        # Remove old folder if empty
        if ((Get-ChildItem $grafsrc).Count -eq 0) { Remove-Item $grafsrc }
    }

    # --- reforma-telhado-caps/ ---
    $reforma = @(
        "pesquisa-precos-reforma-telhado-caps.html",
        "pesquisa-precos-reforma-telhado-caps.md",
        "relatorio-executivo-reforma-telhado-caps.html",
        "relatorio-executivo-reforma-telhado-caps.md"
    )
    foreach ($f in $reforma) {
        $p = Join-Path $out $f
        if (Test-Path $p) { Move-Item $p (Join-Path $out "reforma-telhado-caps") -Force; Write-Host "  -> reforma-telhado-caps/$f" }
    }

    # --- reviews/ (move scattered review files into existing reviews/) ---
    $reviews = @(
        "critical-review-oficio-b-crie-apae.md",
        "critical-review-parceria-apae-mrosc.md",
        "critical-review-parceria-apae-mrosc.txt",
        "expert-evaluation-oficio-crie-apae.md",
        "revisao-critica-tarefas-ADE-2026-02-04.md"
    )
    foreach ($f in $reviews) {
        $p = Join-Path $out $f
        if (Test-Path $p) { Move-Item $p (Join-Path $out "reviews") -Force; Write-Host "  -> reviews/$f" }
    }

    # --- _staging/ (move empty placeholder folders) ---
    foreach ($d in @("etp", "pareceres", "tr")) {
        $oldPath = Join-Path $out $d
        $newPath = Join-Path $out "_staging\$d"
        if (Test-Path $oldPath) {
            if (-not (Test-Path $newPath)) { New-Item -ItemType Directory -Path $newPath | Out-Null }
            # Move gitkeep if exists
            $gk = Join-Path $oldPath ".gitkeep"
            if (Test-Path $gk) { Move-Item $gk $newPath -Force }
            # Remove old folder if empty
            if ((Get-ChildItem $oldPath).Count -eq 0) { Remove-Item $oldPath }
            Write-Host "  -> _staging/$d/"
        }
    }

    # Count after
    $after = (Get-ChildItem $out -File -Recurse | Where-Object { $_.Name -ne '.gitkeep' }).Count
    Write-Host "`nFiles after: $after"

    # Show any remaining root files
    $rootFiles = Get-ChildItem $out -File | Where-Object { $_.Name -ne '.gitkeep' }
    if ($rootFiles.Count -gt 0) {
        Write-Host "`n[WARN] Files remaining at output root:"
        $rootFiles | ForEach-Object { Write-Host "  $($_.Name)" }
    } else {
        Write-Host "[OK] No orphan files at root"
    }

    Write-Host "[OK] Phase 2 complete"
}

# Execute requested action
switch ($Action) {
    "count" { Count-Files }
    "phase0" { Phase0-Dedup }
    "phase1" { Phase1-ReorgSource }
    "phase2" { Phase2-ReorgOutput }
    "all" { Phase0-Dedup; Phase1-ReorgSource; Phase2-ReorgOutput }
    default { Write-Host "Usage: -Action count|phase0|phase1|phase2|all" }
}
