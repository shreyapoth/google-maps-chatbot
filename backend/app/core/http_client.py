import httpx

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


def build_http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        timeout=HTTP_TIMEOUT,
        limits=HTTP_LIMITS,
    )
