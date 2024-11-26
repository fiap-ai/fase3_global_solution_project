#!/bin/bash

# Script para executar o sistema
# Autor: Gabriel Mule (RM560586)
# Data: 25/11/2023

# Ativa ambiente virtual
source venv/bin/activate

# Adiciona diretório src ao PYTHONPATH
export PYTHONPATH=$PYTHONPATH:./src

# Executa sistema
python src/main.py
