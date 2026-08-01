"""Valida `taxa_termo` contra preços de ajuste REAIS do futuro DOL na B3.

Os números abaixo (DI1, DDI, DOL, PTAX) foram capturados via `pyield` para
16/10/2024 e são fixos aqui (fixture), para o teste não depender de rede.
Ver DOCUMENTACAO.md para a validação completa (15 vencimentos, erro < 0,001 bp).
"""
import pytest

from pricer_fx_termo.forward import taxa_termo

PTAX_T_1 = 5.6378  # PTAX de venda em 15/10/2024

# (dias_uteis, dias_corridos, taxa_pre, taxa_cupom_sujo, dol_ajuste_real/1000)
VERTICES_REAIS = [
    (12, 16, 0.10653, -0.03399, 5.673612),
    (31, 47, 0.10910, 0.02445, 5.691905),
    (52, 78, 0.11164, 0.03962, 5.713235),
    (74, 110, 0.11362, 0.04582, 5.738466),
    (94, 140, 0.11570, 0.04829, 5.764550),
    (218, 320, 0.12378, 0.05161, 5.963112),
]


@pytest.mark.parametrize("du,dc,pre,cd,dol_real", VERTICES_REAIS)
def test_taxa_termo_reproduz_dol_real(du, dc, pre, cd, dol_real):
    calculado = taxa_termo(pre, cd, du, dc, PTAX_T_1)
    diff_bps = abs(calculado / dol_real - 1) * 10_000
    assert diff_bps < 0.01  # menos de 0,01 bp de diferença
