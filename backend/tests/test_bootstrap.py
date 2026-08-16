import os
from types import SimpleNamespace

import httpx
import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.bootstrap import (
    build_google_place_client,
    build_google_routes_client,
    configure_tracing,
    get_google_place_client,
    get_google_place_service,
    get_google_routes_client,
    get_google_routes_service,
    get_http_client,
    get_nvidia_client,
)
from app.contracts.coordinates import Coordinates
from app.contracts.place import PlaceNearbySearchRequest
from app.contracts.route import BasicRouteRequest
from app.core.config import settings
from app.integrations.google.places.client import GooglePlaceClient
from app.integrations.google.routes.client import GoogleRoutesClient
from app.main import app
from app.service.places.service import GooglePlaceService
from app.service.routes.service import GoogleRoutesService


def _capture_api_key(captured: dict, json_body: dict):
    def handler(request: httpx.Request) -> httpx.Response:
        captured["api_key"] = request.headers.get("X-Goog-Api-Key")
        return httpx.Response(200, json=json_body)

    return handler


@pytest.mark.asyncio
async def test_place_client_sends_configured_api_key():
    captured = {}
    handler = _capture_api_key(captured, {"places": []})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        place_client = build_google_place_client(http_client)
        place_service = GooglePlaceService(client=place_client)

        assert isinstance(place_client, GooglePlaceClient)

        await place_service.search_nearby_places(
            PlaceNearbySearchRequest(
                included_types=["restaurant"],
                location=Coordinates(latitude=37.33, longitude=-121.89),
            )
        )

    assert captured["api_key"] == settings.google_maps_key


@pytest.mark.asyncio
async def test_routes_client_sends_configured_api_key():
    captured = {}
    handler = _capture_api_key(
        captured,
        {"routes": [{"duration": "900s", "distanceMeters": 3218}]},
    )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        routes_client = build_google_routes_client(http_client)
        routes_service = GoogleRoutesService(client=routes_client)

        assert isinstance(routes_client, GoogleRoutesClient)

        await routes_service.compute_basic_route(
            BasicRouteRequest(
                origin=Coordinates(latitude=47.6062, longitude=-122.3321),
                destination="Pike Place Market",
            )
        )

    assert captured["api_key"] == settings.google_maps_key


def test_state_accessors_return_the_objects_built_at_startup():
    with TestClient(app):
        request = SimpleNamespace(app=app)

        assert get_http_client(request) is app.state.http_client
        assert get_nvidia_client(request) is app.state.nvidia_client
        assert get_google_place_client(request) is app.state.google_places_client
        assert get_google_routes_client(request) is app.state.google_routes_client
        assert get_google_place_service(request) is app.state.google_place_service
        assert get_google_routes_service(request) is app.state.google_routes_service


def _isolate_tracing_env(monkeypatch):
    # monkeypatch owns the keys so the real environment is restored afterwards.
    for name in ("LANGSMITH_TRACING", "LANGSMITH_API_KEY", "LANGSMITH_PROJECT"):
        monkeypatch.setenv(name, "")


def test_tracing_stays_off_until_it_is_asked_for(monkeypatch):
    _isolate_tracing_env(monkeypatch)
    monkeypatch.setattr(settings, "langsmith_tracing", False)

    assert configure_tracing() is False
    assert os.environ["LANGSMITH_TRACING"] == ""


def test_tracing_needs_a_key_even_when_enabled(monkeypatch):
    _isolate_tracing_env(monkeypatch)
    monkeypatch.setattr(settings, "langsmith_tracing", True)
    monkeypatch.setattr(settings, "langsmith_api_key", None)

    assert configure_tracing() is False
    assert os.environ["LANGSMITH_TRACING"] == ""


def test_tracing_exports_settings_to_the_environment_langchain_reads(monkeypatch):
    _isolate_tracing_env(monkeypatch)
    monkeypatch.setattr(settings, "langsmith_tracing", True)
    monkeypatch.setattr(settings, "langsmith_api_key", SecretStr("lsv2_pt_test"))
    monkeypatch.setattr(settings, "langsmith_project", "maps-chatbot-test")

    assert configure_tracing() is True
    assert os.environ["LANGSMITH_TRACING"] == "true"
    assert os.environ["LANGSMITH_API_KEY"] == "lsv2_pt_test"
    assert os.environ["LANGSMITH_PROJECT"] == "maps-chatbot-test"


def test_startup_services_wrap_the_startup_clients():
    with TestClient(app):
        assert isinstance(app.state.google_place_service, GooglePlaceService)
        assert isinstance(app.state.google_routes_service, GoogleRoutesService)
        assert app.state.google_place_service._client is app.state.google_places_client
        assert app.state.google_routes_service._client is app.state.google_routes_client
