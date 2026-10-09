import logging
import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.middleware import RateLimitMiddleware
from src.routes import router

# Configure logging
log_level = os.getenv("LOG_LEVEL", "info").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Task Manager API",
    version="1.0.0",
    description="RESTful task management service with in-memory storage",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Add request logging middleware
class RequestLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info("%s %s", request.method, request.url.path)
        response = await call_next(request)
        return response

app.add_middleware(RequestLogMiddleware)

# Include REST routes
app.include_router(router)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
