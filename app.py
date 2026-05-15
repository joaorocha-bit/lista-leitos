import pandas as pd
import streamlit as st
import requests
from io import StringIO
import streamlit.components.v1 as components

st.set_page_config(page_title="Gestão de Leitos", layout="wide")

# Reduz margem do topo do Streamlit
st.markdown("""
    <style>
        .block-container { padding-top: 0.5rem !important; }
        div[data-testid="stMultiSelect"] > label { font-size: 11px; font-weight: 600; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 2px; }
        div[data-testid="stMultiSelect"] .stMultiSelect > div { border-radius: 6px; border-color: #e2e8f0; font-size: 13px; }
        div[data-testid="stTextInput"] > label { font-size: 11px; font-weight: 600; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 2px; }
        div[data-testid="stTextInput"] input { border-radius: 6px; border-color: #e2e8f0; font-size: 13px; }
        div[data-testid="stHorizontalBlock"] { align-items: flex-end; gap: 12px; }
    </style>
""", unsafe_allow_html=True)

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

    # ── Cabeçalho ──────────────────────────────────────────────────────────────
    st.markdown("""
        <div style="display:flex; align-items:center; padding: 10px 0 6px 0; border-bottom: 2px solid #edf2f7; margin-bottom: 10px;">
            <span style="font-size:22px; font-weight:bold; color:#1e293b;">🏥 Painel de Monitoramento dos Leitos HMV</span>
        </div>
    """, unsafe_allow_html=True)

    # ── Filtros ─────────────────────────────────────────────────────────────────
    col1, col2, col3, col4, col5 = st.columns([2, 2, 1.2, 2, 0.6])

    opcoes_unidade     = sorted([u for u in df['UNIDADE'].cat.categories if u in df['UNIDADE'].values])
    opcoes_especialidade = sorted(df['ESPECIALIDADE'].dropna().unique().tolist())
    opcoes_tipo        = sorted(df['TIPO'].dropna().unique().tolist())

    with col1:
        sel_unidade = st.multiselect("Unidade", opcoes_unidade, placeholder="Todas")
    with col2:
        sel_especialidade = st.multiselect("Especialidade", opcoes_especialidade, placeholder="Todas")
    with col3:
        sel_leito = st.text_input("Leito", placeholder="Ex: 101")
    with col4:
        sel_tipo = st.multiselect("Tipo", opcoes_tipo, placeholder="Todos")
    with col5:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        limpar = st.button("✕ Limpar", use_container_width=True)

    if limpar:
        st.rerun()

    # ── Aplicar filtros ─────────────────────────────────────────────────────────
    df_filtrado = df.copy()
    if sel_unidade:
        df_filtrado = df_filtrado[df_filtrado['UNIDADE'].isin(sel_unidade)]
    if sel_especialidade:
        df_filtrado = df_filtrado[df_filtrado['ESPECIALIDADE'].isin(sel_especialidade)]
    if sel_leito.strip():
        df_filtrado = df_filtrado[df_filtrado['PARA'].str.contains(sel_leito.strip(), case=False, na=False)]
    if sel_tipo:
        df_filtrado = df_filtrado[df_filtrado['TIPO'].isin(sel_tipo)]

    # ── HTML do painel ──────────────────────────────────────────────────────────
    html_style = """
    <style>
        html, body { margin: 0; padding: 0; height: 100%; overflow: hidden; background: white; font-family: sans-serif; }
        .viewport { height: 100vh; display: flex; flex-direction: column; }
        .scroll-area { flex-grow: 1; overflow-y: auto; overflow-x: auto; padding-bottom: 0px; }
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
            .coluna-fixa { position: relative !important; left: 0 !important; box-shadow: none !important; }
            @page { size: landscape; margin: 1cm; }
        }
    </style>
    """

    html_corpo = """
    <div class="viewport">
        <div class="scroll-area">
            <div class="container-geral">
    """

    if df_filtrado.empty:
        html_corpo += "<div style='padding:40px; color:#94a3b8; font-size:15px;'>Nenhum leito encontrado para os filtros selecionados.</div>"
    else:
        for (unidade, especialidade), g_esp in df_filtrado.groupby(['UNIDADE', 'ESPECIALIDADE'], sort=False):
            total_linha = len(g_esp)
            contagem_linha = g_esp['STATUS'].value_counts()
            stats = "".join([
                f"<span class='stat-item' style='background-color:{cores[s]}; color:{'black' if s in ['AMARELO','CINZA'] else 'white'};'>"
                f"{contagem_linha.get(s,0)} ({(contagem_linha.get(s,0)/total_linha)*100:.0f}%)</span>"
                for s in cores if contagem_linha.get(s, 0) > 0
            ])

            html_corpo += f"<div class='linha'><div class='coluna-fixa'><b>{unidade}</b><br><small style='color:gray'>{especialidade}</small><div class='stats-container'>{stats}</div></div>"
            html_corpo += "<div class='wrapper-cards'>"
            for _, row in g_esp.iterrows():
                cor = cores.get(row['STATUS'], '#cbd5e1')
                html_corpo += (
                    f"<div class='card'>"
                    f"<div class='leito'>{row['PARA']}</div>"
                    f"<div class='tipo'>{row['TIPO']}</div>"
                    f"<div class='status-bar' style='background-color:{cor};'></div>"
                    f"</div>"
                )
            html_corpo += "</div></div>"

        # Total geral (do conjunto filtrado)
        total_g = len(df_filtrado)
        cont_g = df_filtrado['STATUS'].value_counts()
        stats_g = "".join([
            f"<span class='stat-item' style='background-color:{cores[s]}; color:{'black' if s in ['AMARELO','CINZA'] else 'white'};'>"
            f"{cont_g.get(s,0)} ({(cont_g.get(s,0)/total_g)*100:.0f}%)</span>"
            for s in cores if cont_g.get(s, 0) > 0
        ])
        html_corpo += (
            f"<div class='linha' style='border-bottom: none;'>"
            f"<div class='coluna-fixa'><b>TOTAL GERAL DE LEITOS</b><br><small>Total: {total_g}</small>"
            f"<div class='stats-container'>{stats_g}</div></div>"
            f"<div class='wrapper-cards'></div></div>"
        )

    html_corpo += "</div></div></div>"
    html_final = f"<html><head>{html_style}</head><body>{html_corpo}</body></html>"

    components.html(html_final, height=800, scrolling=False)

else:
    st.error("Erro ao carregar dados.")
