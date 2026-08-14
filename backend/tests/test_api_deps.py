import httpx
import pytest

from app.api.places.deps import (
    get_google_place_client,
    get_google_place_service,
)
from app.api.routes.deps import (
    get_google_routes_client,
    get_google_routes_service,
)
from app.contracts.coordinates import Coordinates
from app.contracts.place import PlaceNearbySearchRequest
from app.contracts.route import BasicRouteRequest
from app.core.config import settings
from app.integrations.google.places.client import GooglePlaceClient
from app.integrations.google.routes.client import GoogleRoutesClient
from app.service.places.service import GooglePlaceService
from app.service.routes.service import GoogleRoutesService


def _capture_api_key(captured: dict, json_body: dict):
    def handler(request: httpx.Request) -> httpx.Response:
        captured["api_key"] = request.headers.get("X-Goog-Api-Key")
        return httpx.Response(200, json=json_body)

    return handler


@pytest.mark.asyncio
async def test_place_provider_chain_sends_configured_api_key():
    captured = {}
    handler = _capture_api_key(captured, {"places": []})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        place_client = get_google_place_client(http_client)
        place_service = get_google_place_service(place_client)

        assert isinstance(place_client, GooglePlaceClient)
        assert isinstance(place_service, GooglePlaceService)

        await place_service.search_nearby_places(
            PlaceNearbySearchRequest(
                included_types=["restaurant"],
                location=Coordinates(latitude=37.33, longitude=-121.89),
            )
        )

    assert captured["api_key"] == settings.google_maps_server_key_value


@pytest.mark.asyncio
async def test_routes_provider_chain_sends_configured_api_key():
    captured = {}
    handler = _capture_api_key(
        captured,
        {"routes": [{"duration": "900s", "distanceMeters": 3218}]},
    )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        routes_client = get_google_routes_client(http_client)
        routes_service = get_google_routes_service(routes_client)

        assert isinstance(routes_client, GoogleRoutesClient)
        assert isinstance(routes_service, GoogleRoutesService)

        await routes_service.compute_basic_route(
            BasicRouteRequest(
                origin=Coordinates(latitude=47.6062, longitude=-122.3321),
                destination="Pike Place Market",
            )
        )

    assert captured["api_key"] == settings.google_maps_server_key_value
