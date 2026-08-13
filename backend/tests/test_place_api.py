from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.api.places.deps import get_google_place_service
from app.contracts.coordinates import Coordinates
from app.contracts.place import (
    PlaceNearbySearchRequest,
    PlaceResponse,
    PlaceResult,
)
from app.main import app


class _FakePlaceService:
    def __init__(self) -> None:
        self.search_nearby_places = AsyncMock(side_effect=self._search_nearby)

    async def _search_nearby(self, request: PlaceNearbySearchRequest) -> PlaceResponse:
        assert request.included_types == ["restaurant"]
        assert request.location.latitude == 37.33
        assert request.location.longitude == -121.89
        assert request.radius == 5000.0
        assert request.max_results == 10
        return PlaceResponse(
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


def test_places_nearby_endpoint_returns_normalized_places():
    fake_service = _FakePlaceService()
    app.dependency_overrides[get_google_place_service] = lambda: fake_service
    client = TestClient(app)
    try:
        response = client.post(
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
    fake_service.search_nearby_places.assert_awaited_once()


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
