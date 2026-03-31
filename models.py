from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from enum import Enum

class ActionType(str, Enum):
    GET_PRICE = "GET_PRICE"
    GET_NEWS = "GET_NEWS"
    BUY = "BUY"
    SELL = "SELL"
    BACKTEST = "BACKTEST"

class AgentAction(BaseModel):
    type: ActionType
    symbol: Optional[str] = "AAPL"
    amount: Optional[int] = 0
    explanation: Optional[str] = None
    strategy: Optional[str] = None

class MarketObservation(BaseModel):
    timestamp: str
    price: float
    balance: float
    holdings: int
    portfolio_value: float
    last_news: Optional[Dict[str, Any]] = None
    backtest_results: Optional[Dict[str, float]] = None

class EnvironmentState(BaseModel):
    current_step: int
    total_steps: int
    observation: MarketObservation
    tasks_completed: List[str]