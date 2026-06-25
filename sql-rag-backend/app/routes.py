from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text

from app.retriever   import get_context_string, get_all_table_names
from app.generator   import generate_sql
from app.validator   import validate_sql
from app.synthesizer import synthesize_answer
from app.db          import readonly_engine, ping
from app.config      import MAX_RETRIES, MAX_ROWS
from app.indexer     import run_indexer

router = APIRouter()


# ── Request / Response models ──────────────────────────────────────────────────

class QueryRequest(BaseModel):
    question: str
    conversation_history: list[dict] | None = None   # [{question, sql}, ...]


class QueryResponse(BaseModel):
    answer:       str
    sql:          str | None
    columns:      list[str] | None
    rows:         list[list] | None
    retries_used: int
    source_tables: list[str]
    error:        bool = False


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/health")
def health_check():
    db_ok = ping()
    return {
        "status": "ok" if db_ok else "degraded",
        "database": "connected" if db_ok else "unreachable",
    }


@router.get("/schema-tables")
def schema_tables():
    """Return list of all indexed table names for the sidebar."""
    try:
        tables = get_all_table_names()
        return {"tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not fetch schema: {str(e)}")


@router.post("/index")
def trigger_indexing():
    """Manually trigger schema re-indexing (useful after DB schema changes)."""
    try:
        count = run_indexer()
        return {"status": "ok", "documents_indexed": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")


@router.post("/query", response_model=QueryResponse)
def query_database(request: QueryRequest):
    """
    Main pipeline endpoint.
    1. Retrieve relevant schema context
    2. Generate SQL
    3. Validate (syntax + EXPLAIN + cost)
    4. Self-correct up to MAX_RETRIES times
    5. Execute on read-only connection
    6. Synthesize plain-English answer
    """
    question = request.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # Step 1: Retrieve schema context
    try:
        schema_context, source_tables = get_context_string(question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {str(e)}")

    # Steps 2-4: Generate → Validate → Self-correct loop
    sql          = None
    retries_used = 0
    error_feedback = None

    for attempt in range(MAX_RETRIES + 1):
        try:
            sql = generate_sql(
                question=question,
                schema_context=schema_context,
                error_feedback=error_feedback,
                conversation_history=request.conversation_history,
            )
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"LLM generation failed: {str(e)}")

        if sql == "CANNOT_ANSWER":
            return QueryResponse(
                answer="I could not find enough information in the schema to answer this question. Try rephrasing or ask about a specific table.",
                sql=None,
                columns=None,
                rows=None,
                retries_used=retries_used,
                source_tables=source_tables,
                error=True,
            )

        is_valid, err = validate_sql(sql)

        if is_valid:
            break

        retries_used  += 1
        error_feedback = err

        if attempt == MAX_RETRIES:
            return QueryResponse(
                answer=f"Could not generate a valid query after {MAX_RETRIES} attempts. Last error: {err}",
                sql=sql,
                columns=None,
                rows=None,
                retries_used=retries_used,
                source_tables=source_tables,
                error=True,
            )

    # Step 5: Execute on read-only DB
    try:
        with readonly_engine.connect() as conn:
            # Always enforce row cap
            safe_sql = sql.rstrip(";")
            result   = conn.execute(text(f"{safe_sql} LIMIT {MAX_ROWS}"))
            columns  = list(result.keys())
            rows     = [list(row) for row in result.fetchall()]
    except Exception as e:
        return QueryResponse(
            answer=f"Query execution failed: {str(e)}",
            sql=sql,
            columns=None,
            rows=None,
            retries_used=retries_used,
            source_tables=source_tables,
            error=True,
        )

    # Step 6: Synthesize plain-English answer
    try:
        answer = synthesize_answer(question, columns, rows)
    except Exception:
        answer = f"Query returned {len(rows)} row(s)."

    return QueryResponse(
        answer=answer,
        sql=sql,
        columns=columns,
        rows=rows,
        retries_used=retries_used,
        source_tables=source_tables,
        error=False,
    )
