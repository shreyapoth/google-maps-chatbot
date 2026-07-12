import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.domain.errors import ApplicationError
from app.domain.errors import ExternalAuthenticationError
from app.domain.errors import ExternalRateLimitError
from app.domain.errors import ExternalResponseError
from app.domain.errors import ExternalServiceError
from app.domain.errors import ExternalTimeoutError

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ApplicationError, application_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)


async def application_error_handler(
    request: Request,
    error: ApplicationError,
) -> JSONResponse:
    logger.error(
        "application_error path=%s code=%s context=%s",
        request.url.path,
        error.code,
        error.context,
    )
    return JSONResponse(
        status_code=_status_code_for_application_error(error),
        content={"detail": _public_error_detail(error)},
    )


async def validation_error_handler(
    request: Request,
    error: RequestValidationError,
) -> JSONResponse:
    logger.warning(
        "validation_error path=%s errors=%s",
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
    if isinstance(
        error,
        (
            ExternalAuthenticationError,
            ExternalResponseError,
            ExternalServiceError,
        ),
    ):
        return 502
    return 500
