"""Resolve a planilha semanal de revendas mais recente no site oficial da ANP."""

from __future__ import annotations

import re
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from urllib.request import urlopen


ANP_PAGE_URL = (
    "https://www.gov.br/anp/pt-br/assuntos/precos-e-defesa-da-concorrencia/"
    "precos/levantamento-de-precos-de-combustiveis-ultimas-semanas-pesquisadas"
)
ARQUIVO_RE = re.compile(
    r"revendas_lpc_(\d{4}-\d{2}-\d{2})_(\d{4}-\d{2}-\d{2})\.xlsx$",
    re.IGNORECASE,
)


class _Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        for nome, valor in attrs:
            if nome.lower() == "href" and valor:
                self.hrefs.append(valor)


def _oficial(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme == "https" and parsed.hostname == "www.gov.br"


def resolver_url_mais_recente(html: str, page_url: str = ANP_PAGE_URL) -> str:
    if not _oficial(page_url):
        raise ValueError("a pagina da ANP deve usar o host oficial www.gov.br")

    parser = _Links()
    parser.feed(html)
    candidatos: list[tuple[str, str]] = []
    for href in parser.hrefs:
        url = urljoin(page_url, href)
        match = ARQUIVO_RE.search(urlparse(url).path)
        if match and _oficial(url):
            candidatos.append((match.group(2), url))

    if not candidatos:
        raise ValueError("arquivo semanal oficial de revendas nao encontrado")

    return max(candidatos)[1]


def obter_url_mais_recente(page_url: str = ANP_PAGE_URL) -> str:
    with urlopen(page_url, timeout=30) as resposta:
        html = resposta.read().decode("utf-8")
    return resolver_url_mais_recente(html, page_url)


if __name__ == "__main__":
    print(obter_url_mais_recente())
