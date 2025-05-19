import streamlit as st

def apply_styles():
    """Aplica estilos CSS otimizados para a aplicação."""
    st.markdown(
        """
        <style>
        /* Estilos Base */
        body {
            font-family: 'Inter', sans-serif;
            color: #333;
            line-height: 1.5;
        }

        /* Container Principal */
        .main-container {
            max-width: 1200px;
            padding: 1rem;
            margin: auto;
        }

        /* Container do Logo */
        .logo-container {
            text-align: left;
            margin-bottom: 1rem;
            padding: 1rem 0;
        }

        /* Tipografia */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 1rem;
            line-height: 1.2;
        }

        /* Títulos */
        .main-title {
            font-size: 2.2rem;
            color: #264653;
            font-weight: 700;
            text-align: center;
            margin: 1.5rem 0;
            letter-spacing: -0.5px;
            background: linear-gradient(45deg, #264653, #2a9d8f);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .section-title {
            font-size: 1.5rem;
            color: #2a9d8f;
            border-bottom: 2px solid #2a9d8f;
            padding-bottom: 0.5rem;
            margin: 1.5rem 0;
            width: 100%;
            display: inline-block;
            text-align: center;
        }

        /* Botões de Ação */
        .stButton > button {
            background-color: #2a9d8f;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 0.5rem 1rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-size: 0.875rem;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }

        .stButton > button:hover {
            background-color: #1e7d7a;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            transform: translateY(-1px);
        }

        /* Botão de Download */
        .download-button {
            display: inline-block;
            background-color: #3498db;
            color: white !important;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-weight: 500;
            margin-top: 0.5rem;
            transition: all 0.3s ease;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }

        .download-button:hover {
            background-color: #2980b9;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            transform: translateY(-1px);
        }

        /* Caixas de Conteúdo */
        .content-box {
            background-color: white;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border: 1px solid #f0f0f0;
        }

        .content-box:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
        }

        /* Caixas de Métricas */
        .metric-box {
            background-color: white;
            padding: 1.25rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            flex: 1;
            min-width: 200px;
            margin-bottom: 1rem;
            text-align: center;
            transition: transform 0.3s ease;
            border-top: 3px solid #2a9d8f;
        }

        .metric-box:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
        }

        .metric-value {
            font-size: 2rem;
            color: #1d3557;
            font-weight: 700;
            line-height: 1;
            margin-bottom: 0.5rem;
        }

        .metric-label {
            color: #457b9d;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 500;
        }

        /* Gráficos */
        .chart-container {
            background-color: white;
            padding: 1.5rem;
            margin: 1rem 0;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            transition: transform 0.3s ease;
            border: 1px solid #f0f0f0;
        }

        .chart-container:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
        }

        /* Upload de Arquivo */
        .uploadedFile {
            border: 2px dashed #2a9d8f;
            border-radius: 8px;
            padding: 1rem;
            margin-top: 0.5rem;
            background-color: rgba(42, 157, 143, 0.05);
            transition: all 0.3s ease;
        }

        .uploadedFile:hover {
            background-color: rgba(42, 157, 143, 0.1);
            border-color: #1e7d7a;
        }

        /* Estilo das Abas */
        .stTabs [data-baseweb="tab-list"] {
            gap: 1rem;
        }

        .stTabs [data-baseweb="tab"] {
            height: 3rem;
            white-space: pre-wrap;
            background-color: #f8f9fa;
            border-radius: 6px 6px 0 0;
            border: 1px solid #f0f0f0;
            border-bottom: none;
            font-weight: 500;
            color: #495057;
        }

        .stTabs [aria-selected="true"] {
            background-color: white;
            color: #2a9d8f;
            border-top: 3px solid #2a9d8f;
        }

        /* Seletor de Data */
        .stDateInput > div > div {
            padding: 0.5rem;
            border-radius: 6px;
            border: 1px solid #ced4da;
        }

        /* Tabelas */
        .dataframe {
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 1rem;
            font-size: 0.9rem;
        }

        .dataframe th {
            background-color: #f8f9fa;
            color: #495057;
            font-weight: 600;
            text-align: left;
            padding: 0.75rem;
            border-bottom: 2px solid #dee2e6;
        }

        .dataframe td {
            padding: 0.75rem;
            border-top: 1px solid #dee2e6;
            text-align: left;
            vertical-align: top;
        }

        .dataframe tr:hover {
            background-color: rgba(0, 0, 0, 0.03);
        }

        /* Rodapé */
        .footer {
            text-align: center;
            padding: 1.5rem 0;
            margin-top: 2rem;
            font-size: 0.875rem;
            color: #6c757d;
            border-top: 1px solid #dee2e6;
        }

        /* Animações */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .main-title, .section-title, .content-box, .metric-box, .chart-container {
            animation: fadeIn 0.5s ease-out forwards;
        }

        /* Design Responsivo */
        @media (max-width: 768px) {
            .main-title {
                font-size: 1.8rem;
            }
            
            .section-title {
                font-size: 1.3rem;
            }
            
            .metric-box {
                min-width: 100%;
            }
            
            .metric-value {
                font-size: 1.6rem;
            }
        }
        </style>
        """, 
        unsafe_allow_html=True
    )