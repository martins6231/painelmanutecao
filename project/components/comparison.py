import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io
import base64
from utils.data_processing import process_data, filter_data, get_download_link, calculate_aggregated_metrics
from utils.calculations import compare_periods
from utils.visualizations import create_comparison_gauge_chart, create_comparative_bar_chart
from utils.i18n import get_translation

def show_comparison():
    """Display the period comparison page."""
    t = get_translation()
    
    # Check if data is loaded
    if st.session_state.df is None:
        st.warning("Nenhum dado foi carregado. Por favor, faça o upload de um arquivo Excel na página inicial.")
        return
    
    # Title
    st.markdown('<div class="section-title">Comparação de Períodos</div>', unsafe_allow_html=True)
    
    # Comparison setup
    with st.container():
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        st.markdown("### 📊 Selecionar Períodos")
        
        # Machine filter
        available_machines = ["Todas"] + sorted(st.session_state.df['Máquina'].unique().tolist())
        selected_machine = st.selectbox("Selecione a Máquina", available_machines, key="comparison_machine")
        
        # Period selection
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Período 1")
            
            # Date range for period 1
            min_date = st.session_state.df['Inicio'].min().date()
            max_date = st.session_state.df['Inicio'].max().date()
            
            # Default to last month for period 1
            default_end_date1 = max_date - timedelta(days=30)
            default_start_date1 = default_end_date1 - timedelta(days=29)
            
            start_date1 = st.date_input(
                "Data Inicial", 
                value=default_start_date1,
                min_value=min_date,
                max_value=max_date,
                key="start_date1"
            )
            
            end_date1 = st.date_input(
                "Data Final", 
                value=default_end_date1,
                min_value=min_date,
                max_value=max_date,
                key="end_date1"
            )
            
            # Validate date range
            if start_date1 > end_date1:
                st.error("A data inicial não pode ser posterior à data final")
        
        with col2:
            st.markdown("#### Período 2")
            
            # Date range for period 2
            # Default to current month for period 2
            default_start_date2 = max_date - timedelta(days=29)
            
            start_date2 = st.date_input(
                "Data Inicial", 
                value=default_start_date2,
                min_value=min_date,
                max_value=max_date,
                key="start_date2"
            )
            
            end_date2 = st.date_input(
                "Data Final", 
                value=max_date,
                min_value=min_date,
                max_value=max_date,
                key="end_date2"
            )
            
            # Validate date range
            if start_date2 > end_date2:
                st.error("A data inicial não pode ser posterior à data final")
        
        # Compare button
        compare_col1, _ = st.columns([1, 3])
        with compare_col1:
            if st.button("Comparar Períodos", key="btn_compare", use_container_width=True):
                if start_date1 <= end_date1 and start_date2 <= end_date2:
                    with st.spinner('Analisando dados...'):
                        # Convert dates to datetime
                        start_datetime1 = datetime.combine(start_date1, datetime.min.time())
                        end_datetime1 = datetime.combine(end_date1, datetime.max.time())
                        
                        start_datetime2 = datetime.combine(start_date2, datetime.min.time())
                        end_datetime2 = datetime.combine(end_date2, datetime.max.time())
                        
                        # Filter data for both periods
                        data1 = filter_data(
                            st.session_state.df, 
                            selected_machine, 
                            start_date=start_datetime1, 
                            end_date=end_datetime1
                        )[0]  # Get only the filtered data, ignore pagination info
                        
                        data2 = filter_data(
                            st.session_state.df, 
                            selected_machine, 
                            start_date=start_datetime2, 
                            end_date=end_datetime2
                        )[0]  # Get only the filtered data, ignore pagination info
                        
                        # Calculate metrics for both periods
                        metrics1 = calculate_aggregated_metrics(data1)
                        metrics2 = calculate_aggregated_metrics(data2)
                        
                        # Compare periods
                        comparison_results = compare_periods(data1, data2)
                        
                        # Store results in session state
                        st.session_state.comparison_data = {
                            'period1': (start_date1, end_date1),
                            'period2': (start_date2, end_date2),
                            'machine': selected_machine,
                            'data1': data1,
                            'data2': data2,
                            'metrics1': metrics1,
                            'metrics2': metrics2,
                            'results': comparison_results
                        }
                else:
                    if start_date1 > end_date1:
                        st.error("Período 1: A data inicial não pode ser posterior à data final")
                    if start_date2 > end_date2:
                        st.error("Período 2: A data inicial não pode ser posterior à data final")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display comparison results if available
    if 'comparison_data' in st.session_state and st.session_state.comparison_data:
        display_comparison_results()

def display_comparison_results():
    """Display the period comparison results."""
    comparison_data = st.session_state.comparison_data
    
    # Title
    st.markdown('<div class="section-title">Resultados da Comparação</div>', unsafe_allow_html=True)
    
    # Period information
    with st.container():
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        st.markdown("### 📅 Comparação de Períodos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            start_date1, end_date1 = comparison_data['period1']
            st.markdown(f"**Período 1:** {start_date1.strftime('%d/%m/%Y')} - {end_date1.strftime('%d/%m/%Y')}")
            st.markdown(f"**Duração:** {(end_date1 - start_date1).days + 1} dias")
            st.markdown(f"**Máquina:** {comparison_data['machine']}")
            st.markdown(f"**Total de Paradas:** {len(comparison_data['data1'])}")
        
        with col2:
            start_date2, end_date2 = comparison_data['period2']
            st.markdown(f"**Período 2:** {start_date2.strftime('%d/%m/%Y')} - {end_date2.strftime('%d/%m/%Y')}")
            st.markdown(f"**Duração:** {(end_date2 - start_date2).days + 1} dias")
            st.markdown(f"**Total de Paradas:** {len(comparison_data['data2'])}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display metrics comparison
    metrics1 = comparison_data['metrics1']
    metrics2 = comparison_data['metrics2']
    
    st.markdown('<div class="section-title">Comparação de Métricas</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total de Registros",
            metrics2['total_records'],
            metrics2['total_records'] - metrics1['total_records']
        )
    
    with col2:
        duration_diff = (metrics2['total_duration'] - metrics1['total_duration']).total_seconds() / 3600
        st.metric(
            "Duração Total (horas)",
            f"{metrics2['total_duration'].total_seconds() / 3600:.2f}",
            f"{duration_diff:+.2f}"
        )
    
    with col3:
        avg_duration_diff = (metrics2['avg_duration'] - metrics1['avg_duration']).total_seconds() / 3600
        st.metric(
            "Duração Média (horas)",
            f"{metrics2['avg_duration'].total_seconds() / 3600:.2f}",
            f"{avg_duration_diff:+.2f}"
        )
    
    # Display charts
    st.markdown('<div class="section-title">Análise Gráfica</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if len(metrics1['monthly_counts']) > 0 and len(metrics2['monthly_counts']) > 0:
            fig = create_comparative_bar_chart(
                metrics1['monthly_counts'].mean(),
                metrics2['monthly_counts'].mean(),
                "Média de Registros por Mês"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if not metrics1['machine_stats'].empty and not metrics2['machine_stats'].empty:
            fig = create_comparison_gauge_chart(
                metrics1['machine_stats']['Duração']['mean'].total_seconds() / 3600,
                metrics2['machine_stats']['Duração']['mean'].total_seconds() / 3600,
                "Duração Média por Máquina (horas)"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Download buttons
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown("### 📥 Exportar Resultados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(
            get_download_link(comparison_data['data1'], 'periodo1.xlsx', '📥 Baixar dados do Período 1'),
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            get_download_link(comparison_data['data2'], 'periodo2.xlsx', '📥 Baixar dados do Período 2'),
            unsafe_allow_html=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)