import joblib
import pandas as pd
import os

def prever_potencial_solar(hora, temp_ar, umidade, pressao, vento, mes):
    """
    Função que o Dashboard vai chamar para fazer a predição.
    Recebe os dados da tela e retorna o valor estimado em Kj/m².
    """
    # 1. Tenta carregar o modelo salvo (ajusta o caminho caso necessário)
    caminho_modelo = os.path.join(os.path.dirname(__file__), 'modelo_solar.pkl')
    
    try:
        modelo = joblib.load(caminho_modelo)
    except FileNotFoundError:
        return "Erro: Arquivo do modelo (modelo_solar.pkl) não encontrado!"

    # 2. Organiza os dados exatamente na mesma ordem que o modelo foi treinado
    dados_entrada = pd.DataFrame([{
        'hora': hora,
        'temp_ar': temp_ar,
        'umidade_relativa': umidade,
        'pressao_atm': pressao,
        'vento_rajada': vento,
        'mes': mes
    }])

    # 3. Faz a previsão
    predicao = modelo.predict(dados_entrada)[0]
    
    # Retorna o valor arredondado
    return round(predicao, 2)