"""
Análise de porte das empresas.
Author: Guilherme Crepaldi
Classifica por faturamento estimado: MEI, ME, EPP, Médio, Grande.
"""

import logging
from collections import Counter
from typing import Optional

import config

logger = logging.getLogger("cnpj-miner.porte")


def classificar_porte(registro: dict) -> str:
    """
    Classifica o porte da empresa com base no campo 'porte' ou 'capital_social'.

    MEI até 81k, ME até 360k, EPP até 4.8M, Médio até 300M, Grande > 300M.
    Esses valores mudam todo ano — conferir legislação atualizada.

    Args:
        registro: Dicionário com dados da empresa.

    Returns:
        String com a classificação: 'MEI', 'ME', 'EPP', 'MEDIO', 'GRANDE'.
    """
    # Se o CSV já tem porte definido, usa direto
    porte_direto = (
        registro.get("porte") or registro.get("PORTE") or ""
    ).strip().upper()

    if porte_direto in config.PORTE_ORDEM:
        return porte_direto

    # Fallback: estima pelo capital social
    capital_str = (
        registro.get("capital_social") or registro.get("CAPITAL_SOCIAL") or "0"
    )

    try:
        # Lida com formato brasileiro (1.234,56 -> 1234.56)
        capital_str = capital_str.strip().replace(".", "").replace(",", ".")
        capital = float(capital_str)
    except (ValueError, TypeError):
        capital = 0.0

    if capital <= config.PORTE_LIMITES["MEI"]:
        return "MEI"
    elif capital <= config.PORTE_LIMITES["ME"]:
        return "ME"
    elif capital <= config.PORTE_LIMITES["EPP"]:
        return "EPP"
    elif capital <= config.PORTE_LIMITES["MEDIO"]:
        return "MEDIO"
    else:
        return "GRANDE"


def distribuicao_porte(dados: list[dict]) -> Counter:
    """Contagem de empresas por porte."""
    counter: Counter = Counter()
    for reg in dados:
        porte = classificar_porte(reg)
        counter[porte] += 1

    # Garante que todos os portes apareçam (mesmo com zero)
    for p in config.PORTE_ORDEM:
        if p not in counter:
            counter[p] = 0

    logger.info("Distribuição por porte: %s", dict(counter))
    return counter


def porte_por_setor(
    dados: list[dict], setores: dict[str, str]
) -> dict[str, Counter]:
    """
    Cruzamento porte x setor econômico.

    Args:
        dados: Registros de empresas.
        setores: Dict com índice do registro -> nome do setor.

    Returns:
        Dict com setor -> Counter de portes.
    """
    resultado: dict[str, Counter] = {}
    for i, reg in enumerate(dados):
        setor = setores.get(i, "Não classificado")
        porte = classificar_porte(reg)
        if setor not in resultado:
            resultado[setor] = Counter()
        resultado[setor][porte] += 1
    return resultado


def porte_por_uf(dados: list[dict]) -> dict[str, Counter]:
    """Cruzamento porte x UF."""
    resultado: dict[str, Counter] = {}
    for reg in dados:
        uf = (reg.get("uf") or reg.get("UF") or "").strip().upper()
        if uf not in config.ESTADOS_BR:
            continue
        porte = classificar_porte(reg)
        if uf not in resultado:
            resultado[uf] = Counter()
        resultado[uf][porte] += 1
    return resultado


def resumo_porte(dados: list[dict]) -> dict:
    """Resumo completo da análise de porte."""
    dist = distribuicao_porte(dados)
    total = sum(dist.values()) or 1
    return {
        "distribuicao": dict(dist),
        "percentuais": {
            k: round((v / total) * 100, 2) for k, v in dist.items()
        },
        "porte_dominante": dist.most_common(1)[0] if dist else ("N/A", 0),
        "total_empresas": total,
    }
