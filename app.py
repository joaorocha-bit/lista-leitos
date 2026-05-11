import pandas as pd
import streamlit as st
import requests
from io import StringIO

# 1. Configuração da página
st.set_page_config(page_title="Painel de Leitos Hospitalar", layout="wide")

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

# 2. CSS GLOBAL (Força o scroll na página toda e fixa o tamanho dos cards)
st.markdown("""
    <style>
    /* Remove as margens padrão do Streamlit para dar espaço ao scroll */
    .main .block-container {
        max-width: none !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        overflow-x: auto !important;
    }

    /* Estilo da Linha (não deixa quebrar) */
    .linha-painel {
        display: flex !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        margin-bottom: 12px !important;
        width: max-content !important; /* Estica a linha conforme o número de cards */
    }

    /* Nome da Unidade fixo à esquerda */
    .label-unidade {
        width: 220px !important;
        min-width: 220px !important;
        font-weight: bold;
        font-size: 14px;
        color: #1e293b;
        background: white;
        position: sticky;
        left: 0;
        z-index: 99;
        border-right: 2px solid #f1f5f9;
        padding-right: 10px;
    }

    /* Container dos Cards */
    .cards-wrapper {
        display: flex !important;
        gap: 8px !important;
        padding-left: 15px !important;
    }

    /* O Card em si */
    .card-hospitalar {
        flex: 0 0 100px !important; /* LARGURA PADRÃO FIXA */
        width: 100px !important;
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 10px 5px;
        text-align: center;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.05);
    }

    .num-leito { font-size: 14px; font-weight: bold; color: #334155; }
    .tipo-leito { font-size: 9px; color: #94a3b8; text-transform: uppercase; margin-top: 2px; }
    .status-indicador { height: 8px; border-radius: 4px; margin-top: 8px; }
    </style>
    """, unsafe_allow_html=True)

# 3. Execução do Painel
df = carregar_dados()

if df is not None:
    st.title("🏥 Gestão Centralizada de Leitos")
    
    cores = {'VERDE': '#22c55e', 'AMARELO': '#eab308', 'VERMELHO': '#ef4444', 'CINZA': '#94a3b8'}

    # Agrupamento
    for (unidade, especialidade), g_esp in df.groupby(['UNIDADE', 'ESPECIALIDADE'], sort=False):
        
        # Início da linha HTML
        html_linha = f"<div class='linha-painel'>"
        
        # Texto da Unidade
        html_linha += f"<div class='label-unidade'>{unidade}<br><small style='color:#64748b'>{especialidade}</small></div>"
        
        # Container de Cards
        html_linha += "<div class='cards-wrapper'>"
        for _, row in g_esp.iterrows():
            cor = cores.get(row['STATUS'], cores['CINZA'])
            html_linha += f'''
                <div class="card-hospitalar">
                    <div class="num-leito">{row['PARA']}</div>
                    <div class="tipo-leito">{row['TIPO']}</div>
                    <div class="status-indicador" style="background-color: {cor};"></div>
                </div>
            '''
        html_linha += "</div></div>" # Fecha wrapper e linha
        
        # Renderiza a linha na tela
        st.markdown(html_linha, unsafe_allow_html=True)

else:
    st.warning("Verifique a conexão com a planilha do Google.")
