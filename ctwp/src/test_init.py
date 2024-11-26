#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para testar apenas a inicialização do cliente Oracle
"""

import os
import logging
import oracledb
from dotenv import load_dotenv

logging.basicConfig(level=logging.DEBUG)

def test_init():
    """Testa apenas a inicialização do cliente"""
    try:
        # Carrega variáveis de ambiente
        load_dotenv()
        oracle_client_path = os.getenv('ORACLE_CLIENT_PATH')
        logging.debug(f"ORACLE_CLIENT_PATH={oracle_client_path}")
        
        # Verifica diretório
        if os.path.exists(oracle_client_path):
            files = os.listdir(oracle_client_path)
            logging.debug(f"Arquivos no diretório: {files}")
        else:
            logging.error(f"Diretório não existe: {oracle_client_path}")
            return
        
        # Tenta inicializar
        logging.debug("Tentando inicializar cliente Oracle...")
        oracledb.init_oracle_client(lib_dir=oracle_client_path)
        logging.debug("Cliente Oracle inicializado com sucesso")
        
        # Tenta obter versão
        version = oracledb.clientversion()
        logging.debug(f"Versão do cliente: {version}")
        
    except Exception as e:
        logging.error(f"Erro: {str(e)}", exc_info=True)

if __name__ == '__main__':
    test_init()
