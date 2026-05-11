import pandas as pd
import streamlit as st
import requests
from io import StringIO

# 1. Configuração da página - o layout wide é o ponto de partida
st.set_page_config(page_title="Gestão de Leitos", layout="wide")

def carregar_dados():
    SHEET_ID = "1N0zcHuMz2gmilXlu8bKujkwDggPnTxg8fVp90eWEUw4"
    URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
    try:
        response = requests.get(URL)
        response.raise_for_status()
        conteudo = response.text.replace('Âº', 'º').replace('âº', 'º')
        df_raw = pd.read_csv(StringIO(conteudo))
        
        df_final = pd.DataFrame()
        df_final['BLOCO'] = df_raw.iloc[:, 0].astype(str)
        df_final['UNIDADE'] = df_raw.iloc[:, 1].astype(str)
        df_final['ESPECIALIDADE'] = df_raw.iloc[:, 2].astype(str)
        df_final['PARA'] = df_raw.iloc[:, 5].astype(str)
        df_final['TIPO'] = df_raw.iloc[:, 9].astype(str)
        
        if df_raw.shape[1] >= 22: 
            df_final['STATUS'] = df_raw.iloc[:, 21].fillna('CINZA').astype(str).str.upper().str.strip()
        else:
            df_final['STATUS'] = 'CINZA'

        df_final = df_final.map(lambda x: x.strip() if isinstance(x, str) else x)
        return df_final
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None

# 2. CSS PARA TRAVAR COLUNA E PERMITIR SCROLL GLOBAL
st.markdown("""
    <style>
    /* Remove os limites de largura do Streamlit para o scroll ser na página toda */
    .main .block-container {
        max-width: none !important;
        width: 100% !important;
        padding: 1rem 0rem 5rem 0rem !important;
        overflow-x: visible !important;
    }
    
    /* Container que força a largura conforme o conteúdo */
    .painel-container {
        display: inline-block !important;
        min-width: 100%;
        background-color: white;
    }

    /* Linha de cada unidade */
    .linha-hospital {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: stretch !important;
        border-bottom: 1px solid #f0f2f6;
    }

    /* COLUNA TRAVADA (STICKY) */
    .coluna-unidade-fixa {
        position: -webkit-sticky; /* Suporte Safari */
        position: sticky;
        left: 0;
        z-index: 999;
        background-color: #ffffff;
        min-width: 180px;
        width: 180px;
        padding: 15px;
        box-shadow: 5px 0 10px -5px rgba(0,0,0,0.1); /* Sombra para não sobrepor visualmente */
        display: flex;
        flex-direction: column;
        justify-content: center;
        border-right: 1px solid #e6e9ef;
    }

    .nome-unidade { font-size: 13px; font-weight: bold; color: #1e293b; margin: 0; }
    .nome-especialidade { font-size: 11px; color: #64748b; margin: 0; }

    /* ÁREA DOS CARDS */
    .wrapper-leitos {
        display: flex !important;
        gap: 8px;
        padding: 10px 20px;
    }

    .card-hospitalar {
        flex: 0 0 110px !important; /* Tamanho fixo e confortável */
        width: 110px !important;
        background: #fff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px 5px;
        text-align: center;
        transition: transform 0.2s;
    }
    
    .card-hospitalar:hover { border-color: #cbd5e1; }

    .leito-id { font-size: 14px; font-weight: 800; color: #0f172a; margin-bottom: 2px; }
    .leito-tipo { font-size: 9px; color: #94a3b8; text-transform: uppercase; font-weight: 600; }
    .indicador-status { height: 6px; border-radius: 3px; margin-top: 8px; width: 80%; margin-left: 10%; }

    /* Ajuste para o título não sumir ao rolar */
    .titulo-painel {
        position: sticky;
        left: 0;
        padding: 20px;
        background: white;
        z-index: 1000;
        width: 100vw;
    }
    </style>
    """, unsafe_allow_html=True)

df = carregar_dados()

if df is not None:
    # Título travado também à esquerda
    st.markdown('<div class="titulo-painel"><h2>🏥 Gestão Centralizada de Leitos</h2></div>', unsafe_allow_html=True)
    
    cores = {
        'VERDE': '#22c55e', 
        'AMARELO': '#eab308', 
        'VERMELHO': '#ef4444', 
        'CINZA': '#94a3b8'
    }

    # Início do container que permite o scroll lateral na página toda
    painel_html = "<div class='painel-container'>"

    for (unidade, especialidade), g_esp in df.groupby(['UNIDADE', 'ESPECIALIDADE'], sort=False):
        painel_html += f"<div class='linha-hospital'>"
        
        # Coluna fixa
        painel_html += f"""
            <div class='coluna-unidade-fixa'>
                <p class='nome-unidade'>{unidade}</p>
                <p class='nome-especialidade'>{especialidade}</p>
            </div>
        """
        
        # Início dos cards
        painel_html += "<div class='wrapper-leitos'>"
        for _, row in g_esp.iterrows():
            cor = cores.get(row['STATUS'], cores['CINZA'])
            painel_html += f'''
                <div class="card-hospitalar">
                    <div class="leito-id">{row['PARA']}</div>
                    <div class="leito-tipo">{row['TIPO']}</div>
                    <div class="indicador-status" style="background-color: {cor};"></div>
                </div>
            '''
        painel_html += "</div></div>" # Fecha wrapper e linha

    painel_html += "</div>" # Fecha painel-container
    
    st.markdown(painel_html, unsafe_allow_html=True)

else:
    st.info("Aguardando conexão com os dados...")
