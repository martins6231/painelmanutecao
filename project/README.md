# Análise de Eficiência de Máquinas v3.1.0

Sistema de análise e monitoramento de máquinas industriais, desenvolvido para otimizar a gestão de manutenção e melhorar a tomada de decisões.

## 🚀 Novidades da Versão 3.1.0

### Interface e Usabilidade
- Novo seletor de intervalo de datas na visualização de dados
- Análise de distribuição por turnos de trabalho
- Interface otimizada sem indicador de eficiência
- Layout responsivo e intuitivo
- Melhor organização visual dos elementos

### Análise de Dados
- Painel principal com métricas essenciais
- Análise comparativa entre períodos
- Visualização detalhada dos dados
- Gráficos interativos aprimorados
- Exportação de dados em Excel

### Funcionalidades
- Upload simplificado de dados
- Filtros por máquina e período
- Análise de paradas críticas
- Recomendações automáticas
- Comparação entre períodos

### Melhorias Técnicas
- Otimização de performance
- Código refatorado e organizado
- Melhor tratamento de erros
- Responsividade aprimorada
- Documentação atualizada

## 📊 Principais Recursos

### Indicadores
- Disponibilidade
- MTBF (Tempo Médio Entre Falhas)
- MTTR (Tempo Médio Para Reparo)
- Análise de Paradas Críticas
- Distribuição por Turnos

### Visualizações
- Gráficos de Pareto
- Distribuição por Área
- Tendências Temporais
- Comparativos
- Dashboards Interativos

### Análises
- Paradas por Área
- Causas Principais
- Duração das Paradas
- Frequência de Ocorrências
- Recomendações Automáticas

## 🛠️ Tecnologias

- Python
- Streamlit
- Pandas
- Plotly
- NumPy

## 📋 Requisitos

```
streamlit>=1.22.0
pandas>=2.0.1
numpy>=1.26.0
matplotlib>=3.7.1
seaborn>=0.12.2
plotly>=5.14.1
openpyxl>=3.1.2
xlsxwriter>=3.1.0
streamlit-option-menu>=0.3.2
```

## 📦 Instalação

1. Clone o repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```
3. Execute a aplicação:
```bash
streamlit run app.py
```

## 📄 Formato dos Dados

O sistema aceita arquivos Excel (.xlsx) com as seguintes colunas:

- Máquina: Identificador da máquina
- Inicio: Data/hora início da parada
- Fim: Data/hora fim da parada
- Duração: Tempo de parada
- Parada: Tipo de parada
- Área Responsável: Setor responsável

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor, leia as diretrizes de contribuição antes de submeter pull requests.

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.