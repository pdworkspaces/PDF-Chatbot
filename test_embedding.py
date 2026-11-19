from langchain_ollama import OllamaEmbeddings

embeddings = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url="http://localhost:11434"
)

vector = embeddings.embed_query(
    "What is Retrieval Augmented Generation?"
)

print("Embedding successful!")
print("Vector dimensions:", len(vector))
print("First 5 values:", vector[:5])