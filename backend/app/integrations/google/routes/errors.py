import httpx

from app.domain.errors import (
    ExternalAuthenticationError,
    ExternalPermissionError,
    ExternalRateLimitError,
    ExternalResponseError,
    ExternalServiceError,
    ExternalTimeoutError,
)


def google_routes_error_from_response(response: httpx.Response) -> ExternalServiceError:
    upstream_status = response.status_code
    try:
        error_body = response.json().get("error", {})
    except ValueError:
        error_body = {}

    google_status = error_body.get("status")
    google_message = error_body.get("message") or response.text
    error_type, code, message = _status_mapping(upstream_status)

    return error_type(
        code=code,
        message=message,
        context={
            "upstream_status": upstream_status,
            "google_status": google_status,
            "google_message": google_message,
        },
    )


def google_routes_timeout_error() -> ExternalTimeoutError:
    return ExternalTimeoutError(
        code="GOOGLE_ROUTES_TIMEOUT",
        message="Google Routes request timed out.",
        context={
            "upstream_status": None,
        },
    )


def google_routes_request_failed_error() -> ExternalServiceError:
    return ExternalServiceError(
        code="GOOGLE_ROUTES_REQUEST_FAILED",
        message="Google Routes request failed before a valid response was received.",
        context={
            "upstream_status": None,
        },
    )


def _status_mapping(upstream_status: int) -> tuple[type[ExternalServiceError], str, str]:
    detail_by_status = {
        400: (
            ExternalResponseError,
            "GOOGLE_ROUTES_BAD_REQUEST",
            "Google Routes rejected the route request. Check origin and destination formatting.",
        ),
        401: (
            ExternalAuthenticationError,
            "GOOGLE_ROUTES_UNAUTHORIZED",
            "Google Routes authentication failed. Check the server API key.",
        ),
        403: (
            ExternalPermissionError,
            "GOOGLE_ROUTES_FORBIDDEN",
            "Google Routes permission denied. Check API enablement, billing, or key restrictions.",
        ),
        404: (
            ExternalResponseError,
            "GOOGLE_ROUTES_NOT_FOUND",
            "Google Routes endpoint was not found.",
        ),
        429: (
            ExternalRateLimitError,
            "GOOGLE_ROUTES_RATE_LIMITED",
            "Google Routes rate limit or quota was exceeded.",
        ),
    }
    return detail_by_status.get(
        upstream_status,
        (
            ExternalServiceError,
            "GOOGLE_ROUTES_UPSTREAM_ERROR",
            "Google Routes returned an upstream error.",
        ),
    )
