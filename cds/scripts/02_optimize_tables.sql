-- Otimizações para as tabelas de consumo energético
-- Autor: Gabriel Mule (RM560586)
-- Data: 25/11/2023

-- 1. Particionamento da tabela de tarifas
ALTER TABLE tarifas 
MODIFY PARTITION BY RANGE (data_inicio_vigencia) (
    PARTITION tarifa_2012 VALUES LESS THAN (TO_DATE('2013-01-01', 'YYYY-MM-DD')),
    PARTITION tarifa_2013 VALUES LESS THAN (TO_DATE('2014-01-01', 'YYYY-MM-DD')),
    PARTITION tarifa_2014 VALUES LESS THAN (TO_DATE('2015-01-01', 'YYYY-MM-DD')),
    PARTITION tarifa_future VALUES LESS THAN (MAXVALUE)
);

-- 2. Materialized Views para análises comuns

-- 2.1 Média mensal por componente
CREATE MATERIALIZED VIEW mv_media_mensal_componente
BUILD IMMEDIATE
REFRESH COMPLETE ON DEMAND
ENABLE QUERY REWRITE
AS
SELECT 
    TRUNC(t.data_inicio_vigencia, 'MM') as mes,
    ct.descricao as componente,
    ct.unidade,
    AVG(t.valor) as valor_medio,
    COUNT(*) as total_registros,
    MIN(t.valor) as valor_minimo,
    MAX(t.valor) as valor_maximo,
    STDDEV(t.valor) as desvio_padrao
FROM tarifas t
JOIN componentes_tarifarios ct ON t.id_componente = ct.id_componente
GROUP BY 
    TRUNC(t.data_inicio_vigencia, 'MM'),
    ct.descricao,
    ct.unidade;

-- 2.2 Análise por subgrupo e classe
CREATE MATERIALIZED VIEW mv_analise_subgrupo_classe
BUILD IMMEDIATE
REFRESH COMPLETE ON DEMAND
ENABLE QUERY REWRITE
AS
SELECT 
    st.codigo as subgrupo,
    cc.nome as classe,
    cc.subclasse,
    ct.unidade,
    AVG(t.valor) as valor_medio,
    COUNT(*) as total_registros,
    COUNT(DISTINCT t.id_distribuidora) as total_distribuidoras
FROM tarifas t
JOIN subgrupos_tarifarios st ON t.id_subgrupo = st.id_subgrupo
JOIN classes_consumidor cc ON t.id_classe = cc.id_classe
JOIN componentes_tarifarios ct ON t.id_componente = ct.id_componente
GROUP BY 
    st.codigo,
    cc.nome,
    cc.subclasse,
    ct.unidade;

-- 2.3 Análise regional
CREATE MATERIALIZED VIEW mv_analise_regional
BUILD IMMEDIATE
REFRESH COMPLETE ON DEMAND
ENABLE QUERY REWRITE
AS
SELECT 
    d.nome as distribuidora,
    ct.descricao as componente,
    ct.unidade,
    AVG(t.valor) as valor_medio,
    COUNT(*) as total_registros,
    MIN(t.valor) as valor_minimo,
    MAX(t.valor) as valor_maximo
FROM tarifas t
JOIN distribuidoras d ON t.id_distribuidora = d.id_distribuidora
JOIN componentes_tarifarios ct ON t.id_componente = ct.id_componente
GROUP BY 
    d.nome,
    ct.descricao,
    ct.unidade;

-- 3. Índices para as Materialized Views
CREATE INDEX idx_mv_media_mensal_mes ON mv_media_mensal_componente(mes);
CREATE INDEX idx_mv_media_mensal_comp ON mv_media_mensal_componente(componente);

CREATE INDEX idx_mv_subgrupo_classe ON mv_analise_subgrupo_classe(subgrupo, classe);
CREATE INDEX idx_mv_subgrupo_valor ON mv_analise_subgrupo_classe(valor_medio);

CREATE INDEX idx_mv_regional_dist ON mv_analise_regional(distribuidora);
CREATE INDEX idx_mv_regional_comp ON mv_analise_regional(componente);

-- 4. Jobs para refresh das MVs
BEGIN
    DBMS_SCHEDULER.CREATE_JOB (
        job_name        => 'JOB_REFRESH_MV_DIARIO',
        job_type        => 'STORED_PROCEDURE',
        job_action      => 'BEGIN
                            DBMS_MVIEW.REFRESH(''mv_media_mensal_componente'');
                            DBMS_MVIEW.REFRESH(''mv_analise_subgrupo_classe'');
                            DBMS_MVIEW.REFRESH(''mv_analise_regional'');
                           END;',
        start_date     => SYSTIMESTAMP,
        repeat_interval => 'FREQ=DAILY; BYHOUR=1',
        enabled         => TRUE,
        comments        => 'Job para atualização diária das materialized views'
    );
END;
/

-- 5. Tabela de Auditoria
CREATE TABLE audit_tarifas (
    audit_id NUMBER PRIMARY KEY,
    table_name VARCHAR2(30),
    operation VARCHAR2(10),
    old_value CLOB,
    new_value CLOB,
    changed_by VARCHAR2(30),
    change_date TIMESTAMP DEFAULT SYSTIMESTAMP
);

CREATE SEQUENCE seq_audit START WITH 1 INCREMENT BY 1;

-- 6. Trigger de Auditoria
CREATE OR REPLACE TRIGGER trg_audit_tarifas
AFTER INSERT OR UPDATE OR DELETE ON tarifas
FOR EACH ROW
DECLARE
    v_old_value CLOB;
    v_new_value CLOB;
    v_operation VARCHAR2(10);
BEGIN
    IF INSERTING THEN
        v_operation := 'INSERT';
        v_new_value := 
            'ID: ' || :NEW.id_tarifa || 
            ', Valor: ' || :NEW.valor ||
            ', Vigência: ' || TO_CHAR(:NEW.data_inicio_vigencia, 'DD/MM/YYYY');
    ELSIF UPDATING THEN
        v_operation := 'UPDATE';
        v_old_value := 
            'ID: ' || :OLD.id_tarifa || 
            ', Valor: ' || :OLD.valor ||
            ', Vigência: ' || TO_CHAR(:OLD.data_inicio_vigencia, 'DD/MM/YYYY');
        v_new_value := 
            'ID: ' || :NEW.id_tarifa || 
            ', Valor: ' || :NEW.valor ||
            ', Vigência: ' || TO_CHAR(:NEW.data_inicio_vigencia, 'DD/MM/YYYY');
    ELSIF DELETING THEN
        v_operation := 'DELETE';
        v_old_value := 
            'ID: ' || :OLD.id_tarifa || 
            ', Valor: ' || :OLD.valor ||
            ', Vigência: ' || TO_CHAR(:OLD.data_inicio_vigencia, 'DD/MM/YYYY');
    END IF;

    INSERT INTO audit_tarifas (
        audit_id,
        table_name,
        operation,
        old_value,
        new_value,
        changed_by,
        change_date
    ) VALUES (
        seq_audit.NEXTVAL,
        'TARIFAS',
        v_operation,
        v_old_value,
        v_new_value,
        USER,
        SYSTIMESTAMP
    );
END;
/

-- 7. Comentários
COMMENT ON MATERIALIZED VIEW mv_media_mensal_componente IS 'Análise mensal dos componentes tarifários';
COMMENT ON MATERIALIZED VIEW mv_analise_subgrupo_classe IS 'Análise por subgrupo e classe de consumo';
COMMENT ON MATERIALIZED VIEW mv_analise_regional IS 'Análise regional das tarifas';
COMMENT ON TABLE audit_tarifas IS 'Registro de alterações na tabela de tarifas';
