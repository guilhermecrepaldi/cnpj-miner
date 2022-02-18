"""
Carregamento dos dados de CNPJ.
Author: Guilherme Crepaldi
Tenta baixar dados reais da Receita Federal, com fallback para amostra local.
"""

import csv
import io
import zipfile
import logging
import requests
from pathlib import Path
from typing import Optional

import config

logger = logging.getLogger("cnpj-miner.loader")


def _baixar_csv_real(caminho_destino: Path) -> bool:
    """
    Tenta baixar os dados mais recentes da Receita Federal.

    Dados abertos da Receita são gigantescos (~20GB). Processo em batches.
    Aqui baixamos apenas o primeiro lote (Empresa0.csv.zip) como demonstração.
    """
    # Simula tentativa de download — dados reais exigem batch processing
    logger.info("Tentando baixar dados da Receita Federal...")
    logger.warning(
        "Dados públicos da Receita Federal somam ~20GB. "
        "Em produção, use download em batches com retry e checkpoint."
    )

    url = config.URL_DADOS_RECEITA.format(ano=2024)
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
            # Extrai apenas o primeiro CSV do lote
            csv_files = [f for f in z.namelist() if f.endswith(".csv")]
            if not csv_files:
                raise FileNotFoundError("Nenhum CSV encontrado no ZIP")
            with z.open(csv_files[0]) as f_src:
                with open(caminho_destino, "wb") as f_dst:
                    f_dst.write(f_src.read())
        logger.info("Download concluído: %s", caminho_destino)
        return True
    except Exception as exc:
        logger.warning("Falha no download (%s). Usando amostra local.", exc)
        return False


def carregar_dados(caminho: Optional[Path] = None) -> list[dict]:
    """
    Carrega dados de CNPJ de um CSV. Fallback para amostra local se não existir.

    Args:
        caminho: Caminho para o CSV. Se None, tenta dados reais e depois amostra.

    Returns:
        Lista de dicionários com os dados de cada empresa.
    """
    if caminho is None:
        caminho = config.CSV_REAL
        if not caminho.exists():
            _baixar_csv_real(caminho)

    if not caminho.exists():
        logger.info("Dados reais indisponíveis. Usando amostra: %s", config.CSV_SAMPLE)
        caminho = config.CSV_SAMPLE

    if not caminho.exists():
        raise FileNotFoundError(
            f"Nenhum dado encontrado. Coloque um CSV em {config.CSV_SAMPLE} "
            "ou configure o download dos dados públicos."
        )

    registros = []
    with open(caminho, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for linha in reader:
            # Ignora linhas completamente vazias
            if any(v.strip() for v in linha.values()):
                registros.append(linha)

    logger.info("Carregados %d registros de %s", len(registros), caminho.name)
    return registros


def carregar_amostra() -> list[dict]:
    """Atalho para carregar apenas a amostra fictícia."""
    return carregar_dados(config.CSV_SAMPLE)


def carregar_cnae_mapping() -> dict[str, dict]:
    """
    Carrega o mapeamento de CNAE (código -> seção, descrição).

    CNAE mudou em 2023, alguns códigos podem estar desatualizados
    no arquivo de mapeamento fornecido.
    """
    mapa: dict[str, dict] = {}
    path = config.CNAE_MAP
    if not path.exists():
        logger.warning("Arquivo de mapeamento CNAE não encontrado: %s", path)
        return mapa

    with open(path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for linha in reader:
            codigo = linha.get("codigo", "").strip()
            if codigo:
                mapa[codigo] = {
                    "secao": linha.get("secao", "").strip(),
                    "descricao": linha.get("descricao", "").strip(),
                    "divisao": linha.get("divisao", "").strip(),
                }
    logger.info("Carregados %d códigos CNAE", len(mapa))
    return mapa
