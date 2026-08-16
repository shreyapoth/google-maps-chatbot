import json
from unittest.mock import AsyncMock

import pytest

from app.contracts.coordinates import Coordinates
from app.contracts.place import (
    PlaceResponse,
    PlaceResult,
)
from app.contracts.route import BasicRouteResponse
from app.service.places.service import GooglePlaceService
from app.service.routes.service import GoogleRoutesService
from app.tools.tools import (
    google_place_tools,
    google_routes_tools,
)


def _tools_by_name(tools) -> dict:
    return {tool.name: tool for tool in tools}


def _place_response() -> PlaceResponse:
    return PlaceResponse(
        places=[
            PlaceResult(
                place_id="ChIJ123",
                name="Torchy's Tacos",
                formatted_address="Austin, TX",
                location=Coordinates(latitude=30.27, longitude=-97.74),
                primary_type="mexican_restaurant",
                types=["mexican_restaurant", "restaurant"],
            )
        ]
    )


@pytest.mark.asyncio
async def test_nearby_tool_passes_the_coordinates_it_was_called_with():
    place_service = AsyncMock(spec=GooglePlaceService)
    place_service.search_nearby_places.return_value = _place_response()

    tools = _tools_by_name(google_place_tools(place_service))
    result = await tools["search_nearby_places"].ainvoke(
        {"types": ["restaurant"], "latitude": 30.27, "longitude": -97.74}
    )

    nearby_request = place_service.search_nearby_places.await_args.args[0]
    assert nearby_request.included_types == ["restaurant"]
    assert nearby_request.location.latitude == 30.27
    assert nearby_request.location.longitude == -97.74
    assert json.loads(result)["places"][0]["name"] == "Torchy's Tacos"


@pytest.mark.asyncio
async def test_text_search_tool_forwards_the_query_biased_to_the_user():
    place_service = AsyncMock(spec=GooglePlaceService)
    place_service.search_text_places.return_value = _place_response()

    tools = _tools_by_name(google_place_tools(place_service))
    result = await tools["search_text_places"].ainvoke(
        {"text_query": "torchys tacos", "latitude": 30.27, "longitude": -97.74}
    )

    text_request = place_service.search_text_places.await_args.args[0]
    assert text_request.text_query == "torchys tacos"
    assert text_request.location_bias.latitude == 30.27
    assert text_request.location_bias.longitude == -97.74
    assert json.loads(result)["places"][0]["place_id"] == "ChIJ123"


@pytest.mark.asyncio
async def test_route_tool_builds_a_request_from_the_users_location():
    routes_service = AsyncMock(spec=GoogleRoutesService)
    routes_service.compute_basic_route.return_value = BasicRouteResponse(
        duration_minutes=4,
        distance_miles=1.2,
        polyline=None,
    )

    tools = _tools_by_name(google_routes_tools(routes_service))
    result = await tools["compute_route"].ainvoke(
        {"destination": "Torchy's Tacos", "latitude": 30.27, "longitude": -97.74}
    )

    route_request = routes_service.compute_basic_route.await_args.args[0]
    assert route_request.origin.latitude == 30.27
    assert route_request.destination == "Torchy's Tacos"
    assert json.loads(result)["duration_minutes"] == 4


@pytest.mark.asyncio
async def test_nearby_tool_searches_text_for_something_that_is_not_a_category():
    place_service = AsyncMock(spec=GooglePlaceService)
    place_service.search_text_places.return_value = _place_response()

    tools = _tools_by_name(google_place_tools(place_service))
    result = await tools["search_nearby_places"].ainvoke(
        {"types": ["taco"], "latitude": 30.27, "longitude": -97.74}
    )

    place_service.search_nearby_places.assert_not_awaited()
    text_request = place_service.search_text_places.await_args.args[0]
    assert text_request.text_query == "taco"
    assert text_request.location_bias.latitude == 30.27
    assert json.loads(result)["places"][0]["name"] == "Torchy's Tacos"


@pytest.mark.asyncio
async def test_nearby_tool_keeps_the_categories_google_understands():
    place_service = AsyncMock(spec=GooglePlaceService)
    place_service.search_nearby_places.return_value = _place_response()

    tools = _tools_by_name(google_place_tools(place_service))
    await tools["search_nearby_places"].ainvoke(
        {"types": ["taco", "mexican_restaurant"], "latitude": 30.27, "longitude": -97.74}
    )

    nearby_request = place_service.search_nearby_places.await_args.args[0]
    assert nearby_request.included_types == ["mexican_restaurant"]
    place_service.search_text_places.assert_not_awaited()


@pytest.mark.asyncio
async def test_nearby_tool_searches_text_when_nothing_is_nearby():
    place_service = AsyncMock(spec=GooglePlaceService)
    place_service.search_nearby_places.return_value = PlaceResponse(places=[])
    place_service.search_text_places.return_value = _place_response()

    tools = _tools_by_name(google_place_tools(place_service))
    result = await tools["search_nearby_places"].ainvoke(
        {"types": ["sushi_restaurant"], "latitude": 30.27, "longitude": -97.74}
    )

    place_service.search_nearby_places.assert_awaited_once()
    assert place_service.search_text_places.await_args.args[0].text_query == "sushi_restaurant"
    assert json.loads(result)["places"][0]["name"] == "Torchy's Tacos"


def test_every_tool_exposes_a_description_for_the_model():
    tools = [
        *google_place_tools(AsyncMock(spec=GooglePlaceService)),
        *google_routes_tools(AsyncMock(spec=GoogleRoutesService)),
    ]

    assert [tool.name for tool in tools] == [
        "search_nearby_places",
        "search_text_places",
        "compute_route",
    ]
    assert all(tool.description for tool in tools)
