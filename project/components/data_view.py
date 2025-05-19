import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_processing import get_download_link, calculate_aggregated_metrics
from utils.i18n import get_translation

def show_data_view():
    """Display the data view page with pagination."""
    t = get_translation()
    
    if st.session_state.df is not None:
        st.markdown(f'<div class="section-title">{t("data_visualization")}</div>', unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            
            # Filter options
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                available_machines = [t('all')] + sorted(st.session_state.df['Máquina'].unique().tolist())
                machine_filter = st.selectbox(t('filter_by_machine'), available_machines, key="data_machine_filter")
            
            with col2:
                available_months = [t('all')] + sorted(st.session_state.df['Ano-Mês'].unique().tolist())
                month_filter = st.selectbox(t('filter_by_month'), available_months, key="data_month_filter")
            
            with col3:
                items_per_page = st.selectbox(
                    "Itens por página",
                    options=[100, 500, 1000, 5000],
                    index=0
                )
            
            # Initialize page number in session state if not exists
            if 'current_page' not in st.session_state:
                st.session_state.current_page = 1
            
            # Apply filters with pagination
            filtered_data, total_items, total_pages = filter_data(
                st.session_state.df,
                machine_filter,
                month_filter,
                page=st.session_state.current_page,
                items_per_page=items_per_page
            )
            
            # Pagination controls
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                st.markdown(f"**Página {st.session_state.current_page} de {total_pages}**")
                prev, _, next = st.columns([1, 2, 1])
                
                if prev.button("← Anterior") and st.session_state.current_page > 1:
                    st.session_state.current_page -= 1
                    st.rerun()
                
                if next.button("Próxima →") and st.session_state.current_page < total_pages:
                    st.session_state.current_page += 1
                    st.rerun()
            
            # Calculate and display metrics
            metrics = calculate_aggregated_metrics(filtered_data)
            
            # Display filtered data
            st.markdown(f"**Mostrando {len(filtered_data)} de {total_items} registros**")
            st.dataframe(
                filtered_data,
                use_container_width=True,
                hide_index=True,
                height=400
            )
            
            # Download button
            st.markdown(
                get_download_link(filtered_data, 'dados_filtrados.xlsx', f'📥 {t("download_filtered_data")}'),
                unsafe_allow_html=True
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Display optimized statistics
        st.markdown(f'<div class="section-title">{t("basic_statistics")}</div>', unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            
            # Display pre-calculated metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total de Registros", metrics['total_records'])
            
            with col2:
                st.metric("Máquinas Únicas", metrics['unique_machines'])
            
            with col3:
                avg_duration_hours = metrics['avg_duration'].total_seconds() / 3600
                st.metric("Duração Média (horas)", f"{avg_duration_hours:.2f}")
            
            # Display machine statistics
            st.markdown("### Estatísticas por Máquina")
            st.dataframe(
                metrics['machine_stats'],
                use_container_width=True
            )
            
            # Create optimized visualizations
            if len(metrics['monthly_counts']) > 1:
                fig = px.line(
                    x=metrics['monthly_counts'].index,
                    y=metrics['monthly_counts'].values,
                    title="Registros por Mês",
                    labels={'x': 'Mês', 'y': 'Quantidade de Registros'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning(t('no_data_loaded'))