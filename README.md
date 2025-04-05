# IRAH App – Índice de Risco Assistencial Hospitalar

Aplicativo em Streamlit para cálculo automatizado do Índice de Risco Assistencial Hospitalar (IRAH).

## 🔍 Funcionalidades

- Cálculo multiescalar com base em 5 critérios clínicos
- Classificação automática de risco (baixo, moderado, alto)
- Armazenamento automático no Google Sheets
- Compatível com múltiplos profissionais e locais

## 🚀 Como usar

1. Clone este repositório:
```
git clone https://github.com/seu-usuario/SEU-REPO.git
cd SEU-REPO
```

2. Instale as dependências:
```
pip install -r requirements.txt
```

3. Execute o app:
```
streamlit run streamlit_app.py
```

## 🔐 Segurança
As credenciais do Google não estão no repositório. Elas devem ser configuradas via `st.secrets`.

## 📋 Dados salvos
Os dados de cada avaliação incluem:
- Código do atendimento
- Data e hora da avaliação
- Todos os valores das escalas
- Resultado final do índice e classificação

---

**Uso clínico-educacional. A decisão final deve sempre considerar o julgamento profissional.**
