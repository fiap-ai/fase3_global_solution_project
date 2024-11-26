#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para execução de testes
Autor: Gabriel Mule (RM560586)
Data: 25/11/2023
"""

import sys
import pytest
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tests.log'),
        logging.StreamHandler()
    ]
)

def setup_test_tables(connection):
    """Cria tabelas de teste"""
    try:
        cursor = connection.cursor()
        
        # Cria tabelas com sufixo _test
        cursor.execute("""
            CREATE TABLE tarifas_test AS 
            SELECT * FROM tarifas WHERE 1=0
        """)
        
        cursor.execute("""
            CREATE TABLE distribuidoras_test AS 
            SELECT * FROM distribuidoras WHERE 1=0
        """)
        
        cursor.execute("""
            CREATE TABLE componentes_tarifarios_test AS 
            SELECT * FROM componentes_tarifarios WHERE 1=0
        """)
        
        # Insere dados de teste
        cursor.execute("""
            INSERT INTO tarifas_test 
            SELECT * FROM tarifas 
            WHERE ROWNUM <= 1000
        """)
        
        cursor.execute("""
            INSERT INTO distribuidoras_test 
            SELECT * FROM distribuidoras
        """)
        
        cursor.execute("""
            INSERT INTO componentes_tarifarios_test 
            SELECT * FROM componentes_tarifarios
        """)
        
        connection.commit()
        logging.info("Tabelas de teste criadas com sucesso")
        return True
        
    except Exception as e:
        connection.rollback()
        logging.error(f"Erro ao criar tabelas de teste: {str(e)}")
        return False

def cleanup_test_tables(connection):
    """Remove tabelas de teste"""
    try:
        cursor = connection.cursor()
        
        # Remove tabelas de teste
        tables = [
            'tarifas_test',
            'distribuidoras_test',
            'componentes_tarifarios_test'
        ]
        
        for table in tables:
            cursor.execute(f"DROP TABLE {table}")
        
        connection.commit()
        logging.info("Tabelas de teste removidas com sucesso")
        return True
        
    except Exception as e:
        connection.rollback()
        logging.error(f"Erro ao remover tabelas de teste: {str(e)}")
        return False

def run_tests():
    """Executa todos os testes"""
    try:
        # Carrega variáveis de ambiente
        load_dotenv()
        
        # Adiciona src ao PYTHONPATH
        src_path = Path(__file__).parent / 'src'
        sys.path.insert(0, str(src_path))
        
        # Cria diretório de relatórios se não existir
        reports_dir = Path('reports')
        reports_dir.mkdir(exist_ok=True)
        
        # Argumentos do pytest
        args = [
            'tests',                    # Diretório de testes
            '-v',                       # Verbose
            '--cov=src',               # Cobertura do código
            '--cov-report=html',       # Relatório HTML
            '--cov-report=term',       # Relatório no terminal
            '-W', 'ignore::DeprecationWarning'  # Ignora warnings de depreciação
        ]
        
        # Executa testes
        start_time = datetime.now()
        result = pytest.main(args)
        end_time = datetime.now()
        
        # Gera relatório de execução
        duration = end_time - start_time
        
        with open('test_report.txt', 'w') as f:
            f.write(f"Relatório de Testes\n")
            f.write(f"==================\n\n")
            f.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Duração: {duration}\n")
            f.write(f"Resultado: {'Sucesso' if result == 0 else 'Falha'}\n\n")
        
        logging.info(f"Testes concluídos em {duration}")
        return result == 0
        
    except Exception as e:
        logging.error(f"Erro ao executar testes: {str(e)}")
        return False

def cleanup():
    """Limpa arquivos temporários"""
    try:
        # Lista de padrões de arquivos temporários
        temp_patterns = [
            '*.pyc',
            '__pycache__',
            '.pytest_cache',
            'temp_*.png'
        ]
        
        # Remove arquivos
        for pattern in temp_patterns:
            for file in Path('.').rglob(pattern):
                if file.is_file():
                    file.unlink()
                elif file.is_dir():
                    import shutil
                    shutil.rmtree(file)
        
        logging.info("Limpeza concluída")
        return True
        
    except Exception as e:
        logging.error(f"Erro na limpeza: {str(e)}")
        return False

if __name__ == "__main__":
    try:
        # Executa testes
        success = run_tests()
        
        # Limpa arquivos temporários
        cleanup()
        
        # Define código de saída
        sys.exit(0 if success else 1)
        
    except Exception as e:
        logging.error(f"Erro fatal: {str(e)}")
        sys.exit(1)
