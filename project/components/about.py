import streamlit as st
import pandas as pd

def show_about():
    """Exibe a página de informações."""
    
    st.markdown('<div class="section-title">Sobre a Aplicação</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image("https://img.icons8.com/fluency/240/factory.png", width=150)
        
        with col2:
            st.markdown("""
            # Análise de Eficiência de Máquinas
            
            Sistema desenvolvido para análise e monitoramento de eficiência de máquinas industriais, 
            oferecendo insights valiosos para otimização da manutenção e melhoria contínua dos processos.
            """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Funcionalidades
    with st.container():
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        st.markdown("## ✨ Funcionalidades")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 📊 Análise de Dados
            - Indicadores de disponibilidade e eficiência
            - Identificação das principais causas de parada
            - Análise da distribuição de paradas
            - Acompanhamento da evolução temporal
            """)
        
        with col2:
            st.markdown("""
            ### 🔍 Recursos Adicionais
            - Filtros por máquina e período
            - Exportação de dados
            - Visualizações interativas
            - Recomendações automáticas
            - Comparação entre períodos
            """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Como usar
    with st.container():
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        st.markdown("## 🚀 Como Usar")
        
        st.markdown("""
        1. **Upload de Dados**: Faça o upload do arquivo Excel com os dados de paradas
        2. **Filtros**: Selecione a máquina e o período desejado
        3. **Análise**: Visualize os indicadores e gráficos gerados
        4. **Comparação**: Compare diferentes períodos
        5. **Exportação**: Baixe os resultados em formato Excel
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Formato dos dados
    with st.container():
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        st.markdown("## 📋 Formato dos Dados")
        
        st.markdown("""
        O arquivo Excel deve conter as seguintes colunas:
        
        - **Máquina**: Identificador da máquina
        - **Início**: Data/hora de início da parada
        - **Fim**: Data/hora de fim da parada
        - **Duração**: Tempo de duração da parada
        - **Parada**: Tipo/motivo da parada
        - **Área Responsável**: Setor responsável pela parada
        """)
        
        # Dados de exemplo
        st.markdown("### Exemplo de Dados")
        
        example_data = pd.DataFrame({
            'Máquina': [78, 79, 80, 89, 91],
            'Inicio': pd.date_range(start='2023-01-01', periods=5, freq='D'),
            'Fim': pd.date_range(start='2023-01-01 02:00:00', periods=5, freq='D'),
            'Duração': ['02:00:00', '02:00:00', '02:00:00', '02:00:00', '02:00:00'],
            'Parada': ['Manutenção', 'Erro de Configuração', 'Falta de Insumos', 'Falha Elétrica', 'Troca de Produto'],
            'Área Responsável': ['Manutenção', 'Operação', 'Logística', 'Manutenção', 'Produção']
        })
        
        st.dataframe(example_data, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tecnologias utilizadas
    with st.container():
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        st.markdown("## 🛠️ Tecnologias Utilizadas")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### Frontend
            - **Streamlit**: Interface interativa
            - **Plotly**: Gráficos dinâmicos
            - **HTML/CSS**: Estilização
            """)
        
        with col2:
            st.markdown("""
            ### Análise de Dados
            - **Pandas**: Processamento de dados
            - **NumPy**: Cálculos numéricos
            - **Matplotlib/Seaborn**: Visualizações
            """)
        
        with col3:
            st.markdown("""
            ### Infraestrutura
            - **Streamlit Cloud**: Hospedagem
            - **GitHub**: Versionamento
            - **Python**: Linguagem base
            """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Requisitos do sistema
    with st.expander("📦 Requisitos do Sistema"):
        st.code("""
        # requirements.txt
        streamlit>=1.22.0
        pandas>=2.0.1
        numpy>=1.26.0
        matplotlib>=3.7.1
        seaborn>=0.12.2
        plotly>=5.14.1
        openpyxl>=3.1.2
        xlsxwriter>=3.1.0
        streamlit-option-menu>=0.3.2
        """)