import pandas as pd
import streamlit as st
import requests
from io import StringIO
import streamlit.components.v1 as components

# Configuração da página
st.set_page_config(page_title="Painel Dinâmico de Leitos", layout="wide")

def carregar_dados():
    SHEET_ID = "1N0zcHuMz2gmilXlu8bKujkwDggPnTxg8fVp90eWEUw4"
    URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
    try:
        response = requests.get(URL)
        response.raise_for_status()
        conteudo = response.text.replace('Âº', 'º').replace('âº', 'º')
        df_raw = pd.read_csv(StringIO(conteudo))
        
        # Mapeamento A, B, C, F, J
        df_final = pd.DataFrame()
        df_final['BLOCO'] = df_raw.iloc[:, 0].astype(str)
        df_final['UNIDADE'] = df_raw.iloc[:, 1].astype(str)
        df_final['ESPECIALIDADE'] = df_raw.iloc[:, 2].astype(str)
        df_final['PARA'] = df_raw.iloc[:, 5].astype(str)
        df_final['TIPO'] = df_raw.iloc[:, 9].astype(str)
        
        # STATUS na Coluna V (21)
        if df_raw.shape[1] >= 22: 
            df_final['STATUS'] = df_raw.iloc[:, 21].fillna('CINZA').astype(str).str.upper().str.strip()
        else:
            df_final['STATUS'] = 'CINZA'

        df_final = df_final.map(lambda x: x.strip() if isinstance(x, str) else x)
        return df_final
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None

# --- CSS PARA OS CARDS ---
CSS_ESTILO = """
<style>
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; background-color: #f1f5f9; }
    .scroll-container {
        display: flex !important;
        flex-direction: row !important;
        overflow-x: auto !important;
        padding: 10px !important;
        gap: 12px !important;
    }
    .leito-card {
        flex: 0 0 auto !important;
        width: 130px !important;
        background: white !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        padding: 12px !important;
        text-align: center !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    }
    .status-bar { height: 10px !important; border-radius: 4px !important; margin-top: 8px !important; }
    .scroll-container::-webkit-scrollbar { height: 6px; }
    .scroll-container::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
</style>
"""

df = carregar_dados()

if df is not None:
    # --- BARRA LATERAL (DINÂMICA) ---
    st.sidebar.header("📊 Filtros da Dinâmica")
    
    # Filtro de Bloco
    blocos = ["Todos"] + sorted(df['BLOCO'].unique().tolist())
    bloco_selecionado = st.sidebar.selectbox("Filtrar por Bloco:", blocos)
    
    # Filtro de Unidade (atualiza conforme o Bloco)
    if bloco_selecionado != "Todos":
        df_filtrado = df[df['BLOCO'] == bloco_selecionado]
    else:
        df_filtrado = df
        
    unidades = ["Todas"] + sorted(df_filtrado['UNIDADE'].unique().tolist())
    unidade_selecionada = st.sidebar.selectbox("Filtrar por Unidade:", unidades)
    
    if unidade_selecionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado['UNIDADE'] == unidade_selecionada]

    # --- MÉTRICAS (Resumo da Dinâmica) ---
    st.title("🏥 Gestão Dinâmica de Leitos")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total de Leitos", len(df_filtrado))
    m2.metric("Ocupados (Vermelho)", len(df_filtrado[df_filtrado['STATUS'] == 'VERMELHO']))
    m3.metric("Limpando (Amarelo)", len(df_filtrado[df_filtrado['STATUS'] == 'AMARELO']))
    m4.metric("Disponíveis (Verde)", len(df_filtrado[df_filtrado['STATUS'] == 'VERDE']))

    st.divider()

    # --- RENDERIZAÇÃO DOS CARDS ---
    cores = {'VERDE': '#22c55e', 'AMARELO': '#eab308', 'VERMELHO': '#ef4444', 'CINZA': '#94a3b8'}

    # Agrupamento final para exibição
    for unidade, g_unidade in df_filtrado.groupby('UNIDADE', sort=False):
        st.subheader(f"📍 {unidade}")
        
        for especialidade, g_esp in g_unidade.groupby('ESPECIALIDADE', sort=False):
            st.write(f"**Especialidade:** {especialidade} ({len(g_esp)} leitos)")
            
            html_cards = f"{CSS_ESTILO}<div class='scroll-container'>"
            for _, row in g_esp.iterrows():
                cor = cores.get(row['STATUS'], cores['CINZA'])
                html_cards += f'''
                    <div class="leito-card">
                        <div style="font-size: 16px; font-weight: bold; color: #1e293b;">{row['PARA']}</div>
                        <div style="font-size: 10px; color: #64748b; margin-top: 4px; height: 25px; overflow: hidden;">{row['TIPO']}</div>
                        <div class="status-bar" style="background-color: {cor};"></div>
                    </div>
                '''
            html_cards += "</div>"
            components.html(html_cards, height=130)
            
else:
    st.error("Não foi possível conectar à planilha.")
