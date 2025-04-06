
import streamlit as st
import pandas as pd
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import altair as alt

st.set_page_config(page_title="Dashboard IRAH", layout="wide")
st.title("📊 Dashboard de Risco Assistencial (IRAH)")

# Autenticação com Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials_dict = json.loads(st.secrets["gcp_service_account"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
client = gspread.authorize(creds)

try:
    spreadsheet = client.open("IRAH-app")
    sheet = spreadsheet.worksheet("Sheet1")
    dados = pd.DataFrame(sheet.get_all_records())

    if dados.empty or "irah" not in dados.columns:
        st.warning("⚠️ A planilha está vazia ou sem a coluna 'irah'. Faça ao menos uma avaliação.")
        st.stop()

    # Conversões
    dados["data_hora"] = pd.to_datetime(dados.get("data_hora"), errors="coerce")
    dados["Data"] = dados["data_hora"].dt.date
    dados["irah"] = pd.to_numeric(dados.get("irah"), errors="coerce")
    for col in ["fugulin", "mrc", "triagem", "charlson"]:
        if col in dados.columns:
            dados[col] = pd.to_numeric(dados[col], errors="coerce")

    # Métricas principais
    col1, col2, col3 = st.columns(3)
    col1.metric("📋 Total de Avaliações", len(dados))
    col2.metric("🔴 Alto Risco", f'{(dados["classificacao"] == "Alto Risco").sum()} pacientes')
    col3.metric("📅 Última Avaliação", dados["data_hora"].max().strftime("%d/%m/%Y %H:%M"))

    # Distribuição de Risco
    st.markdown("### 🧮 Distribuição de Risco Assistencial")
    risco_counts = dados["classificacao"].value_counts().reset_index()
    risco_counts.columns = ["classificacao", "quantidade"]
    chart = alt.Chart(risco_counts).mark_bar().encode(
        x=alt.X("classificacao", sort=["Baixo Risco", "Risco Moderado", "Alto Risco"]),
        y="quantidade",
        color="classificacao"
    ).properties(width=600, height=400)
    st.altair_chart(chart)

    # Evolução temporal
    st.markdown("### 🕒 Avaliações ao Longo do Tempo")
    temporal = dados.groupby("Data").size().reset_index(name="Avaliações")
    linha = alt.Chart(temporal).mark_line(point=True).encode(
        x="Data:T",
        y="Avaliações:Q"
    ).properties(width=700, height=350)
    st.altair_chart(linha)

    # Médias por escala
    st.markdown("### ⚖️ Médias das Escalas Clínicas")
    escalas = ["fugulin", "mrc", "triagem", "charlson", "irah"]
    medias = dados[escalas].mean(numeric_only=True).round(2)
    st.dataframe(medias.rename("Média Geral"), use_container_width=True)

    # Correlação entre escalas
    st.markdown("### 🔗 Correlação entre Escalas")
    correlacao = dados[escalas].corr()
    st.dataframe(correlacao.style.background_gradient(cmap="coolwarm"), use_container_width=True)

    # Últimos pacientes com alto risco
    st.markdown("### 🚨 Últimos Pacientes com Alto Risco (≥ 0.6)")
    altos = dados[dados["irah"] >= 0.6].sort_values("data_hora", ascending=False)
    st.dataframe(altos[["data_hora", "atendimento", "irah", "classificacao"] + 
                  ["fugulin", "mrc", "triagem", "charlson"]], use_container_width=True)

    # Tabela final com filtros
    st.markdown("### 📄 Tabela com Filtros")
    with st.expander("🔍 Visualizar todos os dados"):
        filtro_risco = st.selectbox("Filtrar por risco:", ["Todos"] + sorted(dados["classificacao"].unique()))
        if filtro_risco != "Todos":
            dados = dados[dados["classificacao"] == filtro_risco]
        st.dataframe(dados.sort_values("data_hora", ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"Erro detectado: {e}")
