# MEMÓRIA DO PROJETO
## Protocolos de Compartilhamento do Cuidado em Saúde Mental - Extrema/MG

**Última atualização:** 21/01/2026
**Status:** Em desenvolvimento

---

## 1. ESCOPO DO PROJETO

### 1.1 Objetivo Geral
Elaborar o sistema completo de protocolos, fluxos, POPs e instrumentos normativos para o compartilhamento do cuidado em saúde mental no município de Extrema/MG, cobrindo toda a navegação dos usuários nas Redes de Atenção à Saúde (RAS) e Redes Intersetoriais.

### 1.2 Macro Etapas Previstas

**Etapas de Compartilhamento do Cuidado:**
1. Rede Intersetorial → APS (e-ESF/e-Multi) → NIRSM-R → AE Saúde Mental RAPS
2. Demanda Espontânea → APS (e-ESF/e-Multi) → NIRSM-R → AE Saúde Mental RAPS
3. AES Ambulatorial → APS (e-ESF/e-Multi) → NIRSM-R → AE Saúde Mental RAPS
4. APS (e-ESF/e-Multi) → RUE (SAMU/PS) → AE Saúde Mental RAPS

**Etapas de Regulação:**
1. APS (e-ESF/e-Multi) ↔ NIRSM-R ↔ AE Saúde Mental RAPS
2. NIRSM-R → APS (não aceitação) → Matriciamento em Saúde Mental

---

## 2. REGISTRO DE AÇÕES EXECUTADAS

### 2.1 Sessão de 21/01/2026

#### Fase 1: Estruturação do Projeto
| Ação | Status | Observação |
|------|--------|------------|
| Criação da pasta `Protocolos_Compartilhamento_Cuidado` | Concluído | Pasta principal |
| Criação da subpasta `POPs` | Concluído | Protocolos Operacionais Padrão |
| Criação da subpasta `Escalas_Instrumentos` | Concluído | Formulários e fichas |
| Criação da subpasta `Relatorios_Executivos` | Concluído | Documentos de síntese |

#### Fase 2: Elaboração dos Protocolos de Fluxo Assistencial
| Código | Documento | Status | Conteúdo Principal |
|--------|-----------|--------|-------------------|
| - | `00_INDICE_MASTER_PROTOCOLOS.md` | Concluído | Índice geral do sistema de protocolos |
| PCC-01 | `01_PROTOCOLO_INTERSETORIAL_APS_NIRSM_AES.md` | Concluído | Fluxo da rede intersetorial (Educação, CRAS, Terceiro Setor) → APS → AES |
| PCC-02 | `02_PROTOCOLO_DEMANDA_ESPONTANEA_APS_NIRSM_AES.md` | Concluído | Fluxo de demanda espontânea na APS → AES |
| PCC-03 | `03_PROTOCOLO_CONTRARREFERENCIA_AES_APS.md` | Concluído | Fluxo de contrarreferência da AES para APS |
| PCC-04 | `04_PROTOCOLO_URGENCIA_EMERGENCIA_SM.md` | Concluído | Fluxo de urgência/emergência (SAMU, UPA, PS) |
| REG-01 | `05_PROTOCOLO_REGULACAO_NIRSM_R.md` | Concluído | Regulação do acesso, critérios de aceite/devolutiva |
| REG-02 | `06_PROTOCOLO_NAO_ACEITACAO_MATRICIAMENTO.md` | Concluído | Não aceitação de casos + matriciamento retroativo |

#### Fase 3: Elaboração dos POPs
| Código | Documento | Status | Conteúdo Principal |
|--------|-----------|--------|-------------------|
| POP-01 | `POP_01_ACOLHIMENTO_SM_APS.md` | Concluído | Procedimento de acolhimento em saúde mental |
| POP-02 | `POP_02_CLASSIFICACAO_RISCO_SM.md` | Concluído | Matriz de classificação de risco |
| POP-03 | `POP_03_GUIA_REFERENCIA_NIRSM.md` | Pendente | Preenchimento da guia de encaminhamento |
| POP-04 | `POP_04_MATRICIAMENTO.md` | Pendente | Realização de matriciamento |
| POP-05 | `POP_05_ELABORACAO_PTS.md` | Concluído | Elaboração do Projeto Terapêutico Singular |
| POP-06 | `POP_06_CONTRARREFERENCIA.md` | Pendente | Contrarreferência estruturada |
| POP-07 | `POP_07_MANEJO_CRISE_SM.md` | Concluído | Manejo de crise em saúde mental |

#### Fase 4: Elaboração de Escalas e Instrumentos
| Código | Documento | Status | Conteúdo Principal |
|--------|-----------|--------|-------------------|
| ESC-01 | `GUIA_REFERENCIA_NIRSM.md` | Pendente | Formulário completo da guia de referência |
| ESC-02 | `FICHA_CONTRARREFERENCIA.md` | Concluído | Ficha de contrarreferência estruturada |
| ESC-03 | `CHECKLIST_ENCAMINHAMENTO.md` | Pendente | Checklist de critérios para encaminhamento |
| ESC-04 | `FICHA_ARTICULACAO_INTERSETORIAL.md` | Pendente | Ficha para encaminhamentos da rede intersetorial |
| ESC-05 | `PLANO_SEGURANCA_POS_CRISE.md` | Pendente | Plano de segurança para pacientes pós-crise |

#### Fase 5: Elaboração de Relatórios Executivos
| Código | Documento | Status | Conteúdo Principal |
|--------|-----------|--------|-------------------|
| REX-01 | `REX_01_MODELO_COMPARTILHAMENTO_CUIDADO.md` | Concluído | Síntese executiva do modelo completo |
| REX-02 | `REX_02_INDICADORES_REDE.md` | Pendente | Painel de indicadores de monitoramento |

---

## 3. ESTRUTURA DE ARQUIVOS CRIADOS

```
Protocolos_Compartilhamento_Cuidado/
├── 00_INDICE_MASTER_PROTOCOLOS.md
├── 01_PROTOCOLO_INTERSETORIAL_APS_NIRSM_AES.md
├── 02_PROTOCOLO_DEMANDA_ESPONTANEA_APS_NIRSM_AES.md
├── 03_PROTOCOLO_CONTRARREFERENCIA_AES_APS.md
├── 04_PROTOCOLO_URGENCIA_EMERGENCIA_SM.md
├── 05_PROTOCOLO_REGULACAO_NIRSM_R.md
├── 06_PROTOCOLO_NAO_ACEITACAO_MATRICIAMENTO.md
├── POPs/
│   ├── POP_01_ACOLHIMENTO_SM_APS.md
│   ├── POP_02_CLASSIFICACAO_RISCO_SM.md
│   ├── POP_05_ELABORACAO_PTS.md
│   └── POP_07_MANEJO_CRISE_SM.md
├── Escalas_Instrumentos/
│   └── FICHA_CONTRARREFERENCIA.md
└── Relatorios_Executivos/
    └── REX_01_MODELO_COMPARTILHAMENTO_CUIDADO.md
```

---

## 4. CONTEÚDOS PRINCIPAIS POR DOCUMENTO

### 4.1 Protocolos de Fluxo (PCC)

**PCC-01 - Intersetorial → APS → NIRSM-R → AES:**
- Definições e âmbito de aplicação
- Fluxograma geral (Mermaid)
- Etapa 1: Identificação na rede intersetorial
- Etapa 2: Acolhimento na APS
- Etapa 3: Classificação de risco
- Etapa 4: Manejo inicial e encaminhamento
- Etapa 5: Atenção especializada
- Etapa 6: Contrarreferência
- Ficha de Articulação Intersetorial (Anexo)
- Indicadores de monitoramento

**PCC-02 - Demanda Espontânea → APS → NIRSM-R → AES:**
- Prevalência epidemiológica
- Fluxograma detalhado
- Acolhimento com escuta qualificada
- Classificação de risco (matriz completa)
- Avaliação clínica e multiprofissional
- Critérios de encaminhamento
- Manejo farmacológico e psicossocial
- Situações especiais (gestantes, idosos, adolescentes)

**PCC-03 - Contrarreferência AES → APS:**
- Critérios de estabilidade por diagnóstico
- Checklist de avaliação
- Preparação para contrarreferência
- Atualização do PTS
- Comunicação com APS
- Período de transição (90 dias)
- Monitoramento (30-60-90 dias)
- Critérios de re-encaminhamento

**PCC-04 - Urgência/Emergência:**
- Classificação de emergências e urgências
- Avaliação rápida de risco (5 min)
- Manejo inicial de crise
- Contenção verbal, química e mecânica
- Acionamento SAMU e apoio policial
- Destino (UPA, CAPS Porta Aberta, internação)
- Seguimento pós-crise
- Plano de segurança

### 4.2 Protocolos de Regulação (REG)

**REG-01 - Regulação NIRSM-R:**
- Estrutura e funcionamento do NIRSM-R
- Checklist de completude da guia
- Critérios clínicos específicos por condição
- Matriz de priorização (P1-P4)
- Processo de devolutiva
- Guia de Referência NIRSM-R (formulário completo)
- Indicadores de qualidade

**REG-02 - Não Aceitação e Matriciamento:**
- Categorias de devolutiva técnica
- Modelo de devolutiva com orientação
- Recebimento e decisão na APS
- Modalidades de matriciamento
- Roteiro de discussão de caso
- PTS pós-matriciamento
- Seguimento e reavaliação
- Temas formativos (calendário anual)

### 4.3 POPs

**POP-01 - Acolhimento:**
- Procedimento passo a passo (6 etapas)
- Prazos de atendimento
- Frases úteis e o que não fazer
- Registro em prontuário

**POP-02 - Classificação de Risco:**
- Matriz VERMELHO/LARANJA/AMARELO/VERDE/AZUL
- Fluxograma de decisão
- Avaliação de risco de suicídio
- Instrumentos de apoio (PHQ, GAD, AUDIT)

**POP-05 - Elaboração do PTS:**
- Componentes obrigatórios
- Procedimento de elaboração
- Modelo de PTS completo
- Critérios de revisão

**POP-07 - Manejo de Crise:**
- Tipos de crise
- Avaliação rápida
- Preparação do ambiente
- Técnicas de desescalada
- Contenção química (medicações)
- Contenção mecânica (último recurso)
- Registro obrigatório
- Pós-crise e debriefing

### 4.4 Instrumentos

**Ficha de Contrarreferência:**
- Formulário completo com 11 seções
- Identificação, diagnósticos, histórico
- Estado atual, medicações
- Orientações para APS
- Sinais de alerta e critérios de re-encaminhamento
- Instruções de preenchimento

### 4.5 Relatórios Executivos

**REX-01 - Modelo de Compartilhamento:**
- Sumário executivo
- Arquitetura da rede (diagrama)
- Síntese dos fluxos
- Classificação de risco
- Regulação NIRSM-R
- Matriciamento
- Contrarreferência
- Indicadores de monitoramento
- Governança
- Lista completa de documentos

---

## 5. REFERÊNCIAS TÉCNICAS UTILIZADAS

### 5.1 Referências Normativas e Bibliográficas
1. Brasil. Lei nº 10.216/2001 - Reforma Psiquiátrica
2. Brasil. Portaria GM/MS nº 3.088/2011 - RAPS
3. Brasil. Cadernos de Atenção Básica nº 34 - Saúde Mental
4. OMS/OPAS. MI-mhGAP 2.0
5. TelessaúdeRS-UFRGS. Protocolos de Encaminhamento para Psiquiatria
6. ABP. Emergências Psiquiátricas - Diretrizes
7. Brasil. Prevenção do Suicídio - Manual APS

### 5.2 Fontes Locais do Projeto (Verificadas em 21/01/2026)
| Arquivo | Descrição | Usado para Validação |
|---------|-----------|---------------------|
| `BASE_TECNICA_CLINICA.md` | Matriz de classificação de risco, critérios de refratariedade, PTS | Sim |
| `CONTEXTO_REDE_EXTREMA.md` | Estrutura RAPS, coordenadores, pontos de atenção | Sim |
| `linha_de_cuidado_saude_mental_extrema_draft.md` | Fluxos assistenciais, MACC, instrumentos | Sim |
| `insights.md` | Compilação de 239 insights do conhecimento base | Sim |
| `Protocolo_Fluxos_Atencao_Saude_Mental_Extrema_2026.md` | Protocolo formal com fluxogramas visuais | Sim |
| `01_fluxos_aps_aes.md` | Rascunho de fluxos APS-AES | Sim |
| `RASCUNHO_PROTOCOLO_FINAL.md` | Versão preliminar protocolo compartilhamento | Sim |
| `fluxo_linha_cuidado_saude_mental_extrema.md` | Diagrama Mermaid dos fluxos | Sim |
| `03_protocolo_estimulacao_precoce.md` | Protocolo de estimulação precoce | Referência TEA |

### 5.3 Instrumentos Citados nas Fontes (Para Inclusão Futura)
| Instrumento | Origem | Status nos Protocolos |
|-------------|--------|----------------------|
| CuidaSM | Fiocruz/e-Planifica | Incluído |
| MI-mhGAP | OMS | Incluído |
| PHQ-9 | Validado | Incluído |
| GAD-7 | Validado | Incluído |
| AUDIT | OMS | Incluído |
| Columbia Protocol | Validado | Incluído |
| Coelho-Savassi | Brasil | **A incluir** |
| Genograma/Ecomapa | Brasil | **A incluir** |
| M-CHAT-R/F | Validado | **A incluir (CLI-02)** |

---

## 6. DECISÕES DE PROJETO

### 6.1 Nomenclatura Adotada

| Tipo | Prefixo | Exemplo |
|------|---------|---------|
| Protocolo de Fluxo | PCC- | PCC-01 |
| Protocolo de Regulação | REG- | REG-01 |
| POP | POP- | POP-01 |
| Escala/Instrumento | ESC- | ESC-01 |
| Relatório Executivo | REX- | REX-01 |

### 6.2 Estrutura Padrão dos Protocolos

1. Cabeçalho institucional
2. Objetivo
3. Âmbito de aplicação
4. Definições
5. Fluxograma (Mermaid)
6. Descrição das etapas
7. Responsabilidades
8. Indicadores
9. Anexos
10. Referências

### 6.3 Classificação de Risco Adotada

| Cor | Gravidade | Tempo-Resposta |
|-----|-----------|----------------|
| VERMELHO | Emergência | Imediato |
| LARANJA | Urgência | 24-72h |
| AMARELO | Prioridade | Até 30 dias |
| VERDE | Rotina | Até 15 dias |
| AZUL | Eletivo | Programado |

---

## 7. PRÓXIMAS SESSÕES

### Documentos a Elaborar:
1. POPs faltantes (03, 04, 06)
2. Instrumentos/escalas faltantes
3. Protocolos clínicos específicos (TEA, Suicidalidade, Álcool e Drogas)
4. Relatório de indicadores

### Revisões Necessárias:
1. Atualizar índice master com novos documentos
2. Padronizar telefones de contato
3. Validar fluxogramas com a rede
4. Alinhar com protocolos existentes no projeto

---

## 8. REVISÃO TÉCNICA REALIZADA (21/01/2026)

### 8.1 Fontes de Referência Consultadas
- `BASE_TECNICA_CLINICA.md`
- `CONTEXTO_REDE_EXTREMA.md`
- `linha_de_cuidado_saude_mental_extrema_draft.md`

### 8.2 Não Conformidades Identificadas e Corrigidas

| Item | Correção Aplicada |
|------|-------------------|
| Critério de refratariedade (PCC-02) | Ajustado para "8-12 semanas com adesão confirmada; OU falha de 2 antidepressivos" |
| Prazo de busca ativa (PCC-04) | Corrigido de "24-48h" para "24-72h" |
| Descrição Centro Integrar (Índice) | Ampliado para "Inclusão, desenvolvimento e reabilitação psicossocial" |

### 8.3 Conformidades Validadas
- Matriz de classificação de risco: CONFORME
- Metodologia PTS (4 momentos): CONFORME
- Escalonamento MACC (níveis 1-5): CONFORME
- Critérios de regulação NIRSM-R: CONFORME
- Estrutura da rede (coordenadores): CONFORME

### 8.4 Documento de Revisão
Ver arquivo: `REVISAO_TECNICA_PROTOCOLOS.md`

---

## 9. SEGUNDA REVISÃO TÉCNICA (21/01/2026)

### 9.1 Fontes Adicionais Consultadas
Na segunda revisão, foram identificadas e consultadas fontes adicionais do projeto que não haviam sido verificadas na primeira revisão:
- `insights.md` - 239 insights compilados do conhecimento base
- `Protocolo_Fluxos_Atencao_Saude_Mental_Extrema_2026.md` - Protocolo formal existente
- `01_fluxos_aps_aes.md` e `RASCUNHO_PROTOCOLO_FINAL.md` - Versões preliminares

### 9.2 Novos Achados

| Item | Situação | Ação |
|------|----------|------|
| Escala Coelho-Savassi | Não incluída | Adicionar aos instrumentos |
| Genograma/Ecomapa | Não incluído | Adicionar ao PTS e escalonamento |
| Limitações CuidaSM | Não documentadas | Documentar (não usar em crianças/adolescentes e eventos agudos) |
| M-CHAT-R/F para TEA | Não incluído | Incluir no protocolo CLI-02 |

### 9.3 Taxa de Conformidade
- **27 itens verificados** contra todas as fontes do projeto
- **22 conformes** (81%)
- **3 corrigidos** na primeira revisão
- **2 pendentes** para inclusão em documentos futuros
- **Taxa final de conformidade: 93%**

### 9.4 Coerência com Protocolo Existente
O `Protocolo_Fluxos_Atencao_Saude_Mental_Extrema_2026.md` existente no projeto é **COERENTE** com os protocolos elaborados. Ambos utilizam:
- Mesma matriz de classificação de risco
- Mesmos princípios norteadores
- Mesma estrutura de fluxos
- Mesmos prazos de atendimento

---

## 10. PRÓXIMAS SESSÕES (ATUALIZADO)

### Documentos a Elaborar (Prioridade):
1. POPs faltantes (03, 04, 06)
2. Protocolo Clínico TEA (CLI-02) - incluir M-CHAT-R/F
3. Protocolo Clínico Suicidalidade (CLI-03)
4. Instrumentos: Coelho-Savassi, Genograma/Ecomapa

### Atualizações Necessárias:
1. Documentar limitações do CuidaSM nos instrumentos
2. Atualizar POP-05 (PTS) com genograma/ecomapa
3. Padronizar telefones de contato em todos os protocolos

### Atividades de Suporte:
1. Validação com gestores
2. Capacitação das equipes
3. Implantação piloto

---

**Documento de controle interno - Coordenação de Saúde Mental Extrema/MG**
**Última atualização: 21/01/2026 - Segunda Revisão Técnica**
