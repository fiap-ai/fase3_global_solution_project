#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de monitoramento de performance do banco de dados
Autor: Gabriel Mule (RM560586)
Data: 25/11/2023
"""

import os
import pandas as pd
import oracledb
from datetime import datetime, timedelta
import logging
from dotenv import load_dotenv
import json
import time

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor_performance.log'),
        logging.StreamHandler()
    ]
)

# Carrega variáveis de ambiente
load_dotenv()

# Configurações do banco
DB_CONFIG = {
    'user': os.getenv('ORACLE_USER'),
    'password': os.getenv('ORACLE_PASSWORD'),
    'dsn': os.getenv('ORACLE_DSN')
}

def conectar_banco():
    """Estabelece conexão com o banco Oracle"""
    try:
        connection = oracledb.connect(**DB_CONFIG)
        logging.info("Conexão estabelecida com sucesso")
        return connection
    except Exception as e:
        logging.error(f"Erro ao conectar ao banco: {str(e)}")
        raise

def monitorar_tablespaces():
    """Monitora uso de tablespaces"""
    try:
        conn = conectar_banco()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                df.tablespace_name "Tablespace",
                df.bytes/1024/1024 "Size MB",
                SUM(fs.bytes)/1024/1024 "Free MB",
                Round(((df.bytes-SUM(fs.bytes))/df.bytes)*100,2) "Used %"
            FROM dba_free_space fs,
                 (SELECT tablespace_name, SUM(bytes) bytes
                  FROM dba_data_files
                  GROUP BY tablespace_name) df
            WHERE fs.tablespace_name (+) = df.tablespace_name
            GROUP BY df.tablespace_name, df.bytes
            ORDER BY ((df.bytes-SUM(fs.bytes))/df.bytes) DESC
        """)
        
        results = cursor.fetchall()
        for row in results:
            if row[3] > 80:  # Alerta se uso > 80%
                logging.warning(f"Tablespace {row[0]} com {row[3]}% de uso!")
        
        return results
    except Exception as e:
        logging.error(f"Erro ao monitorar tablespaces: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()

def monitorar_performance_queries():
    """Monitora performance das principais queries"""
    try:
        conn = conectar_banco()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                sql_id,
                sql_text,
                executions,
                elapsed_time/1000000 as elapsed_seconds,
                cpu_time/1000000 as cpu_seconds,
                buffer_gets,
                disk_reads,
                rows_processed
            FROM v$sql
            WHERE executions > 0
            ORDER BY elapsed_time DESC
            FETCH FIRST 10 ROWS ONLY
        """)
        
        results = cursor.fetchall()
        for row in results:
            if row[3]/row[2] > 1:  # Alerta se média > 1 segundo
                logging.warning(f"Query {row[0]} com tempo médio alto: {row[3]/row[2]:.2f} segundos")
        
        return results
    except Exception as e:
        logging.error(f"Erro ao monitorar performance: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()

def monitorar_indices():
    """Monitora estado dos índices"""
    try:
        conn = conectar_banco()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                i.table_name,
                i.index_name,
                i.status,
                i.blevel,
                i.leaf_blocks,
                i.distinct_keys,
                i.clustering_factor
            FROM user_indexes i
            ORDER BY i.table_name, i.index_name
        """)
        
        results = cursor.fetchall()
        for row in results:
            if row[2] != 'VALID':
                logging.error(f"Índice {row[1]} na tabela {row[0]} com status {row[2]}")
            if row[3] > 4:  # Alerta se altura da árvore > 4
                logging.warning(f"Índice {row[1]} com altura {row[3]} - considerar rebuild")
        
        return results
    except Exception as e:
        logging.error(f"Erro ao monitorar índices: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()

def monitorar_materialized_views():
    """Monitora estado das materialized views"""
    try:
        conn = conectar_banco()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                mview_name,
                last_refresh_date,
                last_refresh_type,
                stale_since,
                compile_state,
                staleness
            FROM user_mviews
        """)
        
        results = cursor.fetchall()
        now = datetime.now()
        for row in results:
            if row[1]:  # Se tem data de último refresh
                last_refresh = row[1].replace(tzinfo=None)
                if (now - last_refresh) > timedelta(days=1):
                    logging.warning(f"MView {row[0]} não atualizada há mais de 24h")
            if row[4] != 'VALID':
                logging.error(f"MView {row[0]} com estado de compilação {row[4]}")
        
        return results
    except Exception as e:
        logging.error(f"Erro ao monitorar MVs: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()

def gerar_relatorio():
    """Gera relatório completo de performance"""
    try:
        report = {
            'timestamp': datetime.now().isoformat(),
            'tablespaces': monitorar_tablespaces(),
            'queries': monitorar_performance_queries(),
            'indices': monitorar_indices(),
            'mvs': monitorar_materialized_views()
        }
        
        # Salva relatório
        filename = f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=4, default=str)
        
        logging.info(f"Relatório gerado: {filename}")
        return report
    except Exception as e:
        logging.error(f"Erro ao gerar relatório: {str(e)}")
        raise

def monitoramento_continuo(intervalo_minutos=60):
    """Executa monitoramento contínuo"""
    logging.info(f"Iniciando monitoramento contínuo (intervalo: {intervalo_minutos} minutos)")
    
    while True:
        try:
            gerar_relatorio()
            time.sleep(intervalo_minutos * 60)
        except Exception as e:
            logging.error(f"Erro no monitoramento: {str(e)}")
            time.sleep(300)  # Espera 5 minutos em caso de erro

if __name__ == "__main__":
    monitoramento_continuo()
