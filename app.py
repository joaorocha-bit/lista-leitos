import pandas as pd
import streamlit as st
from fpdf import FPDF
import requests
from io import StringIO

# Configuração da página
st.set_page_config(page_title="Mapa de Leitos Hospitalar", layout="wide")

def carregar_dados():
    # ID da sua planilha conforme o link enviado
    SHEET_ID = "1N0zcHuMz2gmilXlu8bKujkwDggPnTxg8fVp90eWEUw4"
    URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
    
    try:
        response = requests.get(URL)
        response.raise_for_status()
        # Lê a planilha bruta
        df_raw = pd.read_csv(StringIO(response.text))
        
        # Mapeamento pelas letras das colunas que você passou:
        df_final = pd.DataFrame()
        df_final['BLOCO'] = df_raw.iloc[:, 0]         # Coluna A
        df_final['UNIDADE'] = df_raw.iloc[:, 1]       # Coluna B
        df_final['ESPECIALIDADE'] = df_raw.iloc[:, 2] # Coluna C
        df_final['PARA'] = df_raw.iloc[:, 5]          # Coluna F
        df_final['TIPO'] = df_raw.iloc[:, 9]          # Coluna J
        
        # STATUS: Se não houver uma coluna de cor definida, usaremos 'VERDE' por padrão
        # Você pode mudar o número 10 abaixo se a coluna de cor for outra (Ex: K=10, L=11)
        if df_raw.shape[1] > 10:
            df_final['STATUS'] = df_raw.iloc[:, 10].fillna('VERDE')
        else:
            df_final['STATUS'] = 'VERDE'

        return df_final
    except Exception as e:
        st.error(f"Erro ao conectar com a planilha: {e}")
        return None

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'MAPA OPERACIONAL DE LEITOS', ln=True, align='C')
        self.ln(5)

def gerar_pdf_grid(df):
    pdf = PDF(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()
    
    cores_rgb = {
        'VERDE': (46, 204, 113),
        'AMARELO': (241, 196, 15),
        'VERMELHO': (231, 76, 60),
        'CINZA': (200, 200, 200)
    }

    # Agrupar pela hierarquia solicitada
    grupos = df.groupby(['BLOCO', 'UNIDADE', 'ESPECIALIDADE'], sort=False)

    for (bloco, unidade, especialidade), leitos in grupos:
        h_campo = 7 
        y_linha = pdf.get_y()
        
        # --- CABEÇALHOS À ESQUERDA ---
        pdf.set_font('Arial', 'B', 8)
        # Bloco (Col A)
        pdf.set_xy(10, y_linha)
        pdf.cell(15, h_campo * 3, str(bloco), border=1, align='C')
        # Unidade (Col B)
        pdf.set_xy(25, y_linha)
        pdf.cell(35, h_campo * 3, str(unidade), border=1, align='C')
        # Especialidade (Col C)
        pdf.set_xy(60, y_linha)
        pdf.cell(40, h_campo * 3, str(especialidade), border=1, align='C')
        
        # --- GRID DE LEITOS À DIREITA ---
        x_leito = 105
        for _, row in leitos.iterrows():
            if x_leito > 265: # Quebra para a linha de baixo se acabar o espaço lateral
                y_linha += (h_campo * 3) + 2
                x_leito = 105
                if y_linha > 185:
                    pdf.add_page()
                    y_linha = pdf.get_y()

            # Nível 1: PARA (Col F)
            pdf.set_xy(x_leito, y_linha)
            pdf.set_font('Arial', 'B', 9)
            pdf.set_fill_color(245, 245, 245)
            pdf.cell(28, h_campo, str(row['PARA']), border=1, align='C', fill=True)
            
            # Nível 2: TIPO (Col J)
            pdf.set_xy(x_leito, y_linha + h_campo)
            pdf.set_font('Arial', '', 7)
            pdf.cell(28, h_campo, str(row['TIPO']), border=1, align='C')
            
            # Nível 3: STATUS (Cor)
            pdf.set_xy(x_leito, y_linha + (h_campo * 2))
            status = str(row['STATUS']).upper().strip()
            cor = cores_rgb.get(status, cores_rgb['CINZA'])
            pdf.set_fill_color(*cor)
            pdf.cell(28, h_campo, "", border=1, fill=True)
            
            x_leito += 28
            
        pdf.set_y(y_linha + (h_campo * 3) + 4)

    return bytes(pdf.output())

# Interface do Streamlit
st.title("🏥 Gerador de Mapa de Leitos Profissional")

dados = carregar_dados()

if dados is not None:
    st.subheader("1. Conferência de Dados (Busca por Colunas A, B, C, F, J)")
    st.dataframe(dados, use_container_width=True)
    
    if st.button("🖨️ Gerar PDF com Layout Horizontal"):
        with st.spinner('Processando layout de impressão...'):
            pdf_bytes = gerar_pdf_grid(dados)
            st.success("Mapa de leitos gerado!")
            st.download_button(
                label="📥 Baixar PDF para Impressão",
                data=pdf_bytes,
                file_name="mapa_leitos_hospitalar.pdf",
                mime="application/pdf"
            )
