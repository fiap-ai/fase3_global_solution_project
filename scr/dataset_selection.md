# Seleção de Dataset - ANEEL

## Objetivo
Selecionar um banco de dados do portal ANEEL (https://dadosabertos.aneel.gov.br/organization/) que permita:
1. Identificar padrões de consumo energético
2. Analisar oportunidades para fontes sustentáveis
3. Integrar aspectos de inovação e justiça social
4. Avaliar crescimento econômico
5. Considerar preservação ambiental

## Metodologia de Seleção

### 1. Critérios de Avaliação
Cada dataset será avaliado considerando:

1. Relevância (peso 3)
   - Alinhamento com objetivos do projeto
   - Aplicabilidade para otimização energética
   - Potencial para insights

2. Qualidade dos Dados (peso 2)
   - Completude
   - Consistência
   - Atualidade
   - Formato acessível

3. Cobertura Temporal (peso 2)
   - Período coberto
   - Frequência de atualização
   - Histórico disponível

4. Granularidade (peso 1)
   - Nível de detalhe
   - Possibilidade de agregação
   - Escopo geográfico

5. Integração (peso 2)
   - Facilidade de uso com R
   - Potencial para análise estatística
   - Combinação com outras fontes

### 2. Sistema de Pontuação
- 1: Insatisfatório
- 2: Regular
- 3: Bom
- 4: Muito Bom
- 5: Excelente

Pontuação máxima possível: 50 pontos
(soma dos produtos de cada critério pelo seu peso)

## Análise dos Datasets

### 1. Projetos de Eficiência Energética
**Descrição:** O Programa de Eficiência Energética tem como objetivo promover o uso eficiente da energia elétrica em todos os setores da economia por meio de projetos que demonstram a importância e a viabilidade econômica de melhoria da eficiência energética de equipamentos, processos e usos finais de energia.

**Pontuação:**
- Relevância: 5 (15 pontos)
  - Alinhamento direto com objetivos
  - Foco em eficiência energética
  - Rico em insights práticos
  
- Qualidade: 4 (8 pontos)
  - Dados estruturados
  - Formatos acessíveis (PDF, CSV)
  - Documentação clara
  
- Temporal: 4 (8 pontos)
  - Histórico de projetos
  - Atualizações regulares
  
- Granularidade: 4 (4 pontos)
  - Detalhes por projeto
  - Informações específicas
  
- Integração: 4 (8 pontos)
  - Formato CSV facilita uso
  - Bom para análise estatística

**Total:** 43/50 pontos

### 2. Componentes Tarifárias
**Descrição:** Apresenta os valores das Tarifas de Energia (TE) e das Tarifas de Uso do Sistema de Distribuição (TUSD), resultantes dos processos de reajustes tarifários das distribuidoras de energia elétrica.

**Pontuação:**
- Relevância: 5 (15 pontos)
  - Dados cruciais para análise de custos
  - Impacto direto na otimização
  - Base para decisões econômicas
  
- Qualidade: 5 (10 pontos)
  - Dados oficiais e estruturados
  - Formato CSV ideal para análise
  - Dicionário de metadados disponível
  
- Temporal: 4 (8 pontos)
  - Histórico de reajustes
  - Atualizações regulares
  - Cobertura desde 2012
  
- Granularidade: 5 (5 pontos)
  - Detalhamento por distribuidora
  - Componentes específicos
  - Abrangência nacional
  
- Integração: 5 (10 pontos)
  - CSV facilita uso com R
  - Estrutura clara para análise
  - Fácil combinação com outros dados

**Total:** 48/50 pontos

### 3. Interrupções de Energia Elétrica
**Descrição:** Dados de todas as interrupções de energia elétrica ocorridas nas redes de distribuição de energia elétrica do país. Não constam as interrupções ocorridas em áreas sob gestão de permissionárias de serviço público (cooperativas).

**Pontuação:**
- Relevância: 4 (12 pontos)
  - Importante para análise de confiabilidade
  - Impacto na otimização de consumo
  - Dados de qualidade do serviço
  
- Qualidade: 5 (10 pontos)
  - Dados oficiais e estruturados
  - Formato CSV disponível
  - Cobertura nacional
  
- Temporal: 5 (10 pontos)
  - Dados em tempo real
  - Histórico completo
  - Atualizações frequentes
  
- Granularidade: 5 (5 pontos)
  - Detalhes por ocorrência
  - Localização específica
  - Causas e durações
  
- Integração: 4 (8 pontos)
  - CSV facilita uso com R
  - Bom para análise estatística
  - Complementa outros datasets

**Total:** 45/50 pontos

## Matriz de Decisão

| Dataset                           | Relevância (3) | Qualidade (2) | Temporal (2) | Granular (1) | Integração (2) | Total |
|----------------------------------|----------------|---------------|--------------|--------------|----------------|--------|
| Projetos de Eficiência Energética| 5 (15)        | 4 (8)         | 4 (8)        | 4 (4)        | 4 (8)          | 43    |
| Componentes Tarifárias           | 5 (15)        | 5 (10)        | 4 (8)        | 5 (5)        | 5 (10)         | 48    |
| Interrupções de Energia          | 4 (12)        | 5 (10)        | 5 (10)       | 5 (5)        | 4 (8)          | 45    |

## Dataset Selecionado
**Componentes Tarifárias** (48/50 pontos)

### Justificativa da Escolha
1. Maior pontuação total (48/50)
2. Relevância máxima para otimização de consumo
3. Dados estruturados e bem documentados
4. Excelente granularidade e potencial de integração
5. Cobertura temporal adequada desde 2012

### Características do Dataset
1. Conteúdo:
   - Tarifas de Energia (TE)
   - Tarifas de Uso do Sistema (TUSD)
   - Reajustes tarifários
   - Dados por distribuidora

2. Formato:
   - CSV para análise em R
   - Dicionário de metadados
   - Estrutura clara

3. Atualizações:
   - Regulares
   - Histórico desde 2012
   - Cobertura nacional

4. Potencial de Análise:
   - Padrões de consumo
   - Impacto econômico
   - Oportunidades de otimização
   - Tendências temporais

## Próximos Passos
1. Download do dataset selecionado
2. Preparação do ambiente R
3. Análise exploratória inicial
4. Desenvolvimento de visualizações
5. Integração com outros datasets conforme necessidade

### Datasets Complementares
Podemos utilizar como suporte:
1. Interrupções de Energia: para análise de confiabilidade
2. Projetos de Eficiência: para benchmarking e boas práticas
