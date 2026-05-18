from __future__ import annotations

from collections import defaultdict, deque
from time import monotonic

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import settings

_request_windows: dict[str, deque[float]] = defaultdict(deque)


async def rate_limit_middleware(request: Request, call_next) -> Response:
    client_host = request.client.host if request.client else "unknown"
    key = f"{client_host}:{request.url.path}"
    now = monotonic()
    window_start = now - settings.rate_limit_window_seconds
    request_times = _request_windows[key]

    while request_times and request_times[0] < window_start:
        request_times.popleft()

    if len(request_times) >= settings.rate_limit_requests:
        return JSONResponse(
            status_code=429,
            content={
                "error": {
                    "message": "Too many requests. Please slow down and try again.",
                    "details": {"retry_after_seconds": settings.rate_limit_window_seconds},
                }
            },
        )

    request_times.append(now)
    return await call_next(request)
