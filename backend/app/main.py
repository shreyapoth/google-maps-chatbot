import logging
import time
from uuid import uuid4

from fastapi import (
    FastAPI,
    Request,
)
from fastapi.middleware.cors import CORSMiddleware

from app.api.exception_handlers import register_exception_handlers
from app.api.places.google_places_router import router as places_router
from app.api.routes.google_routes import router as google_routes_router
from app.core.config import settings
from app.core.http_client import lifespan

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Route Assistant API", lifespan=lifespan)
register_exception_handlers(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(places_router)
app.include_router(google_routes_router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    started_at = time.perf_counter()
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    request.state.request_id = request_id
    logger.info(
        "request.start request_id=%s method=%s path=%s",
        request_id,
        request.method,
        request.url.path,
    )

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    elapsed_ms = (time.perf_counter() - started_at) * 1000
    logger.info(
        "request.end request_id=%s method=%s path=%s status=%s elapsed_ms=%.2f",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
