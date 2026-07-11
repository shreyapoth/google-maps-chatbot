import logging
from fastapi import APIRouter
from fastapi import HTTPException
from app.schemas.route import BasicRouteResponse, BasicRouteRequest
from app.services.google_routes_errors import GoogleRoutesError
from app.services.google_routes import compute_basic_route

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/routes", tags=["routes"])


@router.post("/basic", response_model=BasicRouteResponse)
async def basic_route(route_request: BasicRouteRequest) -> BasicRouteResponse:
    logger.info(
        "/basic.request origin_lat=%s origin_lng=%s destination=%r",
        route_request.origin.lat,
        route_request.origin.lng,
        route_request.destination,
    )
    try:
        route = await compute_basic_route(route_request)
    except GoogleRoutesError as error:
        logger.error(
            "/basic.google_routes_error status_code=%s detail=%s",
            error.status_code,
            error.detail,
        )
        raise HTTPException(status_code=error.status_code, detail=error.detail) from error

    logger.info(
        "/basic.response duration_minutes=%s distance_miles=%s",
        route.duration_minutes,
        route.distance_miles
    )
    return route
