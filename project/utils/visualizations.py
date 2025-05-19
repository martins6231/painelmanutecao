import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from utils.i18n import get_translation

@st.cache_data
def create_monthly_duration_chart(monthly_counts, language='pt'):
    """Create a line chart for monthly counts."""
    t = get_translation(language)
    
    if monthly_counts.empty or len(monthly_counts) <= 1:
        return None
    
    fig = px.line(
        x=monthly_counts.index,
        y=monthly_counts.values,
        markers=True,
        labels={'x': t('month'), 'y': t('number_of_stoppages')},
        title=t('stoppages_by_month_title'),
        color_discrete_sequence=['#2ecc71']
    )
    
    # Add area under the line for better visualization of trends
    fig.add_trace(
        go.Scatter(
            x=monthly_counts.index,
            y=monthly_counts.values,
            fill='tozeroy',
            fillcolor='rgba(46, 204, 113, 0.2)',
            line=dict(color='rgba(46, 204, 113, 0)'),
            showlegend=False
        )
    )
    
    # Add values above points
    for i, v in enumerate(monthly_counts):
        fig.add_annotation(
            x=monthly_counts.index[i],
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
        }
    )
    
    return fig
