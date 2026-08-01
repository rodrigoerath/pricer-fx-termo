"""Curva de cupom cambial sujo (item 4.4 do Manual de Curvas da B3).

Fonte oficial: B3, "Manual de Curvas" (v14, 18/11/2024), seção 4.4 "Curva de
Cupom de Dólar Sujo (DOL)". Fórmulas reproduzidas e citadas em
`DOCUMENTACAO.md`.

A curva é construída em três partes:
  1. Vértice 1 (curtíssimo prazo, antes do primeiro vencimento de DDI):
     calculado a partir do CDI do dia e da variação do PTAX (t0 vs t-1).
  2. Vértices "móveis" (nos vencimentos padronizados que têm DDI negociado):
     a taxa de ajuste do próprio contrato DDI é usada diretamente, sem
     transformação.
  3. Vértices intermediários/longos (qualquer prazo entre/além dos
     vencimentos de DDI): interpolados/extrapolados pela fórmula 1.4.3
     ("Flat Forward 252 com Convenção Linear").

Convenção de taxa: todas as funções aqui recebem e retornam taxas em
**decimal** (ex.: 0.05131 = 5,131% a.a.), não em pontos percentuais — ao
contrário da notação do manual da B3, que usa `taxa/100`. As duas convenções
são equivalentes; optou-se pela decimal por ser a que o `pyield` já retorna.
"""
from __future__ import annotations

import pandas as pd


def vertice_1_cupom_sujo(cdi: float, ptax_t0: float, ptax_t_1: float, du_1: int, dc_1: int) -> float:
    """Vértice 1 da curva de cupom sujo (item 4.4, "Vértice 1").

    taxa = [ (1+cdi)^(du_1/252) / (ptax_t0/ptax_t_1) - 1 ] * 360/dc_1
    """
    return ((1 + cdi) ** (du_1 / 252) / (ptax_t0 / ptax_t_1) - 1) * 360 / dc_1


def vertices_moveis(ddi: pd.DataFrame) -> pd.DataFrame:
    """Vértices "móveis" da curva de cupom sujo: taxa do DDI usada diretamente.

    Espera um DataFrame com colunas `dias_uteis`, `dias_corridos`,
    `taxa_ajuste` (uma linha por vencimento de DDI negociado).
    """
    return ddi[["dias_uteis", "dias_corridos", "taxa_ajuste"]].rename(
        columns={"taxa_ajuste": "taxa"}
    ).sort_values("dias_uteis").reset_index(drop=True)


def _flat_forward_linear(
    du_ant: int, dc_ant: int, taxa_ant: float,
    du_post: int, dc_post: int, taxa_post: float,
    du_alvo: int, dc_alvo: int,
) -> float:
    """Item 1.4.3 — Flat Forward 252 com Convenção Linear.

    Interpola no espaço de "fator de capitalização linear" (base ACT/360)
    entre dois vértices adjacentes, usando a fração de dias úteis como peso
    (mesma lógica de peso da interpolação exponencial 1.4.2, aplicada aqui
    a fatores lineares em vez de exponenciais — curva de cupom cambial é
    cotada em base linear/360, não exponencial/252).

    fator_ant  = 1 + taxa_ant  * dc_ant/360
    fator_post = 1 + taxa_post * dc_post/360
    peso       = (du_alvo - du_ant) / (du_post - du_ant)
    fator_alvo = fator_ant * (fator_post/fator_ant)^peso
    taxa_alvo  = (fator_alvo - 1) * 360/dc_alvo
    """
    fator_ant = 1 + taxa_ant * dc_ant / 360
    fator_post = 1 + taxa_post * dc_post / 360
    peso = (du_alvo - du_ant) / (du_post - du_ant)
    fator_alvo = fator_ant * (fator_post / fator_ant) ** peso
    return (fator_alvo - 1) * 360 / dc_alvo


def interpolar_cupom_sujo(
    curva: pd.DataFrame,
    du_alvo: int,
    dc_alvo: int,
    extrapolar: bool = True,
) -> float:
    """Taxa de cupom cambial sujo para um prazo (du_alvo, dc_alvo) qualquer.

    `curva` deve ter colunas `dias_uteis`, `dias_corridos`, `taxa`, ordenada
    por `dias_uteis` crescente (ex.: saída de `vertices_moveis`, com o
    vértice 1 já incluído como primeira linha).

    - Se `du_alvo` coincide exatamente com um vértice, retorna a taxa desse
      vértice (sem interpolar).
    - Se está entre dois vértices, interpola via `_flat_forward_linear`.
    - Se está além do último vértice: extrapola em flat forward usando os
      dois últimos vértices (se `extrapolar=True`), senão levanta erro.
    """
    curva = curva.sort_values("dias_uteis").reset_index(drop=True)

    exato = curva[curva["dias_uteis"] == du_alvo]
    if len(exato) == 1:
        return float(exato.iloc[0]["taxa"])

    anteriores = curva[curva["dias_uteis"] < du_alvo]
    posteriores = curva[curva["dias_uteis"] > du_alvo]

    if len(anteriores) == 0:
        raise ValueError(
            f"du_alvo={du_alvo} é anterior ao primeiro vértice da curva "
            f"({curva['dias_uteis'].min()}); sem extrapolação para o início."
        )

    if len(posteriores) == 0:
        if not extrapolar:
            raise ValueError(f"du_alvo={du_alvo} além do último vértice; extrapolar=False.")
        ant, post = curva.iloc[-2], curva.iloc[-1]
    else:
        ant = anteriores.iloc[-1]
        post = posteriores.iloc[0]

    return _flat_forward_linear(
        du_ant=int(ant["dias_uteis"]), dc_ant=int(ant["dias_corridos"]), taxa_ant=float(ant["taxa"]),
        du_post=int(post["dias_uteis"]), dc_post=int(post["dias_corridos"]), taxa_post=float(post["taxa"]),
        du_alvo=du_alvo, dc_alvo=dc_alvo,
    )


def montar_curva_cupom_sujo(
    ddi: pd.DataFrame,
    cdi: float,
    ptax_t0: float,
    ptax_t_1: float,
    du_1: int,
    dc_1: int,
) -> pd.DataFrame:
    """Monta a curva completa de cupom sujo: vértice 1 + vértices móveis (DDI)."""
    v1 = pd.DataFrame([{
        "dias_uteis": du_1,
        "dias_corridos": dc_1,
        "taxa": vertice_1_cupom_sujo(cdi, ptax_t0, ptax_t_1, du_1, dc_1),
    }])
    demais = vertices_moveis(ddi)
    return pd.concat([v1, demais], ignore_index=True).sort_values("dias_uteis").reset_index(drop=True)
