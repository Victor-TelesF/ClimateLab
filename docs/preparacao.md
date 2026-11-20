# Preparação local

Este guia descreve o ambiente, a aquisição do pacote INMET de 2024 e as
verificações necessárias para iniciar a leitura. Os dados permanecem locais e
não acompanham o clone do repositório.

## Requisitos do ambiente

O projeto requer Python `>=3.14,<3.15`, com `3.14.4` em `.python-version`,
e [uv](https://docs.astral.sh/uv/). Na raiz do repositório:

```bash
uv sync --locked
uv run --locked python --version
uv run --locked jupyter lab
```

O `uv` instala o pacote local e as dependências de `uv.lock`, incluindo pytest
no grupo de desenvolvimento. A configuração do VS Code aponta para
`.venv/bin/python` e usa a raiz como diretório de trabalho dos notebooks.
O mesmo ambiente deve ser selecionado como kernel.

Para registrar um kernel com nome próprio dentro de `.venv`, opcionalmente:

```bash
uv run --locked python -m ipykernel install --sys-prefix --name climatelab --display-name "ClimateLab (.venv)"
```

O ambiente de referência usa Ubuntu 26.04 LTS no WSL2, x86_64, Python 3.14.4
e uv 0.12.3.

## Aquisição dos arquivos

### Obter os CSVs manualmente

1. No [portal oficial do INMET](https://portal.inmet.gov.br/dadoshistoricos),
   selecione **ANO 2024 (AUTOMÁTICA)**. O
   [ZIP de 2024](https://portal.inmet.gov.br/uploads/dadoshistoricos/2024.zip)
   também tem um endereço direto.
2. Salve o pacote em `data/raw/inmet/2024.zip`. Se o download ocorrer no
   Windows, copie-o para essa pasta no WSL.
3. Na raiz do projeto, confira o ZIP e extraia os arquivos em um destino novo:

   ```bash
   uv run --locked python -m zipfile -t data/raw/inmet/2024.zip &&
     mkdir data/raw/inmet/2024 &&
     uv run --locked python -m zipfile -e data/raw/inmet/2024.zip data/raw/inmet/2024
   ```

4. Preserve o ZIP e os CSVs sem alterações, com seus nomes originais. Registre
   origem, data, método, tamanho, hash e verificações da aquisição em
   `data/raw/inmet/aquisicao-2024.json`. Esse registro é local e manual.

Uma cópia já organizada não exige novo download ou extração. A extração não
deve sobrescrever arquivos existentes; transformações devem usar outro destino.

## Estrutura esperada dos dados

```text
data/
├── raw/
│   ├── inmet/
│   │   ├── 2024.zip
│   │   ├── aquisicao-2024.json
│   │   └── 2024/
│   │       └── INMET_..._A001_..._31-12-2024.CSV
│   └── open_meteo/             # Reservado para respostas brutas
└── processed/                 # Reservado para dados preparados
```

O nome abreviado acima ilustra a convenção; os nomes completos devem ser
mantidos. Resultados analíticos terão destino em `outputs/figures/` e
`outputs/tables/`. Esses diretórios, `data/processed/` e `data/raw/open_meteo/`
contêm apenas `.gitkeep` no estado atual. O `.gitignore` exclui dados, resultados,
ambiente e caches do versionamento.

## Preparação para processamento

`DataPaths.csv_paths(year)` lista os CSVs diretamente na pasta do ano.
`ExtractInmet(year)` usa essa lista para identificar arquivos e ler metadados
e medições separadamente. Os caminhos padrão são relativos à raiz do projeto.
Uma pasta ausente gera `FileNotFoundError`, e um arquivo no lugar da pasta gera
`NotADirectoryError`.

O formato atual de leitura considera oito linhas de metadados, cabeçalho na
nona linha, Latin-1, separador `;` e vírgula decimal nas medições. Esses
parâmetros devem ser conferidos antes de incorporar arquivos de outro formato.
As unidades e convenções temporais estão em [fontes.md](fontes.md).

### Primeira leitura

Com os CSVs em `data/raw/inmet/2024/`, rode o exemplo a partir da raiz em
`uv run --locked python`. Ele lê o primeiro arquivo na ordem de caminhos.

```python
from climatelab.etl.extract import ExtractInmet

extractor = ExtractInmet(year=2024)
identifier, csv_path = next(extractor.inmet_paths())
metadata = extractor.inmet_metadata(csv_path)
observations = extractor.inmet_dataframe(csv_path)
print(identifier, metadata.shape, observations.shape)
```

Em uma pasta sem CSVs, o `next()` do exemplo lança `StopIteration`. Para
selecionar uma estação, confira os identificadores de `inmet_paths()`, que
ainda podem se repetir. O notebook de inventário usa A620.
[Notebook de inventário](../notebooks/01-inventario.ipynb)

## Verificações de integridade e execução

Confira o ambiente, a integridade do ZIP e o hash da cópia baixada.

```bash
uv lock --check
uv pip check
uv run --locked python -m zipfile -t data/raw/inmet/2024.zip
sha256sum data/raw/inmet/2024.zip
```

O ZIP de referência tem 102.772.199 bytes. O SHA-256 registrado para essa
cópia é o seguinte.

```text
0a7f89de57427f79b6f82943b2f7f2e932202d9253e34bf25629ed088d108ae7
```

Para executar a suíte de extração, use `uv run --locked pytest`.
[Contrato e execução dos testes](../tests/README.md)

Os resultados da verificação do acervo, da execução dos notebooks e dos
testes estão no [histórico de desenvolvimento](desenvolvimento.md#histórico-de-desenvolvimento).
