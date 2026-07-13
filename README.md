```bash
# LLMOps RAG Platform — Enterprise Question Answering, Fast

LLMOps RAG Platform is a production-ready, developer-first Question Answering API that combines a local Chroma vector store with the Groq chat model to convert your technical manuals into an on-demand, accurate knowledge assistant.

Whether you're building internal SRE tooling, embedding searchable docs in a support portal, or standing up a secure RAG service behind your network, this repo gives you a concise, reproducible starting point.

Why this project matters:

- Fast developer iteration: local vector DB + lightweight FastAPI service.
- Focused answers: retrieval-augmented prompts and low-temperature model calls reduce hallucination.
- Docker-ready: package and ship a reproducible runtime.

## What's included

- `ingest.py` — build the local vector database from `platform_manual.txt` (splits, enriches and stores embeddings).
- `vector_db/` — persistent Chroma DB folder produced by ingestion.
- `main.py` — FastAPI service exposing a single conversational endpoint: `POST /ask`.
- `requirements.txt` — Python dependencies.
- `Dockerfile` — how to containerize the service for deployment.

## Quick Benefits (elevator pitch)

- Answer production-grade SRE and ops questions directly from your manuals.
- Ship a small, auditable RAG service that keeps sensitive documentation in your environment.
- Reduce support overhead by surfacing precise, context-backed answers.

## Requirements

- Python 3.11+ (tested on 3.12)
- Docker (optional, for packaging)

Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

1. Set your Groq API key as an environment variable:

```bash
export GROQ_API_KEY="your_api_key_here"
```

2. Ensure `vector_db/` is writable.

Security note: Never commit `GROQ_API_KEY` to source control — use secrets management for production.

## Build the vector database

Before using the API, create or refresh the vector store from your manual:

```bash
python ingest.py
```

This reads `platform_manual.txt`, creates enriched chunks, and stores them in `vector_db/` under the `sre_manual` collection.

If you update your manual, run the same command to refresh the index.

## Run locally

Start the API:

```bash
python main.py
```

By default the app listens on `0.0.0.0:8000` (suitable for Docker). Locally you can reach it at:

```text
http://127.0.0.1:8000
```

## Docker (recommended for reproducible deployments)

Build the image:

```bash
docker build -t llmops-rag-platform .
```

Run the container (inject your API key):

```bash
docker run --rm -p 8000:8000 -e GROQ_API_KEY="your_api_key_here" llmops-rag-platform
```

Note: If you want the container to include a prebuilt `vector_db/`, generate `vector_db/` locally with `python ingest.py` and include it during image build (the existing Dockerfile copies `vector_db/` into the image).

## API Reference — Developer Examples

## Uploading and Updating Data

There are a few common ways to get your manual or a prebuilt vector database into the running service. Pick the workflow that fits your deployment strategy:

- Include a prebuilt `vector_db/` in the image (bake it in):

  1. Generate the index locally:

  ```bash
  python ingest.py
  ```

  2. Build the Docker image (the `Dockerfile` copies `vector_db/` into the image):

  ```bash
  docker build -t llmops-rag-platform .
  ```

- Mount the `vector_db/` directory at runtime (preferred for iterative development):

  ```bash
  docker run --rm -p 8000:8000 \
    -e GROQ_API_KEY="your_api_key_here" \
    -v $(pwd)/vector_db:/app/vector_db \
    llmops-rag-platform
  ```

  This lets you regenerate `vector_db/` locally (with `python ingest.py`) without rebuilding the image; simply restart the container to pick up changes.

- Update the manual and rebuild the index:

  1. Edit `platform_manual.txt`.
  2. Run:

  ```bash
  python ingest.py
  ```

  3. Restart the service (or rebuild the image if you baked the index into it).

- Note about upload endpoints: this project does not include an HTTP "upload" endpoint to push documents directly to the running API. If you need that workflow (upload → ingest → live update), I can add an `/upload` endpoint that accepts files, runs the ingestion for the new document, and updates the Chroma collection in place.

Notes:

- Avoid concurrent writes to `vector_db/` from multiple processes. Use a single ingest job or offline rebuilds.
- When mounting a host directory, ensure ownership and file permissions allow the container user to read the index.


Endpoint: `POST /ask`

Request JSON schema:

```json
{
  "question": "<your question here>"
}
```

Successful response:

```json
{
  "question": "Does Harness optimize costs?",
  "answer": "...model generated answer..."
}
```

Curl example:

```bash
curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "Does Harness optimize costs?"}'
```

Python example (requests):

```python
import requests

resp = requests.post(
    "http://127.0.0.1:8000/ask",
    json={"question": "Does Harness optimize costs?"}
)
print(resp.json())
```

Advanced example: using `curl` with Docker-hosted service (from host):

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I apply Terraform in prod?"}'
```

## Troubleshooting & Tips

- If you get an authentication error, confirm `GROQ_API_KEY` is set in the environment used to start the app.
- If no results are returned, check that `vector_db/` exists and was generated with `ingest.py`.
- To debug retrieval, inspect the `vector_db/` folder and run `ingest.py` again to ensure chunks were created.
- Consider instrumenting `main.py` to log `retrieved_texts` during development (avoid logging sensitive sections in production).

## Next steps — production hardening

- Move `GROQ_API_KEY` to a secrets manager (Vault, AWS Secrets Manager, etc.).
- Add health checks and readiness probes for orchestration (Kubernetes `livenessProbe` / `readinessProbe`).
- Limit model call concurrency and add rate limiting to the FastAPI app.
- Add tests validating that important manual sections are answerable by the endpoint.

## Want help?

If you'd like, I can:

- Add a `docker-compose.yml` to wire the service and a simple health-check container.
- Add an OpenAPI examples section and automated tests for core queries.

Enjoy — this service gets you from docs to production-ready answers in minutes.
