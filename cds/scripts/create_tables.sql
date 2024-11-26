-- Criação das tabelas para armazenamento dos dados de consumo energético
-- Autor: Gabriel Mule (RM560586)
-- Data: 25/11/2025

-- Tabela de Distribuidoras
CREATE TABLE distribuidoras (
    id_distribuidora NUMBER PRIMARY KEY,
    nome VARCHAR2(100) NOT NULL,
    cnpj VARCHAR2(14) NOT NULL UNIQUE,
    data_cadastro DATE DEFAULT SYSDATE,
    CONSTRAINT uk_cnpj CHECK (REGEXP_LIKE(cnpj, '^\d{14}$'))
);

-- Tabela de Componentes Tarifários
CREATE TABLE componentes_tarifarios (
    id_componente NUMBER PRIMARY KEY,
    descricao VARCHAR2(100) NOT NULL,
    unidade VARCHAR2(10) NOT NULL,
    data_cadastro DATE DEFAULT SYSDATE
);

-- Tabela de Subgrupos Tarifários
CREATE TABLE subgrupos_tarifarios (
    id_subgrupo NUMBER PRIMARY KEY,
    codigo VARCHAR2(10) NOT NULL,
    descricao VARCHAR2(100),
    data_cadastro DATE DEFAULT SYSDATE
);

-- Tabela de Modalidades Tarifárias
CREATE TABLE modalidades_tarifarias (
    id_modalidade NUMBER PRIMARY KEY,
    nome VARCHAR2(50) NOT NULL,
    descricao VARCHAR2(200),
    data_cadastro DATE DEFAULT SYSDATE
);

-- Tabela de Classes de Consumidor
CREATE TABLE classes_consumidor (
    id_classe NUMBER PRIMARY KEY,
    nome VARCHAR2(100) NOT NULL,
    subclasse VARCHAR2(100),
    detalhe VARCHAR2(200),
    data_cadastro DATE DEFAULT SYSDATE
);

-- Tabela de Tarifas
CREATE TABLE tarifas (
    id_tarifa NUMBER PRIMARY KEY,
    id_distribuidora NUMBER NOT NULL,
    id_componente NUMBER NOT NULL,
    id_subgrupo NUMBER NOT NULL,
    id_modalidade NUMBER NOT NULL,
    id_classe NUMBER NOT NULL,
    data_inicio_vigencia DATE NOT NULL,
    data_fim_vigencia DATE NOT NULL,
    posto_tarifario VARCHAR2(20),
    valor NUMBER(12,4) NOT NULL,
    base_tarifaria VARCHAR2(50),
    data_cadastro DATE DEFAULT SYSDATE,
    CONSTRAINT fk_tarifa_distribuidora FOREIGN KEY (id_distribuidora) REFERENCES distribuidoras(id_distribuidora),
    CONSTRAINT fk_tarifa_componente FOREIGN KEY (id_componente) REFERENCES componentes_tarifarios(id_componente),
    CONSTRAINT fk_tarifa_subgrupo FOREIGN KEY (id_subgrupo) REFERENCES subgrupos_tarifarios(id_subgrupo),
    CONSTRAINT fk_tarifa_modalidade FOREIGN KEY (id_modalidade) REFERENCES modalidades_tarifarias(id_modalidade),
    CONSTRAINT fk_tarifa_classe FOREIGN KEY (id_classe) REFERENCES classes_consumidor(id_classe),
    CONSTRAINT ck_valor_positivo CHECK (valor >= 0),
    CONSTRAINT ck_datas_vigencia CHECK (data_fim_vigencia >= data_inicio_vigencia)
);

-- Tabela de Histórico de Consumo
CREATE TABLE consumption_history (
    id NUMBER PRIMARY KEY,
    timestamp DATE DEFAULT SYSDATE,
    consumption NUMBER(12,4) NOT NULL,
    cost NUMBER(12,4) NOT NULL,
    source VARCHAR2(50),
    equipment VARCHAR2(100),
    CONSTRAINT ck_consumption_positive CHECK (consumption >= 0),
    CONSTRAINT ck_cost_positive CHECK (cost >= 0)
);

-- Tabela de Tarifas Vigentes
CREATE TABLE tarifas_vigentes (
    id NUMBER PRIMARY KEY,
    distribuidora VARCHAR2(100) NOT NULL,
    componente VARCHAR2(100) NOT NULL,
    unidade VARCHAR2(20) NOT NULL,
    valor NUMBER(12,4) NOT NULL,
    data_vigencia DATE DEFAULT SYSDATE,
    CONSTRAINT ck_tarifa_vigente_valor CHECK (valor >= 0)
);

-- Tabela de Métricas de Eficiência
CREATE TABLE metricas_eficiencia (
    id NUMBER PRIMARY KEY,
    mes DATE,
    valor_medio NUMBER(12,4),
    variacao_anterior NUMBER(12,4),
    ranking_eficiencia NUMBER(3),
    CONSTRAINT ck_ranking_range CHECK (ranking_eficiencia BETWEEN 1 AND 100)
);

-- Tabela de Fontes Renováveis
CREATE TABLE fontes_renovaveis (
    id NUMBER PRIMARY KEY,
    componente VARCHAR2(100),
    valor_total NUMBER(12,4),
    mes DATE,
    CONSTRAINT ck_valor_total_positive CHECK (valor_total >= 0)
);

-- Tabela de Resultados de Otimização
CREATE TABLE optimization_results (
    id NUMBER PRIMARY KEY,
    timestamp DATE DEFAULT SYSDATE,
    tipo VARCHAR2(50) NOT NULL,
    valor_anterior NUMBER(12,4) NOT NULL,
    valor_otimizado NUMBER(12,4) NOT NULL,
    economia_estimada NUMBER(12,4),
    recomendacao VARCHAR2(4000),
    CONSTRAINT ck_economia_positive CHECK (economia_estimada >= 0)
);

-- Índices para otimização
CREATE INDEX idx_tarifa_datas ON tarifas(data_inicio_vigencia, data_fim_vigencia);
CREATE INDEX idx_tarifa_valor ON tarifas(valor);
CREATE INDEX idx_distribuidora_nome ON distribuidoras(nome);
CREATE INDEX idx_componente_desc ON componentes_tarifarios(descricao);
CREATE INDEX idx_consumption_timestamp ON consumption_history(timestamp);
CREATE INDEX idx_tarifas_vigentes_comp ON tarifas_vigentes(componente);
CREATE INDEX idx_metricas_mes ON metricas_eficiencia(mes);
CREATE INDEX idx_renovaveis_mes ON fontes_renovaveis(mes);
CREATE INDEX idx_optimization_timestamp ON optimization_results(timestamp);

-- Sequências para geração de IDs
CREATE SEQUENCE seq_distribuidora START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE seq_componente START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE seq_subgrupo START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE seq_modalidade START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE seq_classe START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE seq_tarifa START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE seq_consumption START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE seq_tarifa_vigente START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE seq_metrica START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE seq_renovavel START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE seq_optimization START WITH 1 INCREMENT BY 1;

-- View para análise de médias por distribuidora
CREATE OR REPLACE VIEW vw_media_tarifas_distribuidora AS
SELECT 
    d.nome as distribuidora,
    ct.descricao as componente,
    st.codigo as subgrupo,
    mt.nome as modalidade,
    AVG(t.valor) as valor_medio,
    COUNT(*) as total_registros
FROM tarifas t
JOIN distribuidoras d ON t.id_distribuidora = d.id_distribuidora
JOIN componentes_tarifarios ct ON t.id_componente = ct.id_componente
JOIN subgrupos_tarifarios st ON t.id_subgrupo = st.id_subgrupo
JOIN modalidades_tarifarias mt ON t.id_modalidade = mt.id_modalidade
GROUP BY d.nome, ct.descricao, st.codigo, mt.nome;

-- View para análise temporal
CREATE OR REPLACE VIEW vw_evolucao_tarifas AS
SELECT 
    TRUNC(t.data_inicio_vigencia, 'MM') as mes,
    ct.descricao as componente,
    st.codigo as subgrupo,
    AVG(t.valor) as valor_medio,
    MIN(t.valor) as valor_minimo,
    MAX(t.valor) as valor_maximo,
    COUNT(*) as total_registros
FROM tarifas t
JOIN componentes_tarifarios ct ON t.id_componente = ct.id_componente
JOIN subgrupos_tarifarios st ON t.id_subgrupo = st.id_subgrupo
GROUP BY TRUNC(t.data_inicio_vigencia, 'MM'), ct.descricao, st.codigo
ORDER BY mes, componente, subgrupo;

-- View para consumo por fonte
CREATE OR REPLACE VIEW vw_consumo_por_fonte AS
SELECT
    source as fonte,
    SUM(consumption) as consumo_total,
    AVG(cost) as custo_medio,
    COUNT(*) as total_registros
FROM consumption_history
GROUP BY source;

-- Comentários nas tabelas
COMMENT ON TABLE distribuidoras IS 'Cadastro de distribuidoras de energia';
COMMENT ON TABLE componentes_tarifarios IS 'Tipos de componentes tarifários';
COMMENT ON TABLE subgrupos_tarifarios IS 'Subgrupos de classificação tarifária';
COMMENT ON TABLE modalidades_tarifarias IS 'Modalidades de tarifação';
COMMENT ON TABLE classes_consumidor IS 'Classes e subclasses de consumidores';
COMMENT ON TABLE tarifas IS 'Registro de tarifas e seus valores';
COMMENT ON TABLE consumption_history IS 'Histórico de consumo de energia';
COMMENT ON TABLE tarifas_vigentes IS 'Tarifas atualmente vigentes';
COMMENT ON TABLE metricas_eficiencia IS 'Métricas de eficiência energética';
COMMENT ON TABLE fontes_renovaveis IS 'Dados de fontes renováveis de energia';
COMMENT ON TABLE optimization_results IS 'Resultados de otimizações realizadas';
