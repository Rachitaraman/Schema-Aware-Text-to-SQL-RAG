import anthropic
import re
from app.config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You are an expert PostgreSQL query writer.
Your ONLY job is to write a single valid PostgreSQL SELECT query based on the schema context provided.

Rules:
- Use ONLY tables and columns that appear in the schema context below. Never invent columns.
- Always write SELECT queries. Never write INSERT, UPDATE, DELETE, DROP, or any DML/DDL.
- Always alias aggregated columns clearly (e.g. SUM(total) AS total_revenue).
- Always add LIMIT 100 unless the question explicitly asks for all records.
- Return ONLY the raw SQL — no markdown, no backticks, no explanation, no preamble.
- If the question is unanswerable from the given schema, return exactly: CANNOT_ANSWER
"""

def clean_sql(raw: str) -> str:
    """Strip markdown fences and whitespace from LLM output."""
    raw = raw.strip()
    raw = re.sub(r"^```[a-zA-Z]*\n?", "", raw)
    raw = re.sub(r"```$", "", raw)
    return raw.strip()


def generate_sql(
    question: str,
    schema_context: str,
    error_feedback: str | None = None,
    conversation_history: list | None = None,
) -> str:
    """
    Generate a SQL query from a natural language question.

    Args:
        question: The user's NL question.
        schema_context: Retrieved schema/glossary docs as a formatted string.
        error_feedback: If a previous attempt failed, include the error here for self-correction.
        conversation_history: Optional list of prior (question, sql) pairs for multi-turn context.

    Returns:
        Raw SQL string, or "CANNOT_ANSWER".
    """

    history_str = ""
    if conversation_history:
        history_str = "\n\nConversation history (for follow-up context):\n"
        for turn in conversation_history[-2:]:  # last 2 turns max
            history_str += f"Q: {turn['question']}\nSQL: {turn['sql']}\n\n"

    retry_str = ""
    if error_feedback:
        retry_str = f"\n\nPREVIOUS ATTEMPT FAILED with this error:\n{error_feedback}\nFix the issue and return corrected SQL only."

    user_content = f"""Schema context:
{schema_context}
{history_str}
Question: {question}{retry_str}

SQL:"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    )

    raw = response.content[0].text
    return clean_sql(raw)
