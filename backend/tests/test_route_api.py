from fastapi.testclient import TestClient
from app.api.routes import google_routes
from app.core.http_client import get_http_client
from app.service.errors import ExternalPermissionError
from app.main import app
from app.contracts.route import BasicRouteResponse


async def fake_compute_basic_route(request, client, api_key):
    return BasicRouteResponse(duration_minutes=12, distance_miles=3.4, polyline=None)


def test_basic_route_endpoint(monkeypatch):
    monkeypatch.setattr(google_routes, "compute_basic_route", fake_compute_basic_route)
    app.dependency_overrides[get_http_client] = lambda: object()
    client = TestClient(app)

    try:
        response = client.post(
            "/api/routes/directions",
            json={
                "origin": {"lat": 47.6062, "lng": -122.3321},
                "destination": "Pike Place Market",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "duration_minutes": 12,
        "distance_miles": 3.4,
        "polyline": None,
    }


async def fake_compute_basic_route_forbidden(request, client, api_key):
    raise ExternalPermissionError(
        code="GOOGLE_ROUTES_FORBIDDEN",
        message="Google Routes permission denied. Check API enablement, billing, or key restrictions.",
        context={
            "upstream_status": 403,
            "google_status": "PERMISSION_DENIED",
            "google_message": "Requests to this API are blocked.",
        },
    )


def test_basic_route_endpoint_returns_structured_google_error(monkeypatch):
    monkeypatch.setattr(
        google_routes,
        "compute_basic_route",
        fake_compute_basic_route_forbidden,
    )
    app.dependency_overrides[get_http_client] = lambda: object()
    client = TestClient(app)

    try:
        response = client.post(
            "/api/routes/directions",
            json={
                "origin": {"lat": 47.6062, "lng": -122.3321},
                "destination": "Pike Place Market",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 502
    assert response.json()["detail"] == {
        "code": "GOOGLE_ROUTES_FORBIDDEN",
        "message": "Google Routes permission denied. Check API enablement, billing, or key restrictions.",
        "upstream_status": 403,
        "google_status": "PERMISSION_DENIED",
        "google_message": "Requests to this API are blocked.",
    }


def test_request_id_header_is_returned():
    client = TestClient(app)

    response = client.get("/health", headers={"X-Request-ID": "test-request-id"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "test-request-id"


def test_basic_route_endpoint_returns_structured_validation_error():
    with TestClient(app) as client:
        response = client.post(
            "/api/routes/directions",
            json={
                "origin": {"lat": "not-a-number", "lng": -122.3321},
                "destination": "",
            },
        )

    assert response.status_code == 422
    body = response.json()["detail"]
    assert body["code"] == "VALIDATION_ERROR"
    assert body["message"] == "Request validation failed."
    assert body["errors"]


def test_health_route():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_cors_allows_vite_frontend_origin():
    client = TestClient(app)

    response = client.options(
        "/api/routes/directions",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_lifespan_creates_shared_clients():
    with TestClient(app):
        assert hasattr(app.state, "http_client")
        assert hasattr(app.state, "nvidia_client")

