# Banco de Dados - Consumo Energético
> Autor: Gabriel Mule (RM560586)  
> Data: 25/11/2023

## Visão Geral
Este módulo implementa o armazenamento e processamento dos dados de consumo energético, utilizando Oracle Database para persistência e Python para ETL.

## Estrutura
```
cds/
├── scripts/
│   ├── create_tables.sql      # Criação das tabelas
│   ├── 02_optimize_tables.sql # Otimizações (particionamento, MVs)
│   ├── 03_analysis_views.sql  # Views analíticas
│   ├── etl_tarifas.py        # ETL principal
│   ├── monitor_performance.py # Monitoramento
│   └── maintenance.py         # Backup e manutenção
└── README.md
```

## Modelagem do Banco

### Tabelas Dimensão
1. `distribuidoras`
   - Cadastro de distribuidoras
   - Dados de identificação

2. `componentes_tarifarios`
   - Tipos de componentes
   - Unidades de medida

3. `subgrupos_tarifarios`
   - Classificação tarifária
   - Níveis de tensão

4. `modalidades_tarifarias`
   - Tipos de tarifação
   - Características

5. `classes_consumidor`
   - Classes e subclasses
   - Detalhamento

### Tabela Fato
1. `tarifas`
   - Valores e vigências
   - Relacionamentos
   - Particionada por data

### Views Analíticas
1. `vw_consumo_per_capita`
   - Consumo por distribuidora
   - Ranking de consumo
   - Análise temporal

2. `vw_demanda_regional`
   - Demanda por região
   - Estatísticas detalhadas
   - Tendências regionais

3. `vw_eficiencia_energetica`
   - Indicadores de eficiência
   - Variações temporais
   - Rankings de performance

4. `vw_fontes_renovaveis`
   - Componentes PROINFA e CDE
   - Geração distribuída
   - Evolução dos incentivos

5. `vw_tendencias_consumo`
   - Análise temporal
   - Variações percentuais
   - Médias móveis

### Materialized Views
1. `mv_media_mensal_componente`
   - Análise temporal
   - Médias e desvios

2. `mv_analise_subgrupo_classe`
   - Análise por segmento
   - Distribuição

3. `mv_analise_regional`
   - Análise geográfica
   - Comparativos

## ETL

### Processo Principal
1. Extração
   - Leitura do CSV
   - Validação inicial

2. Transformação
   - Limpeza de dados
   - Tratamento de outliers
   - Padronização

3. Carga
   - Dimensões primeiro
   - Fatos em seguida
   - Controle transacional

### Monitoramento
1. Performance
   - Tablespaces
   - Queries
   - Índices
   - MVs

2. Logs
   - Erros
   - Warnings
   - Métricas

## Manutenção

### Backup
- Diário completo
- Retenção: 7 dias
- Compressão

### Otimização
1. Índices
   - Rebuild quando necessário
   - Monitoramento de fragmentação

2. Estatísticas
   - Atualização periódica
   - Amostragem automática

3. MVs
   - Refresh diário
   - Validação de estado

## Configuração

### Requisitos
- Oracle Database 19c+
- Python 3.8+
- oracle-instantclient
- python-oracledb

### Variáveis de Ambiente
```bash
ORACLE_USER=user
ORACLE_PASSWORD=pass
ORACLE_DSN=host:port/service
BACKUP_DIR=/path/to/backups
BACKUP_RETENTION_DAYS=7
```

### Instalação
1. Criar usuário e tablespaces
```sql
CREATE TABLESPACE energy_data
DATAFILE 'energy_data01.dbf'
SIZE 1G
AUTOEXTEND ON;

CREATE USER energy_user
IDENTIFIED BY password
DEFAULT TABLESPACE energy_data;
```

2. Executar scripts
```bash
# Criar estrutura
sqlplus energy_user/password@service @create_tables.sql
sqlplus energy_user/password@service @02_optimize_tables.sql
sqlplus energy_user/password@service @03_analysis_views.sql

# Instalar dependências Python
pip install -r requirements.txt
```

## Uso

### ETL
```bash
# Executar carga
python etl_tarifas.py

# Monitorar performance
python monitor_performance.py

# Manutenção
python maintenance.py
```

### Consultas Úteis

#### Análise de Consumo
```sql
-- Consumo per capita
SELECT * FROM vw_consumo_per_capita
WHERE mes >= ADD_MONTHS(SYSDATE, -12)
ORDER BY mes DESC, consumo_per_capita DESC;

-- Demanda regional
SELECT * FROM vw_demanda_regional
WHERE valor_total > (
    SELECT AVG(valor_total) FROM vw_demanda_regional
)
ORDER BY mes DESC, valor_total DESC;

-- Eficiência energética
SELECT * FROM vw_eficiencia_energetica
WHERE ranking_eficiencia <= 10
ORDER BY mes DESC, valor_medio;
```

#### Fontes Renováveis
```sql
-- Evolução dos incentivos
SELECT * FROM vw_fontes_renovaveis
WHERE mes >= ADD_MONTHS(SYSDATE, -12)
ORDER BY mes DESC, valor_total DESC;

-- Tendências de consumo
SELECT * FROM vw_tendencias_consumo
WHERE variacao_anual_percentual IS NOT NULL
ORDER BY mes DESC, variacao_anual_percentual DESC;
```

#### Análises Agregadas
```sql
-- Média por componente
SELECT * FROM mv_media_mensal_componente
WHERE mes >= ADD_MONTHS(SYSDATE, -12);

-- Análise regional
SELECT * FROM mv_analise_regional
WHERE valor_medio > (
    SELECT AVG(valor_medio) FROM mv_analise_regional
);

-- Evolução temporal
SELECT * FROM vw_evolucao_tarifas
ORDER BY mes DESC;
```

## Monitoramento

### Métricas Principais
1. Performance
   - Tempo de carga
   - Uso de tablespace
   - Tempo de queries

2. Qualidade
   - Registros processados
   - Erros encontrados
   - Dados inconsistentes

3. Disponibilidade
   - Uptime do banco
   - Status das MVs
   - Estado dos backups

### Alertas
- Uso de tablespace > 80%
- Queries lentas (>1s)
- Falhas de backup
- MVs desatualizadas

## Próximos Passos
1. Implementar particionamento por range-hash
2. Adicionar compressão nas partições antigas
3. Implementar parallel query para grandes consultas
4. Expandir monitoramento com métricas adicionais
5. Adicionar replicação para disaster recovery
