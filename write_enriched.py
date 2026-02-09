import os

output_path = r"c:\Users\caiov\OneDrive\Desktop\MEMÓRIA TÉCNICA AI\SAÚDE MENTAL\PLANEJAMENTO\Protocolo SM Extrema 2026\referencias_transcripts\formacao\oficinas\Manual para a organizacao da oficina sobre escalonamento do cuidado em saude mental.md"

source_path = r"c:\Users\caiov\OneDrive\Desktop\MEMÓRIA TÉCNICA AI\SAÚDE MENTAL\PLANEJAMENTO\Protocolo SM Extrema 2026\referencias_preprocessed\formacao\oficinas\Manual para a organizacao da oficina sobre escalonamento do cuidado em saude mental.md"

with open(source_path, 'r', encoding='utf-8') as f:
    original_lines = f.readlines()

# Find where original content starts (after the preliminary YAML block)
in_yaml = False
yaml_end = 0
for i, line in enumerate(original_lines):
    if line.strip() == '---' and i == 0:
        in_yaml = True
        continue
    if in_yaml and line.strip() == '---':
        yaml_end = i + 1
        break

# Get original content after the preliminary YAML
original_content = ''.join(original_lines[yaml_end:])

# Build enriched frontmatter
frontmatter = '''---
doc_id: REF-FOR-016
source_file: "formacao/oficinas/Manual para a organizacao da oficina sobre escalonamento do cuidado em saude mental.pdf"
taxonomy: formacao/oficinas
doc_type: material_formacao
title: "Saude Mental na APS: Manual para Organizacao da Oficina sobre Escalonamento do Cuidado em Saude Mental"
authors:
  - Claudielle De Santana Teodoro
  - Joana Moscoso Teixeira de Mendonca
  - Ana Alice Freire de Sousa
  - Ana Karina de Sousa Gadelha
  - Evelyn Lima de Souza
  - Isadora Siqueira de Souza
  - Larissa Karollyne de Oliveira Santos
  - Valmir Vanderlei Gomes Filho
institution:
  - "Ministerio da Saude - Secretaria de Atencao Primaria a Saude"
  - "Sociedade Beneficente Israelita Brasileira Albert Einstein"
year: 2023
edition: "1a edicao - versao preliminar"
pages_total: 43
topics:
  - escalonamento do cuidado em saude mental
  - Escala CuidaSM
  - Modelo de Atencao as Condicoes Cronicas (MACC)
  - estratificacao de risco em saude mental
  - gestao do cuidado em saude mental na APS
  - Planificacao da Atencao a Saude (PAS)
  - metodologias ativas de ensino-aprendizagem
  - casos clinicos em saude mental
  - Rede de Atencao Psicossocial (RAPS)
  - MI-mhGAP
  - matriciamento em saude mental
  - Escala de Risco Familiar de Coelho-Savassi
  - genograma e ecomapa
key_concepts:
  - escalonamento_cuidado: "Processo sistematico de avaliacao e organizacao do cuidado em saude mental segundo niveis de necessidade, articulando intervencoes da APS com a RAPS conforme o MACC"
  - escala_cuidasm: "Instrumento de 31 itens (17 autorreferidos + 14 profissionais) para avaliacao da necessidade de cuidado em saude mental, com pontuacao de 0 a 31 pontos classificada em baixa, moderada, alta e altissima necessidade"
  - macc_niveis: "Piramide de 5 niveis do Modelo de Atencao as Condicoes Cronicas: N1 determinantes sociais, N2 fatores de risco, N3 condicao simples, N4 condicao complexa, N5 condicao muito complexa"
  - rodadas_conhecimento: "Adaptacao do metodo World Cafe para discussao de casos clinicos em pequenos grupos rotativos com relator fixo por estacao"
  - plano_de_acao_dispersao: "Instrumento de planejamento pos-oficina para incorporacao do escalonamento do cuidado na rotina das equipes da APS"
  - coelho_savassi: "Escala de Risco Familiar com sentinelas de risco e escores R1 (menor), R2 (medio) e R3 (maximo)"
clinical_relevance: "Alta. Documento operacional que instrumentaliza equipes da APS para implementar o escalonamento do cuidado em saude mental utilizando a Escala CuidaSM, com quatro casos clinicos que cobrem os niveis 2 a 5 do MACC (sofrimento psiquico sem transtorno, transtorno mental comum, transtorno mental grave e transtorno mental grave e persistente). Fornece roteiro completo de oficina com metodologias ativas, incluindo genogramas, ecomapas e Escala de Coelho-Savassi para cada caso."
target_audience:
  - referencias tecnicas de saude mental
  - tutores de Planificacao da Atencao a Saude (PAS)
  - profissionais de nivel superior da APS (medicos, enfermeiros, psicologos, assistentes sociais, farmaceuticos, dentistas, educadores fisicos, nutricionistas, fisioterapeutas)
  - equipes da Rede de Atencao Psicossocial (RAPS)
  - gestores municipais de saude mental
summary: >
  Manual tecnico-pedagogico produzido pelo projeto Saude Mental na APS (PROADI-SUS, trienio 2021-2023),
  parceria entre Ministerio da Saude e Hospital Albert Einstein, destinado a orientar a realizacao de oficinas
  locais sobre escalonamento do cuidado em saude mental na Atencao Primaria a Saude. O documento esta
  estruturado em tres partes: (1) planejamento logistico e pedagogico das oficinas, (2) roteiro detalhado de
  seis atividades com 5 horas de duracao total -- acolhimento, dinamica de embarque, exposicao dialogada
  com quiz, rodadas de conhecimento (adaptacao do World Cafe), construcao de plano de acao para dispersao
  e desembarque reflexivo --, e (3) materiais de apoio incluindo quatro casos clinicos completos (Marina,
  Rodrigo, Patricia e Luis) com aplicacao pratica da Escala CuidaSM, genogramas, ecomapas e Escala de
  Risco Familiar de Coelho-Savassi. Os casos cobrem progressivamente os niveis 2 a 5 do Modelo de Atencao
  as Condicoes Cronicas (MACC), desde sofrimento psiquico com fatores de risco ate transtorno mental grave
  e persistente com altissima necessidade de cuidado. Inclui roteiro para rodada de fechamento com gabarito
  dos casos e modelo de plano de acao. Metodologia alinhada a Planificacao da Atencao a Saude e ao
  MI-mhGAP. Relevancia direta para implementacao do escalonamento do cuidado em Extrema-MG.
references_count: 4
quality_flags:
  - versao_preliminar
  - text_extraction_quality_069
  - tabelas_com_formatacao_degradada_na_extracao
  - genogramas_e_ecomapas_como_texto_nao_visual
  - escala_coelho_savassi_repetida_4_vezes
file_hash: f4a1a53c801ae05a9b0f2b6ff1541c08
processed_at: "2026-02-08T10:21:24.829982"
enriched_at: "2026-02-08"
---
'''

sintese = '''
# Saude Mental na APS: Manual para Organizacao da Oficina sobre Escalonamento do Cuidado em Saude Mental

## Sintese Executiva

Este manual, produzido pela parceria entre o Ministerio da Saude e o Hospital Israelita Albert Einstein no ambito do projeto Saude Mental na APS (PROADI-SUS, trienio 2021-2023), constitui um guia tecnico-pedagogico para a realizacao de oficinas locais sobre escalonamento do cuidado em saude mental na Atencao Primaria a Saude. O documento se insere na Etapa 4 da Planificacao da Atencao a Saude (PAS) -- Gestao do Cuidado em Saude Mental -- e utiliza metodologias ativas de ensino-aprendizagem para capacitar profissionais de nivel superior da APS na utilizacao da Escala CuidaSM e na implementacao sistematica do escalonamento do cuidado.

O manual apresenta um roteiro completo de oficina com seis atividades distribuidas em 5 horas: acolhimento com contrato de aprendizagem, dinamica de aquecimento (embarque), exposicao dialogada com quiz sobre o Modelo de Atencao as Condicoes Cronicas (MACC), rodadas de conhecimento no formato World Cafe com quatro casos clinicos, construcao de plano de acao para o periodo de dispersao e atividade reflexiva de desembarque. Os quatro casos clinicos (Marina, Rodrigo, Patricia e Luis) cobrem progressivamente os niveis 2 a 5 do MACC, demonstrando a aplicacao pratica da Escala CuidaSM em cenarios de complexidade crescente -- desde sofrimento psiquico sem transtorno mental instalado ate transtorno mental grave e persistente com altissima necessidade de cuidado (13 pontos). Cada caso inclui genograma familiar, ecomapa de rede de suporte e Escala de Risco Familiar de Coelho-Savassi, fornecendo uma avaliacao multidimensional que fundamenta as decisoes de escalonamento.

A relevancia para o contexto de Extrema-MG e direta: o material fornece o roteiro operacional e os instrumentos necessarios para capacitar as equipes de eSF e eMulti no uso da Escala CuidaSM e na articulacao do cuidado escalonado com a RAPS local, alinhando-se a metodologia de Planificacao ja adotada pelo municipio.

---

'''

os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(frontmatter)
    f.write(sintese)
    f.write(original_content)

print(f"File written successfully. Size: {os.path.getsize(output_path)} bytes")
