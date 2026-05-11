import pandas as pd
import streamlit as st
import requests
from io import StringIO

# Configuração da página
st.set_page_config(page_title="Painel de Leitos", layout="wide")

def carregar_dados():
    SHEET_ID = "1N0zcHuMz2gmilXlu8bKujkwDggPnTxg8fVp90eWEUw4"
    URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
    try:
        response = requests.get(URL)
        response.raise_for_status()
        # Limpeza do caractere Â diretamente no texto bruto
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

# --- CSS PARA O LAYOUT DE TRILHA HORIZONTAL ---
st.markdown("""
    <style>
    /* Container que permite o scroll lateral */
    .scroll-container {
        display: flex !important;
        flex-direction: row !important;
        overflow-x: auto !important;
        white-space: nowrap !important;
        padding: 15px 5px !important;
        gap: 15px !important;
        background-color: #fcfcfc;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    /* Card individual */
    .leito-card {
        flex: 0 0 auto !important;
        width: 140px !important;
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 6px;
        padding: 12px;
        text-align: center;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.05);
        display: inline-block;
    }
    .status-bar {
        height: 12px;
        border-radius: 4px;
        margin-top: 10px;
    }
    .bloco-header {
        background-color: #1e293b;
        color: white;
        padding: 10px 15px;
        border-radius: 4px;
        margin-top: 25px;
        font-family: sans-serif;
    }
    .unidade-header {
        color: #0284c7;
        font-weight: bold;
        font-size: 18px;
        margin-top: 15px;
        font-family: sans-serif;
    }
    /* Estilo da barra de scroll */
    .scroll-container::-webkit-scrollbar { height: 10px; }
    .scroll-container::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 Painel Operacional de Leitos")

df = carregar_dados()

if df is not None:
    cores = {
        'VERDE': '#22c55e',
        'AMARELO': '#eab308',
        'VERMELHO': '#ef4444',
        'CINZA': '#94a3b8'
    }

    # Agrupamento para gerar a visualização
    for bloco, g_bloco in df.groupby('BLOCO', sort=False):
        st.markdown(f"<div class='bloco-header'>BLOCO {bloco}</div>", unsafe_allow_html=True)
        
        for unidade, g_unidade in g_bloco.groupby('UNIDADE', sort=False):
            st.markdown(f"<div class='unidade-header'>➔ {unidade}</div>", unsafe_allow_html=True)
            
            for especialidade, g_esp in g_unidade.groupby('ESPECIALIDADE', sort=False):
                st.write(f"**{especialidade}**")
                
                # CRIANDO A STRING DO HTML DOS CARDS
                html_final = "<div class='scroll-container'>"
                
                for _, row in g_esp.iterrows():
                    cor_status = cores.get(row['STATUS'], cores['CINZA'])
                    html_final += f'''
                        <div class="leito-card">
                            <div style="font-size: 16px; font-weight: bold; color: #334155;">{row['PARA']}</div>
                            <div style="font-size: 12px; color: #64748b; margin-top: 4px; min-height: 20px;">{row['TIPO']}</div>
                            <div class="status-bar" style="background-color: {cor_status};"></div>
                        </div>
                    '''
                
                html_final += "</div>"
                
                # O SEGREDO: Usar st.markdown com unsafe_allow_html=True para a variável html_final
                st.markdown(html_final, unsafe_allow_html=True)
                
else:
    st.warning("Não foi possível carregar os dados. Verifique a planilha.")
