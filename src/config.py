import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 3333))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    # Binance WebSocket Configuration
    BINANCE_WS_URL: str = os.getenv("BINANCE_WS_URL", "wss://stream.binance.com:9443/ws")
    MAX_TRADE_AGE_MINUTES: int = int(os.getenv("MAX_TRADE_AGE_MINUTES", 5))
    TRADE_CLEANUP_INTERVAL_SECONDS: int = int(os.getenv("TRADE_CLEANUP_INTERVAL_SECONDS", 30))

    # Default Trading Pairs
    @property
    def DEFAULT_SYMBOLS(self) -> List[str]:
        symbols = os.getenv("DEFAULT_SYMBOLS", "BTC/USDT,ETH/USDT")
        return [s.strip() for s in symbols.split(",")]

settings = Settings()