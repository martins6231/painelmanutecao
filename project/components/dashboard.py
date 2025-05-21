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

def show_dashboard():
    """Exibe a página do painel principal."""
    
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
                            filtered_data = filter_data(st.session_state.df, selected_machine, selected_month)
                            
                            # Calcular tempo programado
                            scheduled_time, scheduled_hours = calculate_scheduled_time(filtered_data, selected_month)
                            
                            # Calcular indicadores
                            availability = calculate_availability(filtered_data, scheduled_time)
                            efficiency = calculate_operational_efficiency(filtered_data, scheduled_time)
                            average_time = calculate_average_downtime(filtered_data)
                            mtbf, mttr = calculate_mtbf_mttr(filtered_data, scheduled_time)
                            
                            # Calcular tempo total de parada em horas
                            total_downtime = filtered_data['Duração'].sum()
                            total_downtime_hours = total_downtime.total_seconds() / 3600
                            
                            # Gerar recomendações
                            recommendations = generate_recommendations(filtered_data, availability, efficiency)
                            
                            # Análises adicionais
                            area_index = calculate_stoppage_by_area(filtered_data)
                            pareto = pareto_stoppage_causes(filtered_data)
                            occurrences = calculate_stoppage_occurrence_rate(filtered_data)
                            area_time = calculate_total_stoppage_time_by_area(filtered_data)
                            monthly_duration = calculate_total_duration_by_month(filtered_data)
                            frequent_stoppages = most_frequent_stoppages(filtered_data)
                            
                            # Análise de paradas críticas
                            critical_stoppages, critical_percentage = identify_critical_stoppages(filtered_data)
                            top_critical_stoppages = critical_stoppages.groupby('Parada')['Duração'].sum().sort_values(ascending=False).head(10)
                            
                            # Armazenar resultados no estado da sessão
                            st.session_state.resultados = {
                                'filtered_data': filtered_data,
                                'availability': availability,
                                'efficiency': efficiency,
                                'average_time': average_time,
                                'total_downtime': total_downtime,
                                'total_downtime_hours': total_downtime_hours,
                                'total_stoppages': len(filtered_data),
                                'mtbf': mtbf,
                                'mttr': mttr,
                                'area_index': area_index,
                                'pareto': pareto,
                                'occurrences': occurrences,
                                'area_time': area_time,
                                'critical_stoppages': critical_stoppages,
                                'critical_percentage': critical_percentage,
                                'top_critical_stoppages': top_critical_stoppages,
                                'recommendations': recommendations,
                                'selected_machine': selected_machine,
                                'selected_month': selected_month,
                                'scheduled_hours': scheduled_hours,
                                'frequent_stoppages': frequent_stoppages,
                                'monthly_duration': monthly_duration,
                                'date_range': None
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
                                filtered_data = filter_data(
                                    st.session_state.df, 
                                    selected_machine_custom, 
                                    start_date=start_datetime, 
                                    end_date=end_datetime
                                )
                                
                                # Calcular tempo programado baseado no intervalo de datas
                                scheduled_time, scheduled_hours = calculate_scheduled_time(
                                    filtered_data, 
                                    start_date=start_datetime,
                                    end_date=end_datetime
                                )
                                
                                # Calcular indicadores
                                availability = calculate_availability(filtered_data, scheduled_time)
                                efficiency = calculate_operational_efficiency(filtered_data, scheduled_time)
                                average_time = calculate_average_downtime(filtered_data)
                                mtbf, mttr = calculate_mtbf_mttr(filtered_data, scheduled_time)
                                
                                # Calcular tempo total de parada em horas
                                total_downtime = filtered_data['Duração'].sum()
                                total_downtime_hours = total_downtime.total_seconds() / 3600
                                
                                # Gerar recomendações
                                recommendations = generate_recommendations(filtered_data, availability, efficiency)
                                
                                # Análises adicionais
                                area_index = calculate_stoppage_by_area(filtered_data)
                                pareto = pareto_stoppage_causes(filtered_data)
                                occurrences = calculate_stoppage_occurrence_rate(filtered_data)
                                area_time = calculate_total_stoppage_time_by_area(filtered_data)
                                monthly_duration = calculate_total_duration_by_month(filtered_data)
                                frequent_stoppages = most_frequent_stoppages(filtered_data)
                                
                                # Análise de paradas críticas
                                critical_stoppages, critical_percentage = identify_critical_stoppages(filtered_data)
                                top_critical_stoppages = critical_stoppages.groupby('Parada')['Duração'].sum().sort_values(ascending=False).head(10)
                                
                                # Armazenar resultados no estado da sessão
                                st.session_state.resultados = {
                                    'filtered_data': filtered_data,
                                    'availability': availability,
                                    'efficiency': efficiency,
                                    'average_time': average_time,
                                    'total_downtime': total_downtime,
                                    'total_downtime_hours': total_downtime_hours,
                                    'total_stoppages': len(filtered_data),
                                    'mtbf': mtbf,
                                    'mttr': mttr,
                                    'area_index': area_index,
                                    'pareto': pareto,
                                    'occurrences': occurrences,
                                    'area_time': area_time,
                                    'critical_stoppages': critical_stoppages,
                                    'critical_percentage': critical_percentage,
                                    'top_critical_stoppages': top_critical_stoppages,
                                    'recommendations': recommendations,
                                    'selected_machine': selected_machine_custom,
                                    'selected_month': None,
                                    'scheduled_hours': scheduled_hours,
                                    'frequent_stoppages': frequent_stoppages,
                                    'monthly_duration': monthly_duration,
                                    'date_range': (start_date, end_date)
                                }
                        else:
                            st.error("A data inicial não pode ser posterior à data final")
            
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