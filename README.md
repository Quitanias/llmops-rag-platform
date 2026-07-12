# LLMOps RAG Platform

Esta aplicação é uma API em FastAPI que usa um banco vetorial Chroma e a API da Groq para responder perguntas com base no conteúdo do manual `manual_plataforma.txt`.

## Arquitetura

- `ingestao.py`: lê `manual_plataforma.txt`, divide o texto em trechos e cria embeddings usando `SentenceTransformerEmbeddingFunction`.
- `banco_vetorial/`: armazena os embeddings e trechos de texto usados na recuperação de contexto.
- `main.py`: recebe a pergunta, recupera os documentos mais relevantes do Chroma e consulta o modelo Groq para gerar a resposta.

## O que a aplicação faz

- Cria um endpoint POST em `/perguntar`.
- Recebe uma pergunta em JSON.
- Recupera os trechos mais relevantes do banco vetorial.
- Usa o contexto recuperado em um prompt para o modelo Groq.
- Retorna a resposta gerada pela IA junto com o contexto utilizado.

## Tecnologias usadas

- Python
- FastAPI
- Pydantic
- Groq SDK
- ChromaDB
- Uvicorn
- sentence-transformers

## Requisitos

Instale as dependências necessárias:

```bash
pip install fastapi uvicorn groq chromadb sentence-transformers
```

## Configuração

1. Ajuste a chave de API da Groq em `main.py` substituindo `API_KEY` pela sua chave válida.
2. Garanta que o diretório `banco_vetorial/` tenha permissão de escrita.

> Em produção, armazene a chave da Groq em variável de ambiente em vez de deixá-la no código.

## Ingestão de dados

Antes de usar a API, gere o banco vetorial a partir do manual:

```bash
python ingestao.py
```

Isso criará ou atualizará a coleção `manual_sre` em `banco_vetorial` com os pedaços do manual processados.

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
  -d '{"pergunta": "A harness faz otimização de custos?"}'
```

#### Exemplo de resposta

```json
{
  "pergunta": "A harness faz otimização de custos?",
  "contexto_utilizado": [
    "...trecho 1...",
    "...trecho 2...",
    "...trecho 3..."
  ],
  "resposta": "..."
}
```

## Observações

- O contexto usado para responder é recuperado do banco vetorial Chroma.
- Se a informação não estiver no contexto recuperado, o sistema responde que a informação não foi localizada.
- O modelo usado em `main.py` é `llama-3.3-70b-versatile` com temperatura baixa para respostas mais objetivas.
- Para atualizar o conteúdo, altere `manual_plataforma.txt` e execute novamente `python ingestao.py`.
