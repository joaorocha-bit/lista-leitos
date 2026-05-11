import pandas as pd
import streamlit as st
import requests
from io import StringIO

# Configuração da página - layout wide é essencial aqui
st.set_page_config(page_title="Painel de Leitos Integrado", layout="wide")

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

# --- CSS PARA SCROLL LATERAL NA PÁGINA TODA ---
st.markdown("""
    <style>
    /* Força o container principal do Streamlit a permitir scroll horizontal */
    .main .block-container {
        overflow-x: auto !important;
    }
    
    /* Container que abraça todas as linhas e impede quebra */
    .painel-horizontal {
        display: inline-block; /* Faz o container esticar conforme o conteúdo */
        min-width: 100%;
        white-space: nowrap; 
        padding-bottom: 20px;
    }

    .linha-unidade {
        display: flex;
        flex-direction: row;
        margin-bottom: 15px;
        align-items: center;
    }

    .info-secao {
        width: 250px; /* Largura fixa para os nomes das unidades não sumirem */
        position: sticky;
        left: 0;
        background: white;
        z-index: 10;
        padding-right: 15px;
        font-weight: bold;
        font-size: 14px;
        color: #334155;
        border-right: 2px solid #f1f5f9;
    }

    .cards-container {
        display: flex;
        gap: 8px;
        padding-left: 10px;
    }

    .leito-card {
        flex: 0 0 auto;
        width: 100px; /* TAMANHO PADRÃO QUE VOCÊ PEDIU */
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 8px 4px;
        text-align: center;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.05);
    }

    .txt-num { font-size: 13px; font-weight: bold; color: #1e293b; }
    .txt-tipo { font-size: 9px; color: #94a3b8; text-transform: uppercase; }
    .status-bar { height: 8px; border-radius: 2px; margin-top: 6px; }
    </style>
    """, unsafe_allow_html=True)

df = carregar_dados()

if df is not None:
    st.title("🏥 Gestão de Leitos Hospitalares")
    
    cores = {'VERDE': '#22c55e', 'AMARELO': '#eab308', 'VERMELHO': '#ef4444', 'CINZA': '#94a3b8'}

    # Início do Painel Horizontal Único
    html_painel = "<div class='painel-horizontal'>"

    for (unidade, especialidade), g_esp in df.groupby(['UNIDADE', 'ESPECIALIDADE'], sort=False):
        # Cada par Unidade/Especialidade é uma linha
        html_painel += f"<div class='linha-unidade'>"
        
        # Título da Seção (Fica "grudado" na esquerda ao dar scroll)
        html_painel += f"<div class='info-secao'>{unidade}<br><small style='color:gray'>{especialidade}</small></div>"
        
        # Container de cards desta linha
        html_painel += "<div class='cards-container'>"
        for _, row in g_esp.iterrows():
            cor = cores.get(row['STATUS'], cores['CINZA'])
            html_painel += f'''
                <div class="leito-card">
                    <div class="txt-num">{row['PARA']}</div>
                    <div class="txt-tipo">{row['TIPO']}</div>
                    <div class="status-bar" style="background-color: {cor};"></div>
                </div>
            '''
        html_painel += "</div></div>" # Fecha cards-container e linha-unidade

    html_painel += "</div>" # Fecha painel-horizontal
    
    # Renderiza tudo em um único bloco de Markdown/HTML
    st.markdown(html_painel, unsafe_allow_html=True)

else:
    st.error("Erro ao carregar a planilha.")
