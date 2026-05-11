import pandas as pd
import streamlit as st
import requests
from io import StringIO
import streamlit.components.v1 as components

# 1. Configuração da página
st.set_page_config(page_title="Gestão de Leitos", layout="wide")

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
        return None

# 2. Construção do HTML e CSS
df = carregar_dados()

if df is not None:
    st.title("🏥 Painel de Monitoramento")

    cores = {'VERDE': '#22c55e', 'AMARELO': '#eab308', 'VERMELHO': '#ef4444', 'CINZA': '#cbd5e1'}

    # CSS para garantir o sticky e o scroll lateral
    html_style = """
    <style>
        body { font-family: sans-serif; margin: 0; background: white; }
        .container-geral { display: inline-block; min-width: 100%; }
        .linha { display: flex; flex-wrap: nowrap; border-bottom: 1px solid #edf2f7; background: white; }
        .coluna-fixa { 
            position: sticky; left: 0; z-index: 100; 
            min-width: 200px; background: white; padding: 10px;
            border-right: 2px solid #edf2f7; box-shadow: 2px 0 5px rgba(0,0,0,0.05);
        }
        .wrapper-cards { display: flex; flex-wrap: nowrap; gap: 8px; padding: 10px; }
        .card { 
            flex: 0 0 100px; width: 100px; border: 1px solid #e2e8f0; 
            border-radius: 6px; padding: 10px 5px; text-align: center; background: white;
        }
        .leito { font-size: 14px; font-weight: bold; }
        .tipo { font-size: 9px; color: #94a3b8; text-transform: uppercase; margin-top: 2px; }
        .status { height: 6px; border-radius: 3px; margin-top: 8px; width: 80%; margin-left: 10%; }
    </style>
    """

    html_corpo = "<div class='container-geral'>"
    for (unidade, especialidade), g_esp in df.groupby(['UNIDADE', 'ESPECIALIDADE'], sort=False):
        html_corpo += f"<div class='linha'>"
        html_corpo += f"<div class='coluna-fixa'><b>{unidade}</b><br><small style='color:gray'>{especialidade}</small></div>"
        html_corpo += "<div class='wrapper-cards'>"
        for _, row in g_esp.iterrows():
            cor = cores.get(row['STATUS'], cores['CINZA'])
            html_corpo += f"""
                <div class='card'>
                    <div class='leito'>{row['PARA']}</div>
                    <div class='tipo'>{row['TIPO']}</div>
                    <div class='status' style='background-color: {cor};'></div>
                </div>
            """
        html_corpo += "</div></div>"
    html_corpo += "</div>"

    # Junta tudo e renderiza via IFRAME (Garante que o HTML funcione)
    html_final = f"<html><head>{html_style}</head><body>{html_corpo}</body></html>"
    
    # Altura dinâmica baseada na quantidade de linhas
    altura_box = len(df.groupby(['UNIDADE', 'ESPECIALIDADE'])) * 90
    components.html(html_final, height=max(altura_box, 800), scrolling=True)

else:
    st.error("Erro ao carregar dados.")
