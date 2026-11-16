# Fontes e aquisição

Referências consultadas em **15/11/2026**. O caderno anexado foi preservado sem
alterações em [desafios.md](desafios.md); o estado desta preparação está em
[preparacao.md](preparacao.md).

## INMET — observações de estações

- [Portal de históricos anuais](https://portal.inmet.gov.br/dadoshistoricos):
  opção **ANO 2024 (AUTOMÁTICA)**.
- [ZIP oficial de 2024](https://portal.inmet.gov.br/uploads/dadoshistoricos/2024.zip):
  URL efetivamente tentada no download.
- [BDMEP](https://bdmep.inmet.gov.br/).
- [Catálogo de estações automáticas](https://portal.inmet.gov.br/paginas/catalogoaut).

Atribuição para suas entregas: **Fonte: Instituto Nacional de Meteorologia
(INMET), estações automáticas, dados de 2024**, acompanhada do arquivo, estação,
período e data de aquisição efetivos.

Os portais consultados não apresentaram uma licença específica para esse ZIP.
Confira os avisos de uso na fonte e preserve eventuais documentos que acompanhem
o pacote. Não atribuímos automaticamente uma licença de código aos dados.

Após a falha do download automatizado, o estudante baixou e extraiu o pacote.
O ZIP original está em `data/raw/inmet/2024.zip` e seus 565 CSVs em
`data/raw/inmet/2024/`. O registro `data/raw/inmet/aquisicao-2024.json` preserva
as tentativas anteriores e documenta a aquisição manual, a organização e as
verificações locais. Veja [preparacao.md](preparacao.md#dados-locais-organizados).

## Open-Meteo — reanálise em grade

Consulte [Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api),
nas seções **API Documentation**, **Hourly Parameter Definition** e
**Reanalysis models**. O endpoint histórico é
`https://archive-api.open-meteo.com/v1/archive`.

| Parâmetro | Referência para os exercícios |
| --- | --- |
| `latitude`, `longitude` | Coordenadas identificadas nos metadados da estação |
| `start_date`, `end_date` | Período histórico em `AAAA-MM-DD` |
| `models` | Fixar `era5` explicitamente |
| `hourly` | `temperature_2m,relative_humidity_2m,precipitation` |
| `timezone` | `GMT` para aquisição em UTC |
| `temperature_unit`, `precipitation_unit` | `celsius`, `mm` |

Temperatura: °C; umidade relativa: %; precipitação: mm acumulados na hora
precedente. Confira as unidades na resposta.

O INMET registra observações de estações; a reanálise combina observações e
modelagem numa grade. Compare unidades, coordenadas solicitadas e retornadas,
fuso e intervalos de precipitação antes de associar fontes.

As [condições de uso](https://open-meteo.com/en/terms) restringem a API gratuita
ao uso não comercial, com menos de 10.000 chamadas/dia, 5.000/hora e 600/minuto;
reconfira esses limites antes da coleta. A [licença dos dados](https://open-meteo.com/en/licence)
é [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/): cite a fonte, inclua
o link da licença e indique alterações realizadas.

Atribua a **Open-Meteo** e ao **ERA5/ECMWF**, seguindo
[Citation & Acknowledgement](https://open-meteo.com/en/docs/historical-weather-api).
Guarde parâmetros e resposta bruta em `data/raw/open_meteo/`.

**Conectividade da API não verificada:** nenhuma consulta de dados foi executada.
Cliente HTTP, cache, tentativas e normalização ficam para os desafios.
