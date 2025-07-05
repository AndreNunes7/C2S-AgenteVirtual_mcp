# Desafio Técnico – Busca de Veículos

Este projeto é uma solução para o desafio técnico da vaga de Desenvolvedor Python na C2S. Ele implementa uma aplicação de terminal que permite buscar veículos com base em filtros (marca, modelo, ano, preço, etc.) por meio de um agente virtual com suporte a linguagem natural. A aplicação utiliza um protocolo cliente-servidor (MCP) via sockets TCP e um banco de dados relacional para armazenar os dados dos veículos.

## Visão Geral

O projeto é composto por:

- **Modelagem de Dados**: Esquema de banco de dados para representar veículos com mais de 10 atributos (marca, modelo, ano, preço, etc.).
- **População de Dados**: Script para gerar 100+ veículos fictícios usando a biblioteca `Faker`.
- **Protocolo MCP**: Comunicação cliente-servidor para consultar veículos com base em filtros.
- **Agente Virtual**: Interface no terminal que interage com o usuário, processa linguagem natural via Google Gemini API e exibe resultados de forma amigável.
- **Testes Automatizados**: Testes unitários para validar as principais funcionalidades.

## Estrutura do Projeto
```
agente_buscaVeiculos/
├── config/
│   └── veiculos.json            # Configurações de marcas, modelos, opcionais, etc.
├── src/
│   ├── agent/
│   │   ├── init.py
│   │   └── agente_virtual.py    # Lógica do agente virtual com integração ao Gemini
│   ├── database/
│   │   ├── init.py
│   │   ├── conexao.py           # Conexão com o banco de dados
│   │   └── populaBD.py         # Script para popular o banco com dados fictícios
│   ├── mcp/
│   │   ├── init.py
│   │   ├── cliente.py           # Cliente MCP para enviar filtros ao servidor
│   │   └── servidor.py          # Servidor MCP para processar consultas
│   ├── models/
│   │   ├── init.py
│   │   └── veiculos.py         # Modelos SQLAlchemy para veículos e opcionais
│   ├── utils/
│   │   ├── init.py
│   │   └── util.py             # Funções utilitárias
├── tests/
│   ├── init.py
│   ├── test_agente_virtual.py   # Testes do agente virtual
│   ├── test_populaBD.py        # Testes da geração de dados
│   ├── test_mcp.py             # Testes do cliente MCP
│   └── test_servidor.py        # Testes do servidor MCP
├── .env                        # Variáveis de ambiente (ex.: DB_URL, GEMINI_API_KEY)
├── .gitignore                  # Arquivos e pastas ignorados pelo Git
├── requirements.txt            # Dependências do projeto
└── README.md                   # Este arquivo

```


## Pré-requisitos

- **Python**: 3.8 ou superior
- **Banco de Dados**: sqlite (ou outro compatível com SQLAlchemy)
- **API Key**: Chave para a API do Google Gemini (para processamento de linguagem natural)
- **Dependências**: Listadas em `requirements.txt`

## Instalação

1. **Clone o repositório**:
   ```bash
   git clone https://github.com/seu-usuario/agente_buscaVeiculos.git
   cd agente_buscaVeiculos```

2. **Crie e ative um ambiente virtual:**
   ``` bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    venv\Scripts\activate     # Windows
   ```
3. **Instale as dependências:**
  ``` bash
     pip install -r requirements.txt
  ```

4. 
   ``` bash
    GEMINI_API_KEY: <SUA API KEY>
    DB_URL=sqlite:///bancoBD.db
    MCP_HOST=localhost
    MCP_PORT=5050
   ```

**Como Usar**
> Entre na pasta:  `cd .\agente_buscaVeiculos\` 

1. Popular o Banco de Dados Execute o script para gerar 100 veículos fictícios:
  ```bash
   python -m src.database.populaBD
  ```
- Isso criará veículos com atributos variados (marca, modelo, ano, preço, etc.) no banco de dados.
- A saída no terminal mostrará os veículos gerados.


2. Iniciar o Servidor MCP
Execute o servidor para processar as consultas:
  ```bash
    python -m src.mcp.servidor
  ```
- O servidor será iniciado em localhost:5050 (ou conforme configurado no .env).
- Mantenha o servidor rodando em um terminal separado.


3. Iniciar o Agente Virtual
Execute o agente para interagir com o usuário:
  ```bash
    python -m src.agent.agente_virtual
  ```
O agente perguntará sobre suas preferências de veículo (ex.: marca, modelo, preço) ou processará entradas em linguagem natural.
Digite parar para sair.



4. Exemplos de Uso
- Entrada em linguagem natural: "Quero um Toyota Corolla 2020 vermelho até 80 mil"
  - O agente extrairá filtros (marca: Toyota, modelo: Corolla, ano: 2020, cor: Vermelho, preco_max: 80000) e exibirá resultados.

- Interação guiada: Responda às perguntas do agente (ex.: "Qual a marca de carro você está procurando?").
- Resultados: O agente exibe até 10 veículos compatíveis, com detalhes como marca, modelo, ano, preço, quilometragem, etc.

5. Executar Testes
Execute os testes automatizados para validar as funcionalidades:
  ```bash
    pytest tests/ --cov=src
  ```



