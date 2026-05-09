from collections.abc import Awaitable, Callable

from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import settings
from app.schemas.error import ErrorDetail, ErrorResponse


async def request_size_limit_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    content_length = request.headers.get("content-length")

    if content_length is not None and _exceeds_limit(content_length):
        error = ErrorResponse(
            error=ErrorDetail(
                code="request_too_large",
                message="Request body is too large.",
                details={
                    "max_request_body_bytes": settings.max_request_body_bytes,
                },
            )
        )
        return JSONResponse(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            content=error.model_dump(mode="json"),
        )

    return await call_next(request)


def _exceeds_limit(content_length: str) -> bool:
    try:
        return int(content_length) > settings.max_request_body_bytes
    except ValueError:
        return False
