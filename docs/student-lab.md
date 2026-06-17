# Student Lab

## Cenario

Voce assumiu uma operacao serverless em AWS.

O ambiente esta funcional.

Mesmo assim, uma revisao identificou um risco:

```text
As tres Lambdas compartilham a mesma role.
```

Ninguem sabe exatamente:

- quais permissoes cada workload realmente precisa
- quais acessos estao sobrando
- qual seria o blast radius se uma Lambda fosse comprometida

Seu objetivo e revisar esse ambiente de forma operacional, sem partir de respostas prontas.

## O que existe no ambiente

- `receiver-lambda`
- `processor-lambda`
- `worker-lambda`
- tabela DynamoDB `DocumentProcessing`
- bucket S3 de entrada
- fila SQS principal
- fila adicional para testes indevidos
- API Gateway

## Perguntas operacionais

1. O sistema funcionar significa que o IAM esta bom?
2. Qual o risco de uma role compartilhada entre workloads diferentes?
3. Como voce identifica quais permissoes sao realmente usadas?
4. Como voce mede blast radius nesse desenho?
5. Como diferenciar falha legitima de controle funcionando corretamente?
6. Qual evidência voce coletaria antes de alterar qualquer policy?

## Tarefas

1. Subir o ambiente no modo padrao.
2. Validar o pipeline principal.
3. Executar testes indevidos e registrar o comportamento observado.
4. Identificar por que o desenho atual e operacionalmente arriscado.
5. Refatorar para roles especificas por Lambda.
6. Validar novamente o pipeline principal.
7. Executar testes indevidos de novo.
8. Registrar o que passou a falhar e por que isso e desejavel.

## Critérios de aceite

- o pipeline principal deve funcionar antes e depois da refatoracao
- no modo inicial, acessos indevidos nao devem estar devidamente bloqueados
- no modo least privilege, acessos indevidos devem falhar
- a analise final deve justificar permissoes por responsabilidade
- a conclusao nao deve depender de `AdministratorAccess` nem de permissoes genericas

## Entregáveis

- analise do cenario inicial
- roles separadas por Lambda
- justificativa das permissoes
- evidencias dos testes
- comparacao entre risco inicial e estado final

## Regra do exercicio

Nao abra a discussao tentando adivinhar a policy final.

Comece sempre por:

`responsabilidade -> recurso necessario -> action necessaria -> resource correto`

