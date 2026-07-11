import httpx
import pytest

from app.core.external_urls import EXTERNAL_URLS
from app.schemas.route import BasicRouteRequest, Coordinates
from app.services.google_routes import compute_basic_route
from app.services.google_routes_errors import GoogleRoutesError


@pytest.mark.asyncio
async def test_compute_basic_route_converts_google_response():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["headers"] = request.headers
        captured["json"] = request.read().decode()
        return httpx.Response(
            200,
            json={
                "routes": [
                    {
                        "duration": "900s",
                        "distanceMeters": 3218,
                        "polyline": {"encodedPolyline": "abc123"},
                    }
                ]
            },
        )

    transport = httpx.MockTransport(handler)
    request = BasicRouteRequest(
        origin=Coordinates(lat=47.6062, lng=-122.3321),
        destination="Space Needle, Seattle",
    )

    async with httpx.AsyncClient(transport=transport) as client:
        route = await compute_basic_route(request, client=client)

    assert route.duration_minutes == 15
    assert route.distance_miles == 2.0
    assert route.polyline == "abc123"
    assert captured["url"] == EXTERNAL_URLS["google_routes_compute"]
    assert captured["headers"]["X-Goog-FieldMask"] == (
        "routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline"
    )
    assert '"travelMode":"DRIVE"' in captured["json"]


@pytest.mark.asyncio
async def test_compute_basic_route_raises_helpful_error_for_forbidden_response():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            403,
            json={
                "error": {
                    "status": "PERMISSION_DENIED",
                    "message": "Requests to this API are blocked.",
                }
            },
        )

    transport = httpx.MockTransport(handler)
    request = BasicRouteRequest(
        origin=Coordinates(lat=47.6062, lng=-122.3321),
        destination="Space Needle, Seattle",
    )

    async with httpx.AsyncClient(transport=transport) as client:
        with pytest.raises(GoogleRoutesError) as error:
            await compute_basic_route(request, client=client)

    assert error.value.status_code == 502
    assert error.value.detail["upstream_status"] == 403
    assert error.value.detail["code"] == "GOOGLE_ROUTES_FORBIDDEN"
    assert "permission" in error.value.detail["message"].lower()
