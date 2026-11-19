from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from backend.config import (
    OLLAMA_BASE_URL, OLLAMA_CHAT_MODEL,
    GOOGLE_API_KEY, GEMINI_MODEL
)

def get_llm(provider: str):
    provider = provider.lower()

    if provider == "ollama":
        return ChatOllama(
            model=OLLAMA_CHAT_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0
        )

    if provider == "gemini":
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is not configured in .env")
        return ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=GOOGLE_API_KEY,
            temperature=0
        )

    raise ValueError("Provider must be 'ollama' or 'gemini'")
