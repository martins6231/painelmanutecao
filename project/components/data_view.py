import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from utils.data_processing import get_download_link
from utils.i18n import get_translation
from utils.calculations import calculate_shifts_distribution
from utils.visualizations import create_shifts_distribution_chart

def show_data_view():
    """Display the data view page."""
    t = get_translation()
    
    if st.session_state.df is not None:
        st.markdown(f'<div class="section-title">{t("data_visualization")}</div>', unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            # Filter options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Machine filter
                available_machines = [t('all')] + sorted(st.session_state.df['Máquina'].unique().tolist())
                machine_filter = st.selectbox(t('filter_by_machine'), available_machines, key="data_machine_filter")
            
            with col2:
                # Month filter
                available_months = [t('all')] + sorted(st.session_state.df['Ano-Mês'].unique().tolist())
                month_filter = st.selectbox(t('filter_by_month'), available_months, key="data_month_filter")
            
            with col3:
                # Date range filter
                use_date_range = st.checkbox("Usar intervalo de datas", key="use_date_range")
                
                if use_date_range:
                    min_date = st.session_state.df['Inicio'].min().date()
                    max_date = st.session_state.df['Inicio'].max().date()
                    
                    start_date = st.date_input(
                        "Data Inicial",
                        value=min_date,
                        min_value=min_date,
                        max_value=max_date,
                        key="data_start_date"
                    )
                    
                    end_date = st.date_input(
                        "Data Final",
                        value=max_date,
                        min_value=min_date,
                        max_value=max_date,
                        key="data_end_date"
                    )
                    
                    if start_date > end_date:
                        st.error("A data inicial não pode ser posterior à data final")
            
            # Apply filters
            filtered_data = st.session_state.df.copy()
            
            if machine_filter != t('all'):
                filtered_data = filtered_data[filtered_data['Máquina'] == machine_filter]
            
            if not use_date_range and month_filter != t('all'):
                filtered_data = filtered_data[filtered_data['Ano-Mês'] == month_filter]
            elif use_date_range and start_date <= end_date:
                start_datetime = datetime.combine(start_date, datetime.min.time())
                end_datetime = datetime.combine(end_date, datetime.max.time())
                filtered_data = filtered_data[
                    (filtered_data['Inicio'] >= start_datetime) & 
                    (filtered_data['Inicio'] <= end_datetime)
                ]
            
            # Display filtered data
            st.markdown(f"**{t('showing')} {len(filtered_data)} {t('records')}**")
            st.dataframe(
                filtered_data,
                use_container_width=True,
                hide_index=True,
                height=400
            )
            
            # Download button
            st.markdown(
                get_download_link(filtered_data, 'filtered_data.xlsx', f'📥 {t("download_filtered_data")}'),
                unsafe_allow_html=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Basic statistics
        st.markdown(f'<div class="section-title">{t("basic_statistics")}</div>', unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            # Machine summary
            machine_summary = filtered_data.groupby('Máquina').agg({
                'Duração': ['count', 'sum', 'mean']
            })
            machine_summary.columns = [t('number_of_stoppages'), t('total_duration'), t('average_duration')]
            
            # Convert to hours
            machine_summary[f"{t('total_duration')} ({t('hours')})"] = machine_summary[t('total_duration')].apply(lambda x: x.total_seconds() / 3600)
            machine_summary[f"{t('average_duration')} ({t('hours')})"] = machine_summary[t('average_duration')].apply(lambda x: x.total_seconds() / 3600)
            
            st.dataframe(
                machine_summary[[t('number_of_stoppages'), f"{t('total_duration')} ({t('hours')})", f"{t('average_duration')} ({t('hours')})"]], 
                use_container_width=True
            )
            
            # Create summary chart
            if len(machine_summary) > 1:  # Only create chart if there's more than one machine
                fig_summary = px.bar(
                    machine_summary.reset_index(),
                    x='Máquina',
                    y=f"{t('total_duration')} ({t('hours')})",
                    color='Máquina',
                    title=t('total_duration_by_machine'),
                    labels={'Máquina': t('machine'), f"{t('total_duration')} ({t('hours')})": f"{t('total_duration')} ({t('hours')})"},
                    text=f"{t('total_duration')} ({t('hours')})"
                )
                
                fig_summary.update_traces(
                    texttemplate='%{text:.1f}h',
                    textposition='outside'
                )
                
                fig_summary.update_layout(
                    xaxis_tickangle=0,
                    autosize=True,
                    margin=dict(l=50, r=50, t=80, b=50),
                    plot_bgcolor='rgba(0,0,0,0)',
                    showlegend=False,
                    title={
                        'y':0.95,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'
                    }
                )
                
                st.plotly_chart(fig_summary, use_container_width=True)
            
            # Download summary button
            st.markdown(
                get_download_link(machine_summary.reset_index(), 'machine_summary.xlsx', f'📥 {t("download_machine_summary")}'),
                unsafe_allow_html=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Additional analyses
        st.markdown(f'<div class="section-title">{t("additional_analyses")}</div>', unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            
            tab1, tab2, tab3 = st.tabs([
                f"📅 {t('distribution_by_weekday')}", 
                f"🕒 {t('distribution_by_hour')}", 
                "🔄 Distribuição por Turno"
            ])
            
            with tab1:
                # Add weekday column
                filtered_data['Dia da Semana'] = filtered_data['Inicio'].dt.day_name()
                
                # Weekday order starting from Sunday
                weekday_order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
                
                # Mapping to localized names based on language
                if st.session_state.language == 'pt':
                    weekday_names = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']
                else:
                    weekday_names = weekday_order
                
                weekday_mapping = dict(zip(weekday_order, weekday_names))
                filtered_data['Dia da Semana Localizado'] = filtered_data['Dia da Semana'].map(weekday_mapping)
                
                # Group by weekday
                stoppages_by_day = filtered_data.groupby('Dia da Semana Localizado').agg({
                    'Duração': ['count', 'sum']
                })
                stoppages_by_day.columns = [t('number_of_stoppages'), t('total_duration')]
                
                # Convert to hours
                stoppages_by_day[f"{t('duration')} ({t('hours')})"] = stoppages_by_day[t('total_duration')].apply(lambda x: x.total_seconds() / 3600)
                
                # Reorder index according to weekdays
                if not stoppages_by_day.empty:
                    stoppages_by_day = stoppages_by_day.reindex(weekday_names)
                    
                    # Create chart
                    fig_days = px.bar(
                        stoppages_by_day.reset_index(),
                        x='Dia da Semana Localizado',
                        y=t('number_of_stoppages'),
                        title=t('distribution_by_weekday'),
                        labels={t('number_of_stoppages'): t('number_of_stoppages'), 'Dia da Semana Localizado': t('weekday')},
                        text=t('number_of_stoppages'),
                        color='Dia da Semana Localizado',
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    
                    fig_days.update_traces(
                        texttemplate='%{text}',
                        textposition='outside'
                    )
                    
                    fig_days.update_layout(
                        xaxis_tickangle=0,
                        autosize=True,
                        margin=dict(l=50, r=50, t=80, b=50),
                        plot_bgcolor='rgba(0,0,0,0)',
                        showlegend=False,
                        title={
                            'y':0.95,
                            'x':0.5,
                            'xanchor': 'center',
                            'yanchor': 'top'
                        }
                    )
                    
                    st.plotly_chart(fig_days, use_container_width=True)
                    
                    # Display table
                    st.dataframe(
                        stoppages_by_day[[t('number_of_stoppages'), f"{t('duration')} ({t('hours')})"]], 
                        use_container_width=True
                    )
                else:
                    st.info(t('insufficient_data'))
            
            with tab2:
                # Add hour of day column
                filtered_data['Hora do Dia'] = filtered_data['Inicio'].dt.hour
                
                # Group by hour
                stoppages_by_hour = filtered_data.groupby('Hora do Dia').agg({
                    'Duração': ['count', 'sum']
                })
                stoppages_by_hour.columns = [t('number_of_stoppages'), t('total_duration')]
                
                # Convert to hours
                stoppages_by_hour[f"{t('duration')} ({t('hours')})"] = stoppages_by_hour[t('total_duration')].apply(lambda x: x.total_seconds() / 3600)
                
                # Create chart
                if not stoppages_by_hour.empty:
                    fig_hours = px.line(
                        stoppages_by_hour.reset_index(),
                        x='Hora do Dia',
                        y=t('number_of_stoppages'),
                        title=t('distribution_by_hour'),
                        labels={t('number_of_stoppages'): t('number_of_stoppages'), 'Hora do Dia': t('hour_of_day')},
                        markers=True
                    )
                    
                    # Add area under the line
                    fig_hours.add_trace(
                        px.area(
                            stoppages_by_hour.reset_index(),
                            x='Hora do Dia',
                            y=t('number_of_stoppages')
                        ).data[0]
                    )
                    
                    fig_hours.update_layout(
                        xaxis=dict(
                            tickmode='array',
                            tickvals=list(range(0, 24)),
                            ticktext=[f"{h}:00" for h in range(0, 24)]
                        ),
                        autosize=True,
                        margin=dict(l=50, r=50, t=80, b=50),
                        plot_bgcolor='rgba(0,0,0,0)',
                        showlegend=False,
                        title={
                            'y':0.95,
                            'x':0.5,
                            'xanchor': 'center',
                            'yanchor': 'top'
                        }
                    )
                    
                    st.plotly_chart(fig_hours, use_container_width=True)
                    
                    # Display table
                    st.dataframe(
                        stoppages_by_hour[[t('number_of_stoppages'), f"{t('duration')} ({t('hours')})"]], 
                        use_container_width=True
                    )
                else:
                    st.info(t('insufficient_data'))
            
            with tab3:
                # Calculate shift distribution
                shifts_distribution = calculate_shifts_distribution(filtered_data)
                
                if not shifts_distribution.empty:
                    # Create shift distribution chart
                    fig_shifts = create_shifts_distribution_chart(shifts_distribution)
                    if fig_shifts:
                        st.plotly_chart(fig_shifts, use_container_width=True)
                        
                        # Display table
                        shift_data = pd.DataFrame({
                            'Turno': shifts_distribution.index,
                            'Número de Paradas': shifts_distribution.values
                        })
                        st.dataframe(shift_data, use_container_width=True)
                else:
                    st.info(t('insufficient_data'))
            
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning(t('no_data_loaded'))