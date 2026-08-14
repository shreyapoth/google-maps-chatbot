import pytest
from pydantic import ValidationError

from app.contracts.coordinates import Coordinates
from app.contracts.place import (
    PlaceNearbySearchRequest,
    PlaceTextSearchRequest,
)


def test_place_text_search_request_normalizes_query_edges():
    request = PlaceTextSearchRequest(text_query="  coffee shops in Austin  ")

    assert request.text_query == "coffee shops in Austin"


def test_place_text_search_request_rejects_empty_query():
    with pytest.raises(ValidationError):
        PlaceTextSearchRequest(text_query="   ")


def test_place_nearby_search_request_defaults():
    request = PlaceNearbySearchRequest(
        included_types=["restaurant"],
        location=Coordinates(latitude=37.33, longitude=-121.89),
    )

    assert request.included_types == ["restaurant"]
    assert request.radius == 5000.0
    assert request.max_results == 10


def test_place_nearby_search_request_rejects_empty_included_types():
    with pytest.raises(ValidationError):
        PlaceNearbySearchRequest(
            included_types=[],
            location=Coordinates(latitude=37.33, longitude=-121.89),
        )


def test_place_nearby_search_request_rejects_max_results_below_one():
    with pytest.raises(ValidationError):
        PlaceNearbySearchRequest(
            included_types=["cafe"],
            location=Coordinates(latitude=37.33, longitude=-121.89),
            max_results=0,
        )


def test_place_nearby_search_request_rejects_max_results_above_twenty():
    with pytest.raises(ValidationError):
        PlaceNearbySearchRequest(
            included_types=["cafe"],
            location=Coordinates(latitude=37.33, longitude=-121.89),
            max_results=21,
        )


def test_place_nearby_search_request_rejects_invalid_radius():
    with pytest.raises(ValidationError):
        PlaceNearbySearchRequest(
            included_types=["cafe"],
            location=Coordinates(latitude=37.33, longitude=-121.89),
            radius=0,
        )
