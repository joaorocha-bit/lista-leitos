import pandas as pd
import streamlit as st
import requests
from io import StringIO
import streamlit.components.v1 as components

st.set_page_config(page_title="Gestão de Leitos", layout="wide")

# Remove TODA a UI padrão do Streamlit — título, filtros e botão ficam dentro do HTML
st.markdown("""
    <style>
        .block-container { padding: 0 !important; margin: 0 !important; }
        header[data-testid="stHeader"] { display: none !important; }
        section[data-testid="stMain"] > div { padding: 0 !important; }
        .stApp { overflow: hidden; }
    </style>
""", unsafe_allow_html=True)

def carregar_dados():
    SHEET_ID = "1N0zcHuMz2gmilXlu8bKujkwDggPnTxg8fVp90eWEUw4"
    URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
    try:
        response = requests.get(URL)
        response.raise_for_status()
        conteudo = response.text.replace('Âº', 'º').replace('âº', 'º')
        df_raw = pd.read_csv(StringIO(conteudo))

        df_final = pd.DataFrame()
        df_final['UNIDADE']      = df_raw.iloc[:, 1].astype(str).str.strip()
        df_final['ESPECIALIDADE']= df_raw.iloc[:, 2].astype(str)
        df_final['PARA']         = df_raw.iloc[:, 5].astype(str)
        df_final['TIPO']         = df_raw.iloc[:, 9].astype(str)

        if df_raw.shape[1] >= 22:
            df_final['STATUS'] = df_raw.iloc[:, 21].fillna('CINZA').astype(str).str.upper().str.strip()
        else:
            df_final['STATUS'] = 'CINZA'

        ordem_unidades = [
            "A1","A2","B1","B2","C1","C2","D1","D2","D3","E1","E3",
            "F3 (UNIQUE)","G3","5º B","9º MATERNO","10º MATERNO",
            "CTIA 1º","CTIA A1","CTIA A2","CTIA A3","CTIA 3A",
            "CTIA 5A","CTIA 4A","UTI PED","UTI NEO"
        ]
        df_final['UNIDADE'] = pd.Categorical(df_final['UNIDADE'], categories=ordem_unidades, ordered=True)
        df_final = df_final.sort_values(by='UNIDADE')
        return df_final
    except:
        return None

df = carregar_dados()

if df is not None:
    cores = {
        'VERDE':   '#22c55e',
        'AMARELO': '#eab308',
        'VERMELHO':'#ef4444',
        'CINZA':   '#cbd5e1',
        'PRETO':   '#1c1c1c'
    }

    # Listas para os <select> e <datalist>
    opcoes_unidade = [u for u in df['UNIDADE'].cat.categories if u in df['UNIDADE'].values]
    opcoes_especialidade = sorted(df['ESPECIALIDADE'].dropna().unique().tolist())
    opcoes_tipo          = sorted(df['TIPO'].dropna().unique().tolist())

    def opts(lista):
        return "".join(f'<option value="{v}">{v}</option>' for v in lista)

    # Serializa os dados para JSON para o filtro em JS
    import json
    registros = df[['UNIDADE','ESPECIALIDADE','PARA','TIPO','STATUS']].copy()
    registros['UNIDADE'] = registros['UNIDADE'].astype(str)
    dados_json = json.dumps(registros.to_dict(orient='records'), ensure_ascii=False)

    cores_json = json.dumps(cores)

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #fff; overflow: hidden; height: 100vh; display: flex; flex-direction: column; }}

  /* ── Barra de topo ── */
  .topbar {{
    flex-shrink: 0;
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 14px;
    border-bottom: 2px solid #e2e8f0;
    background: #fff;
    z-index: 20;
  }}
  .topbar .titulo {{
    font-size: 17px;
    font-weight: 800;
    color: #1e293b;
    white-space: nowrap;
    flex-shrink: 0;
  }}
  .sep {{ width: 1px; height: 28px; background: #e2e8f0; flex-shrink: 0; }}

  /* ── Filtros ── */
  .filtros {{
    display: flex;
    align-items: flex-end;
    gap: 8px;
    flex: 1;
    min-width: 0;
  }}
  .filtro-group {{
    display: flex;
    flex-direction: column;
    gap: 2px;
    min-width: 0;
  }}
  .filtro-group label {{
    font-size: 9px;
    font-weight: 700;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    white-space: nowrap;
  }}
  .filtro-group select,
  .filtro-group input[type=text] {{
    height: 28px;
    border: 1px solid #e2e8f0;
    border-radius: 5px;
    padding: 0 8px;
    font-size: 12px;
    color: #1e293b;
    background: #fff;
    outline: none;
    width: 100%;
  }}
  
  .btn-limpar, .btn-print {{
    height: 28px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 12px;
    font-weight: 700;
    white-space: nowrap;
    flex-shrink: 0;
    padding: 0 12px;
  }}
  .btn-limpar {{ background: #f1f5f9; color: #475569; }}
  .btn-print  {{ background: #1e293b; color: #fff; }}

  /* ── Painel de leitos ── */
  .scroll-area {{
    flex: 1;
    overflow-y: auto;
    overflow-x: auto;
    padding-bottom: 10px; /* Espaço para não cobrir o último item com a legenda */
  }}
  .container-geral {{ display: inline-block; min-width: 100%; }}
  .linha {{ display: flex; flex-wrap: nowrap; border-bottom: 1px solid #edf2f7; background: #fff; }}
  .coluna-fixa {{
    position: sticky; left: 0; z-index: 10;
    min-width: 220px; max-width: 220px;
    background: #fff;
    padding: 10px 12px;
    border-right: 2px solid #edf2f7;
    box-shadow: 2px 0 5px rgba(0,0,0,.05);
  }}
  .unidade-nome {{ font-size: 15px; font-weight: 700; color: #1e293b; }}
  .especialidade-nome {{ font-size: 11px; color: #94a3b8; margin-top: 1px; }}
  .stats-container {{ margin-top: 6px; display: flex; flex-wrap: wrap; gap: 3px; }}
  .stat-item {{ font-size: 9px; font-weight: 700; padding: 1px 5px; border-radius: 3px; }}
  .wrapper-cards {{ display: flex; flex-wrap: nowrap; gap: 8px; padding: 10px; }}
  
  .card {{
    flex: 0 0 90px; width: 90px;
    border: 1px solid #e2e8f0; border-radius: 6px;
    padding: 8px 4px; text-align: center; background: #fff;
  }}
  .leito-num {{ font-size: 13px; font-weight: 700; color: #1e293b; }}
  .leito-tipo {{ font-size: 8px; color: #94a3b8; text-transform: uppercase; margin-top: 2px; }}
  .status-bar {{ height: 5px; border-radius: 3px; margin: 7px 10% 0; }}

  /* ── LEGENDA NO RODAPÉ ── */
  .legenda-footer {{
    flex-shrink: 0;
    background: #f8fafc;
    border-top: 2px solid #e2e8f0;
    padding: 10px 20px;
    display: flex;
    align-items: center;
    gap: 20px;
    z-index: 20;
  }}
  .legenda-titulo {{
    font-size: 11px;
    font-weight: 800;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }}
  .legenda-itens {{
    display: flex;
    gap: 12px;
  }}
  .legenda-item {{
    display: flex;
    align-items: center;
    gap: 6px;
    background: #fff;
    padding: 4px 10px;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
    color: #1e293b;
  }}
  .legenda-cor {{
    width: 12px;
    height: 12px;
    border-radius: 3px;
  }}

  @media print {{
    body {{ overflow: visible; height: auto; }}
    .topbar, .legenda-footer {{ display: none !important; }}
    .scroll-area {{ overflow: visible; padding-bottom: 0; }}
    .coluna-fixa {{ position: relative !important; box-shadow: none !important; }}
    @page {{ size: landscape; margin: 1cm; }}
  }}
</style>
</head>
<body>

<div class="topbar">
  <span class="titulo">🏥 Painel Monitoramento de Leitos HMV</span>
  <div class="sep"></div>
  <div class="filtros">
    <div class="filtro-group fg-unidade">
      <label>Unidade</label>
      <select id="f-unidade" multiple size="1" onchange="renderizar()">
        <option value="">Todas</option>
        {opts(opcoes_unidade)}
      </select>
    </div>
    <div class="filtro-group fg-especialidade">
      <label>Especialidade</label>
      <select id="f-especialidade" multiple size="1" onchange="renderizar()">
        <option value="">Todas</option>
        {opts(opcoes_especialidade)}
      </select>
    </div>
    <div class="filtro-group fg-leito">
      <label>Leito</label>
      <input type="text" id="f-leito" placeholder="Ex: 101" oninput="renderizar()">
    </div>
    <div class="filtro-group fg-tipo">
      <label>Tipo</label>
      <select id="f-tipo" multiple size="1" onchange="renderizar()">
        <option value="">Todos</option>
        {opts(opcoes_tipo)}
      </select>
    </div>
  </div>
  <button class="btn-limpar" onclick="limpar()">✕ Limpar</button>
  <button class="btn-print"  onclick="window.print()">🖨️ Imprimir</button>
</div>

<div class="scroll-area">
  <div class="container-geral" id="painel"></div>
</div>

<div class="legenda-footer">
  <div class="legenda-titulo">Legenda:</div>
  <div class="legenda-itens">
    <div class="legenda-item"><div class="legenda-cor" style="background:#22c55e"></div> Adequado</div>
    <div class="legenda-item"><div class="legenda-cor" style="background:#eab308"></div> Manutenção s/ Bloqueio</div>
    <div class="legenda-item"><div class="legenda-cor" style="background:#ef4444"></div> Manutenção c/ Bloqueio</div>
    <div class="legenda-item"><div class="legenda-cor" style="background:#1c1c1c"></div> Bloqueio por Reforma</div>
    <div class="legenda-item"><div class="legenda-cor" style="background:#cbd5e1"></div> Não Informado</div>
  </div>
</div>

<script>
const DADOS  = {dados_json};
const CORES  = {cores_json};
const ORDEM  = {json.dumps(opcoes_unidade)};

function getSelected(id) {{
  const sel = document.getElementById(id);
  return Array.from(sel.selectedOptions).map(o => o.value).filter(v => v !== "");
}}

function limpar() {{
  ['f-unidade','f-especialidade','f-tipo'].forEach(id => {{
    const sel = document.getElementById(id);
    Array.from(sel.options).forEach(o => o.selected = false);
    sel.options[0].selected = true;
  }});
  document.getElementById('f-leito').value = '';
  renderizar();
}}

function renderizar() {{
  const fUnidade  = getSelected('f-unidade');
  const fEsp      = getSelected('f-especialidade');
  const fLeito    = document.getElementById('f-leito').value.trim().toLowerCase();
  const fTipo     = getSelected('f-tipo');

  let filtrado = DADOS.filter(r => {{
    if (fUnidade.length && !fUnidade.includes(r.UNIDADE))       return false;
    if (fEsp.length    && !fEsp.includes(r.ESPECIALIDADE))      return false;
    if (fLeito         && !r.PARA.toLowerCase().includes(fLeito)) return false;
    if (fTipo.length   && !fTipo.includes(r.TIPO))              return false;
    return true;
  }});

  const grupos = {{}};
  ORDEM.forEach(u => {{ grupos[u] = {{}}; }});
  filtrado.forEach(r => {{
    if (!grupos[r.UNIDADE]) grupos[r.UNIDADE] = {{}};
    if (!grupos[r.UNIDADE][r.ESPECIALIDADE]) grupos[r.UNIDADE][r.ESPECIALIDADE] = [];
    grupos[r.UNIDADE][r.ESPECIALIDADE].push(r);
  }});

  let html = '';
  let totalG = 0, contG = {{}};

  ORDEM.forEach(unidade => {{
    const esps = grupos[unidade];
    if (!esps) return;
    Object.entries(esps).forEach(([esp, leitos]) => {{
      if (!leitos.length) return;
      totalG += leitos.length;
      const cnt = {{}};
      leitos.forEach(l => {{ cnt[l.STATUS] = (cnt[l.STATUS]||0)+1; }});
      Object.entries(cnt).forEach(([s,n]) => {{ contG[s] = (contG[s]||0)+n; }});

      const stats = Object.entries(CORES)
        .filter(([s]) => cnt[s])
        .map(([s,c]) => {{
          const pct = Math.round(cnt[s]/leitos.length*100);
          const txtColor = ['AMARELO','CINZA'].includes(s) ? '#000' : '#fff';
          return `<span class="stat-item" style="background:${{c}};color:${{txtColor}}">${{cnt[s]}} (${{pct}}%)</span>`;
        }}).join('');

      // ── NOVO BLOCO DO SEU COMPONENTE DE LEITOS (LIMITADO A 20) ──
      let blocosCardsHtml = '<div>'; 
      const LIMITE = 20;

      for (let i = 0; i < leitos.length; i += LIMITE) {{
        const pedaco = leitos.slice(i, i + LIMITE);
        
        const cardsHtml = pedaco.map(r => {{
          const cor = CORES[r.STATUS] || '#cbd5e1';
          return `<div class="card">
            <div class="leito-num">${{r.PARA}}</div>
            <div class="leito-tipo">${{r.TIPO}}</div>
            <div class="status-bar" style="background:${{cor}}"></div>
          </div>`;
        }}).join('');

        const paddingTop = (i === 0) ? '10px' : '4px';
        const paddingBottom = (i + LIMITE >= leitos.length) ? '10px' : '4px';
        
        blocosCardsHtml += `<div class="wrapper-cards" style="padding-top: ${{paddingTop}}; padding-bottom: ${{paddingBottom}};">${{cardsHtml}}</div>`;
      }}
      blocosCardsHtml += '</div>';
      // ────────────────────────────────────────────────────────────

      html += `<div class="linha">
        <div class="coluna-fixa">
          <div class="unidade-nome">${{unidade}}</div>
          <div class="especialidade-nome">${{esp}}</div>
          <div class="stats-container">${{stats}}</div>
        </div>
        ${{blocosCardsHtml}}
      </div>`;
    }});
  }});

  if (!html) {{
    html = '<div class="empty-msg">Nenhum leito encontrado para os filtros selecionados.</div>';
  }} else {{
    const statsG = Object.entries(CORES)
      .filter(([s]) => contG[s])
      .map(([s,c]) => {{
        const pct = Math.round(contG[s]/totalG*100);
        const txtColor = ['AMARELO','CINZA'].includes(s) ? '#000' : '#fff';
        return `<span class="stat-item" style="background:${{c}};color:${{txtColor}}">${{contG[s]}} (${{pct}}%)</span>`;
      }}).join('');
    html += `<div class="linha" style="border-bottom:none">
      <div class="coluna-fixa">
        <div class="unidade-nome">TOTAL GERAL</div>
        <div class="especialidade-nome">Total: ${{totalG}}</div>
        <div class="stats-container">${{statsG}}</div>
      </div>
      <div class="wrapper-cards"></div>
    </div>`;
  }}
  document.getElementById('painel').innerHTML = html;
}}
renderizar();
</script>
</body>
</html>"""

    components.html(html, height=887, scrolling=False)

else:
    st.error("Erro ao carregar dados.")
