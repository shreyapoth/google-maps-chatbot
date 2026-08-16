import logging
from langchain_core.tools import (
    BaseTool,
    tool
)
from app.contracts.coordinates import Coordinates
from app.contracts.place import (
    PlaceNearbySearchRequest,
    PlaceTextSearchRequest
)
from app.contracts.route import BasicRouteRequest, Destination
from app.service.places.service import GooglePlaceService
from app.service.routes.service import GoogleRoutesService
from app.tools.place_types import PLACE_TYPES

logger = logging.getLogger(__name__)


def google_place_tools(place_service: GooglePlaceService) -> list[BaseTool]:
    async def search_text_near(text_query: str, location: Coordinates) -> str:
        response = await place_service.search_text_places(
            PlaceTextSearchRequest(text_query=text_query, location_bias=location)
        )

        return response.model_dump_json(exclude_none=True)

    @tool
    async def search_nearby_places(
        types: list[str],
        latitude: float,
        longitude: float,
    ) -> str:
        """Find places of a given category near the user's current location.
        Use when the user wants whatever is closest — 'restaurants near me',
        'find a gas station', 'coffee shops nearby'. Prefer a Google place
        category such as restaurant, cafe, gas_station or mexican_restaurant;
        anything else, such as a dish or a brand, is searched as text instead."""

        location = Coordinates(latitude=latitude, longitude=longitude)
        categories = [place_type for place_type in types if place_type in PLACE_TYPES]

        if not categories:
            logger.info("tools.nearby_search.unknown_category types=%s", types)
            return await search_text_near(" ".join(types), location)

        response = await place_service.search_nearby_places(
            PlaceNearbySearchRequest(
                included_types=categories,
                location=location,
            )
        )

        if not response.places:
            logger.info("tools.nearby_search.no_results categories=%s", categories)
            return await search_text_near(" ".join(types), location)

        return response.model_dump_json(exclude_none=True)

    @tool
    async def search_text_places(text_query: str, latitude: float, longitude: float) -> str:
        """Search for a specific place by name or description.
        Use when the user names a business, brand, or specific query —
        'chipotle', 'best ramen in Austin', 'Target on Broadway'. Results near
        the user's location are preferred, but a place named in the query wins."""

        return await search_text_near(
            text_query,
            Coordinates(latitude=latitude, longitude=longitude),
        )

    return [search_nearby_places, search_text_places]


def google_routes_tools(routes_service: GoogleRoutesService) -> list[BaseTool]:
    @tool
    async def compute_route(place_id: str, latitude: float, longitude: float) -> str:
        """Get driving time and distance from the user's current location to a destination.
        Use when the user asks how to get somewhere, how far it is, or how long it takes.
        The destination can be a place name or an address."""

        response = await routes_service.compute_basic_route(
            BasicRouteRequest(
                origin=Coordinates(latitude=latitude, longitude=longitude),
                destination=Destination(placeId=place_id),
            )
        )

        return response.model_dump_json(exclude_none=True)

    return [compute_route]
