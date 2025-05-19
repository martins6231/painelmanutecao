# Análise de Eficiência de Máquinas v3.0.0

Sistema de análise e monitoramento de eficiência de máquinas industriais, desenvolvido para otimizar a gestão de manutenção e melhorar a tomada de decisões.

## 🚀 Novidades da Versão 3.0.0

### Interface e Usabilidade
- Interface totalmente em português brasileiro
- Novo layout otimizado sem barra lateral
- Tipografia padronizada e mais legível
- Melhor hierarquia visual dos elementos
- Navegação simplificada e intuitiva

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
- Eficiência Operacional
- MTBF (Tempo Médio Entre Falhas)
- MTTR (Tempo Médio Para Reparo)
- Análise de Paradas Críticas

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