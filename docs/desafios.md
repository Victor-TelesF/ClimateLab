# Planejamento das investigações

Os 30 desafios do ClimateLab organizam perguntas ambientais, requisitos de processamento e critérios de análise. São atividades planejadas de investigação e desenvolvimento, sem pressupor funcionalidades concluídas ou resultados obtidos. O [README](../README.md#estado-da-implementação) descreve o estágio atual.

O desenvolvimento será incremental, começando pela leitura e pelo diagnóstico de uma série e avançando para integração de fontes, indicadores e análises reutilizáveis. O documento mantém a numeração dos desafios como referência dos requisitos do [roadmap](../README.md#roadmap).

## A investigação

**Como caracterizar calor, chuva e períodos secos em uma região, medir a qualidade dos dados e comparar o que uma estação registrou com o que uma reanálise estima para o local?**

A engine planejada será um programa Python que recebe estação, período e parâmetros, integra fontes, calcula indicadores e devolve tabelas e um relatório de ocorrências. A implementação começa com funções pequenas; API própria, banco de dados, aplicação web e aprendizado de máquina não são requisitos desse escopo.

## Fontes previstas na investigação

### CSV: estações automáticas do INMET

O [portal de dados históricos](https://portal.inmet.gov.br/dadoshistoricos) fornece pacotes anuais de estações automáticas. O [BDMEP](https://bdmep.inmet.gov.br/) oferece acesso a dados meteorológicos, e o [catálogo de estações](https://portal.inmet.gov.br/paginas/catalogoaut) auxilia na identificação e localização.

A primeira etapa usa arquivos de 2024. A inspeção do conteúdo deve preceder as decisões sobre leitura, nomes de colunas, codificação, unidades, marcadores de ausência e interpretação temporal. Cabeçalhos e metadados originais devem ser preservados.

### API: histórico meteorológico do Open-Meteo

A [Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api) permite consultar séries por coordenadas e período. A integração planejada fixa explicitamente o modelo ERA5 e registra os parâmetros da consulta, com temperatura, umidade relativa e precipitação. Nomes e unidades devem ser confirmados na documentação vigente.

O produto previsto é uma reanálise, que combina observações e modelagem em uma grade espacial. Ele não equivale à leitura da estação selecionada. Uma divergência não demonstra, isoladamente, erro de sensor ou de API.

A coleta deverá respeitar a modalidade não comercial e os [limites de uso](https://open-meteo.com/en/terms), com atribuição às fontes. Consultas maiores deverão ser particionadas, e respostas preservadas para reutilização.

## Recorte e volume

O recorte piloto será uma estação, um ano e as três variáveis principais. A seleção da estação deverá justificar localização e cobertura. A ampliação para outras estações e anos depende da avaliação desse recorte. Uma cidade é um ponto de partida para localizar estações, não uma chave automática de associação.

Para planejar a escala: 100 estações × 5 anos × 8.760 horários equivalem a aproximadamente **4,38 milhões de registros estação–hora**, antes de considerar anos bissextos, lacunas e alterações de operação. Esse número é uma estimativa de planejamento, não uma contagem verificada dos arquivos.

O volume maior pode vir dos CSVs. Não há necessidade de fazer milhões de requisições à API; uma consulta pode retornar uma série inteira, e as comparações iniciais podem usar poucos locais e períodos.

## Regras para as análises

- Registrar fonte, estação ou coordenadas, variável, unidade, tempo e parâmetros de aquisição.
- Harmonizar o tempo em UTC antes de associar fontes. Converter para o fuso local ao responder perguntas sobre o dia ou horário local.
- Conferir o intervalo representado por cada marcação temporal de precipitação, além do fuso. No Open-Meteo, a precipitação horária corresponde ao acumulado da hora precedente, conforme a documentação.
- Diferenciar observação ausente de precipitação zero, sem preencher lacunas com zero automaticamente.
- Comparar variáveis com unidades, definições e intervalos compatíveis. O pareamento começa por temperatura; precipitação depende de resolver a semântica temporal.
- Declarar cobertura mínima antes do cálculo de indicadores diários, informando quantos dias ou horários foram excluídos e por quê.
- Definir a unidade sorteada e o conjunto de registros elegíveis nas análises de probabilidade.
- Limiares de calor, chuva e secura escolhidos neste caderno são parâmetros didáticos. Eles não constituem alertas oficiais nem critérios de risco à saúde ou de desastre.

## Registro dos métodos e resultados

Cada análise deverá apresentar a pergunta, os dados utilizados, o método aplicado, o código reproduzível, os resultados e as limitações identificadas. Tabelas e gráficos deverão sustentar a interpretação; modelos matemáticos deverão incluir o raciocínio e as hipóteses adotadas.

Os requisitos de implementação estão indicados em cada atividade. Os núcleos de extração de metadados, validação por registro, chaves de consulta, sequências, simulação e modelos explícitos utilizam a biblioteca padrão. A consulta HTTP pode usar `httpx`; pandas organiza a preparação e as tabelas de resultados. A coordenação da engine reutilizará essas funções. Laços sobre estruturas pequenas devem ter o desempenho avaliado antes da aplicação à base inteira.

## Etapa 1 — transformar CSV em dados confiáveis

### 01. O que cada arquivo representa?

A inspeção de um CSV deverá identificar estação, coordenadas, período, frequência, variáveis e unidades, distinguindo metadados de linhas de observação. Mudanças de identificação ou localização da estação no período escolhido deverão ser investigadas.

**Entrega:** inventário de um arquivo, dicionário das três variáveis principais e dúvidas que exijam documentação adicional.

### 02. Como ler arquivos com cabeçalhos e formatos diferentes?

A leitura deverá considerar codificação, separador, representação decimal, posição do cabeçalho e marcadores de ausência do arquivo selecionado, com uma estrutura de saída consistente.

**Python puro:** função de extração dos metadados do cabeçalho, preservando valores originais e definindo o comportamento para campos ausentes e linhas inesperadas.

**Entrega:** metadados estruturados e tabela carregada com pandas. A compatibilidade de formato deverá ser conferida a cada conjunto histórico incorporado.

A leitura de 2024 já disponibiliza metadados e observações em tabelas separadas. A validação do formato e a preservação integral dos textos dos metadados seguem como requisitos. [Formato observado no INMET](fontes.md#formato-e-leitura), [contrato dos testes](../tests/README.md#formato-coberto).

### 03. Quais observações precisam de investigação?

O diagnóstico deverá identificar datas inválidas, horários repetidos, valores ausentes e valores incompatíveis com as unidades e definições documentadas, separando problemas de formato de observações fisicamente suspeitas.

**Python puro:** função que recebe um registro e devolve os problemas identificados, sem modificá-lo, conferida com exemplos pequenos de ausência, zero e valor inválido.

**Entrega:** tabela de verificações, quantidades e decisões de tratamento. Valores extremos, por si só, não justificam excluir observações.

### 04. Quanto do período está realmente coberto?

A cobertura será calculada por variável e por mês a partir da comparação entre a grade de horários esperados no intervalo de operação considerado e os registros disponíveis, preservando a identificação da estação.

**Gráfico:** mapa de disponibilidade ou barras de cobertura mensal.

**Critério:** contar ausências de forma compatível com o período de operação e a regra de duplicatas; dados presentes com valor ausente não são cobertura válida da variável.

### 05. Qual é o retrato estatístico da estação?

A descrição estatística deverá incluir quantidade válida, média, mediana, quartis e desvio padrão por variável. A distribuição de precipitação será examinada incluindo zeros e, separadamente, apenas horários com chuva segundo um limiar declarado.

**Gráfico:** distribuições com unidades e tamanho de cada conjunto.

**Critério:** justificar a convenção de variância/desvio padrão e explicar por que a distribuição de chuva pode mudar muito ao condicionar a horários chuvosos.

### 06. Como transformar horários em dias?

Os indicadores diários serão temperatura média, amplitude entre amostras horárias válidas, umidade média e precipitação acumulada, com fuso, convenção dos intervalos e cobertura mínima definidos por indicador.

**Gráfico:** série diária com indicação de dias sem cobertura suficiente.

**Critério:** não chamar a maior amostra horária de máxima absoluta do dia se houver medições de extremos mais apropriadas; não apresentar soma parcial de chuva como total diário completo.

## Etapa 2 — consumir API e integrar fontes

### 07. Como fazer uma consulta HTTP confiável?

A primeira consulta ao histórico do Open-Meteo deverá abranger um período pequeno nas coordenadas da estação, com parâmetros e modelo confirmados na documentação.

**Python:** função com uma biblioteca HTTP, como `httpx`, que valide parâmetros, estabeleça timeout, verifique status e diferencie falha de rede, erro HTTP e resposta sem a estrutura esperada. A requisição fica separada da preparação de tabelas com pandas.

**Entrega:** resposta bruta preservada e registro da consulta, restrita ao recorte inicial antes de ampliar anos e estações.

### 08. Como evitar downloads e tentativas desnecessários?

O cliente deverá persistir as respostas e reutilizar consultas já realizadas.

**Python puro:** chave reproduzível a partir dos parâmetros relevantes e política de tentativas limitada para falhas transitórias, considerando `Retry-After` quando disponível. Erros de parâmetros não devem gerar tentativas indefinidas.

**Entrega:** demonstração de reutilização local e tratamento de falha com exemplos controlados, sem provocar bloqueio real na API.

### 09. Como transformar o JSON em tabela?

A resposta horária será convertida em tabela com identificador do local consultado, modelo, tempo e variáveis. A validação deverá conferir alinhamento dos vetores, campos de unidades, valores ausentes e unicidade da chave temporal por local/modelo.

**Entrega:** tabela normalizada e conferência de consistência com a resposta original, preservando metadados de coordenadas retornadas e unidades.

### 10. Quais locais podem ser comparados?

A correspondência entre a estação e o ponto consultado deverá registrar coordenadas da estação, coordenadas solicitadas e retornadas e informações espaciais disponíveis. Altitude, distância e resolução da grade serão consideradas como possíveis explicações para diferenças.

**Entrega:** tabela de correspondências e justificativa da comparação. O nome da cidade não basta para associar fontes; vários pontos consultados não correspondem necessariamente a células independentes.

### 11. Os horários significam a mesma coisa?

O pareamento exige padronizar fuso e referência temporal das duas fontes. A associação começa por temperaturas de um período curto, com inspeção manual de alguns pares, antes de examinar os intervalos de precipitação.

**Entrega:** tabela de pares comparáveis e auditoria dos horários que ficaram sem correspondência.

**Critério:** a associação não pode multiplicar linhas inesperadamente. Duplicatas devem ser registradas, e o significado dos horários confirmado antes de qualquer deslocamento da série.

### 12. Como quantificar a divergência entre as fontes?

Os pares válidos de temperatura serão usados para calcular diferença média com sinal definido, erro absoluto médio e raiz do erro quadrático médio, com referência operacional da comparação explicitamente identificada.

**Gráfico:** dispersão com a linha de igualdade e série das diferenças.

**Matemática:** diferenças, valor absoluto, quadrados e médias.

**Critério:** usar o mesmo conjunto de pares nas medidas e informar seu tamanho. A comparação não é uma avaliação de previsão futura: a fonte da API é uma reanálise.

## Etapa 3 — padrões, eventos e probabilidade

### 13. Quais padrões se repetem ao longo do dia e do ano?

A análise comparará temperatura, umidade e chuva por hora local e mês. Um único ano permite descrever o padrão daquele período; uma referência sazonal mais estável requer vários anos com qualidade conhecida.

**Gráfico:** perfil por hora ou mapa mês × hora, acompanhado da cobertura.

**Critério:** declarar se agregou horários diretamente ou deu o mesmo peso a cada dia. Não apresentar um ano como normal climatológica.

### 14. Uma observação extrema é um erro?

A investigação de extremos deverá considerar estação e época do ano, combinando limites físicos/documentados, quantis empíricos e inspeção da vizinhança temporal.

**Entrega:** lista de ocorrências com evidências e classificação como problema confirmado, observação plausível ou caso inconclusivo.

**Critério:** não remover extremos só por ultrapassarem um limite estatístico e não misturar estações em uma mesma referência sem justificativa.

### 15. Qual foi a maior sequência de dias secos?

A definição de dia seco depende de um limiar de precipitação diária declarado. Apenas dias elegíveis pela regra de cobertura entram no cálculo.

**Python puro:** função que recebe datas e estados diários e encontra sequências, com início, fim e duração. Lacunas devem interromper a sequência ou produzir uma condição indeterminada explicitamente descrita; não contam automaticamente como dias secos.

**Entrega:** maiores sequências por estação e conferência em exemplos pequenos, incluindo virada de mês e dias ausentes.

### 16. Como agrupar horas quentes em episódios?

Os episódios serão definidos pelo agrupamento de horários consecutivos acima de um limiar didático de temperatura declarado.

**Python puro:** identificação dos episódios, preservando estação, início, fim, quantidade de amostras e convenção de duração, com tratamento explícito da igualdade com o limiar e de lacunas.

**Gráfico:** temperatura com os episódios marcados.

**Critério:** distinguir contagem de amostras de duração física; o algoritmo identifica episódios segundo sua regra, não ondas de calor oficiais.

### 17. Qual é a probabilidade empírica de um dia chuvoso?

O experimento consiste em sortear uniformemente um dia elegível de uma estação e período. A probabilidade empírica de precipitação diária acima de um limiar positivo declarado será comparada entre meses, com denominadores informados.

**Entrega:** numeradores, denominadores e probabilidades por mês.

**Critério:** diferenciar probabilidade empírica histórica de previsão para amanhã. Não usar todos os dias do calendário como denominador quando existem dias sem cobertura suficiente.

### 18. A umidade altera a frequência observada de chuva?

O experimento passa a sortear um registro horário com umidade e precipitação válidas. Os eventos “umidade alta” e “houve precipitação no intervalo associado ao horário” terão limiares declarados para o cálculo de probabilidades conjuntas e condicionais.

**Gráfico:** comparação das probabilidades com suas contagens.

**Critério:** explicitar que a umidade é uma medida no horário e a precipitação é um acumulado de intervalo. Essa associação não prova causalidade nem capacidade de prever a próxima hora.

### 19. O que muda ao inverter a condição?

A comparação usará o mesmo conjunto elegível do desafio 18 para contrastar a probabilidade de chuva dado umidade alta com a probabilidade de umidade alta dado chuva.

**Matemática:** teorema de Bayes, complementos e probabilidade total.

**Entrega:** cálculo por contagens e pela relação de Bayes, com conferência de consistência e tratamento explícito de eventos condicionantes sem ocorrências.

### 20. O simulador reproduz a frequência conhecida?

A proporção empírica de dias chuvosos será o parâmetro de um experimento de Bernoulli didático. A simulação terá várias repetições e tamanhos para comparar a proporção simulada com o parâmetro usado.

**Python puro:** simulações com `random` e semente reproduzível.

**Gráfico:** distribuição do erro por tamanho de simulação.

**Critério:** a independência é uma hipótese do simulador; dias reais podem apresentar dependência temporal. Essa simulação não é um gerador meteorológico validado, e o erro não precisa decrescer em cada realização individual.

## Etapa 4 — limites com modelos explícitos

Uma série horária finita não oferece observações em intervalos arbitrariamente pequenos. Esta etapa utiliza modelos didáticos definidos matematicamente, distinguindo observação de modelagem. Derivadas não são necessárias.

### 21. Uma conversão de unidade preserva aproximações?

A função de conversão de Celsius para Fahrenheit, `F(T) = 1,8T + 32`, será analisada em torno de uma temperatura de referência observada, com aproximações de `T` pela esquerda e pela direita.

**Entrega:** justificativa algébrica, tabela de aproximações e relação entre tolerâncias de saída e entrada, com explicação das unidades.

**Critério:** este é um limite de uma função de conversão; não uma demonstração de continuidade da temperatura física medida.

### 22. A regra de classificação cria uma descontinuidade?

O modelo terá um limiar didático `L` e duas funções da temperatura: uma categoria numérica igual a 0 abaixo de `L` e 1 a partir de `L`; e um excesso térmico igual a zero até `L` e a `T − L` acima dele.

**Python puro:** duas funções com parâmetros e validações.

**Matemática:** funções por partes, limites laterais e continuidade.

**Entrega:** estudo em `L`, incluindo o valor de cada função no ponto, e gráfico comparativo, explicando como a escolha de uma regra modifica a saída mesmo diante de pequenas variações da entrada.

### 23. Um filtro se aproxima de uma referência constante?

O filtro didático será `y_(k+1) = (1 − α)y_k + αT*`, com `0 < α < 1`, condição inicial `y_0` e entrada constante `T*`. Uma temperatura real pode fornecer o valor de `T*`, mas manter essa entrada constante é uma hipótese do modelo.

**Python puro:** sequência calculada para diferentes valores de `α` e condições iniciais.

**Matemática:** sequência, progressão geométrica e limite quando `k` cresce sem limite, com expressão para `y_k` e justificativa do comportamento esperado.

**Gráfico:** aproximação para diferentes parâmetros.

**Critério:** separar o estudo com entrada constante do uso de um filtro sobre temperaturas que realmente variam. O filtro não cria novas medições.

### 24. Quantos passos atendem à tolerância?

A partir do modelo do desafio 23 e de uma tolerância `ε > 0`, a busca deverá encontrar o menor inteiro `k >= 0` para o qual `|y_k − T*| < ε`.

**Python puro:** busca com limite de iterações e retorno explícito quando o critério não for atingido, incluindo o caso em que a condição inicial já satisfaz a tolerância.

**Entrega:** comparação da busca com uma condição matemática sobre `k`, conferência de valores de fronteira e discussão de arredondamento numérico. O uso de logaritmos é uma possibilidade de aprofundamento.

**Critério:** relacionar a tolerância ao limite da sequência, sem interpretar a aproximação à referência como evidência de acurácia de um sensor.

## Etapa 5 — engine, incerteza e escala

### 25. Como a dependência temporal afeta a incerteza?

A variabilidade de uma média diária de temperatura será investigada por reamostragem, comparando o sorteio de dias individuais com blocos consecutivos de dias, em período relativamente homogêneo e com regra explícita para lacunas.

**Matemática:** bootstrap e bootstrap em blocos. A aplicação depende de avaliar previamente as hipóteses de reamostragem e pode ser adiada até que a série esteja caracterizada.

**Gráfico:** distribuição das estimativas e sensibilidade ao tamanho dos blocos.

**Critério:** discutir dependência e sazonalidade. Um intervalo produzido por reamostragem depende das hipóteses adotadas; vários anos não são obrigatoriamente intercambiáveis e um único ano não representa toda a variabilidade climática.

### 26. Como reunir as funções em uma engine?

A interface em Python deverá receber estação, período, cobertura mínima e limiares didáticos. Ela coordenará leitura, validação, seleção do conjunto elegível, indicadores e episódios, devolvendo tabelas e metadados de execução.

**Python:** reutilização das funções de coleta, validação e identificação de sequências, separando aquisição, cálculo e apresentação para permitir análises com dados já salvos, sem uma requisição a cada cálculo.

**Entrega:** documentação de entrada e saída, exemplos pequenos e tratamento de parâmetros inválidos ou seleção vazia. Funções em módulos são suficientes; classes e frameworks são opcionais.

### 27. Quão sensíveis são os resultados às regras?

A análise de sensibilidade variará o limiar de dia seco, de episódio quente e a cobertura mínima, mudando um parâmetro por vez e comparando quantidade de dias elegíveis, número e duração de episódios e probabilidades empíricas.

**Gráfico:** sensibilidade dos indicadores aos parâmetros.

**Critério:** distinguir mudança no conjunto de dados elegíveis de mudança na definição do evento. A escolha dos parâmetros exige justificativa independente do apelo visual do resultado.

### 28. As referências funcionam em outro período?

Parâmetros e referências descritivas definidos em um período inicial serão aplicados sem alteração a um período posterior, comparando cobertura, distribuições e frequência das ocorrências.

**Entrega:** comparação com separação temporal explícita.

**Critério:** não utilizar o período posterior para definir uma referência apresentada como anterior. Diferença entre dois anos, isoladamente, não demonstra uma tendência climática de longo prazo nem identifica sua causa.

### 29. A engine consegue analisar milhões de horários?

A ampliação abrangerá várias estações e anos dos CSVs, preservando suas identidades e processando por arquivo ou em partes quando necessário. O processamento em maior escala deverá incluir pelo menos contagens, cobertura e indicadores por estação/período.

**Entrega:** número real de registros, tempo, memória pelo método escolhido e comparação com um recorte pequeno processado integralmente.

**Critério:** agregar somas e contagens de forma consistente, sem média simples de médias de blocos de tamanhos diferentes. Sequências que atravessam o limite entre arquivos exigem tratamento explícito. As análises efetivamente executadas em maior escala deverão ser identificadas.

### 30. Que conclusão ambiental os resultados sustentam?

O relatório deverá reunir três conclusões rastreáveis, até quatro gráficos, qualidade/cobertura dos dados, comparação entre fontes e análise de sensibilidade da engine.

**Entrega:** conclusões, evidências, limitações e uma pergunta aberta, com uma investigação de chuva ou secura e uma de temperatura.

**Critério:** diferenciar fenômeno observado, estimativa de reanálise, definição de evento adotada na análise e inferência. O resultado deve permitir refazer a análise a partir das fontes e parâmetros registrados.

## Apresentação dos resultados

Os gráficos deverão partir de tabelas calculadas e verificáveis, acompanhadas de unidades, origem, período, fuso, denominadores e regra de cobertura. A pergunta, os eixos e as referências precisam estar claros. Qualquer transformação adicional deverá ser registrada e os valores apresentados, conferidos com as tabelas de origem.

As tabelas que sustentam os gráficos deverão estar disponíveis em formato reutilizável, como CSV; uma imagem de DataFrame não substitui os dados necessários à reprodução do cálculo.

## Sequência de desenvolvimento

O desenvolvimento começa pelas atividades 01 e 02 em um arquivo de estação, seguido pelo diagnóstico de qualidade e cobertura. A comparação entre fontes depende dessa base e da implementação do cliente HTTP.

| Foco | Desafios |
|---|---|
| CSV e pandas | 01–06 |
| API e integração | 07–12 |
| Estatística e eventos | 05, 12–16, 25 e 27–28 |
| Probabilidade e simulação | 17–20 |
| Limites e funções | 21–24 |
| Construção da engine | 26–29 |

Cada etapa deverá ser conferida com exemplos pequenos e resultados rastreáveis antes da ampliação do processamento.

## Fontes e escopo

- [INMET — dados históricos anuais](https://portal.inmet.gov.br/dadoshistoricos).
- [INMET — BDMEP](https://bdmep.inmet.gov.br/).
- [INMET — catálogo de estações automáticas](https://portal.inmet.gov.br/paginas/catalogoaut).
- [Open-Meteo — Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api).
- [Open-Meteo — condições e limites de uso](https://open-meteo.com/en/terms).

O pacote INMET de 2024 já está organizado no ambiente local, sem versionamento dos dados. Não há consulta de dados ao Open-Meteo registrada. A aquisição e as verificações estão em [preparacao.md](preparacao.md); os formatos e as condições de uso, em [fontes.md](fontes.md). Cobertura e pareamento entre fontes permanecem requisitos a verificar durante as investigações.
