import pandas as pd
import streamlit as st
from fpdf import FPDF
import requests
from io import StringIO

# Configuração da página para ocupar a tela toda
st.set_page_config(page_title="Mapa de Leitos Hospitalar", layout="wide")

# --- CONEXÃO COM A SUA PLANILHA ---
def carregar_dados():
    # ID extraído do seu link: 16pyATNoGY1YUvpv3nGc3DJ3rxaD20QAJ7Rb4ulZ0wvU
    SHEET_ID = "16pyATNoGY1YUvpv3nGc3DJ3rxaD20QAJ7Rb4ulZ0wvU"
    URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
    
    try:
        response = requests.get(URL)
        response.raise_for_status()
        # Lendo o CSV da sua planilha
        df = pd.read_csv(StringIO(response.text))
        
        # Garantindo que as colunas críticas existam (evita erro se houver espaço no nome)
        df.columns = [c.strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Erro ao acessar a planilha: {e}. Verifique se o compartilhamento está ativo para 'Qualquer pessoa com o link'.")
        return None

# --- GERADOR DE PDF (LAYOUT DO DESENHO) ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'MAPA DE LEITOS - VISÃO OPERACIONAL', ln=True, align='C')
        self.ln(5)

def gerar_pdf_horizontal(df):
    pdf = PDF(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()
    
    # Mapeamento de Cores
    cores_rgb = {
        'VERDE': (46, 204, 113),
        'AMARELO': (241, 196, 15),
        'VERMELHO': (231, 76, 60),
        'CINZA': (200, 200, 200)
    }

    # Agrupar pela hierarquia do seu desenho
    # BLOCO -> UNIDADE -> ESPECIALIDADE
    grupos = df.groupby(['BLOCO', 'UNIDADE', 'ESPECIALIDADE'], sort=False)

    for (bloco, unidade, especialidade), leitos in grupos:
        h_base = 8 # Altura de cada "andar" do leito
        y_start = pdf.get_y()
        
        # --- CABEÇALHOS (Lado Esquerdo) ---
        pdf.set_font('Arial', 'B', 8)
        # Célula BLOCO
        pdf.set_xy(10, y_start)
        pdf.cell(15, h_base * 3, f"BLOCO {bloco}", border=1, align='C')
        # Célula UNIDADE
        pdf.set_xy(25, y_start)
        pdf.cell(35, h_base * 3, str(unidade), border=1, align='C')
        # Célula ESPECIALIDADE
        pdf.set_xy(60, y_start)
        pdf.cell(35, h_base * 3, str(especialidade), border=1, align='C')
        
        # --- CARDS DE LEITOS (Lado Direito) ---
        x_pos = 100
        for _, row in leitos.iterrows():
            # Verifica se o card cabe na linha (A4 Paisagem tem ~297mm)
            if x_pos > 265:
                y_start += (h_base * 3) + 2
                x_pos = 100
                if y_start > 180: # Nova página se estourar altura
                    pdf.add_page()
                    y_start = pdf.get_y()

            # Nível 1: PARA (Leito)
            pdf.set_xy(x_pos, y_start)
            pdf.set_font('Arial', 'B', 9)
            pdf.set_fill_color(245, 245, 245)
            pdf.cell(28, h_base, str(row['PARA']), border=1, align='C', fill=True)
            
            # Nível 2: TIPO DE ACOMODAÇÃO
            pdf.set_xy(x_pos, y_start + h_base)
            pdf.set_font('Arial', '', 7)
            pdf.cell(28, h_base, str(row['TIPO DE ACOMODAÇÃO']), border=1, align='C')
            
            # Nível 3: STATUS (Barra de Cor)
            pdf.set_xy(x_pos, y_start + (h_base * 2))
            status = str(row.get('STATUS', 'CINZA')).upper().strip()
            cor = cores_rgb.get(status, cores_rgb['CINZA'])
            pdf.set_fill_color(*cor)
            pdf.cell(28, h_base, "", border=1, fill=True)
            
            x_pos += 28 # Largura do card + margem pequena
            
        pdf.set_y(y_start + (h_base * 3) + 4) # Espaço para a próxima linha

    return bytes(pdf.output())

# --- INTERFACE STREAMLIT ---
st.title("🏥 Sistema de Impressão de Leitos")

df_planilha = carregar_dados()

if df_planilha is not None:
    # 1. Visualização Prévia
    st.subheader("Visualização da Planilha Conectada")
    st.dataframe(df_planilha, use_container_width=True)
    
    # 2. Ação de Impressão
    st.divider()
    if st.button("🛠️ Gerar Layout para Impressão"):
        with st.spinner('Formatando leitos...'):
            pdf_bytes = gerar_pdf_horizontal(df_planilha)
            st.success("Mapa pronto para baixar!")
            st.download_button(
                label="📥 Baixar PDF Agora",
                data=pdf_bytes,
                file_name="mapa_leitos_horizontal.pdf",
                mime="application/pdf"
            )
