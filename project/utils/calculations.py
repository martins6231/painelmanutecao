import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data
def calculate_availability(df, scheduled_time):
    """
    Calcula a taxa de disponibilidade descontando paradas do PCP.
    
    Args:
        df: DataFrame com os dados de parada
        scheduled_time: Tempo total programado (timedelta)
    
    Returns:
        float: Taxa de disponibilidade em percentual
    """
    if df.empty:
        return 0
    
    # Agrupa por máquina se houver múltiplas máquinas
    machines = df['Máquina'].unique()
    if len(machines) > 1:
        # Calcula disponibilidade para cada máquina
        total_scheduled_time = scheduled_time * len(machines)
        
        # Separa paradas do PCP
        pcp_stops = df[df['Área Responsável'] == 'PCP']['Duração'].sum()
        
        # Calcula tempo total de paradas excluindo PCP
        non_pcp_stops = df[df['Área Responsável'] != 'PCP']['Duração'].sum()
        
        # Desconta tempo do PCP do tempo programado total
        adjusted_scheduled_time = total_scheduled_time - pcp_stops
        
        # Calcula disponibilidade considerando todas as máquinas
        if adjusted_scheduled_time.total_seconds() > 0:
            availability = (adjusted_scheduled_time - non_pcp_stops) / adjusted_scheduled_time * 100
            return max(0, min(100, availability))
    else:
        # Cálculo para uma única máquina
        pcp_stops = df[df['Área Responsável'] == 'PCP']['Duração'].sum()
        non_pcp_stops = df[df['Área Responsável'] != 'PCP']['Duração'].sum()
        adjusted_scheduled_time = scheduled_time - pcp_stops
        
        if adjusted_scheduled_time.total_seconds() > 0:
            availability = (adjusted_scheduled_time - non_pcp_stops) / adjusted_scheduled_time * 100
            return max(0, min(100, availability))
    
    return 0

@st.cache_data
def calculate_mtbf_mttr(df, scheduled_time):
    """
    Calcula MTBF (Mean Time Between Failures) e MTTR (Mean Time To Repair).
    Considera múltiplas máquinas quando aplicável.
    """
    if df.empty:
        return 0, 0
    
    # Separa paradas do PCP
    non_pcp_df = df[df['Área Responsável'] != 'PCP']
    pcp_stops = df[df['Área Responsável'] == 'PCP']['Duração'].sum()
    
    # Verifica se há múltiplas máquinas
    machines = df['Máquina'].unique()
    num_machines = len(machines)
    
    if num_machines > 1:
        # Ajusta tempo programado para múltiplas máquinas
        total_scheduled_time = scheduled_time * num_machines
        adjusted_scheduled_time = total_scheduled_time - pcp_stops
        
        # Calcula métricas considerando todas as máquinas
        total_stoppages = len(non_pcp_df)
        total_downtime = non_pcp_df['Duração'].sum()
        
        # MTBF em horas (tempo médio entre falhas para todas as máquinas)
        if total_stoppages > 1:
            mtbf = (adjusted_scheduled_time - total_downtime).total_seconds() / 3600 / total_stoppages
        else:
            mtbf = 0
        
        # MTTR em horas (tempo médio de reparo)
        if total_stoppages > 0:
            mttr = total_downtime.total_seconds() / 3600 / total_stoppages
        else:
            mttr = 0
    else:
        # Cálculo para uma única máquina
        adjusted_scheduled_time = scheduled_time - pcp_stops
        total_stoppages = len(non_pcp_df)
        total_downtime = non_pcp_df['Duração'].sum()
        
        if total_stoppages > 1:
            mtbf = (adjusted_scheduled_time - total_downtime).total_seconds() / 3600 / total_stoppages
        else:
            mtbf = 0
        
        if total_stoppages > 0:
            mttr = total_downtime.total_seconds() / 3600 / total_stoppages
        else:
            mttr = 0
    
    return mtbf, mttr

@st.cache_data
def calculate_scheduled_time(df, month_selected=None, start_date=None, end_date=None):
    """
    Calcula tempo programado baseado no período selecionado.
    Considera múltiplas máquinas quando aplicável.
    """
    if start_date and end_date:
        days_in_period = (end_date - start_date).days + 1
    elif month_selected and month_selected not in ["Todos", "All"]:
        year, month = map(int, month_selected.split('-'))
        days_in_period = pd.Period(f"{year}-{month}").days_in_month
    else:
        if df.empty:
            return pd.Timedelta(hours=24 * 30), 24 * 30
        
        days_in_period = (df['Inicio'].max() - df['Inicio'].min()).days + 1
        days_in_period = max(30, days_in_period)
    
    scheduled_time_hours = days_in_period * 24
    return pd.Timedelta(hours=scheduled_time_hours), scheduled_time_hours

@st.cache_data
def calculate_average_downtime(df):
    """Calcula tempo médio de parada (MTTR)."""
    return df['Duração'].mean() if not df.empty else pd.Timedelta(0)

@st.cache_data
def calculate_stoppage_by_area(df):
    """Calcula percentual de paradas por área responsável."""
    if 'Área Responsável' in df.columns and not df.empty:
        area_counts = df['Área Responsável'].value_counts(normalize=True) * 100
        return area_counts
    else:
        return pd.Series()

@st.cache_data
def pareto_stoppage_causes(df):
    """Identifica principais causas de parada (Pareto) por duração total."""
    if 'Parada' in df.columns and not df.empty:
        pareto = df.groupby('Parada')['Duração'].sum().sort_values(ascending=False).head(10)
        return pareto
    else:
        return pd.Series()

@st.cache_data
def most_frequent_stoppages(df):
    """Identifica paradas mais frequentes por contagem."""
    if 'Parada' in df.columns and not df.empty:
        frequent = df['Parada'].value_counts().head(10)
        return frequent
    else:
        return pd.Series()

@st.cache_data
def calculate_stoppage_occurrence_rate(df):
    """Calcula taxa de ocorrência de paradas por mês."""
    if not df.empty:
        monthly_occurrences = df.groupby('Ano-Mês').size()
        return monthly_occurrences
    else:
        return pd.Series()

@st.cache_data
def calculate_total_duration_by_month(df):
    """Calcula duração total de paradas por mês."""
    if not df.empty:
        monthly_duration = df.groupby('Ano-Mês')['Duração'].sum()
        return monthly_duration
    else:
        return pd.Series()

@st.cache_data
def calculate_total_stoppage_time_by_area(df):
    """Calcula tempo total de parada por área."""
    if 'Área Responsável' in df.columns and not df.empty:
        time_by_area = df.groupby('Área Responsável')['Duração'].sum()
        return time_by_area
    else:
        return pd.Series()

@st.cache_data
def identify_critical_stoppages(df, hour_limit=1):
    """Identifica paradas críticas (com duração maior que o limite especificado)."""
    limit = pd.Timedelta(hours=hour_limit)
    if not df.empty:
        critical_stoppages = df[df['Duração'] > limit]
        critical_percentage = len(critical_stoppages) / len(df) * 100 if len(df) > 0 else 0
        return critical_stoppages, critical_percentage
    else:
        return pd.DataFrame(), 0

@st.cache_data
def generate_recommendations(df, availability):
    """Gera recomendações automáticas baseadas nos dados analisados."""
    recommendations = []
    
    # Análise de disponibilidade
    if availability < 70:
        recommendations.append("⚠️ A disponibilidade está abaixo do nível recomendado (70%). Priorize a redução do tempo de parada não programado.")
    elif availability < 85:
        recommendations.append("⚠️ A disponibilidade está em um nível moderado. Considere implementar melhorias no processo de manutenção preventiva.")
    else:
        recommendations.append("✅ A disponibilidade está em um bom nível. Continue monitorando para manter este desempenho.")
    
    # Análise de paradas críticas
    critical_stoppages, critical_percentage = identify_critical_stoppages(df)
    
    if critical_percentage > 20:
        recommendations.append(f"⚠️ Alta incidência de paradas críticas ({critical_percentage:.1f}%). Revise os procedimentos de manutenção corretiva.")
    elif critical_percentage > 10:
        recommendations.append(f"⚠️ Incidência moderada de paradas críticas ({critical_percentage:.1f}%). Implemente um plano de ação para reduzir este índice.")
    else:
        recommendations.append(f"✅ Baixa incidência de paradas críticas ({critical_percentage:.1f}%). Continue monitorando para manter este desempenho.")
    
    # Análise por área responsável
    if 'Área Responsável' in df.columns and not df.empty:
        areas = calculate_stoppage_by_area(df)
        if not areas.empty:
            most_problematic_area = areas.idxmax()
            area_percentage = areas.max()
            if area_percentage > 40:
                recommendations.append(f"⚠️ A área de {most_problematic_area} é responsável por {area_percentage:.1f}% das paradas. Priorize ações nesta área.")
    
    # Análise de tendência
    occurrences = calculate_stoppage_occurrence_rate(df)
    if len(occurrences) >= 3:
        trend = occurrences.iloc[-1] - occurrences.iloc[0]
        if trend > 0:
            recommendations.append("⚠️ Tendência crescente no número de paradas. Revise os procedimentos de manutenção preventiva.")
        elif trend < 0:
            recommendations.append("✅ Tendência decrescente no número de paradas. Continue com as melhorias implementadas.")
    
    return recommendations

@st.cache_data
def compare_periods(data1, data2):
    """
    Compara dois períodos de dados e retorna métricas comparativas.
    
    Args:
        data1: DataFrame com dados do primeiro período
        data2: DataFrame com dados do segundo período
    
    Returns:
        dict: Dicionário com métricas comparativas
    """
    # Calcula tempo programado para cada período
    scheduled_time1, _ = calculate_scheduled_time(data1)
    scheduled_time2, _ = calculate_scheduled_time(data2)
    
    # Calcula métricas para período 1
    availability1 = calculate_availability(data1, scheduled_time1)
    mtbf1, mttr1 = calculate_mtbf_mttr(data1, scheduled_time1)
    total_stoppages1 = len(data1)
    total_downtime1 = data1['Duração'].sum().total_seconds() / 3600
    
    # Calcula métricas para período 2
    availability2 = calculate_availability(data2, scheduled_time2)
    mtbf2, mttr2 = calculate_mtbf_mttr(data2, scheduled_time2)
    total_stoppages2 = len(data2)
    total_downtime2 = data2['Duração'].sum().total_seconds() / 3600
    
    # Calcula diferenças e variações percentuais
    diff_availability = availability2 - availability1
    diff_mtbf = mtbf2 - mtbf1
    diff_mttr = mttr2 - mttr1
    diff_stoppages = total_stoppages2 - total_stoppages1
    diff_downtime = total_downtime2 - total_downtime1
    
    # Calcula variações percentuais
    pct_availability = (diff_availability / availability1 * 100) if availability1 > 0 else float('inf')
    pct_mtbf = (diff_mtbf / mtbf1 * 100) if mtbf1 > 0 else float('inf')
    pct_mttr = (diff_mttr / mttr1 * 100) if mttr1 > 0 else float('inf')
    pct_stoppages = (diff_stoppages / total_stoppages1 * 100) if total_stoppages1 > 0 else float('inf')
    pct_downtime = (diff_downtime / total_downtime1 * 100) if total_downtime1 > 0 else float('inf')
    
    # Retorna resultados
    return {
        'metrics': {
            'availability': (availability1, availability2, diff_availability, pct_availability),
            'mtbf': (mtbf1, mtbf2, diff_mtbf, pct_mtbf),
            'mttr': (mttr1, mttr2, diff_mttr, pct_mttr),
            'total_stoppages': (total_stoppages1, total_stoppages2, diff_stoppages, pct_stoppages),
            'total_downtime': (total_downtime1, total_downtime2, diff_downtime, pct_downtime)
        }
    }

@st.cache_data
def calculate_shifts_distribution(df):
    """
    Calcula a distribuição de paradas por turno.
    
    Args:
        df: DataFrame com os dados de parada
    
    Returns:
        pd.Series: Série com contagem de paradas por turno
    """
    if df.empty:
        return pd.Series()
    
    # Criar função para classificar hora em turno
    def get_shift(hour):
        if 6 <= hour < 14:
            return "06:00 às 14:00"
        elif 14 <= hour < 22:
            return "14:00 às 22:00"
        else:
            return "22:00 às 06:00"
    
    # Aplicar classificação de turno
    df['Turno'] = df['Inicio'].dt.hour.apply(get_shift)
    
    # Contar paradas por turno
    shifts_count = df['Turno'].value_counts()
    
    # Reordenar turnos
    shift_order = ["06:00 às 14:00", "14:00 às 22:00", "22:00 às 06:00"]
    shifts_count = shifts_count.reindex(shift_order).fillna(0)
    
    return shifts_count