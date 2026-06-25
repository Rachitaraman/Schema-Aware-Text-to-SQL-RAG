from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL          = os.getenv("DATABASE_URL", "postgresql://postgres:pass@localhost:5432/chinook")
READONLY_DATABASE_URL = os.getenv("READONLY_DATABASE_URL", "postgresql://rag_readonly:readonly_pass@localhost:5432/chinook")
ANTHROPIC_API_KEY     = os.getenv("ANTHROPIC_API_KEY", "")
EMBED_MODEL           = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
TOP_K_TABLES          = int(os.getenv("TOP_K_TABLES", 5))
MAX_RETRIES           = int(os.getenv("MAX_RETRIES", 2))
MAX_ROWS              = int(os.getenv("MAX_ROWS", 100))
QUERY_COST_THRESHOLD  = int(os.getenv("QUERY_COST_THRESHOLD", 100000))
