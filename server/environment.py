from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import random

app = FastAPI()

# Simple data
prices = [150, 152, 151, 153, 155, 154, 156, 158, 157, 159]
cash = 10000
shares = 0
step_num = 0

class Action(BaseModel):
    action: str  # BUY, SELL, or GET_PRICE
    amount: Optional[int] = 0

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/reset")
def reset():
    global cash, shares, step_num
    cash = 10000
    shares = 0
    step_num = 0
    return {"cash": cash, "shares": shares, "price": prices[0]}

@app.post("/step")
def step(action: Action):
    global cash, shares, step_num
    step_num = min(step_num + 1, len(prices) - 1)
    price = prices[step_num]
    
    if action.action == "BUY" and action.amount:
        cost = price * action.amount
        if cost <= cash:
            cash -= cost
            shares += action.amount
    elif action.action == "SELL" and action.amount:
        if action.amount <= shares:
            cash += price * action.amount
            shares -= action.amount
    
    return {
        "price": price,
        "cash": cash,
        "shares": shares,
        "portfolio_value": cash + (shares * price),
        "step": step_num
    }

@app.get("/tasks")
def tasks():
    return {
        "tasks": [
            {"id": 1, "name": "Get Price", "description": "Get current stock price"},
            {"id": 2, "name": "Buy Stock", "description": "Buy shares of stock"},
            {"id": 3, "name": "Sell Stock", "description": "Sell shares of stock"}
        ]
    }

@app.get("/")
def root():
    return {"message": "Trading Environment API", "status": "running"}
