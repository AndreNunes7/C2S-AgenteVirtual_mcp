# 🚗 Desafio Técnico – Busca de Veículos

# Solução para o desafio técnico da vaga de Desenvolvedor Python na C2S.
# Aplicação de terminal para buscar veículos com filtros (marca, modelo, ano, preço, etc.)
# usando linguagem natural. Arquitetura cliente-servidor (MCP) via sockets TCP e banco relacional.

# 📦 Visão Geral
# - 📊 Modelagem de Dados: Esquema com >10 atributos para veículos.
# - 🔥 População de Dados: Geração de 100+ veículos fictícios com Faker.
# - 🌐 Protocolo MCP: Comunicação cliente-servidor via JSON/TCP.
# - 🧠 Agente Virtual: Interface no terminal com Google Gemini API.
# - ✅ Testes Automatizados: pytest + coverage.

# 📁 Estrutura do Projeto
# agente_buscaVeiculos/
# ├── config/
# │   └── veiculos.json
# ├── src/
# │   ├── agent/agente_virtual.py
# │   ├── database/conexao.py
# │   ├── database/populaBD.py
# │   ├── mcp/cliente.py
# │   ├── mcp/servidor.py
# │   ├── models/veiculos.py
# │   └── utils/util.py
# ├── tests/
# │   ├── test_agente_virtual.py
# │   ├── test_populaBD.py
# │   ├── test_mcp.py
# │   └── test_servidor.py
# ├── .env
# ├── requirements.txt
# └── README.md

# 🚀 Pré-requisitos
# - Python 3.8+
# - SQLite (ou outro compatível com SQLAlchemy)
# - Google Gemini API Key
# - Dependências em requirements.txt

# ⚙️ Instalação

# Clone o repositório
git clone https://github.com/seu-usuario/agente_buscaVeiculos.git
cd agente_buscaVeiculos

# Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# Instale as dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
echo "GEMINI_API_KEY=<SUA_API_KEY>" >> .env
echo "DB_URL=sqlite:///bancoBD.db" >> .env
echo "MCP_HOST=localhost" >> .env
echo "MCP_PORT=5050" >> .env

# 💻 Como Usar

# 1️⃣ Popular o Banco de Dados
python -m src.database.populaBD

# 2️⃣ Iniciar o Servidor MCP
python -m src.mcp.servidor

# 3️⃣ Rodar o Agente Virtual
python -m src.agent.agente_virtual

# 📝 Exemplos de uso:
# Entrada: "Quero um Honda Civic 2020 branco até 100 mil"
# Saída: Lista de veículos compatíveis com detalhes.

# 4️⃣ Executar Testes
pytest tests/ --cov=src

# 🏗️ Arquitetura
# - models/veiculos.py: SQLAlchemy com validações e índices.
# - database/populaBD.py: Faker para dados realistas (preço, km, ano).
# - mcp/{cliente,servidor}.py: JSON via TCP com threading.
# - agent/agente_virtual.py: Gemini API + interação natural.
# - tests/: pytest com cobertura de comunicação e dados.

# 📦 Dependências principais
# - sqlalchemy
# - faker
# - google-generativeai
# - tenacity
# - pytest / pytest-cov
