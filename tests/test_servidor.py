import pytest
from ..src.mcp.servidor import MCPServidor
from ..src.models.veiculos import Veiculo, Opcional, TipoCombustivel, TipoTransmissao, CondicaoVeiculo
from ..src.database.conexao import connectDb
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, Mock
import json

@pytest.fixture
def session():
    engine = connectDb()
    Session = sessionmaker(bind=engine)
    return Session()

def test_processar_filtros_marca(session):
    servidor = MCPServidor()
    filtros = {"marca": "Toyota"}
    with session as s:
        veiculo = Veiculo(
            marca="Toyota",
            modelo="Corolla",
            ano_fabricacao=2020,
            ano_modelo=2020,
            cor="Branco",
            combustivel=TipoCombustivel.FLEX,
            transmissao=TipoTransmissao.AUTOMATICO,
            condicao=CondicaoVeiculo.SEMINOVO,
            preco=80000.0,
            motor="2.0",
            quilometragem=30000,
            portas=4,
            cidade="São Paulo",
            estado="SP"
        )
        s.add(veiculo)
        s.commit()
        query = servidor._processar_filtros(filtros, s)
        resultados = query.all()
        assert len(resultados) >= 1
        assert resultados[0].marca == "Toyota"