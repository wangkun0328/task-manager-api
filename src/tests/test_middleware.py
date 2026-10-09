import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.middleware import RateLimitMiddleware


def create_test_app() -> FastAPI:
    """Create a test app with a fresh rate limiter."""
    app = FastAPI()
    app.add_middleware(RateLimitMiddleware, max_requests=60, window_seconds=60)

    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    return app


def _client():
    app = create_test_app()
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


def test_rate_limit_blocks_excess():
    """Sending more than 60 requests should trigger 429."""
    import asyncio

    async def _test():
        async with _client() as c:
            blocked = False
            for _ in range(70):
                r = await c.get("/health")
                if r.status_code == 429:
                    blocked = True
                    break
            assert blocked, "Rate limiter should have blocked after 60 requests"

    asyncio.get_event_loop().run_until_complete(_test())
