import asyncio
import uvicorn
from fastapi import FastAPI
import logging
from src.config import settings

from api.routes import router, ws_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(router)

@app.on_event("startup")
async def startup_event():
    """Initialize default symbol subscriptions"""
    logger.info("FastAPI application starting up...")
    for symbol in settings.DEFAULT_SYMBOLS:
        asyncio.create_task(ws_client.connect_symbol(symbol))
        logger.info(f"Initialized {symbol} websocket connection")
    logger.info("FastAPI application startup complete")

if __name__ == "__main__":
        uvicorn.run(
        "src.main:app", 
        host=settings.HOST, 
        port=settings.PORT, 
        reload=settings.DEBUG
    )