"""
Configurações do projeto CNPJ Miner.
Author: Guilherme Crepaldi
Caminhos, mapeamento CNAE, estados brasileiros e constantes.
"""

import os
from pathlib import Path

# ── Caminhos base ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.resolve()
DATA_DIR = BASE_DIR / "data"
SAMPLES_DIR = BASE_DIR / "samples"
OUTPUT_DIR = BASE_DIR / "output"

# Garante que a pasta de output existe
OUTPUT_DIR.mkdir(exist_ok=True)

# ── Arquivos ───────────────────────────────────────────────────────────────────
CSV_REAL = DATA_DIR / "cnpj_real.csv"          # dados públicos verdadeiros
CSV_SAMPLE = SAMPLES_DIR / "cnpj_sample.csv"    # amostra fictícia
CNAE_MAP = SAMPLES_DIR / "cnae_mapping.csv"     # tabela de CNAE
RELATORIO_MD = OUTPUT_DIR / "relatorio.md"
RELATORIO_IMG = OUTPUT_DIR / "graficos"

# ── Estados brasileiros ────────────────────────────────────────────────────────
# Códigos UF usados na Receita Federal
ESTADOS_BR = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AP": "Amapá",
    "AM": "Amazonas",
    "BA": "Bahia",
    "CE": "Ceará",
    "DF": "Distrito Federal",
    "ES": "Espírito Santo",
    "GO": "Goiás",
    "MA": "Maranhão",
    "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais",
    "PA": "Pará",
    "PB": "Paraíba",
    "PR": "Paraná",
    "PE": "Pernambuco",
    "PI": "Piauí",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul",
    "RO": "Rondônia",
    "RR": "Roraima",
    "SC": "Santa Catarina",
    "SP": "São Paulo",
    "SE": "Sergipe",
    "TO": "Tocantins",
}

# Regiões
REGIOES = {
    "Norte":     ["AC", "AP", "AM", "PA", "RO", "RR", "TO"],
    "Nordeste":  ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"],
    "Centro-Oeste": ["DF", "GO", "MT", "MS"],
    "Sudeste":   ["ES", "MG", "RJ", "SP"],
    "Sul":       ["PR", "RS", "SC"],
}

# ── Porte por faturamento estimado (valores em R$) ─────────────────────────────
# MEI até 81k, ME até 360k, EPP até 4.8M, Médio até 300M, Grande > 300M
# Esses valores mudam todo ano — conferir legislação atualizada
PORTE_LIMITES = {
    "MEI":    81_000,
    "ME":    360_000,
    "EPP":  4_800_000,
    "MEDIO": 300_000_000,
    "GRANDE": float("inf"),
}

PORTE_ORDEM = ["MEI", "ME", "EPP", "MEDIO", "GRANDE"]

# ── URLs dos dados abertos da Receita Federal ──────────────────────────────────
# Fonte: https://dados.gov.br/dados/conjuntos-dados/cadastro-nacional-da-pessoa-juridica---cnpj
URL_DADOS_RECEITA = (
    "https://arquivos.receitafederal.gov.br/cnpj/"
    "dados_abertos_cnpj/{ano}/Layout.zip"
)

# ── Colunas esperadas no CSV de amostra ────────────────────────────────────────
COLUNAS_SAMPLE = [
    "cnpj", "razao_social", "nome_fantasia", "cnae_principal",
    "cnae_secundaria", "natureza_juridica", "porte",
    "situacao_cadastral", "data_abertura", "uf", "cidade",
    "bairro", "cep", "logradouro", "numero", "complemento",
    "capital_social", "email", "telefone",
]

# ── Logging ────────────────────────────────────────────────────────────────────
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
