import io
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
    """Returns raw CSV content for use with mock_open"""
    return """Date,Description,Amount
2024-01-15,Coffee Shop,-5.00
2024-01-16,Grocery Store,-45.50
"""