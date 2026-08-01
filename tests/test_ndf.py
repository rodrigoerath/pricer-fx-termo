import pytest

from pricer_fx_termo.ndf import taxa_par, valor_presente


def test_taxa_par_e_a_propria_taxa_termo():
    assert taxa_par(5.7321) == 5.7321


def test_valor_presente_par_e_zero():
    # taxa contratada == taxa a termo teórica -> NDF vale zero na contratação
    v = valor_presente(
        notional_usd=1_000_000, taxa_contratada=5.50,
        taxa_termo_teorica=5.50, pre_liquidacao=0.10, du_liquidacao=126,
    )
    assert v == pytest.approx(0.0)


def test_valor_presente_formula_conhecida():
    # notional=1000, contratada=5.0, termo teórico=5.5, pré=10%, 1 ano útil (252 du)
    v = valor_presente(
        notional_usd=1_000, taxa_contratada=5.0,
        taxa_termo_teorica=5.5, pre_liquidacao=0.10, du_liquidacao=252,
    )
    payoff = 1_000 * (5.5 - 5.0)
    esperado = payoff * (1.10) ** (-252 / 252)
    assert v == pytest.approx(esperado)


def test_valor_presente_positivo_quando_termo_acima_da_contratada():
    v = valor_presente(
        notional_usd=1_000, taxa_contratada=5.0,
        taxa_termo_teorica=5.5, pre_liquidacao=0.10, du_liquidacao=126,
    )
    assert v > 0


def test_valor_presente_negativo_quando_termo_abaixo_da_contratada():
    v = valor_presente(
        notional_usd=1_000, taxa_contratada=5.5,
        taxa_termo_teorica=5.0, pre_liquidacao=0.10, du_liquidacao=126,
    )
    assert v < 0
