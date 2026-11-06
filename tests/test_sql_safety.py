import pytest
from app.sql_analytics import validate_readonly_sql

def test_select_allowed():
    assert "LIMIT 200" in validate_readonly_sql("SELECT COUNT(*) FROM orders")

def test_existing_limit_preserved():
    assert validate_readonly_sql("SELECT * FROM orders LIMIT 10") == (
        "SELECT * FROM orders LIMIT 10"
    )

def test_insert_blocked():
    with pytest.raises(ValueError): validate_readonly_sql("INSERT INTO orders VALUES (1)")

def test_multiple_statements_blocked():
    with pytest.raises(ValueError): validate_readonly_sql("SELECT * FROM orders; DROP TABLE orders")

def test_unknown_table_blocked():
    with pytest.raises(ValueError): validate_readonly_sql("SELECT * FROM users")
