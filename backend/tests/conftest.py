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
    def _make():
        return FileStorage(
            stream=io.BytesIO(csv_data.encode("utf-8")),
            filename="test.csv",
            content_type="text/csv",
        )
    return _make

@pytest.fixture
def mock_csv_content():
    return """Date,Description,Amount
2024-01-15,Coffee Shop,-5.00
2024-01-16,Grocery Store,-45.50
"""

@pytest.fixture
def test_db_path(tmp_path, monkeypatch):
    db_path = tmp_path / "test.sqlite"
    # set both env names used in code (case mismatch in pullReport)
    monkeypatch.setenv("DATABASE_LOCATION", str(db_path))
    monkeypatch.setenv("Database_Location", str(db_path))
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


@pytest.fixture
def mock_get_transactions(monkeypatch):
    def fake_run(report, returnType, internal_transfers):
        return [
            {"date": "2024-01-15", "description": "Coffee Shop", "amount": -5.00}
        ]
    import src.getTransactions as gt
    monkeypatch.setattr(gt, "run", fake_run)
    return fake_run


@pytest.fixture
def mock_valid_user(monkeypatch):
    # Patch uploadTransaction.validUser to avoid DB binding issues in tests
    import src.uploadTransaction as ut
    monkeypatch.setattr(ut, "validUser", lambda uid: True)
    return True


@pytest.fixture
def client(seeded_db):
    # create a Flask test client that uses the seeded test database
    import backend.app as app_module
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as client:
        yield client