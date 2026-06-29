from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables from .env.local file
env_file = Path(__file__).parent.parent / ".env.local"
load_dotenv(dotenv_path=env_file)

DATABASE_URL          = os.getenv("DATABASE_URL", "postgresql://postgres:pass@localhost:5432/chinook")
READONLY_DATABASE_URL = os.getenv("READONLY_DATABASE_URL", "postgresql://rag_readonly:readonly_pass@localhost:5432/chinook")
ANTHROPIC_API_KEY     = os.getenv("ANTHROPIC_API_KEY", "")
GROQ_API_KEY          = os.getenv("GROQ_API_KEY", "")
LLM_PROVIDER          = os.getenv("LLM_PROVIDER", "groq").strip().lower()
EMBED_MODEL           = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
TOP_K_TABLES          = int(os.getenv("TOP_K_TABLES", 5))
MAX_RETRIES           = int(os.getenv("MAX_RETRIES", 2))
MAX_ROWS              = int(os.getenv("MAX_ROWS", 100))
QUERY_COST_THRESHOLD  = int(os.getenv("QUERY_COST_THRESHOLD", 100000))


def get_llm_provider_config() -> dict:
    if LLM_PROVIDER == "anthropic":
        return {
            "provider": "anthropic",
            "api_key": ANTHROPIC_API_KEY,
            "model": os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6"),
            "base_url": None,
        }

    return {
        "provider": "groq",
        "api_key": GROQ_API_KEY or ANTHROPIC_API_KEY,
        "model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        "base_url": "https://api.groq.com/openai/v1",
    }
