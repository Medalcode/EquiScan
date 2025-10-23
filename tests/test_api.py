import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert r.json()["project"] == "EquiScan"


def test_scan_empty_url():
    r = client.post("/api/scan", json={"url": ""})
    body = r.json()
    assert r.status_code == 200
    assert isinstance(body["issues"], list)
    assert "score" in body


def test_scan_invalid_url():
    r = client.post("/api/scan", json={"url": "http://this-domain-does-not-exist-12345.com"})
    body = r.json()
    assert r.status_code == 200
    assert isinstance(body["issues"], list)


def test_scan_history_empty():
    r = client.get("/api/history")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_scan_detail_not_found():
    r = client.get("/api/scan/9999")
    assert r.status_code == 404


def test_scan_result_structure():
    r = client.post("/api/scan", json={"url": ""})
    assert r.status_code == 200
    body = r.json()
    assert "id" in body
    assert "url" in body
    assert "score" in body
    assert "violations" in body
    assert "issues" in body
    assert "created_at" in body
    assert isinstance(body["issues"], list)
