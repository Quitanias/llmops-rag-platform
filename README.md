# LLMOps RAG Platform

Esta aplicação é uma API em FastAPI que usa a API da Groq para responder perguntas com base no conteúdo de um manual em texto. O fluxo principal é simples:

1. O servidor lê o arquivo [manual_plataforma.txt](manual_plataforma.txt).
2. A pergunta enviada pelo usuário é combinada com esse contexto.
3. O modelo da Groq gera uma resposta objetiva, com foco no conteúdo do manual.

## O que a aplicação faz

- Expõe um endpoint POST em `/perguntar`.
- Recebe uma pergunta em JSON.
- Busca o conteúdo de um arquivo local.
- Envia esse contexto para um modelo da Groq.
- Retorna a resposta gerada pela IA.

## Tecnologias usadas

- Python
- FastAPI
- Pydantic
- Groq SDK
- Uvicorn

## Requisitos

Instale as dependências necessárias:

```bash
pip install fastapi uvicorn groq
```

## Configuração

Antes de executar, ajuste a chave de API da Groq no arquivo [main.py](main.py) substituindo o valor atual pela sua chave válida.

## Execução

Na pasta do projeto, execute:

```bash
python main.py
```

A aplicação ficará disponível em:

```text
http://127.0.0.1:8000
```

## Endpoint

### POST /perguntar

Envia uma pergunta para a API.

#### Exemplo de requisição

```bash
curl -X POST "http://127.0.0.1:8000/perguntar" \
  -H "Content-Type: application/json" \
  -d '{"pergunta": "Quais são as principais estratégias de deploy suportadas?"}'
```

#### Exemplo de resposta

```json
{
  "pergunta": "Quais são as principais estratégias de deploy suportadas?",
  "resposta": "As principais estratégias são Rolling Deployment, Blue/Green, Canary Release e GitOps."
}
```

## Observações

- O conteúdo usado para responder vem do arquivo [manual_plataforma.txt](manual_plataforma.txt).
- Se a informação não estiver no manual, a resposta deve indicar que a informação não foi localizada.
- Para uso em produção, é recomendável armazenar a chave da Groq em variável de ambiente em vez de deixá-la diretamente no código.