import pandas as pd
import streamlit as st
import requests
from io import StringIO
import streamlit.components.v1 as components

# Configuração da página para modo tela cheia
st.set_page_config(page_title="Mapa Geral de Leitos", layout="wide")

def carregar_dados():
    SHEET_ID = "1N0zcHuMz2gmilXlu8bKujkwDggPnTxg8fVp90eWEUw4"
    URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
    try:
        response = requests.get(URL)
        response.raise_for_status()
        # Corrige o encoding do símbolo 'º'
        conteudo = response.text.replace('Âº', 'º').replace('âº', 'º')
        df_raw = pd.read_csv(StringIO(conteudo))
        
        # Mapeamento fixo das colunas: A=0, B=1, C=2, F=5, J=9, V=21
        df_final = pd.DataFrame()
        df_final['BLOCO'] = df_raw.iloc[:, 0].astype(str)
        df_final['UNIDADE'] = df_raw.iloc[:, 1].astype(str)
        df_final['ESPECIALIDADE'] = df_raw.iloc[:, 2].astype(str)
        df_final['PARA'] = df_raw.iloc[:, 5].astype(str)
        df_final['TIPO'] = df_raw.iloc[:, 9].astype(str)
        
        # Status na Coluna V. Se vazia, fica Cinza.
        if df_raw.shape[1] >= 22: 
            df_final['STATUS'] = df_raw.iloc[:, 21].fillna('CINZA').astype(str).str.upper().str.strip()
        else:
            df_final['STATUS'] = 'CINZA'

        df_final = df_final.map(lambda x: x.strip() if isinstance(x, str) else x)
        return df_final
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None

# --- CSS ULTRA MINIMALISTA ---
CSS_MOSAICO = """
<style>
    body { font-family: 'Segoe UI', Tahoma, sans-serif; background-color: #ffffff; margin: 0; }
    .mosaico-wrapper {
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 8px !important;
        padding: 10px 0px !important;
    }
    .card-leito {
        flex: 0 1 auto !important;
        width: 90px !important;
        border: 1px solid #eeeeee !important;
        border-radius: 4px !important;
        padding: 8px 4px !important;
        text-align: center !important;
        background-color: #ffffff !important;
    }
    .txt-leito { font-size: 12px !important; font-weight: bold; color: #333; margin-bottom: 2px; }
    .txt-tipo { font-size: 9px !important; color: #888; text-transform: uppercase; white-space: nowrap; overflow: hidden; }
    .barra-cor {
        height: 6px !important;
        width: 100% !important;
        margin-top: 6px !important;
        border-radius: 0px 0px 3px 3px !important;
    }
    .header-unidade { 
        font-size: 16px; 
        font-weight: bold; 
        color: #444; 
        margin-top: 20px; 
        border-bottom: 1px solid #eee;
        padding-bottom: 5px;
    }
</style>
"""

df = carregar_dados()

if df is not None:
    st.title("🏥 Mapa Geral de Leitos")
    
    # Cores flat
    cores_map = {
        'VERDE': '#27ae60', 
        'AMARELO': '#f1c40f', 
        'VERMELHO': '#e74c3c', 
        'CINZA': '#d1d8e0'
    }

    # Agrupa por Bloco e Unidade para organizar a tela
    for (bloco, unidade), g_unidade in df.groupby(['BLOCO', 'UNIDADE'], sort=False):
        st.markdown(f"<div class='header-unidade'>Bloco {bloco} - {unidade}</div>", unsafe_allow_html=True)
        
        # Monta o HTML do bloco de leitos
        html_cards = f"{CSS_MOSAICO}<div class='mosaico-wrapper'>"
        
        for _, row in g_unidade.iterrows():
            cor = cores_map.get(row['STATUS'], cores_map['CINZA'])
            html_cards += f'''
                <div class="card-leito">
                    <div class="txt-leito">{row['PARA']}</div>
                    <div class="txt-tipo">{row['TIPO']}</div>
                    <div class="barra-cor" style="background-color: {cor};"></div>
                </div>
            '''
        html_cards += "</div>"
        
        # Calcula a altura do componente baseado na quantidade de leitos (mosaico)
        # Aproximadamente 12 leitos por linha em resoluções padrão
        linhas = (len(g_unidade) // 12) + 1
        altura = linhas * 85
        
        components.html(html_cards, height=altura, scrolling=False)
else:
    st.info("Conecte a planilha para visualizar o mapa.")
