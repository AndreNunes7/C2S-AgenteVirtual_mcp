import pytest
from ..src.mcp.cliente import MCPCliente
from ..src.mcp.servidor import MCPServidor
from unittest.mock import patch, Mock
import json

@patch("socket.create_connection")
def test_buscar_veiculos_sucesso(mock_socket):
    mock_conn = Mock()
    mock_socket.return_value.__enter__.return_value = mock_conn
    mock_conn.recv.return_value = json.dumps({"status": "ok", "resultados": [{"marca": "Toyota", "modelo": "Corolla"}]})
    cliente = MCPCliente()
    filtros = {"marca": "Toyota"}
    resultado = cliente.buscarVeiculos(filtros)
    assert resultado["status"] == "ok"
    assert len(resultado["resultados"]) == 1

@patch("socket.create_connection")
def test_buscar_veiculos_erro(mock_socket):
    mock_socket.side_effect = ConnectionError("Falha de conexão")
    cliente = MCPCliente()
    resultado = cliente.buscarVeiculos({"marca": "Toyota"})
    assert "erro" in resultado
    assert "Falha de conexão" in resultado["erro"]