import logging

from fastapi import (
    APIRouter,
    Depends,
)

from app.api.places.deps import get_google_place_service
from app.contracts.place import (
    PlaceNearbySearchRequest,
    PlaceResponse,
    PlaceTextSearchRequest,
)
from app.service.places.service import GooglePlaceService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/places", tags=["places"])


@router.post("/text-search", response_model=PlaceResponse)
async def text_search_places(
    request: PlaceTextSearchRequest,
    place_service: GooglePlaceService = Depends(get_google_place_service),
) -> PlaceResponse:
    logger.info(
        "/places/text-search.request text=%r",
        request.text_query,
    )
    return await place_service.search_text_places(request)


@router.post("/nearby", response_model=PlaceResponse)
async def nearby_places(
    request: PlaceNearbySearchRequest,
    place_service: GooglePlaceService = Depends(get_google_place_service),
) -> PlaceResponse:
    logger.info(
        "/places/nearby.request included_types=%r lat=%s lng=%s radius=%s",
        request.included_types,
        request.location.latitude,
        request.location.longitude,
        request.radius,
    )
    return await place_service.search_nearby_places(request)
