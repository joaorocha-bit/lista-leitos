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
        df_final['UNIDADE'] = df_raw.iloc[:, 1].astype(str).str.strip()
        df_final['ESPECIALIDADE'] = df_raw.iloc[:, 2].astype(str)
        df_final['PARA'] = df_raw.iloc[:, 5].astype(str)
        df_final['TIPO'] = df_raw.iloc[:, 9].astype(str)
        
        if df_raw.shape[1] >= 22: 
            df_final['STATUS'] = df_raw.iloc[:, 21].fillna('CINZA').astype(str).str.upper().str.strip()
        else:
            df_final['STATUS'] = 'CINZA'

        df_final = df_final.map(lambda x: x.strip() if isinstance(x, str) else x)

        ordem_unidades = [
            "A1", "A2", "B1", "B2", "C1", "C2", "D1", "D2", "D3", "E1", "E3", 
            "F3 (UNIQUE)", "G3", "5º B", "9º MATERNO", "10º MATERNO", 
            "CTIA 1º", "CTIA A1", "CTIA A2", "CTIA A3", "CTIA 3A", 
            "CTIA 5A", "CTIA 4A", "UTI PED", "UTI NEO"
        ]
        
        df_final['UNIDADE'] = pd.Categorical(df_final['UNIDADE'], categories=ordem_unidades, ordered=True)
        df_final = df_final.sort_values(by='UNIDADE')
        
        return df_final
    except Exception as e:
        return None

# 2. Construção do HTML e CSS
df = carregar_dados()

if df is not None:
    st.title("🏥 Painel de Monitoramento dos Leitos")

    cores = {'VERDE': '#22c55e', 'AMARELO': '#eab308', 'VERMELHO': '#ef4444', 'CINZA': '#cbd5e1', 'PRETO': '#1c1c1c'}

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
        .status-bar { height: 6px; border-radius: 3px; margin-top: 8px; width: 80%; margin-left: 10%; }
        
        /* Estilo para as estatísticas */
        .stats-container { margin-top: 8px; display: flex; flex-wrap: wrap; gap: 4px; }
        .stat-item { font-size: 10px; font-weight: bold; padding: 1px 4px; border-radius: 3px; color: white; }
    </style>
    """

    html_corpo = "<div class='container-geral'>"
    for (unidade, especialidade), g_esp in df.groupby(['UNIDADE', 'ESPECIALIDADE'], sort=False):
        
        # Cálculo das estatísticas da linha
        total = len(g_esp)
        contagem = g_esp['STATUS'].value_counts()
        
        html_stats = "<div class='stats-container'>"
        for status_nome, cor_hex in cores.items():
            qtd = contagem.get(status_nome, 0)
            if qtd > 0:
                porcentagem = (qtd / total) * 100
                # Ajuste de cor do texto para o Amarelo e Cinza para melhor leitura
                texto_cor = "black" if status_nome in ['AMARELO', 'CINZA'] else "white"
                html_stats += f"<span class='stat-item' style='background-color:{cor_hex}; color:{texto_cor};'>{qtd} ({porcentagem:.0f}%)</span>"
        html_stats += "</div>"

        html_corpo += f"<div class='linha'>"
        html_corpo += f"""
            <div class='coluna-fixa'>
                <b>{unidade}</b><br>
                <small style='color:gray'>{especialidade}</small>
                {html_stats}
            </div>"""
        
        html_corpo += "<div class='wrapper-cards'>"
        for _, row in g_esp.iterrows():
            cor = cores.get(row['STATUS'], cores['CINZA'])
            html_corpo += f"""
                <div class='card'>
                    <div class='leito'>{row['PARA']}</div>
                    <div class='tipo'>{row['TIPO']}</div>
                    <div class='status-bar' style='background-color: {cor};'></div>
                </div>
            """
        html_corpo += "</div></div>"
    html_corpo += "</div>"

    html_final = f"<html><head>{html_style}</head><body>{html_corpo}</body></html>"
    
    total_linhas = len(df.groupby(['UNIDADE', 'ESPECIALIDADE']))
    # Aumentei um pouco a altura por linha (de 90 para 110) para acomodar os novos dados
    altura_box = total_linhas * 110
    components.html(html_final, height=max(altura_box, 800), scrolling=True)

else:
    st.error("Erro ao carregar dados.")
