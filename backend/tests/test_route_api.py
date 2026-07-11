from fastapi.testclient import TestClient

from app.api.routes import route
from app.main import app
from app.schemas.route import BasicRouteResponse
from app.services.google_routes_errors import GoogleRoutesError


async def fake_compute_basic_route(request):
    return BasicRouteResponse(duration_minutes=12, distance_miles=3.4, polyline=None)


def test_basic_route_endpoint(monkeypatch):
    monkeypatch.setattr(route, "compute_basic_route", fake_compute_basic_route)
    client = TestClient(app)

    response = client.post(
        "/api/routes/basic",
        json={
            "origin": {"lat": 47.6062, "lng": -122.3321},
            "destination": "Pike Place Market",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "duration_minutes": 12,
        "distance_miles": 3.4,
        "polyline": None,
    }


async def fake_compute_basic_route_forbidden(request):
    raise GoogleRoutesError(
        status_code=502,
        detail={
            "code": "GOOGLE_ROUTES_FORBIDDEN",
            "message": "Google Routes permission denied. Check API enablement, billing, or key restrictions.",
            "upstream_status": 403,
        },
    )


def test_basic_route_endpoint_returns_structured_google_error(monkeypatch):
    monkeypatch.setattr(
        route,
        "compute_basic_route",
        fake_compute_basic_route_forbidden,
    )
    client = TestClient(app)

    response = client.post(
        "/api/routes/basic",
        json={
            "origin": {"lat": 47.6062, "lng": -122.3321},
            "destination": "Pike Place Market",
        },
    )

    assert response.status_code == 502
    assert response.json()["detail"] == {
        "code": "GOOGLE_ROUTES_FORBIDDEN",
        "message": "Google Routes permission denied. Check API enablement, billing, or key restrictions.",
        "upstream_status": 403,
    }


def test_health_route():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_cors_allows_vite_frontend_origin():
    client = TestClient(app)

    response = client.options(
        "/api/routes/basic",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
