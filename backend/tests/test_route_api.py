from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.bootstrap import get_google_routes_service
from app.contracts.route import BasicRouteResponse
from app.integrations.google.places.client import GooglePlaceClient
from app.integrations.google.routes.client import GoogleRoutesClient
from app.main import app
from app.service.errors import ExternalPermissionError
from app.service.routes.service import GoogleRoutesService

DIRECTIONS_REQUEST = {
    "origin": {"lat": 47.6062, "lng": -122.3321},
    "destination": "Pike Place Market",
}


def _fake_routes_service() -> AsyncMock:
    service = AsyncMock(spec=GoogleRoutesService)
    app.dependency_overrides[get_google_routes_service] = lambda: service
    return service


def test_basic_route_endpoint():
    service = _fake_routes_service()
    service.compute_basic_route.return_value = BasicRouteResponse(
        duration_minutes=12,
        distance_miles=3.4,
        polyline=None,
    )

    try:
        response = TestClient(app).post("/routes/directions", json=DIRECTIONS_REQUEST)
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "duration_minutes": 12,
        "distance_miles": 3.4,
        "polyline": None,
    }

    service.compute_basic_route.assert_awaited_once()
    route_request = service.compute_basic_route.await_args.args[0]
    assert route_request.origin.latitude == 47.6062
    assert route_request.origin.longitude == -122.3321
    assert route_request.destination == "Pike Place Market"


def test_basic_route_endpoint_returns_structured_google_error():
    service = _fake_routes_service()
    service.compute_basic_route.side_effect = ExternalPermissionError(
        code="GOOGLE_ROUTES_FORBIDDEN",
        message="Google Routes permission denied. Check API enablement, billing, or key restrictions.",
        context={
            "upstream_status": 403,
            "google_status": "PERMISSION_DENIED",
            "google_message": "Requests to this API are blocked.",
        },
    )

    try:
        response = TestClient(app).post("/routes/directions", json=DIRECTIONS_REQUEST)
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
            "/routes/directions",
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
        "/routes/directions",
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
        assert isinstance(app.state.google_places_client, GooglePlaceClient)
        assert isinstance(app.state.google_routes_client, GoogleRoutesClient)
