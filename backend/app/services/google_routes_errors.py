import httpx


class GoogleRoutesError(Exception):
    def __init__(self, status_code: int, detail: dict):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail["message"])


def google_routes_error_from_response(response: httpx.Response) -> GoogleRoutesError:
    upstream_status = response.status_code
    try:
        error_body = response.json().get("error", {})
    except ValueError:
        error_body = {}

    google_status = error_body.get("status")
    google_message = error_body.get("message") or response.text
    status_code, code, message = _status_mapping(upstream_status)

    return GoogleRoutesError(
        status_code=status_code,
        detail={
            "code": code,
            "message": message,
            "upstream_status": upstream_status,
            "google_status": google_status,
            "google_message": google_message,
        },
    )


def google_routes_timeout_error() -> GoogleRoutesError:
    return GoogleRoutesError(
        status_code=504,
        detail={
            "code": "GOOGLE_ROUTES_TIMEOUT",
            "message": "Google Routes request timed out.",
            "upstream_status": None,
        },
    )


def google_routes_request_failed_error() -> GoogleRoutesError:
    return GoogleRoutesError(
        status_code=502,
        detail={
            "code": "GOOGLE_ROUTES_REQUEST_FAILED",
            "message": "Google Routes request failed before a valid response was received.",
            "upstream_status": None,
        },
    )


def _status_mapping(upstream_status: int) -> tuple[int, str, str]:
    detail_by_status = {
        400: (
            400,
            "GOOGLE_ROUTES_BAD_REQUEST",
            "Google Routes rejected the route request. Check origin and destination formatting.",
        ),
        401: (
            502,
            "GOOGLE_ROUTES_UNAUTHORIZED",
            "Google Routes authentication failed. Check the server API key.",
        ),
        403: (
            502,
            "GOOGLE_ROUTES_FORBIDDEN",
            "Google Routes permission denied. Check API enablement, billing, or key restrictions.",
        ),
        404: (
            502,
            "GOOGLE_ROUTES_NOT_FOUND",
            "Google Routes endpoint was not found.",
        ),
        429: (
            503,
            "GOOGLE_ROUTES_RATE_LIMITED",
            "Google Routes rate limit or quota was exceeded.",
        ),
    }
    return detail_by_status.get(
        upstream_status,
        (
            502,
            "GOOGLE_ROUTES_UPSTREAM_ERROR",
            "Google Routes returned an upstream error.",
        ),
    )
