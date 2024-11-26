-- Views para análise de consumo energético
-- Autor: Gabriel Mule (RM560586)
-- Data: 25/11/2023

-- 1. View de Consumo Per Capita
CREATE OR REPLACE VIEW vw_consumo_per_capita AS
WITH consumo_total AS (
    SELECT 
        d.nome as distribuidora,
        TRUNC(t.data_inicio_vigencia, 'MM') as mes,
        SUM(t.valor) as consumo_total,
        COUNT(DISTINCT cc.id_classe) as total_classes
    FROM tarifas t
    JOIN distribuidoras d ON t.id_distribuidora = d.id_distribuidora
    JOIN classes_consumidor cc ON t.id_classe = cc.id_classe
    WHERE t.valor > 0
    GROUP BY d.nome, TRUNC(t.data_inicio_vigencia, 'MM')
)
SELECT 
    distribuidora,
    mes,
    consumo_total,
    consumo_total / total_classes as consumo_per_capita,
    RANK() OVER (PARTITION BY mes ORDER BY consumo_total DESC) as ranking_consumo
FROM consumo_total
ORDER BY mes DESC, consumo_total DESC;

-- 2. View de Demanda por Região
CREATE OR REPLACE VIEW vw_demanda_regional AS
SELECT 
    d.nome as distribuidora,
    st.codigo as subgrupo,
    ct.descricao as componente,
    ct.unidade,
    TRUNC(t.data_inicio_vigencia, 'MM') as mes,
    COUNT(*) as total_medicoes,
    AVG(t.valor) as valor_medio,
    SUM(t.valor) as valor_total,
    MIN(t.valor) as valor_minimo,
    MAX(t.valor) as valor_maximo,
    STDDEV(t.valor) as desvio_padrao,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY t.valor) as mediana
FROM tarifas t
JOIN distribuidoras d ON t.id_distribuidora = d.id_distribuidora
JOIN componentes_tarifarios ct ON t.id_componente = ct.id_componente
JOIN subgrupos_tarifarios st ON t.id_subgrupo = st.id_subgrupo
WHERE t.valor > 0
GROUP BY 
    d.nome,
    st.codigo,
    ct.descricao,
    ct.unidade,
    TRUNC(t.data_inicio_vigencia, 'MM')
ORDER BY mes DESC, valor_total DESC;

-- 3. View de Análise de Eficiência
CREATE OR REPLACE VIEW vw_eficiencia_energetica AS
WITH base_calculo AS (
    SELECT 
        d.nome as distribuidora,
        cc.nome as classe_consumidor,
        st.codigo as subgrupo,
        TRUNC(t.data_inicio_vigencia, 'MM') as mes,
        AVG(t.valor) as valor_medio,
        COUNT(*) as total_medicoes,
        SUM(CASE WHEN t.valor = 0 THEN 1 ELSE 0 END) as zeros,
        MIN(t.valor) as valor_minimo,
        MAX(t.valor) as valor_maximo
    FROM tarifas t
    JOIN distribuidoras d ON t.id_distribuidora = d.id_distribuidora
    JOIN classes_consumidor cc ON t.id_classe = cc.id_classe
    JOIN subgrupos_tarifarios st ON t.id_subgrupo = st.id_subgrupo
    GROUP BY 
        d.nome,
        cc.nome,
        st.codigo,
        TRUNC(t.data_inicio_vigencia, 'MM')
)
SELECT 
    distribuidora,
    classe_consumidor,
    subgrupo,
    mes,
    valor_medio,
    valor_medio - LAG(valor_medio) OVER (
        PARTITION BY distribuidora, classe_consumidor, subgrupo 
        ORDER BY mes
    ) as variacao_anterior,
    CASE 
        WHEN zeros > 0 THEN total_medicoes - zeros
        ELSE total_medicoes
    END as medicoes_validas,
    ROUND((valor_maximo - valor_minimo) / NULLIF(valor_medio, 0) * 100, 2) as amplitude_percentual,
    RANK() OVER (
        PARTITION BY mes 
        ORDER BY valor_medio
    ) as ranking_eficiencia
FROM base_calculo
WHERE valor_medio > 0
ORDER BY mes DESC, valor_medio;

-- 4. View de Fontes Renováveis
CREATE OR REPLACE VIEW vw_fontes_renovaveis AS
SELECT 
    d.nome as distribuidora,
    ct.descricao as componente,
    TRUNC(t.data_inicio_vigencia, 'MM') as mes,
    COUNT(*) as total_medicoes,
    AVG(t.valor) as valor_medio,
    SUM(t.valor) as valor_total,
    MIN(t.valor) as valor_minimo,
    MAX(t.valor) as valor_maximo
FROM tarifas t
JOIN distribuidoras d ON t.id_distribuidora = d.id_distribuidora
JOIN componentes_tarifarios ct ON t.id_componente = ct.id_componente
WHERE ct.descricao LIKE '%PROINFA%'
   OR ct.descricao LIKE '%CDE%'
   OR ct.descricao LIKE '%GD%'
GROUP BY 
    d.nome,
    ct.descricao,
    TRUNC(t.data_inicio_vigencia, 'MM')
ORDER BY mes DESC, valor_total DESC;

-- 5. View de Tendências de Consumo
CREATE OR REPLACE VIEW vw_tendencias_consumo AS
WITH dados_mensais AS (
    SELECT 
        TRUNC(t.data_inicio_vigencia, 'MM') as mes,
        ct.descricao as componente,
        ct.unidade,
        AVG(t.valor) as valor_medio,
        COUNT(*) as total_medicoes
    FROM tarifas t
    JOIN componentes_tarifarios ct ON t.id_componente = ct.id_componente
    WHERE t.valor > 0
    GROUP BY 
        TRUNC(t.data_inicio_vigencia, 'MM'),
        ct.descricao,
        ct.unidade
)
SELECT 
    mes,
    componente,
    unidade,
    valor_medio,
    valor_medio - LAG(valor_medio) OVER (
        PARTITION BY componente 
        ORDER BY mes
    ) as variacao_mes_anterior,
    ROUND(
        (valor_medio - LAG(valor_medio, 12) OVER (
            PARTITION BY componente 
            ORDER BY mes
        )) / NULLIF(LAG(valor_medio, 12) OVER (
            PARTITION BY componente 
            ORDER BY mes
        ), 0) * 100,
        2
    ) as variacao_anual_percentual,
    AVG(valor_medio) OVER (
        PARTITION BY componente 
        ORDER BY mes 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) as media_movel_3m,
    total_medicoes,
    RANK() OVER (
        PARTITION BY mes 
        ORDER BY valor_medio DESC
    ) as ranking_valor
FROM dados_mensais
ORDER BY mes DESC, valor_medio DESC;

-- Comentários nas views
COMMENT ON VIEW vw_consumo_per_capita IS 'Análise de consumo per capita por distribuidora';
COMMENT ON VIEW vw_demanda_regional IS 'Análise detalhada da demanda por região';
COMMENT ON VIEW vw_eficiencia_energetica IS 'Indicadores de eficiência energética';
COMMENT ON VIEW vw_fontes_renovaveis IS 'Análise de componentes relacionados a fontes renováveis';
COMMENT ON VIEW vw_tendencias_consumo IS 'Análise de tendências de consumo com variações temporais';

-- Índices para otimizar as views
CREATE INDEX idx_tarifa_data_valor ON tarifas(data_inicio_vigencia, valor);
CREATE INDEX idx_tarifa_distribuidora ON tarifas(id_distribuidora);
CREATE INDEX idx_tarifa_componente ON tarifas(id_componente);
CREATE INDEX idx_componente_desc ON componentes_tarifarios(descricao);
