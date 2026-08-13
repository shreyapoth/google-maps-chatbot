import logging

import httpx

from app.contracts.place import PlaceNearbySearchRequest, PlaceTextSearchRequest
from app.core.external_urls import EXTERNAL_URLS
from app.integrations.google.places.request import (
    build_nearby_search_body,
    build_nearby_search_headers,
    build_text_search_body, 
    build_text_search_headers
)

logger = logging.getLogger(__name__)

async def post_text_search(
    client: httpx.AsyncClient,
    request: PlaceTextSearchRequest,
    api_key: str
) -> httpx.Response:
    body = build_text_search_body(request)
    headers = build_text_search_headers(api_key)

    logger.info(
        "google_places.nearby_search.request url=%s has_api_key=%s",
        EXTERNAL_URLS["google_places_text_search"],
        bool(api_key),
    )

    response = await client.post( 
        EXTERNAL_URLS["google_places_text_search"],
        json=body, 
        headers=headers)
    
    logger.info("google_places.nearby_search.response status=%s", response.status_code)
    response.raise_for_status()

    return response 



async def post_nearby_search(
    client: httpx.AsyncClient,
    request: PlaceNearbySearchRequest,
    api_key: str,
) -> httpx.Response:
    body = build_nearby_search_body(request)
    headers = build_nearby_search_headers(api_key)

    logger.info(
        "google_places.nearby_search.request url=%s has_api_key=%s",
        EXTERNAL_URLS["google_places_nearby_search"],
        bool(api_key),
    )

    response = await client.post(
        EXTERNAL_URLS["google_places_nearby_search"],
        json=body,
        headers=headers,
    )

    logger.info("google_places.nearby_search.response status=%s", response.status_code)
    response.raise_for_status()
    
    return response
