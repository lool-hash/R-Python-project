"""
Logging Middleware
==================
Intercepts every HTTP request and logs:
  - Method, URL, client IP
  - Response status code
  - Processing time in milliseconds

All entries go to both the console and logs/app.log via the shared logger.
"""

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.logging.logger import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs every incoming request and its response."""

    async def dispatch(self, request: Request, call_next):
        # ── Record start time ──────────────────────────────────────────────────
        start = time.time()

        # ── Let the request flow through to the actual route handler ──────────
        response = await call_next(request)

        # ── Calculate elapsed time ────────────────────────────────────────────
        elapsed_ms = (time.time() - start) * 1000

        # ── Log the summary line ──────────────────────────────────────────────
        logger.info(
            "%s %s → %d  [%.1f ms]  client=%s",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
            request.client.host if request.client else "unknown",
        )

        return response
