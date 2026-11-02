"""API tests with the executor stubbed out: no Docker needed."""
import pytest
from fastapi.testclient import TestClient

from codecrate import executor as runner
from codecrate import main
from codecrate.config import settings


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(runner, "check_docker_availability", lambda: True)
    monkeypatch.setattr(
        runner,
        "run_code",
        lambda language, code: {"output": "ok\n", "exitCode": 0, "executionTime": 0.2},
    )
    monkeypatch.setattr(runner.executor, "prepull", lambda: None)  # never pull real images
    with TestClient(main.app) as c:
        yield c


def test_health(client):
    for path in ("/health", "/api/v1/health"):
        body = client.get(path).json()
        assert body["status"] == "healthy"
        assert set(body["supported_languages"]) == set(runner.LANGUAGES)


def test_languages(client):
    ids = [lang["id"] for lang in client.get("/api/v1/languages").json()["languages"]]
    assert ids == list(runner.LANGUAGES)


def test_execute_and_metrics(client):
    before = client.get("/api/v1/metrics").json()["total_executions"]
    r = client.post("/api/v1/execute", json={"language": "python", "code": "print('ok')"})
    assert r.status_code == 200
    assert r.json()["output"] == "ok\n"
    after = client.get("/api/v1/metrics").json()
    assert after["total_executions"] == before + 1
    assert after["language_usage"]["python"] >= 1


def test_unsupported_language_is_400(client):
    r = client.post("/api/v1/execute", json={"language": "cobol", "code": "x"})
    assert r.status_code == 400


def test_oversized_code_is_413(client):
    code = "x" * (settings.max_code_bytes + 1)
    r = client.post("/api/v1/execute", json={"language": "python", "code": code})
    assert r.status_code == 413


def test_docker_down_is_503(client, monkeypatch):
    monkeypatch.setattr(runner, "check_docker_availability", lambda: False)
    r = client.post("/api/v1/execute", json={"language": "python", "code": "print(1)"})
    assert r.status_code == 503
