from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import httpx
from fastapi import (
    FastAPI,
    Request,
)
from openai import AsyncOpenAI
from app.core.config import settings

NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"

HTTP_TIMEOUT = httpx.Timeout(
    connect=3.0,
    read=10.0,
    write=5.0,
    pool=3.0,
)

HTTP_LIMITS = httpx.Limits(
    max_connections=100,
    max_keepalive_connections=20,
)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    http_client = httpx.AsyncClient(
        timeout=HTTP_TIMEOUT,
        limits=HTTP_LIMITS,
    )

    nvidia_client = AsyncOpenAI(
        base_url=NVIDIA_BASE_URL,
        api_key=settings.nvidia_api_key_value
    )

    app.state.http_client = http_client
    app.state.nvidia_client = nvidia_client

    try:
        yield
    finally:
        await app.state.http_client.aclose()
        await app.state.nvidia_client.close()


def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client

def get_nvidia_client(request: Request) -> AsyncOpenAI:
    return request.app.state.nvidia_client
