"""
Evaluation harness for NLQueryEngine.
Run from sql-rag-backend/ with:
    python -m eval.run_eval
"""
import sys, json, time
sys.path.append(".")

from app.retriever   import get_context_string
from app.generator   import generate_sql
from app.validator   import validate_sql
from app.synthesizer import synthesize_answer
from app.db          import readonly_engine
from app.config      import MAX_RETRIES, MAX_ROWS
from sqlalchemy      import text

EVAL_SET_PATH    = "eval/eval_set.json"
RESULTS_PATH     = "eval/results.json"


def run_pipeline(question):
    start = time.time()
    schema_context, source_tables = get_context_string(question)

    sql          = None
    retries_used = 0
    error_msg    = None
    error_feedback = None

    for attempt in range(MAX_RETRIES + 1):
        sql      = generate_sql(question, schema_context, error_feedback)
        is_valid, err = validate_sql(sql)
        if is_valid:
            break
        retries_used  += 1
        error_feedback = err
        if attempt == MAX_RETRIES:
            return {"success": False, "error": err, "sql": sql,
                    "retries": retries_used, "latency": time.time() - start,
                    "source_tables": source_tables}

    try:
        with readonly_engine.connect() as conn:
            result  = conn.execute(text(f"{sql.rstrip(';')} LIMIT {MAX_ROWS}"))
            columns = list(result.keys())
            rows    = [list(r) for r in result.fetchall()]
    except Exception as e:
        return {"success": False, "error": str(e), "sql": sql,
                "retries": retries_used, "latency": time.time() - start,
                "source_tables": source_tables}

    return {
        "success":       True,
        "sql":           sql,
        "columns":       columns,
        "row_count":     len(rows),
        "retries":       retries_used,
        "latency":       round(time.time() - start, 3),
        "source_tables": source_tables,
    }


def run_eval():
    with open(EVAL_SET_PATH) as f:
        eval_set = json.load(f)

    results  = []
    latencies = []
    recovered = 0

    print(f"\nRunning eval on {len(eval_set)} questions...\n{'─'*60}")

    for i, case in enumerate(eval_set, 1):
        question = case["question"]
        print(f"[{i:02d}] {question[:60]}")
        out = run_pipeline(question)

        status = "✓" if out["success"] else "✗"
        print(f"     {status}  latency={out.get('latency', 0):.2f}s  retries={out.get('retries', 0)}")

        if out["success"] and out.get("retries", 0) > 0:
            recovered += 1

        latencies.append(out.get("latency", 0))
        results.append({"question": question, **out})

    successes = sum(1 for r in results if r["success"])
    total     = len(results)
    failures  = [r for r in results if not r["success"]]

    latencies_sorted = sorted(latencies)
    p50  = latencies_sorted[len(latencies_sorted) // 2]
    p95  = latencies_sorted[int(len(latencies_sorted) * 0.95)]

    print(f"\n{'═'*60}")
    print(f"  Execution accuracy    : {successes}/{total} ({100*successes/total:.1f}%)")
    print(f"  Self-correction rate  : {recovered} queries recovered from initial failure")
    print(f"  Latency p50 / p95     : {p50:.2f}s / {p95:.2f}s")
    print(f"  Failed questions      : {len(failures)}")
    for f in failures:
        print(f"    ✗ {f['question'][:55]} → {f.get('error','?')[:40]}")
    print(f"{'═'*60}\n")

    with open(RESULTS_PATH, "w") as f:
        json.dump({
            "summary": {
                "total": total,
                "successes": successes,
                "accuracy_pct": round(100 * successes / total, 1),
                "self_corrections": recovered,
                "p50_latency": p50,
                "p95_latency": p95,
            },
            "results": results,
        }, f, indent=2)

    print(f"Results saved to {RESULTS_PATH}")


if __name__ == "__main__":
    run_eval()
