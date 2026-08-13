import logging

from pydantic import ValidationError

from app.service.errors import ExternalResponseError
from app.integrations.google.routes.models import GoogleRoutesResponse
from app.contracts.route import BasicRouteResponse
from app.utils.distance import meters_to_miles
from app.utils.duration import google_duration_to_minutes

logger = logging.getLogger(__name__)


def basic_route_from_google_response(response_body: dict) -> BasicRouteResponse:
    try:
        google_response = GoogleRoutesResponse.model_validate(response_body)
        route = google_response.routes[0]
    except (IndexError, ValidationError) as error:
        raise ExternalResponseError(
            code="GOOGLE_ROUTES_INVALID_RESPONSE",
            message="Google Routes returned an invalid response.",
            context={"upstream_status": None},
        ) from error

    logger.info(
        "google_routes.parsed duration=%s distance_meters=%s has_polyline=%s",
        route.duration,
        route.distance_meters,
        bool(route.polyline and route.polyline.encoded_polyline),
    )
    return BasicRouteResponse(
        duration_minutes=google_duration_to_minutes(route.duration),
        distance_miles=meters_to_miles(route.distance_meters),
        polyline=route.polyline.encoded_polyline if route.polyline else None,
    )
