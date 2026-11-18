# Testes do extrator INMET

Execute os comandos na raiz do projeto:

```bash
uv sync --locked
uv run --locked pytest
```

Para acompanhar cada cenário ou parar na primeira falha:

```bash
uv run --locked pytest -v
uv run --locked pytest -x -v
```

Após uma correção, rode novamente os casos que falharam na última execução:

```bash
uv run --locked pytest --lf -v
```

Depois rode a suíte completa para verificar se a mudança afetou a leitura válida.

Para rodar apenas um grupo ou um caso:

```bash
uv run --locked pytest tests/test_extract_inmet.py tests/test_data_paths.py
uv run --locked pytest tests/test_extract_inmet_errors.py
uv run --locked pytest tests/test_extract_inmet_errors.py::test_rejects_duplicate_timestamps
```

## Organização

| Arquivo | O que verifica |
| --- | --- |
| `conftest.py` | CSVs artificiais em `tmp_path`, com metadados, acentos, vírgula decimal, zeros e ausências |
| `test_data_paths.py` | Filtro de extensão, ordenação, isolamento por ano e erros de diretório |
| `test_extract_inmet.py` | Leitura correta, preservação de valores, iteração e erros de acesso |
| `test_extract_inmet_errors.py` | Validações de entradas inválidas e diagnóstico das falhas |

Os testes usam o parser real e arquivos pequenos criados em diretórios temporários.
Não precisam dos 565 CSVs locais, de rede ou dos notebooks. A única substituição
na criação do extrator é a raiz de `DataPaths`; o teste da leitura sob demanda
também observa as chamadas reais de `inmet_dataframe()`.

## Como interpretar as falhas

Os testes representam o comportamento esperado, inclusive validações ainda não
implementadas. Não há `xfail` nem testes ignorados. Uma falha em
`test_extract_inmet_errors.py` indica que a entrada inválida não foi rejeitada
como esperado, que o erro não identifica o arquivo ou que houve perda de texto
original nos metadados. `DID NOT RAISE` significa que faltou rejeitar a entrada.

Na execução inicial de 17/11/2026, foram **83 cenários: 28 passaram e 55 falharam**.
Todos os casos de `test_data_paths.py` e `test_extract_inmet.py` passaram; as
falhas ficaram em `test_extract_inmet_errors.py`. Esse registro é uma referência
para acompanhar as próximas correções, não uma expectativa fixa de resultado.

O contrato de validação adotado nesta suíte é:

- `year` deve ser um inteiro de 1 a 9999; booleanos não são anos. Tipo incorreto
  causa `TypeError`; valor fora do intervalo causa `ValueError` no construtor.
- Nomes de arquivo devem conter estação e ano válidos. O ano precisa coincidir
  com o solicitado; identificadores estação/ano duplicados causam `ValueError`.
- A estação no nome deve coincidir com `CODIGO (WMO):` dos metadados.
- O formato testado tem oito campos obrigatórios de metadados, sem repetição ou
  valor vazio. Valores textuais como `NA`, `NULL` e `N/A` devem ser preservados.
- As observações têm as 19 colunas conhecidas, podendo incluir a coluna vazia
  final dos arquivos originais, também vazia nos registros. Estrutura truncada
  ou diferente deve ser rejeitada.
- Datas devem existir no calendário e pertencer ao ano solicitado. Horários
  devem seguir `HH00 UTC`, de `0000 UTC` a `2300 UTC`; duplicatas são rejeitadas.
- Medições devem ser numéricas ou ausentes. Zero e valores negativos válidos
  são preservados; registros sem nenhuma medição são permitidos.
- Conteúdo inválido causa `ValueError` (ou subclasse), incluindo **o nome do
  arquivo na mensagem**. Não se exige uma mensagem completa específica.
- A iteração em lote para no primeiro erro e informa o arquivo; não o ignora.
  Esta é a política escolhida para estes testes, sem implementar recuperação.
- Pasta existente sem CSVs produz uma sequência vazia. Arquivo ou pasta de ano
  inexistente mantém `FileNotFoundError`.

Essas regras tornam explícitas as expectativas para as próximas alterações;
não descrevem validações já concluídas. Outros formatos históricos podem exigir
novos cenários e uma revisão consciente do contrato.

## Fora deste contrato

Os testes não exigem converter datas para timestamp, remover `Unnamed: 19`,
normalizar metadados ou interpretar `-9999`. Essas são decisões de transformação.
Também não exigem 8.784 registros, cobertura completa ou limites físicos das
variáveis: arquivos parciais e medições ausentes continuam sendo dados possíveis.

Compatibilidade dos notebooks, o exemplo antigo do README e a execução a partir
de outra pasta com o caminho padrão são verificações de integração/configuração;
não são requisitos impostos à classe nesta suíte unitária. O teste de diretório
alternativo verifica apenas `DataPaths` com uma raiz absoluta explícita.
