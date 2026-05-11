import pandas as pd
import streamlit as st
import requests
from io import StringIO

# Configuração da página para ocupar a tela toda
st.set_page_config(page_title="Painel de Monitoramento de Leitos", layout="wide")

def carregar_dados():
    SHEET_ID = "1N0zcHuMz2gmilXlu8bKujkwDggPnTxg8fVp90eWEUw4"
    URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
    
    try:
        response = requests.get(URL)
        response.raise_for_status()
        
        # Corrige o problema do caractere estranho Â antes de processar
        conteudo_limpo = response.text.replace('Âº', 'º').replace('âº', 'º')
        
        # Lê o conteúdo
        df_raw = pd.read_csv(StringIO(conteudo_limpo))
        
        # Mapeamento das colunas:
        df_final = pd.DataFrame()
        df_final['BLOCO'] = df_raw.iloc[:, 0].astype(str)         # Coluna A
        df_final['UNIDADE'] = df_raw.iloc[:, 1].astype(str)       # Coluna B
        df_final['ESPECIALIDADE'] = df_raw.iloc[:, 2].astype(str) # Coluna C
        df_final['PARA'] = df_raw.iloc[:, 5].astype(str)          # Coluna F
        df_final['TIPO'] = df_raw.iloc[:, 9].astype(str)          # Coluna J
        
        # STATUS na Coluna V (Índice 21)
        # Verificamos se a planilha tem colunas suficientes para chegar na V
        if df_raw.shape[1] >= 22: 
            df_final['STATUS'] = df_raw.iloc[:, 21].fillna('VERDE').astype(str).str.upper().str.strip()
        else:
            # Caso a coluna V não exista ou esteja fora do alcance
            df_final['STATUS'] = 'VERDE'

        # Limpeza final de espaços em branco
        df_final = df_final.map(lambda x: x.strip() if isinstance(x, str) else x)

        return df_final
    except Exception as e:
        st.error(f"Erro ao carregar planilha: {e}")
        return None
        
# Estilização CSS para os Cards
st.markdown("""
    <style>
    .leito-card {
        border: 1px solid #d1d1d1;
        border-radius: 5px;
        padding: 10px;
        text-align: center;
        background-color: #f8f9fa;
        margin-bottom: 10px;
        min-width: 120px;
    }
    .status-bar {
        height: 10px;
        border-radius: 3px;
        margin-top: 8px;
    }
    .bloco-header {
        background-color: #2c3e50;
        color: white;
        padding: 5px 15px;
        border-radius: 5px;
        margin-top: 20px;
    }
    .unidade-header {
        color: #2980b9;
        font-weight: bold;
        border-bottom: 2px solid #eee;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 Painel de Controle de Leitos")

df = carregar_dados()

if df is not None:
    # Cores para o status
    cores = {
        'VERDE': '#2ecc71',
        'AMARELO': '#f1c40f',
        'VERMELHO': '#e74c3c',
        'CINZA': '#bdc3c7'
    }

    # Agrupamento para o Layout
    for bloco, g_bloco in df.groupby('BLOCO', sort=False):
        st.markdown(f"<div class='bloco-header'><h3>BLOCO {bloco}</h3></div>", unsafe_allow_html=True)
        
        for unidade, g_unidade in g_bloco.groupby('UNIDADE', sort=False):
            st.markdown(f"<div class='unidade-header'>UNIDADE: {unidade}</div>", unsafe_allow_html=True)
            
            for especialidade, g_esp in g_unidade.groupby('ESPECIALIDADE', sort=False):
                st.write(f"**Especialidade:** {especialidade}")
                
                # Criar colunas para os cards de leitos (até 8 por linha na tela)
                cols = st.columns(8)
                for i, (_, row) in enumerate(g_esp.iterrows()):
                    with cols[i % 8]:
                        cor_status = cores.get(row['STATUS'], cores['CINZA'])
                        st.markdown(f"""
                            <div class="leito-card">
                                <b>{row['PARA']}</b><br>
                                <small>{row['TIPO']}</small>
                                <div class="status-bar" style="background-color: {cor_status};"></div>
                            </div>
                        """, unsafe_allow_html=True)
                st.divider()
else:
    st.info("Conecte a planilha para visualizar o painel.")
