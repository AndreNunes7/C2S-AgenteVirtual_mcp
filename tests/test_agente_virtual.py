import pytest
from ..src.agent.agente_virtual import AgenteVirtual
from unittest.mock import patch

@pytest.fixture
def agente():
    return AgenteVirtual(config_path="config/veiculos.json")

def test_validar_filtros_marca_invalida(agente):
    filtros = {"marca": "MarcaInexistente", "modelo": "ModeloX"}
    resultado = agente._validar_filtros(filtros)
    assert "marca" not in resultado, "Marca inválida não deve ser incluída"

def test_extrair_filtros_manual(agente):
    input_text = "Quero um Toyota Corolla 2020"
    filtros = agente._extrair_filtros_manual(input_text)
    assert filtros.get("marca") == "Toyota"
    assert filtros.get("modelo") == "Corolla"
    assert filtros.get("ano") == 2020

@patch("google.generativeai.GenerativeModel.generate_content")
def test_gemini_fallback_on_error(mock_generate_content, agente):
    mock_generate_content.side_effect = Exception("Erro do Gemini")
    input_text = "Toyota Corolla"
    filtros = agente.gemini(input_text)
    assert filtros.get("marca") == "Toyota", "Deve usar _extrair_filtros_manual em caso de erro"