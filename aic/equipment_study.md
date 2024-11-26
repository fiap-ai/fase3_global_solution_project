# Análise do Equipamento - Sistema de Ar Condicionado

## 1. Critérios de Seleção

### 1.1 Justificativa da Escolha
O sistema de ar condicionado foi selecionado como caso de estudo pelos seguintes fatores:
- Alto consumo energético (representa ~60% do consumo residencial)
- Uso frequente e programável
- Grande potencial de otimização
- Facilidade de monitoramento via sensores
- Impacto significativo na conta de energia

### 1.2 Comparação com Outras Opções

| Critério               | Ar Condicionado | Geladeira    | Chuveiro Elétrico |
|-----------------------|-----------------|--------------|-------------------|
| Consumo Energético    | Alto           | Médio        | Muito Alto       |
| Frequência de Uso     | Variável       | Constante    | Pontual          |
| Potencial Otimização  | Alto           | Médio        | Baixo            |
| Facilidade Monitoramento | Alta        | Média        | Baixa            |
| Impacto na Conta      | Alto           | Médio        | Alto             |
| Controle Automático   | Possível       | Limitado     | Limitado         |

## 2. Análise Técnica

### 2.1 Características do Equipamento
- Potência média: 1500W
- Tensão: 220V
- Corrente: ~7A
- Ciclo: Frio
- Capacidade: 12000 BTUs
- Eficiência energética: Classe A

### 2.2 Padrões de Uso
- Uso diário: 8-12 horas
- Picos: 13h-15h e 19h-22h
- Sazonalidade: maior uso no verão
- Temperatura média configurada: 23°C
- Variação de temperatura: ±2°C

### 2.3 Perfil de Carga
- Consumo em standby: 5W
- Pico inicial: 2000W (15s)
- Consumo médio: 1200W
- Ciclo de trabalho: 70%

## 3. Oportunidades de Otimização

### 3.1 Controle Inteligente
- Ajuste automático baseado em ocupação
- Programação por horários
- Adaptação à temperatura externa
- Integração com preço dinâmico de energia
- Controle preditivo baseado em padrões

### 3.2 Monitoramento
- Temperatura ambiente
- Temperatura externa
- Umidade
- Consumo energético
- Presença de pessoas
- Qualidade do ar

### 3.3 Economia Potencial
- Redução de 20-30% no consumo
- Economia mensal estimada: R$ 150-200
- Payback esperado: 12-15 meses
- ROI anual: 80-100%

## 4. Requisitos Técnicos

### 4.1 Sensores Necessários
- Temperatura (interno/externo)
- Umidade
- Presença
- Corrente elétrica
- Qualidade do ar (opcional)

### 4.2 Atuadores
- Controle de liga/desliga
- Ajuste de temperatura
- Controle de velocidade do ventilador
- Direcionamento do fluxo de ar

### 4.3 Conectividade
- WiFi para comunicação
- Protocolo MQTT
- API REST para integração
- Armazenamento local de dados

## 5. Impactos

### 5.1 Conforto Térmico
- Manutenção da temperatura ideal
- Redução de variações bruscas
- Melhor qualidade do ar
- Adaptação às preferências do usuário

### 5.2 Vida Útil do Equipamento
- Redução de ciclos desnecessários
- Manutenção preventiva
- Operação otimizada
- Menor desgaste

### 5.3 Impacto Ambiental
- Redução de emissões de CO2
- Menor consumo energético
- Uso mais eficiente
- Suporte a energia renovável

## 6. Integração com o Projeto

### 6.1 Hardware (AICSS)
- ESP32 como controlador
- Sensores de temperatura/umidade
- Sensor de presença
- Medidor de consumo

### 6.2 Software (CTWP)
- Interface de controle
- Algoritmos de otimização
- Dashboard de monitoramento
- APIs de integração

### 6.3 Análise de Dados (SCR/CDS)
- Coleta de métricas
- Análise de padrões
- Previsão de consumo
- Otimização contínua

## 7. Riscos e Mitigações

### 7.1 Técnicos
- Falha de comunicação → Buffer local
- Erro de leitura → Redundância de sensores
- Problema no controle → Modo manual de fallback

### 7.2 Operacionais
- Desconforto térmico → Limites configuráveis
- Consumo excessivo → Alertas e limites
- Falha do equipamento → Monitoramento preventivo

## 8. Próximos Passos
1. Especificação detalhada dos sensores
2. Desenvolvimento do circuito de controle
3. Implementação do firmware básico
4. Testes iniciais de comunicação
5. Integração com sistema principal
