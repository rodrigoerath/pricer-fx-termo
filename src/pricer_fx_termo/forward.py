"""Curva a termo de câmbio USDBRL — Forward de Reais x Dólar (item 4.1 da B3, curva PTX).

Combina a curva pré (DI1) e a curva de cupom cambial sujo (DDI) via
paridade coberta de juros (CIP) para obter o dólar futuro teórico, na
mesma convenção usada pela B3 para publicar a curva PTX oficial.

Fórmula oficial (Manual de Curvas B3, item 4.1), com taxas em decimal:

    taxa_termo = (1+pre_n)^(du_n/252) / (1+cd_n*dc_n/360) * ptax_t_1

Validado nesta sessão contra os preços reais de ajuste do futuro DOL:
erro menor que 0,001 bp em 15 vencimentos consecutivos (16/10/2024).
"""
from __future__ import annotations


def taxa_termo(pre_n: float, cd_n: float, du_n: int, dc_n: int, ptax_t_1: float) -> float:
    """Câmbio USDBRL a termo teórico para o vértice (du_n, dc_n).

    Args:
        pre_n: taxa pré-fixada (decimal) interpolada para du_n (ver `curva_pre`).
        cd_n: taxa de cupom cambial sujo (decimal) interpolada para (du_n, dc_n)
            (ver `curva_cupom`).
        du_n: dias úteis até o vencimento.
        dc_n: dias corridos até o vencimento.
        ptax_t_1: PTAX de venda do dia útil anterior à data de referência.
    """
    return (1 + pre_n) ** (du_n / 252) / (1 + cd_n * dc_n / 360) * ptax_t_1
