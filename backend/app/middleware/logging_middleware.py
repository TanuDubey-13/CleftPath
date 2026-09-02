import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from loguru import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = str(uuid.uuid4())[:8]
        start_time = time.perf_counter()
        
        # Log request start
        logger.debug(f"[{request_id}] {request.method} {request.url.path} - Started")
        
        try:
            response = await call_next(request)
            process_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time-Ms"] = str(process_time_ms)
            
            logger.info(
                f"[{request_id}] {request.method} {request.url.path} "
                f"-> Status {response.status_code} ({process_time_ms}ms)"
            )
            return response
        except Exception as e:
            process_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(
                f"[{request_id}] {request.method} {request.url.path} "
                f"-> Failed after {process_time_ms}ms: {e}"
            )
            raise
