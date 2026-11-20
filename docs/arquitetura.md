# Arquitetura da extração

O pacote em `src/climatelab/` concentra a descoberta e a leitura dos arquivos. A extração preserva os CSVs de origem e carrega as tabelas em memória.

```mermaid
flowchart LR
    CSV["CSVs anuais do INMET"] --> P["DataPaths"]
    P --> E["ExtractInmet"]
    E --> M["Metadados da estação"]
    E --> O["Observações horárias"]
    M --> N["Notebook de inventário"]
    O --> N
```

## Interfaces

| Interface | Comportamento atual |
| --- | --- |
| `DataPaths.csv_paths(year)` | Lista os arquivos diretamente em `data/raw/inmet/<ano>/`, ordenados por caminho. Aceita variações de caixa na extensão `.csv`. A raiz padrão é relativa ao diretório de trabalho. |
| `ExtractInmet(year)` | Consulta a pasta anual no construtor e guarda a lista de caminhos em `paths`. Arquivos adicionados depois da construção exigem uma nova instância para entrar na descoberta. |
| `inmet_paths()` | Ao consumir o iterador, valida o nome de cada arquivo e produz pares `(identificador, caminho)`, como `("A620_2024", caminho)`. |
| `inmet_metadata(file)` | Lê as oito primeiras linhas com pandas, sem cabeçalho, usando `dtype=str`. |
| `inmet_dataframe(file)` | Pula as oito primeiras linhas, usa a seguinte como cabeçalho e carrega todas as medições do arquivo em um DataFrame. |
| `inmet_dataframes()` | Ao consumir o iterador, lê as medições e os metadados de cada caminho aceito e entrega triplas `(identificador, caminho, DataFrame de medições)`. |
| `ColumnName` | Reúne os rótulos das 19 colunas do perfil de observações. O extrator ainda não usa esses rótulos para validar o cabeçalho. |

As leituras individuais recebem um caminho diretamente. Para listar os arquivos sem abrir os CSVs, use `inmet_paths()`. Cada avanço do lote pode examinar vários nomes, mas carrega o conteúdo de um arquivo por vez. [Formato do INMET](fontes.md) · [Exemplo de leitura individual](preparacao.md#primeira-leitura)

## Falhas e limites

| Situação | Momento e comportamento |
| --- | --- |
| Pasta anual ausente ou caminho anual que aponta para um arquivo | O construtor propaga `FileNotFoundError` ou `NotADirectoryError`, respectivamente. |
| Pasta existente sem CSVs | `DataPaths.csv_paths(year)` retorna uma lista vazia. Ao iniciar o consumo de qualquer iterador do extrator, ocorre `NoInmetFilesFoundError`. |
| Nome ou código inválido, data inválida ou invertida, ano final divergente | `inmet_paths()` registra um aviso com nome do arquivo, tipo da exceção e motivo, e segue para o próximo caminho. Se todos os nomes forem rejeitados, o iterador se esgota sem resultados. |
| Nome de estação com `_` | Pode ser rejeitado porque o leitor procura a data inicial em uma posição fixa entre os segmentos do nome. |
| Identificador repetido | O lote pode entregar mais de um resultado para a mesma estação e ano. A política de duplicatas segue em aberto. |
| CSV vazio, malformado ou inacessível | Os leitores diretos propagam os erros de leitura. Um erro ao ler medições ou metadados interrompe o lote. Algumas estruturas inválidas ainda são aceitas pelo pandas. |

A identificação usa o código da estação (uma letra maiúscula e três dígitos) e o ano da data final do nome. O extrator confere a ordem das datas e compara o ano final com o ano solicitado. As exceções de domínio usadas nessa etapa fazem parte do diagnóstico de nomes rejeitados. [Código do extrator](../src/climatelab/etl/extract.py) · [Exceções de domínio](../src/climatelab/exceptions/inmet_exception.py) · [Cenários da suíte](../tests/README.md)

## Destinos previstos

A estrutura reserva `data/raw/open_meteo/` para respostas brutas da futura integração e `data/processed/` para séries preparadas. Tabelas e figuras de análises terão como destino `outputs/tables/` e `outputs/figures/`. A transformação, a validação temporal e a geração desses resultados continuam planejadas.
