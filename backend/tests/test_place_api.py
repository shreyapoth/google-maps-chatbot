from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.api.places.deps import get_google_place_service
from app.contracts.coordinates import Coordinates
from app.contracts.place import (
    PlaceNearbySearchRequest,
    PlaceResponse,
    PlaceResult,
    PlaceTextSearchRequest,
)
from app.main import app
from app.service.places.service import GooglePlaceService


def _fake_place_service() -> AsyncMock:
    service = AsyncMock(spec=GooglePlaceService)
    app.dependency_overrides[get_google_place_service] = lambda: service
    return service


def test_places_nearby_endpoint_returns_normalized_places():
    service = _fake_place_service()
    service.search_nearby_places.return_value = PlaceResponse(
        places=[
            PlaceResult(
                place_id="ChIJ123",
                name="Example Indian Restaurant",
                formatted_address="San Jose, CA",
                location=Coordinates(latitude=37.33, longitude=-121.89),
                primary_type="indian_restaurant",
                types=["indian_restaurant", "restaurant"],
            )
        ]
    )

    try:
        response = TestClient(app).post(
            "/places/nearby",
            json={
                "included_types": ["restaurant"],
                "location": {"latitude": 37.33, "longitude": -121.89},
                "radius": 5000.0,
                "max_results": 10,
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "places": [
            {
                "place_id": "ChIJ123",
                "name": "Example Indian Restaurant",
                "formatted_address": "San Jose, CA",
                "location": {
                    "latitude": 37.33,
                    "longitude": -121.89,
                },
                "primary_type": "indian_restaurant",
                "types": ["indian_restaurant", "restaurant"],
            }
        ]
    }

    service.search_nearby_places.assert_awaited_once()
    nearby_request: PlaceNearbySearchRequest = service.search_nearby_places.await_args.args[0]
    assert nearby_request.included_types == ["restaurant"]
    assert nearby_request.location.latitude == 37.33
    assert nearby_request.location.longitude == -121.89
    assert nearby_request.radius == 5000.0
    assert nearby_request.max_results == 10


def test_places_text_search_endpoint_returns_normalized_places():
    service = _fake_place_service()
    service.search_text_places.return_value = PlaceResponse(
        places=[
            PlaceResult(
                place_id="ChIJ456",
                name="Example Coffee",
                formatted_address="Austin, TX",
                location=Coordinates(latitude=30.27, longitude=-97.74),
                primary_type="coffee_shop",
                types=["coffee_shop", "cafe"],
            )
        ]
    )

    try:
        response = TestClient(app).post(
            "/places/text-search",
            json={"text_query": "  coffee shops in Austin  "},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["places"][0]["name"] == "Example Coffee"

    service.search_text_places.assert_awaited_once()
    text_request: PlaceTextSearchRequest = service.search_text_places.await_args.args[0]
    assert text_request.text_query == "coffee shops in Austin"


def test_places_text_search_endpoint_rejects_blank_query():
    with TestClient(app) as client:
        response = client.post("/places/text-search", json={"text_query": "   "})

    assert response.status_code == 422


def test_places_nearby_endpoint_rejects_empty_included_types():
    with TestClient(app) as client:
        response = client.post(
            "/places/nearby",
            json={
                "included_types": [],
                "location": {"latitude": 37.33, "longitude": -121.89},
            },
        )

    assert response.status_code == 422


def test_places_nearby_endpoint_rejects_max_results_below_one():
    with TestClient(app) as client:
        response = client.post(
            "/places/nearby",
            json={
                "included_types": ["cafe"],
                "location": {"latitude": 37.33, "longitude": -121.89},
                "max_results": 0,
            },
        )

    assert response.status_code == 422


def test_places_nearby_endpoint_rejects_max_results_above_twenty():
    with TestClient(app) as client:
        response = client.post(
            "/places/nearby",
            json={
                "included_types": ["cafe"],
                "location": {"latitude": 37.33, "longitude": -121.89},
                "max_results": 21,
            },
        )

    assert response.status_code == 422
