import io
import pytest

def test_register_login_logout(client):
    register = client.post(
        "/register",
        json={"username": "newuser", "password": "secret123", "email": "new@example.com"},
    )
    assert register.status_code == 201
    assert register.get_json()["user"]["username"] == "newuser"

    me_after_register = client.get("/validUser")
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
    client.post(
        "/register",
        json={"username": "newuser", "password": "secret123", "email": "new@example.com"},
    )

    client.post("/login", json={"username": "newuser", "password": "secret123"})

    file = mock_csv_file()
    file.stream.seek(0)
    data = {
        "returnType": "JSON",
        "internal_transfers": ""
    }
    data["report"] = (file.stream, file.filename)

    response = client.post("/create-report", data=data, content_type="multipart/form-data")

    
    assert response.status_code == 200
    body = response.get_json()
    assert body["Status"] == "Success"
    assert body["transactions"] == mock_get_transactions(None, None, None)  

def test_upload_report(client, mock_valid_user):
    client.post(
        "/register",
        json={"username": "newuser", "password": "secret123", "email": "new@example.com"},
    )

    client.post("/login", json={"username": "newuser", "password": "secret123"})

    payload = {
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
    client.post(
        "/register",
        json={"username": "newuser", "password": "secret123", "email": "new@example.com"},
    )

    client.post("/login", json={"username": "newuser", "password": "secret123"})

    oneMonthYear = {
        "date_start": "2026-04",
        "date_end": "2026-04",
        "return_type": "JSON"
    }

    missingMonth = {
        "date_end": "2026-04",
        "return_type": "JSON"
    }


    missingYear = {
        "date_start": "2026-04",
        "return_type": "JSON"
    }
    
    goodResponse = client.post("/get-report", json=oneMonthYear)   
    assert goodResponse.status_code == 200

    body = goodResponse.get_json()
    assert body["status"] == "success"
    assert "report" in body

    nullResponse = client.post("/get-report", json=missingMonth) 
    assert nullResponse.status_code == 400

    nullResponse = client.post("/get-report", json=missingYear) 
    assert nullResponse.status_code == 400