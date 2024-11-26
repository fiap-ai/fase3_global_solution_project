#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface gráfica do sistema
Autor: Gabriel Mule (RM560586)
Data: 25/11/2024
"""

import logging
from datetime import datetime
from typing import Dict, Any
import os

# Adicionando logs para debug
logging.debug("Configurando matplotlib")

import matplotlib
matplotlib.use('AGG')
matplotlib.interactive(False)
# Usa fonte Arial que é garantida em todos os sistemas
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['Arial']

logging.debug("Matplotlib configurado")
logging.debug("Importando módulos")

import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox, filedialog
import pandas as pd
from .data_manager import DataManager
from .chart_manager import ChartManager

logging.debug("Módulos importados")


class MainWindow:
    """Janela principal do sistema"""
    
    def __init__(self, monitor, optimizer, reporter):
        """Inicializa janela"""
        # Adicionando logs para debug
        logging.debug("Iniciando MainWindow")
        
        try:
            # Configuração do matplotlib
            matplotlib.use('AGG')
            matplotlib.interactive(False)
            logging.debug("Matplotlib reconfigurado")
            
            self.root = ttk.Window(
                title='Sistema de Gerenciamento Energético',
                themename="litera",
                size=(1024, 768)
            )
            logging.debug("Janela principal criada")
            
            # Gerenciadores
            logging.debug("Inicializando gerenciadores")
            self.data_manager = DataManager(monitor, optimizer, reporter)
            logging.debug("DataManager inicializado")
            self.chart_manager = ChartManager(size=(800, 400))
            logging.debug("ChartManager inicializado")
            
            # Referências para as imagens dos gráficos
            self._images = {
                'consumption': None,
                'source': None,
                'optimization': None,
                'report': None
            }
            logging.debug("Referências de imagens inicializadas")
            
            # Interface
            self.notebook = ttk.Notebook(self.root)
            self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
            logging.debug("Notebook criado")
            
            # Abas
            logging.debug("Criando abas")
            try:
                self.dashboard = self.create_dashboard_tab()
                logging.debug("Aba dashboard criada")
                self.monitoring = self.create_monitoring_tab()
                logging.debug("Aba monitoramento criada")
                self.optimization = self.create_optimization_tab()
                logging.debug("Aba otimização criada")
                self.reports = self.create_reports_tab()
                logging.debug("Aba relatórios criada")
            except Exception as e:
                logging.error(f"Erro ao criar abas: {str(e)}", exc_info=True)
                raise
            
            # Menu
            self.create_menu()

            # Loading label com estilo melhorado
            self.loading_label = ttk.Label(
                self.root,
                text="Carregando dados...",
                style="primary.Inverse.TLabel",  # Estilo mais destacado
                font=("Helvetica", 12, "bold"),  # Fonte maior
                padding=10  # Mais espaço ao redor
            )
            self.loading_label.pack(side='bottom', fill='x', pady=5)
            self.loading_label.pack_forget()  # Inicialmente oculto
            
            # Status bar
            self.statusbar = ttk.Label(self.root, text="Sistema iniciado", relief='sunken')
            self.statusbar.pack(side='bottom', fill='x')
            
            # Timer para atualização
            self.root.after(60000, self.on_timer)  # 1 minuto
            
            # Dados iniciais
            logging.debug("Atualizando dados iniciais")
            try:
                self.update_data()
                logging.debug("Dados iniciais atualizados")
            except Exception as e:
                logging.error(f"Erro ao atualizar dados iniciais: {str(e)}", exc_info=True)
                raise
            
            logging.info("Interface inicializada")
            
            # Inicia loop principal
            self.root.mainloop()
            
        except Exception as e:
            logging.error(f"Erro ao inicializar MainWindow: {str(e)}", exc_info=True)
            raise

    def show_loading(self, message: str = "Carregando dados..."):
        """Mostra indicador de loading com mensagem personalizada"""
        self.loading_label.config(text=message)
        self.loading_label.pack(side='bottom', fill='x', pady=5)
        self.root.update()

    def hide_loading(self):
        """Esconde indicador de loading"""
        self.loading_label.pack_forget()
        self.root.update()

    def create_menu(self):
        """Cria menu da aplicação"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Arquivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Exportar Dados", command=self.on_export)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.on_exit)
        
        # Menu Visualização
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Visualização", menu=view_menu)
        view_menu.add_command(label="Atualizar", command=self.on_refresh)
        view_menu.add_separator()
        self.dark_mode = tk.BooleanVar()
        view_menu.add_checkbutton(
            label="Modo Escuro",
            variable=self.dark_mode,
            command=self.on_dark_mode
        )
        
        # Menu Ajuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        help_menu.add_command(label="Sobre", command=self.on_about)
    
    def create_dashboard_tab(self):
        """Cria aba do dashboard"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Dashboard")
        
        # Resumo
        summary_frame = ttk.LabelFrame(frame, text="Resumo", padding=10)
        summary_frame.pack(fill='x', padx=5, pady=5)
        
        # Grid para métricas
        summary_frame.columnconfigure((0,1,2), weight=1)
        
        # Consumo
        ttk.Label(summary_frame, text="Consumo Atual").grid(row=0, column=0)
        self.consumption_value = ttk.Label(summary_frame, text="0.00 kWh")
        self.consumption_value.grid(row=1, column=0)
        
        # Tarifa
        ttk.Label(summary_frame, text="Tarifa Atual").grid(row=0, column=1)
        self.tariff_value = ttk.Label(summary_frame, text="R$ 0.00")
        self.tariff_value.grid(row=1, column=1)
        
        # Economia
        ttk.Label(summary_frame, text="Economia").grid(row=0, column=2)
        self.savings_value = ttk.Label(summary_frame, text="0.0%")
        self.savings_value.grid(row=1, column=2)
        
        # Frame para gráficos e recomendações
        content_frame = ttk.Frame(frame)
        content_frame.pack(fill='both', expand=True, padx=5, pady=5)
        content_frame.columnconfigure((0,1), weight=1)
        
        # Gráfico de consumo
        chart_frame = ttk.LabelFrame(content_frame, text="Consumo", padding=10)
        chart_frame.grid(row=0, column=0, sticky='nsew', padx=5)
        
        self.consumption_label = ttk.Label(chart_frame)
        self.consumption_label.pack(fill='both', expand=True)
        
        # Recomendações
        rec_frame = ttk.LabelFrame(content_frame, text="Recomendações", padding=10)
        rec_frame.grid(row=0, column=1, sticky='nsew', padx=5)
        
        columns = ('tipo', 'acao', 'economia')
        self.recommendations_list = ttk.Treeview(
            rec_frame,
            columns=columns,
            show='headings'
        )
        
        self.recommendations_list.heading('tipo', text='Tipo')
        self.recommendations_list.heading('acao', text='Ação')
        self.recommendations_list.heading('economia', text='Economia')
        
        scrollbar = ttk.Scrollbar(
            rec_frame,
            orient='vertical',
            command=self.recommendations_list.yview
        )
        self.recommendations_list.configure(yscrollcommand=scrollbar.set)
        
        self.recommendations_list.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        return frame
    
    def create_monitoring_tab(self):
        """Cria aba de monitoramento"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Monitoramento")
        
        # Controles
        controls_frame = ttk.Frame(frame)
        controls_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(controls_frame, text="Período:").pack(side='left', padx=5)
        self.period_combo = ttk.Combobox(
            controls_frame,
            values=[
                "Última Hora",
                "Último Dia",
                "Última Semana",
                "Último Mês",
                "Últimos 3 Meses",
                "Últimos 6 Meses",
                "Último Ano"
            ],
            state='readonly'
        )
        self.period_combo.set("Último Dia")  # Valor padrão
        self.period_combo.pack(side='left', padx=5)
        self.period_combo.bind('<<ComboboxSelected>>', self.on_filter_change)
        
        ttk.Label(controls_frame, text="Fonte:").pack(side='left', padx=5)
        self.source_combo = ttk.Combobox(
            controls_frame,
            values=["Todas", "Rede", "Solar", "Bateria"],
            state='readonly'
        )
        self.source_combo.set("Todas")  # Valor padrão
        self.source_combo.pack(side='left', padx=5)
        self.source_combo.bind('<<ComboboxSelected>>', self.on_filter_change)
        
        # Gráfico
        chart_frame = ttk.LabelFrame(frame, text="Consumo por Fonte", padding=10)
        chart_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.source_label = ttk.Label(chart_frame)
        self.source_label.pack(fill='both', expand=True)
        
        # Tabela de dados
        columns = ('data', 'fonte', 'consumo', 'custo')
        self.monitoring_list = ttk.Treeview(
            frame,
            columns=columns,
            show='headings'
        )
        
        self.monitoring_list.heading('data', text='Data')
        self.monitoring_list.heading('fonte', text='Fonte')
        self.monitoring_list.heading('consumo', text='Consumo')
        self.monitoring_list.heading('custo', text='Custo')
        
        scrollbar = ttk.Scrollbar(
            frame,
            orient='vertical',
            command=self.monitoring_list.yview
        )
        self.monitoring_list.configure(yscrollcommand=scrollbar.set)
        
        self.monitoring_list.pack(fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='right', fill='y')
        
        return frame

    def create_optimization_tab(self):
        """Cria aba de otimização"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Otimização")
        
        # Controles
        controls_frame = ttk.Frame(frame)
        controls_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(controls_frame, text="Modo:").pack(side='left', padx=5)
        self.mode_combo = ttk.Combobox(
            controls_frame,
            values=["Econômico", "Balanceado", "Conforto"],
            state='readonly'
        )
        self.mode_combo.set("Balanceado")  # Valor padrão
        self.mode_combo.pack(side='left', padx=5)
        self.mode_combo.bind('<<ComboboxSelected>>', self.on_mode_change)
        
        ttk.Label(controls_frame, text="Limite (kWh):").pack(side='left', padx=5)
        self.limit_var = tk.StringVar(value="1000")
        self.limit_spin = ttk.Spinbox(
            controls_frame,
            from_=0,
            to=10000,
            textvariable=self.limit_var
        )
        self.limit_spin.pack(side='left', padx=5)
        
        # Gráfico
        chart_frame = ttk.LabelFrame(frame, text="Otimização", padding=10)
        chart_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.optimization_label = ttk.Label(chart_frame)
        self.optimization_label.pack(fill='both', expand=True)
        
        # Resultados
        columns = ('fonte', 'antes', 'depois', 'economia')
        self.results_list = ttk.Treeview(
            frame,
            columns=columns,
            show='headings'
        )
        
        self.results_list.heading('fonte', text='Fonte')
        self.results_list.heading('antes', text='Antes')
        self.results_list.heading('depois', text='Depois')
        self.results_list.heading('economia', text='Economia')
        
        scrollbar = ttk.Scrollbar(
            frame,
            orient='vertical',
            command=self.results_list.yview
        )
        self.results_list.configure(yscrollcommand=scrollbar.set)
        
        self.results_list.pack(fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='right', fill='y')
        
        return frame

    def create_reports_tab(self):
        """Cria aba de relatórios"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Relatórios")
        
        # Controles
        controls_frame = ttk.Frame(frame)
        controls_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(controls_frame, text="Tipo:").pack(side='left', padx=5)
        self.report_combo = ttk.Combobox(
            controls_frame,
            values=[
                "Consumo Diário",
                "Análise de Eficiência",
                "Economia",
                "Fontes Renováveis"
            ],
            state='readonly'
        )
        self.report_combo.set("Consumo Diário")  # Valor padrão
        self.report_combo.pack(side='left', padx=5)
        self.report_combo.bind('<<ComboboxSelected>>', self.on_report_type_change)
        
        ttk.Label(controls_frame, text="De:").pack(side='left', padx=5)
        self.start_date = ttk.DateEntry(
            controls_frame,
            dateformat="%d/%m/%Y",  # Formato brasileiro
            firstweekday=6  # Domingo = 6
        )
        self.start_date.pack(side='left', padx=5)
        
        ttk.Label(controls_frame, text="Até:").pack(side='left', padx=5)
        self.end_date = ttk.DateEntry(
            controls_frame,
            dateformat="%d/%m/%Y",  # Formato brasileiro
            firstweekday=6  # Domingo = 6
        )
        self.end_date.pack(side='left', padx=5)
        
        ttk.Button(
            controls_frame,
            text="Gerar Relatório",
            command=self.on_generate_report
        ).pack(side='left', padx=5)
        
        # Frame principal que divide a área em duas partes
        main_frame = ttk.Frame(frame)
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Configura o grid para dividir igualmente
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Frame da lista de relatórios (lado esquerdo)
        list_frame = ttk.LabelFrame(main_frame, text="Relatórios Gerados", padding=10)
        list_frame.grid(row=0, column=0, sticky='nsew', padx=(0,2.5))
        
        # Colunas da lista
        columns = ('nome', 'data', 'tamanho')
        self.reports_list = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings'
        )
        
        self.reports_list.heading('nome', text='Nome')
        self.reports_list.heading('data', text='Data')
        self.reports_list.heading('tamanho', text='Tamanho')
        
        # Configura larguras das colunas
        self.reports_list.column('nome', width=300)
        self.reports_list.column('data', width=150)
        self.reports_list.column('tamanho', width=100)
        
        # Scrollbar para lista
        list_scrollbar = ttk.Scrollbar(
            list_frame,
            orient='vertical',
            command=self.reports_list.yview
        )
        self.reports_list.configure(yscrollcommand=list_scrollbar.set)
        
        # Empacota lista e scrollbar
        self.reports_list.pack(side='left', fill='both', expand=True)
        list_scrollbar.pack(side='right', fill='y')
        
        # Frame de visualização (lado direito)
        view_frame = ttk.LabelFrame(main_frame, text="Visualização", padding=10)
        view_frame.grid(row=0, column=1, sticky='nsew', padx=(2.5,0))
        
        # Label para gráfico
        self.report_label = ttk.Label(view_frame)
        self.report_label.pack(fill='both', expand=True)
        
        # Bind duplo clique para abrir relatório
        self.reports_list.bind('<Double-1>', self.on_open_report)
        
        # Atualiza lista de relatórios
        self.update_reports_list()
        
        return frame

    def update_data(self):
        """Atualiza dados"""
        try:
            self.show_loading("Atualizando dados do sistema...")
            
            # Obtém dados
            consumption = self.data_manager.get_consumption_data()
            tariffs = self.data_manager.get_tariff_data()
            recommendations = self.data_manager.get_recommendations()
            
            # Atualiza valores
            self.consumption_value.config(text=f"{consumption['total']:.2f} kWh")
            self.tariff_value.config(text=f"R$ {tariffs['current']:.2f}")
            self.savings_value.config(text=f"{recommendations['savings']:.1f}%")
            
            # Atualiza gráficos
            self.update_charts(consumption, tariffs, recommendations)
            
            # Atualiza listas
            self.update_lists(consumption, recommendations)
            
            # Atualiza lista de relatórios
            self.update_reports_list()
            
            # Atualiza status
            self.statusbar.config(
                text=f"Última atualização: {datetime.now().strftime('%H:%M:%S')}"
            )
            
            logging.info("Dados atualizados")
            
        except Exception as e:
            logging.error(f"Erro ao atualizar dados: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao atualizar dados: {str(e)}")
        finally:
            self.hide_loading()

    def update_charts(
        self,
        consumption: Dict[str, Any],
        tariffs: Dict[str, Any],
        recommendations: Dict[str, Any]
    ):
        """Atualiza gráficos"""
        try:
            # Gráfico de consumo histórico (dashboard)
            consumption_data = self.data_manager.format_for_consumption_plot("último_dia")
            if not consumption_data.empty:
                self.chart_manager.plot_consumption(
                    consumption_data,
                    title="Consumo Total"
                )
                self._images['consumption'] = self.chart_manager.get_image()
                self.consumption_label.config(image=self._images['consumption'])
            
            # Gráfico de fontes (monitoramento)
            source = self.source_combo.get()
            period = self.period_combo.get().lower().replace(' ', '_')
            source_data = self.data_manager.format_for_consumption_plot(period)
            
            if not source_data.empty:
                if source != "Todas":
                    source_data = source_data[source_data['source'] == source]
                
                # Usa plot_consumption para gráfico de fontes também
                self.chart_manager.plot_consumption(
                    source_data,
                    title=f"Consumo por Fonte {'Total' if source == 'Todas' else source}"
                )
                self._images['source'] = self.chart_manager.get_image()
                self.source_label.config(image=self._images['source'])
            
            # Gráfico de otimização
            before, after = self.data_manager.format_for_savings_plot()
            self.chart_manager.plot_savings(before, after)
            self._images['optimization'] = self.chart_manager.get_image()
            self.optimization_label.config(image=self._images['optimization'])
            
            # Gráfico de relatório (baseado no tipo selecionado)
            report_type = self.report_combo.get()
            if report_type == "Análise de Eficiência":
                efficiency_data = self.data_manager.format_for_efficiency_plot()
                self.chart_manager.plot_efficiency(efficiency_data)
                self._images['report'] = self.chart_manager.get_image()
                self.report_label.config(image=self._images['report'])
            elif report_type == "Fontes Renováveis":
                comparison_data = self.data_manager.format_for_comparison_plot()
                self.chart_manager.plot_comparison(comparison_data)
                self._images['report'] = self.chart_manager.get_image()
                self.report_label.config(image=self._images['report'])
            
        except Exception as e:
            logging.error(f"Erro ao atualizar gráficos: {str(e)}")
            raise

    def update_lists(
        self,
        consumption: Dict[str, Any],
        recommendations: Dict[str, Any]
    ):
        """Atualiza listas"""
        try:
            # Lista de recomendações
            for item in self.recommendations_list.get_children():
                self.recommendations_list.delete(item)
                
            for rec in recommendations['items']:
                self.recommendations_list.insert(
                    '',
                    'end',
                    values=(
                        rec['type'],
                        rec['action'],
                        f"{rec['savings']:.1f}%"
                    )
                )
            
            # Lista de monitoramento
            for item in self.monitoring_list.get_children():
                self.monitoring_list.delete(item)
                
            for detail in consumption['details']:
                self.monitoring_list.insert(
                    '',
                    'end',
                    values=(
                        detail['timestamp'].strftime('%H:%M:%S'),
                        detail['source'],
                        f"{detail['consumption']:.2f} kWh",
                        f"R$ {detail['cost']:.2f}"
                    )
                )
            
            # Lista de resultados
            for item in self.results_list.get_children():
                self.results_list.delete(item)
                
            for result in recommendations['results']:
                self.results_list.insert(
                    '',
                    'end',
                    values=(
                        result['source'],
                        f"{result['before']:.2f} kWh",
                        f"{result['after']:.2f} kWh",
                        f"{result['savings']:.1f}%"
                    )
                )
            
        except Exception as e:
            logging.error(f"Erro ao atualizar listas: {str(e)}")
            raise
    
    def update_reports_list(self):
        """Atualiza lista de relatórios"""
        try:
            # Limpa lista atual
            for item in self.reports_list.get_children():
                self.reports_list.delete(item)
            
            # Obtém lista de relatórios
            reports = self.data_manager.reporter.get_generated_reports()
            
            if reports:
                # Adiciona relatórios à lista
                for report in reports:
                    self.reports_list.insert(
                        '',
                        'end',
                        values=(
                            report['name'],
                            report['date'],
                            report['size']
                        )
                    )
            else:
                # Adiciona mensagem quando não há relatórios
                self.reports_list.insert(
                    '',
                    'end',
                    values=('Nenhum relatório gerado', '-', '-')
                )
            
        except Exception as e:
            logging.error(f"Erro ao atualizar lista de relatórios: {str(e)}")
            raise
    
    def on_timer(self):
        """Manipula evento do timer"""
        self.update_data()
        self.root.after(60000, self.on_timer)  # Agenda próxima atualização

    def on_period_change(self, event):
        """Manipula mudança de período"""
        try:
            self.show_loading("Atualizando período de análise...")
            
            # Força atualização dos dados
            self.data_manager.clear_cache()
            
            # Atualiza todos os dados
            consumption = self.data_manager.get_consumption_data(force_update=True)
            tariffs = self.data_manager.get_tariff_data(force_update=True)
            recommendations = self.data_manager.get_recommendations(force_update=True)
            
            # Atualiza interface
            self.update_charts(consumption, tariffs, recommendations)
            self.update_lists(consumption, recommendations)
            
            # Atualiza status
            self.statusbar.config(
                text=f"Última atualização: {datetime.now().strftime('%H:%M:%S')}"
            )
            
        except Exception as e:
            logging.error(f"Erro ao mudar período: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao mudar período: {str(e)}")
        finally:
            self.hide_loading()

    def on_source_change(self, event):
        """Manipula mudança de fonte"""
        try:
            self.show_loading("Atualizando fonte de energia...")
            
            # Obtém fonte selecionada
            source = self.source_combo.get()
            if source == "Todas":
                source = None
            
            # Força atualização dos dados
            self.data_manager.clear_cache()
            
            # Obtém dados históricos filtrados por fonte
            period = self.period_combo.get().lower().replace(' ', '_')
            data = self.data_manager.get_historical_data(period=period, source=source)
            
            # Atualiza gráfico de fontes
            if not data.empty:
                self.chart_manager.plot_consumption(
                    data,
                    title=f"Consumo por Fonte {'Total' if source is None else source}"
                )
                self._images['source'] = self.chart_manager.get_image()
                self.source_label.config(image=self._images['source'])
            
            # Atualiza lista de monitoramento
            for item in self.monitoring_list.get_children():
                self.monitoring_list.delete(item)
                
            for _, row in data.iterrows():
                self.monitoring_list.insert(
                    '',
                    'end',
                    values=(
                        row.get('timestamp', '').strftime('%H:%M:%S') if 'timestamp' in row else '',
                        row.get('source', source or 'Total'),
                        f"{row.get('value', 0):.2f} kWh",
                        f"R$ {row.get('cost', 0):.2f}" if 'cost' in row else 'N/A'
                    )
                )
            
            # Atualiza status
            self.statusbar.config(
                text=f"Última atualização: {datetime.now().strftime('%H:%M:%S')}"
            )
            
        except Exception as e:
            logging.error(f"Erro ao mudar fonte: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao mudar fonte: {str(e)}")
        finally:
            self.hide_loading()

    def on_filter_change(self, event):
        """Manipula mudança de filtros"""
        try:
            self.show_loading("Atualizando dados...")
            
            # Obtém valores dos filtros
            period = self.period_combo.get().lower().replace(' ', '_')
            source = self.source_combo.get()
            if source == "Todas":
                source = None
            
            # Força atualização dos dados
            self.data_manager.clear_cache()
            
            # Obtém dados históricos filtrados
            data = self.data_manager.get_historical_data(period=period, source=source)
            
            # Atualiza gráfico de fontes
            if not data.empty:
                self.chart_manager.plot_consumption(
                    data,
                    title=f"Consumo por Fonte {'Total' if source is None else source}"
                )
                self._images['source'] = self.chart_manager.get_image()
                self.source_label.config(image=self._images['source'])
            
            # Atualiza lista de monitoramento
            for item in self.monitoring_list.get_children():
                self.monitoring_list.delete(item)
                
            for _, row in data.iterrows():
                self.monitoring_list.insert(
                    '',
                    'end',
                    values=(
                        row.get('timestamp', '').strftime('%H:%M:%S') if 'timestamp' in row else '',
                        row.get('source', source or 'Total'),
                        f"{row.get('value', 0):.2f} kWh",
                        f"R$ {row.get('cost', 0):.2f}" if 'cost' in row else 'N/A'
                    )
                )
            
            # Atualiza status
            self.statusbar.config(
                text=f"Última atualização: {datetime.now().strftime('%H:%M:%S')}"
            )
            
        except Exception as e:
            logging.error(f"Erro ao atualizar filtros: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao atualizar filtros: {str(e)}")
        finally:
            self.hide_loading()
    
    def on_mode_change(self, event):
        """Manipula mudança de modo"""
        try:
            self.show_loading("Alterando modo de operação...")
            
            mode = self.mode_combo.get().lower()
            self.data_manager.optimizer.set_mode(mode)
            self.update_data()
            
        except Exception as e:
            logging.error(f"Erro ao mudar modo: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao mudar modo: {str(e)}")
        finally:
            self.hide_loading()


    def on_report_type_change(self, event):
        """Manipula mudança de tipo de relatório"""
        try:
            report_type = self.report_combo.get()
            if report_type == "Análise de Eficiência":
                efficiency_data = self.data_manager.format_for_efficiency_plot()
                self.chart_manager.plot_efficiency(efficiency_data)
                self._images['report'] = self.chart_manager.get_image()
                self.report_label.config(image=self._images['report'])
            elif report_type == "Fontes Renováveis":
                comparison_data = self.data_manager.format_for_comparison_plot()
                self.chart_manager.plot_comparison(comparison_data)
                self._images['report'] = self.chart_manager.get_image()
                self.report_label.config(image=self._images['report'])
            else:
                # Limpa visualização para outros tipos
                self.report_label.config(image='')
                
        except Exception as e:
            logging.error(f"Erro ao mudar tipo de relatório: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao mudar tipo de relatório: {str(e)}")

    def on_generate_report(self):
        """Manipula geração de relatório"""
        try:
            self.show_loading("Gerando relatório...")
            
            report_type = self.report_combo.get()
            
            # Formata datas como YYYYMMDD
            try:
                start = datetime.strptime(self.start_date.entry.get(), "%d/%m/%Y").strftime("%Y%m%d")
                end = datetime.strptime(self.end_date.entry.get(), "%d/%m/%Y").strftime("%Y%m%d")
            except ValueError as e:
                messagebox.showerror("Erro", "Data inválida. Use o formato DD/MM/AAAA")
                return
            
            if report_type == "Consumo Diário":
                filepath = self.data_manager.reporter.generate_consumption_report(start, end)
            elif report_type == "Análise de Eficiência":
                filepath = self.data_manager.reporter.generate_efficiency_report(start, end)
            elif report_type == "Economia":
                filepath = self.data_manager.reporter.generate_savings_report(start, end)
            else:
                filepath = self.data_manager.reporter.generate_renewable_report(start, end)
            
            # Atualiza lista de relatórios
            self.update_reports_list()
            
            logging.info(f"Relatório gerado: {filepath}")
            messagebox.showinfo("Sucesso", f"Relatório gerado: {filepath}")
            
        except Exception as e:
            logging.error(f"Erro ao gerar relatório: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {str(e)}")
        finally:
            self.hide_loading()
    
    def on_export(self):
        """Manipula exportação de dados"""
        try:
            filetypes = (
                ('CSV files', '*.csv'),
                ('Excel files', '*.xlsx')
            )
            
            filepath = filedialog.asksaveasfilename(
                title='Exportar dados',
                filetypes=filetypes
            )
            
            if not filepath:
                return
            
            self.show_loading("Exportando dados...")
                
            format = "csv" if filepath.endswith(".csv") else "xlsx"
            start = self.start_date.entry.get()
            end = self.end_date.entry.get()
            
            filepath = self.data_manager.export_data(
                start,
                end,
                format=format
            )
            
            messagebox.showinfo("Sucesso", f"Dados exportados: {filepath}")
            
        except Exception as e:
            logging.error(f"Erro ao exportar dados: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao exportar dados: {str(e)}")
        finally:
            self.hide_loading()

    def on_refresh(self):
        """Manipula atualização manual"""
        self.data_manager.clear_cache()
        self.update_data()
    
    def on_dark_mode(self):
        """Manipula modo escuro"""
        if self.dark_mode.get():
            self.root.style.theme_use('darkly')
        else:
            self.root.style.theme_use('litera')
    
    def on_about(self):
        """Manipula sobre"""
        messagebox.showinfo(
            "Sobre",
            "Sistema de Gerenciamento Energético\n\n"
            "Versão: 1.0\n"
            "Autor: Gabriel Mule (RM560586)\n"
            "Copyright © 2024\n\n"
            "Sistema para otimização de consumo energético"
        )
    
    def on_exit(self):
        """Manipula saída"""
        if messagebox.askokcancel("Sair", "Deseja realmente sair?"):
            self.root.quit()
    
    def on_open_report(self, event):
        """Manipula abertura de relatório"""
        try:
            # Obtém item selecionado
            selection = self.reports_list.selection()
            if not selection:
                return
            
            # Obtém dados do relatório
            item = self.reports_list.item(selection[0])
            if not item:
                return
            
            # Se for a mensagem de nenhum relatório, ignora
            if item['values'][0] == 'Nenhum relatório gerado':
                return
            
            # Obtém caminho do relatório
            report_name = item['values'][0]
            report_path = os.path.join('reports', report_name)
            
            # Verifica se arquivo existe
            if not os.path.exists(report_path):
                messagebox.showerror(
                    "Erro",
                    f"Relatório não encontrado: {report_path}"
                )
                return
            
            # Abre relatório com aplicativo padrão
            if os.name == 'nt':  # Windows
                os.startfile(report_path)
            elif os.name == 'posix':  # macOS e Linux
                import subprocess
                subprocess.run(['open' if os.uname().sysname == 'Darwin' else 'xdg-open', report_path])
            
        except Exception as e:
            logging.error(f"Erro ao abrir relatório: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao abrir relatório: {str(e)}")
