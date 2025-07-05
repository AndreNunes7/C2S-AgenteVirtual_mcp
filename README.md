# Desafio Técnico – Sistema de Busca de Veículos

Este projeto é uma solução completa para o desafio técnico da vaga de Desenvolvedor Python na C2S. Implementa uma aplicação de terminal inteligente que permite buscar veículos utilizando filtros avançados através de um agente virtual com processamento de linguagem natural.

## Características Principais

- **Agente Virtual Inteligente**: Interface conversacional que processa linguagem natural usando Google Gemini API
- **Arquitetura Cliente-Servidor**: Protocolo MCP (Model Context Protocol) via sockets TCP
- **Banco de Dados Relacional**: Modelo de dados robusto com mais de 10 atributos por veículo
- **Geração de Dados Fictícios**: População automática com 100+ veículos usando biblioteca Faker
- **Testes Automatizados**: Cobertura completa com testes unitários
- **Busca Avançada**: Filtros por marca, modelo, ano, preço, cor, quilometragem e muito mais

## Tecnologias Utilizadas

- **Python 3.8+**: Linguagem principal
- **SQLAlchemy**: ORM para banco de dados
- **SQLite**: Banco de dados embarcado
- **Google Gemini API**: Processamento de linguagem natural
- **Faker**: Geração de dados fictícios
- **Pytest**: Framework de testes
- **Socket TCP**: Comunicação cliente-servidor

## Arquitetura do Sistema

O sistema é composto por quatro componentes principais:

1. **Agente Virtual**: Interface conversacional que interage com o usuário
2. **Servidor MCP**: Processa consultas e filtros de busca
3. **Cliente MCP**: Envia requisições ao servidor
4. **Banco de Dados**: Armazena informações dos veículos

## Estrutura do Projeto

```
agente_buscaVeiculos/
├── config/
│   └── veiculos.json            # Configurações de marcas, modelos e opcionais
├── src/
│   ├── agent/
│   │   ├── __init__.py
│   │   └── agente_virtual.py    # Lógica do agente virtual com integração Gemini
│   ├── database/
│   │   ├── __init__.py
│   │   ├── conexao.py           # Conexão com banco de dados
│   │   └── populaBD.py          # Script para popular banco com dados fictícios
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── cliente.py           # Cliente MCP para enviar filtros
│   │   └── servidor.py          # Servidor MCP para processar consultas
│   ├── models/
│   │   ├── __init__.py
│   │   └── veiculos.py          # Modelos SQLAlchemy para veículos e opcionais
│   └── utils/
│       ├── __init__.py
│       └── util.py              # Funções utilitárias
├── tests/
│   ├── __init__.py
│   ├── test_agente_virtual.py   # Testes do agente virtual
│   ├── test_populaBD.py         # Testes da geração de dados
│   ├── test_mcp.py              # Testes do cliente MCP
│   └── test_servidor.py         # Testes do servidor MCP
├── .env                         # Variáveis de ambiente
├── .gitignore                   # Arquivos ignorados pelo Git
├── requirements.txt             # Dependências do projeto
└── README.md                    # Documentação do projeto
```

## Pré-requisitos

- **Python**: Versão 3.8 ou superior
- **Chave API**: Google Gemini API para processamento de linguagem natural
- **Dependências**: Listadas em `requirements.txt`

## Instalação

### 1. Clonar o Repositório

```bash
git clone https://github.com/seu-usuario/agente_buscaVeiculos.git
cd agente_buscaVeiculos
```

### 2. Criar Ambiente Virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
GEMINI_API_KEY=sua_chave_api_aqui
DB_URL=sqlite:///bancoBD.db
MCP_HOST=localhost
MCP_PORT=5050
```

## Como Usar

### 1. Popular o Banco de Dados

Execute o script para gerar 100 veículos fictícios:

```bash
cd agente_buscaVeiculos
python -m src.database.populaBD
```

Este comando criará veículos com atributos variados no banco de dados e exibirá um resumo no terminal.

### 2. Iniciar o Servidor MCP

Em um terminal separado, execute:

```bash
python -m src.mcp.servidor
```

O servidor será iniciado em `localhost:5050` e ficará aguardando conexões.

### 3. Iniciar o Agente Virtual

Em outro terminal, execute:

```bash
python -m src.agent.agente_virtual
```

O agente estará pronto para interagir. Digite `parar` para sair da aplicação.

## Exemplos de Uso




## Executar Testes

```bash
pytest tests/ --cov=src 
```






