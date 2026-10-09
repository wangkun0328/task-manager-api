import time
from collections import defaultdict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple sliding window rate limiter: 60 requests per minute per IP."""

    def __init__(
        self,
        app,
        max_requests: int = 60,
        window_seconds: int = 60,
    ) -> None:
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        now = time.monotonic()

        # Prune old timestamps outside the window
        timestamps = self._requests[client_ip]
        cutoff = now - self.window_seconds
        self._requests[client_ip] = [t for t in timestamps if t > cutoff]

        if len(self._requests[client_ip]) >= self.max_requests:
            return Response(
                status_code=429,
                content="Too many requests. Try again later.",
                media_type="text/plain",
            )

        self._requests[client_ip].append(now)
        return await call_next(request)
