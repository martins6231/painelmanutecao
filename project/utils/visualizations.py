import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from utils.i18n import get_translation

@st.cache_data
def create_pareto_chart(pareto, language='pt'):
    """Create a Pareto chart with Plotly."""
    t = get_translation(language)
    
    if pareto.empty:
        return None
    
    # Convert durations to hours
    pareto_hours = pareto.apply(lambda x: x.total_seconds() / 3600)
    
    fig = px.bar(
        x=pareto_hours.index,
        y=pareto_hours.values,
        labels={'x': t('stoppage_cause'), 'y': t('total_duration_hours')},
        title=t('pareto_stoppages_title'),
        color_discrete_sequence=['#3498db'],
        text=pareto_hours.values.round(1)
    )
    
    fig.update_traces(
        texttemplate='%{text}h',
        textposition='outside',
        width=0.7,
        marker_line_width=1,
        marker_line_color='rgba(0,0,0,0.1)'
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        autosize=True,
        margin=dict(l=50, r=50, t=80, b=100),
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis_title=t('total_duration_hours'),
        xaxis_title=t('stoppage_cause'),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        ),
        title={
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        showlegend=False
    )
    
    return fig

@st.cache_data
def create_area_pie_chart(area_index, language='pt'):
    """Create a pie chart for responsible areas with Plotly."""
    t = get_translation(language)
    
    if area_index.empty:
        return None
    
    fig = px.pie(
        values=area_index.values,
        names=area_index.index,
        title=t('stoppages_by_area_title'),
        color_discrete_sequence=px.colors.qualitative.Set3,
        hole=0.4
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(line=dict(color='#FFFFFF', width=2)),
        pull=[0.05 if i == area_index.values.argmax() else 0 for i in range(len(area_index))],
        textfont_size=12
    )
    
    fig.update_layout(
        autosize=True,
        margin=dict(l=20, r=20, t=80, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        title={
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )
    
    return fig

@st.cache_data
def create_occurrences_chart(occurrences, language='pt'):
    """Create a line chart for monthly occurrences with Plotly."""
    t = get_translation(language)
    
    if occurrences.empty or len(occurrences) <= 1:
        return None
    
    fig = px.line(
        x=occurrences.index,
        y=occurrences.values,
        markers=True,
        labels={'x': t('month'), 'y': t('number_of_stoppages')},
        title=t('stoppages_by_month_title'),
        color_discrete_sequence=['#2ecc71']
    )
    
    # Add area under the line
    fig.add_trace(
        go.Scatter(
            x=occurrences.index,
            y=occurrences.values,
            fill='tozeroy',
            fillcolor='rgba(46, 204, 113, 0.2)',
            line=dict(color='rgba(46, 204, 113, 0)'),
            showlegend=False
        )
    )
    
    # Update line and markers
    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=8, line=dict(width=2, color='white')),
        selector=dict(mode='lines+markers')
    )
    
    # Add values above points
    for i, v in enumerate(occurrences):
        fig.add_annotation(
            x=occurrences.index[i],
            y=v,
            text=str(v),
            showarrow=False,
            yshift=10,
            font=dict(color="#2c3e50")
        )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        autosize=True,
        margin=dict(l=50, r=50, t=80, b=100),
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis_title=t('number_of_stoppages'),
        xaxis_title=t('month'),
        hovermode="x unified",
        title={
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        showlegend=False
    )
    
    return fig

@st.cache_data
def create_monthly_duration_chart(monthly_duration, language='pt'):
    """Create a line chart for total stoppage duration by month."""
    t = get_translation(language)
    
    if monthly_duration.empty or len(monthly_duration) <= 1:
        return None
    
    # Convert durations to hours
    duration_hours = monthly_duration.apply(lambda x: x.total_seconds() / 3600)
    
    fig = px.line(
        x=duration_hours.index,
        y=duration_hours.values,
        markers=True,
        labels={'x': t('month'), 'y': t('total_duration_hours')},
        title=t('total_duration_by_month_title'),
        color_discrete_sequence=['#e74c3c']
    )
    
    # Add area under the line
    fig.add_trace(
        go.Scatter(
            x=duration_hours.index,
            y=duration_hours.values,
            fill='tozeroy',
            fillcolor='rgba(231, 76, 60, 0.2)',
            line=dict(color='rgba(231, 76, 60, 0)'),
            showlegend=False
        )
    )
    
    # Update line and markers
    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=8, line=dict(width=2, color='white')),
        selector=dict(mode='lines+markers')
    )
    
    # Add values above points
    for i, v in enumerate(duration_hours):
        fig.add_annotation(
            x=duration_hours.index[i],
            y=v,
            text=f"{v:.1f}h",
            showarrow=False,
            yshift=10,
            font=dict(color="#2c3e50")
        )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        autosize=True,
        margin=dict(l=50, r=50, t=80, b=100),
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis_title=t('total_duration_hours'),
        xaxis_title=t('month'),
        hovermode="x unified",
        title={
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        showlegend=False
    )
    
    return fig

@st.cache_data
def create_area_time_chart(area_time, language='pt'):
    """Create a horizontal bar chart for time by area with Plotly."""
    t = get_translation(language)
    
    if area_time.empty:
        return None
    
    # Convert durations to hours
    area_time_hours = area_time.apply(lambda x: x.total_seconds() / 3600)
    
    # Sort data for better visualization
    area_time_hours = area_time_hours.sort_values(ascending=True)
    
    fig = px.bar(
        y=area_time_hours.index,
        x=area_time_hours.values,
        orientation='h',
        labels={'y': t('responsible_area'), 'x': t('total_duration_hours')},
        title=t('total_time_by_area_title'),
        color_discrete_sequence=['#e74c3c'],
        text=area_time_hours.values.round(1)
    )
    
    fig.update_traces(
        texttemplate='%{text}h',
        textposition='outside',
        width=0.7,
        marker_line_width=1,
        marker_line_color='rgba(0,0,0,0.1)'
    )
    
    fig.update_layout(
        autosize=True,
        margin=dict(l=50, r=50, t=80, b=50),
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title=t('total_duration_hours'),
        yaxis_title=t('responsible_area'),
        title={
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        showlegend=False
    )
    
    return fig

@st.cache_data
def create_critical_stoppages_chart(top_critical, language='pt'):
    """Create a horizontal bar chart for critical stoppages with Plotly."""
    t = get_translation(language)
    
    if top_critical.empty:
        return None
    
    # Convert durations to hours
    top_critical_hours = top_critical.apply(lambda x: x.total_seconds() / 3600)
    
    # Sort data for better visualization
    top_critical_hours = top_critical_hours.sort_values(ascending=True)
    
    fig = px.bar(
        y=top_critical_hours.index,
        x=top_critical_hours.values,
        orientation='h',
        labels={'y': t('stoppage_type'), 'x': t('total_duration_hours')},
        title=t('critical_stoppages_title'),
        color_discrete_sequence=['#9b59b6'],
        text=top_critical_hours.values.round(1)
    )
    
    fig.update_traces(
        texttemplate='%{text}h',
        textposition='outside',
        width=0.7,
        marker_line_width=1,
        marker_line_color='rgba(0,0,0,0.1)'
    )
    
    fig.update_layout(
        autosize=True,
        margin=dict(l=50, r=50, t=80, b=50),
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title=t('total_duration_hours'),
        yaxis_title=t('stoppage_type'),
        title={
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        showlegend=False
    )
    
    return fig

@st.cache_data
def create_critical_areas_pie_chart(critical_stoppages, language='pt'):
    """Create a pie chart for responsible areas for critical stoppages."""
    t = get_translation(language)
    
    if 'Área Responsável' not in critical_stoppages.columns or critical_stoppages.empty:
        return None
    
    critical_areas = critical_stoppages['Área Responsável'].value_counts()
    
    fig = px.pie(
        values=critical_areas.values,
        names=critical_areas.index,
        title=t('critical_stoppages_by_area_title'),
        color_discrete_sequence=px.colors.qualitative.Set3,
        hole=0.4
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(line=dict(color='#FFFFFF', width=2)),
        textfont_size=12
    )
    
    fig.update_layout(
        autosize=True,
        margin=dict(l=20, r=20, t=80, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        title={
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )
    
    return fig

@st.cache_data
def create_duration_distribution_chart(df, language='pt'):
    """Create a histogram of the distribution of stoppage durations."""
    t = get_translation(language)
    
    if df.empty:
        return None
    
    # Convert durations to minutes for better visualization
    durations_minutes = df['Duração'].apply(lambda x: x.total_seconds() / 60)
    
    fig = px.histogram(
        x=durations_minutes,
        nbins=20,
        labels={'x': t('duration_minutes'), 'y': t('frequency')},
        title=t('duration_distribution_title'),
        color_discrete_sequence=['#1abc9c']
    )
    
    fig.update_traces(
        marker_line_width=1,
        marker_line_color='rgba(0,0,0,0.1)',
        opacity=0.8
    )
    
    fig.update_layout(
        autosize=True,
        margin=dict(l=50, r=50, t=80, b=50),
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title=t('duration_minutes'),
        yaxis_title=t('frequency'),
        bargap=0.1,
        title={
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        showlegend=False
    )
    
    return fig

@st.cache_data
def create_comparison_gauge_chart(value1, value2, title, max_value=100, language='pt'):
    """Create a gauge chart to compare two values."""
    t = get_translation(language)
    
    diff = value2 - value1
    pct_diff = (diff / value1) * 100 if value1 > 0 else 0
    
    # Determine color based on metric type
    if title.lower() in ['availability', 'efficiency', 'mtbf', 'disponibilidade', 'eficiência']:
        color = "#2ecc71" if diff > 0 else "#e74c3c"
    else:
        color = "#2ecc71" if diff < 0 else "#e74c3c"
    
    fig = go.Figure()
    
    # Add first period value as reference
    fig.add_trace(go.Indicator(
        mode="number",
        value=value1,
        title={"text": f"<span style='font-size:0.8em;color:gray'>{t('period')} 1</span>"},
        domain={'row': 0, 'column': 0},
        number={'suffix': '%' if max_value == 100 else 'h', 'font': {'size': 20, 'color': 'gray'}},
    ))
    
    # Add gauge for current period
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=value2,
        title={"text": f"<span style='font-size:1em'>{title}</span><br><span style='font-size:0.8em;color:gray'>{t('period')} 2</span>"},
        delta={'reference': value1, 'relative': True, 'valueformat': '.1f%'},
        gauge={
            'axis': {'range': [None, max_value], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, max_value/3], 'color': 'rgba(255, 0, 0, 0.1)'},
                {'range': [max_value/3, 2*max_value/3], 'color': 'rgba(255, 255, 0, 0.1)'},
                {'range': [2*max_value/3, max_value], 'color': 'rgba(0, 255, 0, 0.1)'}
            ],
        },
        number={'suffix': '%' if max_value == 100 else 'h', 'font': {'size': 30}},
        domain={'row': 0, 'column': 1}
    ))
    
    fig.update_layout(
        grid={'rows': 1, 'columns': 2, 'pattern': "independent"},
        margin=dict(l=50, r=50, t=80, b=50),
        height=250,
        title={
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )
    
    return fig

@st.cache_data
def create_comparative_bar_chart(metric1, metric2, title, language='pt'):
    """Create a comparative bar chart for two periods."""
    t = get_translation(language)
    
    labels = [f"{t('period')} 1", f"{t('period')} 2"]
    values = [metric1, metric2]
    
    diff = metric2 - metric1
    pct_diff = (diff / metric1) * 100 if metric1 > 0 else 0
    
    # Determine color based on metric type
    if title.lower() in ['availability', 'efficiency', 'mtbf', 'disponibilidade', 'eficiência']:
        colors = ["#3498db", "#2ecc71" if diff > 0 else "#e74c3c"]
    else:
        colors = ["#3498db", "#2ecc71" if diff < 0 else "#e74c3c"]
    
    fig = px.bar(
        x=labels,
        y=values,
        text=[f"{v:.2f}" for v in values],
        title=f"{title} {t('comparison')}",
        color_discrete_sequence=colors
    )
    
    fig.update_traces(
        textposition='outside',
        textfont_size=14,
        width=0.7,
        marker_line_width=1,
        marker_line_color='rgba(0,0,0,0.1)'
    )
    
    # Add annotation showing the percent change
    arrow = "⬆️" if diff > 0 else "⬇️"
    annotation_text = f"{arrow} {abs(pct_diff):.1f}%"
    
    fig.add_annotation(
        x=1, y=metric2,
        text=annotation_text,
        showarrow=False,
        font=dict(size=16),
        yshift=20
    )
    
    fig.update_layout(
        autosize=True,
        margin=dict(l=50, r=50, t=80, b=50),
        plot_bgcolor='rgba(0,0,0,0)',
        title={
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        showlegend=False
    )
    
    return fig

@st.cache_data
def create_shifts_distribution_chart(shifts_data, language='pt'):
    """Create a bar chart for shift distribution."""
    t = get_translation(language)
    
    if shifts_data.empty:
        return None
    
    fig = px.bar(
        x=shifts_data.index,
        y=shifts_data.values,
        labels={'x': 'Turno', 'y': 'Número de Paradas'},
        title='Distribuição de Paradas por Turno',
        color_discrete_sequence=['#2ecc71'],
        text=shifts_data.values
    )
    
    fig.update_traces(
        texttemplate='%{text:.0f}',
        textposition='outside',
        width=0.7,
        marker_line_width=1,
        marker_line_color='rgba(0,0,0,0.1)'
    )
    
    fig.update_layout(
        xaxis_tickangle=0,
        autosize=True,
        margin=dict(l=50, r=50, t=80, b=50),
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis_title='Número de Paradas',
        xaxis_title='Turno',
        title={
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        showlegend=False
    )
    
    return fig