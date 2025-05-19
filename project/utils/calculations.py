import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data
def calculate_availability(df, scheduled_time):
    """Calculate the availability rate excluding PCP stops."""
    if df.empty:
        return 0
    
    # Filter stops by PCP area
    pcp_stops = df[df['Área Responsável'].str.contains('PCP', case=False, na=False)]
    pcp_downtime = pcp_stops['Duração'].sum()
    
    # Calculate availability
    availability = (scheduled_time - pcp_downtime) / scheduled_time * 100
    return max(0, min(100, availability))

@st.cache_data
def calculate_operational_efficiency(df, scheduled_time):
    """Calculate operational efficiency excluding Operation and Organizational stops."""
    if df.empty:
        return 0
    
    # Filter stops by Operation and Organizational areas
    operation_stops = df[
        df['Área Responsável'].str.contains('Operação|Organizacional', case=False, na=False)
    ]
    operation_downtime = operation_stops['Duração'].sum()
    
    # Calculate efficiency
    efficiency = (scheduled_time - operation_downtime) / scheduled_time * 100
    return max(0, min(100, efficiency))

@st.cache_data
def calculate_average_downtime(df):
    """Calculate average downtime (MTTR)."""
    return df['Duração'].mean() if not df.empty else pd.Timedelta(0)

@st.cache_data
def calculate_stoppage_by_area(df):
    """Calculate percentage of stoppages by responsible area."""
    if 'Área Responsável' in df.columns and not df.empty:
        area_counts = df['Área Responsável'].value_counts(normalize=True) * 100
        return area_counts
    else:
        return pd.Series()

@st.cache_data
def pareto_stoppage_causes(df):
    """Identify the main causes of stoppages (Pareto) by total duration."""
    if 'Parada' in df.columns and not df.empty:
        pareto = df.groupby('Parada')['Duração'].sum().sort_values(ascending=False).head(10)
        return pareto
    else:
        return pd.Series()

@st.cache_data
def most_frequent_stoppages(df):
    """Identify the most frequent stoppages by count."""
    if 'Parada' in df.columns and not df.empty:
        frequent = df['Parada'].value_counts().head(10)
        return frequent
    else:
        return pd.Series()

@st.cache_data
def calculate_stoppage_occurrence_rate(df):
    """Calculate the rate of stoppage occurrences (total number of stoppages per month)."""
    if not df.empty:
        monthly_occurrences = df.groupby('Ano-Mês').size()
        return monthly_occurrences
    else:
        return pd.Series()

@st.cache_data
def calculate_total_duration_by_month(df):
    """Calculate the total duration of stoppages by month."""
    if not df.empty:
        monthly_duration = df.groupby('Ano-Mês')['Duração'].sum()
        return monthly_duration
    else:
        return pd.Series()

@st.cache_data
def calculate_total_stoppage_time_by_area(df):
    """Calculate total stoppage time by area."""
    if 'Área Responsável' in df.columns and not df.empty:
        time_by_area = df.groupby('Área Responsável')['Duração'].sum()
        return time_by_area
    else:
        return pd.Series()

@st.cache_data
def identify_critical_stoppages(df, hour_limit=1):
    """Identify critical stoppages (with duration greater than the specified limit)."""
    limit = pd.Timedelta(hours=hour_limit)
    if not df.empty:
        critical_stoppages = df[df['Duração'] > limit]
        critical_percentage = len(critical_stoppages) / len(df) * 100 if len(df) > 0 else 0
        return critical_stoppages, critical_percentage
    else:
        return pd.DataFrame(), 0

@st.cache_data
def calculate_mtbf_mttr(df, scheduled_time):
    """Calculate MTBF (Mean Time Between Failures) and MTTR (Mean Time To Repair)."""
    if df.empty:
        return 0, 0
    
    total_stoppages = len(df)
    total_downtime = df['Duração'].sum()
    
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
        # If date range is specified, use the number of days in the range
        days_in_period = (end_date - start_date).days + 1
    elif month_selected and month_selected not in ["Todos", "All"]:
        # If month is selected, get the number of days in that month
        year, month = map(int, month_selected.split('-'))
        days_in_period = pd.Period(f"{year}-{month}").days_in_month
    else:
        # If all months are selected, use the total interval of the data
        if df.empty:
            return pd.Timedelta(hours=24 * 30)  # Default to 30 days if no data
        
        days_in_period = (df['Inicio'].max() - df['Inicio'].min()).days + 1
        days_in_period = max(30, days_in_period)  # Use at least 30 days to avoid division by zero
    
    # Scheduled time in hours (24 hours per day)
    scheduled_time_hours = days_in_period * 24
    return pd.Timedelta(hours=scheduled_time_hours), scheduled_time_hours

@st.cache_data
def generate_recommendations(df, availability, efficiency):
    """Generate automatic recommendations based on analyzed data."""
    recommendations = []
    
    # Check availability
    if availability < 70:
        recommendations.append("⚠️ A disponibilidade está abaixo do nível recomendado (70%). Priorize a redução das paradas relacionadas ao PCP.")
    elif availability < 85:
        recommendations.append("⚠️ A disponibilidade está em um nível moderado. Considere otimizar os processos do PCP.")
    else:
        recommendations.append("✅ A disponibilidade está em um bom nível. Continue monitorando para manter este desempenho.")
    
    # Check efficiency
    if efficiency < 65:
        recommendations.append("⚠️ A eficiência operacional está baixa. Analise as causas mais frequentes de paradas operacionais e organizacionais.")
    elif efficiency < 80:
        recommendations.append("⚠️ A eficiência operacional está em um nível moderado. Busque otimizar processos operacionais.")
    else:
        recommendations.append("✅ A eficiência operacional está em um bom nível. Continue com as práticas atuais.")
    
    # Critical stoppages analysis
    critical_stoppages, critical_percentage = identify_critical_stoppages(df)
    if critical_percentage > 20:
        recommendations.append(f"⚠️ Alta incidência de paradas críticas ({critical_percentage:.1f}%). Revise os procedimentos operacionais.")
    elif critical_percentage > 10:
        recommendations.append(f"⚠️ Incidência moderada de paradas críticas ({critical_percentage:.1f}%). Implemente um plano de ação.")
    else:
        recommendations.append(f"✅ Baixa incidência de paradas críticas ({critical_percentage:.1f}%). Continue monitorando.")
    
    # Responsible areas analysis
    if 'Área Responsável' in df.columns and not df.empty:
        areas = calculate_stoppage_by_area(df)
        if not areas.empty:
            most_problematic_area = areas.idxmax()
            area_percentage = areas.max()
            if area_percentage > 40:
                recommendations.append(f"⚠️ A área de {most_problematic_area} é responsável por {area_percentage:.1f}% das paradas. Priorize ações nesta área.")
    
    # Trend analysis
    occurrences = calculate_stoppage_occurrence_rate(df)
    if len(occurrences) >= 3:
        trend = occurrences.iloc[-1] - occurrences.iloc[0]
        if trend > 0:
            recommendations.append("⚠️ Tendência crescente no número de paradas. Revise os procedimentos operacionais.")
        elif trend < 0:
            recommendations.append("✅ Tendência decrescente no número de paradas. Continue com as melhorias implementadas.")
    
    return recommendations

@st.cache_data
def compare_periods(df1, df2):
    """Compare two periods and return the differences in key metrics."""
    if df1.empty or df2.empty:
        return None
    
    # Calculate key metrics for both periods
    scheduled_time1, hours1 = calculate_scheduled_time(df1)
    scheduled_time2, hours2 = calculate_scheduled_time(df2)
    
    availability1 = calculate_availability(df1, scheduled_time1)
    availability2 = calculate_availability(df2, scheduled_time2)
    
    efficiency1 = calculate_operational_efficiency(df1, scheduled_time1)
    efficiency2 = calculate_operational_efficiency(df2, scheduled_time2)
    
    mtbf1, mttr1 = calculate_mtbf_mttr(df1, scheduled_time1)
    mtbf2, mttr2 = calculate_mtbf_mttr(df2, scheduled_time2)
    
    total_stoppages1 = len(df1)
    total_stoppages2 = len(df2)
    
    total_downtime1 = df1['Duração'].sum().total_seconds() / 3600
    total_downtime2 = df2['Duração'].sum().total_seconds() / 3600
    
    # Calculate differences and percent changes
    diff_availability = availability2 - availability1
    pct_availability = (diff_availability / availability1 * 100) if availability1 > 0 else float('inf')
    
    diff_efficiency = efficiency2 - efficiency1
    pct_efficiency = (diff_efficiency / efficiency1 * 100) if efficiency1 > 0 else float('inf')
    
    diff_mtbf = mtbf2 - mtbf1
    pct_mtbf = (diff_mtbf / mtbf1 * 100) if mtbf1 > 0 else float('inf')
    
    diff_mttr = mttr2 - mttr1
    pct_mttr = (diff_mttr / mttr1 * 100) if mttr1 > 0 else float('inf')
    
    diff_stoppages = total_stoppages2 - total_stoppages1
    pct_stoppages = (diff_stoppages / total_stoppages1 * 100) if total_stoppages1 > 0 else float('inf')
    
    diff_downtime = total_downtime2 - total_downtime1
    pct_downtime = (diff_downtime / total_downtime1 * 100) if total_downtime1 > 0 else float('inf')
    
    # Return the comparison results
    return {
        'metrics': {
            'availability': (availability1, availability2, diff_availability, pct_availability),
            'efficiency': (efficiency1, efficiency2, diff_efficiency, pct_efficiency),
            'mtbf': (mtbf1, mtbf2, diff_mtbf, pct_mtbf),
            'mttr': (mttr1, mttr2, diff_mttr, pct_mttr),
            'total_stoppages': (total_stoppages1, total_stoppages2, diff_stoppages, pct_stoppages),
            'total_downtime': (total_downtime1, total_downtime2, diff_downtime, pct_downtime)
        },
        'period_info': {
            'period1_days': hours1 / 24,
            'period2_days': hours2 / 24
        }
    }