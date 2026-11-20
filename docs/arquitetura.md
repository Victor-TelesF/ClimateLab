# Arquitetura da extração

O pacote em `src/climatelab/` concentra a descoberta e a leitura dos arquivos. O notebook consome essas interfaces para inspecionar uma estação. Os dados brutos ficam em `data/raw/inmet/<ano>/` e a extração produz tabelas em memória, preservando os CSVs de origem.

## Interfaces

| Interface | Comportamento atual |
| --- | --- |
| `DataPaths.csv_paths(year)` | Retorna uma lista ordenada de caminhos. Considera apenas arquivos diretamente na pasta do ano e aceita variações de caixa na extensão `.csv`. A raiz padrão é relativa ao diretório de trabalho. |
| `ExtractInmet(year).inmet_paths()` | Produz pares `(identificador, caminho)`. Usa o quarto segmento do nome separado por `_` e os últimos quatro caracteres do segmento final para formar identificadores como `A620_2024`. |
| `inmet_metadata(file)` | Lê as oito linhas iniciais com pandas, sem cabeçalho e com `dtype=str`. No perfil de 2024, cada linha contém um campo e seu valor. |
| `inmet_dataframe(file)` | Pula as oito linhas de metadados e usa a linha seguinte como cabeçalho. Carrega todas as medições do arquivo em um DataFrame. |
| `inmet_dataframes()` | Produz triplas `(identificador, caminho, DataFrame)` em ordem de caminho. A leitura das medições começa quando o iterador é consumido. |
| `ColumnName` | Reúne os rótulos de 19 colunas do perfil de observações. A validação do cabeçalho está pendente. |

A leitura separada permite consultar a identificação e as coordenadas da estação sem carregar as medições. No lote, a lista de caminhos é montada antes da primeira tabela e cada avanço lê somente os arquivos necessários para entregar o próximo resultado. [Formato do INMET](fontes.md) · [Exemplo de leitura individual](preparacao.md#primeira-leitura)

## Falhas e limites

- **Origem do lote.** Uma pasta anual vazia produz uma sequência vazia. Se a pasta estiver ausente, a descoberta propaga `FileNotFoundError`. Se o caminho apontar para um arquivo, propaga `NotADirectoryError`.
- **Identificação.** O nome é interpretado antes do tratamento de erros por arquivo. Um nome curto pode interromper o lote com `IndexError`. O extrator pode entregar identificadores repetidos ou com ano diferente da pasta.
- **Leitura direta.** Os leitores registram `EmptyDataError` e `ParserError` do pandas, mas em seguida tentam devolver uma variável sem valor e podem lançar `UnboundLocalError`. Outros erros, como falhas de acesso, propagam-se ao chamador. Algumas estruturas inválidas são aceitas pelo parser.
- **Leitura em lote.** Quando a leitura das medições lança uma exceção, o lote a guarda na propriedade `registry_erros` da instância, indexada pelo caminho, e passa ao arquivo seguinte. O erro recebido pelo lote pode substituir o erro original do parser no dicionário.

O contrato exercitado pela suíte prevê diagnóstico via `logging`, com arquivo e motivo, e continuidade após falhas isoladas de nome ou estrutura. A implementação atual cobre apenas parte desse contrato. As exceções específicas declaradas em `exceptions/inmet_exception.py` ainda não são lançadas pelos leitores. [Código do extrator](../src/climatelab/etl/extract.py) · [Contrato dos testes](../tests/README.md)

## Destinos previstos

A estrutura reserva `data/raw/open_meteo/` para respostas brutas da futura integração e `data/processed/` para séries preparadas. Tabelas e figuras de análises terão como destino `outputs/tables/` e `outputs/figures/`. A transformação, a validação temporal e a geração desses resultados continuam planejadas.
