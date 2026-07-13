# LLMOps RAG Platform

This repository contains a FastAPI service that answers technical questions using a Groq model and a Chroma vector store built from `platform_manual.txt`.

## Overview

- `ingest.py`: loads `platform_manual.txt`, splits it into chunks, enriches each chunk, and stores embeddings in Chroma.
- `vector_db/`: stores the persistent Chroma collection and vector data.
- `main.py`: receives a question, retrieves relevant chunks from the vector store, builds a prompt, and calls the Groq chat completion API.

## Features

- POST `/ask` endpoint for question answering.
- JSON request payload with a `question` field.
- Retrieves relevant context from the local vector database.
- Uses a low-temperature prompt for more objective answers.
- Returns the generated answer.

## Tech stack

- Python 3.12
- FastAPI
- Pydantic
- Groq SDK
- ChromaDB
- Uvicorn
- sentence-transformers

## Requirements

Install required packages:

```bash
pip install -r requirements.txt
```

## Configuration

1. Set the Groq API key in the environment:

```bash
export GROQ_API_KEY="your_api_key_here"
```

2. Ensure the `vector_db/` directory is writable.

> For production, keep `GROQ_API_KEY` outside source code and use environment variables or secrets management.

## Data ingestion

Build or refresh the vector store before starting the API:

```bash
python ingest.py
```

This creates or updates the `sre_manual` collection in `vector_db` using processed chunks from `platform_manual.txt`.

## Running locally

Start the app from the project folder:

```bash
python main.py
```

The API will be available at:

```text
http://127.0.0.1:8000
```

## Docker

Build the Docker image:

```bash
docker build -t llmops-rag-platform .
```

Run the container:

```bash
docker run -p 8000:8000 -e GROQ_API_KEY="your_api_key_here" llmops-rag-platform
```

If you do not already have a prebuilt `vector_db/` directory, generate it locally with `python ingest.py` before building the image.

## API endpoint

### POST /ask

Send a question to the API.

#### Example request

```bash
curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "Does Harness optimize costs?"}'
```

#### Example response

```json
{
  "question": "Does Harness optimize costs?",
  "answer": "..."
}
```

## Notes

- Answers are based on the context retrieved from the Chroma vector store.
- If the information is not present in the retrieved context, the API will indicate that it does not have the information.
- `main.py` uses the `llama-3.3-70b-versatile` model with a low temperature setting for concise and focused answers.
- To refresh the data, update `platform_manual.txt` and run `python ingest.py` again.
