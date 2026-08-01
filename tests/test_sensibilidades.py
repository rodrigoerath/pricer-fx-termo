import pytest

from pricer_fx_termo.sensibilidades import ParametrosNDF, delta_cambial, dv01_cupom, dv01_pre, precificar


def _parametros_base() -> ParametrosNDF:
    return ParametrosNDF(
        notional_usd=1_000_000,
        taxa_contratada=5.60,
        pre_n=0.1160,
        cd_n=0.0450,
        du_n=94,
        dc_n=140,
        ptax_t_1=5.6378,
        pre_liquidacao=0.1160,
        du_liquidacao=94,
    )


def test_precificar_roda_e_retorna_float():
    valor = precificar(_parametros_base())
    assert isinstance(valor, float)


def test_delta_cambial_positivo_para_posicao_comprada_em_dolar():
    # notional positivo = comprado em USD a termo; dólar mais alto -> ganho
    delta = delta_cambial(_parametros_base())
    assert delta > 0


def test_delta_cambial_bate_com_reprecificacao_manual():
    p = _parametros_base()
    bump = 0.01
    p_alta = ParametrosNDF(**{**p.__dict__, "ptax_t_1": p.ptax_t_1 * (1 + bump)})
    p_baixa = ParametrosNDF(**{**p.__dict__, "ptax_t_1": p.ptax_t_1 * (1 - bump)})
    esperado = (precificar(p_alta) - precificar(p_baixa)) / 2
    assert delta_cambial(p, bump=bump) == pytest.approx(esperado)


def test_dv01_pre_bate_com_reprecificacao_manual():
    p = _parametros_base()
    bump = 0.0001
    p_alta = ParametrosNDF(**{**p.__dict__, "pre_n": p.pre_n + bump, "pre_liquidacao": p.pre_liquidacao + bump})
    p_baixa = ParametrosNDF(**{**p.__dict__, "pre_n": p.pre_n - bump, "pre_liquidacao": p.pre_liquidacao - bump})
    esperado = (precificar(p_alta) - precificar(p_baixa)) / 2
    assert dv01_pre(p, bump=bump) == pytest.approx(esperado)


def test_dv01_cupom_bate_com_reprecificacao_manual():
    p = _parametros_base()
    bump = 0.0001
    p_alta = ParametrosNDF(**{**p.__dict__, "cd_n": p.cd_n + bump})
    p_baixa = ParametrosNDF(**{**p.__dict__, "cd_n": p.cd_n - bump})
    esperado = (precificar(p_alta) - precificar(p_baixa)) / 2
    assert dv01_cupom(p, bump=bump) == pytest.approx(esperado)


def test_dv01_cupom_negativo_para_posicao_comprada_em_dolar():
    # cupom cambial mais alto -> dólar futuro teórico mais baixo (denominador maior)
    # -> perda para quem está comprado em USD a termo
    assert dv01_cupom(_parametros_base()) < 0
