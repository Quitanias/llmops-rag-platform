import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq
import chromadb
from chromadb.utils import embedding_functions

app = FastAPI(title="API LLMOps - RAG com Vector DB")

# Inicializa o cliente da Groq (Cole sua chave gsk_ aqui)
API_KEY = "xxx"
groq_client = Groq(api_key=API_KEY)

# 1. Define o MESMO modelo matemático que usamos na ingestão
emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"
)

chroma_client = chromadb.PersistentClient(path="./banco_vetorial")
collection = chroma_client.get_collection(name="manual_sre", embedding_function=emb_fn)

class PerguntaRequest(BaseModel):
    pergunta: str

@app.post("/perguntar")
async def processar_pergunta(request: PerguntaRequest):
    try:
        # 2. Aumentamos o n_results para 3 (margem de segurança maior)
        resultados = await asyncio.to_thread(
            collection.query,
            query_texts=[request.pergunta],
            n_results=3
        )
        
        textos_recuperados = resultados["documents"][0]
        contexto_final = "\n---\n".join(textos_recuperados)
        
        prompt = (
            f"Você é um assistente técnico SRE.\n"
            f"Use APENAS o contexto abaixo para responder à pergunta.\n"
            f"Se a resposta não estiver no contexto, diga que não tem a informação.\n\n"
            f"CONTEXTO RECUPERADO:\n{contexto_final}\n\n"
            f"Pergunta: {request.pergunta}\n"
            f"Resposta Objetiva:"
        )

        resposta_ia = await asyncio.to_thread(
            groq_client.chat.completions.create,
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1 # <-- TÉCNICA EXTRA: Temperatura baixa para respostas mais focadas em manuais
        )
        
        return {
            "pergunta": request.pergunta,
            # "contexto_utilizado": textos_recuperados, - > send to datadog
            "resposta": resposta_ia.choices[0].message.content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)