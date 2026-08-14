import httpx
from fastapi import Depends

from app.core.config import settings
from app.core.http_client import get_http_client
from app.integrations.google.places.client import GooglePlaceClient
from app.service.places.service import GooglePlaceService


def get_google_place_client(
    http_client: httpx.AsyncClient = Depends(get_http_client),
) -> GooglePlaceClient:
    return GooglePlaceClient(
        api_key=settings.google_maps_server_key_value,
        client=http_client,
    )

def get_google_place_service(
    place_client: GooglePlaceClient = Depends(get_google_place_client),
) -> GooglePlaceService:
    return GooglePlaceService(client=place_client)
