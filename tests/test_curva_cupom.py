import pandas as pd
import pytest

from pricer_fx_termo.curva_cupom import (
    _flat_forward_linear,
    interpolar_cupom_sujo,
    montar_curva_cupom_sujo,
    vertice_1_cupom_sujo,
)


def test_vertice_1_formula_basica():
    # cdi=0.10, ptax_t0=5.00, ptax_t_1=5.00 (câmbio estável -> só efeito do CDI)
    taxa = vertice_1_cupom_sujo(cdi=0.10, ptax_t0=5.00, ptax_t_1=5.00, du_1=1, dc_1=1)
    # sem variação cambial, o cupom sujo deve refletir só a taxa CDI anualizada
    esperado = ((1.10) ** (1 / 252) - 1) * 360
    assert taxa == pytest.approx(esperado)


def test_vertice_1_variacao_cambial_afeta_cupom():
    # dólar caiu de t-1 para t0 (ptax_t0 < ptax_t_1) -> cupom sujo mais alto
    taxa_cambio_estavel = vertice_1_cupom_sujo(0.10, 5.00, 5.00, du_1=1, dc_1=1)
    taxa_dolar_caiu = vertice_1_cupom_sujo(0.10, 4.95, 5.00, du_1=1, dc_1=1)
    assert taxa_dolar_caiu > taxa_cambio_estavel


def test_interpolar_retorna_taxa_exata_no_vertice():
    curva = pd.DataFrame({
        "dias_uteis": [12, 31, 52],
        "dias_corridos": [16, 47, 78],
        "taxa": [-0.03399, 0.02445, 0.03962],
    })
    assert interpolar_cupom_sujo(curva, du_alvo=31, dc_alvo=47) == pytest.approx(0.02445)


def test_interpolar_entre_vertices_bate_com_flat_forward_linear():
    curva = pd.DataFrame({
        "dias_uteis": [12, 31],
        "dias_corridos": [16, 47],
        "taxa": [-0.03399, 0.02445],
    })
    resultado = interpolar_cupom_sujo(curva, du_alvo=20, dc_alvo=28)
    esperado = _flat_forward_linear(
        du_ant=12, dc_ant=16, taxa_ant=-0.03399,
        du_post=31, dc_post=47, taxa_post=0.02445,
        du_alvo=20, dc_alvo=28,
    )
    assert resultado == pytest.approx(esperado)


def test_interpolar_extrapola_alem_do_ultimo_vertice():
    curva = pd.DataFrame({
        "dias_uteis": [12, 31, 52],
        "dias_corridos": [16, 47, 78],
        "taxa": [-0.03399, 0.02445, 0.03962],
    })
    # não levanta erro por padrão (extrapolar=True)
    valor = interpolar_cupom_sujo(curva, du_alvo=100, dc_alvo=150)
    assert isinstance(valor, float)

    with pytest.raises(ValueError):
        interpolar_cupom_sujo(curva, du_alvo=100, dc_alvo=150, extrapolar=False)


def test_interpolar_antes_do_primeiro_vertice_levanta_erro():
    curva = pd.DataFrame({
        "dias_uteis": [12, 31],
        "dias_corridos": [16, 47],
        "taxa": [-0.03399, 0.02445],
    })
    with pytest.raises(ValueError):
        interpolar_cupom_sujo(curva, du_alvo=5, dc_alvo=7)


def test_montar_curva_inclui_vertice_1_e_ddi():
    ddi = pd.DataFrame({
        "data_vencimento": ["2024-11-01", "2024-12-02"],
        "dias_uteis": [12, 31],
        "dias_corridos": [16, 47],
        "taxa_ajuste": [-0.03399, 0.02445],
    })
    curva = montar_curva_cupom_sujo(ddi, cdi=0.1065, ptax_t0=5.6749, ptax_t_1=5.6378, du_1=1, dc_1=1)
    assert list(curva["dias_uteis"]) == [1, 12, 31]
