from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from pgvector.sqlalchemy import Vector
from app.config import DATABASE_URL, READONLY_DATABASE_URL

# Admin engine (indexing, schema inspection)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Read-only engine (query execution — never admin privileges)
readonly_engine = create_engine(READONLY_DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_pgvector(conn):
    """Enable pgvector extension if not already present."""
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    conn.commit()


def create_schema_table():
    """Create the schema_docs table with a vector column."""
    with engine.connect() as conn:
        ensure_pgvector(conn)
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS schema_docs (
                id          SERIAL PRIMARY KEY,
                table_name  TEXT NOT NULL,
                doc_text    TEXT NOT NULL,
                embedding   VECTOR(384)
            )
        """))
        conn.commit()
    print("[db] schema_docs table ready.")


def ping():
    """Health check — verify DB connection."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"[db] ping failed: {e}")
        return False
