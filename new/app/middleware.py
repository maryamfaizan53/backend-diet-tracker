# py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info("Request start: {} {}", request.method, request.url.path)
        try:
            response = await call_next(request)
            logger.info("Request end: {} {} -> {}", request.method, request.url.path, response.status_code)
            return response
        except Exception as exc:
            logger.exception("Unhandled exception")
            raise

def register_middleware(app: FastAPI):
    app.add_middleware(LoggingMiddleware)

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled error in request")
        return JSONResponse(status_code=500, content={"error": "internal_server_error", "details": str(exc)})

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return JSONResponse(status_code=400, content={"error": "bad_request", "details": str(exc)})
