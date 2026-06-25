from sqlalchemy import inspect, text
from sentence_transformers import SentenceTransformer
from app.db import engine, create_schema_table
from app.glossary import GLOSSARY_ENTRIES
from app.config import EMBED_MODEL


def build_table_doc(inspector, engine, table_name: str) -> str:
    """Build an enriched text document for a single table."""
    columns = inspector.get_columns(table_name)
    fks     = inspector.get_foreign_keys(table_name)
    pk      = inspector.get_pk_constraint(table_name)

    col_str = ", ".join(
        f"{c['name']} ({str(c['type']).split('(')[0]})"
        for c in columns
    )

    fk_str = ", ".join(
        f"{fk['constrained_columns']} → {fk['referred_table']}.{fk['referred_columns']}"
        for fk in fks
    ) or "none"

    pk_str = str(pk.get("constrained_columns", [])) if pk else "unknown"

    # Pull 2 sample rows to ground the LLM on real values
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text(f'SELECT * FROM "{table_name}" LIMIT 2')
            )
            sample_rows = [dict(zip(result.keys(), row)) for row in result.fetchall()]
    except Exception:
        sample_rows = []

    sample_str = str(sample_rows) if sample_rows else "no sample data available"

    return (
        f"Table: {table_name}\n"
        f"Columns: {col_str}\n"
        f"Primary key: {pk_str}\n"
        f"Foreign keys: {fk_str}\n"
        f"Sample rows: {sample_str}"
    )


def run_indexer():
    """
    Main indexing pipeline:
    1. Drop and recreate schema_docs table
    2. Inspect all tables in the DB
    3. Build enriched doc text per table
    4. Add business glossary entries
    5. Embed all docs with sentence-transformers
    6. Insert into schema_docs (pgvector)
    """
    print("[indexer] Starting schema indexing...")
    create_schema_table()

    # Clear existing index
    with engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE schema_docs RESTART IDENTITY"))
        conn.commit()

    model     = SentenceTransformer(EMBED_MODEL)
    inspector = inspect(engine)
    tables    = inspector.get_table_names()

    print(f"[indexer] Found {len(tables)} tables.")

    documents = []

    # Schema documents
    for table_name in tables:
        if table_name == "schema_docs":
            continue
        doc_text = build_table_doc(inspector, engine, table_name)
        documents.append({"table_name": table_name, "doc_text": doc_text})
        print(f"  ✓ {table_name}")

    # Glossary documents
    for entry in GLOSSARY_ENTRIES:
        documents.append(entry)
    print(f"[indexer] + {len(GLOSSARY_ENTRIES)} glossary entries.")

    # Embed all at once (batch is faster)
    texts      = [d["doc_text"] for d in documents]
    embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)

    # Insert into Postgres
    with engine.connect() as conn:
        for doc, emb in zip(documents, embeddings):
            conn.execute(
                text("""
                    INSERT INTO schema_docs (table_name, doc_text, embedding)
                    VALUES (:table_name, :doc_text, :embedding)
                """),
                {
                    "table_name": doc["table_name"],
                    "doc_text":   doc["doc_text"],
                    "embedding":  emb.tolist(),
                },
            )
        conn.commit()

    print(f"[indexer] Done. {len(documents)} documents indexed.")
    return len(documents)


if __name__ == "__main__":
    run_indexer()
