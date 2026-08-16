import httpx
import pytest

from app.core.external_urls import EXTERNAL_URLS
from app.service.errors import (
    ExternalAuthenticationError,
    ExternalPermissionError,
    ExternalRateLimitError,
    ExternalResponseError,
    ExternalServiceError,
    ExternalTimeoutError,
)
from app.integrations.google.routes.client import GoogleRoutesClient
from app.service.routes.service import GoogleRoutesService
from app.integrations.google.routes.mapper import basic_route_from_google_response
from app.contracts.route import (
    BasicRouteRequest,
    Coordinates,
    Destination,
)
from app.integrations.google.routes.request import build_compute_routes_body


def _routes_service(http_client: httpx.AsyncClient) -> GoogleRoutesService:
    return GoogleRoutesService(
        client=GoogleRoutesClient(api_key="test-api-key", client=http_client),
    )


def _route_request() -> BasicRouteRequest:
    return BasicRouteRequest(
        origin=Coordinates(lat=47.6062, lng=-122.3321),
        destination=Destination(placeId="ChIJ123"),
    )


def test_destination_accepts_place_id_and_placeId():
    assert Destination(place_id="ChIJ123").place_id == "ChIJ123"
    assert Destination(placeId="ChIJ123").place_id == "ChIJ123"
    assert Destination.model_validate({"place_id": "ChIJ123"}).place_id == "ChIJ123"
    assert Destination.model_validate({"placeId": "ChIJ123"}).place_id == "ChIJ123"


def test_compute_routes_body_sends_the_place_id():
    body = build_compute_routes_body(_route_request())

    assert body["destination"] == {"placeId": "ChIJ123"}
    assert "address" not in body["destination"]


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
        destination=Destination(placeId="ChIJ123"),
    )

    async with httpx.AsyncClient(transport=transport) as client:
        route = await _routes_service(client).compute_basic_route(request)

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
        destination=Destination(placeId="ChIJ123"),
    )

    async with httpx.AsyncClient(transport=transport) as client:
        with pytest.raises(ExternalPermissionError) as error:
            await _routes_service(client).compute_basic_route(request)

    assert error.value.context["upstream_status"] == 403
    assert error.value.code == "GOOGLE_ROUTES_FORBIDDEN"
    assert "permission" in error.value.message.lower()


def test_google_routes_mapper_rejects_malformed_upstream_response():
    with pytest.raises(ExternalResponseError) as error:
        basic_route_from_google_response({"routes": [{"duration": "900s"}]})

    assert error.value.code == "GOOGLE_ROUTES_INVALID_RESPONSE"
    assert "invalid response" in error.value.message.lower()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("upstream_status", "expected_type", "expected_code"),
    [
        (400, ExternalResponseError, "GOOGLE_ROUTES_BAD_REQUEST"),
        (401, ExternalAuthenticationError, "GOOGLE_ROUTES_UNAUTHORIZED"),
        (429, ExternalRateLimitError, "GOOGLE_ROUTES_RATE_LIMITED"),
        (500, ExternalServiceError, "GOOGLE_ROUTES_UPSTREAM_ERROR"),
    ],
)
async def test_compute_basic_route_maps_upstream_status_to_error(
    upstream_status, expected_type, expected_code
):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(upstream_status, json={"error": {"status": "FAILED"}})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(expected_type) as error:
            await _routes_service(client).compute_basic_route(_route_request())

    assert error.value.code == expected_code
    assert error.value.context["upstream_status"] == upstream_status


@pytest.mark.asyncio
async def test_compute_basic_route_raises_timeout_error_for_network_timeout():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timeout", request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(ExternalTimeoutError) as error:
            await _routes_service(client).compute_basic_route(_route_request())

    assert error.value.code == "GOOGLE_ROUTES_TIMEOUT"
    assert error.value.context["upstream_status"] is None


@pytest.mark.asyncio
async def test_compute_basic_route_raises_request_failed_error_for_transport_error():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(ExternalServiceError) as error:
            await _routes_service(client).compute_basic_route(_route_request())

    assert error.value.code == "GOOGLE_ROUTES_REQUEST_FAILED"


@pytest.mark.parametrize(
    ("duration", "expected_minutes"),
    [("900s", 15), ("900.000s", 15), ("1234.500s", 21), ("0s", 0)],
)
def test_google_routes_mapper_accepts_fractional_durations(duration, expected_minutes):
    route = basic_route_from_google_response(
        {"routes": [{"duration": duration, "distanceMeters": 3218}]}
    )

    assert route.duration_minutes == expected_minutes


def test_google_routes_mapper_rejects_unreadable_duration():
    with pytest.raises(ExternalResponseError) as error:
        basic_route_from_google_response(
            {"routes": [{"duration": "fifteen minutes", "distanceMeters": 3218}]}
        )

    assert error.value.code == "GOOGLE_ROUTES_INVALID_RESPONSE"
