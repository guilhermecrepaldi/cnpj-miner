"""
Análise temporal: abertura de empresas por ano, mês, sazonalidade.
Author: Guilherme Crepaldi
"""

import logging
from collections import Counter, defaultdict
from datetime import datetime
from typing import Optional

logger = logging.getLogger("cnpj-miner.temporal")


def _parse_data(data_str: Optional[str]) -> Optional[datetime]:
    """
    Tenta interpretar a data de abertura em múltiplos formatos comuns.

    A Receita Federal usa formato DD/MM/AAAA, mas dados públicos
    podem vir em ISO (AAAA-MM-DD) ou outros formatos.
    """
    if not data_str or not data_str.strip():
        return None

    data_str = data_str.strip()
    formatos = [
        "%d/%m/%Y",       # 01/01/2024
        "%Y-%m-%d",       # 2024-01-01
        "%d/%m/%Y %H:%M:%S",  # 01/01/2024 12:00:00
        "%Y-%m-%d %H:%M:%S",  # 2024-01-01 12:00:00
        "%d-%m-%Y",       # 01-01-2024
    ]

    for fmt in formatos:
        try:
            return datetime.strptime(data_str, fmt)
        except (ValueError, TypeError):
            continue
    return None


def empresas_por_ano(dados: list[dict]) -> Counter:
    """
    Contagem de empresas abertas por ano.

    Returns:
        Counter com ano (int) -> quantidade.
    """
    counter: Counter = Counter()
    nao_parseadas = 0
    for reg in dados:
        data_str = reg.get("data_abertura") or reg.get("DATA_ABERTURA")
        dt = _parse_data(data_str)
        if dt:
            counter[dt.year] += 1
        else:
            nao_parseadas += 1

    if nao_parseadas:
        logger.warning(
            "%d registros com data inválida ou ausente", nao_parseadas
        )
    logger.info("Empresas por ano: %d anos distintos", len(counter))
    return counter


def empresas_por_mes(dados: list[dict]) -> Counter:
    """
    Contagem de empresas abertas por mês (agregado histórico).
    Permite identificar sazonalidade.

    Returns:
        Counter com mês (1-12) -> quantidade.
    """
    counter: Counter = Counter()
    for reg in dados:
        data_str = reg.get("data_abertura") or reg.get("DATA_ABERTURA")
        dt = _parse_data(data_str)
        if dt:
            counter[dt.month] += 1
    return counter


def empresas_por_ano_mes(dados: list[dict]) -> dict[int, Counter]:
    """
    Contagem de empresas abertas por ano + mês.

    Returns:
        Dict: ano -> Counter(mês -> quantidade).
    """
    resultado: dict[int, Counter] = defaultdict(Counter)
    for reg in dados:
        data_str = reg.get("data_abertura") or reg.get("DATA_ABERTURA")
        dt = _parse_data(data_str)
        if dt:
            resultado[dt.year][dt.month] += 1
    return dict(resultado)


def sazonalidade(dados: list[dict]) -> dict:
    """
    Analisa sazonalidade: meses com mais abertura.

    Returns:
        Dict com análises de sazonalidade.
    """
    por_mes = empresas_por_mes(dados)
    total = sum(por_mes.values()) or 1

    meses_nomes = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
    }

    return {
        "total_registros": total,
        "distribuicao_mensal": {
            meses_nomes[m]: qtd for m, qtd in sorted(por_mes.items())
        },
        "mes_mais_empresas": meses_nomes.get(
            por_mes.most_common(1)[0][0], "N/A"
        ) if por_mes else "N/A",
        "mes_mais_empresas_qtd": por_mes.most_common(1)[0][1] if por_mes else 0,
        "mes_menos_empresas": meses_nomes.get(
            por_mes.most_common()[-1][0], "N/A"
        ) if por_mes else "N/A",
        "media_mensal": round(total / 12, 1),
        "variacao_percentual_max_min": (
            round(
                ((por_mes.most_common(1)[0][1] - por_mes.most_common()[-1][1])
                 / por_mes.most_common()[-1][1]) * 100,
                2,
            )
            if por_mes and por_mes.most_common()[-1][1] > 0
            else 0
        ),
    }


def idade_media(dados: list[dict]) -> Optional[float]:
    """
    Calcula a idade média das empresas em anos (desde abertura até hoje).

    Returns:
        Idade média em anos, ou None se não for possível calcular.
    """
    from datetime import date
    hoje = date.today()
    idades: list[float] = []

    for reg in dados:
        data_str = reg.get("data_abertura") or reg.get("DATA_ABERTURA")
        dt = _parse_data(data_str)
        if dt:
            delta = hoje - dt.date()
            idade_anos = delta.days / 365.25
            idades.append(idade_anos)

    if not idades:
        return None
    return round(sum(idades) / len(idades), 2)


def resumo_temporal(dados: list[dict]) -> dict:
    """Resumo completo da análise temporal."""
    return {
        "empresas_por_ano": dict(empresas_por_ano(dados)),
        "sazonalidade": sazonalidade(dados),
        "idade_media_anos": idade_media(dados),
        "empresas_por_ano_mes": {
            str(ano): dict(meses) for ano, meses in empresas_por_ano_mes(dados).items()
        },
    }
