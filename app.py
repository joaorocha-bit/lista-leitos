import pandas as pd
import streamlit as st
import requests
from io import StringIO
import streamlit.components.v1 as components

st.set_page_config(page_title="Mapa de Leitos Horizontal", layout="wide")

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

# --- CSS PARA TRILHA ÚNICA (SEM QUEBRA) ---
CSS_TRILHA = """
<style>
    body { font-family: 'Segoe UI', sans-serif; background-color: #fff; margin: 0; }
    .trilha-container {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important; /* FORÇA A LINHA ÚNICA */
        overflow-x: auto !important;   /* ATIVA SCROLL LATERAL */
        gap: 6px !important;
        padding: 5px 0px 15px 0px !important;
    }
    .card-mini {
        flex: 0 0 auto !important; /* IMPEDE O CARD DE ENCOLHER */
        width: 80px !important;
        border: 1px solid #eee !important;
        border-radius: 4px !important;
        padding: 6px 2px !important;
        text-align: center !important;
        background-color: #fff !important;
    }
    .txt-leito { font-size: 11px !important; font-weight: bold; color: #333; }
    .txt-tipo { font-size: 8px !important; color: #aaa; text-transform: uppercase; overflow: hidden; white-space: nowrap; }
    .barra-status {
        height: 6px !important;
        width: 100% !important;
        margin-top: 4px !important;
        border-radius: 2px !important;
    }
    /* Estilo da barra de rolagem */
    .trilha-container::-webkit-scrollbar { height: 4px; }
    .trilha-container::-webkit-scrollbar-thumb { background: #e0e0e0; border-radius: 10px; }
</style>
"""

df = carregar_dados()

if df is not None:
    st.title("🏥 Mapa Operacional (Visão em Linha)")
    
    cores_dict = {
        'VERDE': '#2ecc71', 
        'AMARELO': '#f1c40f', 
        'VERMELHO': '#e74c3c', 
        'CINZA': '#dcdde1'
    }

    # Agrupamento por Unidade e Especialidade
    for (unidade, especialidade), g_esp in df.groupby(['UNIDADE', 'ESPECIALIDADE'], sort=False):
        st.markdown(f"**{unidade}** <small>({especialidade})</small>", unsafe_allow_html=True)
        
        # Gerando o HTML da trilha horizontal
        html_trilha = f"{CSS_TRILHA}<div class='trilha-container'>"
        
        for _, row in g_esp.iterrows():
            cor = cores_dict.get(row['STATUS'], cores_dict['CINZA'])
            html_trilha += f'''
                <div class="card-mini">
                    <div class="txt-leito">{row['PARA']}</div>
                    <div class="txt-tipo">{row['TIPO']}</div>
                    <div class="barra-status" style="background-color: {cor};"></div>
                </div>
            '''
        html_trilha += "</div>"
        
        # Como é apenas uma linha, a altura pode ser pequena e fixa
        components.html(html_trilha, height=85)
        st.markdown("<hr style='margin:0; border-top:1px solid #f9f9f9'>", unsafe_allow_html=True)

else:
    st.info("Carregando dados da planilha...")
