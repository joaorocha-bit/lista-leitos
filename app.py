import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configurações da Página
st.set_page_config(page_title="Painel SAME & CENTRAL", layout="wide")

# --- AJUSTE OS NOMES DAS SUAS COLUNAS AQUI ---
COL_STATUS = 'Status do armário'
COL_SETOR = 'Setor'
COL_CARGO = 'Cargo'
COL_ARMARIO = 'Número do Armário'
COL_NOME = 'Colaborador'
COL_MATRICULA = 'Matrícula'

# 2. Função de carregamento
@st.cache_data(ttl=60)
def carregar_dados_direto(gid, pular, colunas=None):
    base_url = "https://docs.google.com/spreadsheets/d/1VyOpe3bAhdY6OUxpM2czoSV-06qM_5BiAihVsMy4TlE/export?format=csv&gid="
    url = f"{base_url}{gid}"
    return pd.read_csv(url, skiprows=pular, usecols=colunas)

# --- CARREGAMENTO ---
try:
    df_same = carregar_dados_direto(gid="1374357823", pular=2, colunas=range(13)) 
    df_central = carregar_dados_direto(gid="1301252523", pular=2, colunas=range(13))
    df_contratos_orig = carregar_dados_direto(gid="1717672079", pular=4, colunas=range(6))
    
    df_same['Unidade'] = 'SAME'
    df_central['Unidade'] = 'CENTRAL'
    df_total = pd.concat([df_same, df_central], ignore_index=True)
    
except Exception as e:
    st.error(f"Erro ao carregar: {e}")
    st.stop()

st.title("📊 Gestão Integrada")

# --- PARTE 1: DH - STATUS CONTRATOS ---
st.markdown("---")
st.subheader("📋 Status de Contratos e Armários (DH)")

df_total[COL_MATRICULA] = df_total[COL_MATRICULA].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)
mapa_armarios = dict(zip(df_total[COL_MATRICULA], df_total[df_total.columns[0]]))

def buscar_armario_ajustado(matricula):
    m = str(matricula).strip().replace('.0', '')
    resultado = mapa_armarios.get(m) or mapa_armarios.get(m.lstrip('0'))
    return resultado if pd.notna(resultado) else "Não encontrado"

col_matr_contratos = df_contratos_orig.columns[0] 
df_contratos_orig['Nº Armário Localizado'] = df_contratos_orig[col_matr_contratos].apply(buscar_armario_ajustado)

with st.expander("🔍 Filtrar Colunas da Tabela DH", expanded=False):
    cols_filtros = st.columns(len(df_contratos_orig.columns))
    filtros_selecionados = {}
    for i, col_name in enumerate(df_contratos_orig.columns):
        col_lower = col_name.lower()
        if ('matr' in col_lower or 'nome' in col_lower or 'localizado' in col_lower) and 'status' not in col_lower:
            filtros_selecionados[col_name] = cols_filtros[i].text_input(f"{col_name}", key=f"df_txt_{col_name}")
        else:
            opcoes = ["Todos"] + sorted(df_contratos_orig[col_name].dropna().unique().tolist())
            escolha = cols_filtros[i].selectbox(f"{col_name}", opcoes, key=f"df_sel_{col_name}")
            filtros_selecionados[col_name] = escolha if escolha != "Todos" else None

df_contratos_filtrado = df_contratos_orig.copy()
for col_name, valor in filtros_selecionados.items():
    if valor:
        if valor in df_contratos_orig[col_name].unique():
            df_contratos_filtrado = df_contratos_filtrado[df_contratos_filtrado[col_name] == valor]
        else:
            df_contratos_filtrado = df_contratos_filtrado[df_contratos_filtrado[col_name].astype(str).str.contains(valor, case=False)]

def estilizar_linhas(row):
    status_col = next((c for c in row.index if 'status' in c.lower()), row.index[4])
    status = str(row[status_col]).strip().upper()
    armario = str(row['Nº Armário Localizado'])
    if any(x in status for x in ["DESLIGADO", "DEMITIDO", "RESCISÃO INDIRETA"]) and armario != "Não encontrado":
        return ['background-color: #ffcccc'] * len(row) 
    if any(x in status for x in ["INSS", "AUXÍLIO DOENÇA", "LIC. S/ REMUNERAÇÃO"]) and armario != "Não encontrado":
        return ['background-color: #fff9c4'] * len(row) 
    return [''] * len(row)

st.info("💡 **Legenda:** Vermelho (Desligados c/ armário) | Amarelo (Licenças c/ armário)")
st.dataframe(df_contratos_filtrado.style.apply(estilizar_linhas, axis=1), use_container_width=True, hide_index=True)

# --- PARTE 2: FILTROS GERAIS DASHBOARDS ---
st.markdown("---")
st.subheader("⚙️ Filtros de Dashboards")

c1, c2, c3, c4 = st.columns(4)
with c1:
    opcoes_setor = sorted(df_total[COL_SETOR].dropna().unique()) if COL_SETOR in df_total.columns else []
    setor_sel = st.multiselect("Setor:", opcoes_setor)
with c2:
    opcoes_cargo = sorted(df_total[COL_CARGO].dropna().unique()) if COL_CARGO in df_total.columns else []
    cargo_sel = st.multiselect("Cargo:", opcoes_cargo)
with c3:
    busca_armario = st.text_input("Nº do Armário (Busca Exata):")
with c4:
    busca_nome = st.text_input("Nome Colaborador (Dashboards):")

df_f = df_total.copy()
if setor_sel:
    df_f = df_f[df_f[COL_SETOR].isin(setor_sel)]
if cargo_sel:
    df_f = df_f[df_f[COL_CARGO].isin(cargo_sel)]
if busca_armario:
    col_real_armario = next((c for c in df_f.columns if 'armário' in c.lower() or 'numero' in c.lower()), None)
    if col_real_armario:
        df_f = df_f[df_f[col_real_armario].astype(str).str.strip() == str(busca_armario).strip()]
if busca_nome:
    col_real_nome = next((c for c in df_f.columns if 'nome' in c.lower() or 'colaborador' in c.lower()), None)
    if col_real_nome:
        df_f = df_f[df_f[col_real_nome].astype(str).str.contains(busca_nome, case=False)]

# --- PARTE 3: DASHBOARDS ---
st.markdown("---")

def desenhar_unidade(df_base, nome_unidade):
    df = df_base[df_base['Unidade'] == nome_unidade].copy()
    st.header(f"📍 {nome_unidade}")
    
    if COL_STATUS in df.columns:
        # Padronização de nomes para contagem correta
        df[COL_STATUS] = df[COL_STATUS].astype(str).str.strip().str.upper()
        counts_total = df[COL_STATUS].value_counts()
        
        # Cálculo de Outros (Tudo que não é Ocupado nem Vago)
        ocupados = counts_total.get('OCUPADO', 0)
        vagos = counts_total.get('VAGO', 0)
        total_unidade = len(df)
        outros = total_unidade - (ocupados + vagos)
        
        # Métricas nos números em cima dos gráficos
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(f"Total {nome_unidade}", total_unidade)
        m2.metric("Ocupados", ocupados)
        m3.metric("Vagos", vagos)
        m4.metric("Outros", outros)
        
        cg, ct = st.columns([1, 1])
        with cg:
            # Gráfico de Pizza COM TODOS os valores originais (sem agrupar)
            fig = px.pie(df, names=COL_STATUS, hole=0.4, 
                         color=COL_STATUS,
                         color_discrete_map={'OCUPADO': '#EF553B', 'VAGO': '#00CC96'})
            st.plotly_chart(fig, use_container_width=True)
        with ct:
            st.dataframe(df.drop(columns=['Unidade']), use_container_width=True, hide_index=True)

desenhar_unidade(df_f, "SAME")
st.divider()
desenhar_unidade(df_f, "CENTRAL")