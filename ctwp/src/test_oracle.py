#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para testar conexão Oracle
Autor: Gabriel Mule (RM560586)
Data: 25/11/2024
"""

import os
import logging
import unittest
from datetime import datetime
import pandas as pd
import numpy as np
import oracledb
from dotenv import load_dotenv
from database import OracleConnection

# Configura logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TestOracleConnection(unittest.TestCase):
    """Testes para OracleConnection"""
    
    @classmethod
    def setUpClass(cls):
        """Configuração inicial dos testes"""
        load_dotenv()
        cls.oracle_client_path = os.getenv('ORACLE_CLIENT_PATH')
        cls.user = os.getenv('DB_USER')
        cls.password = os.getenv('DB_PASSWORD')
        cls.dsn = os.getenv('DB_DSN')
    
    def setUp(self):
        """Configuração para cada teste"""
        self.db = OracleConnection()
    
    def tearDown(self):
        """Limpeza após cada teste"""
        if hasattr(self, 'db') and self.db.connection:
            self.db.disconnect()
    
    def test_instant_client_initialization(self):
        """Testa inicialização do instant client"""
        if not self.oracle_client_path:
            self.skipTest("ORACLE_CLIENT_PATH não configurado")
            
        try:
            oracledb.init_oracle_client(lib_dir=self.oracle_client_path)
            # Se não levantar exceção, considera sucesso
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Falha ao inicializar cliente Oracle: {str(e)}")
    
    def test_connection_with_valid_credentials(self):
        """Testa conexão com credenciais válidas"""
        if not all([self.user, self.password, self.dsn]):
            self.skipTest("Credenciais não configuradas")
            
        self.assertTrue(self.db.test_connection())
    
    def test_connection_with_invalid_credentials(self):
        """Testa conexão com credenciais inválidas"""
        db = OracleConnection()
        db.user = "invalid_user"
        db.password = "invalid_pass"
        db.dsn = "invalid_dsn"
        
        # Força verificação de conexão para ativar modo offline
        db.test_connection()
        self.assertTrue(db._offline_mode)
    
    def test_offline_mode_activation(self):
        """Testa ativação do modo offline"""
        db = OracleConnection()
        db.user = None
        
        # Força verificação de conexão para ativar modo offline
        db.test_connection()
        self.assertTrue(db._offline_mode)
        self.assertFalse(db.connect())
    
    def test_mock_data_generation(self):
        """Testa geração de dados mock"""
        db = OracleConnection()
        db._offline_mode = True
        
        # Testa dados de consumo
        consumption = db.get_consumption_history(days=30)
        self.assertIsInstance(consumption, pd.DataFrame)
        self.assertFalse(consumption.empty)
        self.assertTrue(all(col in consumption.columns 
                          for col in ['source', 'value', 'timestamp']))
        
        # Testa dados de tarifas
        tariffs = db.get_current_tariffs()
        self.assertIsInstance(tariffs, pd.DataFrame)
        self.assertFalse(tariffs.empty)
        self.assertTrue(all(col in tariffs.columns 
                          for col in ['source', 'value']))
        
        # Testa métricas de eficiência
        metrics = db.get_efficiency_metrics()
        self.assertIsInstance(metrics, pd.DataFrame)
        self.assertFalse(metrics.empty)
        self.assertTrue(all(col in metrics.columns 
                          for col in ['mes', 'valor_medio']))
        
        # Testa dados de fontes renováveis
        renewables = db.get_renewable_sources()
        self.assertIsInstance(renewables, pd.DataFrame)
        self.assertFalse(renewables.empty)
        self.assertTrue(all(col in renewables.columns 
                          for col in ['source', 'value']))
    
    def test_mock_data_consistency(self):
        """Testa consistência dos dados mock"""
        db = OracleConnection()
        db._offline_mode = True
        
        # Testa consistência temporal
        consumption = db.get_consumption_history(days=30)
        self.assertEqual(len(consumption['timestamp'].unique()), 30 * 24)
        
        # Testa valores dentro de limites esperados
        self.assertTrue(all(consumption['value'] >= 0))
        self.assertTrue(all(consumption['value'] <= 1000))
        
        # Testa fontes de energia
        sources = consumption['source'].unique()
        self.assertEqual(set(sources), {'Rede', 'Solar', 'Bateria'})
        
        # Testa variação diurna da energia solar
        solar_data = consumption[consumption['source'] == 'Solar']
        day_hours = solar_data[solar_data['timestamp'].dt.hour.between(6, 18)]
        night_hours = solar_data[~solar_data['timestamp'].dt.hour.between(6, 18)]
        
        self.assertTrue(day_hours['value'].mean() > night_hours['value'].mean())
    
    def test_dml_operations_offline(self):
        """Testa operações DML em modo offline"""
        db = OracleConnection()
        db._offline_mode = True
        
        # Testa inserção
        data = {
            'timestamp': datetime.now(),
            'consumption': 100.0,
            'cost': 50.0,
            'source': 'Rede',
            'equipment': 'EQ_01'
        }
        
        self.assertTrue(db.save_consumption(data))
        
        # Testa otimização
        data = {
            'timestamp': datetime.now(),
            'tipo': 'Consumo',
            'valor_anterior': 100.0,
            'valor_otimizado': 90.0,
            'economia_estimada': 10.0,
            'recomendacao': 'Reduzir consumo'
        }
        
        self.assertTrue(db.save_optimization(data))
    
    def test_data_format_consistency(self):
        """Testa consistência do formato dos dados"""
        db = OracleConnection()
        db._offline_mode = True
        
        # Testa formato dos dados de consumo
        consumption = db.get_consumption_history()
        self.assertTrue(isinstance(consumption['timestamp'].iloc[0], datetime))
        self.assertTrue(isinstance(consumption['value'].iloc[0], (int, float)))
        self.assertTrue(isinstance(consumption['source'].iloc[0], str))
        
        # Testa formato das métricas
        metrics = db.get_efficiency_metrics()
        self.assertTrue(isinstance(metrics['valor_medio'].iloc[0], (int, float)))
        self.assertTrue(0 <= metrics['valor_medio'].iloc[0] <= 100)
        
        # Testa formato das tarifas
        tariffs = db.get_current_tariffs()
        self.assertTrue(isinstance(tariffs['value'].iloc[0], (int, float)))
        self.assertTrue(tariffs['value'].iloc[0] > 0)

if __name__ == '__main__':
    unittest.main()
