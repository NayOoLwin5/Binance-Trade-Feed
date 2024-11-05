from fastapi import APIRouter, HTTPException
from typing import Optional
import asyncio
from datetime import datetime, timedelta

from models.trade import Trade, TradeStat, SubscribeSymbolRequest
from websocket.binance_client import BinanceWebsocketClient

router = APIRouter()
ws_client = BinanceWebsocketClient()

@router.get("/get_raw_trades")
async def get_raw_trades(symbol: str, since: str, to: str) -> dict:
    """Get raw trades for a symbol within a time range"""
    try:
        binance_symbol = ws_client._format_symbol(symbol)
        if binance_symbol not in ws_client.trades:
            raise HTTPException(status_code=404, detail=f"No trades found for {symbol}")
            
        # Convert timestamps to datetime for comparison
        since_dt = datetime.fromtimestamp(int(since)/1000)
        to_dt = datetime.fromtimestamp(int(to)/1000)
        
        # Check if time range exceeds 5 minutes
        time_diff = to_dt - since_dt
        current_time = datetime.now()
        
        if time_diff.total_seconds() > 300:  # 300 seconds = 5 minutes
            # Adjust to last 5 minutes from the 'to' timestamp
            since_dt = to_dt - timedelta(minutes=5)
            
        # Ensure we don't return data older than 5 minutes from now
        oldest_allowed = current_time - timedelta(minutes=5)
        since_dt = max(since_dt, oldest_allowed)
        
        # Filter trades within adjusted time range
        trades = [
            trade.dict() for trade in ws_client.trades[binance_symbol]
            if since_dt <= datetime.fromtimestamp(int(trade.traded_at)/1000) <= to_dt
        ]
        
        return {"data": trades}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_trades_stat")
async def get_trades_stat(symbol: str, since: str, to: str, side: str) -> TradeStat:
    """Get trade statistics for a symbol within a time range"""
    try:
        binance_symbol = ws_client._format_symbol(symbol)
        if binance_symbol not in ws_client.trades:
            raise HTTPException(status_code=404, detail=f"No trades found for {symbol}")
            
        # Filter trades
        trades = [
            trade for trade in ws_client.trades[binance_symbol]
            if (since <= trade.traded_at <= to) and trade.side == side
        ]
        
        if not trades:
            return TradeStat(
                time_from=since,
                time_to=to,
                symbol=symbol,
                quantity="0",
                weight_avg_price="0",
                side=side
            )
            
        # Calculate statistics
        total_quantity = sum(float(t.quantity) for t in trades)
        weighted_sum = sum(float(t.price) * float(t.quantity) for t in trades)
        
        return TradeStat(
            time_from=since,
            time_to=to,
            symbol=symbol,
            quantity=str(total_quantity),
            weight_avg_price=str(weighted_sum / total_quantity),
            side=side
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/subscribe_trade_symbol")
async def subscribe_trade_symbol(body: SubscribeSymbolRequest):
    """Subscribe to a new trading symbol"""
    try:
        # Start websocket connection in background
        asyncio.create_task(ws_client.connect_symbol(body.symbol))
        return {"message": f"Subscribed to {body.symbol}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))