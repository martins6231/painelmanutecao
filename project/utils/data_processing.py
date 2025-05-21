import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st
from utils.i18n import get_translation

@st.cache_data
def process_data(df):
    """Process and clean the DataFrame data."""
    # Create a copy to avoid SettingWithCopyWarning
    df_processed = df.copy()
    
    # Machine mapping with treatment for unknown codes
    machine_mapping = {
        78: "PET",
        79: "TETRA 1000",
        80: "TETRA 200",
        89: "SIG 1000",
        91: "SIG 200"
    }
    
    if 'Máquina' in df_processed.columns:
        # Preserve the original code if not in the mapping
        df_processed['Máquina'] = df_processed['Máquina'].apply(
            lambda x: machine_mapping.get(x, f"Machine {x}")
        )
    
    # Convert time columns to datetime format
    for col in ['Inicio', 'Fim']:
        if col in df_processed.columns:
            df_processed[col] = pd.to_datetime(df_processed[col], errors='coerce')
    
    # Process the duration column
    if 'Duração' in df_processed.columns:
        # Try to convert the Duration column to timedelta
        try:
            df_processed['Duração'] = pd.to_timedelta(df_processed['Duração'])
        except:
            # If it fails, try to extract hours, minutes, and seconds and create a timedelta
            if isinstance(df_processed['Duração'].iloc[0], str):
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
                
                df_processed['Duração'] = df_processed['Duração'].apply(parse_duration)
    
    # Add year, month, and year-month columns for easier filtering
    df_processed['Ano'] = df_processed['Inicio'].dt.year
    df_processed['Mês'] = df_processed['Inicio'].dt.month
    df_processed['Mês_Nome'] = df_processed['Inicio'].dt.strftime('%B')  # Month name
    df_processed['Ano-Mês'] = df_processed['Inicio'].dt.strftime('%Y-%m')
    
    # Add week number and day of week for more detailed analysis
    df_processed['Semana'] = df_processed['Inicio'].dt.isocalendar().week
    df_processed['Dia_Semana'] = df_processed['Inicio'].dt.dayofweek
    df_processed['Dia_Semana_Nome'] = df_processed['Inicio'].dt.day_name()
    
    # Add hour of day for time-based analysis
    df_processed['Hora'] = df_processed['Inicio'].dt.hour
    
    # Remove records with missing values in essential columns
    df_processed = df_processed.dropna(subset=['Máquina', 'Inicio', 'Fim', 'Duração'])
    
    return df_processed

@st.cache_data
def format_duration(duration):
    """Format a duration (timedelta) for display."""
    if pd.isna(duration):
        return "00:00:00"
    
    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

@st.cache_data
def get_month_name(month_year, language='pt'):
    """Convert the 'YYYY-MM' format to a readable month name."""
    t = get_translation(language)
    
    if month_year == 'Todos' or month_year == 'All':
        return t("all_months")
    
    try:
        date = datetime.strptime(month_year, '%Y-%m')
        if language == 'pt':
            months_dict = {
                1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
                5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
                9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
            }
            return f"{months_dict[date.month]} {date.year}"
        else:
            months_dict = {
                1: 'January', 2: 'February', 3: 'March', 4: 'April',
                5: 'May', 6: 'June', 7: 'July', 8: 'August',
                9: 'September', 10: 'October', 11: 'November', 12: 'December'
            }
            return f"{months_dict[date.month]} {date.year}"
    except:
        return month_year

@st.cache_data
def filter_data_by_date_range(df, start_date, end_date):
    """Filter data by date range."""
    if start_date and end_date:
        return df[(df['Inicio'] >= start_date) & (df['Inicio'] <= end_date)]
    return df

@st.cache_data
def filter_data(df, machine, month=None, start_date=None, end_date=None):
    """Filter data based on machine, month, or date range."""
    filtered_data = df.copy()
    
    if machine != "Todas" and machine != "All":
        filtered_data = filtered_data[filtered_data['Máquina'] == machine]
    
    # Filter by month if specified
    if month and month != "Todos" and month != "All":
        filtered_data = filtered_data[filtered_data['Ano-Mês'] == month]
    
    # Filter by date range if specified (overrides month filter)
    if start_date and end_date:
        filtered_data = filtered_data[(filtered_data['Inicio'] >= start_date) & 
                                      (filtered_data['Inicio'] <= end_date)]
    
    return filtered_data

@st.cache_data
def get_download_link(df, filename, text):
    """Generate a download link for a DataFrame as an Excel file."""
    import io
    import base64
    from datetime import datetime
    
    # Add timestamp to filename to prevent caching issues
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename_with_timestamp = f"{filename.split('.')[0]}_{timestamp}.xlsx"
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Data', index=True)
    
    b64 = base64.b64encode(output.getvalue()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename_with_timestamp}" class="download-button">{text}</a>'
    return href