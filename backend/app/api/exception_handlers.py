import logging

from fastapi import (
    FastAPI,
    Request,
)
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.service.errors import (
    ApplicationError,
    ExternalRateLimitError,
    ExternalServiceError,
    ExternalTimeoutError,
)

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ApplicationError, application_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)


async def application_error_handler(
    request: Request,
    error: Exception,
) -> JSONResponse:
    assert isinstance(error, ApplicationError)
    return JSONResponse(
        status_code=_status_code_for_application_error(error),
        content={"detail": _public_error_detail(error)},
    )


async def validation_error_handler(
    request: Request,
    error: Exception,
) -> JSONResponse:
    assert isinstance(error, RequestValidationError)
    logger.warning(
        "validation_error request_id=%s path=%s errors=%s",
        getattr(request.state, "request_id", None),
        request.url.path,
        error.errors(),
    )
    return JSONResponse(
        status_code=422,
        content={
            "detail": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed.",
                "errors": jsonable_encoder(error.errors()),
            }
        },
    )


def _public_error_detail(error: ApplicationError) -> dict:
    return {
        "code": error.code,
        "message": error.message,
        **error.context,
    }


def _status_code_for_application_error(error: ApplicationError) -> int:
    if isinstance(error, ExternalRateLimitError):
        return 503
    if isinstance(error, ExternalTimeoutError):
        return 504
    if isinstance(error, ExternalServiceError):
        return 502
    return 500
