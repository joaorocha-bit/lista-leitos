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

    # CSS com Rolagem Interna e ajuste de GAP
    html_style = """
    <style>
        /* Remove o scroll da página externa para usar só o interno */
        html, body { 
            margin: 0; padding: 0; height: 100%; overflow: hidden; background: white; font-family: sans-serif; 
        }
        
        /* Container principal que ocupa a tela toda e permite scroll */
        .viewport {
            height: 100vh;
            display: flex;
            flex-direction: column;
        }

        .header-container { 
            display: flex; align-items: center; padding: 15px 20px; 
            border-bottom: 2px solid #edf2f7; background: white; flex-shrink: 0;
        }
        .titulo-painel { font-size: 24px; font-weight: bold; color: #1e293b; margin: 0; }
        .btn-print { margin-left: auto; padding: 8px 16px; background: #1e293b; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; }

        /* Área de conteúdo com scroll próprio: elimina o gap no final */
        .scroll-area {
            flex-grow: 1;
            overflow-y: auto;
            overflow-x: auto;
            padding-bottom: 0px; /* Conecta o total com o fim da barra */
        }

        .container-geral { display: inline-block; min-width: 100%; }
        .linha { display: flex; flex-wrap: nowrap; border-bottom: 1px solid #edf2f7; background: white; width: 100%; }
        .coluna-fixa { position: sticky; left: 0; z-index: 100; min-width: 250px; background: white; padding: 10px; border-right: 2px solid #edf2f7; box-shadow: 2px 0 5px rgba(0,0,0,0.05); }
        .wrapper-cards { display: flex; flex-wrap: nowrap; gap: 8px; padding: 10px; }
        .card { flex: 0 0 100px; width: 100px; border: 1px solid #e2e8f0; border-radius: 6px; padding: 10px 5px; text-align: center; background: white; }
        .leito { font-size: 14px; font-weight: bold; }
        .tipo { font-size: 9px; color: #94a3b8; text-transform: uppercase; margin-top: 2px; }
        .status-bar { height: 6px; border-radius: 3px; margin-top: 8px; width: 80%; margin-left: 10%; }
        .stats-container { margin-top: 8px; display: flex; flex-wrap: wrap; gap: 4px; }
        .stat-item { font-size: 10px; font-weight: bold; padding: 1px 4px; border-radius: 3px; color: white; }

        @media print { 
            .viewport { height: auto; overflow: visible; }
            .scroll-area { overflow: visible; }
            .btn-print { display: none !important; } 
            .coluna-fixa { position: relative !important; left: 0 !important; box-shadow: none !important; }
            @page { size: landscape; margin: 1cm; }
        }
    </style>
    """

    # Montagem do HTML
    html_corpo = f"""
    <div class="viewport">
        <div class="header-container">
            <h1 class="titulo-painel">🏥 Painel de Monitoramento dos Leitos HMV</h1>
            <button class="btn-print" onclick="window.print()">🖨️ Imprimir Painel</button>
        </div>
        <div class="scroll-area">
            <div class="container-geral">
    """
    
    for (unidade, especialidade), g_esp in df.groupby(['UNIDADE', 'ESPECIALIDADE'], sort=False):
        total_linha = len(g_esp)
        contagem_linha = g_esp['STATUS'].value_counts()
        stats = "".join([f"<span class='stat-item' style='background-color:{cores[s]}; color:{'black' if s in ['AMARELO','CINZA'] else 'white'};'>{contagem_linha.get(s,0)} ({(contagem_linha.get(s,0)/total_linha)*100:.0f}%)</span>" for s in cores if contagem_linha.get(s,0) > 0])

        html_corpo += f"<div class='linha'><div class='coluna-fixa'><b>{unidade}</b><br><small style='color:gray'>{especialidade}</small><div class='stats-container'>{stats}</div></div>"
        html_corpo += "<div class='wrapper-cards'>"
        for _, row in g_esp.iterrows():
            html_corpo += f"<div class='card'><div class='leito'>{row['PARA']}</div><div class='tipo'>{row['TIPO']}</div><div class='status-bar' style='background-color: {cores.get(row['STATUS'], '#cbd5e1')};'></div></div>"
        html_corpo += "</div></div>"

    # TOTAL GERAL - Sem margem embaixo para "colar" na barra
    total_g = len(df)
    cont_g = df['STATUS'].value_counts()
    stats_g = "".join([f"<span class='stat-item' style='background-color:{cores[s]}; color:{'black' if s in ['AMARELO','CINZA'] else 'white'};'>{cont_g.get(s,0)} ({(cont_g.get(s,0)/total_g)*100:.0f}%)</span>" for s in cores if cont_g.get(s,0) > 0])
    
    html_corpo += f"""
                <div class='linha' style='border-bottom: none;'>
                    <div class='coluna-fixa'><b>TOTAL GERAL DE LEITOS</b><br><small>Total: {total_g}</small><div class='stats-container'>{stats_g}</div></div>
                    <div class='wrapper-cards'></div>
                </div>
            </div>
        </div>
    </div>
    """

    html_final = f"<html><head>{html_style}</head><body>{html_corpo}</body></html>"
    
    # Altura do componente fixa na tela (ex: 85vh = 85% da altura da visão do usuário)
    # Isso faz com que a barra de rolagem lateral fique "colada" no conteúdo.
    components.html(html_final, height=800, scrolling=False)
else:
    st.error("Erro ao carregar dados.")
