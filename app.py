import pandas as pd
import streamlit as st
import requests
from io import StringIO
import streamlit.components.v1 as components

st.set_page_config(page_title="Painel de Leitos", layout="wide")

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

# --- CSS BASE ---
CSS_ESTILO = """
<style>
    body { font-family: sans-serif; margin: 0; padding: 0; background-color: #f9f9f9; }
    .scroll-container {
        display: flex !important;
        flex-direction: row !important;
        overflow-x: auto !important;
        white-space: nowrap !important;
        padding: 10px !important;
        gap: 15px !important;
    }
    .leito-card {
        flex: 0 0 auto !important;
        width: 140px !important;
        background: white !important;
        border: 1px solid #ddd !important;
        border-radius: 8px !important;
        padding: 15px !important;
        text-align: center !important;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1) !important;
        display: inline-block !important;
    }
    .status-bar {
        height: 12px !important;
        border-radius: 4px !important;
        margin-top: 10px !important;
    }
    /* Scrollbar */
    .scroll-container::-webkit-scrollbar { height: 8px; }
    .scroll-container::-webkit-scrollbar-thumb { background: #ccc; border-radius: 10px; }
</style>
"""

st.title("🏥 Painel de Monitoramento de Leitos")

df = carregar_dados()

if df is not None:
    cores = {
        'VERDE': '#2ecc71',
        'AMARELO': '#f1c40f',
        'VERMELHO': '#e74c3c',
        'CINZA': '#bdc3c7'
    }

    for bloco, g_bloco in df.groupby('BLOCO', sort=False):
        st.subheader(f"🏢 BLOCO {bloco}")
        
        for unidade, g_unidade in g_bloco.groupby('UNIDADE', sort=False):
            st.info(f"📍 UNIDADE: {unidade}")
            
            for especialidade, g_esp in g_unidade.groupby('ESPECIALIDADE', sort=False):
                st.write(f"**{especialidade}**")
                
                # Montando o HTML dos cards para esta linha específica
                html_cards = f"{CSS_ESTILO}<div class='scroll-container'>"
                
                for _, row in g_esp.iterrows():
                    cor_status = cores.get(row['STATUS'], cores['CINZA'])
                    html_cards += f'''
                        <div class="leito-card">
                            <div style="font-size: 18px; font-weight: bold;">{row['PARA']}</div>
                            <div style="font-size: 11px; color: #666; margin-top: 5px;">{row['TIPO']}</div>
                            <div class="status-bar" style="background-color: {cor_status};"></div>
                        </div>
                    '''
                html_cards += "</div>"
                
                # USANDO COMPONENTS PARA FORÇAR A RENDERIZAÇÃO
                components.html(html_cards, height=130, scrolling=True)
                st.write("---")
else:
    st.warning("Verifique a conexão com a planilha.")
