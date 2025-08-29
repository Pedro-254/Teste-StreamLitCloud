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
from datetime import datetime

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
  max-width: 100% !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
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
  white-space: nowrap !important;
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

/* Estilos específicos para os controles de paginação */
div[data-testid="stButton"] button {
  background-color: #EAE3D2 !important;
  color: #8B7B6A !important;
  border-color: #A18C7A !important;
  border-radius: 8px !important;
  padding: 8px 16px !important;
  font-size: 16px !important;
  min-width: 50px !important;
  transition: all 0.2s ease !important;
  white-space: nowrap !important;
  min-height: 40px !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

div[data-testid="stButton"] button:hover {
  background-color: #D1C6B8 !important;
  border-color: #8B7B6A !important;
  transform: translateY(-1px) !important;
}

div[data-testid="stButton"] button:disabled {
  background-color: #F5F5F5 !important;
  color: #CCCCCC !important;
  border-color: #E0E0E0 !important;
  cursor: not-allowed !important;
}

/* Estilo específico para o botão da primeira página */
div[data-testid="stButton"] button[data-testid="baseButton-first_page"] {
  background-color: #B7A99A !important;
  color: #EAE3D2 !important;
  border-color: #A18C7A !important;
}

div[data-testid="stButton"] button[data-testid="baseButton-first_page"]:hover {
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

.detail-card .row .value {
  color: #8B7B6A;
  font-weight: 400;
}

.detail-card .row .empty {
  color: #B7A99A;
  font-style: italic;
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

/* Estilo para links de PDF */
.prontuarios-section .card a {
  color: #8B7B6A !important;
  text-decoration: none;
  font-weight: 500;
}

.prontuarios-section .card a:hover {
  text-decoration: underline;
  color: #A18C7A !important;
}

/* Estilo para o histórico com HTML */
.prontuarios-section .card .row div {
  color: #8B7B6A !important;
  margin-top: 5px;
  line-height: 1.4;
}

/* Estilos para centralizar os controles de paginação */
.pagination-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin: 20px 0;
  padding: 20px;
  flex-wrap: nowrap;
  overflow-x: auto;
}

/* Linha interna da paginação para manter elementos lado a lado */
.pagination-inline {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  flex-wrap: nowrap;
  white-space: nowrap;
}

/* Links/Spans estilizados como botões na paginação */
.pagination-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background-color: #EAE3D2 !important;
  color: #8B7B6A !important;
  border: 1px solid #A18C7A !important;
  border-radius: 8px !important;
  padding: 8px 16px !important;
  font-size: 16px !important;
  min-width: 50px !important;
  min-height: 40px !important;
  text-decoration: none !important;
  transition: all 0.2s ease !important;
  white-space: nowrap !important;
}

.pagination-btn:hover {
  background-color: #D1C6B8 !important;
  border-color: #8B7B6A !important;
  transform: translateY(-1px) !important;
}

.pagination-btn.disabled {
  background-color: #F5F5F5 !important;
  color: #CCCCCC !important;
  border-color: #E0E0E0 !important;
  pointer-events: none !important;
}

/* Responsivo: em telas muito estreitas, reduza fonte/padding do botão para não quebrar o layout */
@media (max-width: 500px) {
  div[data-testid="stButton"] button,
  .stButton > button,
  .pagination-btn {
    font-size: 13px !important;
    padding: 6px 10px !important;
  }
}

/* Evita sobreposição do botão sobre o input em larguras intermediárias */
@media (max-width: 800px) {
  .st-emotion-cache-ocqkz7, /* container de coluna (classe pode variar por tema/versão) */
  .st-emotion-cache-13ln4jf {
    min-width: 0 !important;
  }
  div[data-testid="stButton"] button,
  .stButton > button {
    max-width: 100% !important;
    width: 100% !important;
  }
}

.pagination-info {
  text-align: center;
  color: #8B7B6A;
  font-weight: 500;
  white-space: nowrap;
  min-width: 150px;
}

/* Estilos específicos para botões de navegação */
.navigation-buttons {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
}

/* Container para seletor de página rápida */
.quick-page-selector {
  text-align: center;
  margin-top: 20px;
  padding: 20px;
}

.quick-page-selector .page-selector-title {
  color: #8B7B6A;
  font-weight: 500;
  margin-bottom: 15px;
}

/* Alinha botões à esquerda por padrão */
div[data-testid="stButton"] {
  display: flex;
  justify-content: flex-start;
}

/* Garante que o texto de página ocupe espaço sem quebrar */
.pagination-info {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 40px;
}

/* Centraliza botões apenas nas áreas de paginação e seletor rápido */
.pagination-container div[data-testid="stButton"],
.quick-page-selector div[data-testid="stButton"] {
  justify-content: center !important;
}

/* Search row: keep input + ✖ + Buscar in one line */
div[data-testid="stHorizontalBlock"]:has(input[placeholder*="Digite o nome do paciente"]) {
  display: flex !important;
  flex-wrap: nowrap !important;
  align-items: end !important;
  gap: 8px !important;
}

div[data-testid="stHorizontalBlock"]:has(input[placeholder*="Digite o nome do paciente"]) > div:first-child {
  flex: 1 1 auto !important;
  min-width: 180px !important;
}

div[data-testid="stHorizontalBlock"]:has(input[placeholder*="Digite o nome do paciente"]) > div:nth-child(2),
div[data-testid="stHorizontalBlock"]:has(input[placeholder*="Digite o nome do paciente"]) > div:nth-child(3) {
  flex: 0 0 auto !important;
}

div[data-testid="stHorizontalBlock"]:has(input[placeholder*="Digite o nome do paciente"]) div[data-testid="stButton"] button {
  width: auto !important;
  max-width: none !important;
  white-space: nowrap !important;
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

def fetch_patients(api_base_url: str, nome: str, page: int = 1) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Busca pacientes na API: GET {API_URL}/pacientes?nome=<nome>&page=<page>
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
            {"id": 29, "nome": "Mariana Pereira", "nascimento": "15/03/1985", "celular": "(31) 95563-8579", "telefone_residencial": "(31) 3333-4444", "email": "marianapereira.29@example.com", "profissao": "Advogada", "cpf": "123.456.789-00", "endereco": "Av. Faria Lima, 584", "cidade_estado": "Fortaleza/CE", "cep": "60175-000", "observacao": "Paciente assídua", "como_conheceu": "Indicação"},
            {"id": 33, "nome": "Mariana Araujo", "nascimento": "22/07/1990", "celular": "(48) 99883-1998", "telefone_residencial": "(48) 2222-3333", "email": "marianaaraujo.33@mail.com", "profissao": "Médica", "cpf": "987.654.321-00", "endereco": "Av. Brasil, 3977", "cidade_estado": "São Paulo/SP", "cep": "01330-000", "observacao": "Primeira consulta", "como_conheceu": "Internet"},
        ]
        return items, {"query": nome, "total": len(items), "version": "mock", "page": page, "total_pages": 1}

    # Constrói a URL com parâmetros
    params = []
    if nome and nome.strip():
        params.append(f"nome={quote(nome)}")
    if page > 1:
        params.append(f"page={page}")
    
    if params:
        url = f"{api_base_url}/pacientes?{'&'.join(params)}"
    else:
        url = f"{api_base_url}/pacientes"

    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        items = data.get("items", [])
        normalized = []
        for item in items:
            # Combina cidade e estado se existirem separadamente
            cidade = item.get("cidade", "")
            estado = item.get("estado", "")
            cidade_estado = ""
            if cidade and estado:
                cidade_estado = f"{cidade}/{estado}"
            elif cidade:
                cidade_estado = cidade
            elif estado:
                cidade_estado = estado
            else:
                cidade_estado = item.get("cidade_estado", "")  # Fallback para formato antigo
            
            normalized.append({
                "id": item.get("id"),
                "nome": item.get("nome") or "",
                "nascimento": item.get("nascimento") or "",
                "celular": item.get("celular") or item.get("telefone", "") or "",  # Fallback para compatibilidade
                "telefone_residencial": item.get("telefone_residencial") or "",
                "email": item.get("email") or "",
                "profissao": item.get("profissao") or "",
                "cpf": item.get("cpf") or "",
                "endereco": item.get("endereco") or "",
                "cidade_estado": cidade_estado,
                "cep": item.get("cep") or "",
                "observacao": item.get("observacao") or "",
                "como_conheceu": item.get("como_conheceu") or "",
            })
        
        total = data.get("total", len(normalized))
        total_pages = max(1, (total + 24) // 25)  # Calcula total de páginas (25 por página)
        
        meta = {
            "query": data.get("query", nome),
            "total": total,
            "version": data.get("version", ""),
            "page": page,
            "total_pages": total_pages,
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

    return [], {"query": nome, "total": 0, "version": "", "page": page, "total_pages": 1}

def create_excel_download(pacientes: List[Dict[str, Any]]) -> bytes:
    """Cria um arquivo Excel com todos os pacientes para download."""
    if not pacientes:
        return b""
    
    # Cria DataFrame com os dados dos pacientes
    df = pd.DataFrame(pacientes)
    
    # Garante que todos os campos necessários existam
    required_columns = ['nome', 'nascimento', 'celular', 'telefone_residencial', 'email', 'profissao', 'cpf', 'endereco', 'cidade_estado', 'cep', 'observacao', 'como_conheceu', 'id']
    for col in required_columns:
        if col not in df.columns:
            df[col] = ""
    
    # Reorganiza as colunas para uma ordem mais lógica
    columns_order = ['nome', 'nascimento', 'celular', 'telefone_residencial', 'email', 'profissao', 'cpf', 'endereco', 'cidade_estado', 'cep', 'observacao', 'como_conheceu', 'id']
    df = df[columns_order]
    
    # Renomeia as colunas para português
    df.columns = ['Nome', 'Nascimento', 'Celular', 'Telefone Residencial', 'E-mail', 'Profissão', 'CPF', 'Endereço', 'Cidade/Estado', 'CEP', 'Observação', 'Como conheceu', 'ID']
    
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
      "paciente": {"id": "-1260774740", "nome": "Neide Aparecida Gomes"},
      "prontuarios": [...],
      "total_prontuarios": 3,
      "version": "pacientes-v5-firebase-only"
    }
    Retorna (lista_de_prontuarios, dados_do_paciente)
    """
    if not paciente_id:
        return [], {}
    if not api_base_url:
        # Mock quando não há API
        mock_prontuarios = [
            {"data": "2024-05-02", "historico": "Acompanhamento clínico", "tipo_doc": "pdf", "classe": "exemplo.pdf"},
            {"data": "2024-06-15", "historico": "Hemograma completo", "tipo_doc": "", "classe": ""},
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
            "nascimento": "",
            "celular": "(00) 00000-0000",
            "telefone_residencial": "(00) 00000-0000",
            "email": "paciente@example.com",
            "profissao": "",
            "cpf": "",
            "endereco": "Rua Exemplo, 123",
            "cidade_estado": "",
            "cep": "",
            "observacao": "",
            "como_conheceu": "",
        }
    url = f"{api_base_url}/pacientes/{quote(str(paciente_id))}"
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 404:
            return {}
        resp.raise_for_status()
        data = resp.json()
        # Combina cidade e estado se existirem separadamente
        cidade = data.get("cidade", "")
        estado = data.get("estado", "")
        cidade_estado = ""
        if cidade and estado:
            cidade_estado = f"{cidade}/{estado}"
        elif cidade:
            cidade_estado = cidade
        elif estado:
            cidade_estado = estado
        else:
            cidade_estado = data.get("cidade_estado", "")  # Fallback para formato antigo
        
        return {
            "id": data.get("id"),
            "nome": data.get("nome", ""),
            "nascimento": data.get("nascimento", ""),
            "celular": data.get("celular", "") or data.get("telefone", "") or "",  # Fallback para compatibilidade
            "telefone_residencial": data.get("telefone_residencial", ""),
            "email": data.get("email", ""),
            "profissao": data.get("profissao", ""),
            "cpf": data.get("cpf", ""),
            "endereco": data.get("endereco", ""),
            "cidade_estado": cidade_estado,
            "cep": data.get("cep", ""),
            "observacao": data.get("observacao", ""),
            "como_conheceu": data.get("como_conheceu", ""),
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
                # Limpa todos os parâmetros da URL para garantir estado limpo
                st.query_params.clear()
                # Força limpeza completa do cache da sessão
                for key in list(st.session_state.keys()):
                    if 'cache' in key.lower() or 'paciente' in key.lower() or 'prontuario' in key.lower():
                        del st.session_state[key]
                # Força limpeza do cache do Streamlit
                st.cache_data.clear()
                st.cache_resource.clear()
            except Exception:
                pass
            st.rerun()

    # Usa dados da API se disponível, senão usa dados locais
    nome_paciente = paciente_api.get("nome") if paciente_api else paciente.get("nome", "")
    
    # Função auxiliar para renderizar campos com formatação condicional
    def format_field(value, field_name):
        if value:
            # Formatação especial para data de nascimento
            if field_name == "Nascimento" and isinstance(value, str):
                try:
                    # Remove a hora se existir e formata apenas a data
                    if " " in value:
                        date_part = value.split(" ")[0]
                        dt = datetime.strptime(date_part, "%Y-%m-%d")
                        value = dt.strftime("%d/%m/%Y")
                    elif "T" in value:
                        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
                        value = dt.strftime("%d/%m/%Y")
                except:
                    pass  # Mantém o valor original se não conseguir formatar
            
            return f'<div class="row"><span class="label">{field_name}:</span> <span class="value">{value}</span></div>'
        else:
            return f'<div class="row"><span class="label">{field_name}:</span> <span class="empty">-</span></div>'
    
    # Renderiza os dados do paciente
    st.markdown(
        f"""
<div class="detail-card">
  <h2 style="margin-top:0;">Dados do Paciente</h2>
  {format_field(nome_paciente, "Nome")}
  {format_field(paciente.get("nascimento", ""), "Nascimento")}
  {format_field(paciente.get("celular", "") or paciente.get("telefone", ""), "Celular")}
  {format_field(paciente.get("telefone_residencial", ""), "Telefone Residencial")}
  {format_field(paciente.get("email", ""), "E-mail")}
  {format_field(paciente.get("profissao", ""), "Profissão")}
  {format_field(paciente.get("cpf", ""), "CPF")}
  {format_field(paciente.get("endereco", ""), "Endereço")}
  {format_field(paciente.get("cidade_estado", ""), "Cidade/Estado")}
  {format_field(paciente.get("cep", ""), "CEP")}
  {format_field(paciente.get("observacao", ""), "Observação")}
  {format_field(paciente.get("como_conheceu", ""), "Como conheceu")}
</div>
""",
        unsafe_allow_html=True,
    )

    st.subheader("Prontuários")
    if not prontuarios:
        st.info("Nenhum prontuário encontrado para este paciente.")
    else:
        # Ordena os prontuários por data (mais recente primeiro)
        prontuarios_ordenados = sorted(prontuarios, key=lambda x: x.get("data", ""), reverse=True)
        
        # Cria cards para os prontuários
        html_parts = ['<div class="prontuarios-section">', '<div class="cards-grid">']
        for prontuario in prontuarios_ordenados:
            data = prontuario.get("data", "")
            historico = prontuario.get("historico", "")
            tipo_doc = prontuario.get("tipo_doc", "")
            classe = prontuario.get("classe", "")
            
            # Formata a data para exibição mais amigável
            data_formatada = data
            if data and "T" in data:
                try:
                    dt = datetime.fromisoformat(data.replace("Z", "+00:00"))
                    data_formatada = dt.strftime("%d/%m/%Y %H:%M")
                except:
                    data_formatada = data
            
            # Cria o card do prontuário
            card_html = f"""
<div class="card">
  <div class="row"><span class="label">Data:</span> {data_formatada}</div>
  <div class="row"><span class="label">Histórico:</span> <div style="margin-top: 5px; line-height: 1.4;">{historico}</div></div>
"""
            
            # Adiciona link para PDF se for um documento PDF
            if tipo_doc == "pdf" and classe:
                card_html += f'<div class="row"><span class="label">Documento:</span> <a href="{classe}" target="_blank" rel="noopener">📄 Visualizar PDF</a></div>'
            
            card_html += "</div>"
            html_parts.append(card_html)
            
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
        tel = p.get("celular", "") or p.get("telefone", "")  # Fallback para compatibilidade
        email = p.get("email", "")
        html_parts.append(textwrap.dedent(f"""
<div class="card">
  <a class="overlay-link" href="./?id={p.get('id')}" target="_self" rel="noopener"></a>
  <h3>{nome}</h3>
  <div class="row"><span class="label">Telefone:</span> {tel}</div>
  <div class="row"><span class="label">E-mail:</span> {email}</div>
</div>
""" ).strip())
    html_parts.append("</div>")

    st.markdown("\n".join(html_parts), unsafe_allow_html=True)

# ---------------------------
# UI
# ---------------------------
st.title("Pacientes Dra. Carolina Adorno")

# Verifica se há um paciente selecionado via ?id=
selected_id = get_selected_paciente_id()

# Limpa cache quando não há paciente selecionado para evitar dados residuais
if not selected_id:
    # Limpa qualquer cache residual da sessão
    for key in list(st.session_state.keys()):
        if 'cache' in key.lower() or 'paciente' in key.lower() or 'prontuario' in key.lower():
            del st.session_state[key]
    # Limpa cache do Streamlit para garantir estado limpo
    try:
        st.cache_data.clear()
        st.cache_resource.clear()
    except Exception:
        pass

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
    # Limpa cache da sessão quando não há paciente selecionado
    if 'paciente_cache' in st.session_state:
        del st.session_state['paciente_cache']
    if 'prontuarios_cache' in st.session_state:
        del st.session_state['prontuarios_cache']
    
    # Barra de busca (sem botões)
    st.markdown("<div style='color: #000000; font-weight: 500;'>Pesquisar por nome</div>", unsafe_allow_html=True)
    default_nome = st.query_params.get("nome", "")
    if "search_q" not in st.session_state:
        st.session_state["search_q"] = default_nome
    # Renderiza input sem forçar value em cada rerun
    q = st.text_input("", placeholder="Digite o nome do paciente... (ex.: Maria)", label_visibility="collapsed", key="search_q")
    # Inicializa referência anterior se necessário
    if "last_search_query" not in st.session_state:
        st.session_state["last_search_query"] = (st.session_state.get("search_q", "") or "").strip()
    # Só reseta para página 1 quando o valor realmente muda
    new_query = (st.session_state.get("search_q", "") or "").strip()
    prev_query = st.session_state.get("last_search_query", default_nome or "")
    if new_query != prev_query:
        if new_query:
            st.query_params["nome"] = new_query
        else:
            try:
                del st.query_params["nome"]
            except Exception:
                pass
            try:
                del st.query_params["page"]
            except Exception:
                pass
        st.query_params["page"] = 1
        st.session_state["last_search_query"] = new_query

    # Busca dados na API conforme o texto e página (auto-aplica ao digitar)
    # Se não há texto digitado, tenta pegar da URL
    search_query = q.strip() if q.strip() else st.query_params.get("nome", "")
    # (Sincronização de URL já tratada acima ao detectar mudança de texto)
    
    # Obtém a página atual da URL
    current_page = 1
    url_page = st.query_params.get("page", "1")
    try:
        current_page = int(url_page) if url_page.isdigit() else 1
    except:
        current_page = 1
    
    with st.spinner("Buscando pacientes..."):
        pacientes, meta = fetch_patients(API_URL, search_query, current_page)
    
    
    st.caption(f"{meta.get('total', len(pacientes))} resultado(s) para “{meta.get('query', q or '')}”")

    # Cards
    render_cards(pacientes)

    # Controles de navegação entre páginas - sem colunas (evita quebra em telas estreitas)
    if meta.get('total_pages', 1) > 1:
        st.markdown("---")
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    current_page_num = int(meta.get('page', 1))
    total_pages = int(meta.get('total_pages', 1))

    page_text = (
        f"Página {current_page_num}"
        if total_pages <= 1 else f"Página {current_page_num} de {total_pages}"
    )

    # Controles de paginação usando botões do Streamlit (não abrem nova aba)
    # Aparência similar aos botões originais
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if current_page_num > 1:
            if st.button("◀", help="Página anterior", key="prev_page"):
                st.query_params["page"] = current_page_num - 1
                st.rerun()
        else:
            st.button("◀", disabled=True, key="prev_page_disabled")
    
    with col2:
        st.markdown(f"<div class='pagination-info'>{page_text}</div>", unsafe_allow_html=True)
    
    with col3:
        if current_page_num < total_pages:
            if st.button("▶", help="Próxima página", key="next_page"):
                st.query_params["page"] = current_page_num + 1
                st.rerun()
        else:
            st.button("▶", disabled=True, key="next_page_disabled")
    
    # Seletor rápido de página (apenas se houver muitas páginas)
    if meta.get('total_pages', 1) > 10:
        st.markdown('<div class="quick-page-selector">', unsafe_allow_html=True)
        st.markdown('<div class="page-selector-title">Ir para página específica:</div>', unsafe_allow_html=True)
        
        col_a, col_b, col_c = st.columns([1, 1, 1])
        
        with col_a:
            target_page = st.number_input("Página", min_value=1, max_value=meta.get('total_pages', 1), value=meta.get('page', 1), key="target_page")
        
        with col_b:
            if st.button("Ir para página", help="Navegar para a página selecionada", key="go_to_page"):
                st.query_params["page"] = target_page
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
