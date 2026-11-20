# Testes do extrator INMET

A suíte verifica a descoberta dos CSVs por ano, a preservação dos dados brutos,
a leitura sob demanda e o tratamento de falhas na extração. Usa arquivos
artificiais em `tmp_path` e o parser real da aplicação. A fixture redireciona a
raiz de `DataPaths`, e os testes de leitura sob demanda observam os leitores
reais. Os testes unitários funcionam sem o acervo local, rede ou notebooks. A
compatibilidade com um acervo histórico e a execução dos notebooks são
verificações de integração.

| Arquivo | Cobertura |
| --- | --- |
| [test_data_paths.py](test_data_paths.py) | Extensões CSV, ordenação, isolamento por ano e condições da pasta de origem |
| [test_extract_inmet.py](test_extract_inmet.py) | Identificadores, metadados, observações brutas, leitura sob demanda e acesso individual |
| [test_extract_inmet_errors.py](test_extract_inmet_errors.py) | Estrutura do CSV, continuidade do lote, diagnóstico e propagação de falhas da origem |
| [conftest.py](conftest.py) | Dados e diretórios temporários compartilhados pelos testes |

## Formato coberto

O formato exercitado tem oito linhas de metadados com pares de campo e valor,
cabeçalho na nona linha, Latin-1, separador de ponto e vírgula e vírgula decimal
nas observações. As fixtures usam as 19 colunas do perfil atual e aceitam a
coluna vazia opcional no fim, que pode aparecer como `Unnamed: 19`. Os testes
rejeitam chaves ausentes ou repetidas no bloco de metadados, campos faltantes ou
excedentes nas linhas, delimitador incompatível e cabeçalhos ausentes ou
incompatíveis com esse perfil. A coluna final sem nome é reservada ao campo
vazio. Outros perfis históricos precisam de inspeção antes de serem
incorporados. [Formato observado no acervo de 2024](../docs/fontes.md#formato-e-leitura)

Os nomes dos arquivos devem permitir identificar a estação e o ano. O ano
indicado no nome deve coincidir com o da pasta solicitada. A extração entrega
`(identificador, caminho, DataFrame)` em ordem de caminho, preservando acentos,
datas e horários como texto, zeros e negativos. Medições vazias permanecem
ausentes. Textos literais em metadados devem ser preservados conforme aparecem
na entrada.

## Falhas em arquivos e na origem

Uma falha localizada deve produzir um registro que identifique o arquivo pelo
nome ou caminho e descreva o problema. O lote deve omitir o arquivo inválido e
continuar até o próximo resultado válido. O mesmo vale para um nome que falhe
antes da leitura das observações. Um lote com todos os arquivos inválidos
termina com uma sequência vazia e um diagnóstico por arquivo. Os testes usam
`caplog` para capturar registros do `logging` padrão e verificam os elementos
essenciais da mensagem.

A origem é uma dependência do lote. Se a pasta do ano estiver ausente ou o
caminho apontar para um arquivo em vez de um diretório, a exceção é propagada.
Uma pasta existente e sem CSVs produz uma sequência vazia. As leituras
individuais podem propagar erros de acesso e `ValueError` ou subclasses para
estrutura incompatível. O diagnóstico com o arquivo é verificado no lote.

A descoberta dos caminhos pode acontecer antes da leitura. Criar o iterador
não deve carregar tabelas. A primeira chamada de `next()` lê o necessário
para produzir o primeiro resultado válido, e as chamadas seguintes retomam o
processamento.

## Execução

Na raiz do projeto, com `uv`:

```bash
uv run --locked pytest -v
uv run --locked pytest tests/test_data_paths.py -v
uv run --locked pytest tests/test_extract_inmet_errors.py::test_batch_continues_after_malformed_csv -v
uv run --locked pytest --lf -v
```

Com o ambiente local ativado:

```bash
uv sync --locked
source .venv/bin/activate
pytest -v
pytest tests/test_extract_inmet.py::test_metadata_preserves_literal_text -v
```

Use `--lf` para repetir as falhas da última execução e rode a suíte completa
após cada correção. `DID NOT RAISE` indica que uma leitura direta aceitou a
estrutura inválida. Uma exceção de arquivo que sai de `inmet_dataframes()`
indica interrupção do lote. Se a iteração terminar com resultados incorretos
ou sem o diagnóstico exigido, a comparação de resultados ou o teste de log
identifica a diferença.

## Estado da suíte

Em 19/11/2026, `uv run --locked --offline pytest -q` executou **60 cenários:
29 passaram, 31 falharam e nenhum foi ignorado**.

| Arquivo | Passaram | Falharam |
| --- | ---: | ---: |
| `test_data_paths.py` | 8 | 0 |
| `test_extract_inmet.py` | 19 | 3 |
| `test_extract_inmet_errors.py` | 2 | 28 |

- Passaram a descoberta e a ordenação dos CSVs, a propagação dos erros de
  origem, a leitura de arquivos válidos e a iteração sob demanda em lotes
  válidos.
- `NA`, `NULL` e `N/A` viram ausências nos metadados. Os leitores diretos podem
  lançar `UnboundLocalError` depois de capturar um erro do pandas, pois
  tentam devolver o resultado de uma leitura que falhou. Outros CSVs com
  estrutura inválida são aceitos.
- O lote pula arquivos quando a leitura de medições lança uma exceção e
  mantém um dicionário por caminho em `registry_erros`. O diagnóstico via
  `logging` exigido pela suíte ainda está pendente. A extração do identificador
  ocorre antes desse tratamento, por isso um nome curto pode interromper o
  lote. Também faltam a validação do ano no nome e o tratamento de duplicatas.

Com os mesmos testes e o código de `2e3230a`, a suíte teve 35 aprovações e
25 falhas. Os seis casos que passaram a falhar envolvem arquivo vazio,
metadados truncados ou com campos excedentes, cabeçalho ausente e linha de
observações com campos excedentes. Todos agora lançam `UnboundLocalError`
na leitura direta.

## Decisões em aberto e validação de qualidade

O teste de identificadores duplicados exige, no lote, no máximo um resultado
para a mesma estação e ano, e diagnóstico para cada arquivo excluído. A escolha
entre manter um dos arquivos ou rejeitar o grupo permanece em aberto. A suíte
usa o `logging` padrão, com liberdade para escolher o nível, o logger e o texto
exato das mensagens.

A aceitação de variações de cabeçalho em outros perfis, os valores vazios em
metadados, a precedência entre o WMO do arquivo e o código indicado no nome e
as regras de tipo e intervalo de `year` requerem decisões próprias. Calendário,
anos bissextos, ano das observações, horários UTC, timestamps duplicados e
validação numérica de medições pertencem à transformação ou à qualidade de
dados. Também ficam para essas etapas a interpretação de sentinelas como
`-9999`, os limites físicos e a cobertura temporal.
