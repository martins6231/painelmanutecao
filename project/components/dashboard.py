import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
from utils.data_processing import process_data, filter_data, get_download_link, calculate_aggregated_metrics
from utils.calculations import (
    calculate_availability, calculate_operational_efficiency, calculate_average_downtime,
    calculate_stoppage_by_area, pareto_stoppage_causes, most_frequent_stoppages,
    calculate_stoppage_occurrence_rate, calculate_total_duration_by_month,
    calculate_total_stoppage_time_by_area, identify_critical_stoppages,
    calculate_mtbf_mttr, calculate_scheduled_time, generate_recommendations
)
from utils.visualizations import (
    create_pareto_chart, create_area_pie_chart, create_occurrences_chart,
    create_monthly_duration_chart, create_area_time_chart, create_critical_stoppages_chart,
    create_critical_areas_pie_chart, create_duration_distribution_chart
)
from utils.i18n import get_translation

def show_dashboard():
    """Exibe a página do painel principal."""
    t = get_translation()
    
    # Seção de upload de dados
    with st.container():
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        st.markdown("### 📤 Upload de Dados")
        
        uploaded_file = st.file_uploader("Selecione um arquivo Excel com os dados de paradas", type=["xlsx", "xls"])
        
        if uploaded_file is not None:
            try:
                with st.spinner('Processando dados...'):
                    df = pd.read_excel(uploaded_file)
                    st.session_state.df = process_data(df)
                    st.success(f"✅ Arquivo carregado com sucesso! {len(st.session_state.df)} registros processados.")
            except Exception as e:
                st.error(f"❌ Erro ao processar o arquivo: {str(e)}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Se dados foram carregados, exibe filtros e análise
    if st.session_state.df is not None:
        with st.container():
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            st.markdown("### 🔍 Filtros de Análise")
            
            tab1, tab2 = st.tabs(["Filtros Padrão", "Período Personalizado"])
            
            with tab1:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Filtro de máquina
                    available_machines = ["Todas"] + sorted(st.session_state.df['Máquina'].unique().tolist())
                    selected_machine = st.selectbox("Selecione a Máquina", available_machines)
                
                with col2:
                    # Filtro de mês
                    available_months = ["Todos"] + sorted(st.session_state.df['Ano-Mês'].unique().tolist())
                    selected_month = st.selectbox("Selecione o Mês", available_months)
                
                # Botão de análise
                analyze_col1, _ = st.columns([1, 3])
                with analyze_col1:
                    if st.button("Analisar", key="btn_analyze_standard", use_container_width=True):
                        with st.spinner('Analisando dados...'):
                            # Filtrar dados
                            filtered_data, _, _ = filter_data(st.session_state.df, selected_machine, selected_month)
                            
                            # Calculate metrics
                            metrics = calculate_aggregated_metrics(filtered_data)
                            
                            # Store results in session state
                            st.session_state.resultados = {
                                'filtered_data': filtered_data,
                                'metrics': metrics,
                                'selected_machine': selected_machine,
                                'selected_month': selected_month
                            }
            
            with tab2:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Filtro de máquina
                    available_machines = ["Todas"] + sorted(st.session_state.df['Máquina'].unique().tolist())
                    selected_machine_custom = st.selectbox("Selecione a Máquina", available_machines, key="machine_custom")
                    
                    # Data inicial
                    min_date = st.session_state.df['Inicio'].min().date()
                    max_date = st.session_state.df['Inicio'].max().date()
                    
                    start_date = st.date_input(
                        "Data Inicial", 
                        value=min_date,
                        min_value=min_date,
                        max_value=max_date,
                        key="start_date"
                    )
                
                with col2:
                    # Data final
                    end_date = st.date_input(
                        "Data Final", 
                        value=max_date,
                        min_value=min_date,
                        max_value=max_date,
                        key="end_date"
                    )
                    
                    # Validar intervalo de datas
                    if start_date > end_date:
                        st.error("A data inicial não pode ser posterior à data final")
                
                # Botão de análise
                analyze_col1, _ = st.columns([1, 3])
                with analyze_col1:
                    if st.button("Analisar", key="btn_analyze_custom", use_container_width=True):
                        if start_date <= end_date:
                            with st.spinner('Analisando dados...'):
                                # Converter datas para datetime
                                start_datetime = datetime.combine(start_date, datetime.min.time())
                                end_datetime = datetime.combine(end_date, datetime.max.time())
                                
                                # Filtrar dados por intervalo de datas
                                filtered_data, _, _ = filter_data(
                                    st.session_state.df, 
                                    selected_machine_custom, 
                                    start_date=start_datetime, 
                                    end_date=end_datetime
                                )
                                
                                # Calculate metrics
                                metrics = calculate_aggregated_metrics(filtered_data)
                                
                                # Store results in session state
                                st.session_state.resultados = {
                                    'filtered_data': filtered_data,
                                    'metrics': metrics,
                                    'selected_machine': selected_machine_custom,
                                    'date_range': (start_date, end_date)
                                }
                        else:
                            st.error("A data inicial não pode ser posterior à data final")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Display results if available
        if 'resultados' in st.session_state and st.session_state.resultados:
            display_analysis_results()

def display_analysis_results():
    """Display the analysis results."""
    results = st.session_state.resultados
    metrics = results['metrics']
    
    # Display metrics
    st.markdown('<div class="section-title">Métricas Principais</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Registros", metrics['total_records'])
    
    with col2:
        st.metric("Máquinas Únicas", metrics['unique_machines'])
    
    with col3:
        total_duration_hours = metrics['total_duration'].total_seconds() / 3600
        st.metric("Duração Total (horas)", f"{total_duration_hours:.2f}")
    
    with col4:
        avg_duration_hours = metrics['avg_duration'].total_seconds() / 3600
        st.metric("Duração Média (horas)", f"{avg_duration_hours:.2f}")
    
    # Display charts
    st.markdown('<div class="section-title">Análise Gráfica</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if len(metrics['monthly_counts']) > 1:
            fig = create_monthly_duration_chart(metrics['monthly_counts'])
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if not metrics['machine_stats'].empty:
            fig = create_pareto_chart(metrics['machine_stats']['Duração']['sum'])
            st.plotly_chart(fig, use_container_width=True)
    
    # Display data table
    st.markdown('<div class="section-title">Dados Detalhados</div>', unsafe_allow_html=True)
    
    st.dataframe(
        results['filtered_data'],
        use_container_width=True,
        height=400
    )
    
    # Download button
    st.markdown(
        get_download_link(results['filtered_data'], 'dados_analisados.xlsx', '📥 Baixar dados analisados'),
        unsafe_allow_html=True
    )