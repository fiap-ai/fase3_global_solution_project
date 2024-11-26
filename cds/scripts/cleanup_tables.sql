-- Script para limpar tabelas existentes
-- Autor: Gabriel Mule (RM560586)
-- Data: 25/11/2023

-- Drop sequences
DROP SEQUENCE seq_distribuidora;
DROP SEQUENCE seq_componente;
DROP SEQUENCE seq_subgrupo;
DROP SEQUENCE seq_modalidade;
DROP SEQUENCE seq_classe;
DROP SEQUENCE seq_tarifa;
DROP SEQUENCE seq_consumption;
DROP SEQUENCE seq_tarifa_vigente;
DROP SEQUENCE seq_metrica;
DROP SEQUENCE seq_renovavel;
DROP SEQUENCE seq_optimization;

-- Drop views
DROP VIEW vw_media_tarifas_distribuidora;
DROP VIEW vw_evolucao_tarifas;
DROP VIEW vw_consumo_por_fonte;

-- Drop tables (em ordem para respeitar constraints)
DROP TABLE optimization_results;
DROP TABLE fontes_renovaveis;
DROP TABLE metricas_eficiencia;
DROP TABLE tarifas_vigentes;
DROP TABLE consumption_history;
DROP TABLE tarifas;
DROP TABLE classes_consumidor;
DROP TABLE modalidades_tarifarias;
DROP TABLE subgrupos_tarifarios;
DROP TABLE componentes_tarifarios;
DROP TABLE distribuidoras;
