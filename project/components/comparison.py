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
        st.warning(t('no_data_loaded'))
        return
    
    # Title
    st.markdown(f'<div class="section-title">{t("period_comparison")}</div>', unsafe_allow_html=True)
    
    # Comparison setup
    with st.container():
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        st.markdown(f"### 📊 {t('period_select')}")
        
        # Machine filter
        available_machines = [t('all')] + sorted(st.session_state.df['Máquina'].unique().tolist())
        selected_machine = st.selectbox(t('select_machine'), available_machines, key="comparison_machine")
        
        # Period selection
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"#### {t('period_1')}")
            
            # Date range for period 1
            min_date = st.session_state.df['Inicio'].min().date()
            max_date = st.session_state.df['Inicio'].max().date()
            
            # Default to last month for period 1
            default_end_date1 = max_date - timedelta(days=30)
            default_start_date1 = default_end_date1 - timedelta(days=29)
            
            start_date1 = st.date_input(
                t('comparison_period_start'), 
                value=default_start_date1,
                min_value=min_date,
                max_value=max_date,
                key="start_date1"
            )
            
            end_date1 = st.date_input(
                t('comparison_period_end'), 
                value=default_end_date1,
                min_value=min_date,
                max_value=max_date,
                key="end_date1"
            )
            
            # Validate date range
            if start_date1 > end_date1:
                st.error(t('period_start_after_end'))
        
        with col2:
            st.markdown(f"#### {t('period_2')}")
            
            # Date range for period 2
            # Default to current month for period 2
            default_start_date2 = max_date - timedelta(days=29)
            
            start_date2 = st.date_input(
                t('comparison_period_start'), 
                value=default_start_date2,
                min_value=min_date,
                max_value=max_date,
                key="start_date2"
            )
            
            end_date2 = st.date_input(
                t('comparison_period_end'), 
                value=max_date,
                min_value=min_date,
                max_value=max_date,
                key="end_date2"
            )
            
            # Validate date range
            if start_date2 > end_date2:
                st.error(t('period_start_after_end'))
        
        # Compare button
        compare_col1, _ = st.columns([1, 3])
        with compare_col1:
            if st.button(t('compare_button'), key="btn_compare", use_container_width=True):
                if start_date1 <= end_date1 and start_date2 <= end_date2:
                    with st.spinner(t('analyzing_data')):
                        # Convert dates to datetime
                        start_datetime1 = datetime.combine(start_date1, datetime.min.time())
                        end_datetime1 = datetime.combine(end_date1, datetime.max.time())
                        
                        start_datetime2 = datetime.combine(start_date2, datetime.min.time())
                        end_datetime2 = datetime.combine(end_date2, datetime.max.time())
                        
                        # Convert 'All' to 'Todas' for processing if language is English
                        machine_for_filter = "Todas" if selected_machine == t('all') else selected_machine
                        
                        # Filter data for both periods
                        data1 = filter_data(
                            st.session_state.df, 
                            machine_for_filter, 
                            start_date=start_datetime1, 
                            end_date=end_datetime1
                        )
                        
                        data2 = filter_data(
                            st.session_state.df, 
                            machine_for_filter, 
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
                        st.error(f"{t('period_1')}: {t('period_start_after_end')}")
                    if start_date2 > end_date2:
                        st.error(f"{t('period_2')}: {t('period_start_after_end')}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display comparison results if available
    if 'comparison_data' in st.session_state and st.session_state.comparison_data:
        display_comparison_results()

def display_comparison_results():
    """Display the period comparison results."""
    t = get_translation()
    comparison_data = st.session_state.comparison_data
    
    # Title
    st.markdown(f'<div class="section-title">{t("comparison_results")}</div>', unsafe_allow_html=True)
    
    # Period information
    with st.container():
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        st.markdown(f"### 📅 {t('period_comparison')}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            start_date1, end_date1 = comparison_data['period1']
            st.markdown(f"**{t('period_1')}:** {start_date1.strftime('%d/%m/%Y')} - {end_date1.strftime('%d/%m/%Y')}")
            st.markdown(f"**{t('duration')}:** {(end_date1 - start_date1).days + 1} {t('days')}")
            st.markdown(f"**{t('machine')}:** {comparison_data['machine']}")
            st.markdown(f"**{t('total_stoppages')}:** {len(comparison_data['data1'])}")
        
        with col2:
            start_date2, end_date2 = comparison_data['period2']
            st.markdown(f"**{t('period_2')}:** {start_date2.strftime('%d/%m/%Y')} - {end_date2.strftime('%d/%m/%Y')}")
            st.markdown(f"**{t('duration')}:** {(end_date2 - start_date2).days + 1} {t('days')}")
            st.markdown(f"**{t('total_stoppages')}:** {len(comparison_data['data2'])}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Key metrics comparison
    if comparison_data['results']:
        metrics = comparison_data['results']['metrics']
        
        st.markdown(f'<div class="section-title">{t("metrics_comparison")}</div>', unsafe_allow_html=True)
        
        # Availability and efficiency
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            availability1, availability2, diff_availability, pct_availability = metrics['availability']
            fig_availability = create_comparison_gauge_chart(
                availability1, 
                availability2, 
                t('availability'),
                max_value=100,
                language=st.session_state.language
            )
            st.plotly_chart(fig_availability, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            efficiency1, efficiency2, diff_efficiency, pct_efficiency = metrics['efficiency']
            fig_efficiency = create_comparison_gauge_chart(
                efficiency1, 
                efficiency2, 
                t('efficiency'),
                max_value=100,
                language=st.session_state.language
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
                t('mtbf'),
                language=st.session_state.language
            )
            st.plotly_chart(fig_mtbf, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            mttr1, mttr2, diff_mttr, pct_mttr = metrics['mttr']
            fig_mttr = create_comparative_bar_chart(
                mttr1, 
                mttr2, 
                t('mttr'),
                language=st.session_state.language
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
                t('total_stoppages'),
                language=st.session_state.language
            )
            st.plotly_chart(fig_stoppages, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            downtime1, downtime2, diff_downtime, pct_downtime = metrics['total_downtime']
            fig_downtime = create_comparative_bar_chart(
                downtime1, 
                downtime2, 
                t('total_stoppage_time'),
                language=st.session_state.language
            )
            st.plotly_chart(fig_downtime, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Summary table
        st.markdown(f'<div class="section-title">{t("key_indicators")}</div>', unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            
            # Create summary table
            summary_data = {
                t('indicator'): [
                    t('availability'),
                    t('efficiency'),
                    t('mtbf'),
                    t('mttr'),
                    t('total_stoppages'),
                    t('total_stoppage_time')
                ],
                f"{t('period_1')}": [
                    f"{availability1:.1f}%",
                    f"{efficiency1:.1f}%",
                    f"{mtbf1:.1f}h",
                    f"{mttr1:.1f}h",
                    f"{int(stoppages1)}",
                    f"{downtime1:.1f}h"
                ],
                f"{t('period_2')}": [
                    f"{availability2:.1f}%",
                    f"{efficiency2:.1f}%",
                    f"{mtbf2:.1f}h",
                    f"{mttr2:.1f}h",
                    f"{int(stoppages2)}",
                    f"{downtime2:.1f}h"
                ],
                t('variation'): [
                    f"{diff_availability:+.1f}%",
                    f"{diff_efficiency:+.1f}%",
                    f"{diff_mtbf:+.1f}h",
                    f"{diff_mttr:+.1f}h",
                    f"{int(diff_stoppages):+d}",
                    f"{diff_downtime:+.1f}h"
                ],
                f"{t('variation')} (%)" : [
                    f"{pct_availability:+.1f}%" if pct_availability != float('inf') else "N/A",
                    f"{pct_efficiency:+.1f}%" if pct_efficiency != float('inf') else "N/A",
                    f"{pct_mtbf:+.1f}%" if pct_mtbf != float('inf') else "N/A",
                    f"{pct_mttr:+.1f}%" if pct_mttr != float('inf') else "N/A",
                    f"{pct_stoppages:+.1f}%" if pct_stoppages != float('inf') else "N/A",
                    f"{pct_downtime:+.1f}%" if pct_downtime != float('inf') else "N/A"
                ],
                t('status'): [
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
                get_download_link(summary_df, 'period_comparison.xlsx', f'📥 {t("download_comparison")}'),
                unsafe_allow_html=True
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Conclusions
        st.markdown(f'<div class="section-title">{t("comparison_conclusions")}</div>', unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            st.markdown(f"### 🔍 {t('analysis_summary')}")
            
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
                performance_status = "🟢 " + t('overall_improvement')
                performance_pct = improved_count / total_metrics * 100
                st.markdown(f"**{performance_status}** ({performance_pct:.0f}% {t('metrics_improved')})")
                
                # Generate detailed insights
                st.markdown(f"#### {t('key_improvements')}:")
                if diff_availability > 0:
                    st.markdown(f"- {t('availability')} {t('increased_by')} {diff_availability:.1f}% ({pct_availability:+.1f}%)")
                if diff_efficiency > 0:
                    st.markdown(f"- {t('efficiency')} {t('increased_by')} {diff_efficiency:.1f}% ({pct_efficiency:+.1f}%)")
                if diff_mtbf > 0:
                    st.markdown(f"- {t('mtbf')} {t('increased_by')} {diff_mtbf:.1f}h ({pct_mtbf:+.1f}%)")
                if diff_mttr < 0:
                    st.markdown(f"- {t('mttr')} {t('decreased_by')} {abs(diff_mttr):.1f}h ({pct_mttr:+.1f}%)")
                if diff_stoppages < 0:
                    st.markdown(f"- {t('total_stoppages')} {t('decreased_by')} {abs(int(diff_stoppages))} ({pct_stoppages:+.1f}%)")
                if diff_downtime < 0:
                    st.markdown(f"- {t('total_stoppage_time')} {t('decreased_by')} {abs(diff_downtime):.1f}h ({pct_downtime:+.1f}%)")
                
                if worsened_count > 0:
                    st.markdown(f"#### {t('areas_for_improvement')}:")
                    if diff_availability < 0:
                        st.markdown(f"- {t('availability')} {t('decreased_by')} {abs(diff_availability):.1f}% ({pct_availability:+.1f}%)")
                    if diff_efficiency < 0:
                        st.markdown(f"- {t('efficiency')} {t('decreased_by')} {abs(diff_efficiency):.1f}% ({pct_efficiency:+.1f}%)")
                    if diff_mtbf < 0:
                        st.markdown(f"- {t('mtbf')} {t('decreased_by')} {abs(diff_mtbf):.1f}h ({pct_mtbf:+.1f}%)")
                    if diff_mttr > 0:
                        st.markdown(f"- {t('mttr')} {t('increased_by')} {diff_mttr:.1f}h ({pct_mttr:+.1f}%)")
                    if diff_stoppages > 0:
                        st.markdown(f"- {t('total_stoppages')} {t('increased_by')} {int(diff_stoppages)} ({pct_stoppages:+.1f}%)")
                    if diff_downtime > 0:
                        st.markdown(f"- {t('total_stoppage_time')} {t('increased_by')} {diff_downtime:.1f}h ({pct_downtime:+.1f}%)")
            
            elif worsened_count > improved_count:
                performance_status = "🔴 " + t('overall_deterioration')
                performance_pct = worsened_count / total_metrics * 100
                st.markdown(f"**{performance_status}** ({performance_pct:.0f}% {t('metrics_worsened')})")
                
                # Generate detailed insights
                st.markdown(f"#### {t('areas_for_improvement')}:")
                if diff_availability < 0:
                    st.markdown(f"- {t('availability')} {t('decreased_by')} {abs(diff_availability):.1f}% ({pct_availability:+.1f}%)")
                if diff_efficiency < 0:
                    st.markdown(f"- {t('efficiency')} {t('decreased_by')} {abs(diff_efficiency):.1f}% ({pct_efficiency:+.1f}%)")
                if diff_mtbf < 0:
                    st.markdown(f"- {t('mtbf')} {t('decreased_by')} {abs(diff_mtbf):.1f}h ({pct_mtbf:+.1f}%)")
                if diff_mttr > 0:
                    st.markdown(f"- {t('mttr')} {t('increased_by')} {diff_mttr:.1f}h ({pct_mttr:+.1f}%)")
                if diff_stoppages > 0:
                    st.markdown(f"- {t('total_stoppages')} {t('increased_by')} {int(diff_stoppages)} ({pct_stoppages:+.1f}%)")
                if diff_downtime > 0:
                    st.markdown(f"- {t('total_stoppage_time')} {t('increased_by')} {diff_downtime:.1f}h ({pct_downtime:+.1f}%)")
                
                if improved_count > 0:
                    st.markdown(f"#### {t('key_improvements')}:")
                    if diff_availability > 0:
                        st.markdown(f"- {t('availability')} {t('increased_by')} {diff_availability:.1f}% ({pct_availability:+.1f}%)")
                    if diff_efficiency > 0:
                        st.markdown(f"- {t('efficiency')} {t('increased_by')} {diff_efficiency:.1f}% ({pct_efficiency:+.1f}%)")
                    if diff_mtbf > 0:
                        st.markdown(f"- {t('mtbf')} {t('increased_by')} {diff_mtbf:.1f}h ({pct_mtbf:+.1f}%)")
                    if diff_mttr < 0:
                        st.markdown(f"- {t('mttr')} {t('decreased_by')} {abs(diff_mttr):.1f}h ({pct_mttr:+.1f}%)")
                    if diff_stoppages < 0:
                        st.markdown(f"- {t('total_stoppages')} {t('decreased_by')} {abs(int(diff_stoppages))} ({pct_stoppages:+.1f}%)")
                    if diff_downtime < 0:
                        st.markdown(f"- {t('total_stoppage_time')} {t('decreased_by')} {abs(diff_downtime):.1f}h ({pct_downtime:+.1f}%)")
            
            else:
                performance_status = "⚪ " + t('performance_unchanged')
                st.markdown(f"**{performance_status}**")
                st.markdown(f"{t('equal_improvements_deteriorations')}")
            
            # Calculate performance score
            performance_score = (improved_count - worsened_count) / total_metrics * 100
            
            # Recommendations based on performance
            st.markdown(f"#### {t('recommendations')}:")
            if performance_score > 30:
                st.markdown(f"- {t('excellent_performance_continue')}")
                st.markdown(f"- {t('document_improvements')}")
                st.markdown(f"- {t('set_higher_goals')}")
            elif performance_score > 0:
                st.markdown(f"- {t('good_progress_focus_weak_areas')}")
                st.markdown(f"- {t('analyze_improvement_factors')}")
                st.markdown(f"- {t('implement_targeted_actions')}")
            elif performance_score == 0:
                st.markdown(f"- {t('identify_priority_metrics')}")
                st.markdown(f"- {t('establish_improvement_plan')}")
                st.markdown(f"- {t('conduct_root_cause_analysis')}")
            else:
                st.markdown(f"- {t('urgent_action_needed')}")
                st.markdown(f"- {t('conduct_detailed_investigation')}")
                st.markdown(f"- {t('develop_comprehensive_action_plan')}")
                st.markdown(f"- {t('establish_monitoring_mechanisms')}")
            
            st.markdown('</div>', unsafe_allow_html=True)
