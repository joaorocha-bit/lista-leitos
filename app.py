import pandas as pd
import streamlit as st
from fpdf import FPDF
import requests
from io import StringIO

# Configuração da página para aproveitar o espaço horizontal
st.set_page_config(page_title="Mapa de Leitos Hospitalar", layout="wide")

# --- CONEXÃO COM A PLANILHA DO GOOGLE ---
def carregar_dados():
    # ID extraído do seu novo link
    SHEET_ID = "1N0zcHuMz2gmilXlu8bKujkwDggPnTxg8fVp90eWEUw4"
    URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
    
    try:
        response = requests.get(URL)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text))
        
        # Limpa nomes de colunas (remove espaços extras)
        df.columns = [c.strip() for c in df.columns]
        
        # Garante que as colunas necessárias existam para não dar erro no processamento
        colunas_obrigatorias = ['BLOCO', 'UNIDADE', 'ESPECIALIDADE', 'PARA', 'TIPO DE ACOMODAÇÃO']
        for col in colunas_obrigatorias:
            if col not in df.columns:
                st.error(f"A coluna '{col}' não foi encontrada na planilha!")
                return None
        
        return df
    except Exception as e:
        st.error(f"Erro ao conectar com a planilha: {e}")
        st.info("⚠️ Certifique-se de que a planilha está compartilhada como 'Qualquer pessoa com o link'.")
        return None

# --- GERADOR DE PDF (LAYOUT EM GRID CONFORME DESENHO) ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'MAPA OPERACIONAL DE LEITOS', ln=True, align='C')
        self.ln(5)

def gerar_pdf_grid(df):
    # 'L' = Landscape (Paisagem) para caber os leitos lado a lado
    pdf = PDF(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()
    
    # Cores de Status
    cores_rgb = {
        'VERDE': (46, 204, 113),
        'AMARELO': (241, 196, 15),
        'VERMELHO': (231, 76, 60),
        'CINZA': (200, 200, 200)
    }

    # Agrupamento: BLOCO -> UNIDADE -> ESPECIALIDADE
    grupos = df.groupby(['BLOCO', 'UNIDADE', 'ESPECIALIDADE'], sort=False)

    for (bloco, unidade, especialidade), leitos in grupos:
        h_campo = 7 # Altura de cada campo do leito
        y_linha = pdf.get_y()
        
        # --- COLUNAS DE CABEÇALHO (LADO ESQUERDO) ---
        pdf.set_font('Arial', 'B', 8)
        # BLOCO
        pdf.set_xy(10, y_linha)
        pdf.cell(15, h_campo * 3, f"BLOCO {bloco}", border=1, align='C')
        # UNIDADE
        pdf.set_xy(25, y_linha)
        pdf.cell(35, h_campo * 3, str(unidade), border=1, align='C')
        # ESPECIALIDADE
        pdf.set_xy(60, y_linha)
        pdf.cell(40, h_campo * 3, str(especialidade), border=1, align='C')
        
        # --- CARDS DE LEITOS (EXPANDINDO PARA A DIREITA) ---
        x_leito = 105
        for _, row in leitos.iterrows():
            # Se o próximo leito for ultrapassar a largura da folha, quebra a linha
            if x_leito > 265:
                y_linha += (h_campo * 3) + 2
                x_leito = 105
                if y_linha > 185: # Nova página se estourar altura
                    pdf.add_page()
                    y_linha = pdf.get_y()

            # 1. Topo: PARA (Número do Leito)
            pdf.set_xy(x_leito, y_linha)
            pdf.set_font('Arial', 'B', 9)
            pdf.set_fill_color(245, 245, 245)
            pdf.cell(28, h_campo, str(row['PARA']), border=1, align='C', fill=True)
            
            # 2. Meio: TIPO DE ACOMODAÇÃO
            pdf.set_xy(x_leito, y_linha + h_campo)
            pdf.set_font('Arial', '', 7)
            pdf.cell(28, h_campo, str(row['TIPO DE ACOMODAÇÃO']), border=1, align='C')
            
            # 3. Base: STATUS (Cor)
            pdf.set_xy(x_leito, y_linha + (h_campo * 2))
            status = str(row.get('STATUS', 'CINZA')).upper().strip()
            cor = cores_rgb.get(status, cores_rgb['CINZA'])
            pdf.set_fill_color(*cor)
            pdf.cell(28, h_campo, "", border=1, fill=True)
            
            x_leito += 28 # Largura do card
            
        # Pula para a próxima especialidade/linha
        pdf.set_y(y_linha + (h_campo * 3) + 4)

    return bytes(pdf.output())

# --- INTERFACE STREAMLIT ---
st.title("🏥 Gerador de Mapa de Leitos Hospitalar")

dados = carregar_dados()

if dados is not None:
    st.subheader("1. Dados Identificados na Planilha")
    st.dataframe(dados, use_container_width=True)
    
    st.divider()
    
    st.subheader("2. Ações")
    if st.button("🖨️ Gerar PDF para Impressão"):
        with st.spinner('Montando layout horizontal...'):
            pdf_bytes = gerar_pdf_grid(dados)
            st.success("Mapa gerado!")
            st.download_button(
                label="📥 Baixar PDF Agora",
                data=pdf_bytes,
                file_name="mapa_leitos.pdf",
                mime="application/pdf"
            )
