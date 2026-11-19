from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.chat import router
from backend.database import init_db

app = FastAPI(
    title="AI PDF Chatbot API",
    description="RAG chatbot using LangChain, LangGraph, ChromaDB, Ollama and Gemini.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def health():
    return {"status": "ok", "message": "AI PDF Chatbot API is running"}

app.include_router(router)
