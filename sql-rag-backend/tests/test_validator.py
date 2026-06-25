"""
Unit tests for the SQL validation pipeline.
Run with: pytest tests/test_validator.py -v
"""
import pytest
import sys
sys.path.append(".")

from app.validator import check_syntax, check_is_select, validate_sql


class TestCheckIsSelect:
    def test_valid_select(self):
        ok, err = check_is_select("SELECT * FROM customers")
        assert ok is True
        assert err is None

    def test_rejects_insert(self):
        ok, err = check_is_select("INSERT INTO customers VALUES (1, 'a')")
        assert ok is False
        assert "INSERT" in err

    def test_rejects_drop(self):
        ok, err = check_is_select("DROP TABLE customers")
        assert ok is False

    def test_rejects_delete(self):
        ok, err = check_is_select("DELETE FROM customers WHERE id = 1")
        assert ok is False

    def test_rejects_update(self):
        ok, err = check_is_select("UPDATE customers SET name = 'x'")
        assert ok is False

    def test_rejects_truncate(self):
        ok, err = check_is_select("TRUNCATE TABLE customers")
        assert ok is False

    def test_case_insensitive(self):
        ok, err = check_is_select("select * from customers")
        assert ok is True


class TestCheckSyntax:
    def test_valid_sql(self):
        ok, err = check_syntax("SELECT id, name FROM customers WHERE id = 1")
        assert ok is True

    def test_valid_aggregate(self):
        ok, err = check_syntax("SELECT COUNT(*) AS total FROM invoices GROUP BY customer_id")
        assert ok is True

    def test_invalid_sql(self):
        ok, err = check_syntax("SELECT FROM WHERE")
        assert ok is False
        assert err is not None

    def test_unclosed_paren(self):
        ok, err = check_syntax("SELECT * FROM (SELECT id FROM customers")
        assert ok is False

    def test_valid_join(self):
        ok, err = check_syntax(
            "SELECT c.first_name, SUM(i.total) FROM customers c "
            "JOIN invoices i ON c.customer_id = i.customer_id GROUP BY c.customer_id"
        )
        assert ok is True


class TestCannotAnswer:
    def test_cannot_answer_flag(self):
        ok, err = validate_sql("CANNOT_ANSWER")
        assert ok is False
        assert err == "CANNOT_ANSWER"
