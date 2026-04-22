import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# Importando a função de predição do seu arquivo local
from previsao import prever_potencial_solar

# Configuração da Página
st.set_page_config(
    page_title="Projeto Solar Pampulha",
    page_icon="⚡",
    layout="wide"
)

# --- CARREGAMENTO DE DADOS ---
@st.cache_data
def load_data():
    # Caminho relativo para o CSV limpo
    path = os.path.join("data", "INMET_Pampulha_Limpo.csv")
    df = pd.read_csv(path)
    df['data_hora_local'] = pd.to_datetime(df['data_hora_local'])
    df['mes'] = df['data_hora_local'].dt.month
    df['hora'] = df['data_hora_local'].dt.hour
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}. Certifique-se de que o arquivo está em data/INMET_Pampulha_Limpo.csv")
    df = pd.DataFrame()

# --- SIDEBAR DE NAVEGAÇÃO ---
st.sidebar.title("☀️ Menu de Navegação")
aba = st.sidebar.radio("Escolha uma seção:", 
                         ["Página Inicial", "Análise de Dados (Insights)", "Preditor de Radiação"])

st.sidebar.markdown("---")
st.sidebar.info("""
**Squad:**
- Emmanuel Magalhães (Data Prep)
- Felipe Pereira (EDA & ML)
- Mateus Rabelo (Viz & Ops)
""")

# --- PÁGINA INICIAL ---
if aba == "Página Inicial":
    st.title("⚡ Projeto Solar Pampulha: Predição de Potencial Energético")
    st.markdown("""
    Este dashboard apresenta os resultados da análise preditiva focada na geração de energia fotovoltaica 
    na região da **Pampulha, Belo Horizonte (Estação A521 - INMET)**.
    
    ### 🎯 Objetivos
    * **Análise Climática:** Identificar fatores que influenciam a incidência solar.
    * **Modelo Preditivo:** Estimar a Radiação Global via Machine Learning.
    * **Dashboard:** Interface reprodutível para exploração de dados.
    """)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Dataset", "INMET 2025")
    col2.metric("Localização", "Pampulha, BH")
    col3.metric("Modelo", "Random Forest")

    if not df.empty:
        st.subheader("Amostra dos Dados Processados")
        st.dataframe(df.head(10), use_container_width=True)

# --- ABA DE ANÁLISE (INSIGHTS) ---
elif aba == "Análise de Dados (Insights)":
    st.title("📊 Insights e Visualizações")
    
    if not df.empty:
        # Insight 1: Ciclo Diário
        st.subheader("1. O Ciclo Solar e a Resposta Térmica")
        fig_ciclo = px.line(
            df.groupby('hora')[['radiacao_global', 'temp_ar']].mean().reset_index(),
            x='hora', y=['radiacao_global', 'temp_ar'],
            labels={'value': 'Valor', 'hora': 'Hora do Dia'},
            title="Média Horária: Radiação vs Temperatura",
            color_discrete_sequence=["#FFD700", "#FF4500"]
        )
        st.plotly_chart(fig_ciclo, use_container_width=True)
        st.info("💡 A temperatura costuma ter um 'atraso' em relação ao pico de radiação, confirmando a resposta térmica da atmosfera.")

        # Insight 2: O Papel da Umidade
        st.subheader("2. Umidade como 'Freio' da Radiação")
        fig_corr = px.scatter(
            df[df['radiacao_global'] > 0].sample(1000), 
            x="umidade_relativa", y="radiacao_global", 
            color="temp_ar",
            title="Correlação: Umidade vs Radiação (Amostra)",
            labels={'umidade_relativa': 'Umidade (%)', 'radiacao_global': 'Radiação (Kj/m²)'},
            color_continuous_scale=px.colors.sequential.YlOrRd
        )
        st.plotly_chart(fig_corr, use_container_width=True)
        st.warning("💡 Note como picos de umidade (>80%) limitam severamente a radiação máxima, agindo como um indicador de nebulosidade.")

# --- ABA DE PREDIÇÃO ---
elif aba == "Preditor de Radiação":
    st.title("🤖 Predição de Potencial Solar")
    st.markdown("Insira os dados meteorológicos atuais para estimar a radiação global esperada.")

    with st.form("form_predicao"):
        col1, col2 = st.columns(2)
        
        with col1:
            mes = st.slider("Mês do Ano", 1, 12, 6)
            hora = st.slider("Hora (0-23)", 0, 23, 12)
            temp = st.number_input("Temperatura do Ar (°C)", value=25.0)
        
        with col2:
            umid = st.number_input("Umidade Relativa (%)", value=50.0)
            pres = st.number_input("Pressão Atmosférica (mB)", value=920.0)
            vent = st.number_input("Vento - Rajada (m/s)", value=2.0)
        
        btn_prever = st.form_submit_button("Calcular Radiação Estimada")

    if btn_prever:
        # Chama a função do seu arquivo previsao.py
        resultado = prever_potencial_solar(hora, temp, umid, pres, vent, mes)
        
        if isinstance(resultado, str):
            st.error(resultado)
        else:
            st.success(f"### Radiação Estimada: {resultado} Kj/m²")
            
            # Feedback visual do resultado
            if resultado < 100:
                st.info("Potencial Baixo (Céu muito nublado ou período noturno).")
            elif resultado < 1500:
                st.warning("Potencial Médio (Parcialmente nublado ou transição).")
            else:
                st.balloons()
                st.info("Potencial Alto (Céu limpo, excelente para geração fotovoltaica).")