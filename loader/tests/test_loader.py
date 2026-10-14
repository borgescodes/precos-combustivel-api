"""Testes das funcoes de normalizacao — rode com: pytest"""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from loader import (  # noqa: E402
    chave_coluna,
    normalizar_uf,
    mapear_colunas,
    normalizar_municipio,
    para_decimal,
    sem_acento,
)


@pytest.mark.parametrize(
    "entrada,esperado",
    [
        ("6,49", 6.49),
        ("6.49", 6.49),
        ("1.234,56", 1234.56),   # milhar com ponto, decimal com virgula
        ("R$ 6,09", 6.09),
        ("  7,00  ", 7.00),
        ("", None),
        (None, None),
        ("abc", None),
    ],
)
def test_para_decimal(entrada, esperado):
    assert para_decimal(entrada) == esperado


def test_sem_acento():
    assert sem_acento("Município") == "Municipio"
    assert sem_acento("SÃO PAULO") == "SAO PAULO"


def test_normalizar_municipio():
    assert normalizar_municipio("  são josé dos campos ") == "SAO JOSE DOS CAMPOS"


def test_chave_coluna():
    assert chave_coluna("Regiao - Sigla") == "regiao sigla"
    assert chave_coluna("REGIAO_SIGLA") == "regiao sigla"
    assert chave_coluna("Data_da_Coleta") == "data da coleta"
    assert chave_coluna("  Valor de Venda  ") == "valor de venda"


def test_mapear_colunas_aceita_variacoes():
    df = pd.DataFrame(
        columns=[
            "Regiao - Sigla", "Estado - Sigla", "Municipio", "Revenda",
            "CNPJ da Revenda", "Produto", "Data da Coleta",
            "Valor de Venda", "Unidade de Medida", "Bandeira",
        ]
    )
    mapa = mapear_colunas(df)
    assert mapa["uf"] == "Estado - Sigla"
    assert mapa["valor_venda"] == "Valor de Venda"
    assert mapa["data_coleta"] == "Data da Coleta"


def test_mapear_colunas_falha_sem_obrigatorias():
    df = pd.DataFrame(columns=["Produto", "Bandeira"])
    with pytest.raises(SystemExit):
        mapear_colunas(df)


def test_localizar_cabecalho_pula_linhas_de_titulo():
    """Planilha da ANP costuma ter titulo antes da tabela."""
    previa = pd.DataFrame([
        ["LEVANTAMENTO DE PRECOS DE COMBUSTIVEIS", None, None, None],
        ["Periodo: 09/08/2026 a 15/08/2026", None, None, None],
        [None, None, None, None],
        ["Município", "Produto", "Data da Coleta", "Valor de Venda"],
        ["MANAUS", "GASOLINA", "10/08/2026", "6,49"],
    ])
    from loader import localizar_cabecalho
    assert localizar_cabecalho(previa) == 3


def test_localizar_cabecalho_quando_ja_e_a_primeira_linha():
    previa = pd.DataFrame([
        ["Municipio", "Produto", "Valor de Venda"],
        ["MANAUS", "GASOLINA", "6,49"],
    ])
    from loader import localizar_cabecalho
    assert localizar_cabecalho(previa) == 0


def test_mapear_colunas_do_arquivo_semanal_de_revendas():
    """O arquivo semanal usa outros nomes que a serie historica."""
    df = pd.DataFrame(columns=[
        "CNPJ", "RAZÃO", "FANTASIA", "ENDEREÇO", "NÚMERO", "COMPLEMENTO",
        "BAIRRO", "CEP", "MUNICÍPIO", "ESTADO", "BANDEIRA", "PRODUTO",
        "UNIDADE DE MEDIDA", "PREÇO DE REVENDA", "DATA DA COLETA",
    ])
    mapa = mapear_colunas(df)
    assert mapa["valor_venda"] == "PREÇO DE REVENDA"
    assert mapa["uf"] == "ESTADO"
    assert mapa["municipio"] == "MUNICÍPIO"
    assert mapa["cnpj_revenda"] == "CNPJ"


@pytest.mark.parametrize(
    "entrada,esperado",
    [
        ("AM", "AM"),
        ("am", "AM"),
        ("Amazonas", "AM"),
        ("SÃO PAULO", "SP"),
        ("Rio Grande do Sul", "RS"),
        ("PAIS INEXISTENTE", None),
        (None, None),
    ],
)
def test_normalizar_uf(entrada, esperado):
    from loader import normalizar_uf
    assert normalizar_uf(entrada) == esperado


def test_agregacao_semanal_respeita_periodo_anp_domingo_a_sabado():
    from loader import AGREGA

    assert "data_coleta + INTERVAL '1 day'" in AGREGA
    assert "INTERVAL '5 days'" in AGREGA
    assert "GROUP BY date_trunc('week', data_coleta + INTERVAL '1 day')" in AGREGA



def test_datas_de_outubro_do_excel_nao_invertem_mes_e_dia():
    from datetime import date
    from loader import preparar

    df = pd.DataFrame({
        "ESTADO": ["PARÁ"] * 3,
        "MUNICÍPIO": ["PARAGOMINAS"] * 3,
        "PRODUTO": ["GASOLINA COMUM"] * 3,
        "DATA DA COLETA": [
            "2026-10-05 00:00:00", "2026-10-09", "09/10/2026"
        ],
        "PREÇO DE REVENDA": ["7,05"] * 3,
    })
    resultado = preparar(df)

    assert resultado["data_coleta"].tolist() == [
        date(2026, 10, 5), date(2026, 10, 9), date(2026, 10, 9)
    ]


def test_carga_semanal_falha_se_datas_nao_batem_com_nome_oficial():
    from datetime import date
    from loader import validar_periodo_arquivo

    url = (
        "https://www.gov.br/anp/arquivos-lpc/2026/"
        "revendas_lpc_2026-10-04_2026-10-10.xlsx"
    )
    df = pd.DataFrame({"data_coleta": [date(2026, 5, 10)]})
    with pytest.raises(ValueError, match="fora do periodo oficial"):
        validar_periodo_arquivo(df, url)

    df["data_coleta"] = [date(2026, 10, 5)]
    validar_periodo_arquivo(df, url)
