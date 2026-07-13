import chromadb
from chromadb.utils import embedding_functions

# 1. Define the multilingual embedding model
emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"
)

# Connect to the local vector database directory
client = chromadb.PersistentClient(path="./vector_db")

# 2. Create the collection passing the embedding function
collection = client.get_or_create_collection(
    name="sre_manual", 
    embedding_function=emb_fn
)

# Read the local text file
with open("platform_manual.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Split the text into chunks using double newlines
chunks = [chunk_text.strip() for chunk_text in text.split("\n\n") if chunk_text.strip()]

documents_list = []
ids = []

for i, chunk in enumerate(chunks):
    # LLMOps Technique: Context Enrichment
    # We inject information about the text's content so the vector database doesn't lose track.
    enriched_chunk = f"[Context: Harness Platform Documentation] {chunk}"
    documents_list.append(enriched_chunk)
    ids.append(f"chunk_{i}")

# Add the documents and their IDs to the collection
collection.add(
    documents=documents_list,
    ids=ids
)

print(f"Success! Vector database recreated with Multilingual model and enriched context.")