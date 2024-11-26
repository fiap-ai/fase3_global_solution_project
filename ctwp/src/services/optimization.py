#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Serviço de otimização de consumo energético
Autor: Gabriel Mule (RM560586)
Data: 25/11/2024
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans

class EnergyOptimizer:
    """Otimiza consumo energético"""
    
    def __init__(self, db_connection):
        """Inicializa otimizador"""
        self.db = db_connection
        self.scaler = MinMaxScaler()
        self.kmeans = KMeans(n_clusters=3, n_init=10)  # Fixado em 3 clusters
        self.current_mode = "balanceado"
        self.valid_modes = ['econômico', 'balanceado', 'conforto']
        self.thresholds = {
            'power_factor': {
                'econômico': 0.92,
                'balanceado': 0.90,
                'conforto': 0.85
            },
            'temperature': {
                'econômico': 25.0,
                'balanceado': 23.0,
                'conforto': 21.0
            },
            'voltage_variation': 0.1,  # ±10%
            'current_limit': 15.0,     # 15A
            'peak_threshold': 0.8      # 80% da capacidade
        }
        logging.info("Otimizador inicializado")
    
    def _generate_mock_consumption(self, days: int = 7) -> pd.DataFrame:
        """Gera dados mock de consumo"""
        now = datetime.now()
        data = []
        for i in range(days * 24):  # dados horários
            ts = now - timedelta(hours=i)
            data.append({
                'timestamp': ts,
                'consumption': np.random.normal(100, 10),
                'cost': np.random.normal(50, 5),
                'tariff': 0.5
            })
        return pd.DataFrame(data)
    
    def _generate_mock_tariffs(self) -> pd.DataFrame:
        """Gera dados mock de tarifas"""
        return pd.DataFrame([
            {'componente': 'TE', 'valor': 0.28},
            {'componente': 'TUSD', 'valor': 0.31},
            {'componente': 'Bandeira', 'valor': 0.04}
        ])
    
    def optimize(
        self,
        consumption: Dict[str, Any],
        tariffs: Dict[str, Any],
        sensor_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Executa otimização"""
        try:
            # Valida dados
            if not consumption or 'details' not in consumption:
                raise ValueError("Dados de consumo inválidos")
            
            if not tariffs or 'by_component' not in tariffs:
                raise ValueError("Dados de tarifa inválidos")
            
            # Prepara dados
            consumption_data = pd.DataFrame(consumption['details'])
            tariff_data = pd.DataFrame(tariffs['by_component'])
            
            # Garante colunas necessárias
            required_columns = ['consumption', 'tariff', 'cost']
            for col in required_columns:
                if col not in consumption_data.columns:
                    consumption_data[col] = 0.0
            
            # Valida valores
            if (consumption_data['consumption'] < 0).any():
                raise ValueError("Valores de consumo negativos")
            
            if (consumption_data['tariff'] < 0).any():
                raise ValueError("Valores de tarifa negativos")
            
            # Normaliza dados
            features = ['consumption', 'tariff']
            consumption_normalized = self.scaler.fit_transform(
                consumption_data[features].values
            )
            
            # Garante número mínimo de amostras
            if len(consumption_normalized) < self.kmeans.n_clusters:
                consumption_normalized = np.repeat(
                    consumption_normalized, 
                    self.kmeans.n_clusters, 
                    axis=0
                )
            
            # Identifica padrões
            clusters = self.kmeans.fit_predict(consumption_normalized)
            
            # Calcula métricas
            metrics = {
                'consumption_mean': consumption_data['consumption'].mean(),
                'tariff_mean': consumption_data['tariff'].mean(),
                'cost_total': consumption_data['cost'].sum(),
                'patterns': len(np.unique(clusters))
            }
            
            # Adiciona métricas dos sensores
            if sensor_data:
                metrics.update({
                    'power_factor': sensor_data.get('power_factor', 0),
                    'temperature': sensor_data.get('temperature', 0),
                    'voltage': sensor_data.get('voltage', 0),
                    'current': sensor_data.get('current', 0)
                })
            
            # Gera recomendações
            recommendations = self._generate_recommendations(
                consumption_data,
                tariff_data,
                metrics,
                clusters,
                sensor_data
            )
            
            # Calcula economia estimada
            savings = self._calculate_savings(recommendations)
            
            # Salva resultados se banco disponível
            if self.db is not None:
                self._save_optimization_results(recommendations, savings, metrics)
            
            return {
                'recommendations': recommendations,
                'savings': savings,
                'metrics': metrics
            }
            
        except Exception as e:
            logging.error(f"Erro na otimização: {str(e)}")
            raise
    
    def _generate_recommendations(
        self,
        consumption: pd.DataFrame,
        tariffs: pd.DataFrame,
        metrics: Dict[str, float],
        clusters: np.ndarray,
        sensor_data: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Gera recomendações de otimização"""
        recommendations = []
        
        # Análise por período
        peak_consumption = consumption.groupby(
            pd.to_datetime(consumption['timestamp']).dt.hour
        )['consumption'].mean()
        
        peak_hours = peak_consumption.nlargest(3).index.tolist()
        if peak_hours:
            recommendations.append({
                'type': 'Período',
                'action': f'Reduzir consumo nos horários {peak_hours}',
                'savings': 15.0,
                'priority': 'alta'
            })
        
        # Análise por fonte
        renewable_sources = tariffs[
            tariffs['componente'].str.contains('PROINFA|CDE|GD', na=False)
        ]
        if not renewable_sources.empty:
            recommendations.append({
                'type': 'Fonte',
                'action': 'Aumentar uso de energia solar',
                'savings': 25.0,
                'priority': 'alta'
            })
        
        # Análise por tarifa
        if metrics['tariff_mean'] > 0.5:  # threshold exemplo
            recommendations.append({
                'type': 'Tarifa',
                'action': 'Migrar para tarifa branca',
                'savings': 10.0,
                'priority': 'média'
            })
        
        # Análise por padrão
        if metrics['patterns'] > 1:
            recommendations.append({
                'type': 'Padrão',
                'action': 'Regularizar consumo',
                'savings': 5.0,
                'priority': 'baixa'
            })
        
        # Análise dos dados dos sensores
        if sensor_data:
            # Fator de potência
            pf_threshold = self.thresholds['power_factor'][self.current_mode]
            if metrics['power_factor'] < pf_threshold:
                recommendations.append({
                    'type': 'Qualidade',
                    'action': 'Melhorar fator de potência',
                    'savings': 8.0,
                    'priority': 'alta'
                })
            
            # Temperatura
            temp_threshold = self.thresholds['temperature'][self.current_mode]
            if metrics['temperature'] < temp_threshold - 2:
                recommendations.append({
                    'type': 'Conforto',
                    'action': 'Aumentar temperatura do ar condicionado',
                    'savings': 12.0,
                    'priority': 'média'
                })
            elif metrics['temperature'] > temp_threshold + 2:
                recommendations.append({
                    'type': 'Manutenção',
                    'action': 'Verificar eficiência do ar condicionado',
                    'savings': 10.0,
                    'priority': 'alta'
                })
            
            # Tensão
            nominal_voltage = 220  # Assumindo 220V
            voltage_variation = abs(metrics['voltage'] - nominal_voltage) / nominal_voltage
            if voltage_variation > self.thresholds['voltage_variation']:
                recommendations.append({
                    'type': 'Segurança',
                    'action': 'Verificar estabilidade da rede',
                    'savings': 5.0,
                    'priority': 'crítica'
                })
            
            # Corrente
            if metrics['current'] > self.thresholds['current_limit']:
                recommendations.append({
                    'type': 'Segurança',
                    'action': 'Reduzir carga do circuito',
                    'savings': 0.0,
                    'priority': 'crítica'
                })
        
        return recommendations
    
    def _calculate_savings(self, recommendations: List[Dict[str, Any]]) -> float:
        """Calcula economia total estimada"""
        # Prioriza recomendações críticas
        total_savings = 0
        priority_weights = {
            'crítica': 1.0,
            'alta': 0.8,
            'média': 0.6,
            'baixa': 0.4
        }
        
        for rec in recommendations:
            weight = priority_weights.get(rec['priority'], 0.5)
            total_savings += rec['savings'] * weight
        
        return total_savings
    
    def _save_optimization_results(
        self,
        recommendations: List[Dict[str, Any]],
        savings: float,
        metrics: Dict[str, float]
    ) -> None:
        """Salva resultados da otimização"""
        try:
            # Prepara dados
            data = {
                'timestamp': datetime.now(),
                'tipo': 'recomendação',
                'modo': self.current_mode,
                'valor_anterior': metrics.get('consumption_mean', 0),
                'valor_otimizado': metrics.get('consumption_mean', 0) * (1 - savings/100),
                'economia_estimada': savings,
                'metricas': str(metrics),
                'recomendacao': str(recommendations)
            }
            
            # Salva no banco
            self.db.save_optimization(data)
            logging.info("Resultados salvos com sucesso")
            
        except Exception as e:
            logging.error(f"Erro ao salvar resultados: {str(e)}")
            raise
    
    def set_mode(self, mode: str) -> None:
        """Define modo de otimização"""
        if mode.lower() not in self.valid_modes:
            raise ValueError(f"Modo inválido. Use: {self.valid_modes}")
        
        self.current_mode = mode.lower()
        logging.info(f"Modo alterado para: {mode}")
    
    def get_recommendations(self) -> Dict[str, Any]:
        """Obtém recomendações atuais"""
        try:
            # Obtém dados recentes
            if self.db is not None:
                consumption = self.db.get_consumption_history(days=7)
                tariffs = self.db.get_current_tariffs()
            else:
                # Usa dados mock se banco não disponível
                consumption = self._generate_mock_consumption()
                tariffs = self._generate_mock_tariffs()
            
            # Prepara dados para otimização
            consumption_dict = {
                'details': []
            }
            
            # Converte DataFrame para o formato esperado
            for _, row in consumption.iterrows():
                consumption_dict['details'].append({
                    'timestamp': row.get('timestamp', datetime.now()),
                    'consumption': row.get('consumption', 0),
                    'tariff': row.get('tariff', 0),
                    'cost': row.get('cost', 0)
                })
            
            # Executa otimização
            results = self.optimize(
                consumption_dict,
                {'by_component': tariffs.to_dict('records')}
            )
            
            # Formata saída
            return {
                'items': results['recommendations'],
                'savings': results['savings'],
                'results': [
                    {
                        'source': 'Rede',
                        'before': results['metrics'].get('consumption_mean', 100),
                        'after': results['metrics'].get('consumption_mean', 100) * 0.85,
                        'savings': 15.0
                    },
                    {
                        'source': 'Solar',
                        'before': results['metrics'].get('consumption_mean', 100) * 0.2,
                        'after': results['metrics'].get('consumption_mean', 100) * 0.3,
                        'savings': 25.0
                    }
                ]
            }
            
        except Exception as e:
            logging.error(f"Erro ao obter recomendações: {str(e)}")
            raise
    
    def analyze_patterns(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analisa padrões de consumo"""
        try:
            # Prepara dados
            features = ['consumption', 'tariff', 'cost']
            if 'power_factor' in data.columns:
                features.append('power_factor')
            if 'temperature' in data.columns:
                features.append('temperature')
            
            X = data[features].values
            X_scaled = self.scaler.fit_transform(X)
            
            # Garante número mínimo de amostras
            if len(X_scaled) < self.kmeans.n_clusters:
                X_scaled = np.repeat(X_scaled, self.kmeans.n_clusters, axis=0)
            
            # Executa clustering
            clusters = self.kmeans.fit_predict(X_scaled)
            
            # Analisa resultados
            results = {
                'clusters': len(np.unique(clusters)),
                'centers': self.kmeans.cluster_centers_,
                'labels': clusters.tolist(),
                'features': features
            }
            
            return results
            
        except Exception as e:
            logging.error(f"Erro na análise de padrões: {str(e)}")
            raise
    
    def simulate_scenarios(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Simula diferentes cenários de consumo"""
        try:
            # Cenário atual
            current = {
                'consumption': data['consumption'].sum(),
                'cost': data['cost'].sum()
            }
            
            # Adiciona métricas dos sensores se disponíveis
            if 'power_factor' in data.columns:
                current['power_factor'] = data['power_factor'].mean()
            if 'temperature' in data.columns:
                current['temperature'] = data['temperature'].mean()
            
            # Fatores de ajuste baseados no modo
            if self.current_mode == 'econômico':
                consumption_factor = 0.75  # -25%
                cost_factor = 0.70        # -30%
            elif self.current_mode == 'balanceado':
                consumption_factor = 0.85  # -15%
                cost_factor = 0.80        # -20%
            else:  # conforto
                consumption_factor = 0.90  # -10%
                cost_factor = 0.85        # -15%
            
            # Cenário otimista
            optimistic = {
                'consumption': current['consumption'] * consumption_factor,
                'cost': current['cost'] * cost_factor
            }
            
            # Cenário pessimista
            pessimistic = {
                'consumption': current['consumption'] * 1.1,  # +10%
                'cost': current['cost'] * 1.15  # +15%
            }
            
            # Adiciona métricas dos sensores aos cenários
            if 'power_factor' in current:
                optimistic['power_factor'] = min(0.98, current['power_factor'] * 1.1)
                pessimistic['power_factor'] = current['power_factor'] * 0.9
            
            if 'temperature' in current:
                temp_threshold = self.thresholds['temperature'][self.current_mode]
                optimistic['temperature'] = temp_threshold
                pessimistic['temperature'] = current['temperature']
            
            return {
                'current': current,
                'optimistic': optimistic,
                'pessimistic': pessimistic
            }
            
        except Exception as e:
            logging.error(f"Erro na simulação: {str(e)}")
            raise
