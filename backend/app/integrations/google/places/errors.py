import httpx

from app.service.errors import (
    ExternalAuthenticationError,
    ExternalPermissionError,
    ExternalRateLimitError,
    ExternalResponseError,
    ExternalServiceError,
    ExternalTimeoutError,
)


def google_places_error_from_response(response: httpx.Response) -> ExternalServiceError:
    upstream_status = response.status_code
    try:
        error_body = response.json().get("error", {})
    except ValueError:
        error_body = {}

    google_status = error_body.get("status")
    error_type, code, message = _status_mapping(upstream_status)

    return error_type(
        code=code,
        message=message,
        context={
            "upstream_status": upstream_status,
            "google_status": google_status,
        },
    )


def google_places_timeout_error() -> ExternalTimeoutError:
    return ExternalTimeoutError(
        code="GOOGLE_PLACES_TIMEOUT",
        message="Google Places request timed out.",
        context={"upstream_status": None},
    )


def google_places_request_failed_error() -> ExternalServiceError:
    return ExternalServiceError(
        code="GOOGLE_PLACES_REQUEST_FAILED",
        message="Google Places request failed before a valid response was received.",
        context={"upstream_status": None},
    )


def _status_mapping(upstream_status: int) -> tuple[type[ExternalServiceError], str, str]:
    detail_by_status = {
        400: (
            ExternalResponseError,
            "GOOGLE_PLACES_BAD_REQUEST",
            "Google Places rejected the search request.",
        ),
        401: (
            ExternalAuthenticationError,
            "GOOGLE_PLACES_UNAUTHORIZED",
            "Google Places authentication failed. Check the server API key.",
        ),
        403: (
            ExternalPermissionError,
            "GOOGLE_PLACES_FORBIDDEN",
            "Google Places permission denied. Check API enablement, billing, or key restrictions.",
        ),
        429: (
            ExternalRateLimitError,
            "GOOGLE_PLACES_RATE_LIMITED",
            "Google Places rate limit or quota was exceeded.",
        ),
    }

    if 400 <= upstream_status < 500:
        return detail_by_status.get(
            upstream_status,
            (
                ExternalResponseError,
                "GOOGLE_PLACES_REQUEST_REJECTED",
                "Google Places rejected the search request.",
            ),
        )

    return (
        ExternalServiceError,
        "GOOGLE_PLACES_UPSTREAM_ERROR",
        "Google Places returned an upstream error.",
    )
