import pandas as pd
import streamlit as st
import requests
from io import StringIO
import streamlit.components.v1 as components

st.set_page_config(page_title="Mapa Geral de Leitos", layout="wide")

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

# --- CSS PARA FORÇAR TODOS NA MESMA LINHA (SEM SCROLL) ---
CSS_LINHA_TOTAL = """
<style>
    body { font-family: sans-serif; background-color: white; margin: 0; overflow: hidden; }
    .linha-leitos {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important; /* Proíbe quebra de linha */
        width: 100% !important;
        gap: 2px !important; /* Espaço mínimo entre leitos */
        align-items: stretch !important;
    }
    .leito-unidade {
        flex: 1 1 0px !important; /* Força todos a terem o mesmo tamanho e encolherem o necessário */
        min-width: 0 !important;   /* Permite que o card encolha além do conteúdo */
        border: 1px solid #f0f0f0 !important;
        text-align: center !important;
        padding: 4px 1px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
    }
    .txt-num { 
        font-size: 10px !important; 
        font-weight: bold; 
        overflow: hidden; 
        text-overflow: ellipsis; 
    }
    .txt-sub { 
        font-size: 7px !important; 
        color: #999; 
        white-space: nowrap; 
        overflow: hidden; 
    }
    .faixa-status {
        height: 5px !important;
        width: 100% !important;
        margin-top: 3px !important;
    }
</style>
"""

df = carregar_dados()

if df is not None:
    st.title("🏥 Mapa Geral em Linha Única")
    
    cores_css = {
        'VERDE': '#2ecc71', 
        'AMARELO': '#f1c40f', 
        'VERMELHO': '#e74c3c', 
        'CINZA': '#dcdde1'
    }

    # Agrupa por Unidade para criar uma linha por unidade
    for unidade, g_unidade in df.groupby('UNIDADE', sort=False):
        st.caption(f"📍 **{unidade}** ({len(g_unidade)} leitos)")
        
        # HTML da linha
        html_linha = f"{CSS_LINHA_TOTAL}<div class='linha-leitos'>"
        
        for _, row in g_unidade.iterrows():
            cor = cores_css.get(row['STATUS'], cores_css['CINZA'])
            html_linha += f'''
                <div class="leito-unidade">
                    <div class="txt-num">{row['PARA']}</div>
                    <div class="txt-sub">{row['TIPO'][:3]}</div>
                    <div class="faixa-status" style="background-color: {cor};"></div>
                </div>
            '''
        html_linha += "</div>"
        
        # Renderiza a linha. Altura pequena para ficar minimalista.
        components.html(html_linha, height=55)
else:
    st.info("Aguardando dados da planilha...")
