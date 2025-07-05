from sqlalchemy import Column, String, Integer, Float, Enum
from sqlalchemy.orm import declarative_base, relationship, validates, backref
from enum import Enum as PyEnum
from sqlalchemy import Index, ForeignKey

Base = declarative_base()

class TipoCombustivel(PyEnum):
    GASOLINA = "Gasolina"
    ETANOL = "Etanol"
    FLEX = "Flex"
    HIBRIDO = "Híbrido"
    DIESEL = "Diesel"
    ELETRICO = "Elétrico"
    GNV = "GNV"

class TipoTransmissao(PyEnum):
    MANUAL = "Manual"
    AUTOMATICO = "Automático"
    AUTOMATIZADO = "Automatizado"
    CVT = "CVT"

class CondicaoVeiculo(PyEnum):
    NOVO = "Novo"
    SEMINOVO = "Seminovo"
    USADO = "Usado"

class Opcional(Base):
    __tablename__ = "opcionais"
    id = Column(Integer, primary_key=True)
    nome = Column(String(50), nullable=False, unique=True)

    def __repr__(self):
        return f"<Opcional(nome='{self.nome}')>"

class Veiculo(Base):
    __tablename__ = "veiculos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    marca = Column(String(50), nullable=False)
    modelo = Column(String(100), nullable=False)
    ano_fabricacao = Column(Integer, nullable=False)
    ano_modelo = Column(Integer, nullable=False)
    cor = Column(String(30))
    combustivel = Column(Enum(TipoCombustivel), nullable=False)
    transmissao = Column(Enum(TipoTransmissao), nullable=False)
    condicao = Column(Enum(CondicaoVeiculo), nullable=False)
    preco = Column(Float, nullable=False)
    motor = Column(String(20), nullable=False)
    quilometragem = Column(Integer, default=0)
    portas = Column(Integer, default=4)
    cidade = Column(String(100))
    estado = Column(String(2))
    opcionais = relationship("Opcional", secondary="veiculo_opcional", backref=backref("veiculos", lazy="joined"))

    __table_args__ = (
        Index('idx_marca_modelo', 'marca', 'modelo'),
        Index('idx_preco', 'preco'),
        Index('idx_ano_modelo', 'ano_modelo'),
    )

    @validates('preco')
    def validate_preco(self, key, preco):
        if preco <= 0:
            raise ValueError("O preço deve ser positivo")
        return preco

    @validates('ano_modelo')
    def validate_ano_modelo(self, key, ano):
        if not (1980 <= ano <= 2026):
            raise ValueError("Ano modelo deve estar entre 1980 e 2026")
        return ano

    def to_dict(self):
        return {
            "id": self.id,
            "marca": self.marca,
            "modelo": self.modelo,
            "ano": self.ano_modelo,
            "cor": self.cor,
            "quilometragem": self.quilometragem,
            "preco": self.preco,
            "condicao": self.condicao.value,
            "cidade": self.cidade,
            "estado": self.estado,
            "opcionais": [opcional.nome for opcional in self.opcionais]
        }

class VeiculoOpcional(Base):
    __tablename__ = "veiculo_opcional"
    veiculo_id = Column(Integer, ForeignKey("veiculos.id"), primary_key=True)
    opcional_id = Column(Integer, ForeignKey("opcionais.id"), primary_key=True)