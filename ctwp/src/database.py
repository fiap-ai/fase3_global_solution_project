#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de conexão com banco de dados Oracle
Autor: Gabriel Mule (RM560586)
Data: 25/11/2023
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import oracledb
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# Configura logging mais detalhado
logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger('oracledb').setLevel(logging.DEBUG)

class OracleConnection:
    """Gerencia conexão com Oracle"""
    
    def __init__(self):
        """Inicializa conexão"""
        logging.debug("Iniciando configuração da conexão Oracle")
        
        try:
            # Carrega variáveis de ambiente
            logging.debug("Carregando variáveis de ambiente")
            load_dotenv()
            logging.debug("Variáveis de ambiente carregadas")
            
            self.user = os.getenv('DB_USER')
            self.password = os.getenv('DB_PASSWORD')
            self.dsn = os.getenv('DB_DSN')
            self.oracle_client_path = os.getenv('ORACLE_CLIENT_PATH')
            
            logging.debug(f"Credenciais carregadas - User: {self.user}, DSN: {self.dsn}")
            
            # Inicializa conexão como None e modo offline como False
            self.connection = None
            self._offline_mode = False
            
            # Verifica credenciais
            if not all([self.user, self.password, self.dsn]):
                logging.warning("Credenciais incompletas")
                self._offline_mode = True
                return
            
            # Configura cliente Oracle
            if self.oracle_client_path:
                try:
                    logging.debug(f"Inicializando cliente Oracle em: {self.oracle_client_path}")
                    oracledb.init_oracle_client(lib_dir=self.oracle_client_path)
                    logging.debug("Cliente Oracle inicializado")
                except Exception as e:
                    logging.error(f"Erro ao inicializar cliente Oracle: {str(e)}")
                    self._offline_mode = True
                    return
            
            # Testa conexão inicial
            if not self.test_connection():
                logging.warning("Teste de conexão falhou")
                self._offline_mode = True
            
        except Exception as e:
            logging.error(f"Erro na inicialização: {str(e)}")
            self._offline_mode = True
    
    def test_connection(self) -> bool:
        """Testa conexão com o banco"""
        if not all([self.user, self.password, self.dsn]):
            logging.warning("Credenciais incompletas")
            self._offline_mode = True  # Ativa modo offline
            return False
            
        try:
            # Tenta uma conexão de teste
            with oracledb.connect(
                user=self.user,
                password=self.password,
                dsn=self.dsn
            ) as test_connection:
                cursor = test_connection.cursor()
                cursor.execute("SELECT SYSDATE FROM DUAL")
                cursor.fetchone()
                cursor.close()
            
            logging.info("Teste de conexão bem sucedido")
            return True
            
        except Exception as e:
            logging.error(f"Falha no teste de conexão: {str(e)}")
            self._offline_mode = True  # Ativa modo offline em caso de erro
            return False
    
    def connect(self) -> bool:
        """Estabelece conexão"""
        if self._offline_mode:
            return False
            
        logging.debug("Tentando estabelecer conexão")
        try:
            if not self.connection:
                logging.debug("Criando nova conexão")
                self.connection = oracledb.connect(
                    user=self.user,
                    password=self.password,
                    dsn=self.dsn
                )
                logging.info("Conexão estabelecida")
            return True
                
        except Exception as e:
            logging.error(f"Erro ao conectar: {str(e)}")
            self.connection = None
            self._offline_mode = True
            return False
    
    def disconnect(self) -> None:
        """Encerra conexão"""
        if self.connection:
            try:
                self.connection.close()
                logging.info("Conexão encerrada")
            except Exception as e:
                logging.error(f"Erro ao desconectar: {str(e)}")
            finally:
                self.connection = None
    
    def _generate_mock_data(self, days: int = 30) -> pd.DataFrame:
        """Gera dados mock para modo offline"""
        now = datetime.now()
        dates = [now - timedelta(hours=i) for i in range(days * 24)]
        sources = ['Rede', 'Solar', 'Bateria']
        base_values = {'Rede': 500.0, 'Solar': 250.0, 'Bateria': 100.0}
        
        data = []
        for dt in dates:
            hour = dt.hour
            # Adiciona variação por hora do dia
            hour_factor = 1.0 + np.sin(hour * np.pi / 12) * 0.5  # Pico ao meio-dia
            
            for source in sources:
                base = base_values[source]
                # Adiciona variação aleatória
                value = base * hour_factor * (1 + np.random.normal(0, 0.1))
                # Solar só produz durante o dia
                if source == 'Solar' and (hour < 6 or hour > 18):
                    value *= 0.1
                
                data.append({
                    'source': source,
                    'value': value,
                    'timestamp': dt,
                    'cost': value * 0.5,
                    'equipment': f'EQ_{source.upper()}_01'
                })
        
        return pd.DataFrame(data)
    
    def execute_query(self, query: str, params: Dict = None) -> pd.DataFrame:
        """Executa query e retorna DataFrame"""
        if self._offline_mode:
            logging.warning("Operação ignorada - modo offline")
            return pd.DataFrame()
            
        cursor = None
        try:
            if not self.connect():
                return pd.DataFrame()
                
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            columns = [desc[0].lower() for desc in cursor.description]
            data = cursor.fetchall()
            return pd.DataFrame(data, columns=columns)
            
        except Exception as e:
            logging.error(f"Erro na query: {str(e)}")
            return pd.DataFrame()
            
        finally:
            if cursor:
                cursor.close()
    
    def execute_dml(self, statement: str, params: Dict = None) -> bool:
        """Executa DML (insert, update, delete)"""
        if self._offline_mode:
            logging.warning("Operação ignorada - modo offline")
            return False
            
        cursor = None
        try:
            if not self.connect():
                return False
                
            cursor = self.connection.cursor()
            if params:
                cursor.execute(statement, params)
            else:
                cursor.execute(statement)
            
            self.connection.commit()
            return True
            
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            logging.error(f"Erro no DML: {str(e)}")
            return False
            
        finally:
            if cursor:
                cursor.close()
    
    def get_consumption_history(self, days: int = 30) -> pd.DataFrame:
        """Obtém histórico de consumo"""
        if self._offline_mode:
            return self._generate_mock_data(days)
            
        query = """
        SELECT 
            source,
            consumption as value,
            timestamp,
            cost,
            equipment
        FROM consumption_history 
        WHERE timestamp >= SYSDATE - :days 
        ORDER BY timestamp DESC
        """
        
        df = self.execute_query(query, {'days': days})
        if df.empty:
            return self._generate_mock_data(days)
            
        return df
    
    def get_current_tariffs(self) -> pd.DataFrame:
        """Obtém tarifas atuais"""
        if self._offline_mode:
            # Dados mock de tarifas
            return pd.DataFrame({
                'source': ['Energia', 'Transmissão', 'Distribuição', 'Encargos'],
                'value': [0.35, 0.15, 0.10, 0.05],
                'distribuidora': ['ENEL'] * 4,
                'unidade': ['R$/kWh'] * 4
            })
        
        query = """
        SELECT 
            componente as source,
            valor as value,
            distribuidora,
            unidade
        FROM tarifas_vigentes
        """
        
        df = self.execute_query(query)
        if df.empty:
            return pd.DataFrame({
                'source': ['Energia', 'Transmissão', 'Distribuição', 'Encargos'],
                'value': [0.35, 0.15, 0.10, 0.05],
                'distribuidora': ['ENEL'] * 4,
                'unidade': ['R$/kWh'] * 4
            })
        
        return df
    
    def get_efficiency_metrics(self) -> pd.DataFrame:
        """Obtém métricas de eficiência"""
        if self._offline_mode:
            # Gera dados mock de eficiência
            now = datetime.now()
            dates = [now - timedelta(days=i*30) for i in range(12)]
            
            base = 70  # Eficiência base de 70%
            trend = np.linspace(0, 15, len(dates))  # Tendência de melhoria
            noise = np.random.normal(0, 2, len(dates))  # Variação mensal
            values = base + trend + noise
            values = np.clip(values, 0, 100)  # Limita entre 0 e 100%
            
            return pd.DataFrame({
                'mes': dates,
                'valor_medio': values,
                'variacao_anterior': np.diff(values, prepend=values[0]),
                'ranking_eficiencia': np.random.randint(1, 100, len(dates))
            })
        
        query = """
        SELECT 
            mes,
            valor_medio,
            variacao_anterior,
            ranking_eficiencia
        FROM metricas_eficiencia
        ORDER BY mes DESC
        """
        
        df = self.execute_query(query)
        if df.empty:
            return self.get_efficiency_metrics()  # Retorna dados mock
        
        return df
    
    def get_renewable_sources(self) -> pd.DataFrame:
        """Obtém dados de fontes renováveis"""
        if self._offline_mode:
            # Dados mock de fontes renováveis
            now = datetime.now()
            dates = [now - timedelta(days=i*30) for i in range(12)]
            sources = ['Solar', 'Eólica', 'Biomassa']
            
            data = []
            for dt in dates:
                for source in sources:
                    base = 100.0 if source == 'Solar' else (
                        75.0 if source == 'Eólica' else 50.0
                    )
                    value = base * (1 + np.random.normal(0, 0.1))
                    data.append({
                        'source': source,
                        'value': value,
                        'mes': dt
                    })
            
            return pd.DataFrame(data)
        
        query = """
        SELECT 
            componente as source,
            valor_total as value,
            mes
        FROM fontes_renovaveis
        ORDER BY mes DESC
        """
        
        df = self.execute_query(query)
        if df.empty:
            return self.get_renewable_sources()  # Retorna dados mock
        
        return df
    
    def save_consumption(self, data: Dict[str, Any]) -> bool:
        """Salva leitura de consumo"""
        if self._offline_mode:
            logging.info("Dados salvos em modo offline (simulado)")
            return True
            
        statement = """
        INSERT INTO consumption_history (
            id,
            timestamp,
            consumption,
            cost,
            source,
            equipment
        ) VALUES (
            seq_consumption.NEXTVAL,
            :timestamp,
            :consumption,
            :cost,
            :source,
            :equipment
        )
        """
        
        return self.execute_dml(statement, data)
    
    def save_optimization(self, data: Dict[str, Any]) -> bool:
        """Salva resultado de otimização"""
        if self._offline_mode:
            logging.info("Otimização salva em modo offline (simulado)")
            return True
            
        statement = """
        INSERT INTO optimization_results (
            id,
            timestamp,
            tipo,
            valor_anterior,
            valor_otimizado,
            economia_estimada,
            recomendacao
        ) VALUES (
            seq_optimization.NEXTVAL,
            :timestamp,
            :tipo,
            :valor_anterior,
            :valor_otimizado,
            :economia_estimada,
            :recomendacao
        )
        """
        
        return self.execute_dml(statement, data)

