import pytest
import io

@pytest.fixture
def mock_csv_file():
    """Provides a mock CSV file as StringIO"""
    csv_data = """Date,Description,Amount
2024-01-15,Coffee Shop,-5.00
2024-01-16,Grocery Store,-45.50
"""
    return io.StringIO(csv_data)

@pytest.fixture
def mock_csv_content():
    """Returns raw CSV content for use with mock_open"""
    return """Date,Description,Amount
2024-01-15,Coffee Shop,-5.00
2024-01-16,Grocery Store,-45.50
"""