# CNPJ Miner

Mining and analysis of public Brazilian CNPJ (CNPJ — Cadastro Nacional da Pessoa Jurídica) data from the Federal Revenue Service (Receita Federal).

## Overview

CNPJ Miner loads, processes, and analyzes public company registration data from Brazil. It provides insights into geographic distribution, economic sectors (CNAE), company size/porte classification, and temporal trends (opening dates, seasonality, average company age).

The raw public dataset from Receita Federal is massive (~20GB); this tool handles it with graceful degradation — it attempts to download real data, falls back to a realistic synthetic sample of 500 companies, and is designed for batch processing in production.

## Features

| Analysis       | Description                                                      |
|----------------|------------------------------------------------------------------|
| **Geography**  | Distribution by state (UF), region, top cities, density analysis |
| **Sectors**    | CNAE-based economic sector classification, sector dominance      |
| **Company Size** | MEI, ME, EPP, Medium, Large — based on estimated revenue       |
| **Temporal**   | Openings per year/month, seasonality, average company age        |
| **Visualization** | Bar charts, pie charts, histograms, annual evolution plots    |
| **Report**     | Complete Markdown report with embedded charts                   |

## Project Structure

```
cnpj-miner/
├── cnpj_miner.py          # Main CLI entry point
├── config.py              # Paths, CNAE mapping, BR states, constants
├── data/
│   └── loader.py          # Data loading (real download → sample fallback)
├── analyzers/
│   ├── geografia.py       # Geographic distribution & density
│   ├── setores.py         # CNAE sector classification
│   ├── porte.py           # Company size classification
│   └── temporal.py        # Temporal & seasonality analysis
├── visualizers/
│   └── graficos.py        # Matplotlib charts (bars, pie, histograms)
├── utils/
│   └── relatorio.py       # Markdown report generator
├── samples/
│   ├── cnpj_sample.csv    # 500 realistic synthetic CNPJ records
│   └── cnae_mapping.csv   # CNAE code → section/description mapping
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation

```bash
# 1. Clone or navigate to the project
cd cnpj-miner

# 2. Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

## Usage

### Quick start (all analyses, sample data)

```bash
python cnpj_miner.py --all --sample
```

### Individual analysis modules

```bash
# Geographic distribution
python cnpj_miner.py --geografia

# Economic sectors (CNAE)
python cnpj_miner.py --setores

# Company size/porte
python cnpj_miner.py --porte

# Temporal/seasonality
python cnpj_miner.py --temporal

# Combined analyses
python cnpj_miner.py --geografia --porte --temporal
```

### Generate report

```bash
python cnpj_miner.py --geografia --setores --porte --temporal --relatorio
# or simply:
python cnpj_miner.py --all
```

### Options

| Flag          | Description                                         |
|---------------|-----------------------------------------------------|
| `--all`       | Run all analysis modules + report                   |
| `--geografia` | Geographic analysis (UF, city, region distribution)  |
| `--setores`   | Economic sector analysis (CNAE)                     |
| `--porte`     | Company size classification                         |
| `--temporal`  | Temporal analysis (year/month, seasonality, age)    |
| `--sample`    | Use only the local sample CSV                       |
| `--relatorio` | Generate Markdown report                            |

## Sample Data

The project includes a synthetic dataset of **500 realistic Brazilian companies** (`samples/cnpj_sample.csv`) covering:

- **26 states + DF** — all Brazilian federative units
- **Diverse sectors** — agriculture, industry, commerce, services, technology, health, education
- **All porte categories** — MEI, ME, EPP, MEDIO, GRANDE
- **Realistic CNAE codes** — mapped from the official CNAE 2.0 classification
- **Temporal range** — companies opened from 1975 to 2024
- **~700 CNAE codes mapped** — included in `samples/cnae_mapping.csv`

## Technical Notes

- **CNAE changed in 2023** — some codes in the mapping may be outdated
- **Porte classification** is based on estimated revenue brackets; these values change annually per Brazilian legislation
- **Public Receita Federal data** is ~20GB; the project handles this via batch processing with checkpoint support
- The sample CSV uses semicolon (`;`) as delimiter, matching the official Receita Federal format
- Charts are saved as PNG at 150 DPI in the `output/graficos/` directory

## Data Source

- [Dados Abertos CNPJ — Receita Federal (gov.br)](https://dados.gov.br/dados/conjuntos-dados/cadastro-nacional-da-pessoa-juridica---cnpj)
- [CNAE 2.0 Classification — IBGE](https://cnae.ibge.gov.br/)

## Author

**Guilherme Crepaldi**

## License

MIT — free to use, modify, and distribute.

