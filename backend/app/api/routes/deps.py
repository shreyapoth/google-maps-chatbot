import httpx
from fastapi import Depends

from app.core.config import settings
from app.core.http_client import get_http_client
from app.integrations.google.routes.client import GoogleRoutesClient
from app.service.routes.service import GoogleRoutesService


def get_google_routes_client(
    http_client: httpx.AsyncClient = Depends(get_http_client),
) -> GoogleRoutesClient:
    return GoogleRoutesClient(
        api_key=settings.google_maps_server_key_value,
        client=http_client,
    )


def get_google_routes_service(
    routes_client: GoogleRoutesClient = Depends(get_google_routes_client),
) -> GoogleRoutesService:
    return GoogleRoutesService(client=routes_client)
