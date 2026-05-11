import pandas as pd
import streamlit as st
import requests
from io import StringIO
import streamlit.components.v1 as components

st.set_page_config(page_title="Painel Mosaico de Leitos", layout="wide")

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

# --- CSS MINIMALISTA (MOSAICO COMPACTO) ---
CSS_MINIMALISTA = """
<style>
    body { font-family: 'Inter', sans-serif; background-color: white; margin: 0; }
    .mosaico-container {
        display: flex !important;
        flex-wrap: wrap !important; /* Faz os leitos "quebrarem" para a linha de baixo se faltar espaço */
        gap: 6px !important;
        padding: 5px 0px !important;
    }
    .leito-micro-card {
        flex: 0 1 auto !important;
        width: 85px !important; /* Tamanho reduzido para caber tudo */
        border: 1px solid #f0f0f0 !important;
        border-radius: 4px !important;
        padding: 6px 2px !important;
        text-align: center !important;
        background-color: #fff !important;
    }
    .status-dot {
        height: 6px !important;
        width: 80% !important;
        margin: 4px auto 0 auto !important;
        border-radius: 2px !important;
    }
    .nome-leito { font-size: 11px !important; font-weight: 700 !important; color: #333; }
    .tipo-leito { font-size: 8px !important; color: #999; text-transform: uppercase; overflow: hidden; white-space: nowrap; }
    
    .secao-titulo { font-size: 14px; font-weight: bold; color: #555; margin-top: 15px; border-left: 3px solid #ddd; padding-left: 8px; }
</style>
"""

df = carregar_dados()

if df is not None:
    # Sidebar minimalista
    st.sidebar.caption("Filtros Rápidos")
    bloco_filtro = st.sidebar.multiselect("Blocos", sorted(df['BLOCO'].unique()), default=sorted(df['BLOCO'].unique()))
    df = df[df['BLOCO'].isin(bloco_filtro)]

    st.title("🏥 Mapa Geral de Leitos")
    
    # Cores flat modernas
    cores = {'VERDE': '#27ae60', 'AMARELO': '#f1c40f', 'VERMELHO': '#e74c3c', 'CINZA': '#dcdde1'}

    # Exibição compacta
    for unidade, g_unidade in df.groupby('UNIDADE', sort=False):
        st.markdown(f"<div class='secao-titulo'>{unidade}</div>", unsafe_allow_html=True)
        
        # Gerando o HTML de todos os leitos da unidade de uma vez
        html_mosaico = f"{CSS_MINIMALISTA}<div class='mosaico-container'>"
        
        for _, row in g_unidade.iterrows():
            cor = cores.get(row['STATUS'], cores['CINZA'])
            html_mosaico += f'''
                <div class="leito-micro-card">
                    <div class="nome-leito">{row['PARA']}</div>
                    <div class="tipo-leito">{row['TIPO']}</div>
                    <div class="status-dot" style="background-color: {cor};"></div>
                </div>
            '''
        html_mosaico += "</div>"
        
        # Ajuste de altura automática conforme a quantidade de leitos
        altura_estimada = (len(g_unidade) // 10 + 1) * 65 
        components.html(html_mosaico, height=max(altura_estimada, 70))

else:
    st.error("Planilha não encontrada ou sem acesso.")
