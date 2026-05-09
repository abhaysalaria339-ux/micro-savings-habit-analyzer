import logging
from collections.abc import Awaitable, Callable
from time import perf_counter

from starlette.requests import Request
from starlette.responses import Response

from app.middleware.request_id import REQUEST_ID_HEADER

logger = logging.getLogger("app.request")


async def request_logging_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    started_at = perf_counter()
    request_id = request.headers.get(REQUEST_ID_HEADER)

    try:
        response = await call_next(request)
    except Exception:
        logger.exception(
            "HTTP request failed",
            extra=_log_extra(
                request=request,
                event="request_failed",
                request_id=getattr(request.state, "request_id", request_id),
                status_code=500,
                started_at=started_at,
            ),
        )
        raise

    logger.log(
        _level_for_status_code(response.status_code),
        "HTTP request completed",
        extra=_log_extra(
            request=request,
            event="request_completed",
            request_id=getattr(request.state, "request_id", request_id),
            status_code=response.status_code,
            started_at=started_at,
        ),
    )
    return response


def _log_extra(
    *,
    request: Request,
    event: str,
    request_id: str | None,
    status_code: int,
    started_at: float,
) -> dict[str, object]:
    client_host = request.client.host if request.client else None
    route = request.scope.get("route")
    return {
        "event": event,
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "route": getattr(route, "path", None),
        "status_code": status_code,
        "duration_ms": round((perf_counter() - started_at) * 1000, 2),
        "client_host": client_host,
    }


def _level_for_status_code(status_code: int) -> int:
    if status_code >= 500:
        return logging.ERROR

    if status_code >= 400:
        return logging.WARNING

    return logging.INFO
