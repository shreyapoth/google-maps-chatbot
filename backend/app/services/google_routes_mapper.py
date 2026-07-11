import logging

from app.schemas.route import BasicRouteResponse
from app.utils.distance import meters_to_miles
from app.utils.duration import google_duration_to_minutes

logger = logging.getLogger(__name__)


def basic_route_from_google_response(response_body: dict) -> BasicRouteResponse:
    route = response_body["routes"][0]
    logger.info(
        "google_routes.parsed duration=%s distance_meters=%s has_polyline=%s",
        route.get("duration"),
        route.get("distanceMeters"),
        bool(route.get("polyline", {}).get("encodedPolyline")),
    )
    return BasicRouteResponse(
        duration_minutes=google_duration_to_minutes(route["duration"]),
        distance_miles=meters_to_miles(route["distanceMeters"]),
        polyline=route.get("polyline", {}).get("encodedPolyline"),
    )
