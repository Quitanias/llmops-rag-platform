import chromadb
from chromadb.utils import embedding_functions

# 1. Define o modelo matemático multilíngue (melhor para português)
emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"
)

client = chromadb.PersistentClient(path="./banco_vetorial")

# 2. Passa a função de embedding na criação da collection
collection = client.get_or_create_collection(
    name="manual_sre", 
    embedding_function=emb_fn
)

with open("manual_plataforma.txt", "r", encoding="utf-8") as f:
    texto = f.read()

chunks = [pedaco.strip() for pedaco in texto.split("\n\n") if pedaco.strip()]

documentos = []
ids = []

for i, chunk in enumerate(chunks):
    # TÉCNICA DE LLMOps: Enriquecimento de Contexto
    # Injetamos sobre o que é o texto para o banco vetorial não se perder
    chunk_enriquecido = f"[Contexto: Documentação Plataforma Harness] {chunk}"
    documentos.append(chunk_enriquecido)
    ids.append(f"chunk_{i}")

collection.add(
    documents=documentos,
    ids=ids
)

print(f"Sucesso! Banco recriado com modelo Multilíngue e contexto enriquecido.")