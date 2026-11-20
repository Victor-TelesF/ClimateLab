# Testes da extração do INMET

Na raiz do repositório, prepare o ambiente e execute a suíte com pytest.

```bash
uv sync --locked
uv run --locked pytest -q
```

As fixtures criam CSVs sintéticos em diretórios temporários e redirecionam a origem do extrator. Prepare os arquivos de cada cenário antes de instanciar `ExtractInmet`, que descobre os caminhos no construtor. A suíte usa o parser real do pandas e dispensa downloads. [Fixtures](conftest.py)

| Arquivo | Cenários exercitados |
| --- | --- |
| [test_data_paths.py](test_data_paths.py) | Seleção do ano, extensões CSV, ordem dos caminhos, pasta vazia, ausente ou inválida. |
| [test_extract_inmet.py](test_extract_inmet.py) | Identificação da estação, pasta sem CSVs, leitura separada de metadados e medições, acentos, textos literais, zeros, ausências e leitura sob demanda. |
| [test_extract_inmet_errors.py](test_extract_inmet_errors.py) | Estrutura do CSV, arquivos vazios, nomes inválidos, divergência de ano, identificadores duplicados, continuidade do lote e diagnóstico por arquivo. |

## Expectativas da suíte

Os testes esperam que o construtor sinalize pasta ausente ou caminho anual que seja um arquivo. Para uma pasta existente sem CSVs, esperam `NoInmetFilesFoundError` no primeiro avanço dos iteradores. A leitura do conteúdo começa ao consumir o lote.

Para o perfil de 2024, os testes de estrutura esperam oito pares de metadados, as colunas previstas no cabeçalho e registros com largura consistente. Admitem um campo vazio adicional no fim. Na leitura direta, esperam `ValueError` para estrutura inválida.

No lote, os testes esperam que cada arquivo rejeitado gere um registro de `logging` com identificação e motivo, que os válidos continuem a ser entregues e que cada estação/ano apareça no máximo uma vez. A escolha de qual arquivo manter em uma duplicata segue em aberto. [Comportamento atual e limites](../docs/arquitetura.md#falhas-e-limites)

## Execução de 20 de novembro de 2026

Na revisão `c5cbf71`, com Python 3.14.4, pytest 9.2.0 e pandas 3.1.1, a suíte terminou com **39 aprovados e 22 falhas**. As falhas cobrem textos literais em metadados, nomes de estação com `_`, validação estrutural, duplicatas e continuidade após erro de leitura no lote.

```bash
.venv/bin/python -B -m pytest -q -p no:cacheprovider --tb=short
```
