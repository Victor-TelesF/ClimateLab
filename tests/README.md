# Testes da extração do INMET

Na raiz do repositório, prepare o ambiente e execute a suíte com pytest.

```bash
uv sync --locked
uv run --locked pytest -q
```

As fixtures criam CSVs artificiais em diretórios temporários e redirecionam a origem de dados do extrator. A suíte usa o parser real do pandas e pode rodar sem baixar dados ou abrir o Jupyter. [Fixtures](conftest.py)

| Arquivo | Comportamentos verificados |
| --- | --- |
| [test_data_paths.py](test_data_paths.py) | Seleção do ano, extensões CSV, ordem dos caminhos, pasta vazia, ausente ou inválida. |
| [test_extract_inmet.py](test_extract_inmet.py) | Identificação da estação, leitura separada de metadados e medições, acentos, textos literais, zeros, ausências e leitura sob demanda. |
| [test_extract_inmet_errors.py](test_extract_inmet_errors.py) | Estrutura do CSV, arquivos vazios, nomes inválidos, divergência de ano, identificadores duplicados, continuidade do lote e diagnóstico por arquivo. |

## Contratos em aberto

Para o perfil de 2024, os testes de estrutura exigem oito pares de metadados, as colunas esperadas no cabeçalho e linhas de largura consistente. Admitem um campo vazio adicional no fim. As leituras diretas devem sinalizar estrutura inválida com `ValueError`.

No lote, os testes exigem que cada arquivo rejeitado gere uma mensagem de `logging` com identificação e motivo, que os válidos continuem a ser entregues e que cada estação/ano apareça no máximo uma vez. A escolha de qual arquivo manter em uma duplicata continua em aberto. Falhas na pasta de origem devem chegar ao chamador.

Há casos em que o extrator aceita arquivos inválidos, interrompe a iteração ou registra uma exceção diferente da esperada. Também há falhas na preservação de textos literais. A arquitetura descreve o comportamento implementado. [Falhas e limites da leitura](../docs/arquitetura.md#falhas-e-limites)
