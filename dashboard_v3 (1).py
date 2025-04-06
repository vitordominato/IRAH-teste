
import streamlit as st
import pandas as pd
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import altair as alt
import seaborn as sns
import matplotlib.pyplot as plt

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

    dados.columns = [col.strip().lower() for col in dados.columns]

    if dados.empty or "irah" not in dados.columns:
        st.warning("⚠️ A planilha está vazia ou sem a coluna 'irah'. Faça ao menos uma avaliação.")
        st.stop()

except Exception as e:
    st.error(f"Erro ao acessar a planilha: {e}")
    st.stop()

# Conversões de tipos
dados["data/hora"] = pd.to_datetime(dados["data_hora"], errors='coerce')
dados["irah"] = pd.to_numeric(dados["irah"], errors="coerce")

# Seção 1: Gráfico de distribuição de risco
st.subheader("Distribuição dos Níveis de Risco")
contagem = dados["classificacao"].value_counts().reset_index()
contagem.columns = ["classificacao", "quantidade"]

grafico_risco = alt.Chart(contagem).mark_bar().encode(
    x=alt.X("classificacao", title="Classificação de Risco"),
    y=alt.Y("quantidade", title="Número de Pacientes"),
    tooltip=["classificacao", "quantidade"]
).properties(width=600)

st.altair_chart(grafico_risco)

# Seção 2: Evolução temporal dos atendimentos
st.subheader("Evolução dos Atendimentos ao Longo do Tempo")
evolucao = dados.groupby(dados["data/hora"].dt.date).size().reset_index(name="avaliações")

grafico_evolucao = alt.Chart(evolucao).mark_line(point=True).encode(
    x=alt.X("data/hora:T", title="Data"),
    y=alt.Y("avaliações", title="Nº de Avaliações"),
    tooltip=["data/hora", "avaliações"]
).properties(width=600)

st.altair_chart(grafico_evolucao)

# Seção 3: Médias das escalas
st.subheader("Médias das Escalas Assistenciais")
medias = dados[["fugulin", "mrc", "triagem", "charlson"]].mean().round(2).reset_index()
medias.columns = ["Escala", "Média"]
st.dataframe(medias)

# Seção 4: Comparativo de escalas por risco
st.subheader("🔍 Comparativo: Alto Risco vs Baixo/Moderado")
alto_risco = dados[dados["irah"] >= 0.6]
baixo_moderado = dados[dados["irah"] < 0.6]
escalas = ["charlson", "fugulin", "mrc", "triagem"]
comparativo = pd.DataFrame({
    "Escala": escalas,
    "Média - Alto Risco": [alto_risco[esc].mean() for esc in escalas],
    "Média - Baixo/Moderado": [baixo_moderado[esc].mean() for esc in escalas]
})
st.dataframe(comparativo.round(2))

# Seção 5: Heatmap de correlação
st.subheader("📈 Correlação entre Escalas e IRAH")
fig, ax = plt.subplots()
sns.heatmap(dados[["charlson", "fugulin", "mrc", "triagem", "irah"]].corr(), annot=True, cmap="coolwarm", ax=ax)
st.pyplot(fig)

# Seção 6: Pacientes com Alto Risco
st.subheader("Pacientes com Alto Risco (≥ 0.6)")
st.dataframe(alto_risco[["atendimento", "data/hora", "irah", "classificacao"]])

# Seção 7: Tabela interativa com filtro
st.subheader("📋 Tabela Completa (com Filtro)")
filtro = st.multiselect("Filtrar por Classificação", options=dados["classificacao"].unique())
tabela_filtrada = dados[dados["classificacao"].isin(filtro)] if filtro else dados
st.dataframe(tabela_filtrada)

# Botão de download
csv = tabela_filtrada.to_csv(index=False).encode('utf-8')
st.download_button("📥 Baixar Tabela como CSV", data=csv, file_name="dashboard_irah.csv", mime="text/csv")
