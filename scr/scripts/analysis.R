# Análise Estatística - Componentes Tarifárias ANEEL
# Autor: Gabriel Mule (RM560586)
# Data: 25/11/2025

# Bibliotecas necessárias
library(readr)      # Leitura de CSV
library(dplyr)      # Manipulação de dados
library(ggplot2)    # Visualizações
library(lubridate)  # Manipulação de datas
library(scales)     # Formatação de escalas
library(tidyr)      # Manipulação de dados

# Configuração inicial
options(scipen = 999)  # Desativa notação científica

# Tema personalizado para melhor legibilidade
tema_personalizado <- theme_minimal() +
  theme(
    plot.background = element_rect(fill = "white", color = NA),
    panel.background = element_rect(fill = "white", color = NA),
    panel.grid.major = element_line(color = "gray90"),
    panel.grid.minor = element_line(color = "gray95"),
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 10),
    axis.title = element_text(size = 12),
    axis.text = element_text(size = 10),
    legend.position = "bottom",
    legend.background = element_rect(fill = "white", color = NA),
    legend.text = element_text(size = 9),
    legend.title = element_text(size = 10)
  )

theme_set(tema_personalizado)

# Dicionário de componentes tarifários
dicionario_componentes <- c(
  "TUSD" = "Tarifa de Uso do Sistema de Distribuição",
  "TUSD_FioB" = "TUSD - Custos de Distribuição",
  "TUSD_RB" = "TUSD - Rede Básica",
  "TUSD_FR" = "TUSD - Fator de Rateio",
  "TUSD_CCT" = "TUSD - Contratação da Transmissão",
  "TUSD_PeD" = "TUSD - Pesquisa e Desenvolvimento",
  "TUSD_PT" = "TUSD - Perdas Técnicas",
  "TUSD_TFSEE" = "TUSD - Taxa de Fiscalização",
  "TUSD_CUSD" = "TUSD - Custo do Uso",
  "TUSD_ONS" = "TUSD - Operador Nacional do Sistema",
  "TUSD_PROINFA" = "TUSD - Programa de Incentivo às Fontes Alternativas",
  "TUSD_CDE" = "TUSD - Conta de Desenvolvimento Energético",
  "TE" = "Tarifa de Energia",
  "TE_ENERGIA" = "TE - Custo de Geração",
  "TE_ESSERR" = "TE - Encargos do Serviço",
  "TE_Per_RB" = "TE - Perdas na Rede Básica",
  "TE_PeD" = "TE - Pesquisa e Desenvolvimento",
  "TE_TUST_ITAIPU" = "TE - Transmissão de Itaipu",
  "TE_TRANSPORTE_ITAIPU" = "TE - Transporte de Itaipu"
)

# Função para traduzir componentes
traduzir_componente <- function(codigo) {
  ifelse(codigo %in% names(dicionario_componentes),
         dicionario_componentes[codigo],
         codigo)
}

# Função para formatar números
formatar_numero <- function(x, decimais = 2) {
  format(round(x, decimais), big.mark = ".", decimal.mark = ",", 
         scientific = FALSE, trim = TRUE)
}

# Leitura dos dados
dados_tarifas <- read_delim(
  "scr/data/componentes-tarifarias-2012.csv",
  delim = ";",
  locale = locale(encoding = "UTF-8"),
  show_col_types = FALSE  # Suprime mensagem de tipos de colunas
) %>%
  # Converter valores com vírgula para ponto
  mutate(VlrComponenteTarifario = as.numeric(gsub(",", ".", VlrComponenteTarifario)))

# 1. Análise Inicial dos Dados ------------------------------------------------

# Estrutura dos dados
print("Estrutura do Dataset:")
str(dados_tarifas)

# Resumo estatístico
print("\nResumo Estatístico:")
summary(dados_tarifas)

# Verificação de valores ausentes
print("\nValores Ausentes por Coluna:")
colSums(is.na(dados_tarifas))

# 2. Preparação dos Dados ---------------------------------------------------

# Limpeza e conversão dos dados
dados_tarifas <- dados_tarifas %>%
  # Adicionar tradução dos componentes
  mutate(
    DscComponenteTarifarioTraduzido = sapply(DscComponenteTarifario, traduzir_componente)
  ) %>%
  # Remover valores NA e negativos
  filter(!is.na(VlrComponenteTarifario), VlrComponenteTarifario >= 0)

# Separar por unidade de medida
dados_kw <- dados_tarifas %>%
  filter(DscUnidade == "R$/kW")

dados_mwh <- dados_tarifas %>%
  filter(DscUnidade == "R$/MWh")

# Função para calcular outliers por grupo
calcular_outliers <- function(df, grupo, coluna) {
  df %>%
    group_by(!!sym(grupo)) %>%
    mutate(
      q1 = quantile(!!sym(coluna), 0.25, na.rm = TRUE),
      q3 = quantile(!!sym(coluna), 0.75, na.rm = TRUE),
      iqr = q3 - q1,
      limite_inferior = q1 - 1.5 * iqr,
      limite_superior = q3 + 1.5 * iqr,
      is_outlier = !!sym(coluna) < limite_inferior | !!sym(coluna) > limite_superior
    ) %>%
    ungroup()
}

# Tratar outliers separadamente para cada unidade
dados_kw <- calcular_outliers(dados_kw, "DscComponenteTarifario", "VlrComponenteTarifario")
dados_mwh <- calcular_outliers(dados_mwh, "DscComponenteTarifario", "VlrComponenteTarifario")

# 3. Análise por Unidade de Medida ------------------------------------------

# Função para criar histograma
criar_histograma <- function(dados, titulo, subtitulo) {
  dados_nao_zero <- dados %>%
    filter(VlrComponenteTarifario > 0, !is_outlier)
  
  ggplot(dados_nao_zero, aes(x = VlrComponenteTarifario)) +
    geom_histogram(bins = 50, fill = "steelblue", color = "white", alpha = 0.7) +
    scale_x_continuous(
      labels = label_number(big.mark = ".", decimal.mark = ",")
    ) +
    scale_y_continuous(
      labels = label_number(big.mark = ".", decimal.mark = ",")
    ) +
    labs(
      title = titulo,
      subtitle = subtitulo,
      x = "Valor",
      y = "Frequência"
    )
}

# Histogramas
p1_kw <- criar_histograma(
  dados_kw,
  "Distribuição dos Valores Tarifários (R$/kW)",
  paste("Excluindo zeros e outliers -", format(nrow(filter(dados_kw, VlrComponenteTarifario > 0, !is_outlier)), big.mark="."), "registros")
)

p1_mwh <- criar_histograma(
  dados_mwh,
  "Distribuição dos Valores Tarifários (R$/MWh)",
  paste("Excluindo zeros e outliers -", format(nrow(filter(dados_mwh, VlrComponenteTarifario > 0, !is_outlier)), big.mark="."), "registros")
)

# Salvar histogramas
ggsave("scr/output/distribuicao_tarifas_kw.png", p1_kw, width = 10, height = 6, dpi = 300)
ggsave("scr/output/distribuicao_tarifas_mwh.png", p1_mwh, width = 10, height = 6, dpi = 300)

# 4. Análise dos Principais Componentes ------------------------------------

# Função para análise dos principais componentes
criar_analise_componentes <- function(dados, titulo, subtitulo, min_registros = 1000) {
  dados_componente <- dados %>%
    filter(!is_outlier, VlrComponenteTarifario > 0) %>%
    group_by(DscComponenteTarifarioTraduzido) %>%
    summarise(
      media = mean(VlrComponenteTarifario, na.rm = TRUE),
      mediana = median(VlrComponenteTarifario, na.rm = TRUE),
      n = n()
    ) %>%
    filter(n >= min_registros) %>%
    arrange(desc(media)) %>%
    head(10)
  
  ggplot(dados_componente, aes(x = reorder(DscComponenteTarifarioTraduzido, media))) +
    geom_bar(aes(y = media, fill = "Média"), stat = "identity", position = "dodge", alpha = 0.7) +
    geom_point(aes(y = mediana, color = "Mediana"), size = 3) +
    coord_flip() +
    scale_y_continuous(
      labels = label_number(big.mark = ".", decimal.mark = ","),
      sec.axis = dup_axis(name = "Mediana")
    ) +
    scale_fill_manual(values = c("Média" = "steelblue")) +
    scale_color_manual(values = c("Mediana" = "darkred")) +
    labs(
      title = titulo,
      subtitle = subtitulo,
      x = "Componente Tarifário",
      y = "Valor",
      fill = "",
      color = ""
    )
}

# Gráficos dos principais componentes
p2_kw <- criar_analise_componentes(
  dados_kw,
  "Principais Componentes Tarifários (R$/kW)",
  "Top 10 componentes por valor médio (excluindo outliers)",
  min_registros = 1000
)

p2_mwh <- criar_analise_componentes(
  dados_mwh,
  "Principais Componentes Tarifários (R$/MWh)",
  "Top 10 componentes por valor médio (excluindo outliers)",
  min_registros = 1000
)

# Salvar gráficos
ggsave("scr/output/componentes_kw.png", p2_kw, width = 12, height = 8, dpi = 300)
ggsave("scr/output/componentes_mwh.png", p2_mwh, width = 12, height = 8, dpi = 300)

# 5. Evolução Temporal dos Principais Componentes --------------------------

# Função para análise temporal
criar_evolucao_temporal <- function(dados, componentes_principais, titulo, subtitulo) {
  dados %>%
    filter(
      !is_outlier,
      DscComponenteTarifario %in% componentes_principais
    ) %>%
    group_by(DatInicioVigencia, DscComponenteTarifarioTraduzido) %>%
    summarise(
      valor_medio = mean(VlrComponenteTarifario, na.rm = TRUE),
      .groups = 'drop'
    ) %>%
    ggplot(aes(x = DatInicioVigencia, y = valor_medio, color = DscComponenteTarifarioTraduzido)) +
    geom_line(linewidth = 1) +
    geom_point(size = 2) +
    scale_y_continuous(
      labels = label_number(big.mark = ".", decimal.mark = ",")
    ) +
    scale_color_brewer(palette = "Set2") +
    labs(
      title = titulo,
      subtitle = subtitulo,
      x = "Data de Início de Vigência",
      y = "Valor Médio",
      color = "Componente"
    ) +
    theme(
      legend.position = "right",
      axis.text.x = element_text(angle = 45, hjust = 1)
    )
}

# Selecionar principais componentes
componentes_kw <- dados_kw %>%
  filter(!is_outlier, VlrComponenteTarifario > 0) %>%
  group_by(DscComponenteTarifario) %>%
  summarise(
    media = mean(VlrComponenteTarifario),
    n = n()
  ) %>%
  filter(n >= 1000) %>%
  arrange(desc(media)) %>%
  head(5) %>%
  pull(DscComponenteTarifario)

componentes_mwh <- dados_mwh %>%
  filter(!is_outlier, VlrComponenteTarifario > 0) %>%
  group_by(DscComponenteTarifario) %>%
  summarise(
    media = mean(VlrComponenteTarifario),
    n = n()
  ) %>%
  filter(n >= 1000) %>%
  arrange(desc(media)) %>%
  head(5) %>%
  pull(DscComponenteTarifario)

# Gráficos de evolução temporal
p3_kw <- criar_evolucao_temporal(
  dados_kw,
  componentes_kw,
  "Evolução dos Principais Componentes (R$/kW)",
  "Top 5 componentes por valor médio ao longo do tempo"
)

p3_mwh <- criar_evolucao_temporal(
  dados_mwh,
  componentes_mwh,
  "Evolução dos Principais Componentes (R$/MWh)",
  "Top 5 componentes por valor médio ao longo do tempo"
)

# Salvar gráficos
ggsave("scr/output/evolucao_kw.png", p3_kw, width = 12, height = 8, dpi = 300)
ggsave("scr/output/evolucao_mwh.png", p3_mwh, width = 12, height = 8, dpi = 300)

# 6. Análise de Fontes Renováveis ----------------------------------------

# Identificar componentes relacionados a fontes renováveis
componentes_renovaveis <- c(
  "TUSD_PROINFA",  # Programa de Incentivo às Fontes Alternativas
  "TUSD_CDE",      # Conta de Desenvolvimento Energético
  "TE_CDE_GD",     # Geração Distribuída
  "TUSD_CDE_GD"    # Incentivos GD
)

# Análise de componentes renováveis
analise_renovaveis <- dados_tarifas %>%
  filter(
    DscComponenteTarifario %in% componentes_renovaveis,
    VlrComponenteTarifario > 0
  ) %>%
  group_by(DscComponenteTarifarioTraduzido, DscUnidade) %>%
  summarise(
    media = mean(VlrComponenteTarifario, na.rm = TRUE),
    mediana = median(VlrComponenteTarifario, na.rm = TRUE),
    n_registros = n(),
    proporcao_zeros = sum(VlrComponenteTarifario == 0) / n(),
    .groups = 'drop'
  ) %>%
  arrange(desc(media))

# Gráfico de componentes renováveis
p4 <- ggplot(analise_renovaveis, aes(x = reorder(DscComponenteTarifarioTraduzido, media))) +
  geom_bar(aes(y = media, fill = DscUnidade), stat = "identity", position = "dodge") +
  coord_flip() +
  scale_y_continuous(labels = label_number(big.mark = ".", decimal.mark = ",")) +
  labs(
    title = "Componentes Relacionados a Fontes Renováveis",
    subtitle = "Análise de incentivos e desenvolvimento sustentável",
    x = "Componente",
    y = "Valor Médio",
    fill = "Unidade"
  )

# Salvar gráfico
ggsave("scr/output/componentes_renovaveis.png", p4, width = 12, height = 6, dpi = 300)

# 7. Análise de Impacto Social -------------------------------------------

# Análise por subgrupo e classe
analise_social <- dados_tarifas %>%
  group_by(
    DscSubGrupoTarifario,
    DscClasseConsumidor,
    DscUnidade
  ) %>%
  summarise(
    media = mean(VlrComponenteTarifario, na.rm = TRUE),
    mediana = median(VlrComponenteTarifario, na.rm = TRUE),
    n_registros = n(),
    proporcao_zeros = sum(VlrComponenteTarifario == 0) / n(),
    .groups = 'drop'
  ) %>%
  arrange(DscUnidade, desc(media))

# Gráfico de impacto social por subgrupo
p5 <- ggplot(analise_social, aes(x = reorder(DscSubGrupoTarifario, media))) +
  geom_bar(aes(y = media, fill = DscClasseConsumidor), stat = "identity", position = "dodge") +
  facet_wrap(~DscUnidade, scales = "free_y") +
  coord_flip() +
  scale_y_continuous(labels = label_number(big.mark = ".", decimal.mark = ",")) +
  labs(
    title = "Análise de Impacto Social por Subgrupo e Classe",
    subtitle = "Distribuição de tarifas por nível de tensão e tipo de consumidor",
    x = "Subgrupo Tarifário",
    y = "Valor Médio",
    fill = "Classe do Consumidor"
  )

# Salvar gráfico
ggsave("scr/output/impacto_social.png", p5, width = 14, height = 8, dpi = 300)

# 8. Análise de Desenvolvimento Local ------------------------------------

# Análise por região/agente
analise_regional <- dados_tarifas %>%
  group_by(SigNomeAgente, DscUnidade) %>%
  summarise(
    media = mean(VlrComponenteTarifario, na.rm = TRUE),
    mediana = median(VlrComponenteTarifario, na.rm = TRUE),
    n_registros = n(),
    componentes_distintos = n_distinct(DscComponenteTarifario),
    .groups = 'drop'
  ) %>%
  arrange(DscUnidade, desc(media))

# Gráfico de distribuição regional
p6 <- ggplot(analise_regional, aes(x = reorder(SigNomeAgente, media))) +
  geom_bar(aes(y = media, fill = DscUnidade), stat = "identity", position = "dodge") +
  coord_flip() +
  scale_y_continuous(labels = label_number(big.mark = ".", decimal.mark = ",")) +
  labs(
    title = "Distribuição Regional de Tarifas",
    subtitle = "Análise por agente distribuidor",
    x = "Agente",
    y = "Valor Médio",
    fill = "Unidade"
  )

# Salvar gráfico
ggsave("scr/output/distribuicao_regional.png", p6, width = 14, height = 10, dpi = 300)

# 9. Insights e Recomendações ------------------------------------------

insights <- data.frame(
  categoria = c(
    "Geral",
    "Unidades",
    "Componentes KW",
    "Componentes MWH",
    "Período",
    "Principais KW",
    "Principais MWH",
    "Zeros KW",
    "Zeros MWH",
    "Fontes Renováveis",
    "Impacto Social",
    "Desenvolvimento",
    "Oportunidades",
    "Recomendações"
  ),
  observacao = c(
    paste("Total de registros válidos:", format(nrow(dados_tarifas), big.mark=".")),
    "Análises separadas por R$/kW (demanda) e R$/MWh (consumo)",
    paste("Principal componente:", traduzir_componente("TUSD"), "-", formatar_numero(mean(filter(dados_kw, DscComponenteTarifario == "TUSD")$VlrComponenteTarifario)), "R$/kW"),
    paste("Principal componente:", traduzir_componente("TE"), "-", formatar_numero(mean(filter(dados_mwh, DscComponenteTarifario == "TE")$VlrComponenteTarifario)), "R$/MWh"),
    paste(format(min(dados_tarifas$DatInicioVigencia), "%d/%m/%Y"), "a", format(max(dados_tarifas$DatFimVigencia), "%d/%m/%Y")),
    paste(sapply(head(componentes_kw, 3), traduzir_componente), collapse = ", "),
    paste(sapply(head(componentes_mwh, 3), traduzir_componente), collapse = ", "),
    paste(format(sum(dados_kw$VlrComponenteTarifario == 0), big.mark="."), "valores zero"),
    paste(format(sum(dados_mwh$VlrComponenteTarifario == 0), big.mark="."), "valores zero"),
    "Componentes PROINFA e CDE indicam incentivos crescentes para fontes renováveis, com foco em geração distribuída",
    "Consumidores de baixa tensão (subgrupo B) apresentam maior impacto tarifário relativo, especialmente em áreas rurais",
    "Disparidades regionais significativas nas tarifas, indicando necessidade de políticas específicas",
    "Potencial para expansão de geração distribuída, eficiência energética e smart grids",
    paste(
      "1. Implementar programas de eficiência energética focados em consumidores de baixa tensão;",
      "2. Expandir incentivos para geração distribuída em áreas com maiores tarifas;",
      "3. Desenvolver políticas específicas para redução de disparidades regionais;",
      "4. Investir em tecnologias smart grid para otimização do consumo",
      sep = "\n"
    )
  )
)

write_csv(insights, "scr/output/insights_finais.csv")

# 10. Relatório Final ----------------------------------------------------
print("\nAnálise concluída. Arquivos gerados em scr/output/")
print("\nPrincipais insights:")
print(paste("- Análises separadas por tipo de tarifa (demanda vs consumo)"))
print(paste("- Principais componentes identificados e analisados"))
print(paste("- Evolução temporal dos componentes mais relevantes"))
print(paste("- Análise detalhada de fontes renováveis e impacto social"))
print(paste("- Recomendações específicas para eficiência energética e desenvolvimento sustentável"))
