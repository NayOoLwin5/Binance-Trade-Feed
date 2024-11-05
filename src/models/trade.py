from pydantic import BaseModel
from typing import Literal

class Trade(BaseModel):
    traded_at: str  # Unix timestamp in milliseconds
    symbol: str
    quantity: str
    price: str
    side: Literal["buy", "sell"]

class TradeStat(BaseModel):
    time_from: str
    time_to: str
    symbol: str
    quantity: str
    weight_avg_price: str
    side: Literal["buy", "sell"]

class SubscribeSymbolRequest(BaseModel):
    symbol: str