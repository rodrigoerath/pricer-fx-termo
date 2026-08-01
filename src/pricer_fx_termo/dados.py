"""Carregamento de dados públicos de mercado (B3 + BCB) via pyield.

Fonte: pacote `pyield` (https://pypi.org/project/pyield/), que consolida o
dataset histórico público de derivativos da B3 (Price Report) e as séries
do Banco Central (SGS/PTAX). Nenhum dado é sintético ou raspado: DI1, DDI e
PTAX vêm diretamente da fonte primária do mercado brasileiro.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import pyield as yd


@dataclass
class CurvasMercado:
    """Snapshot de todas as curvas/insumos necessários para uma data de referência."""

    data_referencia: str
    di1: pd.DataFrame  # colunas: data_vencimento, dias_uteis, dias_corridos, taxa_ajuste
    ddi: pd.DataFrame  # colunas: data_vencimento, dias_uteis, dias_corridos, taxa_ajuste
    ptax_t0: float
    ptax_t_1: float
    cdi: float  # taxa CDI referencial do dia, em decimal (ex.: 0.1065)


def carregar_curvas(data_referencia: str, data_anterior: str) -> CurvasMercado:
    """Busca DI1, DDI, PTAX(t0), PTAX(t-1) e CDI para uma data de referência.

    `data_anterior` deve ser o dia útil imediatamente anterior a
    `data_referencia` (necessário para o PTAX t-1 usado na curva a termo).
    """
    di1 = yd.futuro.historico(data_referencia, "DI1").to_pandas()
    ddi = yd.futuro.historico(data_referencia, "DDI").to_pandas()
    ptax_t0 = yd.ptax(data_referencia)
    ptax_t_1 = yd.ptax(data_anterior)
    cdi = yd.di_over(data_referencia)  # taxa CDI/DI-over oficial do dia (CETIP/B3)

    return CurvasMercado(
        data_referencia=data_referencia,
        di1=di1[["data_vencimento", "dias_uteis", "dias_corridos", "taxa_ajuste"]],
        ddi=ddi[["data_vencimento", "dias_uteis", "dias_corridos", "taxa_ajuste"]],
        ptax_t0=ptax_t0,
        ptax_t_1=ptax_t_1,
        cdi=cdi,
    )


def dias_ate_vencimento(data_referencia: str, data_vencimento: str) -> tuple[int, int]:
    """Retorna (dias_uteis, dias_corridos) entre a data de referência e um vencimento alvo."""
    du = yd.du.contar(data_referencia, data_vencimento)
    dc = (pd.Timestamp(data_vencimento) - pd.Timestamp(data_referencia)).days
    return int(du), int(dc)
