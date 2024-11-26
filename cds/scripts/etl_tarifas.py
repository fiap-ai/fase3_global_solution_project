#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de ETL para carga dos dados de tarifas no banco Oracle
Autor: Gabriel Mule (RM560586)
Data: 25/11/2025
"""

import os
import pandas as pd
import oracledb
from datetime import datetime
from dotenv import load_dotenv
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl_tarifas.log'),
        logging.StreamHandler()
    ]
)

# Carrega variáveis de ambiente
load_dotenv()

# Configurações do banco
DB_CONFIG = {
    'user': os.getenv('ORACLE_USER'),
    'password': os.getenv('ORACLE_PASSWORD'),
    'dsn': os.getenv('ORACLE_DSN')
}

def conectar_banco():
    """Estabelece conexão com o banco Oracle"""
    try:
        connection = oracledb.connect(**DB_CONFIG)
        logging.info("Conexão estabelecida com sucesso")
        return connection
    except Exception as e:
        logging.error(f"Erro ao conectar ao banco: {str(e)}")
        raise

def carregar_dados(arquivo):
    """Carrega dados do arquivo CSV"""
    try:
        df = pd.read_csv(
            arquivo,
            sep=';',
            encoding='utf-8',
            parse_dates=['DatGeracaoConjuntoDados', 'DatInicioVigencia', 'DatFimVigencia']
        )
        logging.info(f"Dados carregados: {len(df)} registros")
        return df
    except Exception as e:
        logging.error(f"Erro ao carregar arquivo: {str(e)}")
        raise

def limpar_dados(df):
    """Limpa e prepara os dados para carga"""
    try:
        # Remove duplicatas
        df = df.drop_duplicates()
        
        # Converte valores para numérico
        df['VlrComponenteTarifario'] = pd.to_numeric(
            df['VlrComponenteTarifario'].str.replace(',', '.'),
            errors='coerce'
        )
        
        # Remove valores nulos
        df = df.dropna(subset=['VlrComponenteTarifario'])
        
        # Remove outliers (valores extremos)
        q1 = df['VlrComponenteTarifario'].quantile(0.01)
        q3 = df['VlrComponenteTarifario'].quantile(0.99)
        df = df[
            (df['VlrComponenteTarifario'] >= q1) & 
            (df['VlrComponenteTarifario'] <= q3)
        ]
        
        logging.info(f"Dados limpos: {len(df)} registros mantidos")
        return df
    except Exception as e:
        logging.error(f"Erro na limpeza dos dados: {str(e)}")
        raise

def inserir_dimensoes(conn, df):
    """Insere dados nas tabelas dimensão"""
    try:
        cursor = conn.cursor()
        
        # Distribuidoras
        distribuidoras = df[['SigNomeAgente', 'NumCPFCNPJ']].drop_duplicates()
        for _, row in distribuidoras.iterrows():
            cursor.execute("""
                INSERT INTO distribuidoras (id_distribuidora, nome, cnpj)
                VALUES (seq_distribuidora.nextval, :nome, :cnpj)
            """, nome=row['SigNomeAgente'], cnpj=row['NumCPFCNPJ'])
        
        # Componentes
        componentes = df[['DscComponenteTarifario', 'DscUnidade']].drop_duplicates()
        for _, row in componentes.iterrows():
            cursor.execute("""
                INSERT INTO componentes_tarifarios (id_componente, descricao, unidade)
                VALUES (seq_componente.nextval, :desc, :unidade)
            """, desc=row['DscComponenteTarifario'], unidade=row['DscUnidade'])
        
        # Subgrupos
        subgrupos = df[['DscSubGrupoTarifario']].drop_duplicates()
        for _, row in subgrupos.iterrows():
            cursor.execute("""
                INSERT INTO subgrupos_tarifarios (id_subgrupo, codigo, descricao)
                VALUES (seq_subgrupo.nextval, :codigo, :codigo)
            """, codigo=row['DscSubGrupoTarifario'])
        
        # Modalidades
        modalidades = df[['DscModalidadeTarifaria']].drop_duplicates()
        for _, row in modalidades.iterrows():
            cursor.execute("""
                INSERT INTO modalidades_tarifarias (id_modalidade, nome)
                VALUES (seq_modalidade.nextval, :nome)
            """, nome=row['DscModalidadeTarifaria'])
        
        # Classes
        classes = df[[
            'DscClasseConsumidor',
            'DscSubClasseConsumidor',
            'DscDetalheConsumidor'
        ]].drop_duplicates()
        for _, row in classes.iterrows():
            cursor.execute("""
                INSERT INTO classes_consumidor (
                    id_classe, nome, subclasse, detalhe
                )
                VALUES (
                    seq_classe.nextval, :nome, :subclasse, :detalhe
                )
            """, 
            nome=row['DscClasseConsumidor'],
            subclasse=row['DscSubClasseConsumidor'],
            detalhe=row['DscDetalheConsumidor'])
        
        conn.commit()
        logging.info("Dimensões inseridas com sucesso")
    except Exception as e:
        conn.rollback()
        logging.error(f"Erro ao inserir dimensões: {str(e)}")
        raise

def inserir_fatos(conn, df):
    """Insere dados na tabela fato (tarifas)"""
    try:
        cursor = conn.cursor()
        
        # Mapeia IDs
        cursor.execute("SELECT id_distribuidora, nome FROM distribuidoras")
        map_distribuidoras = dict(cursor.fetchall())
        
        cursor.execute("SELECT id_componente, descricao FROM componentes_tarifarios")
        map_componentes = dict(cursor.fetchall())
        
        cursor.execute("SELECT id_subgrupo, codigo FROM subgrupos_tarifarios")
        map_subgrupos = dict(cursor.fetchall())
        
        cursor.execute("SELECT id_modalidade, nome FROM modalidades_tarifarias")
        map_modalidades = dict(cursor.fetchall())
        
        cursor.execute("SELECT id_classe, nome FROM classes_consumidor")
        map_classes = dict(cursor.fetchall())
        
        # Insere tarifas
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO tarifas (
                    id_tarifa,
                    id_distribuidora,
                    id_componente,
                    id_subgrupo,
                    id_modalidade,
                    id_classe,
                    data_inicio_vigencia,
                    data_fim_vigencia,
                    posto_tarifario,
                    valor,
                    base_tarifaria
                ) VALUES (
                    seq_tarifa.nextval,
                    :id_dist,
                    :id_comp,
                    :id_sub,
                    :id_mod,
                    :id_classe,
                    :dt_ini,
                    :dt_fim,
                    :posto,
                    :valor,
                    :base
                )
            """,
            id_dist=map_distribuidoras[row['SigNomeAgente']],
            id_comp=map_componentes[row['DscComponenteTarifario']],
            id_sub=map_subgrupos[row['DscSubGrupoTarifario']],
            id_mod=map_modalidades[row['DscModalidadeTarifaria']],
            id_classe=map_classes[row['DscClasseConsumidor']],
            dt_ini=row['DatInicioVigencia'],
            dt_fim=row['DatFimVigencia'],
            posto=row['DscPostoTarifario'],
            valor=row['VlrComponenteTarifario'],
            base=row['DscBaseTarifaria'])
            
            if _ % 1000 == 0:  # Commit a cada 1000 registros
                conn.commit()
                logging.info(f"Inseridos {_} registros")
        
        conn.commit()
        logging.info("Fatos inseridos com sucesso")
    except Exception as e:
        conn.rollback()
        logging.error(f"Erro ao inserir fatos: {str(e)}")
        raise

def main():
    """Função principal do ETL"""
    try:
        inicio = datetime.now()
        logging.info("Iniciando processo de ETL")
        
        # Conecta ao banco
        conn = conectar_banco()
        
        # Carrega e limpa dados
        df = carregar_dados("../../scr/data/componentes-tarifarias-2012.csv")
        df = limpar_dados(df)
        
        # Insere dados
        inserir_dimensoes(conn, df)
        inserir_fatos(conn, df)
        
        # Fecha conexão
        conn.close()
        
        fim = datetime.now()
        duracao = fim - inicio
        logging.info(f"Processo concluído em {duracao}")
        
    except Exception as e:
        logging.error(f"Erro no processo de ETL: {str(e)}")
        raise

if __name__ == "__main__":
    main()
