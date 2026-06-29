from openai import OpenAI
from app.config import get_llm_provider_config

provider_config = get_llm_provider_config()
client = OpenAI(api_key=provider_config["api_key"], base_url=provider_config["base_url"]) if provider_config["provider"] == "groq" else None

SYSTEM_PROMPT = """You are a helpful data analyst assistant.
You will be given a user's question and the SQL query results that answer it.
Write a clear, concise plain-English answer (2-4 sentences max).
- Lead with the direct answer.
- Mention key numbers or names from the data.
- If the result is empty, say so clearly.
- Do not mention SQL, tables, or technical details.
- Do not add any preamble like "Based on the data..." — just answer directly.
"""


def synthesize_answer(
    question: str,
    columns: list[str],
    rows: list[list],
) -> str:
    """
    Convert a SQL result set into a plain-English answer.

    Args:
        question: Original NL question.
        columns: Column names from the result.
        rows: Row data (up to 20 rows shown to LLM).

    Returns:
        Plain-English answer string.
    """
    if not rows:
        return "The query returned no results for your question."

    # Show max 20 rows to LLM to avoid huge prompts
    sample_rows = rows[:20]
    result_str  = f"Columns: {columns}\nRows: {sample_rows}"
    if len(rows) > 20:
        result_str += f"\n(showing 20 of {len(rows)} total rows)"

    if provider_config["provider"] == "groq":
        response = client.chat.completions.create(
            model=provider_config["model"],
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Question: {question}\n\nQuery result:\n{result_str}"},
            ],
            temperature=0,
            max_tokens=300,
        )
        return (response.choices[0].message.content or "").strip()

    import anthropic

    anthropic_client = anthropic.Anthropic(api_key=provider_config["api_key"])
    response = anthropic_client.messages.create(
        model=provider_config["model"],
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Question: {question}\n\nQuery result:\n{result_str}",
        }],
    )

    return response.content[0].text.strip()
