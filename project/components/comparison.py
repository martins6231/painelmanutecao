import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io
import base64
from utils.data_processing import process_data, filter_data, get_download_link, filter_data_by_date_range
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
                        )
                        
                        data2 = filter_data(
                            st.session_state.df, 
                            selected_machine, 
                            start_date=start_datetime2, 
                            end_date=end_datetime2
                        )
                        
                        # Compare periods
                        comparison_results = compare_periods(data1, data2)
                        
                        # Store results in session state
                        st.session_state.comparison_data = {
                            'period1': (start_date1, end_date1),
                            'period2': (start_date2, end_date2),
                            'machine': selected_machine,
                            'data1': data1,
                            'data2': data2,
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
    
    # Key metrics comparison
    if comparison_data['results']:
        metrics = comparison_data['results']['metrics']
        
        st.markdown('<div class="section-title">Comparação de Métricas</div>', unsafe_allow_html=True)
        
        # Availability and efficiency
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            availability1, availability2, diff_availability, pct_availability = metrics['availability']
            fig_availability = create_comparison_gauge_chart(
                availability1, 
                availability2, 
                "Disponibilidade",
                max_value=100
            )
            st.plotly_chart(fig_availability, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            efficiency1, efficiency2, diff_efficiency, pct_efficiency = metrics['efficiency']
            fig_efficiency = create_comparison_gauge_chart(
                efficiency1, 
                efficiency2, 
                "Eficiência",
                max_value=100
            )
            st.plotly_chart(fig_efficiency, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # MTBF and MTTR
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            mtbf1, mtbf2, diff_mtbf, pct_mtbf = metrics['mtbf']
            fig_mtbf = create_comparative_bar_chart(
                mtbf1, 
                mtbf2, 
                "MTBF"
            )
            st.plotly_chart(fig_mtbf, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            mttr1, mttr2, diff_mttr, pct_mttr = metrics['mttr']
            fig_mttr = create_comparative_bar_chart(
                mttr1, 
                mttr2, 
                "MTTR"
            )
            st.plotly_chart(fig_mttr, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Total stoppages and downtime
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            stoppages1, stoppages2, diff_stoppages, pct_stoppages = metrics['total_stoppages']
            fig_stoppages = create_comparative_bar_chart(
                stoppages1, 
                stoppages2, 
                "Total de Paradas"
            )
            st.plotly_chart(fig_stoppages, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            downtime1, downtime2, diff_downtime, pct_downtime = metrics['total_downtime']
            fig_downtime = create_comparative_bar_chart(
                downtime1, 
                downtime2, 
                "Tempo Total de Parada"
            )
            st.plotly_chart(fig_downtime, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Summary table
        st.markdown('<div class="section-title">Indicadores Chave</div>', unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            
            # Create summary table
            summary_data = {
                "Indicador": [
                    "Disponibilidade",
                    "Eficiência",
                    "MTBF",
                    "MTTR",
                    "Total de Paradas",
                    "Tempo Total de Parada"
                ],
                "Período 1": [
                    f"{availability1:.1f}%",
                    f"{efficiency1:.1f}%",
                    f"{mtbf1:.1f}h",
                    f"{mttr1:.1f}h",
                    f"{int(stoppages1)}",
                    f"{downtime1:.1f}h"
                ],
                "Período 2": [
                    f"{availability2:.1f}%",
                    f"{efficiency2:.1f}%",
                    f"{mtbf2:.1f}h",
                    f"{mttr2:.1f}h",
                    f"{int(stoppages2)}",
                    f"{downtime2:.1f}h"
                ],
                "Variação": [
                    f"{diff_availability:+.1f}%",
                    f"{diff_efficiency:+.1f}%",
                    f"{diff_mtbf:+.1f}h",
                    f"{diff_mttr:+.1f}h",
                    f"{int(diff_stoppages):+d}",
                    f"{diff_downtime:+.1f}h"
                ],
                "Variação (%)": [
                    f"{pct_availability:+.1f}%" if pct_availability != float('inf') else "N/A",
                    f"{pct_efficiency:+.1f}%" if pct_efficiency != float('inf') else "N/A",
                    f"{pct_mtbf:+.1f}%" if pct_mtbf != float('inf') else "N/A",
                    f"{pct_mttr:+.1f}%" if pct_mttr != float('inf') else "N/A",
                    f"{pct_stoppages:+.1f}%" if pct_stoppages != float('inf') else "N/A",
                    f"{pct_downtime:+.1f}%" if pct_downtime != float('inf') else "N/A"
                ],
                "Status": [
                    "🟢" if diff_availability > 0 else ("🔴" if diff_availability < 0 else "⚪"),
                    "🟢" if diff_efficiency > 0 else ("🔴" if diff_efficiency < 0 else "⚪"),
                    "🟢" if diff_mtbf > 0 else ("🔴" if diff_mtbf < 0 else "⚪"),
                    "🟢" if diff_mttr < 0 else ("🔴" if diff_mttr > 0 else "⚪"),
                    "🟢" if diff_stoppages < 0 else ("🔴" if diff_stoppages > 0 else "⚪"),
                    "🟢" if diff_downtime < 0 else ("🔴" if diff_downtime > 0 else "⚪")
                ]
            }
            
            # Convert to DataFrame
            summary_df = pd.DataFrame(summary_data)
            
            # Display summary table
            st.dataframe(
                summary_df,
                use_container_width=True,
                hide_index=True
            )
            
            # Download button
            st.markdown(
                get_download_link(summary_df, 'comparacao_periodos.xlsx', '📥 Baixar Comparação'),
                unsafe_allow_html=True
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Conclusions
        st.markdown('<div class="section-title">Conclusões da Comparação</div>', unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            st.markdown("### 🔍 Resumo da Análise")
            
            # Calculate performance changes
            improved_count = 0
            worsened_count = 0
            
            # For each metric, determine if it improved or worsened
            if diff_availability > 0: improved_count += 1
            elif diff_availability < 0: worsened_count += 1
            
            if diff_efficiency > 0: improved_count += 1
            elif diff_efficiency < 0: worsened_count += 1
            
            if diff_mtbf > 0: improved_count += 1
            elif diff_mtbf < 0: worsened_count += 1
            
            if diff_mttr < 0: improved_count += 1
            elif diff_mttr > 0: worsened_count += 1
            
            if diff_stoppages < 0: improved_count += 1
            elif diff_stoppages > 0: worsened_count += 1
            
            if diff_downtime < 0: improved_count += 1
            elif diff_downtime > 0: worsened_count += 1
            
            # Generate conclusions based on performance changes
            total_metrics = 6
            if improved_count > worsened_count:
                performance_status = "🟢 Melhoria Geral no Desempenho"
                performance_pct = improved_count / total_metrics * 100
                st.markdown(f"**{performance_status}** ({performance_pct:.0f}% dos indicadores melhoraram)")
                
                # Generate detailed insights
                st.markdown("#### Principais Melhorias:")
                if diff_availability > 0:
                    st.markdown(f"- Disponibilidade aumentou em {diff_availability:.1f}% ({pct_availability:+.1f}%)")
                if diff_efficiency > 0:
                    st.markdown(f"- Eficiência aumentou em {diff_efficiency:.1f}% ({pct_efficiency:+.1f}%)")
                if diff_mtbf > 0:
                    st.markdown(f"- MTBF aumentou em {diff_mtbf:.1f}h ({pct_mtbf:+.1f}%)")
                if diff_mttr < 0:
                    st.markdown(f"- MTTR reduziu em {abs(diff_mttr):.1f}h ({pct_mttr:+.1f}%)")
                if diff_stoppages < 0:
                    st.markdown(f"- Total de paradas reduziu em {abs(int(diff_stoppages))} ({pct_stoppages:+.1f}%)")
                if diff_downtime < 0:
                    st.markdown(f"- Tempo total de parada reduziu em {abs(diff_downtime):.1f}h ({pct_downtime:+.1f}%)")
                
                if worsened_count > 0:
                    st.markdown("#### Pontos de Atenção:")
                    if diff_availability < 0:
                        st.markdown(f"- Disponibilidade reduziu em {abs(diff_availability):.1f}% ({pct_availability:+.1f}%)")
                    if diff_efficiency < 0:
                        st.markdown(f"- Eficiência reduziu em {abs(diff_efficiency):.1f}% ({pct_efficiency:+.1f}%)")
                    if diff_mtbf < 0:
                        st.markdown(f"- MTBF reduziu em {abs(diff_mtbf):.1f}h ({pct_mtbf:+.1f}%)")
                    if diff_mttr > 0:
                        st.markdown(f"- MTTR aumentou em {diff_mttr:.1f}h ({pct_mttr:+.1f}%)")
                    if diff_stoppages > 0:
                        st.markdown(f"- Total de paradas aumentou em {int(diff_stoppages)} ({pct_stoppages:+.1f}%)")
                    if diff_downtime > 0:
                        st.markdown(f"- Tempo total de parada aumentou em {diff_downtime:.1f}h ({pct_downtime:+.1f}%)")
            
            elif worsened_count > improved_count:
                performance_status = "🔴 Deterioração Geral no Desempenho"
                performance_pct = worsened_count / total_metrics * 100
                st.markdown(f"**{performance_status}** ({performance_pct:.0f}% dos indicadores pioraram)")
                
                # Generate detailed insights
                st.markdown("#### Pontos de Atenção:")
                if diff_availability < 0:
                    st.markdown(f"- Disponibilidade reduziu em {abs(diff_availability):.1f}% ({pct_availability:+.1f}%)")
                if diff_efficiency < 0:
                    st.markdown(f"- Eficiência reduziu em {abs(diff_efficiency):.1f}% ({pct_efficiency:+.1f}%)")
                if diff_mtbf < 0:
                    st.markdown(f"- MTBF reduziu em {abs(diff_mtbf):.1f}h ({pct_mtbf:+.1f}%)")
                if diff_mttr > 0:
                    st.markdown(f"- MTTR aumentou em {diff_mttr:.1f}h ({pct_mttr:+.1f}%)")
                if diff_stoppages > 0:
                    st.markdown(f"- Total de paradas aumentou em {int(diff_stoppages)} ({pct_stoppages:+.1f}%)")
                if diff_downtime > 0:
                    st.markdown(f"- Tempo total de parada aumentou em {diff_downtime:.1f}h ({pct_downtime:+.1f}%)")
                
                if improved_count > 0:
                    st.markdown("#### Melhorias Observadas:")
                    if diff_availability > 0:
                        st.markdown(f"- Disponibilidade aumentou em {diff_availability:.1f}% ({pct_availability:+.1f}%)")
                    if diff_efficiency > 0:
                        st.markdown(f"- Eficiência aumentou em {diff_efficiency:.1f}% ({pct_efficiency:+.1f}%)")
                    if diff_mtbf > 0:
                        st.markdown(f"- MTBF aumentou em {diff_mtbf:.1f}h ({pct_mtbf:+.1f}%)")
                    if diff_mttr < 0:
                        st.markdown(f"- MTTR reduziu em {abs(diff_mttr):.1f}h ({pct_mttr:+.1f}%)")
                    if diff_stoppages < 0:
                        st.markdown(f"- Total de paradas reduziu em {abs(int(diff_stoppages))} ({pct_stoppages:+.1f}%)")
                    if diff_downtime < 0:
                        st.markdown(f"- Tempo total de parada reduziu em {abs(diff_downtime):.1f}h ({pct_downtime:+.1f}%)")
            
            else:
                performance_status = "⚪ Desempenho Sem Alterações Significativas"
                st.markdown(f"**{performance_status}**")
                st.markdown("O número de melhorias e deteriorações está equilibrado")
            
            # Calculate performance score
            performance_score = (improved_count - worsened_count) / total_metrics * 100
            
            # Recommendations based on performance
            st.markdown("#### Recomendações:")
            if performance_score > 30:
                st.markdown("- Continue com as práticas atuais que estão gerando resultados positivos")
                st.markdown("- Documente as melhorias implementadas para replicar em outras áreas")
                st.markdown("- Estabeleça metas mais desafiadoras para o próximo período")
            elif performance_score > 0:
                st.markdown("- Mantenha o foco nas áreas que apresentaram melhoria")
                st.markdown("- Analise os fatores que contribuíram para o progresso")
                st.markdown("- Implemente ações específicas para os indicadores que precisam de atenção")
            elif performance_score == 0:
                st.markdown("- Identifique os indicadores prioritários para melhoria")
                st.markdown("- Estabeleça um plano de ação estruturado")
                st.markdown("- Realize análise de causa raiz dos problemas persistentes")
            else:
                st.markdown("- Ação urgente necessária para reverter a tendência negativa")
                st.markdown("- Conduza uma investigação detalhada das causas da deterioração")
                st.markdown("- Desenvolva um plano de ação abrangente com metas claras")
                st.markdown("- Estabeleça mecanismos de monitoramento mais frequentes")
            
            st.markdown('</div>', unsafe_allow_html=True)