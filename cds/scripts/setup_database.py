#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para configuração inicial do banco de dados
Autor: Gabriel Mule (RM560586)
Data: 25/11/2023
"""

import os
import logging
import oracledb
from dotenv import load_dotenv
import importlib.util

def setup_logging():
    """Configura logging"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def read_sql_file(filename):
    """Lê arquivo SQL"""
    with open(filename, 'r') as file:
        return file.read()

def execute_sql_script(connection, sql_script, ignore_errors=False):
    """Executa script SQL"""
    cursor = None
    try:
        cursor = connection.cursor()
        
        # Divide o script em comandos individuais
        commands = sql_script.split(';')
        
        for command in commands:
            # Remove espaços em branco e pula comandos vazios
            command = command.strip()
            if command:
                try:
                    cursor.execute(command)
                    logging.info(f"Comando executado com sucesso: {command[:50]}...")
                except Exception as e:
                    if ignore_errors:
                        logging.warning(f"Ignorando erro no comando: {str(e)}")
                        logging.warning(f"Comando com erro: {command}")
                    else:
                        logging.error(f"Erro ao executar comando: {str(e)}")
                        logging.error(f"Comando com erro: {command}")
                        raise
        
        connection.commit()
        logging.info("Todos os comandos foram executados com sucesso")
        
    except Exception as e:
        if connection:
            connection.rollback()
        if not ignore_errors:
            logging.error(f"Erro ao executar script: {str(e)}")
            raise
        
    finally:
        if cursor:
            cursor.close()

def main():
    """Função principal"""
    setup_logging()
    logging.info("Iniciando configuração do banco de dados")
    
    connection = None
    try:
        # Carrega variáveis de ambiente
        load_dotenv()
        
        # Configura cliente Oracle
        oracle_client_path = os.getenv('ORACLE_CLIENT_PATH')
        if oracle_client_path:
            oracledb.init_oracle_client(lib_dir=oracle_client_path)
        
        # Conecta ao banco
        connection = oracledb.connect(
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            dsn=os.getenv('DB_DSN')
        )
        logging.info("Conectado ao banco de dados")
        
        # Executa scripts SQL
        scripts = [
            ('cleanup_tables.sql', True),    # True = ignora erros
            ('create_tables.sql', False)     # False = não ignora erros
        ]
        
        for script, ignore_errors in scripts:
            logging.info(f"Executando script: {script}")
            script_path = os.path.join(os.path.dirname(__file__), script)
            sql_content = read_sql_file(script_path)
            execute_sql_script(connection, sql_content, ignore_errors)
            logging.info(f"Script {script} executado com sucesso")
        
        # Fecha conexão antes de executar o script de população
        if connection:
            connection.close()
            connection = None
        
        # Importa e executa script de população de dados
        logging.info("Executando script de população de dados")
        populate_script = os.path.join(os.path.dirname(__file__), 'populate_test_data.py')
        spec = importlib.util.spec_from_file_location("populate_test_data", populate_script)
        populate_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(populate_module)
        populate_module.main()
        
        logging.info("Configuração do banco concluída com sucesso")
        
    except Exception as e:
        logging.error(f"Erro na configuração do banco: {str(e)}")
        raise
        
    finally:
        if connection:
            connection.close()
            logging.info("Conexão encerrada")

if __name__ == '__main__':
    main()
