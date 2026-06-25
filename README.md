# NLQueryEngine

> **Production-grade Natural Language Database Intelligence Platform**
> Ask anything about your database in plain English. Get back validated SQL, real results, and a plain-English explanation.

---

## Architecture

```
User Question
     │
     ▼
[Schema Retrieval]  pgvector cosine similarity → top-k relevant tables + glossary
     │
     ▼
[SQL Generation]    Claude API, grounded in retrieved context only
     │
     ▼
[Validation Loop]   sqlglot syntax → EXPLAIN dry-run → cost guard → self-correct
     │
     ▼
[Execution]         Read-only Postgres role, 100-row cap
     │
     ▼
[Answer Synthesis]  Claude API → plain-English answer
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python · FastAPI · uvicorn |
| Database | PostgreSQL 16 · pgvector |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| LLM | Claude API (claude-sonnet-4-6) |
| SQL Validation | sqlglot · PostgreSQL EXPLAIN |
| Frontend | React 18 · Vite · Tailwind CSS |
| Deployment | Docker · Docker Compose |

## Quick Start

```bash
# Clone and enter
git clone https://github.com/your-username/nlqueryengine
cd nlqueryengine

# Start Postgres
docker run --name nlqe-db \
  -e POSTGRES_DB=chinook -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=pass \
  -p 5432:5432 -d ankane/pgvector:latest

# Load data + setup
psql -h localhost -U postgres -d chinook -f sql-rag-backend/data/chinook.sql
psql -h localhost -U postgres -d chinook -f sql-rag-backend/data/db_setup.sql

# Backend
cd sql-rag-backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# Add ANTHROPIC_API_KEY to .env
python -m app.indexer          # index schema into pgvector
uvicorn app.main:app --reload  # runs on :8000

# Frontend (new terminal)
cd sql-rag-frontend
npm install
npm run dev                    # runs on :3000
```

## Eval Results

Run `python -m eval.run_eval` from `sql-rag-backend/` to generate metrics:

| Metric | Score |
|--------|-------|
| Execution accuracy | — |
| Self-correction recovery rate | — |
| p50 latency | — |
| p95 latency | — |

*(Fill in after running eval)*

## Project Structure

```
sql-rag-project/
├── sql-rag-backend/        FastAPI backend
│   ├── app/                Core pipeline modules
│   ├── eval/               Evaluation harness + results
│   ├── tests/              pytest unit tests
│   └── data/               DB setup SQL
├── sql-rag-frontend/       React frontend
│   └── src/
│       ├── components/     UI components
│       └── api/            Axios client
├── docs/                   Architecture diagram, demo GIF
└── docker-compose.yml
```
