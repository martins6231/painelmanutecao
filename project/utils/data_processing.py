import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st
from utils.i18n import get_translation

CHUNK_SIZE = 10000  # Tamanho do chunk para processamento em lote

@st.cache_data(ttl=3600)  # Cache por 1 hora
def process_data(df):
    """Process and clean the DataFrame data."""
    chunks = []
    for chunk_start in range(0, len(df), CHUNK_SIZE):
        chunk_end = chunk_start + CHUNK_SIZE
        chunk = df[chunk_start:chunk_end].copy()
        
        # Machine mapping with treatment for unknown codes
        machine_mapping = {
            78: "PET",
            79: "TETRA 1000",
            80: "TETRA 200",
            89: "SIG 1000",
            91: "SIG 200"
        }
        
        if 'Máquina' in chunk.columns:
            chunk['Máquina'] = chunk['Máquina'].apply(
                lambda x: machine_mapping.get(x, f"Machine {x}")
            )
        
        # Convert time columns to datetime format
        for col in ['Inicio', 'Fim']:
            if col in chunk.columns:
                chunk[col] = pd.to_datetime(chunk[col], errors='coerce')
        
        # Process the duration column
        if 'Duração' in chunk.columns:
            try:
                chunk['Duração'] = pd.to_timedelta(chunk['Duração'])
            except:
                def parse_duration(duration_str):
                    try:
                        parts = duration_str.split(':')
                        if len(parts) == 3:
                            hours, minutes, seconds = map(int, parts)
                            return pd.Timedelta(hours=hours, minutes=minutes, seconds=seconds)
                        else:
                            return pd.NaT
                    except:
                        return pd.NaT
                
                chunk['Duração'] = chunk['Duração'].apply(parse_duration)
        
        # Add time-based columns efficiently using vectorized operations
        chunk['Ano'] = chunk['Inicio'].dt.year
        chunk['Mês'] = chunk['Inicio'].dt.month
        chunk['Mês_Nome'] = chunk['Inicio'].dt.strftime('%B')
        chunk['Ano-Mês'] = chunk['Inicio'].dt.strftime('%Y-%m')
        chunk['Semana'] = chunk['Inicio'].dt.isocalendar().week
        chunk['Dia_Semana'] = chunk['Inicio'].dt.dayofweek
        chunk['Dia_Semana_Nome'] = chunk['Inicio'].dt.day_name()
        chunk['Hora'] = chunk['Inicio'].dt.hour
        
        # Remove records with missing values in essential columns
        chunk = chunk.dropna(subset=['Máquina', 'Inicio', 'Fim', 'Duração'])
        chunks.append(chunk)
    
    return pd.concat(chunks, ignore_index=True)

@st.cache_data(ttl=1800)  # Cache por 30 minutos
def filter_data(df, machine, month=None, start_date=None, end_date=None, page=1, items_per_page=1000):
    """Filter data with pagination support."""
    filtered_df = df.copy()
    
    if machine != "Todas" and machine != "All":
        filtered_df = filtered_df[filtered_df['Máquina'] == machine]
    
    if month and month != "Todos" and month != "All":
        filtered_df = filtered_df[filtered_df['Ano-Mês'] == month]
    
    if start_date and end_date:
        filtered_df = filtered_df[
            (filtered_df['Inicio'] >= start_date) & 
            (filtered_df['Inicio'] <= end_date)
        ]
    
    # Calculate pagination
    total_items = len(filtered_df)
    total_pages = -(-total_items // items_per_page)  # Ceiling division
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    
    paginated_df = filtered_df.iloc[start_idx:end_idx].copy()
    
    return paginated_df, total_items, total_pages

@st.cache_data(ttl=1800)
def get_download_link(df, filename, text):
    """Generate a download link with chunked processing for large files."""
    import io
    import base64
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename_with_timestamp = f"{filename.split('.')[0]}_{timestamp}.xlsx"
    
    output = io.BytesIO()
    
    # Write data in chunks
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for chunk_start in range(0, len(df), CHUNK_SIZE):
            chunk_end = chunk_start + CHUNK_SIZE
            chunk = df.iloc[chunk_start:chunk_end]
            if chunk_start == 0:
                chunk.to_excel(writer, sheet_name='Data', index=True)
            else:
                chunk.to_excel(writer, sheet_name='Data', index=True, startrow=chunk_start+1, header=False)
    
    b64 = base64.b64encode(output.getvalue()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename_with_timestamp}" class="download-button">{text}</a>'
    return href

@st.cache_data(ttl=3600)
def calculate_aggregated_metrics(df):
    """Calculate aggregated metrics efficiently."""
    if df.empty:
        return {
            'total_records': 0,
            'unique_machines': 0,
            'total_duration': pd.Timedelta(0),
            'avg_duration': pd.Timedelta(0),
            'monthly_counts': pd.Series(dtype=int),
            'machine_stats': pd.DataFrame()
        }
    
    try:
        # Calculate monthly counts as integers
        monthly_counts = df.groupby('Ano-Mês').size()
        
        metrics = {
            'total_records': len(df),
            'unique_machines': df['Máquina'].nunique(),
            'total_duration': df['Duração'].sum(),
            'avg_duration': df['Duração'].mean(),
            'monthly_counts': monthly_counts,  # Now storing as integer counts
            'machine_stats': df.groupby('Máquina').agg({
                'Duração': ['count', 'sum', 'mean']
            })
        }
        return metrics
    except Exception as e:
        st.error(f"Erro ao calcular métricas: {str(e)}")
        return {
            'total_records': 0,
            'unique_machines': 0,
            'total_duration': pd.Timedelta(0),
            'avg_duration': pd.Timedelta(0),
            'monthly_counts': pd.Series(dtype=int),
            'machine_stats': pd.DataFrame()
        }
