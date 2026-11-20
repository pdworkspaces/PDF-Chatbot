
from backend.services.embedding_service import get_embedding_model

embeddings = get_embedding_model()

result = embeddings.embed_query(
    "What is the annual leave policy?"
)

print("Embedding successful!")
print("Dimensions:", len(result))
print("First 5 values:", result[:5])
