import pandas as pd
import streamlit as st
import requests
from io import StringIO
import streamlit.components.v1 as components

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

# 2. CSS que será injetado dentro do componente de HTML
CSS_CARDS = """
<style>
    .painel-geral {
        display: flex;
        flex-direction: column;
        font-family: sans-serif;
        gap: 15px;
    }
    .linha-unidade {
        display: flex;
        flex-direction: row;
        flex-wrap: nowrap;
        align-items: center;
    }
    .label-unidade {
        width: 200px;
        min-width: 200px;
        font-weight: bold;
        font-size: 14px;
        color: #334155;
        position: sticky;
        left: 0;
        background: white;
        z-index: 10;
        border-right: 2px solid #f1f5f9;
    }
    .cards-wrapper {
        display: flex;
        flex-direction: row;
        flex-wrap: nowrap;
        gap: 8px;
        padding-left: 10px;
    }
    .card-leito {
        flex: 0 0 100px;
        width: 100px;
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 10px 5px;
        text-align: center;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.05);
    }
    .txt-num { font-size: 14px; font-weight: bold; color: #1e293b; }
    .txt-tipo { font-size: 9px; color: #94a3b8; text-transform: uppercase; margin-top: 2px; }
    .status-bar { height: 8px; border-radius: 4px; margin-top: 8px; }
</style>
"""

df = carregar_dados()

if df is not None:
    st.title("🏥 Gestão Centralizada de Leitos")
    
    cores = {'VERDE': '#22c55e', 'AMARELO': '#eab308', 'VERMELHO': '#ef4444', 'CINZA': '#94a3b8'}

    # Montamos UMA ÚNICA STRING de HTML para o painel todo
    html_total = f"<html><head>{CSS_CARDS}</head><body><div class='painel-geral'>"

    for (unidade, especialidade), g_esp in df.groupby(['UNIDADE', 'ESPECIALIDADE'], sort=False):
        html_total += f"<div class='linha-unidade'>"
        html_total += f"<div class='label-unidade'>{unidade}<br><small style='color:gray'>{especialidade}</small></div>"
        html_total += "<div class='cards-wrapper'>"
        
        for _, row in g_esp.iterrows():
            cor = cores.get(row['STATUS'], cores['CINZA'])
            html_total += f'''
                <div class="card-leito">
                    <div class="txt-num">{row['PARA']}</div>
                    <div class="txt-tipo">{row['TIPO']}</div>
                    <div class="status-bar" style="background-color: {cor};"></div>
                </div>
            '''
        html_total += "</div></div>"

    html_total += "</div></body></html>"
    
    # O SEGREDO: Usar components.html para renderizar tudo de uma vez
    # O height pode ser ajustado conforme o número de linhas (ex: 80px por linha)
    altura_calculada = len(df.groupby(['UNIDADE', 'ESPECIALIDADE'])) * 100
    components.html(html_total, height=max(altura_calculada, 600), scrolling=True)

else:
    st.error("Erro ao carregar os dados da planilha.")
