import os
import json
import asyncio
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from groq import Groq
import chromadb
from chromadb.utils import embedding_functions

app = FastAPI(title="LLMOps Agent API - RAG & Upload")

# --- Security & Initialization ---
API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set.")

groq_client = Groq(api_key=API_KEY)

# --- 1. VECTOR DATABASE CONFIGURATION (RAG) ---
emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"
)
chroma_client = chromadb.PersistentClient(path="./vector_db")
collection = chroma_client.get_or_create_collection(name="sre_manual", embedding_function=emb_fn)


# --- 2. AGENT TOOLS ---
def search_sre_manual(query: str) -> str:
    """Tool: Searches the ChromaDB Knowledge Base"""
    print(f"🛠️ [Tool Called] Searching RAG for: {query}")
    results = collection.query(query_texts=[query], n_results=3)
    if not results["documents"][0]:
        return "No information found in the manual."
    return "\n---\n".join(results["documents"][0])

def get_current_weather(location: str) -> str:
    """Tool: Simulated external API"""
    print(f"[Tool Called] Fetching weather for: {location}")
    return f"The current weather in {location} is 28 degrees, sunny."

available_tools = {
    "search_sre_manual": search_sre_manual,
    "get_current_weather": get_current_weather
}

tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "search_sre_manual",
            "description": "Use to find information about Harness, deployments, pipelines, CI/CD, and SRE rules.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The specific search term to look for."}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "The city name."}
                },
                "required": ["location"]
            }
        }
    }
]

# --- 3. API ROUTES ---

class QuestionRequest(BaseModel):
    question: str

@app.post("/ask")
async def process_question(request: QuestionRequest):
    """SRE Route: Ask the Agent"""
    try:
        # STEP 1: Strict Guardrails BEFORE the AI decides
        messages = [
            {
                "role": "system", 
                "content": (
                    "You are a strict SRE assistant. "
                    "CRITICAL: When calling a tool, you MUST use valid JSON arguments. "
                    "NEVER output raw XML or <function> tags. "
                    "Always reply to the user in Portuguese."
                )
            },
            {"role": "user", "content": request.question}
        ]

        # STEP 2: The AI decides which tool to use
        response = await asyncio.to_thread(
            groq_client.chat.completions.create,
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=tools_schema,
            tool_choice="auto",
            temperature=0.1 # Low temperature to prevent syntax hallucinations
        )

        response_message = response.choices[0].message
        messages.append(response_message) # Append the AI's decision to history

        # STEP 3: Execute the tool if the AI requested it
        if response_message.tool_calls:
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                function_to_call = available_tools[function_name]
                function_response = await asyncio.to_thread(function_to_call, **function_args)
                
                # Append the REAL Python execution result to the history
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                })
            
            # STEP 4: AI generates the final answer based on the tool's result
            final_response = await asyncio.to_thread(
                groq_client.chat.completions.create,
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.1
            )
            final_answer = final_response.choices[0].message.content
            tool_used = True
            
            # FinOps Metrics
            used_tokens = final_response.usage.total_tokens
            estimated_cost = (used_tokens / 1000) * 0.0007 # Base cost for LLaMA 70B
            print(f"[FinOps] Tokens consumed: {used_tokens}")
            print(f"[FinOps] Estimated cost: ${estimated_cost:.6f}")
            
        else:
            final_answer = response_message.content
            tool_used = False

        return {
            "question": request.question,
            "tool_used": tool_used,
            "answer": final_answer
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Error: {str(e)}")


@app.post("/upload_document")
async def update_knowledge_base(file: UploadFile = File(...)):
    """SRE Route: Updates the knowledge base dynamically"""
    try:
        content = await file.read()
        text = content.decode("utf-8")
        
        chunks = [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]
        
        documents = []
        ids = []
        id_prefix = file.filename.replace(".txt", "")
        
        for i, chunk in enumerate(chunks):
            enriched_chunk = f"[Context: File {file.filename}] {chunk}"
            documents.append(enriched_chunk)
            ids.append(f"{id_prefix}_chunk_{i}")
        
        collection.add(documents=documents, ids=ids)
        
        return {
            "status": "success", 
            "message": f"File {file.filename} successfully vectorized!",
            "processed_chunks": len(chunks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)