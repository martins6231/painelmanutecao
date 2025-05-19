import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data
def calculate_availability(df, scheduled_time):
    """Calculate the availability rate considering only PCP downtimes."""
    if df.empty:
        return 0
    
    # Filter only PCP-related downtimes
    pcp_downtimes = df[df['Área Responsável'].str.upper() == 'PCP']
    total_pcp_downtime = pcp_downtimes['Duração'].sum()
    
    # Convert to total seconds for calculation
    scheduled_seconds = scheduled_time.total_seconds()
    downtime_seconds = total_pcp_downtime.total_seconds()
    
    # Calculate availability
    if scheduled_seconds > 0:
        availability = ((scheduled_seconds - downtime_seconds) / scheduled_seconds) * 100
        return max(0, min(100, availability))
    return 0

@st.cache_data
def calculate_mtbf_mttr(df, scheduled_time):
    """Calculate MTBF (Mean Time Between Failures) and MTTR (Mean Time To Repair)."""
    if df.empty:
        return 0, 0
    
    # Filter only PCP-related downtimes for consistency with availability calculation
    pcp_downtimes = df[df['Área Responsável'].str.upper() == 'PCP']
    total_stoppages = len(pcp_downtimes)
    total_downtime = pcp_downtimes['Duração'].sum()
    
    # Calculate MTBF in hours
    if total_stoppages > 1:
        mtbf = (scheduled_time - total_downtime).total_seconds() / 3600 / total_stoppages
    else:
        mtbf = 0
    
    # Calculate MTTR in hours
    if total_stoppages > 0:
        mttr = total_downtime.total_seconds() / 3600 / total_stoppages
    else:
        mttr = 0
    
    return mtbf, mttr

@st.cache_data
def calculate_scheduled_time(df, month_selected=None, start_date=None, end_date=None):
    """Calculate scheduled time based on the selected period."""
    if start_date and end_date:
        days_in_period = (end_date - start_date).days + 1
    elif month_selected and month_selected not in ["Todos", "All"]:
        year, month = map(int, month_selected.split('-'))
        days_in_period = pd.Period(f"{year}-{month}").days_in_month
    else:
        if df.empty:
            return pd.Timedelta(hours=24 * 30)
        days_in_period = (df['Inicio'].max() - df['Inicio'].min()).days + 1
        days_in_period = max(30, days_in_period)
    
    scheduled_time_hours = days_in_period * 24
    return pd.Timedelta(hours=scheduled_time_hours), scheduled_time_hours

@st.cache_data
def calculate_stoppage_by_area(df):
    """Calculate percentage of stoppages by responsible area."""
    if 'Área Responsável' in df.columns and not df.empty:
        area_counts = df['Área Responsável'].value_counts(normalize=True) * 100
        return area_counts
    return pd.Series()

@st.cache_data
def pareto_stoppage_causes(df):
    """Identify the main causes of stoppages (Pareto) by total duration."""
    if 'Parada' in df.columns and not df.empty:
        pareto = df.groupby('Parada')['Duração'].sum().sort_values(ascending=False).head(10)
        return pareto
    return pd.Series()

@st.cache_data
def identify_critical_stoppages(df, hour_limit=1):
    """Identify critical stoppages (with duration greater than the specified limit)."""
    if df.empty:
        return pd.DataFrame(), 0
    
    limit = pd.Timedelta(hours=hour_limit)
    critical_stoppages = df[df['Duração'] > limit]
    critical_percentage = len(critical_stoppages) / len(df) * 100 if len(df) > 0 else 0
    return critical_stoppages, critical_percentage

@st.cache_data
def generate_recommendations(df, availability):
    """Generate automatic recommendations based on analyzed data."""
    recommendations = []
    
    # Availability recommendations
    if availability < 70:
        recommendations.append("⚠️ A disponibilidade está abaixo do nível recomendado (70%). Analise as causas de paradas do PCP.")
    elif availability < 85:
        recommendations.append("⚠️ A disponibilidade está em um nível moderado. Considere otimizar o planejamento de produção.")
    else:
        recommendations.append("✅ A disponibilidade está em um bom nível. Continue com as boas práticas de planejamento.")
    
    # PCP-specific analysis
    pcp_downtimes = df[df['Área Responsável'].str.upper() == 'PCP']
    if not pcp_downtimes.empty:
        avg_duration = pcp_downtimes['Duração'].mean()
        if avg_duration > pd.Timedelta(hours=2):
            recommendations.append("⚠️ Tempo médio de paradas do PCP está elevado. Revise os processos de planejamento.")
        
        most_common_cause = pcp_downtimes['Parada'].mode().iloc[0] if not pcp_downtimes['Parada'].empty else None
        if most_common_cause:
            recommendations.append(f"ℹ️ Principal causa de parada do PCP: {most_common_cause}")
    
    return recommendations

@st.cache_data
def compare_periods(df1, df2):
    """Compare two periods and return the differences in key metrics."""
    if df1.empty or df2.empty:
        return None
    
    # Calculate metrics for both periods
    scheduled_time1, hours1 = calculate_scheduled_time(df1)
    scheduled_time2, hours2 = calculate_scheduled_time(df2)
    
    availability1 = calculate_availability(df1, scheduled_time1)
    availability2 = calculate_availability(df2, scheduled_time2)
    
    mtbf1, mttr1 = calculate_mtbf_mttr(df1, scheduled_time1)
    mtbf2, mttr2 = calculate_mtbf_mttr(df2, scheduled_time2)
    
    # PCP-specific metrics
    pcp_stoppages1 = len(df1[df1['Área Responsável'].str.upper() == 'PCP'])
    pcp_stoppages2 = len(df2[df2['Área Responsável'].str.upper() == 'PCP'])
    
    pcp_downtime1 = df1[df1['Área Responsável'].str.upper() == 'PCP']['Duração'].sum().total_seconds() / 3600
    pcp_downtime2 = df2[df2['Área Responsável'].str.upper() == 'PCP']['Duração'].sum().total_seconds() / 3600
    
    # Calculate differences
    diff_availability = availability2 - availability1
    pct_availability = (diff_availability / availability1 * 100) if availability1 > 0 else float('inf')
    
    diff_mtbf = mtbf2 - mtbf1
    pct_mtbf = (diff_mtbf / mtbf1 * 100) if mtbf1 > 0 else float('inf')
    
    diff_mttr = mttr2 - mttr1
    pct_mttr = (diff_mttr / mttr1 * 100) if mttr1 > 0 else float('inf')
    
    diff_stoppages = pcp_stoppages2 - pcp_stoppages1
    pct_stoppages = (diff_stoppages / pcp_stoppages1 * 100) if pcp_stoppages1 > 0 else float('inf')
    
    diff_downtime = pcp_downtime2 - pcp_downtime1
    pct_downtime = (diff_downtime / pcp_downtime1 * 100) if pcp_downtime1 > 0 else float('inf')
    
    return {
        'metrics': {
            'availability': (availability1, availability2, diff_availability, pct_availability),
            'mtbf': (mtbf1, mtbf2, diff_mtbf, pct_mtbf),
            'mttr': (mttr1, mttr2, diff_mttr, pct_mttr),
            'pcp_stoppages': (pcp_stoppages1, pcp_stoppages2, diff_stoppages, pct_stoppages),
            'pcp_downtime': (pcp_downtime1, pcp_downtime2, diff_downtime, pct_downtime)
        },
        'period_info': {
            'period1_days': hours1 / 24,
            'period2_days': hours2 / 24
        }
    }