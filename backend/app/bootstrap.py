import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import (
    FastAPI,
    Request,
)
from langgraph.graph.state import CompiledStateGraph
from openai import AsyncOpenAI

from app.agent.agent import (
    build_agent,
    build_checkpointer,
)
from app.core.config import settings
from app.core.external_urls import EXTERNAL_URLS
from app.core.http_client import build_http_client
from app.integrations.google.places.client import GooglePlaceClient
from app.integrations.google.routes.client import GoogleRoutesClient
from app.service.places.service import GooglePlaceService
from app.service.routes.service import GoogleRoutesService

logger = logging.getLogger(__name__)


def configure_tracing() -> bool:
    """LangChain reads its tracing settings from the process environment, while
    ours come from Settings, so bridge the two before the first agent run."""

    if not settings.langsmith_tracing:
        return False

    if settings.langsmith_key is None:
        logger.warning("bootstrap.tracing_disabled reason=missing_langsmith_api_key")
        return False

    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_API_KEY"] = settings.langsmith_key
    os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project

    return True


def build_nvidia_client() -> AsyncOpenAI:
    return AsyncOpenAI(
        base_url=EXTERNAL_URLS["nvidia_openai_base"],
        api_key=settings.nvidia_llm_key,
    )


def build_google_place_client(http_client: httpx.AsyncClient) -> GooglePlaceClient:
    return GooglePlaceClient(
        api_key=settings.google_maps_key,
        client=http_client,
    )


def build_google_routes_client(http_client: httpx.AsyncClient) -> GoogleRoutesClient:
    return GoogleRoutesClient(
        api_key=settings.google_maps_key,
        client=http_client,
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info(
        "bootstrap.tracing enabled=%s project=%s",
        configure_tracing(),
        settings.langsmith_project,
    )

    http_client = build_http_client()
    google_places_client = build_google_place_client(http_client)
    google_routes_client = build_google_routes_client(http_client)

    google_place_service = GooglePlaceService(client=google_places_client)
    google_routes_service = GoogleRoutesService(client=google_routes_client)

    app.state.http_client = http_client
    app.state.nvidia_client = build_nvidia_client()
    app.state.google_places_client = google_places_client
    app.state.google_routes_client = google_routes_client
    app.state.google_place_service = google_place_service
    app.state.google_routes_service = google_routes_service
    app.state.agent = build_agent(
        google_place_service,
        google_routes_service,
        build_checkpointer(),
    )

    try:
        yield
    finally:
        await app.state.http_client.aclose()
        await app.state.nvidia_client.close()

def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client

def get_nvidia_client(request: Request) -> AsyncOpenAI:
    return request.app.state.nvidia_client

def get_google_place_client(request: Request) -> GooglePlaceClient:
    return request.app.state.google_places_client

def get_google_routes_client(request: Request) -> GoogleRoutesClient:
    return request.app.state.google_routes_client

def get_google_place_service(request: Request) -> GooglePlaceService:
    return request.app.state.google_place_service

def get_google_routes_service(request: Request) -> GoogleRoutesService:
    return request.app.state.google_routes_service

def get_agent(request: Request) -> CompiledStateGraph:
    return request.app.state.agent
