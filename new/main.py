# py
from fastapi import FastAPI
import uvicorn
from loguru import logger
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.middleware import register_middleware
from app.api.router import api_router
from fastapi.responses import JSONResponse

settings = get_settings()
configure_logging(settings.LOG_LEVEL)

app = FastAPI(title="health-ai-backend", version="1.0.0")
register_middleware(app)

app.include_router(api_router, prefix="/api")

@app.get("/health", response_class=JSONResponse)
async def health_check():
    return {"status": "ok", "service": "health-ai-backend", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(settings.PORT), log_level=settings.LOG_LEVEL)
