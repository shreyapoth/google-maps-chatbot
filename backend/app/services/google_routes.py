from __future__ import annotations
import logging
import httpx
from app.clients.google_routes_client import post_compute_routes
from app.core.config import settings
from app.schemas.route import BasicRouteRequest, BasicRouteResponse
from app.services.google_routes_errors import google_routes_error_from_response, google_routes_request_failed_error, google_routes_timeout_error
from app.services.google_routes_mapper import basic_route_from_google_response
from app.services.route_payloads import build_compute_routes_payload, build_google_routes_headers

logger = logging.getLogger(__name__)


async def compute_basic_route(
    route_request: BasicRouteRequest,
    client: httpx.AsyncClient | None = None,
) -> BasicRouteResponse:
    payload = build_compute_routes_payload(route_request)
    headers = build_google_routes_headers(settings.google_maps_server_key)

    if client is None:
        async with httpx.AsyncClient(timeout=10) as owned_client:
            return await _send_request(owned_client, payload, headers)

    return await _send_request(client, payload, headers)


async def _send_request(
    client: httpx.AsyncClient,
    payload: dict,
    headers: dict[str, str],
) -> BasicRouteResponse:
    try:
        response = await post_compute_routes(client, payload, headers)
        
    except httpx.HTTPStatusError as error:
        routes_error = google_routes_error_from_response(error.response)
        logger.error(
            "google_routes.http_error upstream_status=%s code=%s google_status=%s google_message=%r",
            routes_error.detail["upstream_status"],
            routes_error.detail["code"],
            routes_error.detail["google_status"],
            routes_error.detail["google_message"],
        )
        raise routes_error from error
    except httpx.TimeoutException as error:
        logger.exception("google_routes.timeout")
        raise google_routes_timeout_error() from error
    except httpx.HTTPError as error:
        logger.exception("google_routes.request_failed")
        raise google_routes_request_failed_error() from error

    return basic_route_from_google_response(response.json())
