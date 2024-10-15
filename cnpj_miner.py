#!/usr/bin/env python3
"""
CNPJ Miner — CLI para mineração de dados públicos de CNPJ.
Author: Guilherme Crepaldi

Analisa distribuição geográfica, setores econômicos, porte das empresas,
idade média, sazonalidade e crescimento por região.

Uso:
    python cnpj_miner.py --all
    python cnpj_miner.py --geografia
    python cnpj_miner.py --setores
    python cnpj_miner.py --porte
    python cnpj_miner.py --temporal
    python cnpj_miner.py --sample        # usa apenas a amostra local

Exemplos:
    python cnpj_miner.py --all --sample
    python cnpj_miner.py --geografia --porte --sample
"""

import argparse
import logging
import sys
import os
from pathlib import Path

# Garante que o diretório raiz do projeto esteja no sys.path
_proj_root = Path(__file__).parent.resolve()
if str(_proj_root) not in sys.path:
    sys.path.insert(0, str(_proj_root))

import config
from data.loader import carregar_dados, carregar_amostra, carregar_cnae_mapping
from analyzers import geografia, setores, porte as porte_analyzer, temporal
from visualizers import graficos
from reporting import relatorio as relatorio_mod

# ── Configuração de logging ────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format=config.LOG_FORMAT,
    datefmt=config.LOG_DATE_FORMAT,
)
logger = logging.getLogger("cnpj-miner.cli")


def executar_analise_geografica(dados: list[dict]) -> dict:
    """Executa análise geográfica e gera gráficos."""
    print("\n📊  ANALISANDO GEOGRAFIA...")
    resumo = geografia.resumo_geografico(dados)

    print(f"  • Estados encontrados: {resumo['total_ufs']}")
    for uf, qtd in list(resumo['distribuicao_uf'].items())[:5]:
        print(f"     - {uf}: {qtd} empresas")
    print(f"  • Top cidades: {resumo['top_10_cidades'][0]['cidade']}/{resumo['top_10_cidades'][0]['uf']} "
          f"({resumo['top_10_cidades'][0]['empresas']} empresas)")

    # Gráficos
    uf_counter = geografia.distribuicao_por_estado(dados)
    caminhos = {}
    if uf_counter:
        caminhos["geografia_uf"] = str(
            graficos.grafico_barras(
                uf_counter,
                titulo="Distribuição de Empresas por Estado",
                xlabel="UF",
                nome_arquivo="geografia_uf.png",
            )
        )

    return resumo, caminhos


def executar_analise_setores(dados: list[dict]) -> tuple:
    """Executa análise de setores e gera gráficos."""
    print("\n🏭  ANALISANDO SETORES...")
    cnae_map = carregar_cnae_mapping()
    resumo = setores.resumo_setores(dados, cnae_map)

    if resumo["setor_dominante"]:
        print(f"  • Setor dominante: {resumo['setor_dominante'][0]} "
              f"({resumo['setor_dominante'][1]} empresas)")
    print(f"  • Total de setores: {resumo['total_setores']}")

    # Gráficos
    dist = setores.distribuicao_setores(dados, cnae_map)
    caminhos = {}
    if dist:
        caminhos["setores"] = str(
            graficos.grafico_barras(
                dist,
                titulo="Distribuição de Empresas por Setor",
                xlabel="Setor",
                nome_arquivo="setores.png",
                top_n=12,
                rotacao_x=45,
            )
        )
        caminhos["setores_pizza"] = str(
            graficos.grafico_pizza(
                dist,
                titulo="Distribuição de Setores (%)",
                nome_arquivo="setores_pizza.png",
            )
        )

    return resumo, caminhos


def executar_analise_porte(dados: list[dict]) -> tuple:
    """Executa análise de porte e gera gráficos."""
    print("\n🏢  ANALISANDO PORTE DAS EMPRESAS...")
    resumo = porte_analyzer.resumo_porte(dados)

    print(f"  • Porte dominante: {resumo['porte_dominante'][0]} "
          f"({resumo['porte_dominante'][1]} empresas)")
    for porte in config.PORTE_ORDEM:
        qtd = resumo["distribuicao"].get(porte, 0)
        pct = resumo["percentuais"].get(porte, 0)
        print(f"     - {porte}: {qtd} ({pct}%)")

    # Gráficos
    dist = porte_analyzer.distribuicao_porte(dados)
    caminhos = {}
    if dist:
        caminhos["porte"] = str(
            graficos.grafico_barras(
                dist,
                titulo="Distribuição por Porte das Empresas",
                xlabel="Porte",
                nome_arquivo="porte.png",
            )
        )
        caminhos["porte_pizza"] = str(
            graficos.grafico_pizza(
                dist,
                titulo="Distribuição de Porte (%)",
                nome_arquivo="porte_pizza.png",
            )
        )

    return resumo, caminhos


def executar_analise_temporal(dados: list[dict]) -> tuple:
    """Executa análise temporal e gera gráficos."""
    print("\n📅  ANALISANDO DADOS TEMPORAIS...")
    resumo = temporal.resumo_temporal(dados)

    print(f"  • Idade média empresas: {resumo['idade_media_anos']} anos")
    saz = resumo.get("sazonalidade", {})
    print(f"  • Mês com mais aberturas: {saz.get('mes_mais_empresas', 'N/A')}")
    print(f"  • Mês com menos aberturas: {saz.get('mes_menos_empresas', 'N/A')}")

    # Gráficos
    caminhos = {}
    por_ano = temporal.empresas_por_ano(dados)
    if por_ano:
        caminhos["temporal_evolucao"] = str(
            graficos.grafico_evolucao_anual(
                dict(por_ano),
                nome_arquivo="evolucao_anual.png",
            )
        )

    por_mes = temporal.empresas_por_mes(dados)
    if por_mes:
        meses_nomes = {
            1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
            5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
            9: "Set", 10: "Out", 11: "Nov", 12: "Dez",
        }
        meses_renomeados = {meses_nomes[m]: qtd for m, qtd in por_mes.items()}
        from collections import Counter
        c = Counter(meses_renomeados)
        caminhos["temporal_sazonalidade"] = str(
            graficos.grafico_barras(
                c,
                titulo="Sazonalidade — Empresas Abertas por Mês",
                xlabel="Mês",
                nome_arquivo="sazonalidade.png",
            )
        )

    # Idade média — histograma
    from analyzers.temporal import _parse_data
    from datetime import date
    hoje = date.today()
    idades = []
    for reg in dados:
        dt = _parse_data(reg.get("data_abertura"))
        if dt:
            delta = hoje - dt.date()
            idades.append(round(delta.days / 365.25, 1))
    if idades:
        caminhos["temporal_idade_hist"] = str(
            graficos.grafico_histograma(
                idades,
                titulo="Distribuição da Idade das Empresas (anos)",
                xlabel="Idade (anos)",
                nome_arquivo="idade_empresas.png",
            )
        )

    return resumo, caminhos


def gerar_relatorio_final(
    resumo_geo: dict,
    resumo_set: dict,
    resumo_port: dict,
    resumo_temp: dict,
    caminhos_graficos: dict[str, str],
):
    """Gera relatório markdown consolidado."""
    print("\n📝  GERANDO RELATÓRIO...")
    md = relatorio_mod.gerar_relatorio(
        resumo_geo=resumo_geo,
        resumo_setores=resumo_set,
        resumo_porte=resumo_port,
        resumo_temporal=resumo_temp,
        caminhos_graficos=caminhos_graficos,
    )
    print(f"  ✓ Relatório salvo em: {config.RELATORIO_MD}")
    return md


def main():
    parser = argparse.ArgumentParser(
        description="CNPJ Miner — Mineração de dados públicos de CNPJ",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  %(prog)s --all                    # executa todas as análises
  %(prog)s --all --sample           # usa apenas amostra local
  %(prog)s --geografia --porte      # análises específicas
  %(prog)s --setores --temporal     # setores + tempo
        """,
    )

    parser.add_argument(
        "--all", action="store_true",
        help="Executa todas as análises (geografia, setores, porte, temporal)"
    )
    parser.add_argument(
        "--geografia", action="store_true",
        help="Análise geográfica (distribuição por UF, cidade, região)"
    )
    parser.add_argument(
        "--setores", action="store_true",
        help="Análise de setores econômicos (CNAE)"
    )
    parser.add_argument(
        "--porte", action="store_true",
        help="Análise de porte das empresas (MEI, ME, EPP, Médio, Grande)"
    )
    parser.add_argument(
        "--temporal", action="store_true",
        help="Análise temporal (abertura por ano/mês, sazonalidade, idade)"
    )
    parser.add_argument(
        "--sample", action="store_true",
        help="Usa apenas a amostra local (não tenta baixar dados reais)"
    )
    parser.add_argument(
        "--relatorio", action="store_true",
        help="Gera relatório Markdown ao final"
    )

    args = parser.parse_args()

    # Se nenhum argumento foi passado, mostra help
    if not any([args.all, args.geografia, args.setores, args.porte, args.temporal]):
        parser.print_help()
        sys.exit(0)

    # ── Carregamento de dados ──────────────────────────────────────────────
    print("=" * 60)
    print("  CNPJ MINER — Mineração de Dados de CNPJ")
    print("=" * 60)

    if args.sample:
        print("\n📂  Modo: apenas amostra local")
        dados = carregar_amostra()
    else:
        print("\n📂  Carregando dados...")
        dados = carregar_dados()

    print(f"  → {len(dados)} empresas carregadas\n")

    # ── Execução das análises ──────────────────────────────────────────────
    analises_executadas = []
    caminhos_graficos = {}

    resumo_geo = {}
    resumo_set = {"distribuicao": {}, "percentuais": {}, "total_setores": 0, "setor_dominante": ("N/A", 0)}
    resumo_port = {"distribuicao": {}, "percentuais": {}, "porte_dominante": ("N/A", 0)}
    resumo_temp = {
        "idade_media_anos": None,
        "sazonalidade": {},
        "empresas_por_ano": {},
        "empresas_por_ano_mes": {},
    }

    if args.all or args.geografia:
        resumo_geo, geo_caminhos = executar_analise_geografica(dados)
        caminhos_graficos.update(geo_caminhos)
        analises_executadas.append("geografia")

    if args.all or args.setores:
        resumo_set, set_caminhos = executar_analise_setores(dados)
        caminhos_graficos.update(set_caminhos)
        analises_executadas.append("setores")

    if args.all or args.porte:
        resumo_port, port_caminhos = executar_analise_porte(dados)
        caminhos_graficos.update(port_caminhos)
        analises_executadas.append("porte")

    if args.all or args.temporal:
        resumo_temp, temp_caminhos = executar_analise_temporal(dados)
        caminhos_graficos.update(temp_caminhos)
        analises_executadas.append("temporal")

    # ── Relatório ──────────────────────────────────────────────────────────
    if args.relatorio or args.all:
        gerar_relatorio_final(
            resumo_geo or geografia.resumo_geografico(dados),
            resumo_set,
            resumo_port,
            resumo_temp,
            caminhos_graficos,
        )

    print("\n" + "=" * 60)
    print("  ✅  ANÁLISE CONCLUÍDA")
    print(f"  Análises executadas: {', '.join(analises_executadas)}")
    print(f"  Gráficos salvos em: {config.RELATORIO_IMG}")
    print(f"  Relatório: {config.RELATORIO_MD}")
    print("=" * 60)


if __name__ == "__main__":
    main()
