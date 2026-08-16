import logging

import httpx

from app.contracts.route import BasicRouteRequest
from app.core.external_urls import EXTERNAL_URLS
from app.integrations.google.routes.request import (
    build_compute_routes_body,
    build_compute_routes_headers,
)

logger = logging.getLogger(__name__)

class GoogleRoutesClient:
    def __init__(self, api_key: str, client: httpx.AsyncClient) -> None:
        self._api_key = api_key
        self._client = client 
        
    async def post_compute_routes(self, request: BasicRouteRequest) -> httpx.Response:
        body = build_compute_routes_body(request)
        headers = build_compute_routes_headers(self._api_key)

        logger.info(
            "google_routes.request url=%s destination=%r has_api_key=%s",
            EXTERNAL_URLS["google_routes_compute"],
            body["destination"]["placeId"],
            bool(self._api_key),
        )
        response = await self._client.post(
            EXTERNAL_URLS["google_routes_compute"],
            json=body,
            headers=headers,
        )
        logger.info("google_routes.response status=%s", response.status_code)
        response.raise_for_status()
        return response
