import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from anp_latest import resolver_url_mais_recente  # noqa: E402


ANP_PAGE = (
    "https://www.gov.br/anp/pt-br/assuntos/precos-e-defesa-da-concorrencia/"
    "precos/levantamento-de-precos-de-combustiveis-ultimas-semanas-pesquisadas"
)


def test_resolve_o_arquivo_oficial_de_revendas_mais_recente():
    html = """
    <a href="/anp/arquivos-lpc/2026/revendas_lpc_2026-09-13_2026-09-19.xlsx">postos</a>
    <a href="/anp/arquivos-lpc/2026/resumo_semanal_lpc_2026-09-20_2026-09-26.xlsx">resumo</a>
    <a href="/anp/arquivos-lpc/2026/revendas_lpc_2026-09-20_2026-09-26.xlsx">postos</a>
    """

    assert resolver_url_mais_recente(html, ANP_PAGE) == (
        "https://www.gov.br/anp/arquivos-lpc/2026/"
        "revendas_lpc_2026-09-20_2026-09-26.xlsx"
    )


def test_rejeita_pagina_fora_do_host_oficial():
    with pytest.raises(ValueError, match="host oficial"):
        resolver_url_mais_recente("", "https://example.com/anp")


def test_ignora_link_de_arquivo_fora_do_host_oficial():
    html = (
        '<a href="https://example.com/revendas_lpc_2026-09-20_2026-09-26.xlsx">'
        "postos</a>"
    )

    with pytest.raises(ValueError, match="arquivo semanal oficial"):
        resolver_url_mais_recente(html, ANP_PAGE)


def test_falha_claramente_quando_nao_encontra_planilha():
    with pytest.raises(ValueError, match="arquivo semanal oficial"):
        resolver_url_mais_recente("<html>sem planilhas</html>", ANP_PAGE)
