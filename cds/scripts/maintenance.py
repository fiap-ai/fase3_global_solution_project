#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de backup e manutenção do banco de dados
Autor: Gabriel Mule (RM560586)
Data: 25/11/2023
"""

import os
import subprocess
import logging
from datetime import datetime
import oracledb
from dotenv import load_dotenv
import shutil
import gzip

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('maintenance.log'),
        logging.StreamHandler()
    ]
)

# Carrega variáveis de ambiente
load_dotenv()

# Configurações
DB_CONFIG = {
    'user': os.getenv('ORACLE_USER'),
    'password': os.getenv('ORACLE_PASSWORD'),
    'dsn': os.getenv('ORACLE_DSN')
}

BACKUP_DIR = os.getenv('BACKUP_DIR', 'backups')
RETENTION_DAYS = int(os.getenv('BACKUP_RETENTION_DAYS', '7'))

def conectar_banco():
    """Estabelece conexão com o banco Oracle"""
    try:
        connection = oracledb.connect(**DB_CONFIG)
        logging.info("Conexão estabelecida com sucesso")
        return connection
    except Exception as e:
        logging.error(f"Erro ao conectar ao banco: {str(e)}")
        raise

def executar_backup():
    """Executa backup do banco de dados"""
    try:
        # Cria diretório de backup se não existir
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
        
        # Nome do arquivo de backup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(BACKUP_DIR, f'backup_{timestamp}.dmp')
        logfile = os.path.join(BACKUP_DIR, f'backup_{timestamp}.log')
        
        # Comando de export
        cmd = [
            'expdp',
            f"{DB_CONFIG['user']}/{DB_CONFIG['password']}@{DB_CONFIG['dsn']}",
            f"DIRECTORY=DATA_PUMP_DIR",
            f"DUMPFILE=backup_{timestamp}.dmp",
            f"LOGFILE=backup_{timestamp}.log",
            'SCHEMAS=ENERGY_DB',
            'COMPRESSION=ALL'
        ]
        
        # Executa backup
        logging.info("Iniciando backup...")
        subprocess.run(cmd, check=True)
        
        # Comprime arquivo de backup
        with open(backup_file, 'rb') as f_in:
            with gzip.open(f'{backup_file}.gz', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Remove arquivo original
        os.remove(backup_file)
        
        logging.info(f"Backup concluído: {backup_file}.gz")
        return f'{backup_file}.gz'
    
    except Exception as e:
        logging.error(f"Erro ao executar backup: {str(e)}")
        raise

def limpar_backups_antigos():
    """Remove backups mais antigos que RETENTION_DAYS"""
    try:
        now = datetime.now()
        count = 0
        
        for filename in os.listdir(BACKUP_DIR):
            if filename.startswith('backup_') and filename.endswith('.gz'):
                filepath = os.path.join(BACKUP_DIR, filename)
                file_date = datetime.strptime(filename[7:15], '%Y%m%d')
                
                if (now - file_date).days > RETENTION_DAYS:
                    os.remove(filepath)
                    count += 1
        
        logging.info(f"Removidos {count} backups antigos")
    
    except Exception as e:
        logging.error(f"Erro ao limpar backups: {str(e)}")
        raise

def rebuild_indices():
    """Rebuild de índices fragmentados"""
    try:
        conn = conectar_banco()
        cursor = conn.cursor()
        
        # Identifica índices fragmentados
        cursor.execute("""
            SELECT 
                index_name,
                table_name,
                blevel,
                leaf_blocks,
                clustering_factor
            FROM user_indexes
            WHERE status = 'VALID'
            AND blevel > 4
        """)
        
        indices = cursor.fetchall()
        count = 0
        
        for idx in indices:
            try:
                logging.info(f"Rebuilding índice {idx[0]}...")
                cursor.execute(f"ALTER INDEX {idx[0]} REBUILD")
                count += 1
            except Exception as e:
                logging.error(f"Erro ao rebuild índice {idx[0]}: {str(e)}")
        
        conn.commit()
        logging.info(f"Rebuild concluído em {count} índices")
    
    except Exception as e:
        logging.error(f"Erro no rebuild de índices: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()

def atualizar_estatisticas():
    """Atualiza estatísticas do banco"""
    try:
        conn = conectar_banco()
        cursor = conn.cursor()
        
        # Lista de tabelas principais
        tabelas = [
            'DISTRIBUIDORAS',
            'COMPONENTES_TARIFARIOS',
            'SUBGRUPOS_TARIFARIOS',
            'MODALIDADES_TARIFARIAS',
            'CLASSES_CONSUMIDOR',
            'TARIFAS'
        ]
        
        for tabela in tabelas:
            try:
                logging.info(f"Atualizando estatísticas da tabela {tabela}...")
                cursor.execute(f"""
                    BEGIN
                        DBMS_STATS.GATHER_TABLE_STATS(
                            ownname => USER,
                            tabname => '{tabela}',
                            estimate_percent => DBMS_STATS.AUTO_SAMPLE_SIZE,
                            method_opt => 'FOR ALL COLUMNS SIZE AUTO',
                            cascade => TRUE
                        );
                    END;
                """)
            except Exception as e:
                logging.error(f"Erro ao atualizar estatísticas de {tabela}: {str(e)}")
        
        logging.info("Atualização de estatísticas concluída")
    
    except Exception as e:
        logging.error(f"Erro na atualização de estatísticas: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()

def refresh_materialized_views():
    """Atualiza materialized views"""
    try:
        conn = conectar_banco()
        cursor = conn.cursor()
        
        # Lista MVs
        cursor.execute("SELECT mview_name FROM user_mviews")
        mvs = cursor.fetchall()
        
        for mv in mvs:
            try:
                logging.info(f"Atualizando MV {mv[0]}...")
                cursor.execute(f"""
                    BEGIN
                        DBMS_MVIEW.REFRESH('{mv[0]}', method => 'C');
                    END;
                """)
            except Exception as e:
                logging.error(f"Erro ao atualizar MV {mv[0]}: {str(e)}")
        
        conn.commit()
        logging.info("Refresh de MVs concluído")
    
    except Exception as e:
        logging.error(f"Erro no refresh de MVs: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()

def executar_manutencao():
    """Executa rotina completa de manutenção"""
    try:
        logging.info("Iniciando manutenção do banco...")
        
        # Backup
        executar_backup()
        limpar_backups_antigos()
        
        # Manutenção
        rebuild_indices()
        atualizar_estatisticas()
        refresh_materialized_views()
        
        logging.info("Manutenção concluída com sucesso")
    
    except Exception as e:
        logging.error(f"Erro na manutenção: {str(e)}")
        raise

if __name__ == "__main__":
    executar_manutencao()
