from __future__ import annotations

import logging

import httpx

from app.contracts.place import (
    PlaceNearbySearchRequest,
    PlaceResponse,
    PlaceTextSearchRequest,
)
from app.integrations.google.places.client import (
    post_nearby_search,
    post_text_search,
)
from app.integrations.google.places.errors import (
    google_places_error_from_response,
    google_places_request_failed_error,
    google_places_timeout_error,
)
from app.integrations.google.places.mapper import map_place_response_from_google_response
from app.service.errors import ExternalResponseError

logger = logging.getLogger(__name__)


async def search_text_places(
    request: PlaceTextSearchRequest,
    client: httpx.AsyncClient,
    api_key: str,
) -> PlaceResponse:
    try:
        response = await post_text_search(client, request, api_key)
    except httpx.HTTPStatusError as error:
        places_error = google_places_error_from_response(error.response)
        logger.error(
            "google_places.http_error code=%s upstream_status=%s",
            places_error.code,
            places_error.context["upstream_status"],
        )
        raise places_error from error
    except httpx.TimeoutException as error:
        logger.exception("google_places.timeout")
        raise google_places_timeout_error() from error
    except httpx.HTTPError as error:
        logger.exception("google_places.request_failed")
        raise google_places_request_failed_error() from error

    return _parse_places_response(response)


async def search_nearby_places(
    request: PlaceNearbySearchRequest,
    client: httpx.AsyncClient,
    api_key: str,
) -> PlaceResponse:
    try:
        response = await post_nearby_search(client, request, api_key)
    except httpx.HTTPStatusError as error:
        places_error = google_places_error_from_response(error.response)
        logger.error(
            "google_places.http_error code=%s upstream_status=%s",
            places_error.code,
            places_error.context["upstream_status"],
        )
        raise places_error from error
    except httpx.TimeoutException as error:
        logger.exception("google_places.timeout")
        raise google_places_timeout_error() from error
    except httpx.HTTPError as error:
        logger.exception("google_places.request_failed")
        raise google_places_request_failed_error() from error

    return _parse_places_response(response)


def _parse_places_response(response: httpx.Response) -> PlaceResponse:
    try:
        response_body = response.json()
    except ValueError as error:
        logger.exception("google_places.invalid_json status=%s", response.status_code)
        raise ExternalResponseError(
            code="GOOGLE_PLACES_INVALID_RESPONSE",
            message="Google Places returned an invalid response.",
            context={"upstream_status": response.status_code},
        ) from error

    return map_place_response_from_google_response(
        response_body,
        upstream_status=response.status_code,
    )
