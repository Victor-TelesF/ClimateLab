# ClimateLab

Laboratório de investigação ambiental e ciência de dados com Python. O projeto
explora como temperatura, umidade e chuva variam no tempo, como identificar
extremos e períodos secos e como a cobertura dos dados afeta essas análises.

## Estado da implementação

O recorte inicial é uma estação do INMET em 2024. Já é possível ler os CSVs
locais, separar metadados de medições e inspecionar uma amostra no notebook de
inventário. A validação, os indicadores e a comparação com a reanálise ERA5
via Open-Meteo estão no planejamento. [Fontes de dados](docs/fontes.md)

## Execução local

Com Python 3.14 e uv, execute na raiz do projeto.

```bash
uv sync --locked
uv run --locked jupyter lab
```

Para executar o notebook, obtenha os CSVs do INMET e mantenha os nomes
originais em `data/raw/inmet/2024/`. [Guia de preparação](docs/preparacao.md) ·
[Notebook de inventário](notebooks/01-inventario.ipynb)

## Roadmap

Os 30 desafios partem da leitura e da qualidade dos dados, passam por integração
de fontes, análise de eventos e modelagem e chegam à construção de uma engine
reutilizável. [Trilha de investigação](docs/desafios.md)

## Documentação

- [Desenvolvimento](docs/desenvolvimento.md) — arquitetura, decisões técnicas e histórico.
- [Testes](tests/README.md) — contrato de extração e execução da suíte.
