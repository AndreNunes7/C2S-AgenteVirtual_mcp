# mcp/servidor.py
import json
import socket
import threading
from sqlalchemy.orm import sessionmaker
from ..models.veiculos import Base, Veiculo, Opcional, TipoCombustivel, TipoTransmissao, CondicaoVeiculo
from ..database.conexao import connectDb


class MCPServidor:
    def __init__(self, host='localhost', port=5050):
        self.host = host
        self.port = port
        self.engine = connectDb()
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def _processar_filtros(self, filtros, session):

        query = session.query(Veiculo)

        if 'marca' in filtros and filtros['marca']:
            query = query.filter(Veiculo.marca.ilike(f"%{filtros['marca']}%"))

        if 'modelo' in filtros and filtros['modelo']:
            query = query.filter(Veiculo.modelo.ilike(f"%{filtros['modelo']}%"))

        if 'ano' in filtros and filtros['ano']:
            try:
                ano = int(filtros['ano'])
                query = query.filter(Veiculo.ano_modelo.between(ano - 2, ano + 2))
            except ValueError:
                print(f"Ano inválido: {filtros['ano']}")

        if 'combustivel' in filtros and filtros['combustivel']:
            try:
                combustivel = TipoCombustivel(filtros['combustivel'])
                query = query.filter(Veiculo.combustivel == combustivel)
            except ValueError:
                print(f"Combustível inválido: {filtros['combustivel']}")

        if 'preco_min' in filtros and filtros['preco_min']:
            try:
                query = query.filter(Veiculo.preco >= float(filtros['preco_min']))
            except ValueError:
                print(f"Preço mínimo inválido: {filtros['preco_min']}")

        if 'preco_max' in filtros and filtros['preco_max']:
            try:
                query = query.filter(Veiculo.preco <= float(filtros['preco_max']))
            except ValueError:
                print(f"Preço máximo inválido: {filtros['preco_max']}")

        if 'cor_evitar' in filtros and filtros['cor_evitar']:
            query = query.filter(Veiculo.cor.ilike(f"%{filtros['cor_evitar']}%") == False)

        if 'motor' in filtros and filtros['motor']:
            query = query.filter(Veiculo.motor == filtros['motor'])

        if 'opcionais' in filtros and filtros['opcionais']:
            opcionais_lista = filtros['opcionais']
            if isinstance(opcionais_lista, list):
                for opcional_nome in opcionais_lista:
                    query = query.filter(Veiculo.opcionais.any(Opcional.nome.ilike(f"%{opcional_nome}%")))
            else:
                print(f"Opcionais deve ser uma lista: {opcionais_lista}")

        if 'portas' in filtros and filtros['portas']:
            try:
                query = query.filter(Veiculo.portas == int(filtros['portas']))
            except ValueError:
                print(f"Portas inválido: {filtros['portas']}")

        if 'quilometragem_max' in filtros and filtros['quilometragem_max']:
            try:
                query = query.filter(Veiculo.quilometragem <= float(filtros['quilometragem_max']))
            except ValueError:
                print(f"Quilometragem máxima inválida: {filtros['quilometragem_max']}")

        if 'condicao' in filtros and filtros['condicao']:
            try:
                condicao = CondicaoVeiculo(filtros['condicao'])
                query = query.filter(Veiculo.condicao == condicao)
            except ValueError:
                print(f"Condição inválida: {filtros['condicao']}")

        if 'transmissao' in filtros and filtros['transmissao']:
            try:
                transmissao = TipoTransmissao(filtros['transmissao'])
                query = query.filter(Veiculo.transmissao == transmissao)
            except ValueError:
                print(f"Transmissão inválida: {filtros['transmissao']}")

        if 'cidade' in filtros and filtros['cidade']:
            query = query.filter(Veiculo.cidade.ilike(f"%{filtros['cidade']}%"))

        if 'estado' in filtros and filtros['estado']:
            query = query.filter(Veiculo.estado.ilike(f"%{filtros['estado']}%"))

        return query



    def conexaoCliente(self, client_socket, endereco):
        print(f'Conexão recebida de {endereco}')

        try:
            data = client_socket.recv(8192).decode('utf-8')
            if not data:
                print("Cliente fechou conexão sem enviar dados")
                resposta = json.dumps({"erro": "Nenhum dado recebido"}, ensure_ascii=False)
                client_socket.sendall(resposta.encode('utf-8'))
                return

            try:
                filtros = json.loads(data)
                print(f"Filtros recebidos: {filtros}")
            except json.JSONDecodeError as e:
                print(f"Erro ao decodificar JSON: {e}")
                resposta = json.dumps({"erro": "JSON inválido"}, ensure_ascii=False)
                client_socket.sendall(resposta.encode('utf-8'))
                return


            with self.Session() as session:
                try:
                    query = self._processar_filtros(filtros, session)


                    query = query.order_by(Veiculo.preco.asc())


                    limite = filtros.get('limite', 50)
                    try:
                        limite = int(limite)
                    except ValueError:
                        print(f"Limite inválido, usando padrão: {limite}")
                        limite = 50

                    veiculos = query.limit(limite).all()


                    resultados = []
                    for veiculo in veiculos:
                        try:
                            resultado = veiculo.to_dict()
                            resultados.append(resultado)
                        except Exception as e:
                            print(f"Erro ao converter veículo para dicionário: {e}")
                            continue

                    resposta = json.dumps({"status": "ok", "resultados": resultados}, ensure_ascii=False)
                    client_socket.sendall(resposta.encode('utf-8'))
                    print(f"Enviados {len(resultados)} veículos para {endereco}")

                except Exception as e:
                    print(f"Erro ao processar consulta: {e}")
                    resposta = json.dumps({"erro": f"Erro na consulta: {str(e)}"}, ensure_ascii=False)
                    client_socket.sendall(resposta.encode('utf-8'))


        except Exception as e:
            print(f"Erro na conexão com {endereco}: {e}")
            resposta = json.dumps({"erro": f"Erro no servidor: {str(e)}"}, ensure_ascii=False)
            client_socket.sendall(resposta.encode('utf-8'))

        finally:
            try:
                client_socket.close()
            except Exception as e:
                print(f"Erro ao fechar socket: {e}")


    def iniciar(self):

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            print(f'Servidor MCP rodando em {self.host}:{self.port}')



            while True:
                client_socket, endereco = server_socket.accept()
                client_thread = threading.Thread(target=self.conexaoCliente, args=(client_socket, endereco))
                client_thread.daemon = True
                client_thread.start()



        except Exception as e:
            print(f"Erro no servidor: {e}")
        finally:
            server_socket.close()
            print("Servidor encerrado")



if __name__ == '__main__':
    servidor = MCPServidor()
    servidor.iniciar()