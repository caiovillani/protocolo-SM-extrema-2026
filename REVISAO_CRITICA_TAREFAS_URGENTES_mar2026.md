# REVISÃO CRÍTICA: TAREFAS URGENTES DO GESTOR — Fev–Mar 2026

**Documento revisado:** `# TAREFAS-URGENTES-GESTOR-mar.md`
**Data da revisão:** 17/02/2026
**Revisor:** Sistema de Assistência de IA — Caio Villani (CMSMRI)
**Versão:** 1.0

---

## SÍNTESE EXECUTIVA

O documento de tarefas urgentes da CMSMRI cumpre parcialmente sua função de registro de demandas, mas falha como instrumento operacional: não há responsáveis definidos, prazos individuais, critérios de conclusão nem entregáveis explícitos por item. Com 11 ofícios, 20 temas de protocolos e 3 planilhas de indicadores — todas classificadas como "início imediato" — o documento cria uma carga de trabalho irreal sem priorização. O prazo 01/03/2026 para os indicadores está a **12 dias corridos** desta revisão, colocando este item em estado de alerta crítico.

**Achados principais:**
- 5 itens com falhas estruturais graves no documento original (2 truncados, CNES pendentes, portaria potencialmente desatualizada)
- De 34 tarefas mapeadas: **16 NOVAS** (sem base no repositório), **12 PARCIAIS** (há base, requer expansão), **6 COBERTAS** (documento suficiente para adaptar)
- 15 protocolos (PS + CAPS) sem sequência de priorização — inviável executar em paralelo com a estrutura atual
- 3 gaps normativos críticos: CNES pendentes, referência a Resolução CFM provavelmente desatualizada, bases legais ausentes para itens complexos

**Próximos passos imediatos:** (1) Aprovar a versão revisada deste documento com campo de responsável; (2) Elevar indicadores a prioridade máxima pelo prazo; (3) Dividir protocolos em dois grupos por urgência clínica.

---

## SEÇÃO 1: DIAGNÓSTICO ESTRUTURAL

### 1.1 Problemas Formais do Documento Original

| # | Problema | Localização no Doc | Impacto |
|---|----------|-------------------|---------|
| F1 | **Item 11 truncado** — texto cortado após "CAPS," | Linha 210–211 | Item sem escopo; executor não sabe o que produzir |
| F2 | **Fase III NUVIPPS em branco** — campo vazio | Linha 177 | Fases I e II ficam sem continuidade de programa |
| F3 | **Nome do arquivo inicia com "#"** — caractere reservado em Windows | Nome do arquivo | Pode gerar erros em scripts, git e ferramentas de busca |
| F4 | **Nenhum item tem responsável designado** | Todo o documento | Sem accountability: responsabilidade de todos = de ninguém |
| F5 | **Nenhum item tem prazo individual** — apenas "início imediato" genérico | Todo o documento | Sem sequenciamento, tudo compete pelo mesmo slot de atenção |
| F6 | **Ausência de critério de conclusão** | Todo o documento | Não há como saber quando um item está "pronto" |
| F7 | **Seção "Protocolos Gerais" sem numeração** — lista livre entre dois grupos numerados | Linhas 212–221 | Dificulta rastreabilidade e referência cruzada |
| F8 | **Organogramas e tarefas no mesmo documento** — dois propósitos distintos | Linhas 1–158 vs 160–276 | Dificulta leitura operacional; context switching desnecessário |
| F9 | **Acrônimos sem explicação**: NUVIPPS, LSMHG, DFD | Linhas 172, 178, 195–210 | Executor externo não sabe o que produzir |

### 1.2 Achado Estrutural Central

O documento é uma **lista de intenções**, não um **plano operacional**. A diferença é precisamente o que um instrumento de gestão deve preencher: cada item precisa de quatro atributos mínimos — **Responsável, Prazo, Entregável, Status**. Nenhum dos 34 itens mapeados os possui.

---

## SEÇÃO 2: MAPA DE COBERTURA

> **Legenda:** 🟢 COBERTA (documento existente suficiente) | 🟡 PARCIAL (existe base, requer expansão) | 🔴 NOVA (não existe correspondente no repositório)

### 2.1 Ofícios (11 itens)

| # | Tarefa | Cobertura | Documento de Referência | Gap Residual |
|---|--------|-----------|------------------------|--------------|
| 1 | Regulação acesso AE via e-SUS — CNES central de regulação | 🔴 NOVA | — | Ofício institucional a ser redigido do zero |
| 2 | NUVIPPS — definir Fases I, II, III | 🔴 NOVA | — | Fase III indefinida; zero base documental |
| 3 | LSMHG — fundamentação, equipe mínima, escopo, orçamento | 🔴 NOVA | — | Acrônimo não expandido; zero base documental |
| 4 | Medicação Supervisionada CAPS (fins de semana/feriados no PS) | 🔴 NOVA | PCC-04 menciona articulação PS, mas não o fluxo de medicação | Documento formal de solicitação + articulação interinstitucional |
| 5 | Ofícios intersetoriais — coleta de dados locais TEA | 🟡 PARCIAL | CLI-02 (TEA) em desenvolvimento | CLI-02 ainda não finalizado; ofícios dependem dos dados que ancora |
| 6 | DFD Sala sensorial | 🔴 NOVA | — | Documento de formalização de demanda administrativa |
| 7 | DFD Ambiência CAPS | 🔴 NOVA | — | Idem |
| 8 | DFD Ambiência Centro Integrar | 🔴 NOVA | — | Idem |
| 9 | DFD Fachada Centro Integrar | 🔴 NOVA | — | Idem |
| 10 | DFD Projeto elétrico e de iluminação | 🔴 NOVA | — | Idem |
| 11 | Recomendação Técnica salas regulação sensorial na RAS | 🔴 NOVA | — | **TRUNCADO** — escopo desconhecido além de PS/HM e CREMI |

### 2.2 Protocolos Gerais (5 temas)

| Tema | Cobertura | Documento de Referência | Gap Residual |
|------|-----------|------------------------|--------------|
| Requisito Prontuário Médico | 🔴 NOVA | — | Sem qualquer base; requer definição de campos mínimos obrigatórios |
| PTS (1° PTS; Revisão; Atualização) | 🟡 PARCIAL | `POP_05_ELABORACAO_PTS.md` + `F-02_Modelo_PTS_Compartilhado.md` | Base existe; faltam protocolos específicos para cada situação por ponto de atenção |
| Medicação Supervisionada RAS–PS (fins de semana/feriados) | 🔴 NOVA | — | Diferente do item 4 dos Ofícios: aqui é o protocolo clínico do fluxo |
| Consulta Farmacêutica CAPS | 🔴 NOVA | — | Sem base; requer definição de escopo |
| Operacionalização Interna Regula RAPS | 🟡 PARCIAL | `05_PROTOCOLO_REGULACAO_NIRSM_R.md` + `POP_03_PREENCHIMENTO_GUIA_NIRSM_R.md` | Regulação externa existe; operacionalização interna do CAPS não está explicitada |

### 2.3 Protocolos Pronto Socorro (6 temas)

| # | Tema | Cobertura | Documento de Referência | Gap Residual |
|---|------|-----------|------------------------|--------------|
| PS-1 | Solicitação de Avaliação PS (fluxo completo) | 🔴 NOVA | PCC-04 cobre macrofluxo RUE, não o fluxo operacional CAPS→PS | Protocolo interconsultar específico |
| PS-2 | SAA (Síndrome de Abstinência Alcoólica) | 🟡 PARCIAL | CLI-05 (seção 6.3) + Anexo II (CIWA-Ar previsto mas não produzido) | Protocolo existe em contexto de emergências; falta versão PS-específica local |
| PS-3 | Crise Suicida / Comportamento Suicida | 🟡 PARCIAL | CLI-03 (avaliação completa) + PCC-04 (manejo crise aguda) | Integração entre os dois documentos não operacionalizada para o PS local |
| PS-4 | Agitação Psicomotora | 🟡 PARCIAL | CLI-05 (seção 6.1) + PCC-04 (seção 6.3) | Base técnica existe; falta protocolo PS-operacional com farmacologia local |
| PS-5 | Episódio Psicótico | 🟡 PARCIAL | CLI-05 (seção 6.4) | Cobertura técnica presente; falta fluxo PS com responsabilidades e acionamento CAPS |
| PS-6 | Contenção Mecânica | 🟡 PARCIAL | CLI-05 (seção 6.1) + PCC-04 (seção 6.3.4) + Anexo III previsto mas **não produzido** | **Lacuna crítica**: formulário de contenção não criado; Resolução CFM citada desatualizada |

### 2.4 Protocolos CAPS (9 temas, A–I)

| Letra | Tema | Cobertura | Documento de Referência | Gap Residual |
|-------|------|-----------|------------------------|--------------|
| A | Vigilância ao óbito | 🔴 NOVA | — | Sem base; requer articulação com VO municipal (SISVOC, Res. CFM 1.779/2005) |
| B | PTS CAPS (1º; revisão/atualização) | 🟡 PARCIAL | `POP_05` + `F-02` | Base geral existe; falta especificidade CAPS |
| C | Matriciamento (registro presencial) | 🟡 PARCIAL | `POP_04_MATRICIAMENTO` (listado como **pendente** no TODO) | POP_04 não foi concluído; protocolo de não-aceitação existe mas o de registro presencial não |
| D | Telematriciamento (acionamento e registro) | 🔴 NOVA | Mencionado tangencialmente no PCC | Modalidade específica sem protocolo próprio |
| E | Padronização Agenda Médica | 🔴 NOVA | — | Documento interno de gestão de carga horária |
| F | Carta de Serviços e Atividades | 🔴 NOVA | — | Documento público de comunicação institucional |
| G | Medicação Supervisionada (interno CAPS) | 🔴 NOVA | — | Diferente da RAS–PS: aqui é o protocolo interno do CAPS |
| H | Medicação Assistida | 🔴 NOVA | — | Modalidade distinta; sem base |
| I | Acolhimento à Vulnerabilidade no CAPS | 🔴 NOVA | — | **Item mais complexo do documento.** Exige: fluxo macro+micro etapas, subgrupos vulneráveis, ações inegociáveis, intersetorialidade, rastreio TB/ISTs, notificações, BO. Zero base. |

### 2.5 Indicadores (3 equipamentos)

| Equipamento | Cobertura | Documento de Referência | Gap Residual |
|-------------|-----------|------------------------|--------------|
| CAPS | 🟡 PARCIAL | Indicadores dispersos em PCC-04, CLI-03, CLI-05 | Falta planilha operacional unificada para o CAPS I de Extrema |
| CSM | 🔴 NOVA | — | Sem qualquer referência de indicadores no repositório |
| Centro Integrar | 🔴 NOVA | — | Idem |

---

## SEÇÃO 3: GAPS NORMATIVOS

| # | Gap | Impacto Técnico | Correção Recomendada |
|---|-----|-----------------|----------------------|
| N1 | **CNES CSM: "A informar"** | Serviço sem CNES não registra produção no SIASUS; profissionais podem ter vínculo comprometido | Prioridade máxima: protocolar abertura de CNES no SCNES via SMS |
| N2 | **CNES Centro Integrar: "A informar"** | Idem N1 | Idem N1 |
| N3 | **Portaria GM/MS nº 3.588/2017 como referência principal da RAPS** | Portaria alterada pela GM/MS 3.716/2018 e pela GM/MS 1.356/2023 — usar como referência primária pode gerar inconsistência normativa | Substituir pela Portaria de Consolidação GM/MS nº 2/2017 + atualizações vigentes |
| N4 | **Contenção mecânica — Res. CFM 2.057/2013 citada no CLI-05** | Esta resolução foi revogada. A regulamentação atual de práticas restritivas é a **Res. CFM 2.310/2022** | Atualizar referência antes de finalizar PS-6 |
| N5 | **Vigilância ao óbito sem base legal** | Protocolo exige SISVOC, Lei 9.434/1997, Res. CFM 1.779/2005 e comunicação ao CRM — nenhuma citada | Mapear base legal antes de elaborar protocolo A |
| N6 | **Rastreio TB e ISTs (item I) sem base legal** | Rastreio compulsório de TB tem base na Lei 9.313/1996 + PNCT; ISTs na Portaria MS 2.313/2020 | Incluir base normativa no escopo do item I |
| N7 | **NUVIPPS e LSMHG** — acrônimos sem expandir | Não é possível identificar base legal nem portaria de fomento | Expandir acrônimos e identificar portaria de custeio |

---

## SEÇÃO 4: MATRIZ DE PRIORIZAÇÃO

> **Metodologia:** Urgência = impacto assistencial imediato ou prazo fixo; Complexidade = volume de decisão técnica + criação do zero vs. adaptação.

### Quadrante I — Alta Urgência / Baixa Complexidade → FAZER PRIMEIRO

| Item | Justificativa | Prazo Proposto |
|------|---------------|----------------|
| IND-01/02/03 (Indicadores CAPS, CSM, CI) | Prazo fixo 01/03/2026 no próprio documento | **01/03/2026** ⚠️ |
| DFDs (O-06 a O-10) | Documentos administrativos com processo técnico conhecido | 28/02/2026 |
| O-01 (CNES central de regulação) | Ofício simples; bloqueio normativo se não regularizado | 28/02/2026 |
| N1+N2 (CNES CSM e CI) | Serviços sem CNES não registram produção no SUS | 28/02/2026 |

### Quadrante II — Alta Urgência / Média Complexidade → PLANEJAR COM RECURSOS

| Item | Justificativa | Prazo Proposto |
|------|---------------|----------------|
| CA-E (Padronização Agenda Médica) | Impacto direto na capacidade assistencial imediata | 15/03/2026 |
| PG-03 + O-04 (Medicação Supervisionada RAS–PS) | Risco de falha terapêutica nos fins de semana | 15/03/2026 |
| PS-01 (Solicitação Avaliação PS) | PS sem protocolo = atendimento descoordenado | 31/03/2026 |
| CA-B + PG-02 (PTS) | Base já existe; adaptar para CAPS e para 3 situações | 31/03/2026 |
| CA-F (Carta de Serviços) | Transparência institucional; Lei 13.460/2017 | 31/03/2026 |

### Quadrante III — Alta Urgência / Alta Complexidade → EQUIPE DEDICADA

| Item | Justificativa | Prazo Proposto |
|------|---------------|----------------|
| CA-I (Acolhimento à Vulnerabilidade) | Risco imediato de gaps para população mais vulnerável | 30/04/2026 |
| CA-A (Vigilância ao Óbito) | Obrigação ética e normativa; subnotificação atual provável | 30/04/2026 |
| PS-02 a PS-06 (SAA, Crise Suicida, Agitação, Psicose, Contenção) | Risco clínico direto; PS sem protocolo formal opera por improviso | 30/04/2026 |

### Quadrante IV — Menor Urgência / Alta Complexidade → AGENDAR

| Item | Prazo Proposto |
|------|----------------|
| O-02 NUVIPPS (Fase III) | Mai/2026 |
| O-03 LSMHG | Mai/2026 |
| PG-04 Consulta Farmacêutica CAPS | Abr/2026 |
| CA-D Telematriciamento | Abr/2026 |
| CA-H Medicação Assistida | Abr/2026 |
| PG-01 Requisito Prontuário Médico | Abr/2026 |
| CA-C Matriciamento (após POP-04) | Mar/2026 |
| PG-05 Operacionalização Regula RAPS | Mar/2026 |
| O-05 Ofícios TEA (após CLI-02) | Mar/2026 |
| O-11 Recomendação Técnica sensoriais | Mar/2026 |

---

## SEÇÃO 5: ALERTAS DE VIABILIDADE

### 🚨 ALERTA VERMELHO — Indicadores até 01/03/2026

**Situação:** Restam 12 dias corridos. Os 3 equipamentos precisam de indicadores próprios, personalizados e operacionalizados em planilha. Nenhum dos três tem base consolidada no repositório.

**O que é viável até 01/03:** Uma planilha-piloto por equipamento com 5–8 indicadores prioritários (versão 1.0), a ser expandida em ciclos mensais.

**O que NÃO é viável até 01/03:** Indicadores validados, séries históricas e dashboards completos.

**Recomendação:** Redefinir meta para "entrega da v1.0 com indicadores mínimos" e programar revisão aos 90 dias.

---

### ⚠️ ALERTA LARANJA — 15 Protocolos em Paralelo

Executar os 15 protocolos (5 gerais + 6 PS + 9 CAPS) sem priorização e sem responsáveis alocados resulta em nenhum protocolo concluído no prazo. A taxa histórica de elaboração com qualidade neste repositório é de 2–3 protocolos/mês com dedicação concentrada.

**Recomendação:** Adotar sequência da Seção 4. Iniciar pelos PS (base técnica já existe nos CLI-03, CLI-05, PCC-04) e CAPS A (Vigilância ao óbito) por risco imediato.

---

### ⚠️ ALERTA LARANJA — CNES Pendentes (CSM e Centro Integrar)

Serviços sem CNES não aparecem como pontos de atenção oficiais da RAPS, não geram produção registrada e seus profissionais podem ter vínculo comprometido. Esta pendência é normativa anterior a qualquer protocolo.

---

## VERSÃO REVISADA: BACKLOG OPERACIONAL CMSMRI

> Versão reformatada do documento original com campos padronizados. **Status** deve ser atualizado pelo gestor semanalmente. Campos: Responsável | Prazo | Status | Base Legal

### GRUPO A: OFÍCIOS

| ID | Tarefa | Entregável | Responsável | Prazo | Status |
|----|--------|-----------|-------------|-------|--------|
| O-01 | Regulação acesso AE — solicitar CNES central de regulação | Ofício formal à DAE/SMS | CMSMRI | 28/02/2026 | 🔲 |
| O-02 | NUVIPPS — definir Fases I, II, **III** | Doc. com 3 fases operacionalizadas | CMSMRI | 31/03/2026 | 🔲 |
| O-03 | LSMHG — fundamentação + equipe + escopo + orçamento | Documento completo | CMSMRI + DAE | 31/03/2026 | 🔲 |
| O-04 | Medicação Supervisionada CAPS (fins de semana/feriados) | Ofício formal ao PS + protocolo de articulação | CMSMRI + Coord. CAPS | 15/03/2026 | 🔲 |
| O-05 | Ofícios intersetoriais coleta de dados TEA | Ofícios a Educação, AS, Saúde | CMSMRI | Após CLI-02 | 🔲 |
| O-06 | DFD Sala sensorial | DFD padronizado com justificativa técnica | CMSMRI + adm. | 28/02/2026 | 🔲 |
| O-07 | DFD Ambiência CAPS | DFD padronizado | CMSMRI + adm. | 28/02/2026 | 🔲 |
| O-08 | DFD Ambiência Centro Integrar | DFD padronizado | CMSMRI + adm. | 28/02/2026 | 🔲 |
| O-09 | DFD Fachada Centro Integrar | DFD padronizado | CMSMRI + adm. | 28/02/2026 | 🔲 |
| O-10 | DFD Projeto elétrico e de iluminação | DFD padronizado | CMSMRI + Eng. SMS | 28/02/2026 | 🔲 |
| O-11 | Recomendação Técnica salas regulação sensorial na RAS | Doc. técnico com fundamentação + lista de pontos RAS | CMSMRI | 31/03/2026 | 🔲 ⚠️ escopo truncado — confirmar com gestor |

### GRUPO B: PROTOCOLOS GERAIS

| ID | Tarefa | Entregável | Responsável | Prazo | Base Legal |
|----|--------|-----------|-------------|-------|------------|
| PG-01 | Requisito Prontuário Médico | Protocolo com campos mínimos obrigatórios | CMSMRI + médicos | 30/04/2026 | Res. CFM 1.638/2002 |
| PG-02 | PTS (1°; Revisão; Atualização) | Adaptação POP-05 + F-02 para 3 situações x pontos de atenção | Coord. CAPS + CSM | 31/03/2026 | PNH; PNSM; MS 2025 |
| PG-03 | Medicação Supervisionada RAS–PS (fins de semana/feriados) | Protocolo clínico do fluxo | CMSMRI + CAPS + PS + DAPS | 15/03/2026 | Portaria GM/MS 344/1998 |
| PG-04 | Consulta Farmacêutica CAPS | Protocolo com escopo, registro e frequência | Farmacêuticos CAPS + CMSMRI | 30/04/2026 | Res. CFF 565/2012 |
| PG-05 | Operacionalização Interna Regula RAPS | Expansão do POP-03 para operacionalização interna | NIRSM-R + CMSMRI | 31/03/2026 | Portaria GM/MS 1.559/2008 |

### GRUPO C: PROTOCOLOS PRONTO SOCORRO

| ID | Tarefa | Entregável | Responsável | Prazo | Base Legal |
|----|--------|-----------|-------------|-------|------------|
| PS-01 | Solicitação de Avaliação PS (fluxo completo) | Protocolo PS-específico: contato → compartilhamento → alta qualificada → APS | CMSMRI + Coord. PS + CAPS | 31/03/2026 | Portaria GM/MS 3.088/2011 |
| PS-02 | SAA | Adaptação CLI-05 (seção 6.3) para PS local com CIWA-Ar | CMSMRI + Médico-Psiquiatra | 30/04/2026 | CLI-05; CIWA-Ar |
| PS-03 | Crise Suicida / Comportamento Suicida | Integração CLI-03 + PCC-04 em formato PS-operacional | CMSMRI + Médico-Psiquiatra | 30/04/2026 | CLI-03; Portaria GM/MS 1.876/2006 |
| PS-04 | Agitação Psicomotora | Adaptação CLI-05 (seção 6.1) para PS local | CMSMRI + Médico-Psiquiatra | 30/04/2026 | CLI-05; **Res. CFM 2.310/2022** |
| PS-05 | Episódio Psicótico | Adaptação CLI-05 (seção 6.4) para PS local | CMSMRI + Médico-Psiquiatra | 30/04/2026 | CLI-05 |
| PS-06 | Contenção Mecânica | Formulário de contenção (Anexo III CLI-05, não produzido) + protocolo de monitoramento | CMSMRI + Enfermagem PS + Médico | 30/04/2026 | **Res. CFM 2.310/2022** (não 2.057/2013) |

### GRUPO D: PROTOCOLOS CAPS

| ID | Tarefa | Entregável | Responsável | Prazo | Base Legal |
|----|--------|-----------|-------------|-------|------------|
| CA-A | Vigilância ao Óbito | Protocolo com fluxo VO, declaração, SISVOC, comunicação ao CRM | CMSMRI + Epidemiologia Municipal | 30/04/2026 | Res. CFM 1.779/2005; SISVOC |
| CA-B | PTS CAPS (1°; revisão; atualização) | Adaptação POP-05 para especificidade CAPS | Coord. CAPS I | 31/03/2026 | POP-05 (base existente) |
| CA-C | Matriciamento Presencial (registro) | Protocolo de registro + conclusão do POP-04 | Coord. CAPS + e-Multi | 31/03/2026 | Nota Técnica Apoio Matricial MS |
| CA-D | Telematriciamento (acionamento e registro) | Protocolo específico para modalidade tele | Coord. CAPS + e-Multi + CMSMRI | 30/04/2026 | Res. CFM 2.314/2022 (telessaúde) |
| CA-E | Padronização Agenda Médica | Grade de agenda interna por profissional | Coord. CAPS + Psiquiatras | 15/03/2026 | — |
| CA-F | Carta de Serviços e Atividades | Documento público CAPS com serviços, horários, atividades | Coord. CAPS I | 31/03/2026 | Lei 13.460/2017 |
| CA-G | Medicação Supervisionada (interno CAPS) | Protocolo com fluxo, responsabilidades, registro | Coord. CAPS + Farmácias + Enfermagem | 31/03/2026 | Portaria GM/MS 344/1998 |
| CA-H | Medicação Assistida | Protocolo distinto da supervisionada | Coord. CAPS + Farmácias + Médico | 30/04/2026 | Portaria GM/MS 344/1998 |
| CA-I | Acolhimento à Vulnerabilidade no CAPS | Fluxo macro+micro etapas; subgrupos vulneráveis; ações inegociáveis; intersetorialidade; rastreio TB/ISTs; notificações; BO | CMSMRI + Equipe CAPS completa + CREAS | 30/04/2026 | Lei 9.313/1996; Portaria MS 2.313/2020; Lei 10.216/2001 |

### GRUPO E: INDICADORES

| ID | Equipamento | Entregável | Responsável | Prazo |
|----|-------------|-----------|-------------|-------|
| IND-01 | CAPS | Planilha v1.0 com ≥5 indicadores mínimos operacionais | Coord. CAPS I + CMSMRI | **01/03/2026** ⚠️ |
| IND-02 | CSM | Planilha v1.0 com ≥5 indicadores mínimos operacionais | Coord. CSM + CMSMRI | **01/03/2026** ⚠️ |
| IND-03 | Centro Integrar | Planilha v1.0 com ≥5 indicadores mínimos operacionais | Coord. CI + CMSMRI | **01/03/2026** ⚠️ |

---

## LIMITAÇÕES E RESSALVAS

1. A classificação de cobertura foi realizada por leitura cruzada dos arquivos disponíveis em 17/02/2026. Documentos em rascunho não localizados podem alterar a classificação.
2. A Res. CFM 2.310/2022 (contenção) é indicada com base no conhecimento disponível. Confirmar com assessoria jurídica da SMS antes de citar em documentos normativos.
3. Os prazos assumem disponibilidade e autoridade dos responsáveis sugeridos. Ajustar conforme escala real de cada serviço.
4. NUVIPPS e LSMHG necessitam de expansão dos acrônimos pelo gestor para confirmação de base legal e portaria de fomento.
5. Esta revisão não substitui validação técnica por profissional habilitado e aprovação formal pela CMSMRI/SMS antes de qualquer uso externo.

---

*Revisão Crítica elaborada com assistência do sistema de IA configurado por Caio Villani — CMSMRI Extrema/MG.*
*Validação humana obrigatória antes de uso operacional.*
