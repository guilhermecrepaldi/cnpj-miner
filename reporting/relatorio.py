"""
Gerador de relatório em Markdown.
Author: Guilherme Crepaldi
Compila os resultados das análises em um documento formatado.
"""

import logging
from datetime import datetime

import config

logger = logging.getLogger("cnpj-miner.relatorio")


def gerar_relatorio(
    resumo_geo: dict,
    resumo_setores: dict,
    resumo_porte: dict,
    resumo_temporal: dict,
    caminho_relatorio: str | None = None,
    caminhos_graficos: dict[str, str] | None = None,
) -> str:
    """
    Gera relatório Markdown completo com todas as análises.

    Args:
        resumo_geo: Output de geografia.resumo_geografico()
        resumo_setores: Output de setores.resumo_setores()
        resumo_porte: Output de porte.resumo_porte()
        resumo_temporal: Output de temporal.resumo_temporal()
        caminho_relatorio: Onde salvar. Se None, usa config.RELATORIO_MD.
        caminhos_graficos: Dict com nomes dos gráficos gerados.

    Returns:
        Conteúdo do relatório em string.
    """
    caminho_relatorio = caminho_relatorio or str(config.RELATORIO_MD)
    caminhos_graficos = caminhos_graficos or {}

    md = []
    md.append("# Relatório de Mineração de CNPJ\n")
    md.append(
        f"**Gerado em:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
    )
    md.append("**Fonte:** Dados públicos da Receita Federal / Amostra sintética\n")
    md.append("---\n")

    # ── Resumo geral ───────────────────────────────────────────────────────
    md.append("## 1. Resumo Geral\n")
    md.append(f"- **Total de empresas analisadas:** {resumo_geo.get('total_empresas', 0)}\n")
    md.append(
        f"- **Estados presentes:** {resumo_geo.get('total_ufs', 0)} de 27\n"
    )
    md.append(f"- **Setores identificados:** {resumo_setores.get('total_setores', 0)}\n")
    md.append(f"- **Idade média das empresas:** {resumo_temporal.get('idade_media_anos', 'N/A')} anos\n")
    md.append(f"- **Porte dominante:** {resumo_porte.get('porte_dominante', ('N/A', 0))[0]}\n")
    md.append("\n")

    # ── Geografia ──────────────────────────────────────────────────────────
    md.append("## 2. Análise Geográfica\n")

    if caminhos_graficos.get("geografia_uf"):
        md.append(f"![Distribuição por UF]({caminhos_graficos['geografia_uf']})\n\n")

    md.append("### Distribuição por Região\n")
    md.append("| Região | Empresas |\n")
    md.append("|--------|---------|\n")
    for regiao, qtd in sorted(
        resumo_geo.get("distribuicao_regiao", {}).items(),
        key=lambda x: x[1], reverse=True
    ):
        md.append(f"| {regiao} | {qtd} |\n")
    md.append("\n")

    md.append("### Top 10 Cidades\n")
    md.append("| Cidade | UF | Empresas |\n")
    md.append("|--------|----|---------|\n")
    for item in resumo_geo.get("top_10_cidades", []):
        md.append(f"| {item['cidade']} | {item['uf']} | {item['empresas']} |\n")
    md.append("\n")

    # ── Setores ────────────────────────────────────────────────────────────
    md.append("## 3. Análise de Setores\n")

    if caminhos_graficos.get("setores"):
        md.append(f"![Distribuição por Setor]({caminhos_graficos['setores']})\n\n")

    md.append("### Distribuição por Setor\n")
    md.append("| Setor | Empresas | % |\n")
    md.append("|-------|---------|---|\n")
    for setor, qtd in resumo_setores.get("distribuicao", {}).items():
        pct = resumo_setores.get("percentuais", {}).get(setor, 0)
        md.append(f"| {setor} | {qtd} | {pct}% |\n")
    md.append("\n")

    # ── Porte ──────────────────────────────────────────────────────────────
    md.append("## 4. Análise de Porte\n")

    if caminhos_graficos.get("porte"):
        md.append(f"![Distribuição por Porte]({caminhos_graficos['porte']})\n\n")

    md.append("| Porte | Empresas | % |\n")
    md.append("|-------|---------|---|\n")
    for porte in config.PORTE_ORDEM:
        qtd = resumo_porte.get("distribuicao", {}).get(porte, 0)
        pct = resumo_porte.get("percentuais", {}).get(porte, 0)
        md.append(f"| {porte} | {qtd} | {pct}% |\n")
    md.append("\n")

    # ── Temporal ───────────────────────────────────────────────────────────
    md.append("## 5. Análise Temporal\n")

    if caminhos_graficos.get("temporal_evolucao"):
        md.append(
            f"![Evolução Anual]({caminhos_graficos['temporal_evolucao']})\n\n"
        )

    md.append("### Sazonalidade\n")
    md.append(f"- **Mês com mais aberturas:** {resumo_temporal.get('sazonalidade', {}).get('mes_mais_empresas', 'N/A')}\n")
    md.append(f"- **Mês com menos aberturas:** {resumo_temporal.get('sazonalidade', {}).get('mes_menos_empresas', 'N/A')}\n")
    md.append(f"- **Variação (max-min):** {resumo_temporal.get('sazonalidade', {}).get('variacao_percentual_max_min', 0)}%\n")
    md.append(f"- **Média mensal:** {resumo_temporal.get('sazonalidade', {}).get('media_mensal', 0)}\n\n")

    md.append("### Empresas por Ano\n")
    md.append("| Ano | Empresas |\n")
    md.append("|-----|---------|\n")
    for ano, qtd in sorted(resumo_temporal.get("empresas_por_ano", {}).items()):
        md.append(f"| {ano} | {qtd} |\n")
    md.append("\n")

    # ── Notas técnicas ─────────────────────────────────────────────────────
    md.append("## 6. Notas Técnicas\n")
    md.append("- CNAE mudou em 2023 — alguns códigos podem estar desatualizados no mapeamento.\n")
    md.append("- Classificação de porte baseada em faturamento estimado; valores mudam anualmente.\n")
    md.append("- Dados abertos da Receita Federal somam ~20GB; esta análise usou amostra.\n")
    md.append("- Para produção, recomenda-se processamento em batches com checkpoint.\n")
    md.append("- Fonte: [Dados Abertos CNPJ - Receita Federal](https://dados.gov.br/dados/conjuntos-dados/cadastro-nacional-da-pessoa-juridica---cnpj)\n")
    md.append("\n")

    conteudo = "\n".join(md)

    with open(caminho_relatorio, "w", encoding="utf-8") as f:
        f.write(conteudo)

    logger.info("Relatório salvo em: %s", caminho_relatorio)
    return conteudo
