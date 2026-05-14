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

df = carregar_dados()

if df is not None:
    st.title("🏥 Painel de Monitoramento dos Leitos")

    cores = {'VERDE': '#22c55e', 'AMARELO': '#eab308', 'VERMELHO': '#ef4444', 'CINZA': '#cbd5e1', 'PRETO': '#1c1c1c'}

    # CSS unificado (Tela + Impressão)
    html_style = """
    <style>
        body { font-family: sans-serif; margin: 0; background: white; padding-top: 50px; }
        .btn-print {
            position: fixed; top: 10px; right: 20px; z-index: 1000;
            padding: 10px 20px; background: #1e293b; color: white;
            border: none; border-radius: 6px; cursor: pointer; font-weight: bold;
        }
        .container-geral { display: inline-block; min-width: 100%; }
        .linha { display: flex; flex-wrap: nowrap; border-bottom: 1px solid #edf2f7; background: white; width: 100%; }
        .coluna-fixa { 
            position: sticky; left: 0; z-index: 100; 
            min-width: 250px; background: white; padding: 10px;
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
        .stats-container { margin-top: 8px; display: flex; flex-wrap: wrap; gap: 4px; }
        .stat-item { font-size: 10px; font-weight: bold; padding: 1px 4px; border-radius: 3px; color: white; }
        
        @media print {
            .btn-print { display: none !important; }
            body { padding-top: 0; zoom: 85%; }
            .coluna-fixa { position: relative !important; left: 0 !important; box-shadow: none !important; border-right: 1px solid #ddd !important; }
            .linha { display: flex !important; page-break-inside: avoid !important; }
            @page { size: landscape; margin: 1cm; }
        }
    </style>
    """

    # Script de Impressão simplificado
    js_script = """
    <script>
        function imprimir() {
            window.print();
        }
    </script>
    """

    # Construção do conteúdo HTML
    html_corpo = f"<button class='btn-print' onclick='imprimir()'>🖨️ Imprimir Painel</button>"
    html_corpo += "<div class='container-geral'>"
    
    for (unidade, especialidade), g_esp in df.groupby(['UNIDADE', 'ESPECIALIDADE'], sort=False):
        total_linha = len(g_esp)
        contagem_linha = g_esp['STATUS'].value_counts()
        
        stats = "".join([
            f"<span class='stat-item' style='background-color:{cores[s]}; color:{'black' if s in ['AMARELO','CINZA'] else 'white'};'>"
            f"{contagem_linha.get(s,0)} ({(contagem_linha.get(s,0)/total_linha)*100:.0f}%)</span>" 
            for s in cores if contagem_linha.get(s,0) > 0
        ])

        html_corpo += f"<div class='linha'><div class='coluna-fixa'><b>{unidade}</b><br><small style='color:gray'>{especialidade}</small><div class='stats-container'>{stats}</div></div>"
        html_corpo += "<div class='wrapper-cards'>"
        for _, row in g_esp.iterrows():
            html_corpo += f"<div class='card'><div class='leito'>{row['PARA']}</div><div class='tipo'>{row['TIPO']}</div><div class='status-bar' style='background-color: {cores.get(row['STATUS'], '#cbd5e1')};'></div></div>"
        html_corpo += "</div></div>"

    # TOTAL GERAL
    total_g = len(df)
    cont_g = df['STATUS'].value_counts()
    stats_g = "".join([
        f"<span class='stat-item' style='background-color:{cores[s]}; color:{'black' if s in ['AMARELO','CINZA'] else 'white'};'>"
        f"{cont_g.get(s,0)} ({(cont_g.get(s,0)/total_g)*100:.0f}%)</span>" 
        for s in cores if cont_g.get(s,0) > 0
    ])
    
    html_corpo += f"<div class='linha'><div class='coluna-fixa'><b>TOTAL GERAL</b><br><small>Total: {total_g}</small><div class='stats-container'>{stats_g}</div></div><div class='wrapper-cards'></div></div></div>"

    # Renderização Final
    html_final = f"<html><head>{html_style}{js_script}</head><body>{html_corpo}</body></html>"
    total_linhas = len(df.groupby(['UNIDADE', 'ESPECIALIDADE'])) + 1
    
    components.html(html_final, height=max(total_linhas * 115, 800), scrolling=True)

else:
    st.error("Erro ao carregar dados.")
