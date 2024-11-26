#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gerenciador de gráficos para interface
Autor: Gabriel Mule (RM560586)
Data: 25/11/2024
"""

import logging
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta

# Adicionando logs para debug
logging.debug("Configurando matplotlib")
import matplotlib
matplotlib.use('AGG')
matplotlib.interactive(False)
# Configura fonte padrão
matplotlib.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica']
})
logging.debug("Backend matplotlib configurado")

logging.debug("Importando módulos matplotlib")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
logging.debug("Módulos matplotlib importados")

logging.debug("Importando outros módulos")
import pandas as pd
import numpy as np
from PIL import Image, ImageTk
import io
logging.debug("Módulos importados com sucesso")

class ChartManager:
    """Gerencia gráficos da interface"""
    
    def __init__(self, size: Tuple[int, int] = (640, 480)):
        """Inicializa gerenciador"""
        logging.debug(f"Inicializando ChartManager com tamanho {size}")
        try:
            plt.ioff()  # Desativa modo interativo
            logging.debug("Modo interativo desativado")
            
            self.figure = plt.figure(figsize=(size[0]/100, size[1]/100), dpi=100)
            logging.debug("Figura criada")
            
            # Configuração visual
            self.colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
            
            # Configurações
            self.font_size = 10
            self.title_size = 12
            self.label_size = 10
            self.tick_size = 8
            
            # Cache da última imagem
            self._last_image = None
            
            logging.info("Gerenciador de gráficos inicializado")
        except Exception as e:
            logging.error(f"Erro ao inicializar ChartManager: {str(e)}", exc_info=True)
            raise
    
    def get_image(self) -> ImageTk.PhotoImage:
        """Converte figura atual para imagem Tkinter"""
        logging.debug("Convertendo figura para imagem")
        try:
            buf = io.BytesIO()
            self.figure.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
            logging.debug("Figura salva em buffer")
            
            buf.seek(0)
            image = Image.open(buf)
            logging.debug("Imagem aberta do buffer")
            
            self._last_image = ImageTk.PhotoImage(image)
            logging.debug("Imagem convertida para PhotoImage")
            
            return self._last_image
        except Exception as e:
            logging.error(f"Erro ao converter figura para imagem: {str(e)}", exc_info=True)
            raise
    
    def plot_consumption(
        self,
        data: pd.DataFrame,
        title: str = "Consumo por Fonte"
    ):
        """Plota gráfico de consumo"""
        logging.debug("Plotando gráfico de consumo")
        try:
            # Se não há dados ou são inválidos, gera dados mock
            if data is None or data.empty or 'source' not in data.columns:
                logging.debug("Gerando dados mock para gráfico de consumo")
                now = datetime.now()
                mock_data = []
                for i in range(24):  # 24 horas de dados
                    ts = now - timedelta(hours=i)
                    for source in ['Rede', 'Solar', 'Bateria']:
                        base_value = 70.0 if source == 'Rede' else (20.0 if source == 'Solar' else 10.0)
                        mock_data.append({
                            'timestamp': ts,
                            'source': source,
                            'value': base_value * (1 + np.random.normal(0, 0.1))
                        })
                data = pd.DataFrame(mock_data)
            
            # Garante que temos as colunas necessárias
            if 'timestamp' not in data.columns:
                data['timestamp'] = pd.date_range(
                    end=datetime.now(),
                    periods=len(data)
                )
            if 'source' not in data.columns:
                data['source'] = 'Total'
            if 'value' not in data.columns:
                data['value'] = 0.0
            
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            logging.debug("Subplot criado")
            
            # Verifica se temos dados temporais
            has_timestamp = 'timestamp' in data.columns
            
            if has_timestamp:
                # Determina intervalo de dados
                time_range = data['timestamp'].max() - data['timestamp'].min()
                
                if time_range > timedelta(days=31):
                    # Para períodos maiores que 1 mês, usa gráfico de barras empilhadas
                    # Adiciona coluna de mês/ano para agrupamento
                    data['month_year'] = data['timestamp'].dt.strftime('%Y-%m')
                    
                    # Agrupa dados por mês e fonte
                    grouped_data = data.groupby(['month_year', 'source'])['value'].mean().reset_index()
                    
                    # Pivota dados para ter fontes como colunas
                    pivot_data = grouped_data.pivot(
                        index='month_year',
                        columns='source',
                        values='value'
                    ).fillna(0)
                    
                    # Plota barras empilhadas
                    bottom = np.zeros(len(pivot_data))
                    for source in pivot_data.columns:
                        ax.bar(
                            range(len(pivot_data)),
                            pivot_data[source],
                            bottom=bottom,
                            label=source,
                            color=self.colors[list(pivot_data.columns).index(source) % len(self.colors)],
                            alpha=0.7
                        )
                        # Adiciona valores em cada segmento
                        for i, value in enumerate(pivot_data[source]):
                            if value > 0:  # Só mostra valores significativos
                                ax.text(
                                    i,
                                    bottom + value/2,
                                    f'{value:.0f}',
                                    ha='center',
                                    va='center',
                                    color='white',
                                    fontweight='bold',
                                    fontsize=self.font_size - 1
                                )
                        bottom += pivot_data[source]
                    
                    # Adiciona totais sobre as barras
                    totals = pivot_data.sum(axis=1)
                    for i, total in enumerate(totals):
                        ax.text(
                            i,
                            total,
                            f'Total:\n{total:.0f}',
                            ha='center',
                            va='bottom',
                            fontsize=self.font_size,
                            bbox=dict(
                                facecolor='white',
                                alpha=0.8,
                                edgecolor='none',
                                pad=1
                            )
                        )
                    
                    # Configura eixo x
                    ax.set_xticks(range(len(pivot_data)))
                    ax.set_xticklabels(
                        [datetime.strptime(d, '%Y-%m').strftime('%b/%Y') for d in pivot_data.index],
                        rotation=45,
                        ha='right'
                    )
                    
                    # Ajusta limites do eixo y para dar espaço aos rótulos
                    ylim = ax.get_ylim()
                    ax.set_ylim(ylim[0], ylim[1] * 1.1)
                    
                    # Legenda horizontal no topo
                    ax.legend(
                        bbox_to_anchor=(0.5, 1.15),
                        loc='center',
                        ncol=len(pivot_data.columns),
                        fontsize=self.font_size
                    )
                    
                else:
                    # Para períodos menores, mantém gráfico de linha
                    for i, source in enumerate(data['source'].unique()):
                        source_data = data[data['source'] == source]
                        ax.plot(
                            source_data['timestamp'],
                            source_data['value'],
                            label=source,
                            color=self.colors[i % len(self.colors)],
                            marker='o',
                            markersize=4,
                            linewidth=2
                        )
                    
                    # Determina formato do eixo x baseado no intervalo
                    if time_range <= timedelta(hours=24):
                        date_format = '%H:%M'
                        ax.xaxis.set_major_locator(matplotlib.dates.HourLocator(interval=2))
                    elif time_range <= timedelta(days=7):
                        date_format = '%d/%m %H:%M'
                        ax.xaxis.set_major_locator(matplotlib.dates.DayLocator())
                    else:
                        date_format = '%d/%m'
                        ax.xaxis.set_major_locator(matplotlib.dates.DayLocator(interval=5))
                    
                    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter(date_format))
                    plt.xticks(rotation=45, ha='right')
                    
                    # Legenda no canto superior direito
                    ax.legend(
                        fontsize=self.font_size,
                        loc='upper right'
                    )
                
            else:
                # Gráfico de barras para dados agregados
                plot_data = data.copy()
                bars = ax.bar(
                    plot_data['source'],
                    plot_data['value'],
                    color=self.colors,
                    alpha=0.7
                )
                
                # Adiciona valores sobre as barras
                for bar in bars:
                    height = bar.get_height()
                    ax.text(
                        bar.get_x() + bar.get_width()/2.,
                        height,
                        f'{height:.1f}',
                        ha='center',
                        va='bottom',
                        fontsize=self.font_size
                    )
            
            # Configuração comum
            ax.set_title(title, fontsize=self.title_size, pad=20)
            ax.set_ylabel("Consumo (kWh)", fontsize=self.label_size)
            ax.tick_params(axis='both', labelsize=self.tick_size)
            
            # Grade mais suave
            ax.grid(True, linestyle='--', alpha=0.3)
            
            # Remove bordas superior e direita
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            # Ajusta layout
            self.figure.tight_layout()
            logging.debug("Layout ajustado")
            
        except Exception as e:
            logging.error(f"Erro ao plotar gráfico de consumo: {str(e)}")
            raise
    
    def plot_comparison(
        self,
        data: Dict[str, List[float]],
        title: str = "Comparação de Consumo"
    ):
        """Plota gráfico de comparação"""
        logging.debug("Plotando gráfico de comparação")
        try:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            logging.debug("Subplot criado")
            
            # Prepara dados
            categories = list(data.keys())
            values = [data[cat] for cat in categories]
            
            # Calcula estatísticas
            medians = [np.median(v) for v in values]
            means = [np.mean(v) for v in values]
            
            # Cria box plot
            bp = ax.boxplot(
                values,
                labels=categories,
                patch_artist=True,
                medianprops=dict(color="black", linewidth=1.5),
                flierprops=dict(
                    marker='o',
                    markerfacecolor='gray',
                    markersize=4,
                    alpha=0.5
                ),
                widths=0.7
            )
            
            # Colore as caixas
            for i, box in enumerate(bp['boxes']):
                box.set(
                    facecolor=self.colors[i % len(self.colors)],
                    alpha=0.7
                )
            
            # Adiciona pontos de média
            for i, mean in enumerate(means):
                ax.plot(
                    i + 1,
                    mean,
                    marker='s',
                    color='white',
                    markeredgecolor='black',
                    markersize=8,
                    label='Média' if i == 0 else None
                )
            
            # Adiciona valores
            for i, (median, mean) in enumerate(zip(medians, means)):
                # Mediana
                ax.text(
                    i + 1,
                    median,
                    f'M: {median:.1f}',
                    ha='left',
                    va='bottom',
                    fontsize=self.font_size - 1
                )
                # Média
                ax.text(
                    i + 1,
                    mean,
                    f'μ: {mean:.1f}',
                    ha='right',
                    va='top',
                    fontsize=self.font_size - 1
                )
            
            # Configuração
            ax.set_title(title, fontsize=self.title_size, pad=20)
            ax.set_ylabel("Consumo (kWh)", fontsize=self.label_size)
            ax.tick_params(axis='both', labelsize=self.tick_size)
            
            # Grade mais suave
            ax.grid(True, linestyle='--', alpha=0.3)
            
            # Remove bordas superior e direita
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            # Rotação dos rótulos
            plt.xticks(rotation=45)
            
            # Legenda
            ax.legend(
                ['Média'],
                loc='upper right',
                frameon=True,
                fancybox=True,
                shadow=True,
                fontsize=self.font_size
            )
            
            # Ajusta layout
            self.figure.tight_layout()
            logging.debug("Layout ajustado")
            
        except Exception as e:
            logging.error(f"Erro ao plotar gráfico de comparação: {str(e)}")
            raise
    
    def plot_efficiency(
        self,
        data: pd.DataFrame,
        title: str = "Eficiência Energética"
    ):
        """Plota gráfico de eficiência"""
        logging.debug("Plotando gráfico de eficiência")
        try:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            logging.debug("Subplot criado")
            
            # Se não há dados ou são inválidos, gera dados mock
            if not isinstance(data, pd.DataFrame) or data.empty:
                logging.debug("Gerando dados mock")
                now = datetime.now()
                dates = [now - timedelta(days=i) for i in range(30)]
                
                # Gera tendência crescente com flutuações
                base = 70  # Eficiência base de 70%
                trend = np.linspace(0, 15, len(dates))  # Tendência de melhoria de 15%
                noise = np.random.normal(0, 2, len(dates))  # Variação diária
                values = base + trend + noise
                
                # Limita valores entre 0 e 100
                values = np.clip(values, 0, 100)
                
                data = pd.DataFrame({
                    'timestamp': dates,
                    'valor_medio': values
                })
            
            # Garante que temos as colunas necessárias
            if 'valor_medio' not in data.columns:
                data['valor_medio'] = 0
            if 'timestamp' not in data.columns:
                data['timestamp'] = pd.date_range(end=datetime.now(), periods=len(data))
            
            # Plota linha principal
            line = ax.plot(
                data['timestamp'],
                data['valor_medio'],
                color=self.colors[0],
                linewidth=2,
                label='Eficiência'
            )[0]
            
            # Adiciona área sombreada para destacar tendência
            ax.fill_between(
                data['timestamp'],
                data['valor_medio'],
                alpha=0.2,
                color=self.colors[0]
            )
            
            # Adiciona pontos de dados
            ax.scatter(
                data['timestamp'],
                data['valor_medio'],
                color=self.colors[0],
                s=30,
                alpha=0.6
            )
            
            # Formata eixo x
            ax.xaxis.set_major_formatter(
                matplotlib.dates.DateFormatter('%d/%m')
            )
            plt.xticks(rotation=45)
            
            # Configuração
            ax.set_title(title, fontsize=self.title_size, pad=20)
            ax.set_xlabel("Data", fontsize=self.label_size)
            ax.set_ylabel("Eficiência (%)", fontsize=self.label_size)
            ax.tick_params(axis='both', labelsize=self.tick_size)
            
            # Define limites do eixo y
            ax.set_ylim(0, 100)
            
            # Grade mais suave
            ax.grid(True, linestyle='--', alpha=0.3)
            
            # Remove bordas superior e direita
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            # Adiciona valor atual e tendência
            current = data['valor_medio'].iloc[-1]
            trend = data['valor_medio'].diff().mean() * 30  # Tendência mensal
            
            ax.text(
                0.02, 0.98,
                f'Atual: {current:.1f}%\nTendência: {trend:+.1f}%/mês',
                transform=ax.transAxes,
                verticalalignment='top',
                bbox=dict(
                    boxstyle='round,pad=0.5',
                    facecolor='white',
                    alpha=0.8,
                    edgecolor='none'
                )
            )
            
            # Ajusta layout
            self.figure.tight_layout()
            logging.debug("Layout ajustado")
            
        except Exception as e:
            logging.error(f"Erro ao plotar gráfico de eficiência: {str(e)}")
            raise
    
    def plot_savings(
        self,
        before: List[float],
        after: List[float],
        title: str = "Economia Projetada"
    ):
        """Plota gráfico de economia"""
        logging.debug("Plotando gráfico de economia")
        try:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            logging.debug("Subplot criado")
            
            # Prepara dados
            width = 0.35
            x = np.arange(len(before))
            
            # Calcula economia total
            total_before = sum(before)
            total_after = sum(after)
            total_savings = ((total_before - total_after) / total_before * 100) if total_before > 0 else 0
            
            # Plota barras com cores mais suaves
            bars1 = ax.bar(x - width/2, before, width, label='Antes', 
                         color=self.colors[0], alpha=0.7)
            bars2 = ax.bar(x + width/2, after, width, label='Depois', 
                         color=self.colors[1], alpha=0.7)
            
            # Adiciona valores e economia
            for i, (b, a) in enumerate(zip(before, after)):
                # Valores nas barras
                ax.text(i - width/2, b/2, f'{b:.1f}', 
                       ha='center', va='center', 
                       color='white', fontweight='bold')
                ax.text(i + width/2, a/2, f'{a:.1f}', 
                       ha='center', va='center', 
                       color='white', fontweight='bold')
                
                # Percentual de economia
                if b > 0:  # Evita divisão por zero
                    economia = ((b - a) / b) * 100
                    color = 'green' if economia > 0 else 'red'
                    ax.text(i, max(b, a) + 1, f'{economia:+.1f}%',
                           ha='center', va='bottom', 
                           color=color, fontweight='bold')
            
            # Adiciona economia total
            ax.text(
                0.98, 0.98,
                f'Economia Total: {total_savings:+.1f}%\n'
                f'Antes: {total_before:.1f} kWh\n'
                f'Depois: {total_after:.1f} kWh',
                transform=ax.transAxes,
                ha='right',
                va='top',
                bbox=dict(
                    boxstyle='round,pad=0.5',
                    facecolor='white',
                    alpha=0.8,
                    edgecolor='none'
                ),
                fontsize=self.font_size
            )
            
            # Configuração
            ax.set_title(title, fontsize=self.title_size, pad=20)
            ax.set_ylabel("Consumo (kWh)", fontsize=self.label_size)
            ax.tick_params(axis='both', labelsize=self.tick_size)
            
            # Grade mais suave
            ax.grid(True, linestyle='--', alpha=0.3)
            
            # Remove bordas superior e direita
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            # Legenda com estilo melhorado
            ax.legend(
                fontsize=self.font_size, 
                loc='upper left',
                frameon=True,
                fancybox=True,
                shadow=True
            )
            
            # Remove rótulos do eixo x
            ax.set_xticks([])
            
            # Ajusta layout
            self.figure.tight_layout()
            logging.debug("Layout ajustado")
            
        except Exception as e:
            logging.error(f"Erro ao plotar gráfico de economia: {str(e)}")
            raise
    
    def plot_sources(
        self,
        data: pd.DataFrame,
        title: str = "Fontes de Energia"
    ):
        """Plota gráfico de fontes de energia"""
        logging.debug("Plotando gráfico de fontes")
        try:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            logging.debug("Subplot criado")
            
            # Se não há dados ou são inválidos, gera dados mock
            if data is None or data.empty or 'source' not in data.columns:
                logging.debug("Gerando dados mock para gráfico de fontes")
                data = pd.DataFrame({
                    'source': ['Rede', 'Solar', 'Bateria'],
                    'value': [70.0, 20.0, 10.0]
                })
            
            # Agrupa dados por fonte
            plot_data = data.groupby('source')['value'].sum().reset_index()
            total = plot_data['value'].sum() if not plot_data.empty else 0
            
            # Calcula porcentagens
            if total > 0:
                plot_data['percentage'] = plot_data['value'] / total * 100
            else:
                plot_data['percentage'] = 0
            
            # Ordena por valor
            plot_data = plot_data.sort_values('value', ascending=True)
            
            # Cria gráfico de barras horizontal
            bars = ax.barh(
                plot_data['source'],
                plot_data['value'],
                color=self.colors[:len(plot_data)]
            )
            
            # Adiciona valores e porcentagens
            for bar in bars:
                width = bar.get_width()
                percentage = (width / total * 100) if total > 0 else 0
                ax.text(
                    width,
                    bar.get_y() + bar.get_height()/2,
                    f'{width:.1f} kWh ({percentage:.1f}%)',
                    ha='left',
                    va='center',
                    fontsize=self.font_size
                )
            
            # Configuração
            ax.set_title(title, fontsize=self.title_size, pad=20)
            ax.set_xlabel("Consumo (kWh)", fontsize=self.label_size)
            ax.tick_params(axis='both', labelsize=self.tick_size)
            
            # Grade mais suave
            ax.grid(True, linestyle='--', alpha=0.3)
            
            # Remove bordas superior e direita
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            # Adiciona total
            ax.text(
                0.98, 0.02,
                f'Total: {total:.1f} kWh',
                transform=ax.transAxes,
                ha='right',
                va='bottom',
                bbox=dict(
                    boxstyle='round,pad=0.5',
                    facecolor='white',
                    alpha=0.8,
                    edgecolor='none'
                ),
                fontsize=self.font_size
            )
            
            # Ajusta layout
            self.figure.tight_layout()
            logging.debug("Layout ajustado")
            
        except Exception as e:
            logging.error(f"Erro ao plotar gráfico de fontes: {str(e)}")
            raise
    
    def clear(self):
        """Limpa gráfico"""
        logging.debug("Limpando gráfico")
        try:
            self.figure.clear()
            self._last_image = None
            logging.debug("Gráfico limpo")
        except Exception as e:
            logging.error(f"Erro ao limpar gráfico: {str(e)}", exc_info=True)
            raise
