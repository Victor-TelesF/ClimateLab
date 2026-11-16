# Inteligência Ambiental — laboratório de clima

30 desafios para praticar Python, consumo de API, CSV, pandas, gráficos, probabilidade, estatística e limites. Você implementa as soluções e as regras da engine; pode delegar os gráficos a um agente a partir das tabelas que produzir.

Este é um recorte de estudo proposto para o tema Inteligência Ambiental: análise meteorológica e comparação entre fontes. Não pressupõe detalhes de outro projeto com esse nome. O caderno substitui o tema de filmes para esta trilha e não contém soluções ou resultados calculados.

## A investigação

**Como caracterizar calor, chuva e períodos secos em uma região, medir a qualidade dos dados e comparar o que uma estação registrou com o que uma reanálise estima para o local?**

A engine será um programa Python que recebe região/estação, período e parâmetros, integra fontes, calcula indicadores e devolve tabelas e um relatório de ocorrências. O desenvolvimento começa com funções pequenas. Não exige API própria, banco de dados, aplicação web ou modelos de aprendizado de máquina.

## Fontes verificadas

### CSV: estações automáticas do INMET

O [portal de dados históricos](https://portal.inmet.gov.br/dadoshistoricos) fornece pacotes anuais de estações automáticas. O [BDMEP](https://bdmep.inmet.gov.br/) também apresenta esse caminho para baixar os pacotes anuais e acessar dados em CSV. Consulte o [catálogo de estações](https://portal.inmet.gov.br/paginas/catalogoaut) para identificação e localização.

Comece com arquivos de um ano completo, como 2024. Inspecione o conteúdo real antes de definir leitura, nomes de colunas, codificação, unidades, marcadores de ausência e interpretação temporal. Preserve cabeçalhos e metadados originais.

### API: histórico meteorológico do Open-Meteo

A [Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api) permite consultar séries por coordenadas e período. Para este projeto, fixe explicitamente um modelo como ERA5 e guarde os parâmetros da consulta. Escolha temperatura, umidade relativa e precipitação, confirmando os nomes e unidades na documentação atual.

O histórico é uma **reanálise**, que combina observações e modelagem em uma grade espacial. Ele não equivale à leitura da estação que você selecionou. Uma divergência não demonstra, isoladamente, erro de sensor ou de API.

Use a modalidade não comercial adequada ao estudo, respeite os [limites de uso](https://open-meteo.com/en/terms) e registre atribuição às fontes. Particione consultas maiores e preserve respostas para reutilizá-las.

## Recorte e volume

O recorte piloto será **uma estação, um ano e as três variáveis principais**. Escolha uma estação cuja localização e cobertura permitam trabalhar; registre essa escolha. Depois, amplie para outras estações e anos. Uma cidade é um ponto de partida para localizar estações, não uma chave automática de associação.

Para planejar a escala: 100 estações × 5 anos × 8.760 horários equivalem a aproximadamente **4,38 milhões de registros estação–hora**, antes de considerar anos bissextos, lacunas e alterações de operação. Esse número é uma estimativa de planejamento, não uma contagem verificada dos arquivos.

O volume maior pode vir dos CSVs. Não há necessidade de fazer milhões de requisições à API; uma consulta pode retornar uma série inteira, e as comparações iniciais podem usar poucos locais e períodos.

## Regras para as análises

- Guarde fonte, estação ou coordenadas, variável, unidade, tempo e parâmetros de aquisição.
- Harmonize o tempo em UTC antes de associar fontes. Converta para o fuso local ao responder perguntas sobre o dia ou horário local.
- Para precipitação, confira o intervalo representado por cada marcação temporal, além do fuso. No Open-Meteo, a precipitação horária corresponde ao acumulado da hora precedente, conforme a documentação.
- Diferencie observação ausente de precipitação zero. Não preencha lacunas com zero automaticamente.
- Compare variáveis com unidades, definições e intervalos compatíveis. Comece por temperatura; só inclua precipitação após resolver a semântica temporal.
- Declare cobertura mínima antes de calcular indicadores diários. Mostre quantos dias ou horários foram excluídos e por quê.
- Nos desafios de probabilidade, defina a unidade sorteada e o conjunto de registros elegíveis.
- Limiares de calor, chuva e secura escolhidos neste caderno são parâmetros didáticos. Eles não constituem alertas oficiais nem critérios de risco à saúde ou de desastre.

## Entrega de cada desafio

Guarde o enunciado, sua tentativa em Python/pandas, uma tabela de resposta, o gráfico quando solicitado e uma interpretação curta. Nos exercícios matemáticos, acrescente seu raciocínio e as condições do modelo.

Há tarefas obrigatórias de Python puro nos desafios **02, 03, 07, 08, 15, 16, 20, 22, 23, 24 e 26**. Implemente o núcleo indicado usando a biblioteca padrão. Use pandas para preparar dados e organizar resultados; reserve os laços sobre estruturas pequenas para os exercícios e avalie desempenho antes de aplicá-los à base inteira.

## Etapa 1 — transformar CSV em dados confiáveis

### 01. O que cada arquivo representa?

Inspecione um CSV e identifique estação, coordenadas, período, frequência, variáveis e unidades. Diferencie metadados do arquivo de linhas de observação. Investigue se a estação mudou de identificação ou localização no período escolhido.

**Entrega:** inventário de um arquivo e dicionário das três variáveis principais. Registre dúvidas que precisem de documentação adicional.

### 02. Como ler arquivos com cabeçalhos e formatos diferentes?

Descubra a codificação, o separador, a representação decimal, a posição do cabeçalho e os marcadores de ausência no arquivo selecionado. Defina uma estrutura de saída consistente.

**Python puro:** implemente uma função para extrair os metadados do cabeçalho, preservando os valores originais. Defina comportamento para campos ausentes e linhas inesperadas.

**Entrega:** metadados estruturados e tabela carregada com pandas. Não suponha que todos os arquivos históricos possuem exatamente o mesmo formato.

### 03. Quais observações precisam de investigação?

Procure datas inválidas, horários repetidos, valores ausentes e valores incompatíveis com as unidades e definições documentadas. Separe um problema de formato de uma observação fisicamente suspeita.

**Python puro:** escreva uma função que recebe um registro e devolve os problemas identificados, sem modificá-lo. Confira-a com exemplos pequenos, incluindo ausência, zero e valor inválido.

**Entrega:** tabela de verificações, quantidades e decisões de tratamento. Evite excluir observações apenas por serem extremas.

### 04. Quanto do período está realmente coberto?

Construa a grade de horários esperados no intervalo de operação considerado e compare com os registros disponíveis. Calcule cobertura por variável e por mês, preservando a identificação da estação.

**Gráfico:** mapa de disponibilidade ou barras de cobertura mensal.

**Critério:** contar ausências de forma compatível com o período de operação e a regra de duplicatas; dados presentes com valor ausente não são cobertura válida da variável.

### 05. Qual é o retrato estatístico da estação?

Calcule quantidade válida, média, mediana, quartis e desvio padrão por variável. Observe a distribuição de precipitação incluindo zeros e, separadamente, apenas horários com chuva segundo um limiar declarado.

**Gráfico:** distribuições com unidades e tamanho de cada conjunto.

**Critério:** justificar a convenção de variância/desvio padrão e explicar por que a distribuição de chuva pode mudar muito ao condicionar a horários chuvosos.

### 06. Como transformar horários em dias?

Produza indicadores diários: temperatura média, amplitude entre amostras horárias válidas, umidade média e precipitação acumulada. Defina fuso, convenção dos intervalos e cobertura mínima por indicador.

**Gráfico:** série diária com indicação de dias sem cobertura suficiente.

**Critério:** não chamar a maior amostra horária de máxima absoluta do dia se houver medições de extremos mais apropriadas; não apresentar soma parcial de chuva como total diário completo.

## Etapa 2 — consumir API e integrar fontes

### 07. Como fazer uma consulta HTTP confiável?

Consulte um período pequeno do histórico do Open-Meteo nas coordenadas da estação. Confirme parâmetros e modelo na documentação.

**Python:** implemente uma função com uma biblioteca HTTP, como `httpx`, que valide parâmetros, estabeleça timeout, verifique status e diferencie falha de rede, erro HTTP e resposta sem a estrutura esperada. Não use pandas para executar a requisição.

**Entrega:** resposta bruta preservada e registro da consulta. Não comece baixando todos os anos e estações.

### 08. Como evitar downloads e tentativas desnecessários?

Acrescente persistência das respostas e reutilização de consultas já realizadas.

**Python puro:** construa uma chave reproduzível a partir dos parâmetros relevantes e uma política de tentativas limitada para falhas transitórias. Considere `Retry-After` quando disponível e não repita indefinidamente erros de parâmetros.

**Entrega:** demonstração de reutilização local e tratamento de falha usando exemplos controlados. Não provoque um bloqueio real na API para testar o comportamento.

### 09. Como transformar o JSON em tabela?

Converta a resposta horária em uma tabela com identificador do local consultado, modelo, tempo e variáveis. Valide o alinhamento dos vetores, os campos de unidades, valores ausentes e a unicidade da chave temporal por local/modelo.

**Entrega:** tabela normalizada e conferência de consistência com a resposta original. Não descarte metadados que expliquem coordenadas retornadas ou unidades.

### 10. Quais locais podem ser comparados?

Relacione a estação, suas coordenadas e o ponto consultado na API. Registre coordenadas retornadas e informações espaciais disponíveis. Discuta altitude, distância e resolução da grade como possíveis explicações para diferenças.

**Entrega:** tabela de correspondências e justificativa da comparação. Não associe fontes apenas pelo nome da cidade, nem suponha que vários pontos consultados correspondem a células independentes.

### 11. Os horários significam a mesma coisa?

Padronize fuso e referência temporal das duas fontes. Associe primeiro as temperaturas de um período curto e inspecione manualmente alguns pares. Depois, examine os intervalos de precipitação.

**Entrega:** tabela de pares comparáveis e auditoria dos horários que ficaram sem correspondência.

**Critério:** a associação não pode multiplicar linhas inesperadamente. Registre duplicatas e confirme o significado dos horários antes de deslocar uma série.

### 12. Como quantificar a divergência entre as fontes?

Nos pares válidos de temperatura, calcule diferença média com sinal definido, erro absoluto médio e raiz do erro quadrático médio. Explicite qual fonte é a referência operacional da comparação.

**Gráfico:** dispersão com a linha de igualdade e série das diferenças.

**Matemática:** diferenças, valor absoluto, quadrados e médias.

**Critério:** usar o mesmo conjunto de pares nas medidas e informar seu tamanho. A comparação não é uma avaliação de previsão futura: a fonte da API é uma reanálise.

## Etapa 3 — padrões, eventos e probabilidade

### 13. Quais padrões se repetem ao longo do dia e do ano?

Compare temperatura, umidade e chuva por hora local e mês. Em um único ano, descreva o padrão observado nesse ano; para uma referência sazonal mais estável, amplie para vários anos com qualidade conhecida.

**Gráfico:** perfil por hora ou mapa mês × hora, acompanhado da cobertura.

**Critério:** declarar se agregou horários diretamente ou deu o mesmo peso a cada dia. Não apresentar um ano como normal climatológica.

### 14. Uma observação extrema é um erro?

Investigue extremos por estação e época do ano. Compare limites físicos/documentados, quantis empíricos e inspeção da vizinhança temporal.

**Entrega:** lista de ocorrências com evidências e classificação como problema confirmado, observação plausível ou caso inconclusivo.

**Critério:** não remover extremos só por ultrapassarem um limite estatístico e não misturar estações em uma mesma referência sem justificativa.

### 15. Qual foi a maior sequência de dias secos?

Escolha um limiar de precipitação diária para definir dia seco. Use apenas dias elegíveis pela regra de cobertura.

**Python puro:** implemente uma função que receba datas e estados diários e encontre sequências, com início, fim e duração. Lacunas devem interromper a sequência ou produzir uma condição indeterminada explicitamente descrita; não contam automaticamente como dias secos.

**Entrega:** maiores sequências por estação e conferência em exemplos pequenos, incluindo virada de mês e dias ausentes.

### 16. Como agrupar horas quentes em episódios?

Defina um limiar didático de temperatura e agrupe horários consecutivos que o ultrapassam.

**Python puro:** implemente a identificação dos episódios, preservando estação, início, fim, quantidade de amostras e convenção de duração. Defina o tratamento da igualdade com o limiar e de lacunas.

**Gráfico:** temperatura com os episódios marcados.

**Critério:** distinguir contagem de amostras de duração física; o algoritmo identifica episódios segundo sua regra, não ondas de calor oficiais.

### 17. Qual é a probabilidade empírica de um dia chuvoso?

Defina o experimento: sortear uniformemente um dia elegível de uma estação e período. Estime a probabilidade de precipitação diária acima de um limiar positivo escolhido por você. Compare meses com denominadores informados.

**Entrega:** numeradores, denominadores e probabilidades por mês.

**Critério:** diferenciar probabilidade empírica histórica de previsão para amanhã. Não usar todos os dias do calendário como denominador quando existem dias sem cobertura suficiente.

### 18. A umidade altera a frequência observada de chuva?

Agora sorteie um registro horário com umidade e precipitação válidas. Defina os eventos “umidade alta” e “houve precipitação no intervalo associado ao horário”, com limiares declarados. Calcule probabilidades conjuntas e condicionais.

**Gráfico:** comparação das probabilidades com suas contagens.

**Critério:** explicitar que a umidade é uma medida no horário e a precipitação é um acumulado de intervalo. Essa associação não prova causalidade nem capacidade de prever a próxima hora.

### 19. O que muda ao inverter a condição?

No mesmo conjunto elegível do desafio 18, compare a probabilidade de chuva dado umidade alta com a probabilidade de umidade alta dado chuva.

**Matemática:** teorema de Bayes, complementos e probabilidade total.

**Entrega:** cálculo por contagens e pela relação de Bayes, com conferência de consistência. Trate explicitamente eventos condicionantes sem ocorrências.

### 20. Seu simulador reproduz a frequência conhecida?

Use a proporção empírica de dias chuvosos para construir um experimento de Bernoulli didático. Simule várias repetições e tamanhos, comparando a proporção simulada com o parâmetro usado.

**Python puro:** implemente as simulações com `random` e semente reproduzível.

**Gráfico:** distribuição do erro por tamanho de simulação.

**Critério:** a independência é uma hipótese do simulador; dias reais podem apresentar dependência temporal. Não use essa simulação como gerador meteorológico validado, nem espere erro decrescente em cada realização individual.

## Etapa 4 — limites com modelos explícitos

Uma série horária finita não oferece observações em intervalos arbitrariamente pequenos. Nesta etapa, use modelos didáticos definidos matematicamente e indique o que é observado e o que foi modelado. Derivadas não são necessárias.

### 21. Uma conversão de unidade preserva aproximações?

Considere a função de conversão de Celsius para Fahrenheit, `F(T) = 1,8T + 32`. Escolha uma temperatura de referência observada e estude o limite da função quando `T` se aproxima desse valor pela esquerda e pela direita.

**Entrega:** justificativa algébrica e tabela de aproximações. Relacione uma tolerância na saída a uma tolerância na entrada e explique o significado das unidades.

**Critério:** este é um limite de uma função de conversão; não uma demonstração de continuidade da temperatura física medida.

### 22. Sua regra de classificação cria uma descontinuidade?

Escolha um limiar didático `L` e defina duas funções da temperatura: uma categoria numérica igual a 0 abaixo de `L` e 1 a partir de `L`; e um excesso térmico igual a zero até `L` e a `T − L` acima dele.

**Python puro:** implemente as duas funções, com parâmetros e validações.

**Matemática:** funções por partes, limites laterais e continuidade.

**Entrega:** estudo em `L`, incluindo o valor de cada função no ponto, e gráfico comparativo. Explique como a escolha de uma regra modifica a saída mesmo diante de pequenas variações da entrada.

### 23. Um filtro se aproxima de uma referência constante?

Considere um filtro didático `y_(k+1) = (1 − α)y_k + αT*`, com `0 < α < 1`, condição inicial `y_0` e entrada constante `T*`. Você pode escolher uma temperatura real como valor de `T*`, mas manter essa entrada constante é uma hipótese do exercício.

**Python puro:** implemente a sequência para diferentes valores de `α` e condições iniciais.

**Matemática:** sequência, progressão geométrica e limite quando `k` cresce sem limite. Investigue uma expressão para `y_k` e justifique o comportamento esperado.

**Gráfico:** aproximação para diferentes parâmetros.

**Critério:** separar o estudo com entrada constante do uso de um filtro sobre temperaturas que realmente variam. O filtro não cria novas medições.

### 24. Quantos passos atendem à tolerância?

No modelo do desafio 23, escolha `ε > 0` e procure o menor inteiro `k >= 0` para o qual `|y_k − T*| < ε`.

**Python puro:** implemente uma busca com limite de iterações e retorno explícito quando o critério não for atingido. Trate o caso em que a condição inicial já satisfaz a tolerância.

**Entrega:** comparação da busca com uma condição matemática sobre `k`; usar logaritmos é uma possibilidade de aprofundamento. Confira os valores de fronteira e discuta arredondamento numérico.

**Critério:** relacionar a tolerância ao limite da sequência, sem interpretar a aproximação à referência como evidência de acurácia de um sensor.

## Etapa 5 — engine, incerteza e escala

### 25. Como a dependência temporal afeta a incerteza?

Escolha uma média diária de temperatura como medida e investigue sua variabilidade por reamostragem. Compare uma abordagem que sorteia dias individualmente com uma abordagem em blocos consecutivos de dias, em um período relativamente homogêneo e com regra explícita para lacunas.

**Matemática:** bootstrap e bootstrap em blocos. Este desafio exige estudo adicional e pode ficar para depois.

**Gráfico:** distribuição das estimativas e sensibilidade ao tamanho dos blocos.

**Critério:** discutir dependência e sazonalidade. Um intervalo produzido por reamostragem depende das hipóteses adotadas; vários anos não são obrigatoriamente intercambiáveis e um único ano não representa toda a variabilidade climática.

### 26. Como reunir suas funções em uma engine?

Crie uma interface em Python que receba estação, período, cobertura mínima e limiares didáticos. Ela deve coordenar leitura dos dados, validação, seleção do conjunto elegível, indicadores e episódios, devolvendo tabelas e metadados de execução.

**Python:** reaproveite suas funções de coleta, validação e identificação de sequências. Separe aquisição, cálculo e apresentação para conseguir executar análises com dados já salvos, sem uma requisição a cada cálculo.

**Entrega:** documentação de entrada e saída, exemplos pequenos e tratamento de parâmetros inválidos ou seleção vazia. Funções em módulos são suficientes; classes e frameworks são opcionais.

### 27. Quão sensíveis são seus resultados às regras?

Varie o limiar de dia seco, de episódio quente e a cobertura mínima, mudando um parâmetro por vez. Compare quantidade de dias elegíveis, número e duração de episódios e probabilidades empíricas.

**Gráfico:** sensibilidade dos indicadores aos parâmetros.

**Critério:** distinguir mudança no conjunto de dados elegíveis de mudança na definição do evento. Não escolher parâmetros só porque deixam o resultado mais chamativo.

### 28. Suas referências funcionam em outro período?

Defina parâmetros e referências descritivas em um período inicial e aplique as mesmas regras em um período posterior. Compare a cobertura, as distribuições e a frequência das ocorrências.

**Entrega:** comparação com separação temporal explícita.

**Critério:** não utilizar o período posterior para definir uma referência que você apresenta como anterior. Diferença entre dois anos, isoladamente, não demonstra uma tendência climática de longo prazo nem identifica sua causa.

### 29. A engine consegue analisar milhões de horários?

Amplie a leitura para várias estações e anos dos CSVs, preservando suas identidades. Processe por arquivo ou em partes quando necessário. Leve para a escala grande pelo menos as contagens, cobertura e indicadores por estação/período.

**Entrega:** número real de registros, tempo, memória pelo método escolhido e comparação com um recorte pequeno processado integralmente.

**Critério:** agregar somas e contagens de forma consistente, sem média simples de médias de blocos de tamanhos diferentes. Para sequências, trate eventos que atravessam o limite entre arquivos. Declare quais análises foram efetivamente escaladas.

### 30. Que conclusão ambiental você consegue defender?

Prepare um relatório com três conclusões rastreáveis, até quatro gráficos, qualidade/cobertura dos dados, comparação entre fontes e análise de sensibilidade da engine.

**Entrega:** conclusões, evidências, limitações e uma pergunta aberta. Mostre uma investigação de chuva ou secura e uma de temperatura.

**Critério:** diferenciar fenômeno observado, estimativa de reanálise, definição de evento escolhida por você e inferência. O resultado deve permitir refazer a análise a partir das fontes e parâmetros registrados.

## Como delegar os gráficos

Forneça ao agente a tabela calculada, unidades, origem, período, fuso, denominadores e regra de cobertura. Descreva a pergunta, os eixos e as referências desejadas. Peça que qualquer transformação adicional seja explicada antes da execução e confira os valores apresentados.

Você mantém a responsabilidade pelo cálculo e pela interpretação. Não envie só uma imagem de um DataFrame se puder fornecer a tabela em CSV.

## Começo sugerido

Na primeira sessão, faça apenas **01 e 02** em um arquivo de estação. Depois, trate qualidade e cobertura antes de comparar fontes. O cliente HTTP é um dos exercícios que você desenvolverá: preparar o ambiente não deve resolvê-lo antecipadamente.

| Foco | Desafios |
|---|---|
| CSV e pandas | 01–06 |
| API e integração | 07–12 |
| Estatística e eventos | 05, 12–16, 25 e 27–28 |
| Probabilidade e simulação | 17–20 |
| Limites e funções | 21–24 |
| Construção da engine | 26–29 |

Em uma revisão, envie sua tentativa e peça primeiro avaliação do raciocínio ou uma pista. Código completo e soluções ficam para quando você os solicitar explicitamente.

## Fontes e escopo

- [INMET — dados históricos anuais](https://portal.inmet.gov.br/dadoshistoricos).
- [INMET — BDMEP](https://bdmep.inmet.gov.br/).
- [INMET — catálogo de estações automáticas](https://portal.inmet.gov.br/paginas/catalogoaut).
- [Open-Meteo — Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api).
- [Open-Meteo — condições e limites de uso](https://open-meteo.com/en/terms).

As fontes e sua documentação foram consultadas para propor o projeto. Não foram baixados os pacotes meteorológicos nem executadas consultas de dados à API nesta preparação. Cobertura, nomes efetivos de colunas e pareamento entre fontes devem ser verificados durante os desafios.
