import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

def resolve_data_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else BASE_DIR / path

UPLOAD_DIR = resolve_data_path(os.getenv("UPLOAD_DIR", "data/uploads"))
CHROMA_DB_DIR = resolve_data_path(os.getenv("CHROMA_DB_DIR", "data/chroma_db"))
DATABASE_PATH = resolve_data_path(os.getenv("DATABASE_URL", "data/chat_history.db"))

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "llama3.2:3b")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "20"))

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
