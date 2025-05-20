import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
from utils.data_processing import process_data, filter_data, get_month_name, get_download_link
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
            st.markdown(f"### 🔍 {t('analysis_filters')}")
            
            # Create tabs for basic and advanced filters
            basic_tab, advanced_tab = st.tabs([t("filter_settings"), t("advanced_filters")])
            
            with basic_tab:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Machine filter
                    available_machines = ["Todas"] + sorted(st.session_state.df['Máquina'].unique().tolist())
                    selected_machine = st.selectbox(t("select_machine"), available_machines)
                
                with col2:
                    # Month filter
                    available_months = ["Todos"] + sorted(st.session_state.df['Ano-Mês'].unique().tolist())
                    selected_month = st.selectbox(t("select_month"), available_months)
            
            with advanced_tab:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Weekend filter
                    only_weekends = st.checkbox(t("only_weekends"), key="weekend_filter")
                    
                    # Night shift filter
                    only_night_shift = st.checkbox(t("only_night_shift"), key="night_shift_filter")
                
                with col2:
                    # Responsible area filter
                    available_areas = [t("all_areas")] + sorted(st.session_state.df['Área Responsável'].unique().tolist())
                    selected_area = st.selectbox(t("responsible_area"), available_areas, key="area_filter")
            
            # Analysis button
            analyze_col1, clear_col, _ = st.columns([1, 1, 2])
            with analyze_col1:
                if st.button(t("analyze_button"), key="btn_analyze", use_container_width=True):
                    with st.spinner(t("analyzing_data")):
                        # Convert area selection to internal format
                        area_for_filter = None if selected_area == t("all_areas") else selected_area
                        
                        # Filter data with all criteria
                        filtered_data = filter_data(
                            st.session_state.df,
                            selected_machine,
                            selected_month,
                            only_weekends=only_weekends,
                            only_night_shift=only_night_shift,
                            responsible_area=area_for_filter
                        )
                        
                        if filtered_data.empty:
                            st.warning(t("no_data_after_filters"))
                            return
                        
                        # Continue with existing analysis code...
                        
            with clear_col:
                if st.button(t("clear_filters"), key="btn_clear_filters", use_container_width=True):
                    st.session_state.weekend_filter = False
                    st.session_state.night_shift_filter = False
                    st.session_state.area_filter = t("all_areas")
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Exibir resultados se disponíveis
        if 'resultados' in st.session_state and st.session_state.resultados:
            display_analysis_results()

def display_analysis_results():
    """Exibe os resultados da análise."""
    results = st.session_state.resultados
    
    # Obter texto da máquina e período
    machine_text = results['selected_machine']
    
    if results['date_range']:
        start_date, end_date = results['date_range']
        period_text = f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}"
    else:
        period_text = get_month_name(results['selected_month'])
    
    # Título da seção de resultados
    st.markdown(f'<div class="section-title">Resultados da Análise: {machine_text} - {period_text}</div>', unsafe_allow_html=True)
    
    # Indicadores principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-value">{results['availability']:.1f}%</div>
                <div class="metric-label">Disponibilidade</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-value">{results['efficiency']:.1f}%</div>
                <div class="metric-label">Eficiência</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-value">{results['mtbf']:.1f}h</div>
                <div class="metric-label">MTBF</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col4:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-value">{results['mttr']:.1f}h</div>
                <div class="metric-label">MTTR</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    # Resumo da análise
    with st.container():
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        st.markdown("### 📊 Resumo da Análise")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Período Analisado:** {period_text}")
            st.markdown(f"**Máquina:** {machine_text}")
            st.markdown(f"**Tempo Programado:** {results['scheduled_hours']:.1f} horas")
        
        with col2:
            st.markdown(f"**Total de Paradas:** {results['total_stoppages']} ocorrências")
            st.markdown(f"**Tempo Total de Paradas:** {results['total_downtime_hours']:.1f} horas")
            average_minutes = results['average_time'].total_seconds() / 60 if not pd.isna(results['average_time']) else 0
            st.markdown(f"**Tempo Médio por Parada:** {average_minutes:.1f} minutos")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tabelas de resumo
    st.markdown('<div class="section-title">Tabelas de Resumo</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        st.markdown("### 📋 Top 10 Paradas Mais Frequentes")
        
        if not results['frequent_stoppages'].empty:
            # Criar DataFrame para melhor formatação
            df_frequent = pd.DataFrame({
                'Tipo de Parada': results['frequent_stoppages'].index,
                'Número de Paradas': results['frequent_stoppages'].values
            })
            
            st.dataframe(
                df_frequent,
                column_config={
                    'Tipo de Parada': st.column_config.TextColumn('Tipo de Parada'),
                    'Número de Paradas': st.column_config.NumberColumn('Número de Paradas', format="%d")
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Dados insuficientes para análise")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        st.markdown("### ⏱️ Top 10 Paradas Mais Longas")
        
        if not results['pareto'].empty:
            # Converter durações para horas
            pareto_hours = results['pareto'].apply(lambda x: x.total_seconds() / 3600)
            
            # Criar DataFrame para melhor formatação
            df_longest = pd.DataFrame({
                'Tipo de Parada': pareto_hours.index,
                'Duração Total (horas)': pareto_hours.values
            })
            
            st.dataframe(
                df_longest,
                column_config={
                    'Tipo de Parada': st.column_config.TextColumn('Tipo de Parada'),
                    'Duração Total (horas)': st.column_config.NumberColumn('Duração Total (horas)', format="%.2f")
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Dados insuficientes para análise")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Análise temporal
    st.markdown('<div class="section-title">Análise Temporal</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_occurrences = create_occurrences_chart(results['occurrences'])
        if fig_occurrences:
            st.plotly_chart(fig_occurrences, use_container_width=True)
        else:
            st.info("Dados insuficientes para análise")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_monthly_duration = create_monthly_duration_chart(results['monthly_duration'])
        if fig_monthly_duration:
            st.plotly_chart(fig_monthly_duration, use_container_width=True)
        else:
            st.info("Dados insuficientes para análise")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Análise gráfica
    st.markdown('<div class="section-title">Análise Gráfica</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_pareto = create_pareto_chart(results['pareto'])
        if fig_pareto:
            st.plotly_chart(fig_pareto, use_container_width=True)
        else:
            st.info("Dados insuficientes para análise")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_area = create_area_pie_chart(results['area_index'])
        if fig_area:
            st.plotly_chart(fig_area, use_container_width=True)
        else:
            st.info("Dados insuficientes para análise")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Segunda linha de gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_area_time = create_area_time_chart(results['area_time'])
        if fig_area_time:
            st.plotly_chart(fig_area_time, use_container_width=True)
        else:
            st.info("Dados insuficientes para análise")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_distribution = create_duration_distribution_chart(results['filtered_data'])
        if fig_distribution:
            st.plotly_chart(fig_distribution, use_container_width=True)
        else:
            st.info("Dados insuficientes para análise")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Análise de paradas críticas
    st.markdown('<div class="section-title">Análise de Paradas Críticas</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_critical_stoppages = create_critical_stoppages_chart(results['top_critical_stoppages'])
        if fig_critical_stoppages:
            st.plotly_chart(fig_critical_stoppages, use_container_width=True)
        else:
            st.info("Dados insuficientes para análise")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig_critical_areas = create_critical_areas_pie_chart(results['critical_stoppages'])
        if fig_critical_areas:
            st.plotly_chart(fig_critical_areas, use_container_width=True)
        else:
            st.info("Dados insuficientes para análise")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Recomendações
    st.markdown('<div class="section-title">Recomendações</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        st.markdown("### 💡 Insights e Ações Recomendadas")
        
        for rec in results['recommendations']:
            st.markdown(f"- {rec}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Exportar resultados
    with st.container():
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        st.markdown("### 📥 Exportar Resultados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Exportar dados filtrados
            st.markdown(
                get_download_link(results['filtered_data'], 'dados_analisados.xlsx', '📥 Baixar dados analisados'),
                unsafe_allow_html=True
            )
        
        with col2:
            # Exportar paradas críticas
            if not results['critical_stoppages'].empty:
                st.markdown(
                    get_download_link(results['critical_stoppages'], 'paradas_criticas.xlsx', '📥 Baixar paradas críticas'),
                    unsafe_allow_html=True
                )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Botão para limpar dados
    with st.container():
        clear_col1, _ = st.columns([1, 3])
        with clear_col1:
            if st.button("Limpar Dados", key="btn_clear", use_container_width=True):
                st.session_state.resultados = None
                st.session_state.df = None
                st.rerun()
