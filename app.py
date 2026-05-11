import pandas as pd
import streamlit as st
import requests
from io import StringIO

# 1. Configuração da página
st.set_page_config(page_title="Gestão de Leitos", layout="wide")

def carregar_dados():
    SHEET_ID = "1N0zcHuMz2gmilXlu8bKujkwDggPnTxg8fVp90eWEUw4"
    URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
    try:
        response = requests.get(URL)
        response.raise_for_status()
        # Limpeza de encoding para evitar o "Â"
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

# 2. CSS Robusto para Travar a Coluna e Scroll Global
st.markdown("""
    <style>
    /* Remove limites de largura do Streamlit */
    .main .block-container {
        max-width: none !important;
        padding: 0 !important;
        overflow-x: auto !important;
    }
    
    .painel-completo {
        display: inline-block;
        min-width: 100%;
        padding: 20px;
        background: white;
    }

    .linha-hospitalar {
        display: flex;
        flex-wrap: nowrap;
        align-items: stretch;
        border-bottom: 1px solid #f1f5f9;
        background: white;
    }

    /* COLUNA TRAVADA - O segredo está no z-index e na posição sticky */
    .unidade-fixa {
        position: sticky;
        left: 0;
        z-index: 100; /* Garante que os cards passem por baixo */
        min-width: 200px;
        width: 200px;
        background-color: white;
        padding: 15px;
        border-right: 2px solid #e2e8f0;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 4px 0 6px -2px rgba(0,0,0,0.05);
    }

    .cards-scroll-area {
        display: flex;
        flex-wrap: nowrap;
        gap: 10px;
        padding: 15px;
    }

    .card-individual {
        flex: 0 0 110px; /* Largura fixa sem espremer */
        width: 110px;
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px 5px;
        text-align: center;
    }

    .leito-nome { font-size: 14px; font-weight: bold; color: #1e293b; }
    .leito-desc { font-size: 9px; color: #94a3b8; text-transform: uppercase; }
    .status-cor { height: 6px; border-radius: 3px; margin-top: 8px; width: 80%; margin-left: 10%; }

    /* Força o título a não sumir */
    .header-fixo { position: sticky; left: 0; padding: 20px; z-index: 101; background: white; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

df = carregar_dados()

if df is not None:
    st.markdown('<div class="header-fixo"><h1>🏥 Gestão de Leitos</h1></div>', unsafe_allow_html=True)
    
    cores_map = {'VERDE': '#22c55e', 'AMARELO': '#eab308', 'VERMELHO': '#ef4444', 'CINZA': '#cbd5e1'}

    # Montando o HTML em um bloco único para evitar que o Streamlit quebre a renderização
    html_output = "<div class='painel-completo'>"

    for (unidade, especialidade), g_esp in df.groupby(['UNIDADE', 'ESPECIALIDADE'], sort=False):
        html_output += f"<div class='linha-hospitalar'>"
        
        # Lado Esquerdo (Sticky)
        html_output += f"""
            <div class='unidade-fixa'>
                <div style='font-size:13px; font-weight:bold;'>{unidade}</div>
                <div style='font-size:11px; color:#64748b;'>{especialidade}</div>
            </div>
        """
        
        # Lado Direito (Cards)
        html_output += "<div class='cards-scroll-area'>"
        for _, row in g_esp.iterrows():
            cor = cores_map.get(row['STATUS'], cores_map['CINZA'])
            html_output += f'''
                <div class="card-individual">
                    <div class="leito-nome">{row['PARA']}</div>
                    <div class="leito-desc">{row['TIPO']}</div>
                    <div class="status-cor" style="background-color: {cor};"></div>
                </div>
            '''
        html_output += "</div></div>"

    html_output += "</div>"
    
    # Renderizando tudo de uma vez
    st.markdown(html_output, unsafe_allow_html=True)
