import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from enum import Enum

# Simple models for the API
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
    timestamp: str = ""
    price: float = 150.0
    balance: float = 10000.0
    holdings: int = 0
    portfolio_value: float = 10000.0
    last_news: Optional[Dict[str, Any]] = None
    backtest_results: Optional[Dict[str, float]] = None

app = FastAPI(title="Quant-Gym", description="Financial Analysis Environment")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple environment state
class SimpleEnv:
    def __init__(self):
        self.prices = [150, 152, 151, 153, 155, 154, 156, 158, 157, 159]
        self.news = [
            {"headline": "Apple announces new AI chip", "sentiment": "positive"},
            {"headline": "Supply chain delays expected", "sentiment": "negative"},
            {"headline": "Analysts raise price target", "sentiment": "positive"},
            {"headline": "Market shows strong growth", "sentiment": "positive"},
        ]
        self.reset()
    
    def reset(self):
        self.idx = 0
        self.cash = 10000.0
        self.shares = 0
        return self._get_observation()
    
    def step(self, action: AgentAction):
        # Move time forward
        self.idx = min(self.idx + 1, len(self.prices) - 1)
        price = self.prices[self.idx]
        
        if action.type == "BUY" and action.amount:
            cost = price * action.amount
            if cost <= self.cash:
                self.cash -= cost
                self.shares += action.amount
        elif action.type == "SELL" and action.amount:
            if action.amount <= self.shares:
                self.cash += price * action.amount
                self.shares -= action.amount
        
        return self._get_observation()
    
    def _get_observation(self):
        price = self.prices[self.idx]
        news_idx = self.idx % len(self.news)
        
        return MarketObservation(
            timestamp=f"step_{self.idx}",
            price=float(price),
            balance=round(self.cash, 2),
            holdings=self.shares,
            portfolio_value=round(self.cash + self.shares * price, 2),
            last_news=self.news[news_idx]
        )
    
    def get_state(self):
        obs = self._get_observation()
        return {
            "current_step": self.idx,
            "total_steps": len(self.prices),
            "observation": obs.dict(),
            "tasks_completed": []
        }

env = SimpleEnv()

@app.get("/")
def root():
    return {"message": "Quant-Gym API is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/reset")
def reset():
    obs = env.reset()
    return {"status": "reset", "observation": obs.dict()}

@app.post("/step")
def step(action: AgentAction):
    try:
        observation = env.step(action)
        return {"observation": observation.dict()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/state")
def get_state():
    return env.get_state()

@app.get("/tasks")
def get_tasks():
    return {
        "tasks": [
            {"id": "1", "name": "Fetch Market Data", "description": "Get current price for AAPL"},
            {"id": "2", "name": "News Analysis", "description": "Analyze news and recommend action with explanation"},
            {"id": "3", "name": "Backtest Strategy", "description": "Backtest a trading strategy and return risk metrics"}
        ]
    }
