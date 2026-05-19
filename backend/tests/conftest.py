import io
import os
import sqlite3
from pathlib import Path

import pytest
from werkzeug.datastructures import FileStorage

@pytest.fixture
def mock_csv_file():
    csv_data = """Date,Description,Amount
2024-01-15,Coffee Shop,-5.00
2024-01-16,Grocery Store,-45.50
"""
    return FileStorage(
        stream=io.BytesIO(csv_data.encode("utf-8")),
        filename="test.csv",
        content_type="text/csv",
    )

@pytest.fixture
def mock_csv_content():
    return """Date,Description,Amount
2024-01-15,Coffee Shop,-5.00
2024-01-16,Grocery Store,-45.50
"""

@pytest.fixture
def test_db_path(tmp_path, monkeypatch):
    db_path = tmp_path / "test.sqlite"
    monkeypatch.setenv("DATABASE_LOCATION", str(db_path))
    return db_path

@pytest.fixture
def seeded_db(test_db_path):
    schema_path = Path(__file__).resolve().parents[2] / "schema.sql"

    with sqlite3.connect(test_db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(schema_path.read_text(encoding="utf-8"))
        connection.execute(
            'INSERT INTO "user" (id, username, password, email) VALUES (?, ?, ?, ?)',
            (1, "testuser", "password", "test@example.com"),
        )
        connection.commit()

    return test_db_path