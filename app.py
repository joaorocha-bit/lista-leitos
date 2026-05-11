import pandas as pd
import streamlit as st
import requests
from io import StringIO

# Configuração da página
st.set_page_config(page_title="Painel Horizontal de Leitos", layout="wide")

def carregar_dados():
    SHEET_ID = "1N0zcHuMz2gmilXlu8bKujkwDggPnTxg8fVp90eWEUw4"
    URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
    
    try:
        response = requests.get(URL)
        response.raise_for_status()
        conteudo_limpo = response.text.replace('Âº', 'º').replace('âº', 'º')
        df_raw = pd.read_csv(StringIO(conteudo_limpo))
        
        df_final = pd.DataFrame()
        df_final['BLOCO'] = df_raw.iloc[:, 0].astype(str)         # Coluna A
        df_final['UNIDADE'] = df_raw.iloc[:, 1].astype(str)       # Coluna B
        df_final['ESPECIALIDADE'] = df_raw.iloc[:, 2].astype(str) # Coluna C
        df_final['PARA'] = df_raw.iloc[:, 5].astype(str)          # Coluna F
        df_final['TIPO'] = df_raw.iloc[:, 9].astype(str)          # Coluna J
        
        # STATUS na Coluna V (Índice 21)
        if df_raw.shape[1] >= 22: 
            df_final['STATUS'] = df_raw.iloc[:, 21].fillna('CINZA').astype(str).str.upper().str.strip()
        else:
            df_final['STATUS'] = 'CINZA'

        df_final = df_final.map(lambda x: x.strip() if isinstance(x, str) else x)
        return df_final
    except Exception as e:
        st.error(f"Erro ao carregar planilha: {e}")
        return None

# --- ESTILIZAÇÃO CSS PARA SCROLL HORIZONTAL ---
st.markdown("""
    <style>
    .scroll-container {
        display: flex;
        overflow-x: auto;
        white-space: nowrap;
        padding: 10px 0px;
        gap: 10px;
        scrollbar-width: thin;
        scrollbar-color: #bdc3c7 #f8f9fa;
    }
    .leito-card {
        flex: 0 0 auto; /* Impede o card de encolher */
        width: 130px;
        border: 1px solid #d1d1d1;
        border-radius: 5px;
        padding: 10px;
        text-align: center;
        background-color: #ffffff;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .status-bar {
        height: 10px;
        border-radius: 3px;
        margin-top: 8px;
    }
    .bloco-header {
        background-color: #2c3e50;
        color: white;
        padding: 8px 15px;
        border-radius: 5px;
        margin-top: 30px;
    }
    .unidade-header {
        color: #2980b9;
        font-weight: bold;
        padding: 5px 0px;
        border-bottom: 2px solid #eee;
        margin-top: 15px;
    }
    /* Estilo da barra de rolagem para Chrome/Edge/Safari */
    .scroll-container::-webkit-scrollbar {
        height: 8px;
    }
    .scroll-container::-webkit-scrollbar-thumb {
        background: #bdc3c7;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 Painel Operacional de Leitos (Visão Contínua)")

df = carregar_dados()

if df is not None:
    cores = {
        'VERDE': '#2ecc71',
        'AMARELO': '#f1c40f',
        'VERMELHO': '#e74c3c',
        'CINZA': '#bdc3c7'
    }

    for bloco, g_bloco in df.groupby('BLOCO', sort=False):
        st.markdown(f"<div class='bloco-header'><b>BLOCO {bloco}</b></div>", unsafe_allow_html=True)
        
        for unidade, g_unidade in g_bloco.groupby('UNIDADE', sort=False):
            st.markdown(f"<div class='unidade-header'>➔ UNIDADE: {unidade}</div>", unsafe_allow_html=True)
            
            for especialidade, g_esp in g_unidade.groupby('ESPECIALIDADE', sort=False):
                st.write(f"**{especialidade}**")
                
                # Início da div de scroll
                cards_html = "<div class='scroll-container'>"
                
                for _, row in g_esp.iterrows():
                    cor_status = cores.get(row['STATUS'], cores['CINZA'])
                    cards_html += f"""
                        <div class="leito-card">
                            <div style="font-size: 14px; font-weight: bold;">{row['PARA']}</div>
                            <div style="font-size: 11px; color: #666; height: 30px; display: flex; align-items: center; justify-content: center;">{row['TIPO']}</div>
                            <div class="status-bar" style="background-color: {cor_status};"></div>
                        </div>
                    """
                
                cards_html += "</div>" # Fecha a div de scroll
                st.markdown(cards_html, unsafe_allow_html=True)
                st.divider()
else:
    st.info("Aguardando conexão com os dados...")
