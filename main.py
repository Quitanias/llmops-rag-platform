import os
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq

# Inicializa o FastAPI
app = FastAPI(title="Busca Local com Groq")

# Inicializa o cliente da Groq (Cole sua chave gsk_ aqui)
API_KEY = "xxx"
client = Groq(api_key=API_KEY)

class PerguntaRequest(BaseModel):
    pergunta: str

def ler_arquivo_completo(caminho_arquivo: str) -> str:
    if not os.path.exists(caminho_arquivo):
        raise FileNotFoundError(f"O arquivo '{caminho_arquivo}' não foi encontrado.")
    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        return f.read()

@app.post("/perguntar")
async def processar_pergunta(request: PerguntaRequest):
    caminho_doc = "manual_plataforma.txt"
    
    try:
        conteudo_total = await asyncio.to_thread(ler_arquivo_completo, caminho_doc)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao ler o arquivo: {e}")

    # Monta o prompt com o conteúdo do seu manual de 17 linhas
    prompt_final = (
        f"Você é um assistente técnico preciso. Use o conteúdo do manual fornecido abaixo para responder à pergunta do usuário.\n"
        f"Se a resposta não estiver descrita no documento, informe que a informação não foi localizada.\n\n"
        f"--- CONTEXTO DO ARQUIVO MANUAL_PLATAFORMA.TXT ---\n{conteudo_total}\n----------------------------------\n\n"
        f"Pergunta do Usuário: {request.pergunta}\n\n"
        f"Resposta Objetiva:"
    )

    try:
        # Chama o modelo atualizado e ativo da Groq
        resposta_ia = await asyncio.to_thread(
            client.chat.completions.create,
            model="llama-3.3-70b-versatile",  # Versão atualizada de produção da Groq
            messages=[{"role": "user", "content": prompt_final}]
        )
        
        return {
            "pergunta": request.pergunta,
            "resposta": resposta_ia.choices[0].message.content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na API da Groq: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)