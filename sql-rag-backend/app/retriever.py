from sentence_transformers import SentenceTransformer
from sqlalchemy import text
from app.db import engine
from app.config import EMBED_MODEL, TOP_K_TABLES

# Load model once at module level (not per-request)
_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL)
    return _model


def retrieve_schema_context(question: str, k: int = TOP_K_TABLES) -> list[dict]:
    """
    Embed the question, then query pgvector for the top-k most relevant
    schema documents (tables + glossary entries) using cosine similarity.

    Returns a list of dicts: [{table_name, doc_text, similarity}, ...]
    """
    model     = get_model()
    question_emb = model.encode([question], normalize_embeddings=True)[0].tolist()

    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT
                    table_name,
                    doc_text,
                    1 - (embedding <=> CAST(:embedding AS vector)) AS similarity
                FROM schema_docs
                ORDER BY embedding <=> CAST(:embedding AS vector)
                LIMIT :k
            """),
            {"embedding": str(question_emb), "k": k},
        ).fetchall()

    results = [
        {
            "table_name": row[0],
            "doc_text":   row[1],
            "similarity": round(float(row[2]), 4),
        }
        for row in rows
    ]

    return results


def get_context_string(question: str) -> tuple[str, list[str]]:
    """
    Convenience wrapper: returns (formatted_context_string, list_of_table_names).
    """
    results      = retrieve_schema_context(question)
    context_str  = "\n\n---\n\n".join(r["doc_text"] for r in results)
    source_tables = [
        r["table_name"] for r in results
        if r["table_name"] != "__glossary__"
    ]
    return context_str, source_tables


def get_all_table_names() -> list[str]:
    """Return all non-glossary table names from the index."""
    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT DISTINCT table_name
                FROM schema_docs
                WHERE table_name != '__glossary__'
                ORDER BY table_name
            """)
        ).fetchall()
    return [row[0] for row in rows]
