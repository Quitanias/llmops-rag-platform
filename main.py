import os
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq
import chromadb
from chromadb.utils import embedding_functions

app = FastAPI(title="LLMOps API - RAG with Vector DB")

API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set.")

groq_client = Groq(api_key=API_KEY)

# 1. Define the SAME mathematical model we use during ingestion.
emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"
)

# Connects to the local database created by ingest.py
chroma_client = chromadb.PersistentClient(path="./vector_db")
collection = chroma_client.get_collection(name="sre_manual", embedding_function=emb_fn)

class QuestionRequest(BaseModel):
    question: str

@app.post("/ask")
async def process_question(request: QuestionRequest):
    try:
        # 2. Increase n_results to 3 (higher safety margin for retrieval)
        results = await asyncio.to_thread(
            collection.query,
            query_texts=[request.question],
            n_results=3
        )
        
        retrieved_texts = results["documents"][0]
        final_context = "\n---\n".join(retrieved_texts)
        
        prompt = (
            f"You are an SRE technical assistant.\n"
            f"Use ONLY the context below to answer the question.\n"
            f"If the answer is not in the context, say you do not have the information.\n\n"
            f"RETRIEVED CONTEXT:\n{final_context}\n\n"
            f"Question: {request.question}\n"
            f"Objective Answer:"
        )

        ai_response = await asyncio.to_thread(
            groq_client.chat.completions.create,
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1 # <-- EXTRA TECHNIQUE: Low temperature for strict, factual answers
        )
        
        return {
            "question": request.question,
            # "used_context": retrieved_texts, -> send to Datadog in a real scenario
            "answer": ai_response.choices[0].message.content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # Host 0.0.0.0 is required for the API to be accessible outside the Docker container
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)