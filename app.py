import pandas as pd
from weasyprint import HTML

# 1. Carregar os dados (Substitua pelo caminho do seu arquivo CSV ou conexão gspread)
# df = pd.read_csv('seu_arquivo.csv')
# Abaixo, uma simulação baseada na sua estrutura:
data = {
    'BLOCO': ['BLOCO A', 'BLOCO A', 'BLOCO B'],
    'UNIDADE': ['UTI', 'UTI', 'ENFERMARIA'],
    'ESPECIALIDADE': ['CARDIOLOGIA', 'CARDIOLOGIA', 'CLINICA MEDICA'],
    'PARA': ['101', '102', '205'],
    'TIPO DE ACOMODAÇÃO': ['INDIVIDUAL', 'DUPLO', 'COLETIVO'],
    'STATUS': ['VERDE', 'AMARELO', 'VERMELHO'] # Coluna que você adicionará
}
df = pd.DataFrame(data)

# 2. Configuração de Cores
color_map = {
    'VERDE': '#2ecc71',
    'AMARELO': '#f1c40f',
    'VERMELHO': '#e74c3c'
}

# 3. Construção do Layout HTML/CSS
html_template = """
<html>
<head>
    <style>
        @page { size: A4 landscape; margin: 10mm; }
        body { font-family: sans-serif; color: #333; }
        .bloco { background: #2c3e50; color: white; padding: 10px; margin-top: 20px; border-radius: 4px; }
        .unidade { color: #2980b9; margin-left: 20px; border-bottom: 2px solid #eee; padding: 5px; font-weight: bold; }
        .especialidade { margin-left: 40px; color: #7f8c8d; font-style: italic; margin-bottom: 10px; }
        .container-leitos { margin-left: 40px; }
        .card { 
            display: inline-block; width: 100px; border: 1px solid #ccc; 
            margin: 5px; text-align: center; border-radius: 4px; overflow: hidden;
        }
        .leito-id { font-weight: bold; padding: 5px; background: #f4f4f4; }
        .leito-tipo { font-size: 8pt; padding: 10px 2px; min-height: 30px; }
        .status-bar { height: 15px; width: 100%; }
    </style>
</head>
<body>
    <h1 style="text-align:center">Mapa de Leitos</h1>
"""

# 4. Lógica de Ramificação (Grouping)
for bloco, g_bloco in df.groupby('BLOCO'):
    html_template += f'<div class="bloco">BLOCO: {bloco}</div>'
    for unidade, g_unidade in g_bloco.groupby('UNIDADE'):
        html_template += f'<div class="unidade">UNIDADE: {unidade}</div>'
        for especialidade, g_esp in g_unidade.groupby('ESPECIALIDADE'):
            html_template += f'<div class="especialidade">{especialidade}</div>'
            html_template += '<div class="container-leitos">'
            for _, row in g_esp.iterrows():
                cor = color_map.get(row['STATUS'], '#bdc3c7')
                html_template += f'''
                <div class="card">
                    <div class="leito-id">{row['PARA']}</div>
                    <div class="leito-tipo">{row['TIPO DE ACOMODAÇÃO']}</div>
                    <div class="status-bar" style="background-color: {cor}"></div>
                </div>
                '''
            html_template += '</div>'

html_template += "</body></html>"

# 5. Gerar PDF
HTML(string=html_template).write_pdf("Mapa_Leitos_Final.pdf")
print("PDF gerado com sucesso!")
