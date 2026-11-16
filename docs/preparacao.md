# Registro da preparação — 15/11/2026

## Ambiente e verificações realizadas

- Sistema: Ubuntu 26.04 LTS no WSL2, x86_64.
- Python: 3.14.4; `uv`: 0.12.3. Ambiente criado em `.venv`.
- A pasta continha somente o README inicial; nenhum arquivo ou ambiente do
  CineMetrics foi encontrado nesta pasta.
- Caderno anexado copiado integralmente para `docs/desafios.md`.
- Dependências instaladas e fixadas em `uv.lock`; `uv lock --check` e
  `uv pip check` passaram.
- Imports confirmados no Python de `.venv`: pandas 3.1.1, NumPy 2.5.4,
  Matplotlib 3.11.2, Seaborn 0.13.2, JupyterLab 4.6.6, ipykernel 7.4.0,
  PyArrow 26.0.1 e httpx 0.28.1. O pacote local também foi importado.
- Kernel **ClimateLab (.venv)** registrado somente dentro de `.venv`, em
  `.venv/share/jupyter/kernels/climatelab/`, com executável desta instalação.
- `notebooks/01-inventario.ipynb` validado com `nbformat` e executado por inteiro
  com `nbclient`, a partir da raiz, sem erros e sem tabelas ou gráficos gerados.
- Configuração do VS Code aponta para `.venv/bin/python` e usa a raiz como
  diretório dos notebooks. Extensões oficiais Python e Jupyter já instaladas.
  A seleção do kernel e a aparência na interface do VS Code não foram
  verificadas; siga os passos do README para selecionar o ambiente e abrir o notebook.
- Dados, ambiente, caches e resultados abrangidos pelo `.gitignore`.
- Nenhum commit, publicação ou solução dos desafios foi produzido.

## Histórico do download automatizado

O portal oficial foi consultado e o link **ANO 2024 (AUTOMÁTICA)** aponta para
<https://portal.inmet.gov.br/uploads/dadoshistoricos/2024.zip>.

O acesso pelo terminal e o download foram tentados no ambiente restrito e
repetidos fora dele. Falharam com conexão encerrada pelo destino:

```text
ConnectionResetError: [Errno 104] Connection reset by peer
curl: (56) Recv failure: Connection reset by peer
http_code=000
size_download=0
```

O navegador de pesquisa identificou o recurso como `application/zip`, mas não
oferece suporte à entrega desse binário ao workspace. Na preparação inicial,
nenhum ZIP foi salvo e nenhum CSV foi extraído ou lido. A aquisição manual
posterior, descrita abaixo, resolveu essa pendência.

## Dados locais organizados

Em **15/11/2026**, o estudante informou ter baixado e extraído o pacote. Foram
encontrados `2024.zip` e 565 CSVs na raiz e movidos para:

- `data/raw/inmet/2024.zip`: ZIP original, com 102.772.199 bytes.
- `data/raw/inmet/2024/`: 565 CSVs com seus nomes originais.
- `data/raw/inmet/aquisicao-2024.json`: registro atualizado da aquisição e das
  verificações, preservando os erros anteriores como histórico.

Todos os nomes e tamanhos dos CSVs coincidem com o diretório do ZIP, sem arquivos
ausentes ou adicionais. A movimentação preservou dispositivo, inode, tamanho e
data de modificação de cada arquivo. O SHA-256 do ZIP permaneceu igual:

```text
0a7f89de57427f79b6f82943b2f7f2e932202d9253e34bf25629ed088d108ae7
```

Foi feita somente uma leitura técnica das primeiras dez linhas, em bytes, de:

```text
data/raw/inmet/2024/INMET_CO_DF_A001_BRASILIA_01-01-2024_A_31-12-2024.CSV
```

Esse arquivo também foi comparado integralmente com sua entrada no ZIP e é
idêntico. Não foram diagnosticados cabeçalhos, codificação, colunas ou cobertura,
nem feitas limpeza ou análises. A escolha da estação para estudo continua sendo
do estudante. ZIP, CSVs e registro local de aquisição ficam ignorados pelo Git.

**API:** a documentação e as condições foram consultadas, mas a conectividade
do endpoint de dados não foi testada. A consulta opcional foi omitida porque
não havia CSV local na preparação inicial. A organização posterior não executou
consultas à API.

## Obter os CSVs manualmente

Referência para uma nova cópia: o pacote atual já está organizado e verificado;
não é necessário repetir estes passos para começar o desafio 01.

1. Abra o [portal oficial](https://portal.inmet.gov.br/dadoshistoricos) no seu
   navegador e clique em **ANO 2024 (AUTOMÁTICA)**. O
   [link direto](https://portal.inmet.gov.br/uploads/dadoshistoricos/2024.zip)
   foi confirmado nessa página.
2. Salve somente esse pacote como `data/raw/inmet/2024.zip`. Se baixar no
   Windows, copie o ZIP para essa pasta do projeto no WSL.
3. Na raiz do projeto, com a `.venv` ativada, confira e extraia:

   ```bash
   python -m zipfile -t data/raw/inmet/2024.zip
   python -m zipfile -e data/raw/inmet/2024.zip data/raw/inmet/2024
   ```

4. Preserve o ZIP e os arquivos extraídos sem modificações. Em uma nova aquisição,
   atualize a data e as verificações em `data/raw/inmet/aquisicao-2024.json`.
5. No explorador do VS Code, procure um `.CSV` ou `.csv` dentro de
   `data/raw/inmet/2024/`. Abra apenas um arquivo para conferir a extração.
6. Abra `notebooks/01-inventario.ipynb`, selecione **ClimateLab (.venv)** e
   comece o desafio 01 com esse arquivo. Sua escolha de estação, o inventário e
   o diagnóstico do conteúdo continuam sendo parte do exercício.

Não repita a extração sobre arquivos de estudo já modificados.
