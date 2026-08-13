import json
import httpx
import pytest
from app.core.external_urls import EXTERNAL_URLS
from app.service.errors import (
    ExternalRateLimitError,
    ExternalResponseError,
    ExternalServiceError,
    ExternalTimeoutError,
)
from app.service.places.service import search_nearby_places
from app.integrations.google.places.mapper import map_place_response_from_google_response
from app.integrations.google.places.request import GOOGLE_PLACES_NEARBY_SEARCH_FIELD_MASK
from app.contracts.coordinates import Coordinates
from app.contracts.place import PlaceNearbySearchRequest


def _nearby_request() -> PlaceNearbySearchRequest:
    return PlaceNearbySearchRequest(
        included_types=["restaurant"],
        location=Coordinates(latitude=37.33, longitude=-121.89),
        radius=5000.0,
        max_results=10,
    )


@pytest.mark.asyncio
async def test_search_nearby_places_sends_expected_request():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["headers"] = request.headers
        captured["json"] = json.loads(request.content.decode())
        return httpx.Response(
            200,
            json={
                "places": [
                    {
                        "id": "ChIJ123",
                        "displayName": {"text": "Example Indian Restaurant"},
                        "formattedAddress": "San Jose, CA",
                        "location": {"latitude": 37.33, "longitude": -121.89},
                        "primaryType": "indian_restaurant",
                        "types": ["indian_restaurant", "restaurant"],
                        "rating": 4.5,
                        "userRatingCount": 420,
                        "priceLevel": "PRICE_LEVEL_INEXPENSIVE",
                        "googleMapsUri": "https://maps.google.com/example",
                    }
                ]
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        response = await search_nearby_places(_nearby_request(), http_client, api_key="test-api-key")

    assert captured["url"] == EXTERNAL_URLS["google_places_nearby_search"]
    assert captured["headers"]["X-Goog-Api-Key"]
    assert captured["headers"]["Content-Type"] == "application/json"
    assert captured["headers"]["X-Goog-FieldMask"] == GOOGLE_PLACES_NEARBY_SEARCH_FIELD_MASK
    assert captured["json"] == {
        "includedTypes": ["restaurant"],
        "maxResultCount": 10,
        "locationRestriction": {
            "circle": {
                "center": {"latitude": 37.33, "longitude": -121.89},
                "radius": 5000.0,
            }
        },
    }
    assert response.model_dump() == {
        "places": [
            {
                "place_id": "ChIJ123",
                "name": "Example Indian Restaurant",
                "formatted_address": "San Jose, CA",
                "location": {"latitude": 37.33, "longitude": -121.89},
                "primary_type": "indian_restaurant",
                "types": ["indian_restaurant", "restaurant"],
            }
        ]
    }


@pytest.mark.asyncio
async def test_search_nearby_places_handles_missing_optional_fields():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "places": [
                    {
                        "id": "ChIJ123",
                        "displayName": {"text": "Example Cafe"},
                        "types": [],
                    }
                ]
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        response = await search_nearby_places(_nearby_request(), http_client, api_key="test-api-key")

    place = response.places[0]
    assert place.place_id == "ChIJ123"
    assert place.name == "Example Cafe"
    assert place.formatted_address is None
    assert place.location is None
    assert place.primary_type is None
    assert place.types == []


@pytest.mark.asyncio
async def test_search_nearby_places_raises_rate_limit_error_for_429():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={"error": {"status": "RESOURCE_EXHAUSTED"}})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        with pytest.raises(ExternalRateLimitError) as error:
            await search_nearby_places(_nearby_request(), http_client, api_key="test-api-key")

    assert error.value.code == "GOOGLE_PLACES_RATE_LIMITED"
    assert error.value.context["upstream_status"] == 429


@pytest.mark.asyncio
async def test_search_nearby_places_raises_service_error_for_500():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"error": {"status": "INTERNAL"}})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        with pytest.raises(ExternalServiceError) as error:
            await search_nearby_places(_nearby_request(), http_client, api_key="test-api-key")

    assert error.value.code == "GOOGLE_PLACES_UPSTREAM_ERROR"
    assert error.value.context["upstream_status"] == 500


@pytest.mark.asyncio
async def test_search_nearby_places_raises_timeout_error_for_network_timeout():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timeout", request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        with pytest.raises(ExternalTimeoutError) as error:
            await search_nearby_places(_nearby_request(), http_client, api_key="test-api-key")

    assert error.value.code == "GOOGLE_PLACES_TIMEOUT"
    assert error.value.context["upstream_status"] is None


@pytest.mark.asyncio
async def test_search_nearby_places_rejects_invalid_google_response():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"places": [{"displayName": {"text": "No ID"}}]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        with pytest.raises(ExternalResponseError) as error:
            await search_nearby_places(_nearby_request(), http_client, api_key="test-api-key")

    assert error.value.code == "GOOGLE_PLACES_INVALID_RESPONSE"


@pytest.mark.asyncio
async def test_search_nearby_places_rejects_invalid_json_body():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"not-json", headers={"Content-Type": "application/json"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        with pytest.raises(ExternalResponseError) as error:
            await search_nearby_places(_nearby_request(), http_client, api_key="test-api-key")

    assert error.value.code == "GOOGLE_PLACES_INVALID_RESPONSE"
    assert error.value.context["upstream_status"] == 200


def test_places_mapper_rejects_malformed_upstream_response():
    with pytest.raises(ExternalResponseError) as error:
        map_place_response_from_google_response({"places": [{"displayName": {"text": "No ID"}}]})

    assert error.value.code == "GOOGLE_PLACES_INVALID_RESPONSE"
