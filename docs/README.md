# NLQueryEngine — Backend

Production-grade Natural Language to SQL RAG system built with FastAPI, PostgreSQL, pgvector, and Claude API.

## Setup

```bash
# 1. Create and activate virtual environment
python -m venv venv && source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Fill in your credentials
cp .env .env.local  # edit ANTHROPIC_API_KEY

# 4. Start Postgres with pgvector
docker run --name nlqe-db \
  -e POSTGRES_DB=chinook \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=pass \
  -p 5432:5432 -d ankane/pgvector:latest

# 5. Load Chinook dataset
psql -h localhost -U postgres -d chinook -f data/chinook.sql

# 6. Run DB setup (readonly role + pgvector extension)
psql -h localhost -U postgres -d chinook -f data/db_setup.sql

# 7. Index the schema
python -m app.indexer

# 8. Start the server
uvicorn app.main:app --reload --port 8000
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET  | `/api/health` | Health check |
| GET  | `/api/schema-tables` | List indexed tables |
| POST | `/api/query` | Run NL query |
| POST | `/api/index` | Re-trigger indexing |

## Running Tests

```bash
pytest tests/ -v
```

## Running Eval

```bash
python -m eval.run_eval
# Results saved to eval/results.json
```

## Architecture

```
Question → Schema Retrieval (pgvector) → SQL Generation (Claude)
        → Validation (sqlglot + EXPLAIN) → Self-Correction Loop
        → Execution (read-only role) → Answer Synthesis (Claude)
```
