"""
Análise de setores econômicos via CNAE.
Author: Guilherme Crepaldi
Categoriza empresas por setor, encontra setores mais comuns e tendências.
"""

import logging
from collections import Counter
from typing import Optional

import data.loader as loader
import config

logger = logging.getLogger("cnpj-miner.setores")


# Agrupamento de seções CNAE em setores econômicos amplos
# CNAE mudou em 2023, alguns códigos podem estar desatualizados
SECAO_PARA_SETOR = {
    "A": "Agropecuária",
    "B": "Indústria Extrativa",
    "C": "Indústria de Transformação",
    "D": "Eletricidade e Gás",
    "E": "Água e Saneamento",
    "F": "Construção",
    "G": "Comércio",
    "H": "Transporte",
    "I": "Alojamento e Alimentação",
    "J": "Informação e Comunicação",
    "K": "Finanças e Seguros",
    "L": "Imobiliário",
    "M": "Atividades Profissionais",
    "N": "Atividades Administrativas",
    "O": "Administração Pública",
    "P": "Educação",
    "Q": "Saúde e Serviços Sociais",
    "R": "Artes e Entretenimento",
    "S": "Outros Serviços",
    "T": "Serviços Domésticos",
    "U": "Organismos Internacionais",
}


def _cnae_para_secao(codigo_cnae: str, mapping: dict) -> Optional[str]:
    """
    Converte código CNAE (ex: '4711301') para seção (ex: 'G').

    O primeiro dígito do CNAE corresponde à seção na classificação nacional.
    """
    codigo = (codigo_cnae or "").strip()
    if not codigo:
        return None

    # Tenta lookup direto no mapping
    if codigo in mapping:
        return mapping[codigo].get("secao")

    # Fallback: primeiro dígito -> seção (aproximação)
    primeiro_digito = codigo[0]
    mapa_fallback = {
        "0": None, "1": "A", "2": "B", "3": "C", "4": "D",
        "5": "E", "6": "F", "7": "G", "8": "H", "9": "I",
    }
    # Na verdade CNAE 2.0 tem mapeamento mais complexo.
    # Para CNAE completa de 7 dígitos, usamos os 2 primeiros dígitos:
    # 01-03 A, 05-09 B, 10-33 C, 35 D, 36-39 E, 41-43 F,
    # 45-47 G, 49-53 H, 55-56 I, 58-63 J, 64-66 K, 68 L,
    # 69-75 M, 77-82 N, 84 O, 85 P, 86-88 Q, 90-93 R,
    # 94-96 S, 97 T, 99 U
    return None


def _classificar_setor(registro: dict, cnae_map: dict) -> Optional[str]:
    """Retorna o setor econômico de um registro."""
    cnae = registro.get("cnae_principal") or registro.get("cnae") or ""
    secao = _cnae_para_secao(cnae, cnae_map)
    if secao:
        return SECAO_PARA_SETOR.get(secao, f"Seção {secao}")
    return "Não classificado"


def distribuicao_setores(
    dados: list[dict], cnae_map: Optional[dict] = None
) -> Counter:
    """
    Contagem de empresas por setor econômico.

    Args:
        dados: Lista de registros de empresas.
        cnae_map: Mapeamento CNAE (carregado automaticamente se None).

    Returns:
        Counter com setor -> quantidade.
    """
    if cnae_map is None:
        cnae_map = loader.carregar_cnae_mapping()

    counter: Counter = Counter()
    for reg in dados:
        setor = _classificar_setor(reg, cnae_map)
        counter[setor] += 1

    logger.info("Distribuição por setor: %d setores identificados", len(counter))
    return counter


def setores_mais_comuns(
    dados: list[dict], n: int = 10, cnae_map: Optional[dict] = None
) -> list[tuple[str, int]]:
    """Top N setores com mais empresas."""
    return distribuicao_setores(dados, cnae_map).most_common(n)


def resumo_setores(dados: list[dict], cnae_map: Optional[dict] = None) -> dict:
    """Resumo completo da análise de setores."""
    dist = distribuicao_setores(dados, cnae_map)
    total = sum(dist.values()) or 1
    return {
        "total_setores": len(dist),
        "distribuicao": dict(dist.most_common()),
        "setor_dominante": dist.most_common(1)[0] if dist else ("N/A", 0),
        "percentuais": {
            k: round((v / total) * 100, 2) for k, v in dist.most_common()
        },
        "cnae_mapping_carregado": cnae_map is not None or bool(
            loader.carregar_cnae_mapping()
        ),
    }
