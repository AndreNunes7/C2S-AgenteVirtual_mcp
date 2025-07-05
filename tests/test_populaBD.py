import pytest
from ..src.database.populaBD import GeraVeiculos
from ..src.models.veiculos import Veiculo, VeiculoOpcional, Opcional
from sqlalchemy.orm import sessionmaker
from ..src.database.conexao import connectDb

@pytest.fixture
def session():
    engine = connectDb()
    Session = sessionmaker(bind=engine)
    session = Session()
    session.query(VeiculoOpcional).delete()
    session.query(Opcional).delete()
    session.query(Veiculo).delete()
    session.commit()
    yield session
    session.query(VeiculoOpcional).delete()
    session.query(Opcional).delete()
    session.query(Veiculo).delete()
    session.commit()
    session.close()

def test_gerar_veiculo(session):
    gera_veiculos = GeraVeiculos()
    veiculo = gera_veiculos.gerar_veiculo(session)
    session.commit()
    assert veiculo.marca in gera_veiculos.marcas_modelos
    assert 1980 <= veiculo.ano_modelo <= 2025
    assert veiculo.preco > 0

def test_popular_banco_quantidade(session):
    gera_veiculos = GeraVeiculos()
    gera_veiculos.popular_banco(quantidade=10)
    count = session.query(Veiculo).count()
    assert count == 10, "Deve gerar exatamente 10 veículos"