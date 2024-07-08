def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.content == b"{}"


def test_health_ready(client):
    response = client.get("/health?ready=true")
    assert response.status_code == 200
    assert response.json() == {}


def test_metrics(client):
    response = client.get("/metrics/")
    assert response.status_code == 200
    metrics = response.text.splitlines()
    assert "# TYPE auth_service_authorize_created gauge" in metrics
    assert "# TYPE auth_service_login_created gauge" in metrics
    assert "# TYPE auth_service_logout_created gauge" in metrics
    assert "# TYPE auth_service_user_created gauge" in metrics
