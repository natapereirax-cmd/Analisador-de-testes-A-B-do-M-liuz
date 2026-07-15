# Análise de Testes A/B de Cashback (Méliuz)

Teste técnico pra vaga de Estágio de Growth AI-Native. A ideia é ter uma ferramenta que pega o CSV de qualquer teste A/B de cashback do Méliuz e devolve a análise pronta, sem precisar mexer no código pra cada teste novo.

## O que o projeto faz

Recebe um CSV de teste A/B (com as variantes, compradores, comissão, cashback e vendas por dia) e devolve:

- as métricas de cada grupo (margem, ticket médio, conversão)
- um teste estatístico comparando os grupos, pra saber se a diferença é real ou só coincidência dos dias observados
- a decisão final: qual grupo escalar pra 100% do tráfego, e por quê
- um relatório em Markdown pronto pra mostrar pra um gestor
- o registro do teste numa planilha de acompanhamento

Testei nos 3 datasets fornecidos (Parceiro A, B e C) e funcionou nos três sem precisar alterar nada no código, só trocando o arquivo de entrada.

## Como rodar

Precisa de Python instalado. No Windows o comando costuma ser `py`, no Mac/Linux `python3`.

Primeiro instala as dependências:

```
py -m pip install -r requirements.txt
```

Depois roda cada etapa apontando pro CSV que quiser analisar (sempre a partir da pasta raiz do projeto):

```
py src/load_data.py data/dataset_01_parceiroA.csv
py src/compute_metrics.py data/dataset_01_parceiroA.csv
py src/ab_test.py data/dataset_01_parceiroA.csv
py src/decision_engine.py data/dataset_01_parceiroA.csv
py src/report.py data/dataset_01_parceiroA.csv
py src/sheets.py data/dataset_01_parceiroA.csv
```

O `report.py` gera o relatório em `reports/`. O `sheets.py` registra o teste, e se não tiver credencial do Google configurada, ele cai automaticamente pra um CSV local (`reports/acompanhamento_testes.csv`), sem quebrar.

Pra rodar com outro dataset é só trocar o caminho do arquivo, o resto do comando é igual. Funciona pra qualquer CSV que siga o mesmo schema (Data, Grupos de usuários, Parceiro, compradores, comissão, cashback, vendas totais), com qualquer número de variantes.

## Estrutura

```
src/
  load_data.py        -> lê e limpa o CSV
  compute_metrics.py  -> calcula margem, ticket médio, etc por grupo
  ab_test.py           -> teste estatístico entre os grupos
  decision_engine.py  -> decide qual grupo escalar
  report.py             -> gera o relatório em Markdown
  sheets.py             -> registra o teste na planilha (ou CSV, como fallback)
data/       -> os 3 CSVs de teste
reports/    -> relatórios gerados + CSV de acompanhamento
```

## Planilha de acompanhamento

https://docs.google.com/spreadsheets/d/1_1TWmhi6CuwEOs8dDLR-6mfk5HUuun9rFoHwrzDqzCo/edit?usp=sharing

Tem uma linha por teste rodado, com nome, descrição, resultado e decisão tomada. Se quiser gerar isso automaticamente via API do Google Sheets, é só criar um `credentials.json` de uma conta de serviço do Google e passar o ID da planilha na hora de rodar o `sheets.py`. Sem isso, ele usa o CSV local, que também é aceito.

## Decisões que tomei

**Critério de decisão é margem, não volume.** Escalar a variante que vendeu mais não faz sentido se ela também aumentou o cashback pago mais do que aumentou a comissão recebida, porque nesse caso o Méliuz fica com menos dinheiro no fim, mesmo vendendo mais. Por isso a decisão final olha pra margem (comissão − cashback), não pra GMV bruto.

**Grupo controle é sempre o primeiro em ordem alfabética** (na prática, "Grupo 1"), por convenção de teste A/B. Dá pra mudar isso passando outro nome de grupo como parâmetro nas funções, caso o Méliuz use outra convenção.

**Só recomendo escalar uma variante diferente do controle se a diferença de margem for estatisticamente significativa** (teste t, 95% de confiança). Nos 3 datasets que testei, isso aconteceu de dar sempre "manter o controle": os grupos com mais cashback venderam mais, mas a margem caiu de forma consistente e comprovada estatisticamente. Não é bug, é o resultado real dos dados.

**CAC incremental** (cashback pago dividido pelo comprador extra que a variante trouxe) só é calculado quando a variante trouxe de fato mais compradores que o controle. Quando não trouxe, o valor fica em branco, porque dividir por um número negativo ou zero não faz sentido de negócio.
