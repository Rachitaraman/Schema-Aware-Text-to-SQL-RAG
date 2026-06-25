import sqlglot
import re
from sqlalchemy import text
from app.db import readonly_engine
from app.config import QUERY_COST_THRESHOLD


def check_syntax(sql: str) -> tuple[bool, str | None]:
    """Layer 1: Parse SQL with sqlglot to catch syntax errors without hitting DB."""
    try:
        sqlglot.parse_one(sql, dialect="postgres")
        return True, None
    except sqlglot.errors.ParseError as e:
        return False, f"Syntax error: {str(e)}"


def check_is_select(sql: str) -> tuple[bool, str | None]:
    """Layer 0: Reject any non-SELECT statement outright."""
    stripped = sql.strip().upper()
    forbidden = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "CREATE", "GRANT"]
    for keyword in forbidden:
        if stripped.startswith(keyword):
            return False, f"Only SELECT queries are permitted. Got: {keyword}"
    return True, None


def check_explain(sql: str) -> tuple[bool, str | None, float | None]:
    """
    Layer 2: Run EXPLAIN (no actual execution) against the read-only DB.
    Returns (is_valid, error_message, estimated_cost).
    """
    try:
        with readonly_engine.connect() as conn:
            result = conn.execute(text(f"EXPLAIN (FORMAT JSON) {sql}"))
            plan   = result.fetchone()[0]
            # Extract estimated cost from the query plan
            estimated_cost = plan[0]["Plan"].get("Total Cost", 0)
            return True, None, estimated_cost
    except Exception as e:
        error = str(e)
        # Strip SQLAlchemy internals for cleaner LLM feedback
        error = re.sub(r"\(Background on this error.*\)", "", error).strip()
        return False, f"Schema/execution error: {error}", None


def check_cost(estimated_cost: float) -> tuple[bool, str | None]:
    """Layer 3: Reject queries with absurdly high estimated cost (full-table scans on huge tables)."""
    if estimated_cost and estimated_cost > QUERY_COST_THRESHOLD:
        return False, (
            f"Query estimated cost ({estimated_cost:.0f}) exceeds threshold ({QUERY_COST_THRESHOLD}). "
            "Add a WHERE clause or LIMIT to reduce scope."
        )
    return True, None


def validate_sql(sql: str) -> tuple[bool, str | None]:
    """
    Full 3-layer validation pipeline.
    Returns (is_valid, error_message_or_None).
    """
    if sql.strip() == "CANNOT_ANSWER":
        return False, "CANNOT_ANSWER"

    # Layer 0: must be SELECT
    ok, err = check_is_select(sql)
    if not ok:
        return False, err

    # Layer 1: syntax check
    ok, err = check_syntax(sql)
    if not ok:
        return False, err

    # Layer 2: EXPLAIN dry-run
    ok, err, cost = check_explain(sql)
    if not ok:
        return False, err

    # Layer 3: cost guard
    ok, err = check_cost(cost)
    if not ok:
        return False, err

    return True, None
