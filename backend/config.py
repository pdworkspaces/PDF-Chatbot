
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent


# Resolve local or absolute storage paths
def resolve_data_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else BASE_DIR / path


# Storage configuration
UPLOAD_DIR = resolve_data_path(
    os.getenv("UPLOAD_DIR", "data/uploads")
)

CHROMA_DB_DIR = resolve_data_path(
    os.getenv("CHROMA_DB_DIR", "data/chroma_db")
)

DATABASE_PATH = resolve_data_path(
    os.getenv("DATABASE_URL", "data/chat_history.db")
)


# Gemini configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
)

GEMINI_EMBEDDING_MODEL = os.getenv(
    "GEMINI_EMBEDDING_MODEL",
    "gemini-embedding-001"
)

GEMINI_EMBEDDING_DIMENSION = int(
    os.getenv("GEMINI_EMBEDDING_DIMENSION", "768")
)


# Embedding provider: ollama or google
EMBEDDING_PROVIDER = os.getenv(
    "EMBEDDING_PROVIDER",
    "ollama"
).lower()


# Ollama configuration for local development
OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434"
)

OLLAMA_CHAT_MODEL = os.getenv(
    "OLLAMA_CHAT_MODEL",
    "llama3.2:3b"
)

OLLAMA_EMBED_MODEL = os.getenv(
    "OLLAMA_EMBED_MODEL",
    "nomic-embed-text"
)


# Upload configuration
MAX_UPLOAD_MB = int(
    os.getenv("MAX_UPLOAD_MB", "20")
)


# Create storage directories
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
