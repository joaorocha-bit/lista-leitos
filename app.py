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
        df_final['UNIDADE'] = df_raw.iloc[:, 1].astype(str).str.strip()
        df_final['ESPECIALIDADE'] = df_raw.iloc[:, 2].astype(str)
        df_final['PARA'] = df_raw.iloc[:, 5].astype(str)
        df_final['TIPO'] = df_raw.iloc[:, 9].astype(str)
        
        if df_raw.shape[1] >= 22: 
            df_final['STATUS'] = df_raw.iloc[:, 21].fillna('CINZA').astype(str).str.upper().str.strip()
        else:
            df_final['STATUS'] = 'CINZA'

        ordem_unidades = [
            "A1", "A2", "B1", "B2", "C1", "C2", "D1", "D2", "D3", "E1", "E3", 
            "F3 (UNIQUE)", "G3", "5º B", "9º MATERNO", "10º MATERNO", 
            "CTIA 1º", "CTIA A1", "CTIA A2", "CTIA A3", "CTIA 3A", 
            "CTIA 5A", "CTIA 4A", "UTI PED", "UTI NEO"
        ]
        df_final['UNIDADE'] = pd.Categorical(df_final['UNIDADE'], categories=ordem_unidades, ordered=True)
        df_final = df_final.sort_values(by='UNIDADE')
        return df_final
    except:
        return None

df = carregar_dados()

if df is not None:
    cores = {'VERDE': '#22c55e', 'AMARELO': '#eab308', 'VERMELHO': '#ef4444', 'CINZA': '#cbd5e1', 'PRETO': '#1c1c1c'}

    html_style = """
    <style>
        /* overflow-y: hidden mata a barra de cima/baixo | overflow-x: auto mantém a de esquerda/direita */
        body { 
            font-family: sans-serif; 
            margin: 0; 
            background: white; 
            padding: 10px; 
            overflow-y: hidden; 
            overflow-x: auto; 
        }
        
        .header-container { 
            display: flex; align-items: center; padding: 10px 0; 
            border-bottom: 2px solid #edf2f7; margin-bottom: 10px;
        }
        .titulo-painel { font-size: 24px; font-weight: bold; color: #1e293b; margin: 0; }
        .btn-print { margin-left: auto; padding: 8px 16px; background: #1e293b; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; }

        .container-geral { display: inline-block; min-width: 100%; }
        .linha { display: flex; flex-wrap: nowrap; border-bottom: 1px solid #edf2f7; background: white; width: 100%; }
        
        .coluna-fixa { 
            position: sticky; left: 0; z-index: 100; min-width: 250px; 
            background: white; padding: 10px; border-right: 2px solid #edf2f7; 
        }
        
        .wrapper-cards { display: flex; flex-wrap: nowrap; gap: 8px; padding: 10px; }
        .card { flex: 0 0 100px; width: 100px; border: 1px solid #e2e8f0; border-radius: 6px; padding: 10px 5px; text-align: center; }
        .leito { font-size: 14px; font-weight: bold; }
        .tipo { font-size: 9px; color: #94a3b8; text-transform: uppercase; }
        .status-bar { height: 6px; border-radius: 3px; margin-top: 8px; width: 80%; margin-left: 10%; }
        .stats-container { margin-top: 8px; display: flex; flex-wrap: wrap; gap: 4px; }
        .stat-item { font-size: 10px; font-weight: bold; padding: 1px 4px; border-radius: 3px; color: white; }

        @media print { 
            .btn-print { display: none !important; } 
            .coluna-fixa { position: relative !important; left: 0 !important; }
        }
    </style>
    """

    html_corpo = f"""
    <div class="header-container">
        <h1 class="titulo-painel">🏥 Painel de Monitoramento dos Leitos</h1>
        <button class="btn-print" onclick="window.print()">🖨️ Imprimir Painel</button>
    </div>
    <div class="container-geral">
    """
    
    num_linhas = 0
    for (unidade, especialidade), g_esp in df.groupby(['UNIDADE', 'ESPECIALIDADE'], sort=False):
        num_linhas += 1
        total_linha = len(g_esp)
        contagem_linha = g_esp['STATUS'].value_counts()
        stats = "".join([f"<span class='stat-item' style='background-color:{cores[s]}; color:{'black' if s in ['AMARELO','CINZA'] else 'white'};'>{contagem_linha.get(s,0)} ({(contagem_linha.get(s,0)/total_linha)*100:.0f}%)</span>" for s in cores if contagem_linha.get(s,0) > 0])

        html_corpo += f"<div class='linha'><div class='coluna-fixa'><b>{unidade}</b><br><small style='color:gray'>{especialidade}</small><div class='stats-container'>{stats}</div></div>"
        html_corpo += "<div class='wrapper-cards'>"
        for _, row in g_esp.iterrows():
            html_corpo += f"<div class='card'><div class='leito'>{row['PARA']}</div><div class='tipo'>{row['TIPO']}</div><div class='status-bar' style='background-color: {cores.get(row['STATUS'], '#cbd5e1')};'></div></div>"
        html_corpo += "</div></div>"

    # TOTAL GERAL
    total_g = len(df)
    cont_g = df['STATUS'].value_counts()
    stats_g = "".join([f"<span class='stat-item' style='background-color:{cores[s]}; color:{'black' if s in ['AMARELO','CINZA'] else 'white'};'>{cont_g.get(s,0)} ({(cont_g.get(s,0)/total_g)*100:.0f}%)</span>" for s in cores if cont_g.get(s,0) > 0])
    
    html_corpo += f"""
        <div class='linha' style='border-bottom: none;'>
            <div class='coluna-fixa'><b>TOTAL GERAL</b><br><small>Total: {total_g}</small><div class='stats-container'>{stats_g}</div></div>
            <div class='wrapper-cards'></div>
        </div>
    </div>
    """

    html_final = f"<html><head>{html_style}</head><body>{html_corpo}</body></html>"
    
    # Altura total calculada para "esticar" o componente e não precisar de scroll vertical
    # Usei 110px para dar uma margem de segurança e não cortar a barra horizontal
    altura_total = (num_linhas * 110) + 160
    
    components.html(html_final, height=altura_total, scrolling=False)
else:
    st.error("Erro ao carregar dados.")
