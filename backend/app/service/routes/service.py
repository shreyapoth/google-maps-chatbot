from __future__ import annotations

import logging

import httpx

from app.contracts.route import (
    BasicRouteRequest,
    BasicRouteResponse,
)
from app.integrations.google.routes.client import GoogleRoutesClient
from app.integrations.google.routes.errors import (
    google_routes_error_from_response,
    google_routes_request_failed_error,
    google_routes_timeout_error,
)
from app.integrations.google.routes.mapper import basic_route_from_google_response

logger = logging.getLogger(__name__)


class GoogleRoutesService:
    def __init__(self, client: GoogleRoutesClient) -> None:
        self._client = client

    async def compute_basic_route(self, request: BasicRouteRequest) -> BasicRouteResponse:
        try:
            response = await self._client.post_compute_routes(request)
        except httpx.HTTPStatusError as error:
            routes_error = google_routes_error_from_response(error.response)
            logger.error(
                "google_routes.http_error upstream_status=%s code=%s google_status=%s google_message=%r",
                routes_error.context["upstream_status"],
                routes_error.code,
                routes_error.context["google_status"],
                routes_error.context.get("google_message"),
            )
            raise routes_error from error
        except httpx.TimeoutException as error:
            logger.exception("google_routes.timeout")
            raise google_routes_timeout_error() from error
        except httpx.HTTPError as error:
            logger.exception("google_routes.request_failed")
            raise google_routes_request_failed_error() from error

        return basic_route_from_google_response(response.json())
