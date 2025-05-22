import streamlit as st
from components.dashboard import show_dashboard
from components.data_view import show_data_view
from components.about import show_about
from components.comparison import show_comparison
from utils.styles import apply_styles
from streamlit_option_menu import option_menu

# ----- CONFIGURAÇÃO DA PÁGINA -----
st.set_page_config(
    page_title="Análise de Eficiência de Máquinas",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Aplica estilos CSS
apply_styles()

# Inicializa estado da sessão
if 'df' not in st.session_state:
    st.session_state.df = None

if 'resultados' not in st.session_state:
    st.session_state.resultados = None

if 'comparison_data' not in st.session_state:
    st.session_state.comparison_data = None

if 'first_load' not in st.session_state:
    st.session_state.first_load = False

# Initialize language state
if 'language' not in st.session_state:
    st.session_state.language = 'pt'

# Logo da Britvic
with st.container():
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    logo_url = "https://raw.githubusercontent.com/martins6231/app_atd/main/britvic_logo.png"
    st.image(logo_url, width=200, output_format="PNG", use_container_width=False)
    st.markdown('</div>', unsafe_allow_html=True)

# Título principal
st.markdown('<div class="main-title">Análise de Eficiência de Máquinas</div>', unsafe_allow_html=True)

# Menu de navegação
selected = option_menu(
    menu_title=None,
    options=["Painel Principal", "Análise Comparativa", "Visualização de Dados", "Informações"],
    icons=["speedometer2", "graph-up-arrow", "table", "info-circle"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#f8f9fa", "border-radius": "10px", "margin-bottom": "20px"},
        "icon": {"color": "#3498db", "font-size": "14px"},
        "nav-link": {"font-size": "14px", "text-align": "center", "margin": "0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "#3498db", "color": "white"},
    }
)

# Exibe a página selecionada
if selected == "Painel Principal":
    show_dashboard()
elif selected == "Análise Comparativa":
    show_comparison()
elif selected == "Visualização de Dados":
    show_data_view()
elif selected == "Informações":
    show_about()

# Rodapé
st.markdown("""
<div class="footer">
    <p>© 2025 Análise de Eficiência de Máquinas | Desenvolvido com ❤️ usando Streamlit</p>
    <p><small>Versão 3.1.0 | Última atualização: Maio 2025</small></p>
</div>
""", unsafe_allow_html=True)