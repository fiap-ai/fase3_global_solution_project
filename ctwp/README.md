# Sistema de Gerenciamento Energético
> Autor: Gabriel Mule (RM560586)  
> Data: 25/11/2023

## Visão Geral
Sistema em Python para gerenciamento e otimização do consumo energético em residências, com interface gráfica e monitoramento em tempo real.

## Requisitos do Sistema

### macOS
```bash
# Instala Python e Tk
brew install python tcl-tk

# Instala Oracle Instant Client
brew install instantclient-basic
brew install instantclient-sdk

# Configura variáveis de ambiente
echo 'export ORACLE_HOME=/usr/local/opt/instantclient' >> ~/.zshrc
echo 'export DYLD_LIBRARY_PATH=$ORACLE_HOME:$DYLD_LIBRARY_PATH' >> ~/.zshrc
source ~/.zshrc
```

### Linux (Ubuntu/Debian)
```bash
# Instala Python e Tk
sudo apt-get update
sudo apt-get install python3-dev python3-tk

# Instala Oracle Instant Client
sudo apt-get install libaio1
wget https://download.oracle.com/otn_software/linux/instantclient/instantclient-basic-linux.zip
unzip instantclient-basic-linux.zip
sudo mv instantclient_* /opt/oracle
echo 'export ORACLE_HOME=/opt/oracle/instantclient_*' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=$ORACLE_HOME:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
```

### Windows
1. Instale Python do [python.org](https://www.python.org/downloads/)
   - Marque "Add Python to PATH"
   - Marque "tcl/tk and IDLE"

2. Instale Oracle Instant Client:
   - Baixe de [Oracle Instant Client](https://www.oracle.com/database/technologies/instant-client/winx64-64-downloads.html)
   - Extraia para C:\oracle\instantclient
   - Adicione C:\oracle\instantclient ao PATH

## Configuração do Ambiente

1. Clone o repositório:
```bash
git clone <repository-url>
cd ctwp
```

2. Configure as variáveis de ambiente:
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite com suas credenciais
vim .env
```

3. Execute o script de setup:
```bash
# Dê permissão de execução
chmod +x setup_and_test.sh

# Execute o setup
./setup_and_test.sh
```

## Estrutura do Projeto
```
ctwp/
├── src/
│   ├── main.py              # Ponto de entrada
│   ├── database.py          # Conexão com Oracle
│   ├── ui/
│   │   └── main_window.py   # Interface gráfica
│   └── services/
│       ├── monitoring.py    # Monitoramento
│       ├── optimization.py  # Otimização
│       └── reporting.py     # Relatórios
├── tests/
│   ├── test_database.py
│   ├── test_monitoring.py
│   ├── test_optimization.py
│   ├── test_reporting.py
│   └── test_ui.py
└── requirements.txt
```

## Execução

### Sistema Principal
```bash
# Ative o ambiente virtual
source venv/bin/activate

# Execute o sistema
python src/main.py
```

### Testes
```bash
# Execute todos os testes
./setup_and_test.sh

# Ou execute testes específicos
source venv/bin/activate
python -m pytest tests/test_database.py -v
```

## Funcionalidades

### 1. Monitoramento
- Consumo em tempo real
- Histórico de consumo
- Análise de tarifas
- Métricas de eficiência

### 2. Otimização
- Recomendações automáticas
- Análise de padrões
- Simulação de cenários
- Machine learning

### 3. Relatórios
- Consumo diário
- Análise de eficiência
- Economia mensal
- Fontes renováveis

### 4. Interface Gráfica
- Dashboard em tempo real
- Gráficos interativos
- Controles de configuração
- Visualização de relatórios

## Suporte
Para problemas ou dúvidas, abra uma issue no repositório ou contate o autor:
- Email: rm560586@fiap.com
- RM560586
