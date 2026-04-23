import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestRegressor
import datetime
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Solar Analytics Pampulha",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilização Customizada CSS
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    [data-testid="stSidebar"] { background-color: #1e293b; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- CARREGAMENTO DE DADOS E MODELO ---
@st.cache_data
def carregar_dados():
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_csv = os.path.join(diretorio_atual, 'INMET_Pampulha_Limpo.csv')
    df = pd.read_csv(caminho_csv)
    df['data_hora_local'] = pd.to_datetime(df['data_hora_local'])
    df['mes'] = df['data_hora_local'].dt.month
    df['hora'] = df['data_hora_local'].dt.hour
    return df

@st.cache_resource
def treinar_modelo(df):
    features = ['hora', 'temp_ar', 'umidade_relativa', 'pressao_atm', 'vento_rajada', 'mes']
    target = 'radiacao_global'
    X = df[features]
    y = df[target]
    modelo = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
    modelo.fit(X, y)
    return modelo

# Inicialização
df_solar = carregar_dados()
modelo_rf = treinar_modelo(df_solar)

# --- NAVEGAÇÃO LATERAL ---
st.sidebar.title("⚡ Solar Ops")
pagina = st.sidebar.radio("Navegação", ["Predição em Tempo Real", "Análise de Investimento", "Insights do Projeto"])

# --- PÁGINA 1: PREDIÇÃO (História do Morador) ---
if pagina == "Predição em Tempo Real":
    st.header("🔮 Simulador de Eficiência Diária")
    st.subheader("Insira a previsão para saber o potencial do seu sistema")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        st.info("Configurações do Dia")
        data_amanha = datetime.date.today() + datetime.timedelta(days=1)
        mes_ref = st.selectbox("Mês de Referência", list(range(1, 13)), index=data_amanha.month - 1)
        hora_ref = st.slider("Hora da Previsão", 6, 18, 12)

    with col2:
        st.write("#### Condições Climáticas Estimadas")
        c1, c2 = st.columns(2)
        temp = c1.number_input("Temperatura (°C)", value=25.0)
        umid = c2.number_input("Umidade (%)", value=60.0)
        pres = c1.number_input("Pressão (mB)", value=920.0)
        vent = c2.number_input("Vento/Rajada (m/s)", value=3.5)

    # Lógica de Predição
    entrada = pd.DataFrame([[hora_ref, temp, umid, pres, vent, mes_ref]], 
                          columns=['hora', 'temp_ar', 'umidade_relativa', 'pressao_atm', 'vento_rajada', 'mes'])
    pred = max(0, modelo_rf.predict(entrada)[0])

    with col3:
        st.write("#### Resultado")
        st.metric("Radiação Estimada", f"{pred:.2f} Kj/m²")
        if pred > 2200:
            st.success("Alta Eficiência ☀️")
        elif pred > 1200:
            st.warning("Eficiência Média ⛅")
        else:
            st.error("Baixa Eficiência ☁️")

# --- PÁGINA 2: INVESTIMENTO (História do Investidor) ---
elif pagina == "Análise de Investimento":
    st.header("📉 Sazonalidade e Retorno (ROI)")
    st.markdown("Visualize o comportamento histórico para planejar seu investimento.")

    # Agrupamento mensal para ver a queda
    df_mensal = df_solar.groupby('mes')['radiacao_global'].mean().reset_index()
    df_mensal['mes_nome'] = df_mensal['mes'].apply(lambda x: datetime.date(2025, x, 1).strftime('%B'))

    fig_sazonal = px.line(df_mensal, x='mes_nome', y='radiacao_global', 
                         title="Média de Radiação por Mês (Pampulha)",
                         labels={'radiacao_global': 'Radiação Média (Kj/m²)', 'mes_nome': 'Mês'},
                         markers=True, line_shape="spline", color_discrete_sequence=['#f1c40f'])
    
    st.plotly_chart(fig_sazonal, use_container_width=True)

    col_inv1, col_inv2 = st.columns(2)
    with col_inv1:
        st.write("### Meses Críticos")
        st.write("Note que nos meses de **Inverno (Junho/Julho)**, o potencial cai significativamente devido à inclinação solar, o que deve ser considerado no cálculo de payback.")
    
    with col_inv2:
        mes_min = df_mensal.loc[df_mensal['radiacao_global'].idxmin()]
        st.error(f"Menor Potencial: {mes_min['mes_nome']} ({mes_min['radiacao_global']:.2f} Kj/m²)")

# --- PÁGINA 3: INSIGHTS (Análise dos Notebooks) ---
elif pagina == "Insights do Projeto":
    st.header("🔬 Metodologia e Desempenho do Modelo")
    
    tab1, tab2 = st.tabs(["Importância das Variáveis", "Performance (Baseline vs RF)"])

    with tab1:
        st.subheader("O que mais afeta a geração?")
        # Dados extraídos do notebook 02 e 04
        importancias = pd.DataFrame({
            'Atributo': ['Hora do Dia', 'Temperatura', 'Umidade', 'Vento', 'Pressão'],
            'Impacto': [0.55, 0.25, 0.12, 0.05, 0.03]
        }).sort_values(by='Impacto', ascending=True)

        fig_imp = px.bar(importancias, x='Impacto', y='Atributo', orientation='h',
                        title="Feature Importance (Baseado no Random Forest)",
                        color_discrete_sequence=['#3498db'])
        st.plotly_chart(fig_imp, use_container_width=True)
        st.info("💡 A Umidade atua como o principal 'freio' da radiação, confirmando as análises exploratórias.")

    with tab2:
        st.subheader("Evolução do Modelo")
        c_m1, c_m2 = st.columns(2)
        c_m1.metric("R² Regressão Linear (Baseline)", "0.78")
        c_m2.metric("R² Random Forest (Final)", "0.941", delta="20% melhoria")
        
        st.markdown("""
        **Conclusões Técnicas:**
        - O modelo Random Forest conseguiu capturar as quedas bruscas de radiação causadas por nuvens.
        - A filtragem do período diurno (06h-18h) nos notebooks foi essencial para evitar viés noturno.
        """)