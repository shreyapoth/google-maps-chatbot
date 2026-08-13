import http
import logging

import httpx
from fastapi import (
    APIRouter,
    Depends,
)

from app.contracts.place import (
    PlaceNearbySearchRequest,
    PlaceResponse,
    PlaceTextSearchRequest
)
from app.core.config import settings
from app.core.http_client import get_http_client
from app.service.places.service import search_nearby_places, search_text_places

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/places", tags=["places"])


@router.post("/text-search", response_model=PlaceResponse)
async def text_search_places(
    request: PlaceTextSearchRequest,
    http_client: httpx.AsyncClient = Depends(get_http_client)
) -> PlaceResponse:
    logger.info(
        "/places/text-search.request text=%r",
        request.text_query
    )
    return await search_text_places(
        request,
        http_client,
        settings.google_maps_server_key_value
    )

@router.post("/nearby", response_model=PlaceResponse)
async def nearby_places(
    request: PlaceNearbySearchRequest,
    http_client: httpx.AsyncClient = Depends(get_http_client),
) -> PlaceResponse:
    logger.info(
        "/places/nearby.request included_types=%r lat=%s lng=%s radius=%s",
        request.included_types,
        request.location.latitude,
        request.location.longitude,
        request.radius,
    )
    return await search_nearby_places(
        request,
        http_client,
        settings.google_maps_server_key_value,
    )
