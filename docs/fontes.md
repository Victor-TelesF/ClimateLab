# Fontes meteorológicas

## INMET · fonte utilizada

O ClimateLab lê os CSVs do pacote anual de estações automáticas do Instituto Nacional de Meteorologia. Cada arquivo reúne a identificação de uma estação e suas observações. Para reproduzir o inventário, use o pacote de 2024. Ao publicar um recorte, identifique o INMET como fonte e registre estação, período e arquivo de origem. [Históricos anuais](https://portal.inmet.gov.br/dadoshistoricos) · [Catálogo de estações automáticas](https://portal.inmet.gov.br/paginas/catalogoaut)

### Formato dos arquivos de 2024

| Parte do CSV | Conteúdo |
| --- | --- |
| Linhas 1 a 8 | Pares de campo e valor para região, UF, estação, código WMO, latitude, longitude, altitude e data de fundação. |
| Linha 9 | Cabeçalho das observações, com data, hora UTC e variáveis meteorológicas identificadas por nome e unidade. |
| Linhas seguintes | Registros horários. Entre as variáveis estão temperatura do ar de bulbo seco (°C), umidade relativa do ar (%) e precipitação total horária (mm). |

O leitor usa Latin-1, ponto e vírgula como separador e vírgula decimal nas medições. Um delimitador no fim do cabeçalho pode aparecer no DataFrame como a coluna extra `Unnamed: 19`.

Preserve os nomes originais dos arquivos. Em `INMET_SE_RJ_A620_CAMPOS DOS GOYTACAZES - SAO TOME_01-01-2024_A_31-12-2024.CSV`, o extrator obtém `A620` do código da estação e `2024` da data final. As datas do nome delimitam o período indicado pelo arquivo. Para medir cobertura, é preciso verificar os registros da série. [Validação dos nomes](arquitetura.md#falhas-e-limites)

Data e hora ficam em colunas separadas. Medições em branco permanecem ausentes, e zero é um valor observado. O extrator não interpreta sentinelas como `-9999`. Nos metadados, o pandas pode converter textos literais como `NA`, `NULL` e `N/A` em valores ausentes. Antes de incorporar outro perfil histórico, confira o cabeçalho, as unidades e os marcadores de ausência. [Preparação dos arquivos](preparacao.md)

## Open-Meteo · integração planejada

A integração prevista usará a Historical Weather API para obter a reanálise ERA5 por coordenadas e período. O INMET mede em um ponto, enquanto a reanálise estima condições para uma célula de grade. A comparação exige registrar as coordenadas da estação e da célula retornada, a altitude, o fuso e as unidades. [Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api)

No ERA5 via Open-Meteo, a temperatura e a umidade a dois metros representam o horário indicado. A precipitação horária acumula a hora precedente. Para comparar chuva, será necessário alinhar os intervalos de acumulação das duas fontes e identificar lacunas. Antes da coleta ou publicação, confira as condições de acesso à API e a atribuição exigida para os dados. [Variáveis horárias](https://open-meteo.com/en/docs/historical-weather-api#hourly_parameter_definition) · [Condições de uso](https://open-meteo.com/en/terms) · [Licença e atribuição](https://open-meteo.com/en/licence)
