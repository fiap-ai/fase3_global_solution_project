#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Serviço de monitoramento de consumo energético
Autor: Gabriel Mule (RM560586)
Data: 25/11/2024
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from queue import Queue
from threading import Lock, Thread
import time

class SensorReader:
    """Leitor de sensores"""
    
    def __init__(self):
        """Inicializa leitor"""
        self.running = False
        self.data_queue = Queue()
        self.lock = Lock()
        self.last_reading = None
        self.error_count = 0
        self.max_errors = 3
        logging.info("Leitor de sensores inicializado")
        # Inicia leitura automaticamente
        self.start()
    
    def start(self):
        """Inicia leitura"""
        if not self.running:
            self.running = True
            self.thread = Thread(target=self._read_loop)
            self.thread.daemon = True
            self.thread.start()
            logging.info("Leitura de sensores iniciada")
    
    def stop(self):
        """Para leitura"""
        self.running = False
        if hasattr(self, 'thread'):
            self.thread.join()
        logging.info("Leitura de sensores parada")
    
    def _read_loop(self):
        """Loop de leitura"""
        while self.running:
            try:
                # TODO: Implementar leitura real dos sensores
                # Por enquanto usa simulação
                reading = self._simulate_reading()
                
                with self.lock:
                    self.last_reading = reading
                    self.data_queue.put(reading)
                    self.error_count = 0
                
                time.sleep(1)  # 1 leitura por segundo
                
            except Exception as e:
                logging.error(f"Erro na leitura: {str(e)}")
                self.error_count += 1
                if self.error_count >= self.max_errors:
                    logging.error("Muitos erros consecutivos, parando leitura")
                    self.running = False
    
    def _simulate_reading(self) -> Dict[str, Any]:
        """Simula leitura dos sensores"""
        now = datetime.now()
        return {
            'timestamp': now,
            'consumption': np.random.normal(100, 10),
            'voltage': np.random.normal(220, 5),
            'current': np.random.normal(10, 1),
            'power_factor': np.random.normal(0.92, 0.02),
            'temperature': np.random.normal(25, 2)
        }
    
    def get_last_reading(self) -> Optional[Dict[str, Any]]:
        """Obtém última leitura"""
        with self.lock:
            return self.last_reading

class EnergyMonitor:
    """Monitora consumo e tarifas em tempo real"""
    
    def __init__(self, db_connection):
        """Inicializa monitor"""
        self.db = db_connection
        self.current_consumption = 0
        self.current_tariff = 0
        self.history = []
        self.valid_units = ['R$/kW', 'R$/MWh']
        self.sensor_reader = SensorReader()
        self.alert_thresholds = {
            'consumption': 150.0,  # kWh
            'voltage': 240.0,      # V
            'current': 15.0,       # A
            'power_factor': 0.85,  # min
            'temperature': 35.0    # °C
        }
        logging.info("Monitor inicializado")
    
    def check_alerts(self, reading: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Verifica alertas"""
        alerts = []
        
        if reading['consumption'] > self.alert_thresholds['consumption']:
            alerts.append({
                'type': 'consumption',
                'message': f"Consumo alto: {reading['consumption']:.2f} kWh",
                'severity': 'high'
            })
        
        if reading['voltage'] > self.alert_thresholds['voltage']:
            alerts.append({
                'type': 'voltage',
                'message': f"Tensão alta: {reading['voltage']:.2f} V",
                'severity': 'critical'
            })
        
        if reading['current'] > self.alert_thresholds['current']:
            alerts.append({
                'type': 'current',
                'message': f"Corrente alta: {reading['current']:.2f} A",
                'severity': 'critical'
            })
        
        if reading['power_factor'] < self.alert_thresholds['power_factor']:
            alerts.append({
                'type': 'power_factor',
                'message': f"Fator de potência baixo: {reading['power_factor']:.2f}",
                'severity': 'medium'
            })
        
        if reading['temperature'] > self.alert_thresholds['temperature']:
            alerts.append({
                'type': 'temperature',
                'message': f"Temperatura alta: {reading['temperature']:.2f} °C",
                'severity': 'high'
            })
        
        return alerts

    def get_mock_consumption_history(self, days: int = 30) -> pd.DataFrame:
        """Gera dados históricos mock"""
        now = datetime.now()
        data = []
        sources = ['Rede', 'Solar', 'Bateria']
        base_values = {'Rede': 70.0, 'Solar': 20.0, 'Bateria': 10.0}
        
        # Calcula número de horas baseado nos dias (permite frações de dia)
        hours = int(days * 24)
        
        for i in range(hours):  # Dados horários
            timestamp = now - timedelta(hours=i)
            for source in sources:
                base = base_values[source]
                value = base * (1 + np.random.normal(0, 0.1))
                data.append({
                    'timestamp': timestamp,
                    'source': source,
                    'value': value,
                    'cost': value * 0.5
                })
        
        return pd.DataFrame(data)
    
    def get_mock_tariffs(self) -> pd.DataFrame:
        """Gera dados de tarifa mock"""
        components = [
            ('Energia', 0.35, 'R$/kWh'),
            ('Transmissão', 0.15, 'R$/kWh'),
            ('Distribuição', 0.10, 'R$/kWh'),
            ('Encargos', 0.05, 'R$/kWh')
        ]
        
        data = []
        for name, value, unit in components:
            data.append({
                'componente': name,
                'valor': value * (1 + np.random.normal(0, 0.05)),
                'unidade': unit
            })
        
        return pd.DataFrame(data)
    
    def get_mock_efficiency_metrics(self) -> pd.DataFrame:
        """Gera métricas de eficiência mock"""
        now = datetime.now()
        data = []
        
        base_efficiency = 75.0  # Eficiência base de 75%
        trend = 0.1  # Tendência positiva
        
        for i in range(30):  # 30 dias de dados
            timestamp = now - timedelta(days=i)
            efficiency = base_efficiency * (1 + trend * i/30 + np.random.normal(0, 0.05))
            data.append({
                'timestamp': timestamp,
                'valor_medio': efficiency,
                'variacao_anterior': trend * 100,
                'ranking_eficiencia': 2
            })
        
        return pd.DataFrame(data)
    
    def get_mock_renewable_sources(self) -> pd.DataFrame:
        """Gera dados de fontes renováveis mock"""
        components = [
            ('PROINFA Solar', 300),
            ('PROINFA Eólica', 200),
            ('CDE Renováveis', 150),
            ('GD Solar', 250)
        ]
        
        data = []
        for name, value in components:
            data.append({
                'componente': name,
                'valor_total': value * (1 + np.random.normal(0, 0.1))
            })
        
        return pd.DataFrame(data)
    
    def get_current_consumption(self) -> Dict[str, Any]:
        """Obtém consumo atual"""
        try:
            # Obtém leitura dos sensores
            reading = self.sensor_reader.get_last_reading()
            if reading:
                self.current_consumption = reading['consumption']
            else:
                # Fallback para simulação se sensor não disponível
                self.current_consumption = np.random.normal(100, 10)
            
            # Obtém histórico mock (já que estamos em modo offline)
            history_df = self.get_mock_consumption_history()
            
            # Calcula consumo por fonte
            by_source = {
                'Rede': 0.7 * self.current_consumption,
                'Solar': 0.2 * self.current_consumption,
                'Bateria': 0.1 * self.current_consumption
            }
            
            # Prepara detalhes
            details = []
            now = datetime.now()
            sources = ['Rede', 'Solar', 'Bateria']
            base_values = {'Rede': 70.0, 'Solar': 20.0, 'Bateria': 10.0}
            
            for i in range(24):  # últimas 24 horas
                timestamp = now - timedelta(hours=i)
                for source in sources:
                    base = base_values[source]
                    value = base * (1 + np.random.normal(0, 0.1))
                    details.append({
                        'timestamp': timestamp,
                        'source': source,
                        'consumption': value,
                        'cost': value * 0.5
                    })
            
            # Verifica alertas
            alerts = []
            if reading:
                alerts = self.check_alerts(reading)
            
            # Retorna dados formatados
            return {
                'total': float(self.current_consumption),
                'by_source': by_source,
                'history': history_df.to_dict('records') if not history_df.empty else [],
                'details': details,
                'alerts': alerts,
                'sensor_data': reading
            }
            
        except Exception as e:
            logging.error(f"Erro ao obter consumo: {str(e)}", exc_info=True)
            # Retorna estrutura padrão em caso de erro
            return {
                'total': 0.0,
                'by_source': {},
                'history': [],
                'details': [],
                'alerts': [],
                'sensor_data': None
            }
    
    def get_current_tariffs(self) -> Dict[str, Any]:
        """Obtém tarifas atuais"""
        try:
            # Obtém tarifas (reais ou mock)
            if self.db is not None:
                try:
                    tariffs_df = self.db.get_current_tariffs()
                except Exception as e:
                    logging.warning(f"Erro ao obter tarifas do banco: {str(e)}")
                    tariffs_df = self.get_mock_tariffs()
            else:
                tariffs_df = self.get_mock_tariffs()
            
            # Calcula tarifa atual
            self.current_tariff = tariffs_df['valor'].mean()
            
            # Prepara histórico
            history = []
            now = datetime.now()
            for i in range(24):  # últimas 24 horas
                timestamp = now - timedelta(hours=i)
                history.append({
                    'timestamp': timestamp,
                    'value': self.current_tariff * (1 + np.random.normal(0, 0.05))
                })
            
            return {
                'current': float(self.current_tariff),
                'by_component': tariffs_df.to_dict('records'),
                'history': history
            }
            
        except Exception as e:
            logging.error(f"Erro ao obter tarifas: {str(e)}")
            return {
                'current': 0.0,
                'by_component': [],
                'history': []
            }
    
    def get_efficiency_metrics(self) -> Dict[str, Any]:
        """Obtém métricas de eficiência"""
        try:
            # Obtém métricas (reais ou mock)
            if self.db is not None:
                try:
                    metrics_df = self.db.get_efficiency_metrics()
                except Exception as e:
                    logging.warning(f"Erro ao obter métricas do banco: {str(e)}")
                    metrics_df = self.get_mock_efficiency_metrics()
            else:
                metrics_df = self.get_mock_efficiency_metrics()
            
            # Calcula indicadores
            efficiency = {
                'current': float(metrics_df['valor_medio'].iloc[0]),
                'trend': float(metrics_df['variacao_anterior'].mean()),
                'ranking': int(metrics_df['ranking_eficiencia'].iloc[0])
            }
            
            # Adiciona dados do sensor se disponível
            reading = self.sensor_reader.get_last_reading()
            if reading:
                efficiency['power_factor'] = float(reading['power_factor'])
                efficiency['temperature'] = float(reading['temperature'])
            
            return {
                'metrics': metrics_df.to_dict('records'),
                'indicators': efficiency
            }
            
        except Exception as e:
            logging.error(f"Erro ao obter métricas: {str(e)}")
            return {
                'metrics': [],
                'indicators': {
                    'current': 0.0,
                    'trend': 0.0,
                    'ranking': 0
                }
            }
    
    def get_renewable_sources(self) -> Dict[str, Any]:
        """Obtém dados de fontes renováveis"""
        try:
            # Obtém dados (reais ou mock)
            if self.db is not None:
                try:
                    renewable_df = self.db.get_renewable_sources()
                except Exception as e:
                    logging.warning(f"Erro ao obter dados renováveis do banco: {str(e)}")
                    renewable_df = self.get_mock_renewable_sources()
            else:
                renewable_df = self.get_mock_renewable_sources()
            
            # Calcula percentuais
            total = renewable_df['valor_total'].sum()
            
            # Agrupa por tipo (PROINFA, CDE, GD)
            percentages = {
                'PROINFA': float(renewable_df[renewable_df['componente'].str.contains('PROINFA')]['valor_total'].sum() / total),
                'CDE': float(renewable_df[renewable_df['componente'].str.contains('CDE')]['valor_total'].sum() / total),
                'GD': float(renewable_df[renewable_df['componente'].str.contains('GD')]['valor_total'].sum() / total)
            }
            
            return {
                'data': renewable_df.to_dict('records'),
                'percentages': percentages
            }
            
        except Exception as e:
            logging.error(f"Erro ao obter dados renováveis: {str(e)}")
            return {
                'data': [],
                'percentages': {}
            }
    
    def save_reading(self, reading: Dict[str, Any]) -> None:
        """Salva leitura no banco"""
        try:
            # Valida dados
            if 'value' not in reading:
                raise ValueError("Valor de leitura ausente")
            
            if reading['value'] <= 0:
                raise ValueError("Valor de consumo inválido")
            
            if 'source' not in reading:
                raise ValueError("Fonte de energia ausente")
            
            # Prepara dados
            data = {
                'timestamp': datetime.now(),
                'valor': reading['value'],
                'fonte': reading['source'],
                'equipamento': reading.get('equipment', 'default')
            }
            
            # Adiciona dados do sensor se disponível
            sensor_reading = self.sensor_reader.get_last_reading()
            if sensor_reading:
                data.update({
                    'voltage': sensor_reading['voltage'],
                    'current': sensor_reading['current'],
                    'power_factor': sensor_reading['power_factor'],
                    'temperature': sensor_reading['temperature']
                })
            
            # Salva no banco
            self.db.save_consumption(data)
            
            # Atualiza histórico local
            self.history.append(data)
            if len(self.history) > 1000:  # mantém últimas 1000 leituras
                self.history.pop(0)
            
            logging.info("Leitura salva com sucesso")
            
        except Exception as e:
            logging.error(f"Erro ao salvar leitura: {str(e)}")
            raise
