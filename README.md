# API de Classifição de Atendimento

Serviço para classificação de atendimento de acordo com o conteúdo da mensagem escrita pelo cliente. O objetivo é que o cliente seja direcionado para o setor adequado e especialista no assunto.

Utilizado modelo basedo em container, implementado no modelo serverless utilizando AWS Lambda.

## Modo de utilização

O handler da API espera entrada de dados no formato JSON, como no exemplo as seguir:

```json
{
    "data": [
      {
        "id_reclamacao": 1,
        "data_abertura": "2024-05-17",
        "descricao_reclamacao": "Texto"
      }
    ]
  }
```


Todos os parâmetros precisam ser enviados, obrigatoriamente.

O resultado é retornado no formato JSON, informando a categoria da predição e a versão do modelo.

```json
{
"statusCode": 200,
"body": "[{\"id_reclamacao\": 5, \"data_abertura\": \"2024-05-17\", \"descricao_reclamacao\": \"Linguei para o banco porque estou com problemas para utilizar o meu cartão de crédito, a senha não autoriza.\", \"prediction\": \"Cartão de crédito / Cartão pré-pago\"}]",
"version": "v0.0.3"
}
```

## Uso

Este repositório possui os seguintes módulos:

* Arquivo de montagem do container Docker, contendo as instruções para empacotamento da imagem incluindo dependências e o modelo.
