#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para popular banco com dados de teste
Autor: Gabriel Mule (RM560586)
Data: 25/11/2023
"""

import os
import logging
from datetime import datetime, timedelta
import random
import oracledb
from dotenv import load_dotenv

def setup_logging():
    """Configura logging"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def insert_consumption_history(cursor):
    """Insere dados de consumo"""
    sources = ['Solar', 'Eólica', 'Rede', 'Biomassa']
    equipments = ['Painel Solar A1', 'Turbina E1', 'Medidor Principal', 'Gerador B1']
    
    for i in range(30):  # 30 dias
        timestamp = datetime.now() - timedelta(days=i)
        
        for source, equipment in zip(sources, equipments):
            cursor.execute("""
                INSERT INTO consumption_history (
                    id, timestamp, consumption, cost, source, equipment
                ) VALUES (
                    seq_consumption.NEXTVAL, :1, :2, :3, :4, :5
                )
            """, [
                timestamp,
                random.uniform(100, 500),  # consumo entre 100 e 500 kWh
                random.uniform(50, 250),   # custo entre 50 e 250 reais
                source,
                equipment
            ])
    logging.info(f"Inseridos {30 * len(sources)} registros de consumo")

def insert_tariffs(cursor):
    """Insere tarifas vigentes"""
    tarifas = [
        ('ENEL', 'Consumo', 'kWh', 0.65),
        ('ENEL', 'Demanda', 'kW', 25.00),
        ('ENEL', 'TUSD', 'kWh', 0.35),
        ('CPFL', 'Consumo', 'kWh', 0.68),
        ('CPFL', 'Demanda', 'kW', 26.50)
    ]
    
    for distribuidora, componente, unidade, valor in tarifas:
        cursor.execute("""
            INSERT INTO tarifas_vigentes (
                id, distribuidora, componente, unidade, valor, data_vigencia
            ) VALUES (
                seq_tarifa_vigente.NEXTVAL, :1, :2, :3, :4, SYSDATE
            )
        """, [distribuidora, componente, unidade, valor])
    logging.info(f"Inseridas {len(tarifas)} tarifas")

def insert_efficiency_metrics(cursor):
    """Insere métricas de eficiência"""
    valor_anterior = 100
    
    for i in range(12):  # 12 meses
        mes = datetime.now() - timedelta(days=30*i)
        valor_atual = valor_anterior * (1 + random.uniform(-0.1, 0.1))
        variacao = ((valor_atual - valor_anterior) / valor_anterior) * 100
        
        cursor.execute("""
            INSERT INTO metricas_eficiencia (
                id, mes, valor_medio, variacao_anterior, ranking_eficiencia
            ) VALUES (
                seq_metrica.NEXTVAL, :1, :2, :3, :4
            )
        """, [mes, valor_atual, variacao, random.randint(1, 100)])
        
        valor_anterior = valor_atual
    logging.info("Inseridas 12 métricas de eficiência")

def insert_renewable_sources(cursor):
    """Insere dados de fontes renováveis"""
    fontes = {
        'Solar': 1000,
        'Eólica': 800,
        'Biomassa': 500,
        'PCH': 300
    }
    
    for i in range(12):  # 12 meses
        mes = datetime.now() - timedelta(days=30*i)
        
        for fonte, base_valor in fontes.items():
            valor = base_valor * (1 + random.uniform(-0.2, 0.2))
            cursor.execute("""
                INSERT INTO fontes_renovaveis (
                    id, componente, valor_total, mes
                ) VALUES (
                    seq_renovavel.NEXTVAL, :1, :2, :3
                )
            """, [fonte, valor, mes])
    logging.info(f"Inseridos {12 * len(fontes)} registros de fontes renováveis")

def insert_optimization_results(cursor):
    """Insere resultados de otimização"""
    resultados = [
        ('Consumo', 1500, 1200, 300, 'Ajuste no sistema de refrigeração pode economizar até 20% no consumo'),
        ('Demanda', 500, 450, 50, 'Redistribuição de cargas pode reduzir demanda em horário de ponta')
    ]
    
    for tipo, valor_anterior, valor_otimizado, economia, recomendacao in resultados:
        cursor.execute("""
            INSERT INTO optimization_results (
                id, timestamp, tipo, valor_anterior, valor_otimizado, 
                economia_estimada, recomendacao
            ) VALUES (
                seq_optimization.NEXTVAL, SYSDATE - :1, :2, :3, :4, :5, :6
            )
        """, [random.randint(1, 5), tipo, valor_anterior, valor_otimizado, 
              economia, recomendacao])
    logging.info(f"Inseridos {len(resultados)} resultados de otimização")

def main():
    """Função principal"""
    setup_logging()
    logging.info("Iniciando população de dados de teste")
    
    try:
        # Carrega variáveis de ambiente
        load_dotenv()
        
        # Conecta ao banco
        connection = oracledb.connect(
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            dsn=os.getenv('DB_DSN')
        )
        logging.info("Conectado ao banco de dados")
        
        cursor = connection.cursor()
        
        # Limpa dados existentes
        tables = [
            'consumption_history',
            'tarifas_vigentes',
            'metricas_eficiencia',
            'fontes_renovaveis',
            'optimization_results'
        ]
        
        for table in tables:
            cursor.execute(f"DELETE FROM {table}")
        logging.info("Dados existentes removidos")
        
        # Insere novos dados
        insert_consumption_history(cursor)
        insert_tariffs(cursor)
        insert_efficiency_metrics(cursor)
        insert_renewable_sources(cursor)
        insert_optimization_results(cursor)
        
        connection.commit()
        logging.info("Dados de teste inseridos com sucesso")
        
    except Exception as e:
        logging.error(f"Erro ao popular dados: {str(e)}")
        if 'connection' in locals():
            connection.rollback()
        raise
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
            logging.info("Conexão encerrada")

if __name__ == '__main__':
    main()
