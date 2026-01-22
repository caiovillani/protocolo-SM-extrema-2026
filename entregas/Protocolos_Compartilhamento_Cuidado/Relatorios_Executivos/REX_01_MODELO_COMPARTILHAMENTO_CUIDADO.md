# RELATÓRIO EXECUTIVO
## Modelo de Compartilhamento do Cuidado em Saúde Mental
### Município de Extrema/MG - 2026

**Secretaria Municipal de Saúde**
**Coordenação de Saúde Mental**
**Versão:** 1.0 | **Data:** Janeiro/2026

---

## SUMÁRIO EXECUTIVO

Este documento apresenta o modelo de compartilhamento do cuidado em saúde mental implementado no município de Extrema/MG, descrevendo a estrutura, os fluxos, os protocolos e os instrumentos que organizam a navegação dos usuários nas Redes de Atenção à Saúde (RAS) e Redes Intersetoriais.

O modelo fundamenta-se em quatro pilares:
1. **APS como coordenadora do cuidado**
2. **Regulação qualificada do acesso (NIRSM-R)**
3. **Matriciamento como ferramenta de integração**
4. **Contrarreferência estruturada para continuidade**

---

## 1. VISÃO GERAL DO MODELO

### 1.1 Arquitetura da Rede

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    MODELO DE COMPARTILHAMENTO DO CUIDADO               │
│                         SAÚDE MENTAL - EXTREMA/MG                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐                                    ┌─────────────────┐│
│  │   REDE      │                                    │    ATENÇÃO      ││
│  │INTERSETORIAL│──────────────┐                     │  ESPECIALIZADA  ││
│  │ Educação    │              │                     │  ┌───────────┐  ││
│  │ Assist.Soc. │              │                     │  │  CAPS I   │  ││
│  │ 3º Setor    │              │      ┌─────────┐    │  ├───────────┤  ││
│  └─────────────┘              ▼      │         │    │  │   CSM     │  ││
│                          ┌────────┐  │ NIRSM-R │    │  ├───────────┤  ││
│  ┌─────────────┐         │  APS   │◄─┤Regulação├───►│  │ Centro    │  ││
│  │  DEMANDA    │────────►│ e-ESF  │  │         │    │  │ Integrar  │  ││
│  │ ESPONTÂNEA  │         │e-Multi │  └─────────┘    │  └───────────┘  ││
│  └─────────────┘         └────┬───┘       ▲         └─────────────────┘│
│                               │           │                             │
│                               │     ┌─────┴──────┐                      │
│  ┌─────────────┐              │     │MATRICIAMENTO│                     │
│  │    RUE      │◄─────────────┘     │ Capacitação │                     │
│  │ SAMU/UPA/PS │                    └────────────┘                      │
│  └─────────────┘                                                        │
│                                                                         │
│         ────────►  Fluxo principal                                      │
│         ◄───────►  Fluxo bidirecional                                   │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Pontos de Atenção

| Ponto | Função | Capacidade |
|-------|--------|------------|
| **APS (11 UBS)** | Porta de entrada preferencial, coordenação do cuidado, manejo de casos leves/moderados | 70% dos casos de SM |
| **NIRSM-R** | Regulação do acesso à AES, qualificação de encaminhamentos | 100% das solicitações |
| **CAPS I** | Transtornos graves/persistentes, crises, reabilitação psicossocial | Casos graves |
| **CSM** | Ambulatório especializado, casos refratários | Casos moderados refratários |
| **Centro Integrar** | TEA, deficiência intelectual, reabilitação | Público específico |
| **UPA/PS** | Urgências e emergências psiquiátricas | Porta aberta 24h |

---

## 2. FLUXOS DE NAVEGAÇÃO

### 2.1 Macro Fluxos Implementados

| Código | Fluxo | Documento |
|--------|-------|-----------|
| **PCC-01** | Rede Intersetorial → APS → NIRSM-R → AES | `01_PROTOCOLO_INTERSETORIAL_APS_NIRSM_AES.md` |
| **PCC-02** | Demanda Espontânea → APS → NIRSM-R → AES | `02_PROTOCOLO_DEMANDA_ESPONTANEA_APS_NIRSM_AES.md` |
| **PCC-03** | AES → APS (Contrarreferência) | `03_PROTOCOLO_CONTRARREFERENCIA_AES_APS.md` |
| **PCC-04** | APS → RUE → AES (Urgência/Emergência) | `04_PROTOCOLO_URGENCIA_EMERGENCIA_SM.md` |
| **REG-01** | Regulação NIRSM-R | `05_PROTOCOLO_REGULACAO_NIRSM_R.md` |
| **REG-02** | Não Aceitação + Matriciamento | `06_PROTOCOLO_NAO_ACEITACAO_MATRICIAMENTO.md` |

### 2.2 Síntese dos Fluxos

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         SÍNTESE DOS FLUXOS                              │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ENTRADA                    PROCESSAMENTO              SAÍDA             │
│  ─────────                  ─────────────              ──────            │
│                                                                          │
│  ┌────────────┐            ┌─────────────┐                               │
│  │Intersetorial├───┐       │  ACOLHIMENTO│                               │
│  └────────────┘   │       │     +       │                               │
│                    │       │CLASSIFICAÇÃO│                               │
│  ┌────────────┐   │       │  DE RISCO   │      ┌───────────────────┐   │
│  │  Demanda   ├───┼──────►├─────────────┤      │                   │   │
│  │ Espontânea │   │       │             │──────►   VERDE/AZUL      │   │
│  └────────────┘   │       │             │      │   Manejo APS      │   │
│                    │       │             │      └───────────────────┘   │
│  ┌────────────┐   │       │    APS      │                               │
│  │Contrarrefe-├───┘       │  AVALIAÇÃO  │      ┌───────────────────┐   │
│  │  rência    │           │   CLÍNICA   │──────►   AMARELO         │   │
│  └────────────┘           │             │      │ NIRSM-R → AES     │   │
│                            │             │      └───────────────────┘   │
│                            │             │                               │
│  ┌────────────┐           │             │      ┌───────────────────┐   │
│  │  Urgência  ├───────────►─────────────┤──────►   LARANJA         │   │
│  │   RUE      │           │             │      │ CAPS Porta Aberta │   │
│  └────────────┘           │             │      └───────────────────┘   │
│                            │             │                               │
│                            │             │      ┌───────────────────┐   │
│                            │             │──────►   VERMELHO        │   │
│                            │             │      │ SAMU → UPA/PS     │   │
│                            └─────────────┘      └───────────────────┘   │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 3. CLASSIFICAÇÃO DE RISCO

### 3.1 Matriz de Risco RAPS Extrema

| Cor | Critérios | Tempo-Resposta | Destino |
|-----|-----------|----------------|---------|
| **VERMELHO** | Risco iminente (suicídio, violência, psicose com comando) | Imediato | SAMU → UPA/PS |
| **LARANJA** | Crise não contida, ideação suicida, psicose aguda | 24-72h | CAPS Porta Aberta |
| **AMARELO** | Moderado refratário, prejuízo funcional significativo | Até 30 dias | NIRSM-R → AES |
| **VERDE/AZUL** | Leve/estável, manejável na APS | 7-15 dias | APS |

### 3.2 Instrumentos de Apoio

- PHQ-2/PHQ-9 (depressão)
- GAD-2/GAD-7 (ansiedade)
- AUDIT-C (álcool)
- Columbia Protocol (suicidalidade)
- CuidaSM (estratificação)
- M-CHAT-R/F (TEA infantil)

---

## 4. REGULAÇÃO NIRSM-R

### 4.1 Função
Gatekeeper qualificado que garante:
- Encaminhamentos pertinentes e completos
- Direcionamento ao ponto adequado
- Apoio à APS via devolutivas qualificadas
- Monitoramento de filas e tempos de espera

### 4.2 Critérios de Aceite

**Aceito quando:**
- Guia NIRSM-R completa
- Avaliação por e-ESF E e-Multi
- Critério clínico para AES atendido
- Tentativa de manejo na APS documentada

**Devolvido quando:**
- Guia incompleta
- Sem avaliação prévia
- Caso manejável na APS
- Sem tentativa de tratamento

### 4.3 Fluxo de Priorização

| Prioridade | Tempo | Casos |
|------------|-------|-------|
| P1 - Vermelha | 24-72h | Crise, risco elevado |
| P2 - Laranja | Até 15 dias | Grave, primeiro diagnóstico |
| P3 - Amarela | Até 30 dias | Refratário, ajuste |
| P4 - Verde | Até 60 dias | Reavaliação, manutenção |

---

## 5. MATRICIAMENTO

### 5.1 Conceito
Apoio técnico-pedagógico dos especialistas às equipes da APS, permitindo:
- Discussão de casos sem transferência
- Capacitação em serviço
- Aumento da resolutividade da APS
- Redução de encaminhamentos desnecessários

### 5.2 Modalidades

| Modalidade | Frequência | Formato |
|------------|------------|---------|
| Tele-matriciamento | Semanal | 2h videoconferência |
| Presencial | Quinzenal | 3h na UBS |
| Interconsulta | Sob demanda | Avaliação conjunta |

### 5.3 Integração com Devolutivas
- Todo caso devolvido recebe oferta de matriciamento
- Matriciamento transforma devolutiva em momento pedagógico
- Capacita APS para casos semelhantes

---

## 6. CONTRARREFERÊNCIA

### 6.1 Conceito
Processo estruturado de retorno do caso da AES para APS, garantindo:
- Transição segura do cuidado
- Continuidade do tratamento
- Capacitação da APS para seguimento
- Monitoramento do período crítico (90 dias)

### 6.2 Critérios de Estabilidade
- Sintomas controlados
- Funcionalidade recuperada
- Risco baixo
- Medicação estável por ≥4 semanas
- Adesão demonstrada por ≥8 semanas

### 6.3 Período de Transição
- Consulta na APS em até 15 dias
- Reavaliação em 30, 60 e 90 dias
- Monitoramento intensificado
- Retaguarda especializada disponível

---

## 7. POPs IMPLEMENTADOS

| Código | POP | Finalidade |
|--------|-----|------------|
| POP-01 | Acolhimento SM na APS | Padronizar escuta qualificada |
| POP-02 | Classificação de Risco | Padronizar triagem |
| POP-05 | Elaboração do PTS | Padronizar planejamento |
| POP-07 | Manejo de Crise | Padronizar intervenções de urgência |

---

## 8. INDICADORES DE MONITORAMENTO

### 8.1 Indicadores de Acesso

| Indicador | Meta | Frequência |
|-----------|------|------------|
| % de demandas SM acolhidas no mesmo dia | ≥90% | Mensal |
| Tempo médio para consulta especializada | ≤30 dias | Mensal |
| % de contrarreferências agendadas em 15 dias | ≥85% | Mensal |

### 8.2 Indicadores de Qualidade

| Indicador | Meta | Frequência |
|-----------|------|------------|
| % de Guias NIRSM-R completas | ≥90% | Mensal |
| Taxa de aceite de encaminhamentos | 60-70% | Mensal |
| Taxa de re-encaminhamento em 90 dias | ≤20% | Trimestral |

### 8.3 Indicadores de Resultado

| Indicador | Meta | Frequência |
|-----------|------|------------|
| Taxa de resolutividade da APS | ≥60% | Trimestral |
| % de usuários CAPS com PTS elaborado | 100% | Mensal |
| Taxa de vinculação pós-urgência | ≥80% | Mensal |

---

## 9. EDUCAÇÃO PERMANENTE

### 9.1 Capacitações Prioritárias

| Tema | Público | Carga Horária |
|------|---------|---------------|
| MI-mhGAP | Médicos e Enfermeiros APS | 46h |
| Classificação de Risco SM | Enfermeiros | 8h |
| Manejo de Crise | Toda equipe UBS | 4h |
| Prevenção do Suicídio | Toda equipe UBS | 4h |

### 9.2 Calendário de Temas

Temas mensais no matriciamento:
- Jan: Classificação de risco
- Fev: Depressão na APS
- Mar: Ansiedade na APS
- Abr: Prevenção do suicídio
- Mai: Psicofarmacologia básica
- Jun: Intervenções psicossociais
- Jul: Saúde mental infantil
- Ago: Álcool e drogas
- Set: Setembro Amarelo
- Out: SM do idoso
- Nov: Emergências
- Dez: Avaliação anual

---

## 10. GOVERNANÇA

### 10.1 Estrutura de Gestão

| Instância | Composição | Frequência |
|-----------|------------|------------|
| Colegiado de Gestão RAPS | Coord. SM + Gerentes serviços | Mensal |
| Reunião de Regulação NIRSM-R | Equipe reguladora | Semanal |
| Fórum Intersetorial SM | Saúde + Educação + Assist. Social | Bimestral |

### 10.2 Responsabilidades

| Ator | Responsabilidade Principal |
|------|---------------------------|
| Coordenação SM | Gestão estratégica, normatização, monitoramento |
| NIRSM-R | Regulação do acesso, gestão de filas |
| APS | Coordenação do cuidado, resolutividade |
| AES | Tratamento especializado, matriciamento, contrarreferência |

---

## 11. DOCUMENTOS DO SISTEMA

### 11.1 Protocolos

| Documento | Código |
|-----------|--------|
| Intersetorial → APS → NIRSM-R → AES | PCC-01 |
| Demanda Espontânea → APS → NIRSM-R → AES | PCC-02 |
| Contrarreferência AES → APS | PCC-03 |
| Urgência/Emergência | PCC-04 |
| Regulação NIRSM-R | REG-01 |
| Não Aceitação + Matriciamento | REG-02 |

### 11.2 POPs

| Documento | Código |
|-----------|--------|
| Acolhimento SM na APS | POP-01 |
| Classificação de Risco | POP-02 |
| Elaboração do PTS | POP-05 |
| Manejo de Crise | POP-07 |

### 11.3 Instrumentos

| Documento | Finalidade |
|-----------|------------|
| Guia de Referência NIRSM-R | Encaminhamento para AES |
| Ficha de Contrarreferência | Retorno da AES para APS |
| Ficha de Articulação Intersetorial | Encaminhamento da rede intersetorial |

---

## 12. CONSIDERAÇÕES FINAIS

O modelo de compartilhamento do cuidado em saúde mental de Extrema/MG foi estruturado para:

1. **Garantir acesso qualificado** através de portas de entrada claras e regulação transparente

2. **Fortalecer a APS** como coordenadora do cuidado, com suporte de matriciamento

3. **Racionalizar a atenção especializada** com critérios técnicos de encaminhamento

4. **Assegurar continuidade** através de contrarreferência estruturada e PTS compartilhado

5. **Integrar a rede** com fluxos claros entre todos os pontos de atenção

A implementação deste modelo requer:
- Capacitação contínua das equipes
- Monitoramento sistemático de indicadores
- Revisão periódica dos protocolos
- Participação ativa de todos os atores

---

**Aprovado pela Coordenação de Saúde Mental de Extrema/MG**
**Data: Janeiro/2026**

---

*Este documento faz parte do Compêndio de Protocolos de Compartilhamento do Cuidado em Saúde Mental - Extrema/MG*
