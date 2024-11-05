import asyncio
import json
import logging
from collections import deque
from datetime import datetime, timedelta
import websockets
from typing import Dict, Deque
from src.config import settings

from models.trade import Trade

logger = logging.getLogger(__name__)

class BinanceWebsocketClient:
    def __init__(self):
        self.ws_url = settings.BINANCE_WS_URL
        self.trades: Dict[str, Deque[Trade]] = {}
        self.active_symbols = set()
        self.max_age = timedelta(minutes=settings.MAX_TRADE_AGE_MINUTES)
        
    def _format_symbol(self, symbol: str) -> str:
        """Convert API symbol format (BTC/USDT) to Binance format (btcusdt)"""
        return symbol.replace("/", "").lower()

    def _deformat_symbol(self, symbol: str) -> str:
        """Convert Binance format to API format"""
        return f"{symbol[:-4].upper()}/{symbol[-4:].upper()}"

    async def _clean_old_trades(self, symbol: str):
        """Remove trades older than 5 minutes"""
        while True:
            await asyncio.sleep(settings.TRADE_CLEANUP_INTERVAL_SECONDS)  # Clean every nth seconds
            if symbol not in self.trades:
                continue
                
            current_time = datetime.now()
            while self.trades[symbol] and \
                  current_time - datetime.fromtimestamp(int(self.trades[symbol][-1].traded_at)/1000) > self.max_age:
                self.trades[symbol].pop()

    async def _handle_trade_message(self, message: dict):
        """Process incoming trade message"""
        binance_symbol = self._format_symbol(message["s"])
        trade = Trade(
            traded_at=str(message["T"]),
            symbol=self._deformat_symbol(message["s"]),
            quantity=message["q"],
            price=message["p"],
            side="sell" if message["m"] else "buy"
        )
        
        if binance_symbol not in self.trades:
            self.trades[binance_symbol] = deque()
        
        self.trades[binance_symbol].appendleft(trade)

    async def connect_symbol(self, symbol: str):
        """Connect to trade stream for a symbol"""
        binance_symbol = self._format_symbol(symbol)
        if binance_symbol in self.active_symbols:
            return
            
        self.active_symbols.add(binance_symbol)
        
        # Start cleaner task
        asyncio.create_task(self._clean_old_trades(binance_symbol))
        
        while True:
            try:
                async with websockets.connect(f"{self.ws_url}/{binance_symbol}@trade") as ws:
                    logger.info(f"Connected to {symbol} trade stream")
                    
                    while True:
                        message = await ws.recv()
                        logger.info(f"Received message: {message}")
                        await self._handle_trade_message(json.loads(message))
                        
            except Exception as e:
                logger.error(f"WebSocket error for {symbol}: {str(e)}")
                await asyncio.sleep(5)  # Wait before reconnecting