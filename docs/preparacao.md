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
e uv 0.12.3. A seleção do kernel e a apresentação dos notebooks na interface
do VS Code não foram verificadas nesta revisão.

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

O exemplo do README lê um arquivo usando a interface atual. O notebook de
inventário exibe uma prévia de A620, e o de teste contém uma tentativa de
navegação entre arquivos via `input()`.
[Exemplo de leitura](../README.md#execução-local),
[inventário](../notebooks/01-inventario.ipynb) e [teste](../notebooks/teste.ipynb).

## Verificações de integridade e execução

Para conferir o ambiente e executar a suíte:

```bash
uv lock --check
uv pip check
uv run --locked pytest
```

As verificações locais de 19/11/2026 confirmaram os seguintes resultados.

- Compatibilidade do lockfile com o projeto e das dependências instaladas.
- ZIP com 102.772.199 bytes e SHA-256 igual ao registro da aquisição:

  ```text
  0a7f89de57427f79b6f82943b2f7f2e932202d9253e34bf25629ed088d108ae7
  ```

- Correspondência de nomes e tamanhos dos 565 CSVs com o diretório do ZIP.
  O CSV A001 de Brasília também coincide, byte a byte, com sua entrada no pacote.
- Execução do exemplo de leitura com A001: metadados com formato `(8, 2)` e
  medições com `(8784, 20)`. Essa contagem não comprova cobertura válida por variável.
- A leitura em lote retornou 565 tabelas e deixou `registry_erros` vazio
  nesse acervo local.
- Validade estrutural dos dois notebooks pelo `nbformat`. A execução de
  `01-inventario.ipynb` com `nbclient` exibiu duas tabelas de A620.
  Em `teste.ipynb`, entradas simuladas `0` e `1` encerraram a célula após
  o primeiro arquivo.
- A suíte executou 60 cenários, com falhas na preservação de texto nos
  metadados, na validação e no diagnóstico do lote.
  [Resultado detalhado da suíte](../tests/README.md#estado-da-suíte)

O checksum identifica a cópia adquirida. A comparação com o ZIP confere os
arquivos extraídos. A leitura em lote comprova que o pandas carregou as tabelas
neste ambiente. A auditoria da estrutura e da qualidade meteorológica das
565 séries continua pendente.

## Limitações conhecidas

O extrator ainda não valida integralmente nomes, metadados, colunas, datas,
horários ou medições. Campos textuais como `NA` e `NULL` podem virar ausências,
e a coluna vazia final permanece na tabela. Não há normalização temporal,
tratamento explícito de sentinelas, cálculo de cobertura ou exportação de dados
processados. Essas etapas estão no [planejamento](desafios.md).

O cliente Open-Meteo e a verificação da conectividade do endpoint continuam
pendentes. Os testes unitários usam CSVs artificiais. A execução dos notebooks
foi feita em kernel local, sem conferência da interface do VS Code.

## Histórico técnico

Na preparação de 15/11/2026, a versão inicial de `01-inventario.ipynb` foi
validada com `nbformat` e executada com `nbclient` a partir da raiz.

Em 15/11/2026, o download do ZIP pelo terminal falhou com encerramento da conexão
pelo destino, tanto no ambiente restrito quanto fora dele:

```text
ConnectionResetError: [Errno 104] Connection reset by peer
curl: (56) Recv failure: Connection reset by peer
http_code=000
size_download=0
```

O pacote foi adquirido manualmente e organizado no mesmo dia. O registro local
`data/raw/inmet/aquisicao-2024.json` preserva as tentativas e as verificações:
nomes e tamanhos de todos os CSVs, comparação integral de A001 com o ZIP e
preservação de dispositivo, inode, tamanho e data de modificação na movimentação.

Na aquisição inicial, a inspeção limitou-se às dez primeiras linhas de A001 em
bytes. O campo `csv_read_scope` do JSON descreve esse momento, não as leituras
posteriores pelo extrator e pelos notebooks. A verificação atual da cópia está
na seção de integridade acima.
