import pytest
from app.main import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# 1️⃣ Test health
def test_health(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json["status"] == "OK"


# 2️⃣ Test liste serveurs
def test_get_servers(client):
    response = client.get("/api/v1/servers")
    assert response.status_code == 200
    assert "servers" in response.json
    assert response.json["count"] == 2


# 3️⃣ Test serveur ID 1
def test_get_server_by_id(client):
    response = client.get("/api/v1/servers/1")
    assert response.status_code == 200
    assert response.json["hostname"] == "web-prod-01"


# 4️⃣ Test serveur inexistant
def test_get_server_not_found(client):
    response = client.get("/api/v1/servers/999")
    assert response.status_code == 404
    assert response.json["error"] == "Server not found"
