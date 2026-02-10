---
doc_id: CRIE-SIN-007
title: Planejamento Executivo - Diretoria de Contratos e Licitacoes SMS Extrema
taxonomy: sinteses_analise
doc_type: planejamento
source_file: sinteses_ia/planejamento-executivo-diretoria_contrato_compras_licitacoes-extrema.md
original_format: MD
language: pt-BR
publisher: Analise Tecnica IA
topics:
- planejamento
- licitacoes
- contratos
- L14133
- governanca
- KPIs
related_documents: []
file_hash: ba4f758cb3779c317ae069690752671e
extraction_method: copy
extraction_date: '2026-02-09'
needs_human_review: false
year: 2026
---

# PLANEJAMENTO EXECUTIVO: DIRETORIA DE LICITAÇÕES, COMPRAS E CONTRATOS
## Secretaria Municipal de Saúde de Extrema/MG

**Versão:** 1.0  
**Data:** 29 de dezembro de 2025  
**Elaboração:** Claude Opus 4.5 (Anthropic) em colaboração com Caio Villani  
**Classificação:** Documento Técnico-Operacional  
**Metodologia:** Ciclos de self-consistency, self-feedback, self-iteration com Chain of Thoughts

---

## SÍNTESE EXECUTIVA

Este planejamento executivo estabelece a arquitetura organizacional, operacional e de governança para a Diretoria de Licitações, Compras e Contratos da Secretaria Municipal de Saúde de Extrema/MG, em conformidade integral com a Lei 14.133/2021 (Nova Lei de Licitações e Contratos Administrativos) e regulamentação correlata.

**Contexto Territorial:** Extrema/MG possui aproximadamente 59.000 habitantes (dezembro/2025), com PIB per capita elevado decorrente do polo industrial, o que gera demandas de saúde específicas e orçamento relativamente robusto para porte municipal. A Secretaria de Saúde opera dispositivos assistenciais que incluem CAPS I, Centro de Saúde Mental, Centro Integrar, 11 Unidades Básicas de Saúde e articulação com a RAPS regional (85.000 habitantes).

**Objetivo Central:** Estruturar sistema de contratações públicas que assegure: (i) conformidade legal integral; (ii) eficiência operacional mensurável; (iii) economicidade nas aquisições; (iv) transparência e controle social; (v) desenvolvimento sustentável de competências na equipe; (vi) integração com planejamento estratégico da saúde municipal.

**Resultado Esperado:** Diretoria operando em maturidade intermediária em 12 meses, com processos padronizados, equipe capacitada, indicadores monitorados e governança funcional, atingindo maturidade avançada em 24 meses com integração plena ao ciclo de planejamento e execução orçamentária.

---

## PARTE I: ESTRUTURA ORGANIZACIONAL

### 1. Arquitetura Funcional da Diretoria

A estrutura proposta segue o modelo de **segregação de funções** exigido pelo art. 7º, §1º da Lei 14.133/2021, organizando as atribuições em três núcleos funcionais distintos que correspondem às fases do metaprocesso de contratações:

```
SECRETARIA MUNICIPAL DE SAÚDE
│
├── DIRETORIA DE LICITAÇÕES, COMPRAS E CONTRATOS
│   │
│   ├── NÚCLEO DE PLANEJAMENTO DE CONTRATAÇÕES
│   │   ├── Elaboração de DFD (Documento de Formalização de Demanda)
│   │   ├── Consolidação do PCA (Plano de Contratações Anual)
│   │   ├── Elaboração de ETP (Estudo Técnico Preliminar)
│   │   ├── Pesquisa de Preços
│   │   ├── Elaboração de TR/PB (Termo de Referência/Projeto Básico)
│   │   └── Análise de Riscos
│   │
│   ├── NÚCLEO DE SELEÇÃO DE FORNECEDORES
│   │   ├── Agente de Contratação / Pregoeiro
│   │   ├── Equipe de Apoio
│   │   ├── Comissão de Contratação (quando aplicável)
│   │   ├── Condução de Pregões e Concorrências
│   │   ├── Dispensas e Inexigibilidades
│   │   └── Sistema de Registro de Preços
│   │
│   └── NÚCLEO DE GESTÃO CONTRATUAL
│       ├── Gestor de Contratos
│       ├── Fiscal Técnico
│       ├── Fiscal Administrativo
│       ├── Acompanhamento de Execução
│       ├── Alterações Contratuais
│       └── Aplicação de Sanções
│
└── ASSESSORIA JURÍDICA (Vinculada à Procuradoria Municipal)
    └── Parecer Jurídico em Minutas e Processos
```

### 2. Dimensionamento de Pessoal Mínimo

Para município de porte de Extrema/MG com volume estimado de 200-400 processos licitatórios/ano na área de saúde:

| Função | Quantidade Mínima | Requisitos Essenciais |
|--------|------------------|----------------------|
| Diretor Técnico/Coordenador Executivo | 1 | Servidor efetivo ou comissionado; formação superior; certificação ENAP recomendada |
| Agente de Contratação/Pregoeiro | 2 | Servidor efetivo; capacitação específica Lei 14.133/2021; certificação ENAP |
| Elaborador de ETP/TR | 2 | Conhecimento técnico do objeto; capacitação em planejamento de contratações |
| Gestor de Contratos | 2 | Servidor efetivo; capacitação em gestão contratual |
| Fiscal Técnico | 3-5 | Conhecimento técnico específico por tipo de contrato |
| Fiscal Administrativo | 2 | Conhecimento em regularidade fiscal/trabalhista |
| Equipe de Apoio | 2-3 | Capacitação básica em licitações |
| **TOTAL** | **14-17** | — |

**Nota Crítica:** A realidade municipal frequentemente impõe acumulação de funções. Neste caso, deve-se documentar formalmente as acumulações permitidas, observando vedações legais (ex: elaborador de ETP não pode ser agente de contratação do mesmo processo sem justificativa excepcional).

### 3. Vedações de Designação (art. 9º Lei 14.133/2021)

Não podem participar de licitação ou execução contratual, direta ou indiretamente:

- Autor do anteprojeto, projeto básico ou executivo (pessoa física ou jurídica)
- Empresa responsável pela elaboração do projeto (ou da qual o autor seja dirigente, gerente, controlador, acionista, sócio ou responsável técnico)
- Pessoa física ou jurídica que tenha consultoria ou apoio à fiscalização ou supervisão da execução
- Servidor ou empregado público com poder decisório ou componente de comissão que tenha parentesco até 3º grau ou afinidade/vínculo com licitante ou contratado
- Agente público que tenha participado da elaboração de orçamento até 3 anos antes

---

## PARTE II: ATRIBUIÇÕES DO DIRETOR TÉCNICO E COORDENADOR EXECUTIVO

### 4. Papel Estratégico na Governança

O Diretor Técnico e Coordenador Executivo atua como **autoridade competente delegada** pelo Secretário Municipal de Saúde para matérias de licitações e contratos, exercendo funções de:

**4.1 Governança e Liderança**
- Institucionalizar estrutura de governança das contratações conforme art. 11 da Lei 14.133/2021
- Implementar processos e estruturas de gestão de riscos e controles internos
- Promover gestão por competências com desenvolvimento contínuo da equipe
- Designar formalmente agentes públicos para funções essenciais (agente de contratação, pregoeiro, gestores, fiscais)
- Aprovar normas internas e procedimentos operacionais padronizados
- Representar a Diretoria em comitês e colegiados municipais

**4.2 Planejamento Estratégico**
- Coordenar elaboração do Plano de Contratações Anual (PCA) da Secretaria de Saúde
- Aprovar o PCA consolidado e encaminhar para homologação do Secretário
- Articular alinhamento entre PCA, PPA, LDO e LOA
- Definir estratégias de contratação (registro de preços, compras compartilhadas, centralização)
- Monitorar execução do PCA e propor ajustes

**4.3 Supervisão Operacional**
- Autorizar abertura de processos licitatórios até limite delegado
- Homologar licitações até limite delegado (acima: Secretário)
- Autorizar dispensas de licitação conforme art. 75 (incisos I e II)
- Ratificar inexigibilidades após parecer jurídico
- Autorizar adesões a atas de registro de preços
- Aprovar alterações contratuais dentro de limites legais
- Aplicar sanções administrativas (advertência, multa) conforme previsão contratual

**4.4 Controle e Transparência**
- Assegurar publicações obrigatórias no PNCP (Portal Nacional de Contratações Públicas)
- Garantir atualização de informações no Portal da Transparência municipal
- Responder demandas de órgãos de controle (TCE-MG, CGM, MP)
- Implementar programa de integridade nas contratações
- Coordenar auditorias internas periódicas

### 5. Limites de Delegação Sugeridos

| Ato | Limite Sugerido (Diretor) | Acima do Limite (Secretário) |
|-----|--------------------------|------------------------------|
| Autorização de licitação | Até R$ 500.000,00 | Acima de R$ 500.000,00 |
| Homologação de licitação | Até R$ 500.000,00 | Acima de R$ 500.000,00 |
| Dispensa de licitação (art. 75, I e II) | Conforme valores legais | — |
| Alteração contratual | Até 10% do valor inicial | Acima de 10% |
| Aplicação de sanções | Advertência e multa | Suspensão e declaração de inidoneidade |
| Rescisão contratual | Consensual | Unilateral |

**Observação:** Limites devem ser formalizados em Portaria do Secretário Municipal de Saúde, registrada em Diário Oficial.

---

## PARTE III: FLUXOS DE TRABALHO OPERACIONAIS

### 6. Metaprocesso de Contratações Adaptado

O fluxo integra as três fases legais com particularidades da saúde pública municipal:

#### FASE I: PLANEJAMENTO (Núcleo de Planejamento)

```
[1] IDENTIFICAÇÃO DA NECESSIDADE
    │
    ├── Origem: Demanda programada (PCA) ou demanda emergente
    ├── Documento: DFD (Documento de Formalização de Demanda)
    ├── Conteúdo: Justificativa, quantidade, prazo, área requisitante
    └── Responsável: Área técnica demandante (ex: CAPS, UBS, Vigilância)
    │
    ▼
[2] ESTUDO TÉCNICO PRELIMINAR (ETP)
    │
    ├── Obrigatoriedade: Regra geral (dispensável em casos específicos)
    ├── Conteúdo mínimo (art. 18, §1º):
    │   ├── Descrição da necessidade
    │   ├── Área requisitante e responsável
    │   ├── Requisitos da contratação
    │   ├── Levantamento de mercado
    │   ├── Descrição de soluções (mínimo 3)
    │   ├── Estimativa de quantidades
    │   ├── Estimativa de valor
    │   ├── Justificativa da escolha do tipo de solução
    │   ├── Justificativa de parcelamento ou não
    │   ├── Contratações correlatas/interdependentes
    │   ├── Demonstrativo de resultados pretendidos
    │   ├── Providências para continuidade
    │   └── Análise de riscos (Matriz de Riscos)
    ├── Responsável: Elaborador de ETP (área técnica + Núcleo de Planejamento)
    └── Prazo sugerido: 10-30 dias úteis (conforme complexidade)
    │
    ▼
[3] PESQUISA DE PREÇOS
    │
    ├── Parâmetros obrigatórios (art. 23, §1º):
    │   ├── Painel de Preços (preços praticados pela Administração)
    │   ├── Preços de bancos de preços públicos
    │   ├── Preços em mídias/sítios especializados
    │   └── Pesquisa com fornecedores (mínimo 3 cotações)
    ├── Validade: 6 meses (atualizar se necessário)
    ├── Responsável: Núcleo de Planejamento
    └── Prazo sugerido: 5-10 dias úteis
    │
    ▼
[4] TERMO DE REFERÊNCIA / PROJETO BÁSICO
    │
    ├── TR: Serviços e compras
    ├── PB: Obras e serviços de engenharia
    ├── Conteúdo mínimo (art. 6º, XXIII):
    │   ├── Definição do objeto (claro, preciso, suficiente)
    │   ├── Fundamentação da necessidade
    │   ├── Descrição da solução como um todo
    │   ├── Requisitos da contratação
    │   ├── Modelo de execução/gestão
    │   ├── Critérios de medição e pagamento
    │   ├── Forma de seleção do fornecedor
    │   ├── Critérios de julgamento
    │   ├── Estimativa de preço
    │   └── Adequação orçamentária
    ├── Responsável: Elaborador de TR (área técnica + Núcleo)
    └── Prazo sugerido: 10-20 dias úteis
    │
    ▼
[5] ANÁLISE DE RISCOS E MATRIZ
    │
    ├── Identificação de riscos por fase
    ├── Probabilidade x Impacto
    ├── Medidas de mitigação
    ├── Alocação de responsabilidades (Administração x Contratado)
    └── Prazo sugerido: Integrado ao ETP
    │
    ▼
[6] ELABORAÇÃO DO EDITAL E ANEXOS
    │
    ├── Minuta de edital conforme modelo aprovado
    ├── Anexos: TR/PB, Minuta de contrato, Declarações
    ├── Responsável: Núcleo de Planejamento
    └── Prazo sugerido: 5-10 dias úteis
    │
    ▼
[7] PARECER JURÍDICO
    │
    ├── Análise de legalidade da minuta
    ├── Verificação de requisitos formais
    ├── Responsável: Assessoria Jurídica / Procuradoria
    └── Prazo legal: Conforme regulamento interno (sugestão: 5-10 dias)
    │
    ▼
[8] AUTORIZAÇÃO DE ABERTURA
    │
    ├── Despacho autorizativo
    ├── Responsável: Diretor Técnico ou Secretário (conforme limite)
    └── Publicação: PNCP + Diário Oficial
```

#### FASE II: SELEÇÃO DO FORNECEDOR (Núcleo de Seleção)

```
[9] PUBLICAÇÃO E DIVULGAÇÃO
    │
    ├── PNCP (obrigatório)
    ├── Diário Oficial do Município
    ├── Sítio eletrônico oficial
    └── Prazos mínimos de publicidade conforme modalidade
    │
    ▼
[10] RECEBIMENTO DE PROPOSTAS
    │
    ├── Plataforma eletrônica (ComprasNet, BLL, Licitanet, etc.)
    ├── Verificação de requisitos de participação
    └── Sigilo até abertura
    │
    ▼
[11] FASE DE JULGAMENTO
    │
    ├── Abertura de propostas
    ├── Verificação de conformidade com edital
    ├── Classificação/Desclassificação
    ├── Negociação (quando aplicável)
    ├── Declaração de vencedor provisório
    └── Responsável: Agente de Contratação/Pregoeiro
    │
    ▼
[12] FASE DE HABILITAÇÃO (Modelo Invertido - Regra)
    │
    ├── Habilitação apenas do vencedor (economia processual)
    ├── Documentos (art. 62-70):
    │   ├── Jurídica
    │   ├── Técnica
    │   ├── Fiscal, social e trabalhista
    │   └── Econômico-financeira
    ├── Verificação de regularidade
    └── Responsável: Agente de Contratação/Pregoeiro
    │
    ▼
[13] RECURSOS ADMINISTRATIVOS
    │
    ├── Intenção de recurso: Imediata na sessão
    ├── Prazo para razões: 3 dias úteis
    ├── Contrarrazões: 3 dias úteis
    ├── Decisão: Agente/Autoridade competente
    └── Prazo decisão: 10 dias úteis
    │
    ▼
[14] ADJUDICAÇÃO E HOMOLOGAÇÃO
    │
    ├── Adjudicação: Agente de Contratação
    ├── Homologação: Diretor Técnico ou Secretário
    └── Publicação: PNCP + Diário Oficial
```

#### FASE III: GESTÃO CONTRATUAL (Núcleo de Gestão)

```
[15] FORMALIZAÇÃO DO CONTRATO
    │
    ├── Convocação do adjudicatário
    ├── Assinatura do contrato (prazo: 5 dias úteis, prorrogável)
    ├── Publicação de extrato
    ├── Designação de Gestor e Fiscais
    └── Responsável: Núcleo de Gestão
    │
    ▼
[16] REUNIÃO INAUGURAL
    │
    ├── Participantes: Gestor, Fiscais, Contratado
    ├── Conteúdo: Apresentação de obrigações, cronograma, canais de comunicação
    └── Registro: Ata de reunião
    │
    ▼
[17] EXECUÇÃO E FISCALIZAÇÃO
    │
    ├── Acompanhamento técnico (Fiscal Técnico)
    ├── Verificação administrativa (Fiscal Administrativo)
    ├── Medições e atestações
    ├── Notificações de irregularidades
    ├── Registro em livro/sistema de ocorrências
    └── Responsável: Equipe de Fiscalização
    │
    ▼
[18] PAGAMENTOS
    │
    ├── Emissão de nota fiscal pelo contratado
    ├── Atestação pelo Fiscal Técnico
    ├── Verificação de regularidade pelo Fiscal Administrativo
    ├── Autorização de pagamento pelo Gestor
    ├── Liquidação e pagamento pelo setor financeiro
    └── Prazo: Conforme contrato (máximo 30 dias)
    │
    ▼
[19] ALTERAÇÕES CONTRATUAIS
    │
    ├── Unilaterais (art. 124, I): Por interesse público
    ├── Consensuais (art. 124, II): Por acordo das partes
    ├── Limites: +25% ou -25% (obras: +50% para acréscimos)
    ├── Formalização: Termo aditivo
    └── Responsável: Gestor + Diretor/Secretário
    │
    ▼
[20] APLICAÇÃO DE SANÇÕES (quando necessário)
    │
    ├── Tipos (art. 156): Advertência, multa, impedimento, declaração de inidoneidade
    ├── Processo administrativo com contraditório
    ├── Gradação conforme gravidade
    └── Responsável: Diretor (advertência/multa) ou Secretário (demais)
    │
    ▼
[21] RECEBIMENTO E ENCERRAMENTO
    │
    ├── Recebimento provisório: Fiscal Técnico (até 15 dias)
    ├── Recebimento definitivo: Gestor (até 90 dias)
    ├── Verificação de quitação de obrigações
    ├── Liberação de garantias
    └── Arquivamento do processo
```

### 7. Prazos Referenciais por Tipo de Contratação

| Tipo de Contratação | Planejamento | Seleção | Gestão | Total Estimado |
|---------------------|-------------|---------|--------|----------------|
| Pregão Eletrônico (bens/serviços comuns) | 20-30 dias | 15-25 dias | Vigência contratual | 35-55 dias até contrato |
| Concorrência | 30-45 dias | 30-45 dias | Vigência contratual | 60-90 dias até contrato |
| Dispensa de Licitação | 10-15 dias | 5-10 dias | Vigência contratual | 15-25 dias até contrato |
| Inexigibilidade | 10-15 dias | 5-10 dias | Vigência contratual | 15-25 dias até contrato |
| Registro de Preços | 30-45 dias | 20-30 dias | 12 meses + execuções | 50-75 dias até ata |

---

## PARTE IV: MATRIZ DE COMPETÊNCIAS CUSTOMIZADA

### 8. Competências Técnicas por Função

#### 8.1 Diretor Técnico e Coordenador Executivo

| Competência Técnica | Nível Requerido | Descrição |
|---------------------|-----------------|-----------|
| Governança de contratações | Alto | Domínio completo de mecanismos de governança, controle interno e gestão de riscos |
| Legislação de licitações | Alto | Conhecimento aprofundado da Lei 14.133/2021 e regulamentação |
| Planejamento estratégico | Alto | Capacidade de articular PCA com instrumentos de planejamento municipal |
| Gestão de pessoas | Alto | Liderança de equipes, delegação, desenvolvimento de competências |
| Análise de riscos | Médio-Alto | Identificação, avaliação e tratamento de riscos em contratações |
| Gestão contratual | Médio | Conhecimento dos principais aspectos de execução contratual |
| Sistemas de informação | Médio | Operação de sistemas (PNCP, ComprasNet, sistemas municipais) |

#### 8.2 Agente de Contratação / Pregoeiro

| Competência Técnica | Nível Requerido | Descrição |
|---------------------|-----------------|-----------|
| Condução de licitações | Alto | Domínio completo de todas as fases do procedimento licitatório |
| Legislação de licitações | Alto | Conhecimento aprofundado de Lei 14.133/2021 |
| Julgamento de propostas | Alto | Capacidade de análise de conformidade e classificação |
| Habilitação de licitantes | Alto | Verificação de documentação conforme requisitos legais |
| Negociação | Médio-Alto | Técnicas de negociação para obtenção de melhores condições |
| Sistemas eletrônicos | Alto | Operação fluente de plataformas de licitação |
| Análise de recursos | Médio | Capacidade de analisar e responder recursos administrativos |

#### 8.3 Elaborador de ETP / TR

| Competência Técnica | Nível Requerido | Descrição |
|---------------------|-----------------|-----------|
| Análise de demanda | Alto | Identificar e justificar necessidades de contratação |
| Pesquisa de mercado | Alto | Levantamento de soluções disponíveis e fornecedores |
| Elaboração de especificações | Alto | Redação clara e precisa de requisitos técnicos |
| Pesquisa de preços | Alto | Metodologia de estimativa conforme parâmetros legais |
| Análise de viabilidade | Médio-Alto | Comparação de alternativas e justificativa de escolha |
| Análise de riscos | Médio | Identificação de riscos na fase de planejamento |
| Legislação aplicável | Médio | Conhecimento de dispositivos relevantes ao planejamento |

#### 8.4 Gestor de Contratos

| Competência Técnica | Nível Requerido | Descrição |
|---------------------|-----------------|-----------|
| Gestão contratual | Alto | Coordenação completa do ciclo de vida do contrato |
| Fiscalização | Alto | Supervisão de equipe de fiscalização |
| Alterações contratuais | Alto | Domínio de hipóteses e limites de alteração |
| Aplicação de sanções | Médio-Alto | Conhecimento de procedimento sancionatório |
| Recebimento de objeto | Alto | Procedimentos de recebimento provisório e definitivo |
| Legislação contratual | Médio-Alto | Conhecimento de dispositivos de execução contratual |
| Sistemas de gestão | Médio | Operação de sistemas de acompanhamento |

#### 8.5 Fiscal Técnico

| Competência Técnica | Nível Requerido | Descrição |
|---------------------|-----------------|-----------|
| Conhecimento do objeto | Alto | Domínio técnico específico do objeto fiscalizado |
| Fiscalização técnica | Alto | Verificação de conformidade técnica |
| Medições | Alto | Aferição de quantidades e qualidade |
| Registro de ocorrências | Médio-Alto | Documentação adequada de eventos relevantes |
| Comunicação | Médio | Elaboração de notificações e relatórios |
| Legislação básica | Médio | Conhecimento de dispositivos essenciais |

#### 8.6 Fiscal Administrativo

| Competência Técnica | Nível Requerido | Descrição |
|---------------------|-----------------|-----------|
| Regularidade fiscal | Alto | Verificação de CNDs e certidões |
| Regularidade trabalhista | Alto | Verificação de CNDT e obrigações trabalhistas |
| Regularidade previdenciária | Alto | Verificação de CRF/FGTS e obrigações previdenciárias |
| Controle documental | Alto | Organização e arquivo de documentação |
| Legislação trabalhista/fiscal | Médio | Conhecimento de obrigações aplicáveis |
| Sistemas de consulta | Médio | Operação de sistemas de verificação |

### 9. Competências Comportamentais por Função

| Competência Comportamental | Diretor | Agente/Pregoeiro | Elaborador ETP/TR | Gestor | Fiscal Técnico | Fiscal Admin. |
|---------------------------|---------|------------------|-------------------|--------|----------------|---------------|
| Visão sistêmica | Alto | Médio | Médio | Médio | Baixo | Baixo |
| Liderança | Alto | Médio | Baixo | Médio | Baixo | Baixo |
| Tomada de decisão | Alto | Alto | Médio | Alto | Médio | Médio |
| Comunicação | Alto | Alto | Alto | Alto | Alto | Médio |
| Ética e integridade | Alto | Alto | Alto | Alto | Alto | Alto |
| Trabalho em equipe | Alto | Alto | Alto | Alto | Médio | Médio |
| Gestão de conflitos | Alto | Alto | Baixo | Alto | Médio | Baixo |
| Orientação para resultados | Alto | Alto | Alto | Alto | Alto | Alto |
| Capacidade analítica | Alto | Alto | Alto | Alto | Alto | Alto |
| Resiliência sob pressão | Alto | Alto | Médio | Alto | Médio | Médio |

---

## PARTE V: PLANO DE CAPACITAÇÃO

### 10. Trilhas de Aprendizagem Recomendadas (ENAP)

A ENAP oferece a **Trilha "Contratações Públicas"** com mais de 100 soluções de aprendizagem gratuitas, organizadas por competências e fases do metaprocesso.

#### 10.1 Formação Básica Obrigatória (Todos os Agentes)

| Curso | Carga Horária | Prioridade | Público |
|-------|--------------|------------|---------|
| Nova Lei de Licitações e Contratos - Visão Geral | 20h | Imediata | Todos |
| Planejamento da Contratação Pública | 20h | Imediata | Todos |
| Gestão e Fiscalização de Contratos | 20h | Imediata | Gestores/Fiscais |
| Ética e Integridade nas Contratações | 10h | Imediata | Todos |
| Sistema de Registro de Preços | 15h | 90 dias | Agentes/Elaboradores |

#### 10.2 Formação Específica por Função

**Diretor Técnico:**
- Governança das Contratações Públicas (20h)
- Gestão de Riscos em Contratações (15h)
- Liderança e Gestão de Equipes (20h)
- Planejamento Estratégico no Setor Público (20h)

**Agente de Contratação / Pregoeiro:**
- Pregão na Nova Lei de Licitações (20h)
- Concorrência na Nova Lei de Licitações (15h)
- Dispensa e Inexigibilidade (15h)
- Recursos Administrativos (10h)

**Elaborador de ETP / TR:**
- Estudo Técnico Preliminar (ETP) - Passo a Passo (15h)
- Elaboração de Termo de Referência (20h)
- Pesquisa de Preços em Contratações (15h)
- Análise de Riscos em Contratações (15h)

**Gestor de Contratos:**
- Gestão de Contratos na Prática (20h)
- Alterações Contratuais (15h)
- Aplicação de Sanções Administrativas (10h)
- Encerramento de Contratos (10h)

**Fiscais:**
- Fiscalização de Contratos Administrativos (20h)
- Fiscalização de Obras e Serviços de Engenharia (20h) - quando aplicável
- Fiscalização de Contratos de TI (15h) - quando aplicável

#### 10.3 Certificação Profissional ENAP

A ENAP oferece **Certificação Profissional Básica em Licitações e Contratos** (2024), gratuita e online, recomendada para todos os agentes após conclusão da formação básica.

### 11. Cronograma de Capacitação (12 meses)

| Período | Atividade | Público-Alvo |
|---------|-----------|--------------|
| Mês 1-2 | Formação básica obrigatória | Todos os agentes |
| Mês 3-4 | Formação específica inicial | Por função |
| Mês 5-6 | Workshops práticos internos | Equipes integradas |
| Mês 7-8 | Formação específica avançada | Por função |
| Mês 9-10 | Certificação ENAP | Agentes-chave |
| Mês 11-12 | Atualização e reciclagem | Todos os agentes |

---

## PARTE VI: INDICADORES DE DESEMPENHO

### 12. Painel de Indicadores (KPIs)

#### 12.1 Indicadores de Eficiência

| Indicador | Fórmula | Meta | Periodicidade |
|-----------|---------|------|---------------|
| Tempo médio de planejamento | Σ (Data TR aprovado - Data DFD) / Nº processos | ≤ 30 dias | Mensal |
| Tempo médio de seleção | Σ (Data homologação - Data publicação) / Nº processos | ≤ 45 dias | Mensal |
| Tempo médio total | Σ (Data contrato - Data DFD) / Nº processos | ≤ 60 dias | Mensal |
| Taxa de licitações desertas | (Nº desertas / Total de licitações) × 100 | ≤ 5% | Trimestral |
| Taxa de licitações fracassadas | (Nº fracassadas / Total de licitações) × 100 | ≤ 5% | Trimestral |

#### 12.2 Indicadores de Economicidade

| Indicador | Fórmula | Meta | Periodicidade |
|-----------|---------|------|---------------|
| Economia média obtida | (Valor estimado - Valor contratado) / Valor estimado × 100 | ≥ 10% | Mensal |
| Índice de variação de preços | (Preço contratado / Preço de referência) × 100 | ≤ 100% | Mensal |
| Economia com registro de preços | (Valor s/ RP - Valor c/ RP) / Valor s/ RP × 100 | ≥ 5% | Semestral |

#### 12.3 Indicadores de Conformidade

| Indicador | Fórmula | Meta | Periodicidade |
|-----------|---------|------|---------------|
| Taxa de processos com ETP | (Nº processos c/ ETP / Total) × 100 | 100% | Mensal |
| Taxa de publicações no PNCP | (Nº publicações realizadas / Nº obrigatórias) × 100 | 100% | Mensal |
| Taxa de pareceres jurídicos favoráveis | (Nº favoráveis / Total de pareceres) × 100 | ≥ 95% | Trimestral |
| Taxa de recursos providos | (Nº recursos providos / Total de recursos) × 100 | ≤ 10% | Trimestral |

#### 12.4 Indicadores de Gestão Contratual

| Indicador | Fórmula | Meta | Periodicidade |
|-----------|---------|------|---------------|
| Taxa de contratos com gestor designado | (Nº contratos c/ gestor / Total) × 100 | 100% | Mensal |
| Taxa de contratos com fiscal designado | (Nº contratos c/ fiscal / Total) × 100 | 100% | Mensal |
| Taxa de aditivos | (Nº aditivos / Nº contratos vigentes) × 100 | ≤ 20% | Trimestral |
| Taxa de sanções aplicadas | (Nº sanções / Nº contratos vigentes) × 100 | Monitorar | Trimestral |
| Índice de execução contratual | (Valor executado / Valor contratado) × 100 | ≥ 90% | Mensal |

#### 12.5 Indicadores de Capacitação

| Indicador | Fórmula | Meta | Periodicidade |
|-----------|---------|------|---------------|
| Taxa de agentes capacitados | (Nº agentes c/ formação básica / Total) × 100 | 100% | Semestral |
| Carga horária média de capacitação | Σ horas de capacitação / Nº agentes | ≥ 40h/ano | Anual |
| Taxa de certificação ENAP | (Nº certificados / Nº elegíveis) × 100 | ≥ 50% | Anual |

---

## PARTE VII: PROTOCOLOS DE GOVERNANÇA

### 13. Mecanismos de Controle Interno

#### 13.1 Modelo de Três Linhas de Defesa

**Primeira Linha: Gestão Operacional**
- Controles executados pelos próprios agentes durante as atividades
- Checklists de verificação em cada fase do processo
- Revisão hierárquica imediata (Coordenador → Diretor)
- Registro de ocorrências e não-conformidades

**Segunda Linha: Supervisão e Monitoramento**
- Revisão periódica de processos por amostragem
- Monitoramento de indicadores de desempenho
- Análise de riscos sistemática
- Atualização de procedimentos operacionais

**Terceira Linha: Auditoria Interna**
- Auditorias programadas (mínimo semestral)
- Auditorias especiais por demanda
- Relatórios para Secretário e Controle Interno municipal
- Acompanhamento de recomendações

#### 13.2 Checklists de Verificação por Fase

**Checklist de Planejamento:**
- [ ] DFD com justificativa adequada
- [ ] ETP completo conforme art. 18
- [ ] Pesquisa de preços com 3+ fontes
- [ ] TR/PB com elementos obrigatórios
- [ ] Matriz de riscos elaborada
- [ ] Dotação orçamentária identificada
- [ ] Minuta de edital revisada

**Checklist de Seleção:**
- [ ] Publicações realizadas (PNCP, DO)
- [ ] Prazos de publicidade cumpridos
- [ ] Propostas analisadas conforme critérios
- [ ] Habilitação verificada completamente
- [ ] Recursos analisados tempestivamente
- [ ] Adjudicação e homologação formalizadas

**Checklist de Gestão Contratual:**
- [ ] Contrato assinado e publicado
- [ ] Gestor e fiscais designados
- [ ] Reunião inaugural realizada
- [ ] Fiscalização em dia
- [ ] Pagamentos regulares
- [ ] Aditivos formalizados quando necessário
- [ ] Recebimento provisório/definitivo documentado

### 14. Programa de Integridade

#### 14.1 Código de Conduta Específico

Elaborar código de conduta complementar ao Estatuto dos Servidores, abordando:
- Conflitos de interesse em contratações
- Recebimento de presentes e hospitalidades
- Sigilo de informações de processos
- Relacionamento com fornecedores
- Canais de denúncia e proteção ao denunciante

#### 14.2 Gestão de Conflitos de Interesse

- Declaração anual de inexistência de impedimentos
- Comunicação obrigatória de situações de conflito
- Afastamento imediato de processos em caso de conflito
- Registro em sistema de controle

#### 14.3 Canal de Denúncias

- Ouvidoria municipal como canal principal
- Garantia de anonimato
- Procedimento de apuração definido
- Proteção ao denunciante de boa-fé

---

## PARTE VIII: INTEGRAÇÃO COM SISTEMAS

### 15. Sistemas Obrigatórios

| Sistema | Finalidade | Obrigatoriedade |
|---------|-----------|-----------------|
| PNCP (Portal Nacional de Contratações Públicas) | Publicação de editais, contratos, atas | Obrigatório (Lei 14.133/2021) |
| ComprasNet / BLL / Licitanet | Condução de licitações eletrônicas | Obrigatório para pregão eletrônico |
| SICONV / Transferegov | Convênios e transferências voluntárias | Quando aplicável |
| e-SUS APS | Integração com demandas de saúde | Interno à Secretaria |
| Sistema de Protocolo Municipal | Tramitação de processos | Conforme regulamento municipal |

### 16. Sistemas Recomendados

| Sistema | Finalidade | Benefício |
|---------|-----------|-----------|
| Sistema de Gestão de Contratações | Controle integrado de processos | Eficiência e rastreabilidade |
| Sistema de Gestão de Contratos | Acompanhamento de execução | Controle de vigências e pagamentos |
| Sistema de Pesquisa de Preços | Consulta a bancos de preços | Celeridade na pesquisa |
| Sistema de Gestão de Riscos | Matriz e monitoramento | Governança e controle |

### 17. Integração com Planejamento de Saúde

A Diretoria de Licitações deve articular-se com os instrumentos de planejamento da saúde municipal:

- **PMS (Plano Municipal de Saúde):** Alinhamento das contratações com objetivos estratégicos
- **PAS (Programação Anual de Saúde):** Cronograma de contratações conforme metas anuais
- **RAG (Relatório Anual de Gestão):** Prestação de contas das contratações realizadas
- **PDSM (Plano de Desenvolvimento da Saúde Mental):** Integração com projeto RAPS 4.0

---

## PARTE IX: CRONOGRAMA DE IMPLEMENTAÇÃO

### 18. Fases de Implantação (24 meses)

#### FASE 1: ESTRUTURAÇÃO (Meses 1-3)

| Atividade | Responsável | Prazo | Entregável |
|-----------|-------------|-------|------------|
| Formalização da estrutura organizacional | Diretor + Secretário | Mês 1 | Portaria de estrutura |
| Designação de agentes públicos | Diretor | Mês 1 | Portarias de designação |
| Elaboração de normas internas | Diretor | Mês 2 | Manual de procedimentos (v1) |
| Configuração de sistemas | Equipe TI | Mês 2-3 | Sistemas operacionais |
| Capacitação básica | Todos | Mês 1-3 | Certificados ENAP |
| Diagnóstico de processos existentes | Equipe | Mês 1-2 | Relatório diagnóstico |

#### FASE 2: OPERACIONALIZAÇÃO (Meses 4-6)

| Atividade | Responsável | Prazo | Entregável |
|-----------|-------------|-------|------------|
| Elaboração do PCA 2026 | Núcleo Planejamento | Mês 4 | PCA aprovado |
| Padronização de modelos de documentos | Equipe | Mês 4-5 | Biblioteca de modelos |
| Implementação de checklists | Equipe | Mês 5 | Checklists validados |
| Início de monitoramento de indicadores | Diretor | Mês 6 | Painel de indicadores |
| Capacitação específica | Por função | Mês 4-6 | Certificados ENAP |

#### FASE 3: CONSOLIDAÇÃO (Meses 7-12)

| Atividade | Responsável | Prazo | Entregável |
|-----------|-------------|-------|------------|
| Primeira auditoria interna | Controle Interno | Mês 8 | Relatório de auditoria |
| Revisão de procedimentos | Diretor | Mês 9 | Manual (v2) |
| Programa de integridade | Diretor | Mês 10 | Código de conduta |
| Avaliação de desempenho | Diretor | Mês 12 | Relatório anual |
| Certificação ENAP agentes-chave | Agentes | Mês 9-12 | Certificados |

#### FASE 4: MATURIDADE (Meses 13-24)

| Atividade | Responsável | Prazo | Entregável |
|-----------|-------------|-------|------------|
| Implementação de melhorias | Equipe | Contínuo | Processos otimizados |
| Segunda auditoria interna | Controle Interno | Mês 18 | Relatório de auditoria |
| Integração plena com planejamento de saúde | Diretor | Mês 18 | Fluxos integrados |
| Avaliação de maturidade | Diretor + Controle | Mês 24 | Diagnóstico de maturidade |
| Planejamento do ciclo seguinte | Equipe | Mês 24 | PCA 2027 + Plano de ação |

---

## PARTE X: MECANISMOS DE CONTROLE E TRANSPARÊNCIA

### 19. Transparência Ativa

**Publicações Obrigatórias no PNCP:**
- Editais e anexos
- Atas de registro de preços
- Contratos e aditivos
- Resultados de licitações
- Sanções aplicadas

**Publicações no Portal da Transparência Municipal:**
- Relatório mensal de contratações
- Contratos vigentes com valores e prazos
- Pagamentos realizados
- Indicadores de desempenho

**Publicações no Diário Oficial:**
- Extratos de editais, contratos, aditivos
- Portarias de designação
- Sanções aplicadas

### 20. Transparência Passiva

- Atendimento a pedidos de informação via LAI (Lei de Acesso à Informação)
- Prazo de resposta: 20 dias, prorrogáveis por mais 10
- Ouvidoria como canal principal
- Registro e acompanhamento de demandas

### 21. Controle Social

- Disponibilização de informações em linguagem acessível
- Audiências públicas para contratações de grande vulto
- Participação de conselhos de saúde no monitoramento
- Canal para denúncias de irregularidades

### 22. Controle Externo

**Tribunal de Contas do Estado de Minas Gerais (TCE-MG):**
- Prestação de contas anual
- Atendimento a diligências e auditorias
- Cumprimento de decisões e recomendações

**Ministério Público:**
- Atendimento a requisições
- Cooperação em investigações

**Controladoria-Geral do Município:**
- Auditorias programadas
- Acompanhamento de recomendações
- Suporte técnico

---

## PARTE XI: CONSIDERAÇÕES FINAIS E LIMITAÇÕES

### 23. Premissas do Planejamento

Este planejamento executivo foi elaborado considerando:

1. **Contexto municipal:** Extrema/MG com aproximadamente 59.000 habitantes e estrutura administrativa de médio porte
2. **Recursos humanos:** Disponibilidade de equipe mínima de 14-17 servidores para funções essenciais
3. **Infraestrutura tecnológica:** Acesso a sistemas obrigatórios (PNCP, plataformas de licitação)
4. **Capacidade orçamentária:** Recursos para capacitação e sistemas de gestão
5. **Apoio institucional:** Compromisso da alta administração (Secretário de Saúde, Prefeito)

### 24. Limitações e Ressalvas

**24.1 Limitações do Documento:**
- Este planejamento é um modelo de referência, devendo ser adaptado às particularidades locais
- Valores de limites de delegação são sugestivos e dependem de regulamentação municipal
- Cronograma pode variar conforme capacidade operacional real
- Dimensionamento de pessoal é referencial e deve ser validado localmente

**24.2 Áreas que Requerem Expertise Adicional:**
- Regulamentação municipal específica (Decreto de licitações)
- Integração com sistemas já existentes no município
- Negociação sindical para designações de funções
- Aspectos orçamentários e financeiros específicos

**24.3 Atualizações Necessárias:**
- Acompanhar regulamentação complementar da Lei 14.133/2021
- Monitorar jurisprudência do TCE-MG
- Atualizar conforme orientações do PNCP
- Revisar anualmente (mínimo) ou quando houver mudanças normativas relevantes

### 25. Declaração de Uso de IA

Este documento foi elaborado com assistência de Inteligência Artificial (Claude Opus 4.5, Anthropic), aplicando metodologia de ciclos iterativos de validação (self-consistency, self-feedback, self-iteration, self-review, self-correction). O conteúdo foi fundamentado em:

- Lei 14.133/2021 (Nova Lei de Licitações e Contratos Administrativos)
- Decreto 11.246/2022 (Regulamentação de agentes de contratação)
- Portaria SEGES/ME 8.678/2021 (Governança das contratações)
- Manual de Boas Práticas em Contratações Públicas (MGI, janeiro/2025)
- Trilhas de Aprendizagem ENAP em Contratações Públicas

**A validação final e adaptação ao contexto local são de responsabilidade do gestor humano.**

---

## REFERÊNCIAS NORMATIVAS

1. **Lei 14.133/2021** — Lei de Licitações e Contratos Administrativos
2. **Decreto 11.246/2022** — Regulamenta arts. 7º, 8º e 9º da Lei 14.133/2021
3. **Decreto 11.462/2023** — Regulamenta sistema de registro de preços
4. **Portaria SEGES/ME 8.678/2021** — Governança das contratações
5. **Instrução Normativa SEGES/ME 65/2021** — Dispensa eletrônica
6. **Instrução Normativa SEGES/ME 73/2022** — Pesquisa de preços
7. **Manual de Boas Práticas em Contratações Públicas** — MGI, janeiro/2025
8. **Trilhas de Aprendizagem em Contratações Públicas** — ENAP, 2023

---

**Documento Finalizado**

*Extrema/MG, 29 de dezembro de 2025*

---

## ANEXO I: MODELOS DE DOCUMENTOS (REFERÊNCIA)

### A1. Modelo de Portaria de Designação de Agente de Contratação

```
PORTARIA SMS Nº XXX/2025

O SECRETÁRIO MUNICIPAL DE SAÚDE DE EXTREMA, Estado de Minas Gerais, no uso de 
suas atribuições legais, e considerando:

- O disposto nos arts. 7º e 8º da Lei Federal nº 14.133/2021;
- O disposto no Decreto Federal nº 11.246/2022;
- A necessidade de designação de agentes públicos para funções essenciais de 
  licitações e contratos;

RESOLVE:

Art. 1º DESIGNAR o(a) servidor(a) [NOME COMPLETO], matrícula nº [XXXXX], 
ocupante do cargo de [CARGO], para exercer a função de AGENTE DE CONTRATAÇÃO 
da Secretaria Municipal de Saúde de Extrema/MG.

Art. 2º O Agente de Contratação designado terá as seguintes atribuições, 
conforme art. 8º da Lei 14.133/2021:
I - tomar decisões em prol da boa condução da licitação;
II - acompanhar o trâmite da licitação;
III - dar impulso ao procedimento licitatório;
IV - executar quaisquer outras atividades necessárias ao bom andamento do certame.

Art. 3º O servidor designado declara, para os fins do art. 9º da Lei 14.133/2021, 
que não se encontra em nenhuma das situações de impedimento previstas em lei.

Art. 4º Esta Portaria entra em vigor na data de sua publicação.

Extrema/MG, [DATA].

_____________________________________
[NOME]
Secretário Municipal de Saúde
```

### A2. Modelo de DFD (Documento de Formalização de Demanda)

```
DOCUMENTO DE FORMALIZAÇÃO DE DEMANDA (DFD)
Lei 14.133/2021, art. 18, I

1. IDENTIFICAÇÃO
Órgão/Setor Requisitante: _______________________
Responsável pela Demanda: _______________________
Data: ___/___/_____

2. DESCRIÇÃO DA NECESSIDADE
[Descrever de forma clara e objetiva a necessidade que motiva a contratação, 
indicando o problema a ser resolvido ou a oportunidade a ser aproveitada]

3. ÁREA REQUISITANTE
[Identificar a unidade que utilizará o objeto da contratação]

4. QUANTIDADE ESTIMADA
[Indicar quantitativo preliminar estimado]

5. PREVISÃO DE DATA PARA INÍCIO
[Indicar quando a contratação deve estar concluída]

6. INDICAÇÃO DE SERVIDOR PARA ELABORAR ETP/TR
Nome: _______________________
Cargo/Função: _______________________

7. ALINHAMENTO COM PLANEJAMENTO
( ) Consta no PCA 2025/2026
( ) Demanda emergente (justificar): _______________________

8. DECLARAÇÃO
Declaro que a necessidade descrita é real, atual e adequada ao interesse público.

_______________________
Assinatura do Requisitante

APROVAÇÃO PELA DIRETORIA DE LICITAÇÕES
( ) Aprovado para elaboração de ETP
( ) Devolvido para complementação: _______________________

_______________________
Diretor Técnico
Data: ___/___/_____
```

### A3. Estrutura de ETP (Estudo Técnico Preliminar)

```
ESTUDO TÉCNICO PRELIMINAR (ETP)
Lei 14.133/2021, art. 18, §1º

PROCESSO ADMINISTRATIVO Nº: _______________
DFD DE ORIGEM: _______________

SUMÁRIO
1. Descrição da necessidade
2. Área requisitante e responsável
3. Requisitos da contratação
4. Levantamento de mercado
5. Descrição da solução como um todo
6. Estimativa das quantidades
7. Estimativa do valor
8. Justificativa da escolha do tipo de solução
9. Justificativa de parcelamento ou não
10. Contratações correlatas e/ou interdependentes
11. Demonstrativo de resultados pretendidos
12. Providências para continuidade
13. Análise de riscos

[Desenvolver cada seção conforme art. 18, §1º da Lei 14.133/2021]
```

---

## ANEXO II: GLOSSÁRIO DE TERMOS TÉCNICOS

| Termo | Definição |
|-------|-----------|
| **Agente de Contratação** | Servidor designado para conduzir processo licitatório (art. 8º, Lei 14.133/2021) |
| **DFD** | Documento de Formalização de Demanda — inicia o processo de contratação |
| **ETP** | Estudo Técnico Preliminar — análise completa da contratação |
| **Gestor de Contrato** | Responsável pela coordenação das atividades de gestão e fiscalização |
| **Fiscal Técnico** | Responsável pelo acompanhamento técnico da execução contratual |
| **Fiscal Administrativo** | Responsável pela verificação de regularidade fiscal/trabalhista |
| **PCA** | Plano de Contratações Anual — instrumento de planejamento |
| **PNCP** | Portal Nacional de Contratações Públicas — sistema de publicidade |
| **Pregoeiro** | Agente de contratação designado especificamente para pregões |
| **SRP** | Sistema de Registro de Preços — conjunto de procedimentos para contratações frequentes |
| **TR** | Termo de Referência — documento que define o objeto para serviços e compras |
| **PB** | Projeto Básico — documento que define o objeto para obras e serviços de engenharia |

---

*Fim do Documento*
