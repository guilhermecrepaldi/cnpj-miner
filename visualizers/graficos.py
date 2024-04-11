"""
Gerador de gráficos: barras, pizza, histogramas para visualização dos dados.
Author: Guilherme Crepaldi
"""

import logging
from pathlib import Path
from collections import Counter
from typing import Optional

import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

import config

logger = logging.getLogger("cnpj-miner.graficos")

# Paleta de cores brasileira
CORES = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
    "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
    "#1a55a0", "#e65d00", "#1a8a1a", "#b31515", "#7b3fa0",
]

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "font.size": 10,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
})


def _salvar(fig, nome: str) -> Path:
    """Salva a figura no diretório de output."""
    config.RELATORIO_IMG.mkdir(parents=True, exist_ok=True)
    path = config.RELATORIO_IMG / nome
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info("Gráfico salvo: %s", path)
    return path


def grafico_barras(
    dados: Counter,
    titulo: str,
    xlabel: str = "",
    ylabel: str = "Quantidade",
    nome_arquivo: str = "barras.png",
    top_n: Optional[int] = None,
    rotacao_x: int = 45,
) -> Path:
    """Gráfico de barras vertical."""
    if top_n:
        items = dados.most_common(top_n)
    else:
        items = sorted(dados.items(), key=lambda x: x[1], reverse=True)

    if not items:
        logger.warning("Nenhum dado para gerar gráfico: %s", titulo)
        return _salvar(plt.figure(), nome_arquivo)

    labels, valores = zip(*items) if items else ([], [])

    fig, ax = plt.subplots(figsize=(10, 6))
    barras = ax.bar(range(len(labels)), valores, color=CORES[: len(labels)])
    ax.set_title(titulo, fontweight="bold")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=rotacao_x, ha="right")

    # Rótulos nas barras
    for bar, val in zip(barras, valores):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(valores) * 0.01,
            str(val),
            ha="center", va="bottom", fontsize=8,
        )

    fig.tight_layout()
    return _salvar(fig, nome_arquivo)


def grafico_pizza(
    dados: Counter,
    titulo: str,
    nome_arquivo: str = "pizza.png",
    top_n: int = 8,
) -> Path:
    """Gráfico de pizza com agrupamento de 'Outros'."""
    items = dados.most_common(top_n)
    outros = sum(v for _, v in dados.items()) - sum(v for _, v in items)

    labels = [item[0] for item in items]
    valores = [item[1] for item in items]
    if outros > 0:
        labels.append("Outros")
        valores.append(outros)

    if not valores:
        return _salvar(plt.figure(), nome_arquivo)

    fig, ax = plt.subplots(figsize=(8, 8))
    cores = CORES[: len(labels)]
    wedges, texts, autotexts = ax.pie(
        valores,
        labels=labels,
        autopct="%1.1f%%",
        startangle=90,
        colors=cores,
        textprops={"fontsize": 9},
    )
    for at in autotexts:
        at.set_fontsize(8)
        at.set_color("white")

    ax.set_title(titulo, fontweight="bold", pad=20)
    fig.tight_layout()
    return _salvar(fig, nome_arquivo)


def grafico_histograma(
    dados: list[float],
    titulo: str,
    xlabel: str = "Valor",
    ylabel: str = "Frequência",
    nome_arquivo: str = "histograma.png",
    bins: int = 20,
) -> Path:
    """Histograma para dados numéricos (ex: idade das empresas)."""
    if not dados:
        return _salvar(plt.figure(), nome_arquivo)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(dados, bins=bins, color=CORES[0], edgecolor="white", alpha=0.8)
    ax.set_title(titulo, fontweight="bold")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%d"))
    fig.tight_layout()
    return _salvar(fig, nome_arquivo)


def grafico_evolucao_anual(
    dados: dict[int, int],
    titulo: str = "Evolução de abertura de empresas por ano",
    nome_arquivo: str = "evolucao_anual.png",
) -> Path:
    """Gráfico de linha mostrando evolução ao longo dos anos."""
    if not dados:
        return _salvar(plt.figure(), nome_arquivo)

    anos = sorted(dados.keys())
    valores = [dados[a] for a in anos]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(anos, valores, marker="o", linestyle="-", color=CORES[0],
            linewidth=2, markersize=6)
    ax.fill_between(anos, valores, alpha=0.15, color=CORES[0])
    ax.set_title(titulo, fontweight="bold")
    ax.set_xlabel("Ano")
    ax.set_ylabel("Empresas abertas")
    ax.grid(axis="y", alpha=0.3)

    for ano, val in zip(anos, valores):
        ax.annotate(
            str(val), (ano, val),
            textcoords="offset points", xytext=(0, 10),
            ha="center", fontsize=8,
        )

    fig.tight_layout()
    return _salvar(fig, nome_arquivo)
