#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Serviço de geração de relatórios
Autor: Gabriel Mule (RM560586)
Data: 25/11/2024
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
import os

class CustomPDF(FPDF):
    """PDF customizado com suporte a Unicode"""
    def __init__(self):
        super().__init__()
        # Usa fonte padrão
        self.set_font('Arial', '', 12)

class ReportGenerator:
    """Gera relatórios de consumo e eficiência"""
    
    def __init__(self, monitor):
        """Inicializa gerador"""
        self.monitor = monitor
        self.output_dir = Path("reports")
        self.temp_dir = Path("temp")
        # Cria diretórios se não existirem
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.temp_dir.mkdir(exist_ok=True, parents=True)
        logging.info("Gerador de relatórios inicializado")
    
    def get_generated_reports(self) -> List[Dict[str, Any]]:
        """Retorna lista de relatórios gerados"""
        reports = []
        if self.output_dir.exists():
            for file in self.output_dir.glob('*.pdf'):
                reports.append({
                    'name': file.name,
                    'path': str(file),
                    'date': datetime.fromtimestamp(file.stat().st_mtime).strftime('%d/%m/%Y %H:%M:%S'),
                    'size': f"{file.stat().st_size / 1024:.1f} KB"
                })
        return sorted(reports, key=lambda x: x['date'], reverse=True)

    def _get_consumption_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Obtém dados de consumo"""
        data = self.monitor.get_current_consumption()
        if data and 'history' in data and data['history']:
            df = pd.DataFrame(data['history'])
            
            # Converte datas
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            start = pd.to_datetime(start_date, format='%Y%m%d')
            end = pd.to_datetime(end_date, format='%Y%m%d')
            
            # Filtra pelo range de datas
            df = df[(df['timestamp'].dt.date >= start.date()) & 
                   (df['timestamp'].dt.date <= end.date())]
            
            # Renomeia colunas para manter compatibilidade
            if 'value' in df.columns:
                df['consumption'] = df['value']
            if 'cost' not in df.columns:
                df['cost'] = df['consumption'] * 0.5  # Custo estimado
            return df
        return pd.DataFrame(columns=['timestamp', 'consumption', 'cost'])
    
    def _get_efficiency_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Obtém dados de eficiência"""
        data = self.monitor.get_efficiency_metrics()
        if data and 'metrics' in data:
            df = pd.DataFrame(data['metrics'])
            
            # Converte datas
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            start = pd.to_datetime(start_date, format='%Y%m%d')
            end = pd.to_datetime(end_date, format='%Y%m%d')
            
            # Filtra pelo range de datas
            df = df[(df['timestamp'].dt.date >= start.date()) & 
                   (df['timestamp'].dt.date <= end.date())]
            
            return df
        return pd.DataFrame(columns=['timestamp', 'valor_medio', 'variacao_anterior'])
    
    def _get_renewable_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Obtém dados de fontes renováveis"""
        data = self.monitor.get_renewable_sources()
        if data and 'data' in data:
            df = pd.DataFrame(data['data'])
            
            # Converte datas
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            start = pd.to_datetime(start_date, format='%Y%m%d')
            end = pd.to_datetime(end_date, format='%Y%m%d')
            
            # Filtra pelo range de datas
            df = df[(df['timestamp'].dt.date >= start.date()) & 
                   (df['timestamp'].dt.date <= end.date())]
            
            return df
        return pd.DataFrame(columns=['componente', 'valor_total'])
    
    def generate_consumption_report(self, start_date: str, end_date: str) -> str:
        """Gera relatório de consumo"""
        try:
            # Obtém dados
            consumption = self._get_consumption_data(start_date, end_date)
            if consumption.empty:
                raise ValueError("Sem dados de consumo disponíveis")
            
            # Cria relatório
            report = CustomPDF()
            report.add_page()
            
            # Cabeçalho
            report.set_font('Arial', 'B', 16)
            report.cell(0, 10, 'Relatorio de Consumo', ln=True, align='C')
            report.set_font('Arial', '', 12)
            
            # Formata datas para exibição
            start = datetime.strptime(start_date, '%Y%m%d').strftime('%d/%m/%Y')
            end = datetime.strptime(end_date, '%Y%m%d').strftime('%d/%m/%Y')
            report.cell(0, 10, f'Período: {start} a {end}', ln=True)
            
            # Resumo
            report.set_font('Arial', 'B', 14)
            report.cell(0, 10, 'Resumo', ln=True)
            report.set_font('Arial', '', 12)
            
            total_consumption = consumption['consumption'].sum()
            total_cost = consumption['cost'].sum()
            
            report.cell(0, 10, f'Consumo Total: {total_consumption:.2f} kWh', ln=True)
            report.cell(0, 10, f'Custo Total: R$ {total_cost:.2f}', ln=True)
            
            # Gráficos
            self._add_consumption_chart(report, consumption)
            self._add_cost_chart(report, consumption)
            
            # Salva relatório
            filename = f"consumo_{start_date}_{end_date}.pdf"
            filepath = self.output_dir / filename
            report.output(str(filepath))
            
            logging.info(f"Relatório de consumo gerado: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logging.error(f"Erro ao gerar relatório de consumo: {str(e)}")
            raise
    
    def generate_efficiency_report(self, start_date: str, end_date: str) -> str:
        """Gera relatório de eficiência"""
        try:
            # Obtém dados
            metrics = self._get_efficiency_data(start_date, end_date)
            renewable = self._get_renewable_data(start_date, end_date)
            
            if metrics.empty:
                raise ValueError("Sem dados de eficiência disponíveis")
            
            # Cria relatório
            report = CustomPDF()
            report.add_page()
            
            # Cabeçalho
            report.set_font('Arial', 'B', 16)
            report.cell(0, 10, 'Analise de Eficiencia Energetica', ln=True, align='C')
            report.set_font('Arial', '', 12)
            
            # Formata datas para exibição
            start = datetime.strptime(start_date, '%Y%m%d').strftime('%d/%m/%Y')
            end = datetime.strptime(end_date, '%Y%m%d').strftime('%d/%m/%Y')
            report.cell(0, 10, f'Período: {start} a {end}', ln=True)
            
            # Métricas principais
            report.set_font('Arial', 'B', 14)
            report.cell(0, 10, 'Metricas de Eficiencia', ln=True)
            report.set_font('Arial', '', 12)
            
            avg_efficiency = metrics['valor_medio'].mean()
            trend = metrics['variacao_anterior'].mean()
            
            report.cell(0, 10, f'Eficiencia Media: {avg_efficiency:.2f}%', ln=True)
            report.cell(0, 10, f'Tendencia: {trend:+.2f}%', ln=True)
            
            # Gráficos
            self._add_efficiency_chart(report, metrics)
            self._add_renewable_chart(report, renewable)
            
            # Recomendações
            report.add_page()
            report.set_font('Arial', 'B', 14)
            report.cell(0, 10, 'Recomendacoes', ln=True)
            report.set_font('Arial', '', 12)
            
            recommendations = [
                "Aumentar uso de energia solar nos horarios de pico",
                "Implementar sistema de automacao para controle de consumo",
                "Realizar manutencao preventiva dos equipamentos",
                "Investir em equipamentos mais eficientes"
            ]
            
            for rec in recommendations:
                report.cell(0, 10, f"* {rec}", ln=True)
            
            # Salva relatório
            filename = f"eficiencia_{start_date}_{end_date}.pdf"
            filepath = self.output_dir / filename
            report.output(str(filepath))
            
            logging.info(f"Relatório de eficiência gerado: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logging.error(f"Erro ao gerar relatório de eficiência: {str(e)}")
            raise
    
    def generate_savings_report(self, start_date: str, end_date: str) -> str:
        """Gera relatório de economia"""
        try:
            # Obtém dados
            consumption = self._get_consumption_data(start_date, end_date)
            if consumption.empty:
                raise ValueError("Sem dados de consumo disponíveis")
            
            # Cria relatório
            report = CustomPDF()
            report.add_page()
            
            # Cabeçalho
            report.set_font('Arial', 'B', 16)
            report.cell(0, 10, 'Relatorio de Economia', ln=True, align='C')
            report.set_font('Arial', '', 12)
            
            # Formata datas para exibição
            start = datetime.strptime(start_date, '%Y%m%d').strftime('%d/%m/%Y')
            end = datetime.strptime(end_date, '%Y%m%d').strftime('%d/%m/%Y')
            report.cell(0, 10, f'Período: {start} a {end}', ln=True)
            
            # Resumo
            report.set_font('Arial', 'B', 14)
            report.cell(0, 10, 'Resumo de Economia', ln=True)
            report.set_font('Arial', '', 12)
            
            # Calcula economia baseado no consumo real vs otimizado
            total_consumption = consumption['consumption'].sum()
            optimized_consumption = total_consumption * 0.85  # 15% de economia
            total_savings = (total_consumption - optimized_consumption) * 0.5  # Custo estimado
            percentage = ((total_consumption - optimized_consumption) / total_consumption) * 100
            
            report.cell(0, 10, f'Economia Total: R$ {total_savings:.2f}', ln=True)
            report.cell(0, 10, f'Percentual: {percentage:.1f}%', ln=True)
            
            # Gráficos
            self._add_savings_chart(report, consumption)
            
            # Detalhamento
            report.add_page()
            report.set_font('Arial', 'B', 14)
            report.cell(0, 10, 'Detalhamento', ln=True)
            report.set_font('Arial', '', 12)
            
            # Calcula economia por fonte
            details = [
                ("Otimizacao de horarios", total_savings * 0.4),
                ("Uso de energia solar", total_savings * 0.35),
                ("Automacao", total_savings * 0.25)
            ]
            
            for item, value in details:
                report.cell(0, 10, f"{item}: R$ {value:.2f}", ln=True)
            
            # Salva relatório
            filename = f"economia_{start_date}_{end_date}.pdf"
            filepath = self.output_dir / filename
            report.output(str(filepath))
            
            logging.info(f"Relatório de economia gerado: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logging.error(f"Erro ao gerar relatório de economia: {str(e)}")
            raise
    
    def generate_renewable_report(self, start_date: str, end_date: str) -> str:
        """Gera relatório de fontes renováveis"""
        try:
            # Obtém dados
            renewable = self._get_renewable_data(start_date, end_date)
            if renewable.empty:
                raise ValueError("Sem dados de fontes renováveis disponíveis")
            
            # Cria relatório
            report = CustomPDF()
            report.add_page()
            
            # Cabeçalho
            report.set_font('Arial', 'B', 16)
            report.cell(0, 10, 'Analise de Fontes Renovaveis', ln=True, align='C')
            report.set_font('Arial', '', 12)
            
            # Formata datas para exibição
            start = datetime.strptime(start_date, '%Y%m%d').strftime('%d/%m/%Y')
            end = datetime.strptime(end_date, '%Y%m%d').strftime('%d/%m/%Y')
            report.cell(0, 10, f'Período: {start} a {end}', ln=True)
            
            # Resumo
            report.set_font('Arial', 'B', 14)
            report.cell(0, 10, 'Resumo', ln=True)
            report.set_font('Arial', '', 12)
            
            total = renewable['valor_total'].sum()
            report.cell(0, 10, f'Total Gerado: {total:.2f} kWh', ln=True)
            
            # Distribuição
            report.set_font('Arial', 'B', 14)
            report.cell(0, 10, 'Distribuicao por Fonte', ln=True)
            report.set_font('Arial', '', 12)
            
            sources = renewable.groupby('componente')['valor_total'].sum()
            for source, value in sources.items():
                percentage = (value / total) * 100
                report.cell(0, 10, f"{source}: {percentage:.1f}%", ln=True)
            
            # Gráficos
            self._add_renewable_distribution_chart(report, renewable)
            self._add_renewable_trend_chart(report, renewable)
            
            # Salva relatório
            filename = f"renovaveis_{start_date}_{end_date}.pdf"
            filepath = self.output_dir / filename
            report.output(str(filepath))
            
            logging.info(f"Relatório de renováveis gerado: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logging.error(f"Erro ao gerar relatório de renováveis: {str(e)}")
            raise
    
    def _add_consumption_chart(self, report: FPDF, data: pd.DataFrame) -> None:
        """Adiciona gráfico de consumo"""
        plt.figure(figsize=(10, 5))
        if not data.empty and 'consumption' in data.columns:
            sns.lineplot(data=data, x='timestamp', y='consumption')
        plt.title('Consumo ao Longo do Dia')
        plt.xlabel('Hora')
        plt.ylabel('Consumo (kWh)')
        
        # Salva temporariamente
        temp_file = self.temp_dir / 'temp_consumption.png'
        plt.savefig(temp_file)
        plt.close()
        
        # Adiciona ao relatório
        report.image(str(temp_file), x=10, w=190)
        temp_file.unlink()
    
    def _add_cost_chart(self, report: FPDF, data: pd.DataFrame) -> None:
        """Adiciona gráfico de custo"""
        plt.figure(figsize=(10, 5))
        if not data.empty and 'cost' in data.columns:
            sns.lineplot(data=data, x='timestamp', y='cost')
        plt.title('Custo ao Longo do Dia')
        plt.xlabel('Hora')
        plt.ylabel('Custo (R$)')
        
        # Salva temporariamente
        temp_file = self.temp_dir / 'temp_cost.png'
        plt.savefig(temp_file)
        plt.close()
        
        # Adiciona ao relatório
        report.image(str(temp_file), x=10, w=190)
        temp_file.unlink()
    
    def _add_efficiency_chart(self, report: FPDF, data: pd.DataFrame) -> None:
        """Adiciona gráfico de eficiência"""
        plt.figure(figsize=(10, 5))
        
        if not data.empty and 'valor_medio' in data.columns:
            sns.lineplot(data=data, x=data.index, y='valor_medio')
        
        plt.title('Evolucao da Eficiencia')
        plt.xlabel('Periodo')
        plt.ylabel('Eficiencia (%)')
        
        # Salva temporariamente
        temp_file = self.temp_dir / 'temp_efficiency.png'
        plt.savefig(temp_file)
        plt.close()
        
        # Adiciona ao relatório
        report.image(str(temp_file), x=10, w=190)
        temp_file.unlink()
    
    def _add_renewable_chart(self, report: FPDF, data: pd.DataFrame) -> None:
        """Adiciona gráfico de fontes renováveis"""
        plt.figure(figsize=(10, 5))
        
        if not data.empty and 'valor_total' in data.columns:
            sns.barplot(data=data, x='componente', y='valor_total')
        
        plt.title('Geracao por Fonte Renovavel')
        plt.xlabel('Fonte')
        plt.ylabel('Geracao (kWh)')
        plt.xticks(rotation=45)
        
        # Salva temporariamente
        temp_file = self.temp_dir / 'temp_renewable.png'
        plt.savefig(temp_file, bbox_inches='tight')
        plt.close()
        
        # Adiciona ao relatório
        report.image(str(temp_file), x=10, w=190)
        temp_file.unlink()
    
    def _add_savings_chart(self, report: FPDF, data: pd.DataFrame) -> None:
        """Adiciona gráfico de economia"""
        plt.figure(figsize=(10, 5))
        
        if not data.empty and 'consumption' in data.columns:
            plt.plot(data['timestamp'], data['consumption'], label='Real')
            plt.plot(data['timestamp'], data['consumption'] * 0.85, label='Otimizado')
        
        plt.title('Consumo Real vs Otimizado')
        plt.xlabel('Data')
        plt.ylabel('Consumo (kWh)')
        plt.legend()
        
        # Salva temporariamente
        temp_file = self.temp_dir / 'temp_savings.png'
        plt.savefig(temp_file)
        plt.close()
        
        # Adiciona ao relatório
        report.image(str(temp_file), x=10, w=190)
        temp_file.unlink()
    
    def _add_renewable_distribution_chart(self, report: FPDF, data: pd.DataFrame) -> None:
        """Adiciona gráfico de distribuição de renováveis"""
        plt.figure(figsize=(10, 5))
        
        if not data.empty and 'valor_total' in data.columns:
            sources = data.groupby('componente')['valor_total'].sum()
            plt.pie(sources.values, labels=sources.index, autopct='%1.1f%%')
        
        plt.title('Distribuicao de Fontes Renovaveis')
        
        # Salva temporariamente
        temp_file = self.temp_dir / 'temp_renewable_dist.png'
        plt.savefig(temp_file)
        plt.close()
        
        # Adiciona ao relatório
        report.image(str(temp_file), x=10, w=190)
        temp_file.unlink()
    
    def _add_renewable_trend_chart(self, report: FPDF, data: pd.DataFrame) -> None:
        """Adiciona gráfico de tendência de renováveis"""
        plt.figure(figsize=(10, 5))
        
        if not data.empty and 'valor_total' in data.columns:
            sns.lineplot(data=data, x=data.index, y='valor_total', hue='componente')
        
        plt.title('Tendencia de Geracao Renovavel')
        plt.xlabel('Periodo')
        plt.ylabel('Geracao (kWh)')
        plt.xticks(rotation=45)
        
        # Salva temporariamente
        temp_file = self.temp_dir / 'temp_renewable_trend.png'
        plt.savefig(temp_file, bbox_inches='tight')
        plt.close()
        
        # Adiciona ao relatório
        report.image(str(temp_file), x=10, w=190)
        temp_file.unlink()
