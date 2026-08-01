import pandas as pd
import pytest

from pricer_fx_termo.curva_pre import _flat_forward_252, interpolar_pre


def test_interpolar_retorna_taxa_exata_no_vertice():
    di1 = pd.DataFrame({"dias_uteis": [12, 31, 52], "taxa_ajuste": [0.10653, 0.10910, 0.11164]})
    assert interpolar_pre(di1, du_alvo=31) == pytest.approx(0.10910)


def test_interpolar_entre_vertices_bate_com_flat_forward_252():
    di1 = pd.DataFrame({"dias_uteis": [12, 31], "taxa_ajuste": [0.10653, 0.10910]})
    resultado = interpolar_pre(di1, du_alvo=20)
    esperado = _flat_forward_252(du_ant=12, taxa_ant=0.10653, du_post=31, taxa_post=0.10910, du_alvo=20)
    assert resultado == pytest.approx(esperado)


def test_interpolar_entre_vertices_fica_entre_os_dois_valores():
    di1 = pd.DataFrame({"dias_uteis": [12, 31], "taxa_ajuste": [0.10653, 0.10910]})
    resultado = interpolar_pre(di1, du_alvo=20)
    assert 0.10653 < resultado < 0.10910


def test_interpolar_extrapola_alem_do_ultimo_vertice():
    di1 = pd.DataFrame({"dias_uteis": [12, 31, 52], "taxa_ajuste": [0.10653, 0.10910, 0.11164]})
    valor = interpolar_pre(di1, du_alvo=100)
    assert isinstance(valor, float)
    with pytest.raises(ValueError):
        interpolar_pre(di1, du_alvo=100, extrapolar=False)


def test_interpolar_antes_do_primeiro_vertice_levanta_erro():
    di1 = pd.DataFrame({"dias_uteis": [12, 31], "taxa_ajuste": [0.10653, 0.10910]})
    with pytest.raises(ValueError):
        interpolar_pre(di1, du_alvo=5)
