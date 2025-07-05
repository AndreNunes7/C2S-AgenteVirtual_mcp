import json
import random
import os

from faker import Faker
from sqlalchemy.orm import sessionmaker
from .conexao import connectDb
from ..models.veiculos import Base, VeiculoOpcional
from datetime import datetime, timedelta
from sqlalchemy import func

from ..models.veiculos import Veiculo, TipoCombustivel, TipoTransmissao, CondicaoVeiculo, Opcional
from ..utils.util import quebra_linha

base_dir = os.path.dirname(__file__)
path = os.path.join(base_dir, '..', '..', 'config', 'veiculos.json')
path = os.path.abspath(path)

class GeraVeiculos:
    def __init__(self, path=path):
        self.faker = Faker('pt_BR')

        with open(path, 'r', encoding='utf-8') as arquivo:
            config = json.load(arquivo)
        self.marcas_modelos = config.get('marcas_modelos', {})
        self.cores_populares = config.get('cores_populares', [])
        self.motorizacoes = config.get('motorizacoes', [])
        self.cidades_estados = config.get('cidades_estados', [])
        self.opcionais = config.get('opcionais', [])
        self.precos_base = config.get('precos_base', {})





    def calcular_preco(self, marca, modelo, ano_modelo, quilometragem, condicao):

        preco_base = self.precos_base.get(marca, {}).get(modelo, 85000)

        # Faz o ajuste do valor por depreciação
        anos_uso = 2025 - ano_modelo
        depreciacao = max(0.7, 1 - (anos_uso * 0.08))  # no caso vai ser 8% ao ano
        preco_base *= depreciacao

        if quilometragem > 100000:
            preco_base *= 0.85
        elif quilometragem > 50000:
            preco_base *= 0.92

        variacao = random.uniform(0.85, 1.15)
        preco_final = preco_base * variacao

        return round(preco_final, 2)


    def gerar_veiculo(self, session):

        marca = random.choice(list(self.marcas_modelos.keys()))
        modelo = random.choice(self.marcas_modelos[marca])

        peso_anos = [1, 2, 3, 5, 8, 10, 8, 5, 3, 2, 1, 1, 1, 1, 2, 3]

        ano_modelo = random.choices(range(2010, 2026), weights=peso_anos)[0]
        ano_fabricacao = random.choice([ano_modelo - 1, ano_modelo])

        if ano_modelo >= 2024:
            condicao = random.choice([CondicaoVeiculo.NOVO, CondicaoVeiculo.SEMINOVO])
        elif ano_modelo >= 2020:
            condicao = random.choice([CondicaoVeiculo.SEMINOVO, CondicaoVeiculo.USADO])
        else:
            condicao = CondicaoVeiculo.USADO

        anos_uso = 2025 - ano_modelo

        quilometragem = random.randint(0, 5000) if condicao == CondicaoVeiculo.NOVO \
            else max(0,int(anos_uso * random.randint(12000,20000) * random.uniform(0.5, 1.5)))

        cidade, estado = random.choice(self.cidades_estados)

        combustivel = random.choices(list(TipoCombustivel), weights=[20, 5, 50, 10, 8, 5, 2])[0]

        portas = random.choice([2, 4, 5])

        transmissao = random.choice(list(TipoTransmissao))

        motor = random.choice(self.motorizacoes)

        cor = random.choice(self.cores_populares)
        num_opcionais = random.randint(3, 8)

        opcionais_selecionados = random.sample(self.opcionais, num_opcionais)
        objetos_opcionais = []

        for nome_opcional in opcionais_selecionados:
            opcional = session.query(Opcional).filter_by(nome=nome_opcional).first()

            if not opcional:
                opcional = Opcional(nome=nome_opcional)
                session.add(opcional)
            objetos_opcionais.append(opcional)

        preco = self.calcular_preco(marca, modelo, ano_modelo, quilometragem, condicao)


        veiculo = Veiculo(
            marca=marca,
            modelo=modelo,
            ano_fabricacao=ano_fabricacao,
            ano_modelo=ano_modelo,
            motor=motor,
            combustivel=combustivel,
            cor=cor,
            quilometragem=quilometragem,
            transmissao=transmissao,
            preco=preco,
            condicao=condicao,
            cidade=cidade,
            estado=estado,
            portas=portas,
            opcionais=objetos_opcionais
        )

        # print(f"Veículo gerado: {marca} {modelo} ({ano_modelo}, {condicao.value}, {preco:.2f})")
        return veiculo



    def popular_banco(self, quantidade=100):
        engine = connectDb()
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        with Session() as session:
            # LIMPAR A TABELA
            session.query(VeiculoOpcional).delete()
            session.query(Opcional).delete()
            session.query(Veiculo).delete()


            session.commit()
            veiculos = []

            for i in range(quantidade):
                veiculo = self.gerar_veiculo(session)
                veiculos.append(veiculo)

            session.bulk_save_objects(veiculos)
            session.commit()

            print(f"{quantidade} veículos gerados com sucesso")

            for veiculo in veiculos:
                print(
                    f"Marca: {veiculo.marca} \nModelo: {veiculo.modelo} \nValor: R${veiculo.preco} \nAno: {veiculo.ano_modelo} \nCondição: {veiculo.condicao.value}")

                quebra_linha()
            session.close()




        # Não quis deixar as estatisticas p nao poluir tanto a saida no terminal

        # def mostrar_estatisticas(self, sessao):
        #     print("\n Estatisticas dos dados gerados: ")
        #
        #     marcas = sessao.query(
        #         Veiculo.marca,
        #         func.count(Veiculo.id).label('quantidade')
        #     ).group_by(Veiculo.marca).order_by(func.count(Veiculo.id).desc()).all()
        #
        #     print("\n Veículos por marca:")
        #     # aqui pega o top 5
        #     for marca, qtd in marcas[:5]:
        #         print(f"   {marca}: {qtd} veículos")
        #
        #
        #     preco_min = sessao.query(func.min(Veiculo.preco)).scalar()
        #     preco_max = sessao.query(func.max(Veiculo.preco)).scalar()
        #     preco_medio = sessao.query(func.avg(Veiculo.preco)).scalar()
        #
        #     print(f"\n Faixa de preços:")
        #     print(f"   Menor: R$ {preco_min:,.2f}")
        #     print(f"   Maior: R$ {preco_max:,.2f}")
        #     print(f"   Média: R$ {preco_medio:,.2f}")



gera_veiculos = GeraVeiculos()
veiculos = gera_veiculos.popular_banco()
