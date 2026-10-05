import pytest
from starlette.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_api_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["classes_count"] == 8
    assert data["model_loaded"] is True


def test_api_classes():
    response = client.get("/api/v1/classes")
    assert response.status_code == 200
    data = response.json()
    assert "classes" in data
    assert len(data["classes"]) == 8
    assert "Temple Border" in data["classes"]


def test_api_presets():
    response = client.get("/api/v1/presets")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 8
    assert any("Temple" in p["design"] for p in data)


def test_api_recolor():
    response = client.post("/api/v1/recolor", data={
        "preset_filename": "Temple_Border__Crimson_Red.jpg",
        "target_hex": "#1864AB"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["predicted_design"] == "Temple Border"
    assert "recolored_image" in data
    assert "visual_stages" in data
