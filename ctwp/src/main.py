#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sistema de gerenciamento energético
Autor: Gabriel Mule (RM560586)
Data: 25/11/2023
"""

import sys
import logging
import os
from pathlib import Path

# Configuração de logging
log_file = 'energy_system.log'
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# Cria diretórios necessários
for directory in ['reports', 'temp']:
    Path(directory).mkdir(exist_ok=True)

logging.debug("Iniciando configuração do matplotlib")
try:
    import matplotlib
    logging.debug("Matplotlib importado com sucesso")
    matplotlib.use('AGG')
    logging.debug("Backend AGG configurado")
    matplotlib.interactive(False)
    logging.debug("Modo interativo desativado")
except Exception as e:
    logging.error(f"Erro ao configurar matplotlib: {str(e)}")
    raise

logging.debug("Importando módulos")
try:
    from database import OracleConnection
    from services.monitoring import EnergyMonitor
    from services.optimization import EnergyOptimizer
    from services.reporting import ReportGenerator
    from ui.main_window import MainWindow
    logging.debug("Módulos importados com sucesso")
except Exception as e:
    logging.error(f"Erro ao importar módulos: {str(e)}")
    raise

def setup_database():
    """Configura conexão com banco de dados"""
    try:
        logging.debug("Iniciando configuração da conexão Oracle")
        
        # Verifica variáveis de ambiente necessárias
        required_vars = ['ORACLE_HOME', 'ORACLE_USER', 'ORACLE_PASS', 'ORACLE_DSN']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logging.warning(f"Variáveis de ambiente ausentes: {', '.join(missing_vars)}")
            logging.info("Sistema iniciará em modo offline")
            return None
        
        # Inicializa conexão
        logging.debug(f"Inicializando cliente Oracle em: {os.getenv('ORACLE_HOME')}")
        db = OracleConnection()
        logging.debug("Cliente Oracle inicializado")
        
        # Testa conexão
        if db.test_connection():
            logging.info("Conexão estabelecida")
            return db
        else:
            logging.warning("Teste de conexão falhou")
            return None
            
    except Exception as e:
        logging.error(f"Erro ao configurar banco de dados: {str(e)}")
        return None

def main():
    """Função principal"""
    try:
        # Configura banco de dados
        db = setup_database()
        
        # Inicializa serviços
        logging.debug("Inicializando serviços")
        monitor = EnergyMonitor(db)
        logging.info("Monitor inicializado")
        optimizer = EnergyOptimizer(db)
        logging.info("Otimizador inicializado")
        reporter = ReportGenerator(monitor)  # Passa o monitor ao invés do db
        logging.info("Gerador de relatórios inicializado")
        
        # Inicializa interface
        logging.debug("Inicializando interface gráfica")
        window = MainWindow(monitor, optimizer, reporter)
        logging.info("Interface inicializada")
        
    except Exception as e:
        logging.error(f"Erro ao inicializar sistema: {str(e)}", exc_info=True)
        raise

if __name__ == '__main__':
    try:
        # Adiciona diretório src ao PYTHONPATH
        src_path = str(Path(__file__).parent)
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        logging.debug("Diretório src adicionado ao PYTHONPATH")
        
        # Executa sistema
        main()
        
    except KeyboardInterrupt:
        logging.info("Sistema encerrado pelo usuário")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Erro fatal: {str(e)}", exc_info=True)
        sys.exit(1)
