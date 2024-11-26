#!/bin/bash

# Script para configurar ambiente e executar testes (macOS/Linux)
# Autor: Gabriel Mule (RM560586)
# Data: 25/11/2023

echo "Configurando ambiente de testes..."

# Verifica se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Python 3 não encontrado. Por favor, instale o Python 3."
    exit 1
fi

# Define diretório do script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Cria ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativa ambiente virtual
echo "Ativando ambiente virtual..."
source venv/bin/activate

# Atualiza pip
python -m pip install --upgrade pip

# Instala todas as dependências
echo "Instalando dependências..."
pip install -r requirements.txt

# Executa testes unitários
echo "Executando testes unitários..."
python -m pytest -v --cov=src

# Desativa ambiente virtual
deactivate
