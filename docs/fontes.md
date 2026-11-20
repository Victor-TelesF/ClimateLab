# Fontes de dados

O INMET fornece as observações usadas na leitura atual. A integração com a
reanálise ERA5 pelo Open-Meteo está planejada. Referências oficiais e condições
do Open-Meteo conferidas em 18/11/2026; a aquisição local do INMET foi registrada
em 15/11/2026. Os procedimentos estão em [preparacao.md](preparacao.md).

## INMET — observações de estações

- [Portal de históricos anuais](https://portal.inmet.gov.br/dadoshistoricos):
  opção **ANO 2024 (AUTOMÁTICA)**.
- [ZIP oficial de 2024](https://portal.inmet.gov.br/uploads/dadoshistoricos/2024.zip).
- [BDMEP](https://bdmep.inmet.gov.br/).
- [Catálogo de estações automáticas](https://portal.inmet.gov.br/paginas/catalogoaut).

O pacote de 2024 foi obtido por download manual. A cópia local mantém o ZIP em
`data/raw/inmet/2024.zip`, os 565 CSVs em `data/raw/inmet/2024/` e o registro
`data/raw/inmet/aquisicao-2024.json`. Esses arquivos são ignorados pelo Git e
precisam ser adquiridos separadamente em uma nova instalação.

### Formato e leitura

No formato inspecionado, as oito primeiras linhas contêm região, UF, estação,
código WMO, latitude, longitude, altitude e data de fundação. A nona linha
contém o cabeçalho das observações. A leitura atual usa Latin-1, separador `;`
e vírgula decimal para as medições.

O extrator monta o identificador estação/ano com o quarto segmento do nome
do arquivo (delimitado por `_`) e os quatro últimos caracteres antes da
extensão. A validação do código da estação e do ano indicado no nome ainda
está pendente. [Contrato da descoberta e da leitura](../tests/README.md#formato-coberto)

As três variáveis do recorte inicial são temperatura do ar de bulbo seco
horária (°C), umidade relativa do ar horária (%) e precipitação total horária
(mm). Data e `Hora UTC` são lidas como texto; a interpretação temporal e a
construção de timestamps ainda estão pendentes. Uma coluna final sem nome pode
ser lida como `Unnamed: 19`.

Nos metadados, a leitura com pandas ainda converte textos literais como
`NA`, `NULL` e `N/A` em ausências.

Cabeçalhos, marcadores de ausência e convenções podem variar entre arquivos.
A leitura pelo pandas não comprova validade física, cobertura ou consistência
da série. Valores ausentes, zero e eventuais sentinelas, como `-9999`, precisam
de regras explícitas; o extrator ainda não interpreta essa sentinela.

### Atribuição e condições de uso

Referência de atribuição: **Fonte: Instituto Nacional de Meteorologia (INMET),
estações automáticas, dados de 2024**, acompanhada de arquivo, estação, período
e data de aquisição efetivos.

O registro de aquisição não identifica uma licença específica para o ZIP.
As condições aplicáveis devem ser conferidas na fonte, preservando eventuais
avisos que acompanhem o pacote. A licença de um código não se estende
automaticamente aos dados.

## Open-Meteo — reanálise em grade

A [Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api)
documenta os parâmetros, unidades, modelos e referências de atribuição.
O endpoint previsto é `https://archive-api.open-meteo.com/v1/archive`.

| Parâmetro | Configuração planejada |
| --- | --- |
| `latitude`, `longitude` | Coordenadas da estação |
| `start_date`, `end_date` | Datas em `AAAA-MM-DD` |
| `models` | `era5`, explicitamente |
| `hourly` | `temperature_2m,relative_humidity_2m,precipitation` |
| `timezone` | `GMT`, para aquisição em UTC |
| `temperature_unit`, `precipitation_unit` | `celsius`, `mm` |

Temperatura e umidade são valores no horário indicado, a dois metros do solo.
A precipitação é o acumulado da hora precedente. As unidades esperadas são
°C, % e mm, a confirmar na resposta. Parâmetros e respostas brutas deverão
ser preservados em `data/raw/open_meteo/`.

### Atribuição e condições de uso

Na consulta de 18/11/2026, as [condições de uso](https://open-meteo.com/en/terms)
da API gratuita limitavam o acesso ao uso não comercial, com menos de 10.000
chamadas/dia, 5.000/hora e 600/minuto. Esses limites devem ser reconferidos
antes de cada coleta.

Os [dados da API](https://open-meteo.com/en/licence) são oferecidos sob
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), com crédito, link da
licença e indicação de alterações. A atribuição deve acompanhar a apresentação
dos dados. Para ERA5, devem constar Open-Meteo e a fonte ERA5/ECMWF, conforme
as referências em [Citation & Acknowledgement](https://open-meteo.com/en/docs/historical-weather-api#citation).

Não há consulta de dados registrada no projeto. A conferência da documentação
não verifica a conectividade do endpoint; cliente HTTP, persistência de
respostas, tentativas e normalização ainda estão planejados.

## Comparação entre fontes

O INMET registra observações pontuais; a reanálise combina observações e
modelagem em uma grade. A comparação deverá registrar coordenadas solicitadas
e retornadas, altitude e resolução espacial, além de unidades, fuso e intervalos
de acumulação. O nome da cidade não é uma chave suficiente de associação.

O pareamento deverá começar por temperatura em um período curto. Precipitação
exige conferir o significado dos intervalos nas duas fontes antes de somar ou
deslocar horários. Lacunas não equivalem a chuva zero. Uma divergência, por si
só, não identifica erro de sensor nem estabelece qual fonte é mais adequada.

Os critérios de cobertura, elegibilidade e interpretação estão detalhados no
[planejamento das investigações](desafios.md).
