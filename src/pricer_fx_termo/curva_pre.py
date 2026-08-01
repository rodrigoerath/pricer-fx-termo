"""Curva de juros pré-fixada (item 2.1 do Manual de Curvas da B3, curva PRE).

Construída a partir dos vencimentos do contrato futuro DI1 (Depósito
Interfinanceiro de Um Dia), em base exponencial 252 dias úteis — a
convenção padrão de juros pré no mercado brasileiro.

Convenção de taxa: decimal (ver nota em `curva_cupom.py`).
"""
from __future__ import annotations

import pandas as pd


def _flat_forward_252(
    du_ant: int, taxa_ant: float,
    du_post: int, taxa_post: float,
    du_alvo: int,
) -> float:
    """Item 1.4.2 — Flat Forward 252 (interpolação exponencial da curva PRE).

    fator_ant  = (1+taxa_ant)^(du_ant/252)
    fator_post = (1+taxa_post)^(du_post/252)
    peso       = (du_alvo - du_ant) / (du_post - du_ant)
    fator_alvo = fator_ant * (fator_post/fator_ant)^peso
    taxa_alvo  = fator_alvo^(252/du_alvo) - 1
    """
    fator_ant = (1 + taxa_ant) ** (du_ant / 252)
    fator_post = (1 + taxa_post) ** (du_post / 252)
    peso = (du_alvo - du_ant) / (du_post - du_ant)
    fator_alvo = fator_ant * (fator_post / fator_ant) ** peso
    return fator_alvo ** (252 / du_alvo) - 1


def interpolar_pre(di1: pd.DataFrame, du_alvo: int, extrapolar: bool = True) -> float:
    """Taxa pré-fixada para um prazo `du_alvo` (dias úteis) qualquer.

    `di1` deve ter colunas `dias_uteis`, `taxa_ajuste` (uma linha por
    vencimento do futuro DI1).
    """
    curva = di1[["dias_uteis", "taxa_ajuste"]].sort_values("dias_uteis").reset_index(drop=True)

    exato = curva[curva["dias_uteis"] == du_alvo]
    if len(exato) == 1:
        return float(exato.iloc[0]["taxa_ajuste"])

    anteriores = curva[curva["dias_uteis"] < du_alvo]
    posteriores = curva[curva["dias_uteis"] > du_alvo]

    if len(anteriores) == 0:
        raise ValueError(
            f"du_alvo={du_alvo} é anterior ao primeiro vencimento de DI1 "
            f"({curva['dias_uteis'].min()}); sem extrapolação para o início."
        )

    if len(posteriores) == 0:
        if not extrapolar:
            raise ValueError(f"du_alvo={du_alvo} além do último vencimento; extrapolar=False.")
        ant, post = curva.iloc[-2], curva.iloc[-1]
    else:
        ant = anteriores.iloc[-1]
        post = posteriores.iloc[0]

    return _flat_forward_252(
        du_ant=int(ant["dias_uteis"]), taxa_ant=float(ant["taxa_ajuste"]),
        du_post=int(post["dias_uteis"]), taxa_post=float(post["taxa_ajuste"]),
        du_alvo=du_alvo,
    )
