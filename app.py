import os
import requests
import streamlit as st
from typing import List, Dict, Any, Tuple
import unicodedata
from dotenv import load_dotenv
from urllib.parse import quote
import textwrap
import pandas as pd
from io import BytesIO

# Carrega variáveis do .env
load_dotenv()

# ---------------------------
# Configuração básica
# ---------------------------
st.set_page_config(page_title="Pacientes", page_icon="🩺", layout="wide")
API_URL = os.getenv("API_URL", "").rstrip("/")  # ex: https://sua.api

# ---------------------------
# Estilo (CSS para cards)
# ---------------------------
CARD_CSS = """
<style>
:root {
  --card-bg: #0e1117;
  --card-border: #30363d;
  --card-shadow: 0 6px 20px rgba(0,0,0,0.15);
  --text-muted: #9ba3af;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
  margin-top: 12px;
}

.card {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 16px;
  padding: 16px 18px;
  box-shadow: var(--card-shadow);
}

.card h3 {
  margin: 0 0 8px 0;
  font-size: 1.1rem;
}

.card .row {
  margin: 6px 0;
  font-size: 0.95rem;
}

.card .label {
  display: inline-block;
  width: 92px;
  color: var(--text-muted);
}

.card a {
  text-decoration: none;
}

.card a:hover { text-decoration: underline; }
</style>
"""
st.markdown(CARD_CSS, unsafe_allow_html=True)

# ---------------------------
# Utilidades
# ---------------------------
def normalize(s: str) -> str:
    """Remove acentos e normaliza para comparação case-insensitive (se precisar)."""
    if not isinstance(s, str):
        return ""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return s.lower().strip()

@st.cache_data(ttl=60)
def fetch_patients(api_base_url: str, nome: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Busca pacientes na API: GET {API_URL}/pacientes?nome=<nome>
    Espera resposta:
    {
      "items": [...],
      "query": "Maria",
      "total": 2,
      "version": "pacientes-v2-only-endpoint"
    }
    Retorna (lista_de_pacientes, meta)
    """
    if not api_base_url:
        # Mock para dev/local sem API
        items = [
            {"id": 29, "nome": "Mariana Pereira", "endereco": "Av. Faria Lima, 584 - Fortaleza/CE",
             "telefone": "(31) 95563-8579", "email": "marianapereira.29@example.com"},
            {"id": 33, "nome": "Mariana Araujo", "endereco": "Av. Brasil, 3977 - São Paulo/SP",
             "telefone": "(48) 99883-1998", "email": "marianaaraujo.33@mail.com"},
        ]
        return items, {"query": nome, "total": len(items), "version": "mock"}

    # Se não houver nome, faz query sem parâmetro
    if nome and nome.strip():
        url = f"{api_base_url}/pacientes?nome={quote(nome)}"
    else:
        url = f"{api_base_url}/pacientes"

    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        items = data.get("items", [])
        normalized = []
        for item in items:
            normalized.append({
                "id": item.get("id"),
                "nome": item.get("nome") or "",
                "endereco": item.get("endereco") or "",
                "telefone": item.get("telefone") or "",
                "email": item.get("email") or "",
            })
        meta = {
            "query": data.get("query", nome),
            "total": data.get("total", len(normalized)),
            "version": data.get("version", ""),
        }
        return normalized, meta

    except requests.HTTPError as e:
        st.error(f"Erro HTTP ao buscar pacientes: {e}")
    except requests.RequestException as e:
        st.error(f"Erro de rede ao buscar pacientes: {e}")
    except ValueError:
        st.error("Não foi possível decodificar o JSON retornado pela API.")

    return [], {"query": nome, "total": 0, "version": ""}

def create_excel_download(pacientes: List[Dict[str, Any]]) -> bytes:
    """Cria um arquivo Excel com todos os pacientes para download."""
    if not pacientes:
        return b""
    
    # Cria DataFrame com os dados dos pacientes
    df = pd.DataFrame(pacientes)
    
    # Reorganiza as colunas para uma ordem mais lógica
    columns_order = ['nome', 'endereco', 'telefone', 'email', 'id']
    df = df[columns_order]
    
    # Renomeia as colunas para português
    df.columns = ['Nome', 'Endereço', 'Telefone', 'E-mail', 'ID']
    
    # Cria o arquivo Excel em memória
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Pacientes', index=False)
        
        # Ajusta a largura das colunas automaticamente
        worksheet = writer.sheets['Pacientes']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)  # Máximo de 50 caracteres
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    output.seek(0)
    return output.getvalue()

def render_cards(pacientes: List[Dict[str, Any]]):
    """Renderiza cards dos pacientes em grid responsivo."""
    if not pacientes:
        st.info("Nenhum paciente encontrado.")
        return

    html_parts = ['<div class="cards-grid">']
    for p in pacientes:
        nome = p.get("nome", "")
        end = p.get("endereco", "")
        tel = p.get("telefone", "")
        email = p.get("email", "")
        tel_href = "".join(ch for ch in tel if ch.isdigit())

        html_parts.append(textwrap.dedent(f"""
<div class="card">
  <h3>{nome}</h3>
  <div class="row"><span class="label">Endereço:</span> {end}</div>
  <div class="row"><span class="label">Telefone:</span> <a href="tel:{tel_href}">{tel}</a></div>
  <div class="row"><span class="label">E-mail:</span> <a href="mailto:{email}">{email}</a></div>
</div>
""").strip())
    html_parts.append("</div>")

    st.markdown("\n".join(html_parts), unsafe_allow_html=True)

# ---------------------------
# UI
# ---------------------------
st.title("🩺 Pacientes do Consultório")

# Barra de busca (envia direto para a API no parâmetro ?nome=)
q = st.text_input("Pesquisar por nome", placeholder="Digite o nome do paciente... (ex.: Maria)")

# Busca dados na API conforme o texto
pacientes, meta = fetch_patients(API_URL, q)

# Botão de download Excel
if pacientes:
    excel_data = create_excel_download(pacientes)
    if excel_data:
        st.download_button(
            label="📊 Baixar Excel com todos os pacientes",
            data=excel_data,
            file_name=f"pacientes_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Clique para baixar todos os pacientes em um arquivo Excel"
        )

# Resultados


st.caption(f"{meta.get('total', len(pacientes))} resultado(s) para “{meta.get('query', q or '')}”")

# Cards
render_cards(pacientes)
