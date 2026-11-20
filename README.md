# 🌦️ ClimateLab

[![Python 3.14](https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![uv](https://img.shields.io/badge/uv-Astral-blueviolet?style=for-the-badge&logo=astral&logoColor=white)](https://docs.astral.sh/uv/)
[![pytest](https://img.shields.io/badge/Tests-pytest-orange?style=for-the-badge&logo=pytest&logoColor=white)](tests/README.md)
[![pandas](https://img.shields.io/badge/pandas-3.x-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)

O ClimateLab é um laboratório de engenharia e análise de dados meteorológicos. Investiga como temperatura, umidade e chuva variam ao longo do tempo e como as lacunas de observação afetam a identificação de extremos e períodos secos.

## Estado atual

A extração localiza os CSVs anuais de estações automáticas do INMET, identifica os arquivos pela estação e pelo ano e permite ler metadados e medições separadamente. A leitura em lote carrega um arquivo por vez. O notebook de inventário ilustra a exploração dos dados de 2024. A validação da estrutura dos CSVs e a continuidade após erros de leitura seguem em desenvolvimento. [Arquitetura da extração](docs/arquitetura.md) · [Inventário](notebooks/01-inventario.ipynb)

## Execução local

Na raiz do repositório, use Python 3.14 e uv.

```bash
uv sync --locked
uv run --locked pytest -q
```

Os testes usam CSVs sintéticos. Para explorar dados reais, extraia os CSVs em `data/raw/inmet/2024/` e inicie o JupyterLab com `uv run --locked jupyter lab`. [Preparação dos dados e primeira leitura](docs/preparacao.md) · [Cenários e resultado da suíte](tests/README.md)

## Próximas etapas

- Validar a estrutura dos CSVs e tratar lacunas, sentinelas e datas.
- Coletar dados ERA5 via Open-Meteo e alinhar as fontes no espaço e no tempo.
- Medir a cobertura das séries e investigar extremos térmicos e períodos secos.

Ao publicar recortes ou análises, atribua os dados ao INMET e registre a estação, o período e o arquivo de origem. [Fontes meteorológicas e unidades](docs/fontes.md)
