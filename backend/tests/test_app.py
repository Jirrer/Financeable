import io
import pytest


def test_register_login_logout(client):
    register = client.post(
        "/register",
        json={"username": "newuser", "password": "secret123", "email": "new@example.com"},
    )
    assert register.status_code == 201
    assert register.get_json()["user"]["username"] == "newuser"

    me_after_register = client.get("/me")
    assert me_after_register.status_code == 200
    assert me_after_register.get_json()["user"]["username"] == "newuser"

    logout = client.post("/logout")
    assert logout.status_code == 200

    login = client.post("/login", json={"username": "newuser", "password": "secret123"})
    assert login.status_code == 200
    assert login.get_json()["user"]["username"] == "newuser"


def test_login_rejects_bad_password(client):
    response = client.post("/login", json={"username": "testuser", "password": "wrong"})
    assert response.status_code == 401

def test_create_report(client, mock_csv_file, mock_get_transactions):
    for index in range(100):
        file = mock_csv_file()
        file.stream.seek(0)
        data = {
            "returnType": "JSON",
            "internal_transfers": ""
        }
        data["report"] = (file.stream, file.filename)

        response = client.post("/create-report", data=data, content_type="multipart/form-data")

        if index < 1:
            assert response.status_code == 200
            body = response.get_json()
            assert body["Status"] == "Success"
            assert body["transactions"] == mock_get_transactions(None, None, None)
            
        else:
            assert response.status_code == 429

def test_upload_report(client, mock_valid_user):
    for index in range(100):
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

        if index < 10:
            assert response.status_code == 200
            assert response.get_json().get("Status") == "Success"

        else:
            assert response.status_code == 429

def test_get_report(client):
    for index in range(100):
        qs = {"id": "1", "input_type": "month", "date": "2024-01-01", "return_type": "json"}

        response = client.get("/get-report", query_string=qs)
    
        if index < 60:    
            assert response.status_code == 200
            body = response.get_json()
            assert body["status"] == "success"
            assert "report" in body

        else:
            assert response.status_code == 429