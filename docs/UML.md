# Diagramas UML - Projeto Solar Pampulha

## 1. Diagrama de Sequência (Comportamental)
Este diagrama ilustra a interação em tempo real entre o usuário (Morador/Investidor), a interface do Dashboard e o modelo de Machine Learning exportado.
```mermaid
sequenceDiagram
    autonumber
    actor U as Morador/Investidor
    participant S as App (Streamlit)
    participant P as Script (previsao.py)
    participant M as Cérebro (Random Forest .pkl)

    U->>S: Insere Condições (Temp, Umidade, etc.)
    U->>S: Clica em Simular (ou interage com sliders)
    
    S->>P: Chama função prever_potencial_solar()
    activate P
    
    P->>M: joblib.load('modelo_solar.pkl')
    activate M
    M-->>P: Instancia Objeto do Modelo
    deactivate M
    
    P->>M: model.predict(dados_formatados)
    activate M
    M-->>P: Retorna Predição Contínua (Kj/m²)
    deactivate M
    
    P-->>S: Retorna Valor Final
    deactivate P

    alt Predição > 2200
        S-->>U: Renderiza UI: "Alta Eficiência " 
    else Predição > 1200
        S-->>U: Renderiza UI: "Eficiência Média " 
    else
        S-->>U: Renderiza UI: "Baixa Eficiência " 
    end
```
## 2. Diagrama de Atividades (Fluxo de Processamento)
Mapeamento das ações do sistema divididas entre a Interface do Usuário e o Processamento de Dados.
```mermaid
flowchart TD
    subgraph Frontend [Interface Streamlit]
        A([Início da Sessão]) --> B{Escolha de Navegação}
        B -->|Tempo Real| C[Preencher Parâmetros Climáticos]
        B -->|Investimento| D[Acessar Calculadora de ROI]
        
        C --> E[Disparar Previsão]
        D --> F[Visualizar Gráfico Sazonal]
        
        J[Exibir Métrica na Tela] --> K([Fim da Interação])
    end

    subgraph Backend [Lógica e Modelagem]
        E --> G[Formatar DataFrame de Entrada]
        G --> H[Injetar no Modelo Random Forest]
        H --> I[Aplicar Regras de Negócio/Classificação]
        I --> J
    end
```
