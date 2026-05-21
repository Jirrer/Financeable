import io
import pytest


def test_create_report(client, mock_csv_file, mock_get_transactions):
    mock_csv_file.stream.seek(0)
    data = {
        "returnType": "JSON",
        "internal_transfers": ""
    }
    data["report"] = (mock_csv_file.stream, mock_csv_file.filename)

    response = client.post("/create-report", data=data, content_type="multipart/form-data")

    assert response.status_code == 200
    body = response.get_json()
    assert body["Status"] == "Success"
    assert body["transactions"] == mock_get_transactions(None, None, None)


def test_upload_report(client, mock_valid_user):
    # uploadTransaction expects a dict of transactions keyed by some id
    payload = {
        "user_id": 1,
        "transactions": {
            "t1": {
                "group": "purchase",
                "value": 10.0,
                "date": "2024-01-01",
                "info": "t",
                "category": "food",
            }
        },
    }
    response = client.post("/upload-report", json=payload)

    assert response.status_code == 200
    assert response.get_json().get("Status") == "Success"

def test_get_report(client):
    qs = {"id": "1", "input_type": "month", "date": "2024-01-01", "return_type": "json"}

    
    response = client.get("/get-report", query_string=qs)
    assert response.status_code == 200
    body = response.get_json()
    assert body["status"] == "success"
    assert "report" in body
