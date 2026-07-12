import logging
import httpx
from fastapi import APIRouter
from fastapi import Depends
from app.core.http_client import get_http_client
from app.domain.routes.service import compute_basic_route
from app.schemas.route import BasicRouteResponse, BasicRouteRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/routes", tags=["routes"])


@router.post("/basic", response_model=BasicRouteResponse)
async def basic_route(
    route_request: BasicRouteRequest,
    http_client: httpx.AsyncClient = Depends(get_http_client),
) -> BasicRouteResponse:
    logger.info(
        "/basic.request origin_lat=%s origin_lng=%s destination=%r",
        route_request.origin.lat,
        route_request.origin.lng,
        route_request.destination,
    )
    route = await compute_basic_route(route_request, http_client)
    logger.info(
        "/basic.response duration_minutes=%s distance_miles=%s",
        route.duration_minutes,
        route.distance_miles
    )
    return route
