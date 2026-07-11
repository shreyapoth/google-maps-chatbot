import logging

import httpx

from app.core.external_urls import EXTERNAL_URLS

logger = logging.getLogger(__name__)


async def post_compute_routes(
    client: httpx.AsyncClient,
    payload: dict,
    headers: dict[str, str],
) -> httpx.Response:
    logger.info(
        "google_routes.request url=%s destination=%r has_api_key=%s",
        EXTERNAL_URLS["google_routes_compute"],
        payload["destination"]["address"],
        bool(headers["X-Goog-Api-Key"]),
    )
    response = await client.post(
        EXTERNAL_URLS["google_routes_compute"],
        json=payload,
        headers=headers,
    )
    logger.info("google_routes.response status=%s", response.status_code)
    response.raise_for_status()
    return response
