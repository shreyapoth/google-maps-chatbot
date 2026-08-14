import logging

from fastapi import (
    APIRouter,
    Depends,
)

from app.api.routes.deps import get_google_routes_service
from app.contracts.route import (
    BasicRouteRequest,
    BasicRouteResponse,
)
from app.service.routes.service import GoogleRoutesService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/routes", tags=["routes"])


@router.post("/directions", response_model=BasicRouteResponse)
async def directions(
    route_request: BasicRouteRequest,
    routes_service: GoogleRoutesService = Depends(get_google_routes_service),
) -> BasicRouteResponse:
    logger.info(
        "/directions.request origin_lat=%s origin_lng=%s destination=%r",
        route_request.origin.latitude,
        route_request.origin.longitude,
        route_request.destination,
    )
    return await routes_service.compute_basic_route(route_request)
