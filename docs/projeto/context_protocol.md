# context_protocol.md

## Missao
Definir e documentar protocolos/fluxos de saude mental para a Secretaria Municipal de Saude de Extrema/MG, cobrindo APS <-> AES, com rastreabilidade total por evidencia do corpus.

## Escopo APS <-> AES
- Atencao Primaria a Saude (APS) e Atencao Especializada (AES).
- Integracao, referencia e contrarreferencia, matriciamento e compartilhamento do cuidado.

## Entregaveis
- corpus_index.md
- todos_protocol.md
- insights_protocol.md
- evidence_ledger.csv
- conflicts.md
- mermaid_standards.md
- changelog.md
- /protocols_out/00_sumario_backbone.md
- /protocols_out/01_fluxos_aps_aes.md
- /protocols_out/02_protocolos_por_papel.md
- /protocols_out/03_matriciamento_escalonamento.md
- /protocols_out/04_regulacao_referencia_contrarref.md
- /protocols_out/05_artigo_como_usar.md
- /protocols_out/06_mapa_lacunas.md
- /protocols_out/07_rastreabilidade.md

## Regras R1-R4
- R1: Nao modificar arquivos fonte; somente criar/editar os arquivos autorizados.
- R2: Base-only + rastreabilidade (toda regra/criterio/acao/definicao exige evidencia com localizador; se ausente: "NAO ENCONTRADO NA BASE").
- R3: SAFETY-DEFAULT (user-authorized) apenas em risco iminente; bloco curto e rotulado.
- R4: Privacidade/LGPD: nao reproduzir identificadores pessoais; anonimizar.

## Limites BASE-ONLY
Somente evidencias explicitas do corpus. Nada inferido sem evidencia. Excecao: SAFETY-DEFAULT em risco iminente.

## Regra de duas fases
1) Extracao: indexacao e registro das evidencias.
2) Redacao final: somente apos todos_protocol.md sem TO DO.

## Nota CID
Quando pertinente em textos clinico-normativos, incluir: "CID-10 -> CID-11 (implantacao prevista para 2027 no Brasil)".
