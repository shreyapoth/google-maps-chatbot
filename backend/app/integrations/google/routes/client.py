import logging

import httpx

from app.contracts.route import BasicRouteRequest
from app.core.external_urls import EXTERNAL_URLS
from app.integrations.google.routes.request import (
    build_compute_routes_body,
    build_compute_routes_headers,
)

logger = logging.getLogger(__name__)


async def post_compute_routes(
    client: httpx.AsyncClient,
    route_request: BasicRouteRequest,
    api_key: str,
) -> httpx.Response:
    body = build_compute_routes_body(route_request)
    headers = build_compute_routes_headers(api_key)

    logger.info(
        "google_routes.request url=%s destination=%r has_api_key=%s",
        EXTERNAL_URLS["google_routes_compute"],
        body["destination"]["address"],
        bool(api_key),
    )
    response = await client.post(
        EXTERNAL_URLS["google_routes_compute"],
        json=body,
        headers=headers,
    )
    logger.info("google_routes.response status=%s", response.status_code)
    response.raise_for_status()
    return response
