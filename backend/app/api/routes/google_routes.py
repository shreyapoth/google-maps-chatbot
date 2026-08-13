import logging
import httpx
from fastapi import (
    APIRouter,
    Depends
)

from app.contracts.route import (
    BasicRouteRequest,
    BasicRouteResponse,
)
from app.core.config import settings
from app.core.http_client import get_http_client
from app.service.routes.service import compute_basic_route

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/routes", tags=["routes"])

@router.post("/directions", response_model=BasicRouteResponse)
async def directions(
    route_request: BasicRouteRequest,
    http_client: httpx.AsyncClient = Depends(get_http_client),
) -> BasicRouteResponse:
    logger.info(
        "/directions.request origin_lat=%s origin_lng=%s destination=%r",
        route_request.origin.latitude,
        route_request.origin.longitude,
        route_request.destination,
    )
    route = await compute_basic_route(
        route_request,
        http_client,
        settings.google_maps_server_key_value,
    )

    return route
