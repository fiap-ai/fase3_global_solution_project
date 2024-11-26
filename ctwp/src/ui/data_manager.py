#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gerenciador de dados para interface
Autor: Gabriel Mule (RM560586)
Data: 25/11/2024
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

class DataManager:
    """Gerencia dados da interface"""
    
    def __init__(self, monitor, optimizer, reporter):
        """Inicializa gerenciador"""
        logging.debug("Inicializando DataManager")
        try:
            self.monitor = monitor
            self.optimizer = optimizer
            self.reporter = reporter
            self.cache = {}
            logging.info("Gerenciador de dados inicializado")
        except Exception as e:
            logging.error(f"Erro ao inicializar DataManager: {str(e)}")
            raise
    
    def get_consumption_data(self, days: int = 30) -> Dict[str, Any]:
        """Obtém dados de consumo"""
        logging.debug("Obtendo dados de consumo")
        try:
            # Obtém dados do monitor
            data = self.monitor.get_current_consumption()
            
            if data is None:
                data = {
                    'total': 0.0,
                    'by_source': {},
                    'history': [],
                    'details': [],
                    'alerts': [],
                    'sensor_data': None
                }
            
            return data
            
        except Exception as e:
            logging.error(f"Erro ao obter dados de consumo: {str(e)}")
            raise
    
    def get_tariff_data(self) -> Dict[str, Any]:
        """Obtém dados de tarifas"""
        logging.debug("Obtendo dados de tarifas")
        try:
            # Obtém dados do monitor
            data = self.monitor.get_current_tariffs()
            
            if data is None:
                data = {
                    'current': 0.0,
                    'by_component': [],
                    'history': []
                }
            
            return data
            
        except Exception as e:
            logging.error(f"Erro ao obter dados de tarifas: {str(e)}")
            raise
    
    def get_recommendations(self) -> Dict[str, Any]:
        """Obtém recomendações"""
        logging.debug("Obtendo recomendações")
        try:
            # Obtém dados do otimizador
            data = self.optimizer.get_recommendations()
            
            if data is None:
                data = {
                    'items': [],
                    'savings': 0.0,
                    'results': []
                }
            
            return data
            
        except Exception as e:
            logging.error(f"Erro ao obter recomendações: {str(e)}")
            raise
    
    def update_data(self) -> bool:
        """Atualiza todos os dados"""
        logging.debug("Atualizando dados")
        try:
            # Atualiza dados de consumo
            self.cache['consumption'] = self.get_consumption_data()
            
            # Atualiza dados de tarifas
            self.cache['tariffs'] = self.get_tariff_data()
            
            # Atualiza recomendações
            self.cache['recommendations'] = self.get_recommendations()
            
            return True
            
        except Exception as e:
            logging.error(f"Erro ao atualizar dados: {str(e)}")
            return False
    
    def get_cached_data(self, key: str) -> Optional[Dict[str, Any]]:
        """Obtém dados do cache"""
        return self.cache.get(key)
    
    def clear_cache(self):
        """Limpa cache de dados"""
        self.cache.clear()
    
    def format_for_consumption_plot(self, period: str) -> pd.DataFrame:
        """Formata dados para gráfico de consumo"""
        try:
            # Obtém dados do cache ou atualiza
            data = self.cache.get('consumption')
            if data is None:
                data = self.get_consumption_data()
                self.cache['consumption'] = data
            
            # Converte histórico para DataFrame
            df = pd.DataFrame(data['history'])
            
            # Filtra por período se necessário
            if period != "todos" and not df.empty:
                now = datetime.now()
                if period == "última_hora":
                    start = now - timedelta(hours=1)
                elif period == "último_dia":
                    start = now - timedelta(days=1)
                elif period == "última_semana":
                    start = now - timedelta(weeks=1)
                elif period == "último_mês":
                    start = now - timedelta(days=30)
                elif period == "últimos_3_meses":
                    start = now - timedelta(days=90)
                elif period == "últimos_6_meses":
                    start = now - timedelta(days=180)
                else:  # último_ano
                    start = now - timedelta(days=365)
                
                df = df[df['timestamp'] >= start]
            
            return df
            
        except Exception as e:
            logging.error(f"Erro ao formatar dados para gráfico: {str(e)}")
            return pd.DataFrame()
    
    def format_for_savings_plot(self) -> tuple:
        """Formata dados para gráfico de economia"""
        try:
            # Obtém dados do cache ou atualiza
            data = self.cache.get('recommendations')
            if data is None:
                data = self.get_recommendations()
                self.cache['recommendations'] = data
            
            # Extrai dados de antes e depois
            before = []
            after = []
            
            for result in data['results']:
                before.append(result['before'])
                after.append(result['after'])
            
            return before, after
            
        except Exception as e:
            logging.error(f"Erro ao formatar dados para gráfico: {str(e)}")
            return [], []
    
    def format_for_efficiency_plot(self) -> pd.DataFrame:
        """Formata dados para gráfico de eficiência"""
        try:
            # Obtém dados do cache ou atualiza
            data = self.cache.get('consumption')
            if data is None:
                data = self.get_consumption_data()
                self.cache['consumption'] = data
            
            # Converte histórico para DataFrame
            df = pd.DataFrame(data['history'])
            
            # Calcula eficiência por fonte
            if not df.empty:
                efficiency = df.groupby('source')['value'].agg(['mean', 'std']).reset_index()
                efficiency.columns = ['source', 'efficiency', 'variation']
            else:
                efficiency = pd.DataFrame(columns=['source', 'efficiency', 'variation'])
            
            return efficiency
            
        except Exception as e:
            logging.error(f"Erro ao formatar dados para gráfico: {str(e)}")
            return pd.DataFrame()
    
    def format_for_comparison_plot(self) -> pd.DataFrame:
        """Formata dados para gráfico de comparação"""
        try:
            # Obtém dados do cache ou atualiza
            data = self.cache.get('consumption')
            if data is None:
                data = self.get_consumption_data()
                self.cache['consumption'] = data
            
            # Converte histórico para DataFrame
            df = pd.DataFrame(data['history'])
            
            # Calcula proporção de fontes renováveis
            if not df.empty:
                total = df.groupby('source')['value'].sum().reset_index()
                total['percentage'] = total['value'] / total['value'].sum() * 100
            else:
                total = pd.DataFrame(columns=['source', 'value', 'percentage'])
            
            return total
            
        except Exception as e:
            logging.error(f"Erro ao formatar dados para gráfico: {str(e)}")
            return pd.DataFrame()
    
    def get_historical_data(self, period: str = "último_dia", source: Optional[str] = None) -> pd.DataFrame:
        """Obtém dados históricos filtrados"""
        try:
            # Obtém dados formatados
            data = self.format_for_consumption_plot(period)
            
            # Filtra por fonte se necessário
            if source is not None and not data.empty:
                data = data[data['source'] == source]
            
            return data
            
        except Exception as e:
            logging.error(f"Erro ao obter dados históricos: {str(e)}")
            return pd.DataFrame()
    
    def export_data(self, start: str, end: str, format: str = "csv") -> str:
        """Exporta dados para arquivo"""
        try:
            # Obtém dados do cache ou atualiza
            data = self.cache.get('consumption')
            if data is None:
                data = self.get_consumption_data()
                self.cache['consumption'] = data
            
            # Converte histórico para DataFrame
            df = pd.DataFrame(data['history'])
            
            # Filtra por período
            if not df.empty:
                start_date = datetime.strptime(start, "%Y-%m-%d")
                end_date = datetime.strptime(end, "%Y-%m-%d")
                mask = (df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)
                filtered = df.loc[mask]
            else:
                filtered = df
            
            # Exporta para arquivo
            filename = f"consumption_{start}_{end}.{format}"
            if format == "csv":
                filtered.to_csv(filename, index=False)
            else:
                filtered.to_excel(filename, index=False)
            
            return filename
            
        except Exception as e:
            logging.error(f"Erro ao exportar dados: {str(e)}")
            raise
