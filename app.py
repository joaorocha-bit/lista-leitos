import pandas as pd
import streamlit as st
from fpdf import FPDF

# Configuração da página do Streamlit
st.set_page_config(page_title="Mapa de Leitos", layout="wide")

# 1. Carregamento dos Dados (Simulação - substitua pela sua leitura do Google Sheets)
# Exemplo: df = pd.read_csv("link_da_sua_planilha_csv")
data = {
    'BLOCO': ['BLOCO A', 'BLOCO A', 'BLOCO A', 'BLOCO B', 'BLOCO B'],
    'UNIDADE': ['UTI ADULTO', 'UTI ADULTO', 'ENFERMARIA', 'UTI PEDIATRICA', 'UTI PEDIATRICA'],
    'ESPECIALIDADE': ['CARDIOLOGIA', 'CARDIOLOGIA', 'CLINICA MEDICA', 'NEUROLOGIA', 'NEUROLOGIA'],
    'PARA': ['101-A', '101-B', '205', '301', '302'],
    'TIPO DE ACOMODAÇÃO': ['APARTAMENTO', 'ENFERMARIA', 'ENFERMARIA', 'APARTAMENTO', 'APARTAMENTO'],
    'STATUS': ['VERDE', 'AMARELO', 'VERMELHO', 'VERDE', 'VERDE']
}
df = pd.DataFrame(data)

st.title("🏥 Gestão de Leitos - Visualização e Impressão")

# --- VISUALIZAÇÃO DA PLANILHA ---
st.subheader("1. Confira os dados da planilha abaixo:")
st.dataframe(df, use_container_width=True)

# --- LÓGICA DO PDF ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'MAPA DE CONTROLE DE LEITOS', ln=True, align='C')
        self.ln(5)

def gerar_pdf(dataframe):
    # 'L' = Landscape (Paisagem)
    pdf = PDF(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    cores_rgb = {
        'VERDE': (46, 204, 113),
        'AMARELO': (241, 196, 15),
        'VERMELHO': (231, 76, 60)
    }

    # Agrupamento: Bloco -> Unidade -> Especialidade
    for bloco, g_bloco in dataframe.groupby('BLOCO'):
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
                
                # Início dos cards de leitos
                pdf.ln(2)
                for index, row in g_esp.iterrows():
                    curr_x = pdf.get_x()
                    curr_y = pdf.get_y()
                    
                    # Se o card for sair da página, pula linha
                    if curr_x > 250:
                        pdf.ln(25)
                        curr_x = pdf.get_x()
                        curr_y = pdf.get_y()

                    # Desenha Card
                    pdf.set_fill_color(245, 245, 245)
                    pdf.rect(pdf.get_x() + 5, curr_y, 35, 18, 'F') # Fundo
                    
                    # Número do Leito
                    pdf.set_font('Arial', 'B', 11)
                    pdf.set_xy(pdf.get_x() + 5, curr_y + 1)
                    pdf.cell(35, 5, str(row['PARA']), border=0, align='C')
                    
                    # Acomodação
                    pdf.set_font('Arial', '', 7)
                    pdf.set_xy(pdf.get_x() - 35, curr_y + 6)
                    pdf.multi_cell(35, 3, str(row['TIPO DE ACOMODAÇÃO']), border=0, align='C')
                    
                    # Barra de Status
                    cor = cores_rgb.get(str(row['STATUS']).upper(), (200, 200, 200))
                    pdf.set_fill_color(*cor)
                    pdf.rect(pdf.get_x(), curr_y + 14, 35, 4, 'F') # Barra colorida
                    pdf.rect(pdf.get_x(), curr_y, 35, 18, 'D')     # Borda externa
                    
                    # Move para a direita para o próximo card
                    pdf.set_xy(pdf.get_x() + 40, curr_y)
                
                pdf.ln(22) # Espaço após cada grupo de especialidade

    # RETORNO IMPORTANTE: Convertendo para bytes que o Streamlit aceita
    return bytes(pdf.output())

# --- BOTÃO DE DOWNLOAD ---
st.subheader("2. Gerar arquivo para impressão:")
if st.button("Preparar PDF"):
    try:
        pdf_output = gerar_pdf(df)
        st.success("✅ PDF gerado com sucesso!")
        st.download_button(
            label="Clique aqui para baixar o PDF",
            data=pdf_output,
            file_name="mapa_leitos_hospitalar.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Erro ao gerar o PDF: {e}")
