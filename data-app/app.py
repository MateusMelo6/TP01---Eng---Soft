import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import datetime
import os

# 1. Configuração da Página
st.set_page_config(page_title="Preditor Solar Pampulha", layout="wide")

# 2. Carregamento e Treinamento do Modelo (Cacheado para performance)
@st.cache_resource
def carregar_e_treinar_modelo():
    try:

        # 1. Descobre o caminho da pasta onde este arquivo app.py está salvo
        diretorio_atual = os.path.dirname(os.path.abspath(__file__))

        # 2. Constrói o caminho completo para o CSV
        caminho_csv = os.path.join(diretorio_atual, 'INMET_Pampulha_Limpo.csv')

        # 3. Carrega o arquivo usando o caminho absoluto
        df = pd.read_csv(caminho_csv)
        
        # Converte a data para extrair Hora e Mês (essenciais para o modelo)
        df['data_hora_local'] = pd.to_datetime(df['data_hora_local'])
        df['hora'] = df['data_hora_local'].dt.hour
        df['mes'] = df['data_hora_local'].dt.month
        
        # Define as variáveis que o modelo usa (Features) e o que queremos prever (Target)
        features = ['hora', 'temp_ar', 'umidade_relativa', 'pressao_atm', 'vento_rajada', 'mes']
        target = 'radiacao_global'
        
        X = df[features]
        y = df[target]
        
        # Treina o modelo Random Forest
        # Usamos parâmetros que equilibram velocidade e precisão
        modelo = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
        modelo.fit(X, y)
        
        return modelo
    except Exception as e:
        st.error(f"Erro ao processar dados ou treinar modelo: {e}")
        return None

# Inicializa o modelo
modelo_solar = carregar_e_treinar_modelo()

# 3. Interface do Usuário (Sidebar para Inputs)
st.title("⚡ Predição de Potencial Solar - Pampulha")
st.markdown("""
Esta ferramenta utiliza um modelo de **Machine Learning (Random Forest)** treinado com dados reais da estação do INMET 
para estimar a radiação global com base nas condições climáticas atuais.
""")

st.sidebar.header("📥 Parâmetros Climáticos")

with st.sidebar:
    hora = st.slider("Hora do Dia", 0, 23, 12)
    mes = st.selectbox("Mês", list(range(1, 13)), index=datetime.datetime.now().month - 1)
    temp = st.number_input("Temperatura do Ar (°C)", value=25.0)
    umidade = st.number_input("Umidade Relativa (%)", value=60.0)
    pressao = st.number_input("Pressão Atmosférica (mB)", value=920.0)
    vento = st.number_input("Rajada de Vento (m/s)", value=2.0)

# 4. Lógica de Predição e Exibição
if modelo_solar:
    # Organiza os dados para o formato que o modelo espera
    dados_entrada = pd.DataFrame([{
        'hora': hora,
        'temp_ar': temp,
        'umidade_relativa': umidade,
        'pressao_atm': pressao,
        'vento_rajada': vento,
        'mes': mes
    }])

    # Realiza a predição
    predicao = modelo_solar.predict(dados_entrada)[0]
    
    # Se a radiação for muito baixa (ex: noite), ajustamos para zero
    valor_final = max(0, round(predicao, 2))

    # Exibição dos Resultados
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(label="Radiação Estimada (Kj/m²)", value=f"{valor_final} Kj/m²")
        
    with col2:
        if valor_final > 2000:
            st.success("☀️ Potencial Solar: **Muito Alto**")
        elif valor_final > 1000:
            st.info("⛅ Potencial Solar: **Moderado**")
        else:
            st.warning("☁️ Potencial Solar: **Baixo**")

    # Gráfico simples de contexto
    st.divider()
    st.subheader("Configurações Selecionadas")
    st.write(dados_entrada)

else:
    st.error("O modelo não pôde ser carregado. Verifique se o arquivo 'INMET_Pampulha_Limpo.csv' está na mesma pasta.")