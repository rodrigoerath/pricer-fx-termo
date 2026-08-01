"""Precificação de NDF (Non-Deliverable Forward) USDBRL.

Um NDF é um contrato a termo de câmbio liquidado financeiramente em BRL na
data de vencimento, sem entrega física de dólares: na liquidação, uma parte
paga à outra `notional_usd * (câmbio_termo_realizado - taxa_contratada)`,
convertido/apurado em BRL.

Aqui calculamos:
  - a taxa "par" do NDF (a taxa a termo teórica — ver `forward.py` —, que é
    a taxa contratada que zera o valor do contrato na data de negociação);
  - o valor presente, em BRL, de um NDF com taxa contratada `K` diferente da
    taxa par (ex.: um NDF legado, fora da curva atual), trazendo o payoff
    esperado na liquidação a valor presente pela curva pré.
"""
from __future__ import annotations


def taxa_par(taxa_termo_teorica: float) -> float:
    """Taxa contratada que zera o valor do NDF na data de negociação.

    É, por definição, a própria taxa a termo teórica (CIP) — ver `forward.taxa_termo`.
    """
    return taxa_termo_teorica


def valor_presente(
    notional_usd: float,
    taxa_contratada: float,
    taxa_termo_teorica: float,
    pre_liquidacao: float,
    du_liquidacao: int,
) -> float:
    """Valor presente em BRL de um NDF com taxa contratada `taxa_contratada`.

    payoff_liquidacao_brl = notional_usd * (taxa_termo_teorica - taxa_contratada)
    valor_presente_brl     = payoff_liquidacao_brl * (1+pre_liquidacao)^(-du_liquidacao/252)

    Positivo do ponto de vista de quem está comprado em dólar a termo
    (recebe se o dólar a termo teórico ficou acima da taxa contratada).
    """
    payoff_liquidacao = notional_usd * (taxa_termo_teorica - taxa_contratada)
    fator_desconto = (1 + pre_liquidacao) ** (-du_liquidacao / 252)
    return payoff_liquidacao * fator_desconto
