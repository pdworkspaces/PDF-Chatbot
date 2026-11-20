
from langchain_ollama import OllamaEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from backend.config import (
    EMBEDDING_PROVIDER,
    GOOGLE_API_KEY,
    GEMINI_EMBEDDING_MODEL,
    GEMINI_EMBEDDING_DIMENSION,
    OLLAMA_BASE_URL,
    OLLAMA_EMBED_MODEL
)


def get_embedding_model():

    # Cloud embedding provider
    if EMBEDDING_PROVIDER == "google":

        if not GOOGLE_API_KEY:
            raise ValueError(
                "GOOGLE_API_KEY is not configured."
            )

        return GoogleGenerativeAIEmbeddings(
            model=GEMINI_EMBEDDING_MODEL,
            google_api_key=GOOGLE_API_KEY,
            output_dimensionality=GEMINI_EMBEDDING_DIMENSION
        )

    # Local embedding provider
    if EMBEDDING_PROVIDER == "ollama":

        return OllamaEmbeddings(
            model=OLLAMA_EMBED_MODEL,
            base_url=OLLAMA_BASE_URL
        )

    raise ValueError(
        "EMBEDDING_PROVIDER must be 'ollama' or 'google'."
    )
