from langchain_ollama import OllamaEmbeddings

from backend.config import (
    OLLAMA_BASE_URL,
    OLLAMA_EMBED_MODEL
)


def get_embedding_model():

    embeddings = OllamaEmbeddings(
        model=OLLAMA_EMBED_MODEL,
        base_url=OLLAMA_BASE_URL
    )

    return embeddings