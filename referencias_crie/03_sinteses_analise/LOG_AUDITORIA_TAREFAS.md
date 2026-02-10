---
doc_id: CRIE-SIN-005
title: Log de Auditoria de Tarefas - Projeto CRIE
taxonomy: sinteses_analise
doc_type: log
source_file: sinteses_ia/LOG_AUDITORIA_TAREFAS.md
original_format: MD
language: pt-BR
publisher: Analise Tecnica IA
topics:
- auditoria
- tarefas
- progresso
- fases
related_documents: []
file_hash: 9ba32d02a1cfb0d1e04b62a1f351acd5
extraction_method: copy
extraction_date: '2026-02-09'
needs_human_review: false
year: 2026
---

# LOG DE AUDITORIA E CONTROLE DE TAREFAS
**Sistema de Rastreamento de Progressão**
**Sessão Iniciada em:** 2026-01-19

---

## FASE 1: INGESTÃO E MINERAÇÃO DE DADOS

### 1.1. Varredura Normativa (Legal Scan)

- [x] Mapeamento de arquivos no diretório
- [ ] Leitura: `manual_MROSC_MG_AGE.pdf`
  - [ ] Extração: Regras de Prestação de Contas Simplificada
  - [ ] Extração: Vedação de Pagamento de Servidor (Art. 45)
  - [ ] Extração: Limites de Apostilamento vs. Aditivo
- [ ] Leitura: `DECRETO Nº 47.132, DE 20 DE JANEIRO.txt`
  - [ ] Extração: Arts. 39 a 42 (Custos e Vedações)
  - [ ] Extração: Art. 54 (Rateio de Custos Indiretos)
  - [ ] Extração: Sistemas Obrigatórios (CAGEC/SIGCON)
- [ ] Leitura: `A aplicabilidade do MROSC nas parcerias da Saúde – Observatório da Sociedade Civil.pdf`
  - [ ] Extração: Posicionamento sobre CER e APAE
- [ ] Leitura: `DELIBERAÇÃO_CIB_SUS_MG_1403_2013.pdf`
  - [ ] Extração: Diretrizes de Habilitação em Saúde

### 1.2. Varredura da Entidade (Entity Scan)

- [ ] Leitura: `TR - CRIE.docx`
  - [ ] Check: Objeto descrito com precisão?
  - [ ] Check: Regime jurídico definido?
  - [ ] Check: Fundamentação de dispensa presente?
- [ ] Leitura: `PLANO DE TRABALHO CRIE.docx`
  - [ ] Extração: Metas quantitativas e qualitativas
  - [ ] Extração: Cronograma de execução
  - [ ] Extração: Plano de aplicação financeira
  - [ ] Extração: Composição de RH
- [ ] Leitura: `Plano_de_trabalho_Saude_para_manutencao_de_pagamento_e_educador_fisico_assinado.pdf`
  - [ ] Análise: Estrutura de custos de pessoal
- [ ] Leitura: `CUSTO FUNCIONARIO com educador fisico 2.pdf`
  - [ ] Extração: Modelo de cálculo de encargos

### 1.3. Análise de Benchmarks

- [ ] Leitura: `exemplo_apae_pouso_alegre.pdf`
  - [ ] Extração: Valor de referência
  - [ ] Extração: Metas de produção
  - [ ] Extração: Indicadores de qualidade
- [ ] Leitura: `exemplo_apae_2.pdf`
  - [ ] Extração: Estrutura de monitoramento

### 1.4. Extração de Modelos

- [ ] Leitura: `Anexo I - Manual MROSC - Modelo de Proposta e Plano de Trabalho.docx`
  - [ ] Copiar: Estrutura padrão de Plano de Trabalho
- [ ] Leitura: `Anexo IV - Manual MROSC - Modelo Técnico de Monitoramento e Avaliação.docx`
  - [ ] Copiar: Matriz de indicadores

---

## FASE 2: ESTRUTURAÇÃO DO BANCO DE DADOS TÉCNICO

- [ ] População da Seção 1 (Fundamentação Jurídica) no BANCO_CONHECIMENTO_TECNICO.md
- [ ] População da Seção 2 (Matriz de Custos) no BANCO_CONHECIMENTO_TECNICO.md
- [ ] População da Seção 3 (Diretrizes Clínicas) no BANCO_CONHECIMENTO_TECNICO.md
- [ ] População da Seção 4 (Capacidade Operacional) no BANCO_CONHECIMENTO_TECNICO.md
- [ ] População da Seção 5 (Benchmarks) no BANCO_CONHECIMENTO_TECNICO.md
- [ ] Atualização do CONTEXTO_ESTRATEGICO_EXTREMA.md com dados confirmados

---

## FASE 3: PLANEJAMENTO E REDAÇÃO

### 3.1. Termo de Referência (TR)

- [ ] Criação de arquivo: `RASCUNHO_INSTRUMENTOS_JURIDICOS.md`
- [ ] Redação: Seção 1 - Dados da Administração Pública
- [ ] Redação: Seção 2 - Objeto (descrição precisa)
- [ ] Redação: Seção 3 - Justificativa Técnica
- [ ] Redação: Seção 4 - Fundamentação Legal (Dispensa/Inexigibilidade)
- [ ] Redação: Seção 5 - Especificação dos Serviços
- [ ] Redação: Seção 6 - Requisitos de Qualificação (CAGEC, CNES, Certidões)
- [ ] Redação: Seção 7 - Valor Estimado e Dotação
- [ ] Redação: Seção 8 - Vigência
- [ ] Redação: Seção 9 - Critérios de Monitoramento
- [ ] Redação: Seção 10 - Obrigações das Partes

### 3.2. Plano de Trabalho (PT)

- [ ] Redação: Identificação da OSC
- [ ] Redação: Descrição da Realidade (diagnóstico)
- [ ] Redação: Objetivos (Geral e Específicos)
- [ ] Redação: Metas SMART
- [ ] Redação: Metodologia de Execução
- [ ] Redação: Cronograma Físico-Financeiro
- [ ] Redação: Plano de Aplicação Detalhado
  - [ ] Rubrica: Recursos Humanos
  - [ ] Rubrica: Material de Consumo
  - [ ] Rubrica: Serviços de Terceiros
  - [ ] Rubrica: Custos Indiretos (com memória de rateio)
- [ ] Redação: Indicadores de Monitoramento
- [ ] Redação: Meios de Verificação

---

## FASE 4: REVISÃO E VALIDAÇÃO

### 4.1. Testes de Consistência

- [ ] Teste de Estadualidade (Decreto MG vs. Norma Federal)
- [ ] Teste de Integridade Financeira (Ausência de taxas vedadas)
- [ ] Teste de Nexo Causal (Despesa x Meta)
- [ ] Teste de Contexto (Valores reais vs. Placeholders)

### 4.2. Checklist de Conformidade Legal

- [ ] Todas as cláusulas possuem base legal citada?
- [ ] Orçamento possui memória de cálculo?
- [ ] Metas são mensuráveis e verificáveis?
- [ ] Há exigência de regularidade no CAGEC?
- [ ] Há previsão de conta bancária específica?

---

## REGISTRO DE DECISÕES TÉCNICAS

### Decisão 1: [Aguardando primeira decisão]
**Data:** [DATA]
**Contexto:** [CONTEXTO]
**Opções Avaliadas:** [OPÇÕES]
**Decisão Tomada:** [DECISÃO]
**Justificativa:** [JUSTIFICATIVA]

---

## BLOQUEIOS E IMPEDIMENTOS

### Bloqueio 1: [Nenhum no momento]

---

**ÚLTIMA ATUALIZAÇÃO:** 2026-01-19 15:05
**PRÓXIMA REVISÃO:** Após conclusão da Fase 1.1
