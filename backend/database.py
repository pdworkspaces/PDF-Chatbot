import sqlite3
from backend.config import DATABASE_PATH

def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                document_id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                total_pages INTEGER NOT NULL,
                total_chunks INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                provider TEXT NOT NULL,
                sources TEXT NOT NULL DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def save_document(document_id, filename, total_pages, total_chunks):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO documents (document_id, filename, total_pages, total_chunks) VALUES (?, ?, ?, ?)",
            (document_id, filename, total_pages, total_chunks)
        )

def document_exists(document_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM documents WHERE document_id = ?", (document_id,)
        ).fetchone()
        return row is not None

def save_chat(document_id, question, answer, provider, sources):
    source_text = ",".join(str(x) for x in sources)
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO chat_history
            (document_id, question, answer, provider, sources)
            VALUES (?, ?, ?, ?, ?)""",
            (document_id, question, answer, provider, source_text)
        )

def get_history(document_id):
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT question, answer, provider, sources, created_at
            FROM chat_history WHERE document_id = ? ORDER BY id""",
            (document_id,)
        ).fetchall()
        return [
            {**dict(row), "sources": [int(x) for x in row["sources"].split(",") if x]}
            for row in rows
        ]

def delete_document_record(document_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM chat_history WHERE document_id = ?", (document_id,))
        conn.execute("DELETE FROM documents WHERE document_id = ?", (document_id,))
