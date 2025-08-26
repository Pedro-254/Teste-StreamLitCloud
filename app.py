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
  --card-bg: #EAE3D2;
  --card-border: #A18C7A;
  --text-muted: #8B7B6A;
  --brand: #B7A99A;
  --page-bg: #D1C6B8;
  --accent: #B7A99A;
}

/* Estilo geral da página */
.main {
  background-color: var(--page-bg);
}

/* Estilo para o título principal */
h1 {
  color: #8B7B6A !important;
}

/* Estilo para subheaders (incluindo "Prontuários") */
h2, h3 {
  color: #8B7B6A !important;
}

/* Estilo para os campos de input */
.stTextInput > div > div > input {
  background-color: #EAE3D2 !important;
  border-color: #A18C7A !important;
  color: #000000 !important;
}

/* Estilo para o label "Pesquisar por nome" */
.stTextInput > div > div > label {
  color: #000000 !important;
}

/* Estilo para o texto "X resultado(s) para..." */
p[data-testid="caption"] {
  color: #000000 !important;
}

/* Estilos específicos para o caption dos resultados */
.stCaption {
  color: #000000 !important;
}

/* Estilo para qualquer elemento que contenha o texto de resultados */
p, span, div {
  color: inherit;
}

/* Estilo específico para o caption dos resultados */
.stCaption {
  color: #000000 !important;
}

/* Estilo para o texto digitado no input */
.stTextInput input {
  color: #000000 !important;
}

/* Estilo para o placeholder também */
.stTextInput input::placeholder {
  color: #666666 !important;
}

/* Estilos mais específicos para garantir que funcionem */
div[data-testid="stTextInput"] label,
div[data-testid="stTextInput"] input {
  color: #000000 !important;
}

/* Estilo para o caption com máxima especificidade */
div[data-testid="stCaption"] p,
div[data-testid="stCaption"] span,
p[data-testid="caption"],
span[data-testid="caption"] {
  color: #000000 !important;
}

/* Estilo para qualquer texto dentro do campo de input */
input[type="text"],
input[placeholder*="Digite o nome"] {
  color: #000000 !important;
}

/* Estilos com máxima especificidade para o texto digitado */
input[type="text"] {
  color: #000000 !important;
}

/* Estilos para o texto dos resultados com máxima especificidade */
div[data-testid="stCaption"] {
  color: #000000 !important;
}

div[data-testid="stCaption"] * {
  color: #000000 !important;
}

/* Estilo específico para o caption dos resultados */
.stCaption {
  color: #000000 !important;
}

/* Estilo para o texto digitado no input */
.stTextInput input {
  color: #000000 !important;
}

/* Estilo para o placeholder também */
.stTextInput input::placeholder {
  color: #666666 !important;
}

/* Estilo para botões */
.stButton > button {
  background-color: #EAE3D2 !important;
  color: #8B7B6A !important;
  border-color: #A18C7A !important;
}

.stButton > button:hover {
  background-color: #D1C6B8 !important;
  border-color: #8B7B6A !important;
}

/* Estilo mais específico para garantir que funcione */
button[data-testid="baseButton-secondary"] {
  background-color: #EAE3D2 !important;
  color: #8B7B6A !important;
  border-color: #A18C7A !important;
}

button[data-testid="baseButton-secondary"]:hover {
  background-color: #D1C6B8 !important;
  border-color: #8B7B6A !important;
}

/* Estilo com máxima especificidade para botões */
div[data-testid="stButton"] button,
div[data-testid="stButton"] button:hover,
div[data-testid="stButton"] button:focus,
div[data-testid="stButton"] button:active {
  background-color: #EAE3D2 !important;
  color: #8B7B6A !important;
  border-color: #A18C7A !important;
}

div[data-testid="stButton"] button:hover {
  background-color: #D1C6B8 !important;
  border-color: #8B7B6A !important;
}

/* Estilo para botões de download também */
.stDownloadButton > button {
  background-color: #B7A99A !important;
  color: #EAE3D2 !important;
  border-color: #A18C7A !important;
}

.stDownloadButton > button:hover {
  background-color: #A18C7A !important;
  border-color: #8B7B6A !important;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  margin-top: 12px;
}

.card {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 16px;
  padding: 18px 20px;
  position: relative;
  cursor: pointer;
  transition: transform 0.08s ease-in-out, border-color 0.2s ease, box-shadow 0.2s ease;
}

.card:hover {
  border-color: var(--brand);
  transform: translateY(-2px);
}

.card h3 {
  margin: 0 0 10px 0;
  font-size: 1.15rem;
  line-height: 1.3;
  color: #8B7B6A;
}

.card .row {
  margin: 8px 0;
  font-size: 0.96rem;
  color: #A18C7A;
}

.card .label {
  display: inline-block;
  width: 110px;
  color: var(--text-muted);
}

.card a {
  text-decoration: none;
}

.card a:hover { text-decoration: underline; }

.card .overlay-link {
  position: absolute;
  inset: 0;
  z-index: 10;
}

.detail-card {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 16px;
  padding: 22px;
  margin-top: 8px;
}

.detail-card h2 {
  color: #8B7B6A;
  margin-bottom: 16px;
}

.detail-card .row {
  margin: 10px 0;
  font-size: 1rem;
  color: #A18C7A;
  line-height: 1.5;
}

.detail-card .label {
  display: inline-block;
  width: 120px;
  color: var(--text-muted);
  font-weight: 500;
}

/* Estilos para a seção de prontuários */
.prontuarios-section {
  margin-top: 24px;
}

.prontuarios-section h3 {
  color: #8B7B6A;
  margin-bottom: 16px;
}

/* Grid específico para prontuários - uma coluna */
.prontuarios-section .cards-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-top: 12px;
}

.prontuarios-section .cards-grid .card {
  width: 100%;
  max-width: 600px;
}

/* Estilos específicos para os cards de prontuários */
.prontuarios-section .card {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 16px;
  padding: 18px 20px;
  position: relative;
  transition: transform 0.08s ease-in-out, border-color 0.2s ease, box-shadow 0.2s ease;
}

.prontuarios-section .card:hover {
  border-color: var(--brand);
  transform: translateY(-2px);
}

.prontuarios-section .card h3 {
  margin: 0 0 10px 0;
  font-size: 1.15rem;
  line-height: 1.3;
  color: #8B7B6A;
}

.prontuarios-section .card .row {
  margin: 8px 0;
  font-size: 0.96rem;
  color: #A18C7A;
}

.prontuarios-section .card .label {
  display: inline-block;
  width: 110px;
  color: var(--text-muted);
  font-weight: 500;
}

/* Estilo com máxima especificidade para o caption dos resultados */
div[data-testid="stCaption"],
div[data-testid="stCaption"] p,
div[data-testid="stCaption"] span,
div[data-testid="stCaption"] div,
div[data-testid="stCaptionContainer"],
div[data-testid="stCaptionContainer"] p,
div[data-testid="stCaptionContainer"] span,
div[data-testid="stCaptionContainer"] div,
p[data-testid="caption"],
span[data-testid="caption"],
.stCaption,
.stCaption * {
  color: #000000 !important;
}

/* Estilo para qualquer elemento que possa conter o texto de resultados */
p, span, div {
  color: inherit;
}

/* Estilo para alertas/info boxes (como "Nenhum prontuário encontrado") */
.stAlert,
.stAlert > div,
.stAlert > div > div {
  background-color: #EAE3D2 !important;
  color: #8B7B6A !important;
}

.stAlert p,
.stAlert span,
.stAlert div {
  color: #8B7B6A !important;
}

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

    except requests.HTTPError:
        # Erro HTTP - não exibe erro na interface
        pass
    except requests.RequestException:
        # Erro de rede - não exibe erro na interface
        pass
    except ValueError:
        # Erro de JSON - não exibe erro na interface
        pass

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

def fetch_prontuarios(api_base_url: str, paciente_id: Any) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Busca prontuários na API: GET {API_URL}/pacientes/prontuarios?id=<id>
    Espera resposta:
    {
      "paciente": {"id": 30, "nome": "Eduardo Rocha"},
      "prontuarios": [...],
      "total_prontuarios": 2,
      "version": "pacientes-v3-com-prontuarios"
    }
    Retorna (lista_de_prontuarios, dados_do_paciente)
    """
    if not paciente_id:
        return [], {}
    if not api_base_url:
        # Mock quando não há API
        mock_prontuarios = [
            {"data": "2024-05-02", "tipo": "Consulta", "descricao": "Acompanhamento clínico"},
            {"data": "2024-06-15", "tipo": "Exame", "descricao": "Hemograma completo"},
        ]
        mock_paciente = {
            "id": int(paciente_id) if str(paciente_id).isdigit() else paciente_id,
            "nome": "Paciente (mock)"
        }
        return mock_prontuarios, mock_paciente
    
    url = f"{api_base_url}/pacientes/prontuarios?id={quote(str(paciente_id))}"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        
        if isinstance(data, dict):
            prontuarios = data.get("prontuarios", [])
            paciente_info = data.get("paciente", {})
            return prontuarios, paciente_info
        else:
            return [], {}
            
    except requests.HTTPError:
        # Erro HTTP (como 404) - não exibe erro na interface
        pass
    except requests.RequestException:
        # Erro de rede - não exibe erro na interface
        pass
    except ValueError:
        # Erro de JSON - não exibe erro na interface
        pass
    
    return [], {}

def fetch_patient_by_id(api_base_url: str, paciente_id: Any) -> Dict[str, Any]:
    """Busca um paciente específico em {API_URL}/pacientes/<id> (se existir)."""
    if not paciente_id:
        return {}
    if not api_base_url:
        return {
            "id": int(paciente_id) if str(paciente_id).isdigit() else paciente_id,
            "nome": "Paciente (mock)",
            "endereco": "Rua Exemplo, 123",
            "telefone": "(00) 00000-0000",
            "email": "paciente@example.com",
        }
    url = f"{api_base_url}/pacientes/{quote(str(paciente_id))}"
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 404:
            return {}
        resp.raise_for_status()
        data = resp.json()
        return {
            "id": data.get("id"),
            "nome": data.get("nome", ""),
            "endereco": data.get("endereco", ""),
            "telefone": data.get("telefone", ""),
            "email": data.get("email", ""),
        }
    except Exception:
        return {}

def get_selected_paciente_id() -> Any:
    """Obtém o parâmetro id da URL (compatível com APIs antiga e nova)."""
    selected_id = None
    try:
        qp = st.query_params
        id_value = qp.get("id")
        if isinstance(id_value, list):
            selected_id = id_value[0]
        elif id_value is not None:
            selected_id = id_value
    except Exception:
        pass
    return selected_id


def render_patient_detail(paciente: Dict[str, Any], prontuarios: List[Dict[str, Any]], paciente_api: Dict[str, Any] = None):
    """Renderiza detalhe do paciente com prontuários abaixo, ocupando a página."""
    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        if st.button("⬅ Voltar para lista", help="Voltar para a listagem de pacientes"):
            try:
                # Limpa apenas o id se possível
                try:
                    del st.query_params["id"]
                except KeyError:
                    st.query_params.clear()
            except Exception:
                pass
            st.rerun()

    # Usa dados da API se disponível, senão usa dados locais
    nome_paciente = paciente_api.get("nome") if paciente_api else paciente.get("nome", "")
    
    st.markdown(
        """
<div class="detail-card">
  <h2 style="margin-top:0;">Dados do Paciente</h2>
  <div class="row"><span class="label">Nome:</span> {nome}</div>
  <div class="row"><span class="label">Endereço:</span> {endereco}</div>
  <div class="row"><span class="label">Telefone:</span> {telefone}</div>
  <div class="row"><span class="label">E-mail:</span> {email}</div>
</div>
""".format(
            nome=nome_paciente,
            endereco=paciente.get("endereco", ""),
            telefone=paciente.get("telefone", ""),
            email=paciente.get("email", ""),
        ),
        unsafe_allow_html=True,
    )

    st.subheader("Prontuários")
    if not prontuarios:
        st.info("Nenhum prontuário encontrado para este paciente.")
    else:
        # Cria cards para os prontuários
        html_parts = ['<div class="prontuarios-section">', '<div class="cards-grid">']
        for prontuario in prontuarios:
            data = prontuario.get("data", "")
            tipo = prontuario.get("tipo", "")
            descricao = prontuario.get("descricao", "")
            
            html_parts.append(textwrap.dedent(f"""
<div class="card">
  <h3>{tipo}</h3>
  <div class="row"><span class="label">Data:</span> {data}</div>
  <div class="row"><span class="label">Descrição:</span> {descricao}</div>
</div>
""").strip())
        html_parts.append("</div>")
        html_parts.append("</div>")
        
        st.markdown("\n".join(html_parts), unsafe_allow_html=True)

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
        html_parts.append(textwrap.dedent(f"""
<div class="card">
  <a class="overlay-link" href="./?id={p.get('id')}" target="_self" rel="noopener"></a>
  <h3>{nome}</h3>
  <div class="row"><span class="label">Endereço:</span> {end}</div>
  <div class="row"><span class="label">Telefone:</span> {tel}</div>
  <div class="row"><span class="label">E-mail:</span> {email}</div>
</div>
""" ).strip())
    html_parts.append("</div>")

    st.markdown("\n".join(html_parts), unsafe_allow_html=True)

# ---------------------------
# UI
# ---------------------------
st.title("Pacientes Carolina Adorno")

# Verifica se há um paciente selecionado via ?id=
selected_id = get_selected_paciente_id()

if selected_id:
    try:
        selected_id_int = int(str(selected_id))
    except Exception:
        selected_id_int = selected_id

    paciente = fetch_patient_by_id(API_URL, selected_id_int)
    if not paciente:
        pacientes_tmp, _ = fetch_patients(API_URL, "")
        paciente = next((p for p in pacientes_tmp if str(p.get("id")) == str(selected_id_int)), None)

    if paciente:
        with st.spinner("Carregando dados do paciente..."):
            prontuarios, paciente_api = fetch_prontuarios(API_URL, paciente.get("id"))
        render_patient_detail(paciente, prontuarios, paciente_api)
    else:
        st.warning("Paciente não encontrado.")
else:
    # Barra de busca (envia direto para a API no parâmetro ?nome=)
    q = st.text_input("Pesquisar por nome", placeholder="Digite o nome do paciente... (ex.: Maria)")

    # Busca dados na API conforme o texto
    with st.spinner("Buscando pacientes..."):
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

    st.caption(f"{meta.get('total', len(pacientes))} resultado(s) para “{meta.get('query', q or '')}”")

    # Cards
    render_cards(pacientes)
