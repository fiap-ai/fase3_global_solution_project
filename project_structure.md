# Estrutura do Projeto

```
📁 docs/                      # Documentação geral do projeto
├── 📄 main.md               # Documentação técnica principal do projeto
├── 📄 architecture.md       # Arquitetura geral da solução
└── 📄 requirements.md       # Requisitos e especificações gerais

📁 aic/                      # Artificial Intelligence Challenges (10%)
├── 📄 article_analysis.md   # Análise do artigo científico
├── 📄 article_review.md     # Fichamento detalhado do artigo
└── 📄 equipment_study.md    # Análise do equipamento selecionado

📁 aicss/                    # AI with Computer Systems and Sensors (20%)
├── 📄 circuit_design.md     # Design do circuito
├── 📄 components.md         # Especificação dos componentes
└── 📄 firmware.md          # Documentação do firmware

📁 scr/                      # Statistical Computing with R (20%)
├── 📄 data_analysis.md      # Análise exploratória de dados
├── 📄 dataset_selection.md  # Seleção e justificativa do dataset ANEEL
└── 📁 scripts/              # Scripts R para análise
    └── 📄 analysis.R

📁 cds/                      # Cognitive Data Science (20%)
├── 📄 database_design.md    # Design do banco de dados
├── 📄 pipeline.md          # Documentação do pipeline de dados
└── 📁 scripts/              # Scripts SQL e outros
    └── 📄 schema.sql

📁 ctwp/                     # Computational Thinking with Python (20%)
├── 📄 system_design.md      # Design do sistema Python
├── 📄 api_docs.md          # Documentação das APIs
└── 📁 src/                  # Código fonte Python
    └── 📄 main.py

📁 integration/              # Integração (Opcional - 10%)
├── 📄 integration_plan.md   # Plano de integração
└── 📄 video_script.md      # Roteiro do vídeo final

📁 assets/                   # Recursos do projeto
├── 📁 images/              # Imagens e diagramas
└── 📁 data/                # Datasets e outros dados

📄 .env                      # Variáveis de ambiente
📄 .gitignore               # Configuração do Git
📄 README.md                # Visão geral do projeto
```

## Convenções de Nomenclatura

1. Diretórios principais em minúsculas, representando cada disciplina
2. Arquivos em snake_case
3. Documentação em Markdown para melhor compatibilidade
4. Separação clara entre documentação e código fonte

## Organização por Disciplina

### AIC (10%)
- Foco em documentação da análise do artigo e equipamento
- Base teórica para outras disciplinas

### AICSS (20%)
- Documentação técnica do hardware
- Designs e especificações do circuito

### SCR (20%)
- Análises estatísticas
- Scripts R e documentação

### CDS (20%)
- Design e implementação do banco de dados
- Documentação do pipeline de dados

### CTWP (20%)
- Sistema Python
- APIs e integrações

### Integration (10% - Opcional)
- Documentação de integração
- Material para vídeo final

## Documentação Central

O diretório `docs/` contém a documentação principal do projeto:
- main.md: Documentação técnica central
- architecture.md: Arquitetura geral da solução
- requirements.md: Requisitos e especificações

Esta estrutura permite:
1. Fácil navegação
2. Clara separação de responsabilidades
3. Escalabilidade para novas features
4. Manutenção simplificada
5. Integração eficiente entre componentes
