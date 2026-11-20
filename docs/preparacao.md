# Preparação local

## Ambiente Python

Use Python 3.14 e uv. Na raiz do repositório, o comando abaixo cria a `.venv` e instala o pacote local e as dependências do lockfile, incluindo pytest no grupo de desenvolvimento. [Instalação do uv](https://docs.astral.sh/uv/getting-started/installation/)

```bash
uv sync --locked
```

A suíte pode ser executada assim que o ambiente estiver pronto. [Execução e cobertura dos testes](../tests/README.md)

## Dados do INMET

1. No portal do INMET, selecione **ANO 2024 (AUTOMÁTICA)** e baixe o ZIP. Os arquivos meteorológicos são obtidos separadamente do clone. [Históricos anuais](https://portal.inmet.gov.br/dadoshistoricos)
2. Extraia os CSVs diretamente em `data/raw/inmet/2024/`, preservando seus nomes. O extrator procura os arquivos apenas nesse nível. Se já estiverem nessa pasta, siga para a leitura.
3. Para reproduzir o inventário, confirme que a pasta contém o CSV da estação A620. [Formato e identificação dos arquivos](fontes.md)

## Primeira leitura

Abra o interpretador com `uv run --locked python` na raiz do repositório. O exemplo usa o primeiro CSV na ordem de caminhos e mostra o identificador e as dimensões das duas tabelas.

```python
from climatelab.etl.extract import ExtractInmet

extrator = ExtractInmet(year=2024)
identificador, arquivo = next(extrator.inmet_paths())
metadados = extrator.inmet_metadata(arquivo)
medicoes = extrator.inmet_dataframe(arquivo)
print(identificador, metadados.shape, medicoes.shape)
```

Se o exemplo gerar `StopIteration`, a pasta anual existe, mas não contém CSVs diretamente nela. [Comportamento da descoberta](arquitetura.md#falhas-e-limites)

## Notebook de inventário

A partir da raiz, inicie o JupyterLab e abra o notebook. Use o kernel Python da `.venv` e execute as células em ordem. O inventário exibe a identificação da estação A620 e uma amostra das suas medições. [Abrir o inventário](../notebooks/01-inventario.ipynb)

```bash
uv run --locked jupyter lab
```
