# Notas do Projeto — CNPJ Miner

## Ideia Original
Ferramenta CLI para baixar, processar e analisar os dados públicos de CNPJ
da Receita Federal. Foco em análise exploratória de dados (EDA).

## Status Atual
✅ Estrutura completa
✅ CLI funcional com argparse
✅ Amostra sintética com 500 CNPJs realistas
✅ Mapeamento CNAE com ~700 códigos
✅ 4 módulos de análise (geografia, setores, porte, temporal)
✅ Visualizações com matplotlib
✅ Relatório markdown
✅ Fallback dados reais → amostra local
✅ Comentários em pt-br no código
✅ README em inglês profissional

## Pendências / Ideias Futuras
- [ ] Download real em batches com checkpoint (dados ~20GB)
- [ ] Mapa coroplético do Brasil por densidade de empresas
- [ ] Dashboard interativo (Streamlit)
- [ ] Exportar para Excel/CSV com análises
- [ ] Cache de download para evitar re-baixar
- [ ] Testes unitários com pytest
- [ ] CI/CD GitHub Actions
- [ ] Dockerfile para container
- [ ] Análise de CNAE secundária (empresas com múltiplas atividades)
- [ ] Correlação entre capital social e porte
- [ ] API de consulta rápida (Flask/FastAPI)

## Autor

**Guilherme Crepaldi**

## Observações Técnicas

### CNAE
- CNAE mudou em 2023 (CNAE 2.0 → CNAE 2.1).
- Alguns códigos antigos podem ter sido descontinuados ou alterados.
- O mapeamento incluso usa predominantemente CNAE 2.0 (vigente até 2022).

### Porte
- MEI: faturamento ≤ R$ 81.000,00 (2024)
- ME: faturamento ≤ R$ 360.000,00
- EPP: faturamento ≤ R$ 4.800.000,00
- Médio: faturamento ≤ R$ 300.000.000,00
- Grande: faturamento > R$ 300.000.000,00
- Valores atualizados periodicamente pelo governo.

### Dados Públicos
- URL oficial: https://arquivos.receitafederal.gov.br/cnpj/dados_abertos_cnpj/
- Formato: CSV com delimiter ';', encoding utf-8-sig
- Arquivos grandes: layout.zip ~300MB, descompactado ~2GB por lote
- Total aproximado: 20GB para todo o dataset

### Amostra
- 500 empresas sintéticas mas com dados coerentes
- Distribuição geográfica proporcional aproximada (SP mais empresas)
- Setores variados (comércio, serviços, indústria, agro)
- Datas realistas (1975-2024)
- CNPJs no formato válido (XX.XXX.XXX/XXXX-XX)

