import pandas as pd
import streamlit as st
from fpdf import FPDF

# 1. Dados de exemplo (Substitua pela sua lógica de leitura da planilha)
data = {
    'BLOCO': ['BLOCO A', 'BLOCO A', 'BLOCO B'],
    'UNIDADE': ['UTI', 'UTI', 'ENFERMARIA'],
    'ESPECIALIDADE': ['CARDIOLOGIA', 'CARDIOLOGIA', 'CLINICA MEDICA'],
    'PARA': ['1001', '1002', '2001'],
    'TIPO DE ACOMODAÇÃO': ['INDIVIDUAL', 'DUPLO', 'COLETIVO'],
    'STATUS': ['VERDE', 'AMARELO', 'VERMELHO']
}
df = pd.DataFrame(data)

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'MAPA DE CONTROLE DE LEITOS', ln=True, align='C')
        self.ln(5)

def gerar_pdf(dataframe):
    pdf = PDF(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Cores
    cores_rgb = {
        'VERDE': (46, 204, 113),
        'AMARELO': (241, 196, 15),
        'VERMELHO': (231, 76, 60)
    }

    for bloco, g_bloco in dataframe.groupby('BLOCO'):
        # Título do Bloco
        pdf.set_fill_color(44, 62, 80)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, f" BLOCO: {bloco}", ln=True, fill=True)
        pdf.set_text_color(0, 0, 0)
        
        for unidade, g_unidade in g_bloco.groupby('UNIDADE'):
            pdf.ln(2)
            pdf.set_font('Arial', 'B', 11)
            pdf.set_text_color(41, 128, 185)
            pdf.cell(0, 8, f"  UNIDADE: {unidade}", ln=True)
            
            for especialidade, g_esp in g_unidade.groupby('ESPECIALIDADE'):
                pdf.set_font('Arial', 'I', 10)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 7, f"    Especialidade: {especialidade}", ln=True)
                
                # Desenhar os "Cards" dos leitos
                pdf.set_font('Arial', '', 9)
                x_inicial = pdf.get_x() + 15
                
                for index, row in g_esp.iterrows():
                    # Borda do card
                    curr_x = pdf.get_x()
                    curr_y = pdf.get_y()
                    
                    # Cabeçalho do Leito (Número)
                    pdf.set_fill_color(240, 240, 240)
                    pdf.rect(curr_x + 15, curr_y, 30, 8, 'F')
                    pdf.set_xy(curr_x + 15, curr_y)
                    pdf.set_font('Arial', 'B', 10)
                    pdf.cell(30, 8, str(row['PARA']), border=1, align='C')
                    
                    # Tipo de Acomodação
                    pdf.set_xy(curr_x + 15, curr_y + 8)
                    pdf.set_font('Arial', '', 7)
                    pdf.multi_cell(30, 4, row['TIPO DE ACOMODAÇÃO'], border=1, align='C')
                    
                    # Barra de Status (Cor)
                    cor = cores_rgb.get(row['STATUS'], (200, 200, 200))
                    pdf.set_fill_color(*cor)
                    pdf.rect(curr_x + 15, pdf.get_y(), 30, 4, 'F')
                    pdf.rect(curr_x + 15, pdf.get_y(), 30, 4, 'D')
                    
                    # Move para o lado para o próximo card
                    pdf.set_xy(curr_x + 35, curr_y)
                    
                    if pdf.get_x() > 250: # Quebra linha se chegar no fim da página
                        pdf.ln(25)
                
                pdf.ln(25) # Espaço após fechar uma especialidade
    
    return pdf.output(dest='S')

# Interface Streamlit
st.title("Gerador de Mapa de Leitos")

if st.button("Gerar PDF para Impressão"):
    pdf_bytes = gerar_pdf(df)
    st.download_button(
        label="Baixar PDF",
        data=pdf_bytes,
        file_name="mapa_leitos.pdf",
        mime="application/pdf"
    )
