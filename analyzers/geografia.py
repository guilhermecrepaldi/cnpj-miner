"""
Análise geográfica: distribuição por estado, cidade, região, densidade.
Author: Guilherme Crepaldi
"""

import logging
from collections import Counter
from typing import Optional

import config

logger = logging.getLogger("cnpj-miner.geografia")


def _extrair_uf(registro: dict) -> Optional[str]:
    """Extrai UF padronizada (2 letras maiúsculas) do registro."""
    uf = (registro.get("uf") or registro.get("UF") or "").strip().upper()
    return uf if uf in config.ESTADOS_BR else None


def _extrair_cidade(registro: dict) -> Optional[str]:
    cidade = (registro.get("cidade") or registro.get("municipio") or "").strip()
    return cidade.upper() if cidade else None


def distribuicao_por_estado(dados: list[dict]) -> Counter:
    """
    Contagem de empresas por UF.

    Returns:
        Counter com UF como chave e contagem como valor.
    """
    counter: Counter = Counter()
    for reg in dados:
        uf = _extrair_uf(reg)
        if uf:
            counter[uf] += 1
    logger.info("Distribuição por estado: %d UFs encontradas", len(counter))
    return counter


def distribuicao_por_regiao(dados: list[dict]) -> dict[str, int]:
    """Agrega a contagem por região geográfica (Norte, Nordeste, etc.)."""
    uf_count = distribuicao_por_estado(dados)
    regioes: dict[str, int] = {}
    for regiao, ufs in config.REGIOES.items():
        total = sum(uf_count.get(uf, 0) for uf in ufs)
        if total > 0:
            regioes[regiao] = total
    logger.info("Distribuição por região: %d regiões", len(regioes))
    return regioes


def top_cidades(dados: list[dict], n: int = 10) -> list[tuple[str, str, int]]:
    """
    Top N cidades com mais empresas.

    Returns:
        Lista de tuplas (cidade, uf, quantidade).
    """
    counter: Counter = Counter()
    for reg in dados:
        cidade = _extrair_cidade(reg)
        uf = _extrair_uf(reg)
        if cidade and uf:
            chave = (cidade, uf)
            counter[chave] += 1
    return [(cidade, uf, qtd) for (cidade, uf), qtd in counter.most_common(n)]


def densidade_por_estado(dados: list[dict]) -> dict[str, float]:
    """
    Calcula densidade relativa (% do total) por estado.

    Returns:
        Dict com UF -> percentual (0-100).
    """
    uf_count = distribuicao_por_estado(dados)
    total = sum(uf_count.values())
    if total == 0:
        return {}
    return {uf: round((count / total) * 100, 2) for uf, count in uf_count.items()}


def resumo_geografico(dados: list[dict]) -> dict:
    """
    Resumo completo da análise geográfica.
    """
    return {
        "total_empresas": len(dados),
        "ufs_presentes": sorted(distribuicao_por_estado(dados).keys()),
        "total_ufs": len(distribuicao_por_estado(dados)),
        "distribuicao_uf": dict(distribuicao_por_estado(dados).most_common()),
        "distribuicao_regiao": distribuicao_por_regiao(dados),
        "densidade": densidade_por_estado(dados),
        "top_10_cidades": [
            {"cidade": c, "uf": u, "empresas": q}
            for c, u, q in top_cidades(dados, 10)
        ],
    }
