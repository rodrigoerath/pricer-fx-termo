# Pricer de Câmbio a Termo com Cupom Cambial (USDBRL)

Pricer de NDF (forward de dólar não-entregável) USDBRL a partir da
**paridade coberta de juros (CIP)**, combinando a curva de juros pré-fixada
(futuro DI1) com a curva de cupom cambial (futuro DDI) — a mesma metodologia
que a B3 usa para publicar sua curva oficial de câmbio a termo.

> Fórmulas reproduzidas do *Manual de Curvas* da B3 (item 4.1 — Forward de
> Reais x Dólar) e validadas nesta sessão contra os preços reais de ajuste
> do futuro DOL: erro menor que 0,01 ponto-base em 15+ vencimentos.

## Fonte dos dados

100% dados públicos, via o pacote [`pyield`](https://pypi.org/project/pyield/):
- **DI1** e **DDI** — dataset histórico oficial da B3 (Price Report).
- **PTAX** e **CDI/DI-over** — Banco Central (SGS) e CETIP/B3.

Nenhum dado sintético, nenhum scraping.

## Módulos (`src/pricer_fx_termo/`)

- **`dados.py`** — busca DI1, DDI, PTAX(t0/t-1) e CDI via `pyield` para uma data de referência.
- **`curva_pre.py`** — interpolação flat-forward 252 da curva de juros pré (DI1).
- **`curva_cupom.py`** — monta e interpola a curva de cupom cambial sujo (DDI).
- **`forward.py`** — fórmula da B3 (item 4.1) que combina as duas curvas em um câmbio a termo teórico.
- **`ndf.py`** — precificação/valor presente de um NDF.
- **`sensibilidades.py`** — delta cambial, DV01 pré e DV01 cupom via bump-and-reprice.

## Notebook

`notebooks/pricer_fx_termo_analise.ipynb` percorre as 5 etapas (curva pré,
curva de cupom, validação CIP x dólar futuro real, precificação de um NDF
customizado, sensibilidades) de forma narrada, com gráficos.

## Rodando

Requer **Python 3.12+** (o pacote `pyield>=0.54` não instala em versões
anteriores). Este projeto foi desenvolvido com um kernel Jupyter dedicado:

```bash
pip install -r requirements.txt
python -m ipykernel install --user --name pricer-fx-termo --display-name "Python (pricer-fx-termo)"

PYTHONPATH=src pytest tests/ -v
jupyter nbconvert --to notebook --execute --inplace notebooks/pricer_fx_termo_analise.ipynb
```

## Limitações conhecidas

- A curva de cupom cambial usa apenas os vencimentos padronizados de DDI; a
  B3 também usa contratos FRC para alguns vértices — não incorporado nesta v1.
- A interpolação entre vértices da curva de cupom (item 1.4.3 do manual) foi
  reconstruída por analogia estrutural com a interpolação exponencial da
  curva pré (item 1.4.2) — o mecanismo central de precificação (fórmula de
  paridade, item 4.1) foi validado numericamente contra preços reais de
  mercado; a interpolação em si não foi validada ponto a ponto contra uma
  curva de cupom limpo oficial publicada pela B3.
