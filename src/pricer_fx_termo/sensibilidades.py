"""Sensibilidades do NDF via bump-and-reprice (diferenças finitas centradas).

Em vez de derivar fórmulas fechadas para cada grego (frágil a erros de
sinal/convenção), cada sensibilidade choca um insumo da curva para cima e
para baixo em uma quantidade pequena, reprecifica o NDF nos dois cenários
com as mesmas funções de `forward.py`/`ndf.py`, e mede a diferença — a
mesma técnica usada em mesas de risco reais para full reval.
"""
from __future__ import annotations

from dataclasses import dataclass

from . import forward, ndf


@dataclass
class ParametrosNDF:
    notional_usd: float
    taxa_contratada: float
    pre_n: float          # taxa pré interpolada no vencimento do NDF
    cd_n: float           # taxa de cupom sujo interpolada no vencimento do NDF
    du_n: int
    dc_n: int
    ptax_t_1: float
    pre_liquidacao: float  # taxa pré para desconto até a liquidação (normalmente = pre_n)
    du_liquidacao: int      # normalmente = du_n


def precificar(p: ParametrosNDF) -> float:
    """Valor presente (BRL) do NDF para o conjunto de parâmetros dado."""
    fwd = forward.taxa_termo(p.pre_n, p.cd_n, p.du_n, p.dc_n, p.ptax_t_1)
    return ndf.valor_presente(
        p.notional_usd, p.taxa_contratada, fwd, p.pre_liquidacao, p.du_liquidacao
    )


def delta_cambial(p: ParametrosNDF, bump: float = 0.01) -> float:
    """Variação do valor do NDF para +1% no PTAX(t-1) (spot), por bump simétrico.

    Retorna a variação de valor (BRL) para um choque de `bump` (fração,
    padrão 1%) no câmbio à vista — não normalizado por 1 real de spot.
    """
    alta = precificar(_com_ptax(p, p.ptax_t_1 * (1 + bump)))
    baixa = precificar(_com_ptax(p, p.ptax_t_1 * (1 - bump)))
    return (alta - baixa) / 2


def dv01_pre(p: ParametrosNDF, bump: float = 0.0001) -> float:
    """Variação do valor do NDF para 1 bp de choque na taxa pré (du_n)."""
    alta = precificar(_com_pre(p, p.pre_n + bump))
    baixa = precificar(_com_pre(p, p.pre_n - bump))
    return (alta - baixa) / 2


def dv01_cupom(p: ParametrosNDF, bump: float = 0.0001) -> float:
    """Variação do valor do NDF para 1 bp de choque no cupom cambial (cd_n)."""
    alta = precificar(_com_cupom(p, p.cd_n + bump))
    baixa = precificar(_com_cupom(p, p.cd_n - bump))
    return (alta - baixa) / 2


def _com_ptax(p: ParametrosNDF, novo_ptax: float) -> ParametrosNDF:
    return ParametrosNDF(**{**p.__dict__, "ptax_t_1": novo_ptax})


def _com_pre(p: ParametrosNDF, novo_pre: float) -> ParametrosNDF:
    # bump na taxa pré do vencimento do NDF também desloca a taxa usada no desconto,
    # já que por padrão pre_liquidacao == pre_n (mesmo vértice).
    mesma_taxa_desconto = p.pre_liquidacao == p.pre_n
    novo_desconto = novo_pre if mesma_taxa_desconto else p.pre_liquidacao
    return ParametrosNDF(**{**p.__dict__, "pre_n": novo_pre, "pre_liquidacao": novo_desconto})


def _com_cupom(p: ParametrosNDF, novo_cd: float) -> ParametrosNDF:
    return ParametrosNDF(**{**p.__dict__, "cd_n": novo_cd})
