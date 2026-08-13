from __future__ import annotations

from pydantic import ValidationError

from app.service.errors import ExternalResponseError
from app.integrations.google.places.models import (
    GooglePlace,
    GooglePlacesNearbySearchResponse,
)
from app.contracts.coordinates import Coordinates
from app.contracts.place import (
    PlaceResult,
    PlaceResponse,
)


def map_place_response_from_google_response(
    response_body: dict,
    upstream_status: int | None = None,
) -> PlaceResponse:
    try:
        google_response = GooglePlacesNearbySearchResponse.model_validate(response_body)
    except (ValueError, ValidationError) as error:
        raise ExternalResponseError(
            code="GOOGLE_PLACES_INVALID_RESPONSE",
            message="Google Places returned an invalid response.",
            context={"upstream_status": upstream_status},
        ) from error

    return PlaceResponse(
        places=[_place_result_from_google_place(place) for place in google_response.places]
    )


def _place_result_from_google_place(place: GooglePlace) -> PlaceResult:
    return PlaceResult(
        place_id=place.id,
        name=place.display_name.text,
        formatted_address=place.formatted_address,
        location=(
            Coordinates(
                latitude=place.location.latitude,
                longitude=place.location.longitude,
            )
            if place.location
            else None
        ),
        primary_type=place.primary_type,
        types=place.types
    )
