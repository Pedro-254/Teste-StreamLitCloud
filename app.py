import streamlit as st
import requests

st.title("Minha Página Streamlit 🚀")

if st.button("Testar API"):
    try:
        response = requests.get("https://flask-api.onrender.com")
        st.success(f"Resposta da API: {response.json()['message']}")
    except Exception as e:
        st.error(f"Erro ao chamar a API: {e}")
