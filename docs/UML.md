# Diagramas UML - Projeto Solar Pampulha

## 1. Diagrama de Componentes (Arquitetura)
Aqui está a arquitetura do nosso pipeline de dados:

```mermaid
graph TD
    subgraph "Camada de Dados"
        A[CSV Bruto INMET] --> B[Script de Limpeza]
        B --> C[(Dataset Processado)]
    end

    subgraph "Camada de Inteligência"
        C --> D[Notebook de Modelagem]
        D --> E[Modelo Random Forest .pkl]
    end

    subgraph "Camada de Aplicação"
        E --> F[App Streamlit]
        G[Entrada do Usuário] --> F
        F --> H[Dashboard de Predição]
    end
```

## 2. Diagrama de Atividades (Fluxo)
Aqui está o passo a passo de como os dados se movem:

```mermaid
stateDiagram-v2
    [*] --> Carregamento
    Carregamento --> Limpeza: Pular Cabeçalho
    Limpeza --> Tratamento: Zerar Radiação Noturna
    Tratamento --> Filtro: Período Diurno (06h-18h)
    Filtro --> Treinamento: Random Forest
    Treinamento --> Exportação: Joblib/Pickle
    Exportação --> Dashboard: Carregar Modelo
    Dashboard --> [*]: Predição de Potencial Solar
```