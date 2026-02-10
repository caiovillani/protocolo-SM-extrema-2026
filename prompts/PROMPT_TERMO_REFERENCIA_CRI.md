# PROMPT — ELABORAÇÃO DO TERMO DE REFERÊNCIA PARA TERMO DE COLABORAÇÃO (CRI/INEX)

> **Finalidade:** Prompt estruturado para que o Claude elabore, passo a passo e com rigor técnico-jurídico, o Termo de Referência completo do Termo de Colaboração entre a Secretaria Municipal de Saúde de Extrema/MG e a instituição parceira (CRI), por inexigibilidade de chamamento público.
>
> **Modo de uso:** Copiar integralmente este prompt em uma sessão Claude. Cada etapa gera uma seção do documento. O usuário deve validar a saída de cada etapa antes de prosseguir para a seguinte.

---

## CONTEXTO COMPLETO PARA O CLAUDE

Você é um redator técnico-jurídico especializado em direito administrativo municipal e parcerias com organizações da sociedade civil. Sua tarefa é elaborar o **Termo de Referência** para a celebração de um Termo de Colaboração por inexigibilidade de chamamento público, em conformidade com a legislação brasileira.

### Situação

A Secretaria Municipal de Saúde de Extrema/MG, por meio da Coordenação de Saúde Mental e Reabilitação, formalizará um Termo de Colaboração com uma organização da sociedade civil (OSC) para prestação de serviços de reabilitação e cuidado integral a pessoas com deficiência intelectual (DI) e Transtorno do Espectro Autista (TEA). A parceria será celebrada por dispensa de chamamento público (inexigibilidade), nos termos do Art. 31 da Lei Federal nº 13.019/2014.

### Dados Concretos

| Dado | Valor |
|------|-------|
| **Município** | Extrema/MG |
| **Órgão** | Secretaria Municipal de Saúde — Coordenação de Saúde Mental e Reabilitação |
| **Modalidade** | Termo de Colaboração (Art. 2º, VII, Lei 13.019/2014) — interesse é da administração pública |
| **Dispensa** | Inexigibilidade de chamamento público (Art. 31, Lei 13.019/2014) |
| **Instituição** | [NOME DA OSC — a inserir] |
| **CNPJ** | [A PREENCHER] |
| **Valor mensal** | R$ 38.860,41 (trinta e oito mil, oitocentos e sessenta reais e quarenta e um centavos) |
| **Vigência** | 12 meses, prorrogável conforme Art. 55, Lei 13.019/2014 |
| **Público-alvo** | Crianças (0-18 anos) e adultos com DI e/ou TEA, referenciados pela rede municipal |
| **Fontes de custeio** | (i) Recursos próprios municipais (Fonte 1), dotação SMS, observado Art. 7º, LC 141/2012; (ii) Cofinanciamento estadual, condicionado à habilitação como SERDI/SES-MG |

### Marco Regulatório Aplicável

| Norma | Dispositivo relevante |
|-------|----------------------|
| Lei Federal nº 13.019/2014 | Marco Regulatório das OSC — Arts. 2º, 5º, 22, 24, 31, 33-42, 55, 63-72 |
| Decreto Federal nº 8.726/2016 | Regulamenta a Lei 13.019 |
| Lei Federal nº 10.216/2001 | Proteção e direitos das pessoas com transtornos mentais |
| Lei Federal nº 13.146/2015 | Estatuto da Pessoa com Deficiência (LBI) |
| Lei Federal nº 13.709/2018 | LGPD — proteção de dados pessoais |
| LC nº 141/2012 | Regulamenta EC 29 — financiamento SUS |
| Legislação municipal | [Verificar se há regulamentação local da Lei 13.019 — inserir se houver] |
| Portarias MS | Linha de Cuidado TEA (2025), RAPS (Portaria 3.088/2011) |
| Programa SERDI/SES-MG | Habilitação estadual para serviço de reabilitação intelectual |

### Equipe Prevista no Plano de Trabalho

| Profissional | Carga horária | Vínculo | Centro de custo |
|-------------|--------------|---------|----------------|
| Fisioterapeuta | [CH] h/sem | Contratado pela OSC | Saúde |
| Psicólogo(a) | [CH] h/sem | Contratado pela OSC | Saúde |
| Fonoaudiólogo(a) | [CH] h/sem | Contratado pela OSC | Saúde |
| Terapeuta Ocupacional | [CH] h/sem | Contratado pela OSC | Saúde |
| Educador(a) Físico(a) | 20 h/sem | Contratado pela OSC | Saúde |
| Coordenador(a) Técnico(a) | 20 h/sem | Contratado pela OSC (PJ) | Saúde |
| Médico (clínico ou pediatra) | 8 h/sem | Cedido pelo município (apostilamento posterior) | Saúde |

> **REGRA CRÍTICA:** Nenhum profissional pode ter carga horária sobreposta entre centro de custo Saúde e Assistência Social. Se o profissional atuar nos dois, os horários devem ser distintos e documentados em instrumentos separados.

### Composição Financeira

| Rubrica | Valor mensal estimado |
|---------|----------------------|
| Recursos Humanos (equipe multidisciplinar + encargos) | ~R$ 28.000 |
| Coordenação técnica (20h) | ~R$ 3.000 |
| Material de consumo | ~R$ 500 |
| Transporte (van + motorista) | ~R$ 5.000 (a confirmar) |
| Reserva administrativa/impostos | Diferença para R$ 38.860,41 |
| **TOTAL** | **R$ 38.860,41** |

### Metas e Indicadores Acordados

**Quantitativas:**
- Satisfação de usuários e familiares: ≥70%
- Vagas preenchidas conforme termo: 100%
- Atendidos com PTI: 100%

**Qualitativas:**
- Pesquisa de satisfação: aplicada semestralmente
- Educação permanente: 1 capacitação/mês
- CNES atualizado: verificação trimestral

**Indicadores de desempenho:**
- Pontualidade da prestação de contas
- Frequência dos usuários (via sistema Vector)
- Faturamento BPA (procedimentos faturados vs. realizados) — ≥80%

---

## PIPELINE DE EXECUÇÃO — 8 ETAPAS

### Instruções gerais para o Claude:

1. **Execute uma etapa por vez.** Após gerar cada seção, apresente ao usuário para validação antes de prosseguir.
2. **Linguagem:** Técnico-jurídica acessível. Evitar jargão desnecessário, mas usar terminologia legal precisa.
3. **Campos sensíveis:** Usar `[A PREENCHER]` para dados que dependem de informação não disponível (CNPJ, nomes completos, endereços, dotações orçamentárias específicas).
4. **Referências normativas:** Sempre citar artigo, lei e ano. Ex.: "nos termos do Art. 31 da Lei Federal nº 13.019/2014".
5. **Não inventar:** Não gerar números de CNPJ, CPF, processos ou dotações fictícios.
6. **Formato:** Markdown com tabelas. Seções numeradas sequencialmente.

---

### ETAPA 1 — JUSTIFICATIVA TÉCNICA DA INEXIGIBILIDADE

**Objetivo:** Redigir a justificativa técnica que fundamenta a dispensa de chamamento público.

**Conteúdo obrigatório:**
- Fundamentação legal: Art. 31, Lei 13.019/2014
- Demonstração de singularidade da OSC (única no município com cuidado integral)
- Diferenciação entre cuidado integral vs. atendimento fragmentado (clínicas privadas)
- Histórico de parceria anterior com o município
- Ampliação de escopo: novos serviços (aquáticos, adulto DI, educação permanente)
- Dois escopos contratualizados distintos (Saúde e Assistência Social — separados)
- Alinhamento com Linha de Cuidado TEA/MS 2025 e Lei 13.146/2015 (LBI)

**Validação humana:** O coordenador deve confirmar que os argumentos de singularidade estão corretos e acrescentar dados específicos da instituição (anos de atuação, certificações, número de profissionais).

---

### ETAPA 2 — OBJETO E ESCOPO DO TERMO

**Objetivo:** Definir com precisão o objeto da parceria.

**Conteúdo obrigatório:**
- Definição do objeto (cuidado integral DI/TEA)
- Público-alvo com critérios de elegibilidade (faixa etária, CID, referenciamento pela rede)
- Serviços incluídos (lista exaustiva por modalidade)
- Modelo de atendimento (integral, não fragmentado, com PTI)
- Capacidade operacional: mínimo 150, máximo 200 atendimentos/mês
- Dois escopos distintos (Saúde / Assistência Social) com clareza sobre centros de custo
- Exclusões: o que NÃO faz parte do objeto (decisões clínicas individuais são de responsabilidade profissional, não da parceria)

**Validação humana:** Confirmar critérios de elegibilidade e capacidade operacional real.

---

### ETAPA 3 — OBRIGAÇÕES DO MUNICÍPIO

**Objetivo:** Listar o que o município fornece/garante na parceria.

**Conteúdo obrigatório:**
- Repasse financeiro mensal (R$ 38.860,41) com fonte orçamentária
- Cessão de profissional médico (8h/sem) — posterior, via apostilamento
- Acesso ao sistema Vector para faturamento BPA, com cláusula LGPD
- Referenciamento de pacientes pela rede (APS, CAPS, intersetorial)
- Articulação para habilitação SERDI junto à SES/MG
- Monitoramento e avaliação via comissão MIROSC
- Não interferência na gestão operacional da OSC (autonomia, Art. 5º da Lei 13.019)

---

### ETAPA 4 — OBRIGAÇÕES DA INSTITUIÇÃO (OSC)

**Objetivo:** Listar as obrigações da OSC.

**Conteúdo obrigatório:**
- Manter equipe conforme plano de trabalho (com substituição em caso de vacância)
- Elaborar PTI para 100% dos atendidos
- Garantir separação de centros de custo (Saúde ≠ Assistência Social)
- Designar coordenador técnico (20h) responsável pela gestão e prestação de contas
- Manter CNES atualizado
- Aplicar pesquisa de satisfação semestral
- Realizar 1 ação de educação permanente/mês
- Apresentar prestação de contas conforme MIROSC (periodicidade e modelo a definir)
- Faturar procedimentos via BPA quando habilitado
- Garantir transporte dos pacientes (se acordado) — van + motorista
- Cumprir LGPD no manejo de dados do Vector e prontuários
- Não utilizar profissionais com carga horária sobreposta entre secretarias
- Manter escrituração contábil específica para os recursos recebidos (Art. 51, Lei 13.019)

---

### ETAPA 5 — PLANO DE TRABALHO

**Objetivo:** Estruturar o modelo de plano de trabalho conforme Art. 22, Lei 13.019/2014.

**Conteúdo obrigatório (Art. 22):**

a) Diagnóstico da realidade (situação DI/TEA em Extrema, demanda reprimida, fila de espera)
b) Descrição de metas quantitativas e qualitativas (conforme acordado na reunião)
c) Forma de execução das ações (metodologia de atendimento, fluxo de referenciamento)
d) Definição dos indicadores, documentos e critérios de avaliação (tabela completa)
e) Previsão de receitas e despesas (planilha de custos detalhada por rubrica)
f) Cronograma de execução (12 meses, com marcos trimestrais)

**Incluir tabela de indicadores com:** nome, fórmula, fonte de dados, periodicidade, meta.

---

### ETAPA 6 — COMPOSIÇÃO DE CUSTOS

**Objetivo:** Detalhar a planilha de custos com memória de cálculo.

**Conteúdo obrigatório:**
- Tabela de RH: profissional, carga horária, valor unitário, encargos, valor total
- Rubrica de material de consumo (discriminar tipos)
- Rubrica de coordenação técnica
- Rubrica de transporte (se aplicável)
- Total mensal = R$ 38.860,41
- Total anual (12 meses)
- Memória de cálculo: de onde vem cada valor (piso municipal, referência de mercado)
- **REGRA:** A OSC não pode ter "gordura" — parceria é pau a pau (Lei 13.019 proíbe lucro, mas permite despesas administrativas razoáveis)

**Validação humana:** Conferir se valores individuais correspondem à planilha real da instituição.

---

### ETAPA 7 — MONITORAMENTO E AVALIAÇÃO

**Objetivo:** Estruturar o sistema de monitoramento conforme MIROSC.

**Conteúdo obrigatório:**
- Comissão de Monitoramento e Avaliação (CMA) — composição, atribuições, periodicidade
- Relatório de execução do objeto (formato, periodicidade — sugestão: trimestral)
- Prestação de contas (anual, com possibilidade de diligências)
- Instrumentos de acompanhamento: relatórios, listas de presença, prontuários (anonimizados), pesquisas de satisfação, faturamento BPA
- Mecanismos de controle: visitas in loco, cruzamento de dados Vector, verificação CNES
- Glosas e sanções: hipóteses de glosa, notificação, prazo de regularização
- Referência ao checklist MIROSC 600-AP (18 itens)

---

### ETAPA 8 — VIGÊNCIA, RESCISÃO E DISPOSIÇÕES FINAIS

**Objetivo:** Redigir as cláusulas finais do Termo de Referência.

**Conteúdo obrigatório:**
- Vigência: 12 meses a partir da assinatura, prorrogável (Art. 55)
- Hipóteses de rescisão: unilateral (com notificação de 30 dias), bilateral, por descumprimento
- Apostilamento: cláusula permitindo inclusão posterior de médico cedido e ajustes no plano
- Foro: comarca de Extrema/MG
- Cláusula LGPD: responsabilidades específicas sobre dados de saúde
- Cláusula anticorrupção
- Publicação: extrato no Diário Oficial do Município
- Disposição transitória: prestação de contas do contrato anterior deve ser quitada antes da assinatura do novo termo (ou condição suspensiva)
- Assinaturas: Secretário(a) Municipal de Saúde + Representante Legal da OSC + Testemunhas

---

## CHECKLIST DE CONFORMIDADE FINAL

Após gerar todas as 8 etapas, verificar:

- [ ] Todas as referências legais estão com artigo, lei e ano corretos
- [ ] Nenhum CNPJ/CPF/processo fictício foi gerado
- [ ] Campos `[A PREENCHER]` estão em todos os dados sensíveis
- [ ] Valor mensal = R$ 38.860,41 em todas as menções
- [ ] Separação de centros de custo Saúde/Social está explícita
- [ ] LGPD mencionada em pelo menos 3 pontos (Vector, prontuários, pesquisa)
- [ ] Linguagem é pessoa-primeiro ("pessoa com TEA", não "autista")
- [ ] Metas correspondem ao acordado na reunião de 29/01/2026
- [ ] Monitoramento segue MIROSC / Lei 13.019
- [ ] Não há decisões clínicas atribuídas ao instrumento (apenas ao profissional)

---

## PONTOS DE VALIDAÇÃO HUMANA OBRIGATÓRIA

| Ponto | Etapa | O que validar |
|-------|-------|--------------|
| V1 | Etapa 1 | Argumentos de singularidade — dados reais da instituição |
| V2 | Etapa 2 | Critérios de elegibilidade — confirmar CIDs e faixa etária |
| V3 | Etapa 5 | Diagnóstico da realidade — dados epidemiológicos locais |
| V4 | Etapa 6 | Composição de custos — conferir com planilha real |
| V5 | Etapa 8 | Condição sobre prestação de contas anterior — verificar status |

> **ATENÇÃO:** Este prompt gera um Termo de Referência — documento técnico que instruirá o processo de celebração do Termo de Colaboração. O Termo de Colaboração em si (instrumento jurídico) será elaborado pelo setor jurídico do município a partir deste Termo de Referência. Não confundir os dois documentos.

---

**Prompt elaborado em:** Fevereiro de 2026
**Base:** Reunião de 29/01/2026 — Ofício nº [___]/2025-SMS (provocação INEX)
**Coordenação de Saúde Mental e Reabilitação — SMS Extrema/MG**
