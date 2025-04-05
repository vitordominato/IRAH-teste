
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json
import altair as alt

st.set_page_config(page_title="Dashboard IRAH", layout="wide")
st.title("📊 Dashboard de Risco Assistencial (IRAH)")

# Autenticação com Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials_dict = json.loads(st.secrets["gcp_service_account"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
client = gspread.authorize(creds)

# Conectando à planilha
spreadsheet = client.open("IRAH-app")
sheet = spreadsheet.worksheet("Sheet1")
dados = pd.DataFrame(sheet.get_all_records())

# Conversões de data/hora
dados["Data/Hora"] = pd.to_datetime(dados["data_hora"], errors='coerce')
dados["Data"] = dados["Data/Hora"].dt.date

# Layout em colunas
col1, col2, col3 = st.columns(3)
col1.metric("📋 Total de Avaliações", len(dados))
col2.metric("🔴 Alto Risco", f'{(dados["classificacao"] == "Alto Risco").sum()} pacientes')
col3.metric("📅 Última Avaliação", dados["Data/Hora"].max().strftime("%d/%m/%Y %H:%M"))

st.markdown("### 🧮 Distribuição de Risco")
risco_counts = dados["classificacao"].value_counts().reset_index()
risco_counts.columns = ["classificacao", "quantidade"]

chart = alt.Chart(risco_counts).mark_bar().encode(
    x=alt.X("classificacao", sort=["Baixo Risco", "Risco Moderado", "Alto Risco"]),
    y="quantidade",
    color="classificacao"
).properties(width=600, height=400)

st.altair_chart(chart)

st.markdown("### 🕒 Avaliações ao Longo do Tempo")
temporal = dados.groupby("Data").size().reset_index(name="Avaliações")
linha = alt.Chart(temporal).mark_line(point=True).encode(
    x="Data:T",
    y="Avaliações:Q"
).properties(width=700, height=350)

st.altair_chart(linha)

st.markdown("### 📄 Tabela com Filtros")
with st.expander("🔍 Visualizar dados"):
    filtro_risco = st.selectbox("Filtrar por risco:", ["Todos"] + sorted(dados["classificacao"].unique()))
    if filtro_risco != "Todos":
        dados = dados[dados["classificacao"] == filtro_risco]
    st.dataframe(dados.sort_values("Data/Hora", ascending=False), use_container_width=True)
