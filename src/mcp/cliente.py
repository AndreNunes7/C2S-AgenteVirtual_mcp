# mcp/cliente.py
import json
import os
import socket

from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_fixed

load_dotenv()
MCP_HOST=os.getenv('MCP_HOST')
MCP_PORT=os.getenv('MCP_PORT')

class MCPCliente:
    def __init__(self, host=MCP_HOST, port=MCP_PORT):
        self.host = host
        self.port = port

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def buscarVeiculos(self, filtros):
        print(f"Enviando filtros....")
        try:
            with socket.create_connection((self.host, self.port), timeout=10) as client_socket:

                client_socket.sendall(json.dumps(filtros, ensure_ascii=False).encode('utf-8'))

                data = client_socket.recv(8192).decode('utf-8')

                if not data.strip():
                    print("Resposta vazia do servidor")
                    return {"erro": "Resposta vazia do servidor"}

                resultados = json.loads(data)

                print(f"Resultados recebidos: {len(resultados.get('resultados', []))} veículos")

                return resultados


        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar resposta do servidor: {e}")
            return {"erro": "Resposta do servidor não é JSON válido"}

        except Exception as e:
            print(f"Erro ao conectar no servidor: {e}")
            return {"erro": str(e)}